from psycopg2.extras import RealDictCursor # type: ignore
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests
from PIL import Image
import calendar
from application.helpers.server_log_helper import ServerLogHelper

load_dotenv()

class BillingService:
  def __init__(self, db_pool):
    self.db_pool = db_pool
    self.api_key = os.getenv("SLIPOK_API_KEY")

    if not self.api_key:
      raise ValueError("Missing SLIPOK_API_KEY in environment variables")

  def calculate_bill(self, portfolio_id, model_id):
    try:
      conn = self.db_pool.get_connection()
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      
      now = datetime.now()
      first_day = now.replace(day=1).strftime('%Y-%m-%d')
      last_day = now.replace(day=calendar.monthrange(now.year, now.month)[1]).strftime('%Y-%m-%d')
      due_date = (now + timedelta(days=5)).strftime('%Y-%m-%d')
      # Get total profit for unbilled orders
      cursor.execute("""
        SELECT SUM(profit) FROM orders 
        WHERE portfolio_id = %s 
        AND created_at BETWEEN %s AND %s
        AND bill_id IS NULL
      """, (portfolio_id, first_day, last_day))

      profit = cursor.fetchone()["sum"] or 0

      if profit <= 0:  # No profit, no bill needed
        return None  

      # Get commission rate
      cursor.execute("SELECT commission FROM models WHERE model_id = %s", (model_id,))
      commission = cursor.fetchone()["commission"] or 0

      request_body = {
        "method":"spotRateHistory",
        "data":{"base":"USD","term":"THB","period":"week"}
      }
      
      response = requests.post("https://api.rates-history-service.prd.aws.ofx.com/rate-history/api/1", json=request_body)
      exchange_rate = response.json().get("data", {}).get("CurrentInterbankRate")
      
      net_amount = max(profit * exchange_rate * commission, 0)  # Ensure non-negative
      net_amount = round(net_amount, 2)

      # Insert new bill
      cursor.execute("""
        INSERT INTO bills (portfolio_id, model_id, total_profit, commission, net_amount, due_date, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'pending')
        RETURNING bill_id
      """, (portfolio_id, model_id, profit, commission, net_amount, due_date))

      bill_id = cursor.fetchone()["bill_id"]

      # Update orders to reference this bill
      cursor.execute("""
        UPDATE orders SET bill_id = %s
        WHERE portfolio_id = %s 
        AND created_at BETWEEN %s AND %s
        AND bill_id IS NULL
      """, (bill_id, portfolio_id, first_day, last_day))

      conn.commit()  # Commit transaction

      return bill_id  # Return the created bill ID
    except Exception as e:
      conn.rollback()  # Rollback in case of failure
      raise e
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def bill_all(self):
    try:
      conn = self.db_pool.get_connection()
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      
      cursor.execute("SELECT portfolio_id, model_id FROM portfolios")
      portfolios = cursor.fetchall()

      for portfolio in portfolios:
        bill_id = self.calculate_bill(portfolio["portfolio_id"], portfolio["model_id"])
        if bill_id:
          print(f"Created Bill ID: {bill_id} for Portfolio {portfolio['portfolio_id']}")
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def get_bills(self, user_id):
    try:
      conn = self.db_pool.get_connection()
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      
      cursor.execute("""
        SELECT * FROM bills
        LEFT JOIN portfolios ON bills.portfolio_id = portfolios.portfolio_id
        WHERE user_id = %s
      """, (user_id,))
      bills = cursor.fetchall()

      return {"bills": bills}
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def get_bill(self, user_id, bill_id):
    try:
      conn = self.db_pool.get_connection()
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      
      cursor.execute("""
        SELECT bills.*, portfolios.user_id 
        FROM bills
        LEFT JOIN portfolios ON bills.portfolio_id = portfolios.portfolio_id 
        WHERE bill_id = %s AND portfolios.user_id = %s
      """, (bill_id, user_id))
      bill = cursor.fetchone()

      return {"bill": bill}
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

