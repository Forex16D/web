from psycopg2.extras import RealDictCursor # type: ignore
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests
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
      if profit <= 0:
        return None  

      # Get commission rate
      cursor.execute("""
        SELECT COALESCE(models.commission, portfolios.commission, 0) AS commission
        FROM portfolios
        LEFT JOIN models ON models.model_id = %s
        LEFT JOIN portfolios AS linked_portfolio ON linked_portfolio.portfolio_id = %s
        LIMIT 1
      """, (model_id, model_id))

      commission = cursor.fetchone()["commission"]

      # Fetch exchange rate
      request_body = {
        "method": "spotRateHistory",
        "data": {"base": "USD", "term": "THB", "period": "week"}
      }
      response = requests.post("https://api.rates-history-service.prd.aws.ofx.com/rate-history/api/1", json=request_body)
      exchange_rate = response.json().get("data", {}).get("CurrentInterbankRate", 33.5)  # Default to 33.5 if API fails

      net_amount_usd = max(profit * commission, 0)
      net_amount = net_amount_usd * exchange_rate
      net_amount = round(net_amount, 2)

      # Check user balance
      cursor.execute("""
        SELECT balance FROM users 
        LEFT JOIN portfolios
        WHERE portfolio_id = %s
      """, (portfolio_id,))
      user_balance = cursor.fetchone()["balance"] or 0

      if user_balance >= net_amount_usd:
        # Deduct balance and mark bill as paid
        cursor.execute("""
          UPDATE users SET balance = balance - %s WHERE portfolio_id = %s
        """, (net_amount_usd, portfolio_id))
        
        bill_status = 'paid'
      else:
        # Create a pending bill if balance is insufficient
        bill_status = 'pending'

      # Insert new bill
      cursor.execute("""
        INSERT INTO bills (portfolio_id, model_id, total_profit, commission, net_amount, due_date, status, exchange_rate, net_amount_usd)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING bill_id
      """, (portfolio_id, model_id, profit, commission, net_amount, due_date, bill_status, exchange_rate, net_amount_usd))

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

  def calculate_bill_v2(self, user_id):
    try:
      conn = self.db_pool.get_connection()
      cursor = conn.cursor(cursor_factory=RealDictCursor)

      now = datetime.now()
      first_day = now.replace(day=1).strftime('%Y-%m-%d')
      last_day = now.replace(day=calendar.monthrange(now.year, now.month)[1]).strftime('%Y-%m-%d')
      due_date = (now + timedelta(days=5)).strftime('%Y-%m-%d')

      # Get total profit for unbilled orders
      cursor.execute("""
        SELECT SUM(total_profit) 
        FROM (
          SELECT 
            (orders.profit - orders.profit * COALESCE(models.commission, p2.commission, 0)) AS total_profit
          FROM orders
          RIGHT JOIN portfolios AS p1 ON orders.portfolio_id = p1.portfolio_id
          LEFT JOIN models ON orders.model_id = models.model_id
          LEFT JOIN portfolios AS p2 ON orders.model_id = p2.portfolio_id  -- Used only for commission
          WHERE p1.user_id = %s
          AND orders.created_at BETWEEN %s AND %s
          AND bill_id IS NULL
        ) AS subquery;
      """, (user_id, first_day, last_day))
      net_amount_usd = cursor.fetchone()["sum"]

      if net_amount_usd <= 0:
        return None

      # Fetch exchange rate
      request_body = {
        "method": "spotRateHistory",
        "data": {"base": "USD", "term": "THB", "period": "week"}
      }
      response = requests.post("https://api.rates-history-service.prd.aws.ofx.com/rate-history/api/1", json=request_body)
      exchange_rate = response.json().get("data", {}).get("CurrentInterbankRate", 33.5)  # Default to 33.5 if API fails

      net_amount = net_amount_usd * exchange_rate
      net_amount = round(net_amount, 2)

      # Check user balance
      cursor.execute("""
        SELECT balance FROM users WHERE user_id = %s
      """, (user_id,))
      user_balance = cursor.fetchone()["balance"]

      if user_balance >= net_amount_usd:
        # Deduct balance and mark bill as paid
        cursor.execute("""
          UPDATE users SET balance = balance - %s WHERE user_id = %s
        """, (net_amount_usd, user_id))
        
        bill_status = 'paid'
      else:
        # Create a pending bill if balance is insufficient
        bill_status = 'pending'

      # Insert new bill
      cursor.execute("""
        INSERT INTO bills (user_id, net_amount, due_date, status, exchange_rate, net_amount_usd)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING bill_id
      """, (user_id, net_amount, due_date, bill_status, exchange_rate, net_amount_usd))

      bill_id = cursor.fetchone()["bill_id"]

      # Update orders to reference this bill
      cursor.execute("""
          UPDATE orders 
          SET bill_id = %s
          WHERE portfolio_id IN (
            SELECT portfolio_id FROM portfolios WHERE user_id = %s
          )
          AND created_at BETWEEN %s AND %s
          AND bill_id IS NULL
      """, (bill_id, user_id, first_day, last_day))

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
      
      cursor.execute("SELECT user_id FROM users")
      users = cursor.fetchall()

      for user in users:
        bill_id = self.calculate_bill_v2(user["user_id"])
        if bill_id:
          print(f"Created Bill ID: {bill_id} for User {user['user_id']}")
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)
  
  def pay_expert_commission(self, user_id):
    try:
      conn = self.db_pool.get_connection()
      cursor = conn.cursor(cursor_factory=RealDictCursor)

      now = datetime.now()
      first_day = now.replace(day=1).strftime('%Y-%m-%d')
      last_day = now.replace(day=calendar.monthrange(now.year, now.month)[1]).strftime('%Y-%m-%d')

      # First, fetch the total profit
      cursor.execute("""
        SELECT COALESCE(SUM(orders.profit * portfolios.commission), 0) AS total_profit
        FROM orders
        JOIN portfolios ON orders.model_id = portfolios.portfolio_id
        WHERE portfolios.user_id = %s
        AND orders.created_at BETWEEN %s AND %s
      """, (user_id, first_day, last_day))
      
      total_profit_result = cursor.fetchone()
      total_profit = total_profit_result['total_profit'] if total_profit_result else 0

      # Now, update the user's balance
      cursor.execute("""
        UPDATE users 
        SET balance = balance + %s
        WHERE user_id = %s
      """, (total_profit, user_id))

      conn.commit()  # Don't forget to commit the transaction!

      return {"total_profit": total_profit}  # Return the calculated profit

    except Exception as e:
      # Handle any potential errors
      conn.rollback()  # Rollback in case of error
      return {"error": str(e)}

    finally:
      cursor.close()
      self.db_pool.release_connection(conn)


  def pay_all_expert(self):
    try:
      conn = self.db_pool.get_connection()
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      
      cursor.execute("SELECT user_id FROM users")
      users = cursor.fetchall()

      for user in users:
        amount = self.pay_expert_commission(user["user_id"])
        if amount:
          print(f"Pay User {user['user_id']} Amount {amount}")
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def get_bills(self, user_id):
    try:
      conn = self.db_pool.get_connection()
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      
      cursor.execute("""
        SELECT * FROM bills WHERE user_id = %s
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
        SELECT bills.*
        FROM bills
        WHERE bill_id = %s AND user_id = %s
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
        cursor.execute("SELECT net_amount, status FROM bills WHERE bill_id = %s", (bill_id,))
        bill = cursor.fetchone()
        if not bill:
          raise ValueError("Bill not found!")

        status = bill[1]
        
        if status == "paid":
          raise ValueError("Bill already paid!")

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
          INSERT INTO receipts (bill_id, user_id, amount_paid, receipt_image, reference_number, payment_date, notes, method)
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (bill_id, user_id, amount_paid, image_path, reference_number, payment_date, notes, "receipt"))

        # Check if user still has overdue bills
        cursor.execute("""
          SELECT COUNT(*) FROM bills 
          WHERE user_id = %s 
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
        
  def pay_bill_wallet(self, user_id, bill_id, notes):
    try:
      conn = self.db_pool.get_connection()
      cursor = conn.cursor(cursor_factory=RealDictCursor)

      # Fetch bill details (net_amount_usd)
      cursor.execute("SELECT net_amount_usd, status FROM bills WHERE bill_id = %s", (bill_id,))
      bill = cursor.fetchone()
      if not bill:
        raise ValueError("Bill not found!")
      
      status = bill["status"]

      if status.strip() == "paid":
        ServerLogHelper.log("Paying wallet")
        raise ValueError("Bill already paid!")

      amount_paid = bill["net_amount_usd"]
      payment_date = datetime.now()

      # Deduct balance from user
      cursor.execute("""
        UPDATE users 
        SET balance = balance - %s 
        WHERE user_id = %s
      """, (amount_paid, user_id))

      # Mark bill as paid
      cursor.execute("""
        UPDATE bills 
        SET status = 'paid' 
        WHERE bill_id = %s
      """, (bill_id,))

      # Insert into receipts table
      cursor.execute("""
        INSERT INTO receipts (bill_id, user_id, amount_paid, payment_date, notes, method)
        VALUES (%s, %s, %s, %s, %s, %s)
      """, (bill_id, user_id, amount_paid, payment_date, notes, "wallet"))

      # Check if user has unpaid bills
      cursor.execute("""
        SELECT COUNT(*) FROM bills 
        WHERE user_id = %s 
        AND status IN ('pending', 'overdue')
      """, (user_id,))
      
      unpaid_bills_count = cursor.fetchone()[0]

      if unpaid_bills_count == 0:
        # Unban the user if they have no unpaid bills
        cursor.execute("UPDATE users SET is_banned = FALSE WHERE user_id = %s", (user_id,))

      conn.commit()
      return {"message": "Payment Successful!"}

    except ValueError as e:
      conn.rollback()
      raise ValueError(e)
    except Exception as e:
      conn.rollback()
      raise Exception(e)
    finally:
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
        SELECT DISTINCT user_id 
        FROM bills 
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