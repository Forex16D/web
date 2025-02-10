#include <Zmq/Zmq.mqh>  // ZeroMQ Library

#define SERVER_URL "http://127.0.0.1:5000/v1/mt/auth"

input string   zmq_publisher_address="tcp://127.0.0.1:5555";
input string   zmq_receiver_address="tcp://127.0.0.1:5557";
input string   expert_id="expert123";
input string   token="MzlkN2I2NmEtZjAyMC00ODE1LWJmMzAtZDU3NWE1ZGE3NzY2OmUwMjFlZTJiLWVkYWItNGQwMS04OTRkLTNmOGI3NTQxOGRmNjpkZWEyZGE4ZS0zMmI2LTQ3NmYtYTQwNi05OThmYzllZjJhNDc6MTczODk4NDQzNC5LB_zN3LFdOyfZzvhRetkEyNyMN0kkGrnJA5IZDuLPyA==";

Context context("AccountSender");
Socket sub_socket(context, ZMQ_SUB);
Socket req_socket(context, ZMQ_REQ);

int OnInit() {
   EventSetTimer(1);
   bool isAuthorized = checkAuth();
   if (!isAuthorized)
      return INIT_FAILED;

    initConnection();
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
  EventKillTimer();
  sub_socket.disconnect("close");
  req_socket.disconnect("close");
  Print("Disconnected from ZeroMQ server.");
}

void OnTimer() {
   ZmqMsg message;
   if (sub_socket.recv(message)) {
      string data = message.getData();
      Print("Received message: ", data);
   } else {
      Print("No message received.");
   }
}

void OnTick() {
   
}

int checkAuth() {
   string headers = StringFormat("Authorization: Bearer %s\r\n", token);
   char result[];
   char response_body[];
   string response_headers;
 
   int timeout = 5000;

   int response_code = WebRequest("GET", SERVER_URL, headers, timeout, response_body, result, response_headers);
   
   if (response_code != 200) {
      Print("Request failed. Response code: ", response_code);
      return false;
   }
   
   Print("Request succeeded. Response: ", CharArrayToString(result));
   return true;
}

void initConnection()
{
  if (!sub_socket.connect(zmq_publisher_address)) {
    Print("Failed to connect to server: ", GetLastError());
  }

  sub_socket.subscribe(expert_id);

  if (!req_socket.connect(zmq_receiver_address)) {
    Print("Failed to connect to server: ", GetLastError());
  }

  Print("Connected to ZeroMQ server for sending data: ", zmq_receiver_address);
}

void sendData()
{
//  string user_data = "User Data: Hello World!";
//  ZmqMsg request_msg;
   
//   request_msg.setData(user_data);

//   if (req_socket.send(request_msg)) {
//      Print("Data sent: ", user_data);
//   } else {
//      Print("Failed to send data.");
//  }

//   ZmqMsg reply_msg;
//   if (req_socket.recv(reply_msg)) {
//      string response = reply_msg.getData();
//      Print("Received reply: ", response);
//   } else {
//      Print("No reply received.");
//   }
}