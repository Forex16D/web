import zmq
import signal
from application.helpers.server_log_helper import ServerLogHelper

class ZeroMQReceiver:
  def __init__(self):
    self.context = zmq.Context()
    self.receiver_socket = self.context.socket(zmq.REP)
    self.kill_now = False

    signal.signal(signal.SIGTERM, self.handle_termination)
    signal.signal(signal.SIGINT, self.handle_termination)

  def start_zmq(self):
    try:
      self.receiver_socket.bind("tcp://*:5557")
      ServerLogHelper().log("ZeroMQ receiver bound to tcp://*:5557")

      while not self.kill_now:
        try:
          message_received = self.receiver_socket.recv_string(flags=zmq.NOBLOCK)
          ServerLogHelper().log(f"Received message: {message_received}")
          
          self.receiver_socket.send_string("ACK")
          ServerLogHelper().log(f"Sent ACK for message: {message_received}")

        except zmq.Again:
          continue


    except Exception as e:
      ServerLogHelper().error(f"Error in ZeroMQ service: {str(e)}")
    finally:
      self.cleanup()

  def handle_termination(self, signum, frame):
    ServerLogHelper().log(f"Received termination signal: {signum}")
    self.kill_now = True
    
  def cleanup(self):
    self.receiver_socket.close()
    self.context.term()
    ServerLogHelper().error("ZeroMQ service terminated.")

if __name__ == "__main__":
  zmq_service = ZeroMQReceiver()
  zmq_service.start_zmq()