def pay_bill(self, user_id, bill_id, image_file, notes):
  conn = None
  try:
    conn = self.db_pool.get_connection()
    with conn.cursor() as cursor:
      
      # Fetch bill details
      cursor.execute("SELECT net_amount FROM bills WHERE bill_id = %s", (bill_id,))
      bill = cursor.fetchone()
      if not bill:
        raise ValueError("Bill not found!")

      amount_bill = bill[0]

      response = requests.post(
        "https://api.slipok.com/api/line/apikey/41247",
        files={"files": image_file}, 
        headers={"x-authorization": self.api_key}
      )

      try:
        response_json = response.json()
      except Exception:
        raise ValueError("Invalid API response format (not JSON)")

      ServerLogHelper.log(response_json)

      if response.status_code != 200 or not response_json.get("success", False):
        raise Exception("Error uploading receipt image")

      # Extract payment data
      data = response_json.get("data", {})
      if not data:
        raise ValueError("Missing payment data in response")

      reference_number = data.get("transRef")
      payment_date = data.get("transTimestamp")
      amount_paid = data.get("amount")
      receiver_name = data.get("receiver", {}).get("name")

      if not all([reference_number, payment_date, amount_paid, receiver_name]):
        raise ValueError("Incomplete payment data received")

      ServerLogHelper.log(f"Receiver Name: {receiver_name}")

      if receiver_name != "Mr. Nathanon S":
        raise ValueError("Invalid receiver")

      if amount_paid < amount_bill:
        raise ValueError("Amount paid does not match the bill amount")

      os.makedirs("uploads", exist_ok=True)

      image_path = os.path.join("uploads", image_file.filename)
      image_file.seek(0)  # Reset pointer before saving
      with open(image_path, "wb") as f:
        f.write(image_file.read())

      # Update bill status and insert receipt record
      cursor.execute("UPDATE bills SET status = 'paid' WHERE bill_id = %s", (bill_id,))
      cursor.execute("""
        INSERT INTO receipts (bill_id, user_id, amount_paid, receipt_image, reference_number, payment_date, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
      """, (bill_id, user_id, amount_paid, image_path, reference_number, payment_date, notes))

      # Check if user still has overdue bills
      cursor.execute("""
        SELECT COUNT(*) FROM bills 
        WHERE portfolio_id IN (SELECT portfolio_id FROM portfolios WHERE user_id = %s) 
        AND status IN ('pending', 'overdue')
      """, (user_id,))
      unpaid_bills_count = cursor.fetchone()[0]

      if unpaid_bills_count == 0:
        # Unban user if they have no unpaid bills
        cursor.execute("UPDATE users SET is_banned = FALSE WHERE user_id = %s", (user_id,))

      conn.commit()
      return {"message": "Payment Successful!"}

  except Exception as e:
    if conn:
      conn.rollback()
    ServerLogHelper.log(f"Payment error: {str(e)}")
    raise Exception(f"Error processing payment: {str(e)}")

  finally:
    if conn:
      self.db_pool.release_connection(conn)

def mark_overdue_bills(self, cursor):
  """
  Updates all pending bills to 'overdue' if their due date has passed.
  """
  cursor.execute("""
    UPDATE bills 
    SET status = 'overdue' 
    WHERE due_date < NOW() AND status = 'pending'
  """)

def ban_users_with_overdue_bills(self, cursor):
  """
  Bans users who have portfolios associated with overdue bills.
  """
  cursor.execute("""
    UPDATE users 
    SET is_banned = TRUE 
    WHERE user_id IN (
      SELECT DISTINCT portfolios.user_id 
      FROM bills 
      JOIN portfolios ON bills.portfolio_id = portfolios.portfolio_id
      WHERE bills.status = 'overdue'
    )
  """)

def check_unpaid_bills(self):
  """
  Main function that marks overdue bills and bans users accordingly.
  """
  conn = self.db_pool.get_connection()

  try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("BEGIN;")  # Start transaction

    self.mark_overdue_bills(cursor)  # Mark overdue bills
    self.ban_users_with_overdue_bills(cursor)  # Ban users

    conn.commit()  # Commit transaction if successful

  except Exception as e:
    conn.rollback()  # Rollback on error
    raise RuntimeError(f"Something went wrong: {str(e)}")

  finally:
    cursor.close()
    self.db_pool.release_connection(conn)