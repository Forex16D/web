import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

class ServerLogHelper:
    @staticmethod
    def log(message):
        logging.info(message)

    @staticmethod
    def error(message):
        logging.error(message)
