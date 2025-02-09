import subprocess
import time
import signal
import os

class ZmqScriptRunner:

  def run_publisher(self):
    self.publisher_process = subprocess.Popen(["python3", "-m" "application.zmq.zmq_publisher"])

  def run_receiver(self):
    self.receiver_process = subprocess.Popen(["python3", "-m", "application.zmq.zmq_receiver"])

  def terminate_publisher(self):
    if self.publisher_process.poll() is None:
      os.kill(self.publisher_process.pid, signal.SIGTERM)
      self.publisher_process.wait()
      print(f"Publisher process terminated with exit code {self.publisher_process.returncode}")

  def terminate_receiver(self):
    if self.receiver_process.poll() is None:
      os.kill(self.receiver_process.pid, signal.SIGTERM)
      self.receiver_process.wait()
      print(f"Receiver process terminated with exit code {self.receiver_process.returncode}")
