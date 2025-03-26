import threading
import time
import schedule
from datetime import datetime
from application.helpers.server_log_helper import ServerLogHelper
from application.container import container

def monthly_billing_task():
  today = datetime.today()
  if today.day == 1:
    ServerLogHelper.log("Running monthly billing task...")
    container.billing_service.bill_all()
    ServerLogHelper.log("Monthly billing task completed.")

def check_unpaid_bills():
  ServerLogHelper.log("Checking unpaid bills...")
  container.billing_service.check_unpaid_bills()
  ServerLogHelper.log("Unpaid bills checked.")

def pay_expert():
  container.bill_service.pay_all_expert()

def run_scheduler():
  schedule.every().day.at("00:00").do(pay_expert)
  schedule.every().day.at("00:00").do(monthly_billing_task)
  schedule.every().day.at("00:00").do(check_unpaid_bills)

  while True:
    schedule.run_pending()
    time.sleep(60)
