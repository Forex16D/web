from psycopg2.extras import RealDictCursor # type: ignore
from datetime import datetime, timedelta
import calendar

class BillingService:
  def __init__(self, db_pool):
    self.db_pool = db_pool
  
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

      net_amount = max(profit * commission, 0)  # Ensure non-negative
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

  def pay_bill(self, user_id, bill_id, image_path, payment_method, reference_number, payment_date, notes):
    try:
        conn = self.db_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT net_amount FROM bills WHERE bill_id = %s", (bill_id,))
        bill = cursor.fetchone()

        if not bill:
          raise ValueError("Bill not found!")

        amount_paid = bill[0]

        cursor.execute("UPDATE bills SET status = 'paid' WHERE bill_id = %s", (bill_id,))
        cursor.execute("""
          INSERT INTO receipts (
            bill_id, user_id, amount_paid, receipt_image, payment_method, reference_number, payment_date, notes
          ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (bill_id, user_id, amount_paid, image_path, payment_method, reference_number, payment_date, notes))

        conn.commit()
        return {"message": "Payment Success!"}

    except Exception as e:
      conn.rollback()
      raise Exception(f"Error processing payment: {str(e)}")
    
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

        
