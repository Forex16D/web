import logging

class ServerLogService:
  def __init__(self):
    if not logging.getLogger().hasHandlers():
      logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

  def log(self, message):
    logging.info(message)

  def log_error(self, message):
    logging.error(message)
