import zmq
import time

def start_zmq():
  context = zmq.Context()
  req_socket = context.socket(zmq.REQ)
  req_socket.connect("tcp://127.0.0.1:5557")
  while True:
    req_socket.send_string("Hello from client")
    print("Sending Message...")
    reply = req_socket.recv_string()
    print(f"Received reply: {reply}")
    time.sleep(1)    

if __name__ == "__main__":
  start_zmq()
