import zmq
import time
import json
import signal
from application.helpers.server_log_helper import ServerLogHelper

class ZeroMQPublisher:
  def __init__(self):
    self.context = zmq.Context()
    self.receiver_socket = self.context.socket(zmq.ROUTER)
    self.sender_socket = self.context.socket(zmq.PUB)
    self.kill_now = False

    signal.signal(signal.SIGTERM, self.handle_termination)
    signal.signal(signal.SIGINT, self.handle_termination)

  def start_zmq(self):
    try:
      self.sender_socket.bind("tcp://*:5555")
      ServerLogHelper().log("ZeroMQ sender bound to tcp://*:5555")

      while not self.kill_now:
        expert_id = "expert_123"
        trade_signal = {
          "symbol": "EURUSD",
          "action": "BUY",
          "lot_size": 0.1,
          "price": 1.2
        }

        message = f"{expert_id} {json.dumps(trade_signal)}"
        self.sender_socket.send_string(message)
        ServerLogHelper().log(f"Sent: {message}")

        time.sleep(3)
    except Exception as e:
      ServerLogHelper().error(f"Error in ZeroMQ service: {str(e)}")
    finally:
      self.cleanup()

  def handle_termination(self, signum, frame):
    ServerLogHelper().log(f"Received termination signal: {signum}")
    self.kill_now = True

  def cleanup(self):
    self.sender_socket.close()
    self.context.term()
    ServerLogHelper().log("ZeroMQ service terminated.")

if __name__ == "__main__":
  zmq_service = ZeroMQPublisher()
  zmq_service.start_zmq()
