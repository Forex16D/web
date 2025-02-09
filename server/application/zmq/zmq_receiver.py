import zmq
import signal
from application.helpers.server_log_helper import ServerLogService

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
      ServerLogService().log("ZeroMQ receiver bound to tcp://*:5557")

      while not self.kill_now:
        try:
          message_received = self.receiver_socket.recv_string(flags=zmq.NOBLOCK)
          ServerLogService().log(f"Received message: {message_received}")
          
          self.receiver_socket.send_string("ACK")
          ServerLogService().log(f"Sent ACK for message: {message_received}")

        except zmq.Again:
          continue


    except Exception as e:
      ServerLogService().error(f"Error in ZeroMQ service: {str(e)}")
    finally:
      self.cleanup()

  def handle_termination(self, signum, frame):
    ServerLogService().log(f"Received termination signal: {signum}")
    self.kill_now = True
    
  def cleanup(self):
    self.receiver_socket.close()
    self.context.term()
    ServerLogService().error("ZeroMQ service terminated.")

if __name__ == "__main__":
  zmq_service = ZeroMQReceiver()
  zmq_service.start_zmq()
