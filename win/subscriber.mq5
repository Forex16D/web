#include <Zmq/Zmq.mqh>
#include <Trade/Trade.mqh>

#define SERVER_URL "http://127.0.0.1:5000"

input string zmq_dealer_address = "tcp://127.0.0.1:5557";
input string zmq_sub_address = "tcp://127.0.0.1:5555";

input double lot_size = 0.01;
input int magic_number = 1987;
input string token="MjJhYjg5YTgtMzkzYy00MmEyLThlOTAtYzY3NTRmOTgyZDM4OjA3NTJkMDcxLTc3NjctNDViMS04ZDlkLWYyNGM4OGQyNDdjOTowNzZmY2QzOS1lNmRhLTRkYmMtYjc3Yy1iZmNhMzgxNGYxYmI6MTc0MTAwNzkxNy64Su9hFmtZfGxb4b_F4f8szzR2GqW14sRVXJtnha7qwg==";

string portfolio_id;
string expert_id;

Context context("Receiver");
Socket sub_socket(context, ZMQ_SUB);
Socket ack_socket(context, ZMQ_DEALER);

struct WebResponse {
  string result;
  int code;
};

int OnInit()
{
  // Authenticate with server
//  WebResponse response = webRequest("GET", SERVER_URL + "/v1/mt/auth");
  
//  if (response.code == 403) {
//    Print("Pay! you prick!");
//    return INIT_FAILED;
//  }
  
//  if (response.code != 200) {
//    Print("Request failed. Response code: ", response.code);
//    return INIT_FAILED;
//  }
  
//  Print("Request succeeded. Response: ", response.result);
  
//  expert_id = ExtractJsonValue(response.result, "expert_id");
//  portfolio_id = ExtractJsonValue(response.result, "portfolio_id");
  
//  if (expert_id == "null" || expert_id == "") {
//    Print("You are not currently subscribed to an expert.");
 //   return INIT_FAILED;
//  }

  // 🔹 CONNECT THE SUBSCRIBER SOCKET TO THE PUBLISHER
  if (!sub_socket.connect(zmq_sub_address)) {  // Connects to the PUB server
    Print("Failed to connect SUB socket to ZeroMQ at ", zmq_sub_address);
    return INIT_FAILED;
  }

  Print("Connected SUB socket to ZeroMQ at ", zmq_sub_address);

  // 🔹 SUBSCRIBE TO THE ASSIGNED EXPERT_ID
  if (!sub_socket.subscribe(expert_id)) {
    Print("Failed to subscribe to expert ID: ", expert_id);
    return INIT_FAILED;
  }
  
  Print("Subscribed to expert ID: ", expert_id);

  // 🔹 CONNECT ACK SOCKET FOR TRADE CONFIRMATIONS
  if (!ack_socket.connect(zmq_dealer_address)) {  // Connects to DEALER
    Print("Failed to connect ACK socket to ZeroMQ at ", zmq_dealer_address);
    return INIT_FAILED;
  }

  Print("Connected ACK socket to ZeroMQ at ", zmq_dealer_address);

  // 🔹 SEND INIT MESSAGE TO ACK SERVER
  ZmqMsg request_msg("init");
  if (ack_socket.send(request_msg, ZMQ_DONTWAIT)) {
    Print("Data sent: ", "init");
  } else {
    Print("Failed to send init message.");
  }

  // 🔹 SET TIMER TO RECEIVE MESSAGES
  EventSetTimer(1);
  
  return INIT_SUCCEEDED;
}


void OnDeinit(const int reason)
{
  EventKillTimer();
  sub_socket.disconnect("close");
  ack_socket.disconnect("close");
  Print("Sockets closed.");
}

void OnTick() {

}

void OnTimer() {
  ZmqMsg topic, received_msg;


  if (!sub_socket.recv(topic, ZMQ_DONTWAIT)) return;

  if (!sub_socket.recv(received_msg, ZMQ_DONTWAIT)) return;

  string received_expert_id = topic.getData();
  string message = received_msg.getData();
  
  PrintFormat("expert_id: %s\nmessage: %s", received_expert_id, message);
    // 🔹 Ignore messages not meant for this expert_id
//  if (received_expert_id != expert_id) return;

  Print("Received Signal: ", message);

  // Parse JSON message
  string signal = ExtractJsonValue(message, "signal");
  string symbol = ExtractJsonValue(message, "symbol");
  double price = StringToDouble(ExtractJsonValue(message, "price"));

  ExecuteTrade(signal, symbol, price);
}

void OnTrade()
  {
   
  }


void OnTradeTransaction(const MqlTradeTransaction& trans,
                        const MqlTradeRequest& request,
                        const MqlTradeResult& result)
  {

   
  }

WebResponse webRequest(string method, string url) {
  string headers = "Authorization: Bearer " + token + "\r\n";
  char result[];
  char response_body[];
  string response_headers;
  int timeout = 5000;
  int response_code;
  
  ResetLastError();

  // Perform the web request
  response_code = WebRequest(method, url, headers, timeout, response_body, result, response_headers);
  
  WebResponse response;
  response.result = CharArrayToString(result);
  response.code = response_code;

  if(response_code != 200) {
    PrintFormat("Error in WebRequest: %d - %s", response_code, GetLastError());
  }

  return response;
}

string ExtractJsonValue(string json, string key)
{
  string value = "";
  string keyPattern = "\"" + key + "\"";

  int start_pos = StringFind(json, keyPattern);
  if (start_pos == -1) return "";

  start_pos = StringFind(json, ":", start_pos);
  if (start_pos == -1) return "";

  start_pos++; // Move past ':'
  while (StringGetCharacter(json, start_pos) == ' ') start_pos++; // Skip spaces

  char firstChar = StringGetCharacter(json, start_pos);
  int end_pos;

  if (firstChar == '\"') { // String value
    start_pos++; // Move past opening quote
    end_pos = StringFind(json, "\"", start_pos);
  } else { // Non-string value (number, boolean, etc.)
    end_pos = StringFind(json, ",", start_pos);
    if (end_pos == -1) end_pos = StringFind(json, "}", start_pos);
  }

  if (end_pos == -1) return "";

  value = StringSubstr(json, start_pos, end_pos - start_pos);
  return value;
}

void ExecuteTrade(string action, string symbol, double price)
{
  MqlTradeRequest request;
  MqlTradeResult result;
  ZeroMemory(request);

  // Get real-time price
  double bid_price = SymbolInfoDouble(symbol, SYMBOL_BID);
  double ask_price = SymbolInfoDouble(symbol, SYMBOL_ASK);

  // Determine the correct price
  double order_price = (action == "BUY") ? ask_price : bid_price;
  order_price = NormalizeDouble(order_price, _Digits);

  // Validate the price
  if (order_price <= 0) {
    Print("Trade failed: Invalid price for ", symbol);
    return;
  }

  request.action = TRADE_ACTION_DEAL;
  request.symbol = symbol;
  request.magic = magic_number;
  request.volume = lot_size;
  request.type = (action == "BUY") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
  request.price = order_price;
  request.deviation = 30; // Increased slippage
  request.type_filling = SymbolInfoInteger(symbol, SYMBOL_FILLING_MODE); // Use broker-supported filling mode
  request.type_time = ORDER_TIME_GTC;

  // Send the trade request
  if (!OrderSend(request, result)) {
    Print("Trade failed: ", result.comment, " Code: ", result.retcode);
  } else {
    Print("Trade executed: ", action, " ", symbol, " @ ", order_price);
  }
}
