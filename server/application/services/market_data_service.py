import os
from psycopg2.extras import RealDictCursor  # type: ignore
from application.helpers.server_log_helper import ServerLogHelper

class MarketDataService:
  def __init__(self, db_pool):
    self.db_pool = db_pool

  def import_from_csv(self, file_path):  # Receive file path as parameter
    conn = self.db_pool.get_connection()
    try:
      # Extract the file name from the provided path
      file_name = os.path.basename(file_path)
      ServerLogHelper().log(f"Importing data from file: {file_name}")

      # Open the CSV file and copy data into the database
      with open(file_path, "r") as f:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.copy_from(f, "market_data", sep="\t", columns=("timestamp", "open", "high", "low", "close", "volume"))

      ServerLogHelper().log(f"Waiting...")
      conn.commit()
      ServerLogHelper().log(f"Done")
    except Exception as e:
      conn.rollback()  # Rollback in case of error
      ServerLogHelper().log(f"Error importing data from {file_name}: {e}")
    finally:
      conn.close()
