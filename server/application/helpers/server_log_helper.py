import logging

class ServerLogHelper:
  def __init__(self):
    if not logging.getLogger().hasHandlers():
      logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

  def log(self, message):
    logging.info(message)

  def error(self, message):
    logging.error(message)
