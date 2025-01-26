from psycopg2 import pool
import threading

class DatabasePool:
  _instance = None
  _lock = threading.Lock()

  def __new__(cls, *args, **kwargs):
    if not cls._instance:
      with cls._lock:
        if not cls._instance:
          cls._instance = super(DatabasePool, cls).__new__(cls)
    return cls._instance

  def __init__(self):
    if not hasattr(self, "_pool"):
      try:
        self._pool = pool.SimpleConnectionPool(
          minconn=1,
          maxconn=10,
          database="forex16d",
          user="admin",
          password="admin",
          host="postgres",
          port=5432,
        )
        print("Connection pool created successfully.")
      except Exception as e:
        print(f"Failed to create connection pool: {e}")
        self._pool = None

  def get_connection(self):
    if self._pool:
      return self._pool.getconn()

  def release_connection(self, conn):
    if self._pool:
      self._pool.putconn(conn)

  def close_all(self):
    if self._pool:
      self._pool.closeall()
