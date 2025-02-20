import datetime

class Logging:
  @staticmethod
  def server_log(message):
   
    x = datetime.datetime.now()
    log_filename = f"/app/logs/server_{x.strftime('%Y_%m')}.log"
    
    with open(log_filename, "a") as log_file:
      log_file.write(f"{x} - {message}\n")

  @staticmethod
  def user_log(message):
    x = datetime.datetime.now()
    log_filename = f"/app/logs/user_{x.strftime('%Y_%m')}.log"
    
    with open(log_filename, "a") as log_file:
      log_file.write(f"{x} - {message}\n")

  @staticmethod
  def admin_log(message):
    x = datetime.datetime.now()
    log_filename = f"/app/logs/admin_{x.strftime('%Y_%m')}.log"
    
    with open(log_filename, "a") as log_file:
      log_file.write(f"{x} - {message}\n")