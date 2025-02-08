import zmq
import time
import json
from application.helpers.server_log_helper import ServerLogService

class ZeroMQService:
  def __init__(self):
    self.context = zmq.Context()
    self.sender_socket = self.context.socket(zmq.PUB)
    self.receiver_socket = self.context.socket(zmq.REP)

  def start_zmq(self):
    try:
      self.sender_socket.setsockopt(zmq.LINGER, 0)
      self.receiver_socket.setsockopt(zmq.LINGER, 0)
       
      self.sender_socket.bind("tcp://*:5555")
      self.receiver_socket.bind("tcp://*:5557")

      ServerLogService().log("ZeroMQ sender bound to tcp://*:5555")
      ServerLogService().log("ZeroMQ receiver bound to tcp://*:5557")

      while True:
        expert_id = "expert_123"
        trade_signal = {
          "symbol": "EURUSD",
          "action": "BUY",
          "lot_size": 0.1,
          "price": 1.2
        }

        message = f"{expert_id} {json.dumps(trade_signal)}"
        self.sender_socket.send_string(message)
        ServerLogService().log(f"Sent: {message}")
        
        message_received = self.receiver_socket.recv_string()
        ServerLogService().log(f"Received message: {message_received}")
        
        self.receiver_socket.send_string("ACK")
        ServerLogService().log(f"Sent ACK for message: {message_received}")
        
        time.sleep(3) # Debug Delay

    except Exception as e:
      ServerLogService().error(f"Error in ZeroMQ service: {str(e)}")
    finally:
      self.cleanup()

  def cleanup(self):
    self.sender_socket.close()
    self.receiver_socket.close()
    self.context.term()
    ServerLogService().error("ZeroMQ service terminated.")

