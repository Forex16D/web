from flask import jsonify
from psycopg2.extras import RealDictCursor
import jwt
import datetime
import uuid
import os

def get_portfolios_by_user(user_id, current_user):
  
  return

def manage_portfolio(portfolio_id, current_user):
  pass
  
def get_all_portfolios(request, db_pool):
  conn = db_pool.get_connection()