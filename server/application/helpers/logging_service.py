import logging
import datetime

class LoggingHelper:
  @staticmethod
  def setup_logging():
    if not logging.getLogger().hasHandlers():
      logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

  @staticmethod
  def server_log():
    LoggingHelper.setup_logging()
    x = datetime.datetime.now()
    log_filename = f"/app/logs/server_{x.strftime('%Y_%m')}.log"
    logging.info("Server log entry")
    
    with open(log_filename, "a") as log_file:
      log_file.write(f"{x} - Server log entry\n")
