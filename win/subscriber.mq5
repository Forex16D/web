#include <Zmq/Zmq.mqh>
#include <Trade/Trade.mqh>

#define SERVER_URL "http://127.0.0.1:5000"

input string zmq_dealer_address = "tcp://127.0.0.1:5557";
input string zmq_sub_address = "tcp://127.0.0.1:5555";

input double lot_size = 0.01;
input int magic_number = 1987;
input string token="MDVmMDBlNDEtODFlOC00ZDJjLThlNjEtNDkwZGY3NDUxNmVjOmVhYzMyMmJkLTUxNDktNGIxYi1hM2ZlLWY5MzI4MGIwODg2Nzo1NjQ2MGYwMi01M2RlLTQwZWQtODk4ZS0yMjIxNzkxODg5NWM6MTc0Mjc5ODk4Ny6KTWzslZMjnC86wX3oQT-IegGveHThXDgZIIbApXWrDw==";

string portfolio_id;
string expert_id;

Context context("Receiver");
Socket sub_socket(context, ZMQ_SUB);
Socket ack_socket(context, ZMQ_DEALER);

struct WebResponse {
  string result;
  int code;
};

struct ClosedPosition {
  ulong order_id;
  string order_type;
  string symbol;
  double volume;
  double entry_price;
  double exit_price;
  double profit;
  datetime created_at;
};

int OnInit()
{
  // Authenticate with server
  WebResponse response = webRequest("GET", SERVER_URL + "/v1/mt/auth");
  
  if (response.code == 403) {
    Print("Pay! you prick!");
    return INIT_FAILED;
  }
  
  if (response.code != 200) {
    Print("Request failed. Response code: ", response.code);
    return INIT_FAILED;
  }
  
  Print("Request succeeded. Response: ", response.result);
  
  expert_id = ExtractJsonValue(response.result, "expert_id");
  portfolio_id = ExtractJsonValue(response.result, "portfolio_id");

  if (expert_id == "null" || expert_id == "") {
    Print("You are not currently subscribed to an expert.");
    return INIT_FAILED;
  }

  // 🔹 CONNECT THE SUBSCRIBER SOCKET TO THE PUBLISHER
  if (!sub_socket.connect(zmq_sub_address)) {  // Connects to the PUB server
    Print("Failed to connect SUB socket to ZeroMQ at ", zmq_sub_address);
    return INIT_FAILED;
  }

  Print("Connected SUB socket to ZeroMQ at ", zmq_sub_address);

  // 🔹 SUBSCRIBE TO THE ASSIGNED EXPERT_ID
  if (!sub_socket.subscribe("")) {
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
  ZmqMsg topic, received_msg;

  // 🔹 Ensure both messages are received properly
  if (!sub_socket.recv(topic, ZMQ_DONTWAIT) || !sub_socket.recv(received_msg, ZMQ_DONTWAIT)) {
    return;
  }

  string received_expert_id = topic.getData();
  string message = received_msg.getData();

  // 🔹 If needed, filter messages for the current expert ID
  if (received_expert_id != expert_id) return;

  PrintFormat("expert_id: %s\nmessage: %s", received_expert_id, message);


  string action = ExtractJsonValue(message, "action");

  if (action == "open_long" || action == "open_short") {
    string symbol = Symbol();
    ExecuteCloseOrder(action, symbol);
    ExecuteTrade(action, symbol);
  }
}

void OnTimer() {

}


void OnTrade()
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

void ExecuteTrade(string action, string symbol)
{
  MqlTradeRequest request;
  MqlTradeResult result;
  ZeroMemory(request);

  // Get real-time price
  double bid_price = SymbolInfoDouble(symbol, SYMBOL_BID);
  double ask_price = SymbolInfoDouble(symbol, SYMBOL_ASK);

  // Determine the correct price
  double order_price = (action == "open_long") ? ask_price : bid_price;
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
  request.type = (action == "open_long") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
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

void ExecuteCloseOrder(string action, string symbol)
{
    // Validate input
  if (symbol == "" || (action != "open_long" && action != "open_short")) {
    Print("❌ Invalid input parameters for closing order");
    return;
  }
    
  // Determine position type to close based on action
  ENUM_POSITION_TYPE closeType = (action == "open_long") ? POSITION_TYPE_SELL : POSITION_TYPE_BUY;
    
  // Array to store closed positions
  ClosedPosition closedPositions[];
  ArrayResize(closedPositions, 0);
    
  CTrade trade;
    
  // Configure trade object for error handling
  trade.SetDeviationInPoints(10);  // Set acceptable price deviation
  // Track total closed positions
  int closedCount = 0;
  // Iterate through positions
  for (int i = 0; i < PositionsTotal(); i++) {
    // Select position by index - corrected for MQL5
    if (!PositionSelect(PositionGetSymbol(i))) {
      Print("⚠️ Failed to select position at index ", i);
      continue;
    }
    // Check if position matches the specified symbol and type
    if (PositionGetString(POSITION_SYMBOL) != symbol || 
      PositionGetInteger(POSITION_TYPE) != closeType) {
      continue;
    }
    ulong ticket = PositionGetInteger(POSITION_TICKET);
        
    // Attempt to close position
    if (trade.PositionClose(ticket)) {
      // Resize array and add new closed position
      ArrayResize(closedPositions, ArraySize(closedPositions) + 1);
      int lastIndex = ArraySize(closedPositions) - 1;
            
      closedPositions[lastIndex].order_id = ticket;
      closedPositions[lastIndex].symbol = symbol;
      closedPositions[lastIndex].volume = PositionGetDouble(POSITION_VOLUME);
      closedPositions[lastIndex].entry_price = PositionGetDouble(POSITION_PRICE_OPEN);
      closedPositions[lastIndex].order_type = (closeType == POSITION_TYPE_SELL) ? "SELL" : "BUY";
            
      closedCount++;
    } else {
      Print("❌ Failed to close position: ", ticket, 
                " Error: ", trade.ResultRetcode(), " ", trade.ResultRetcodeDescription());
    }
  }
  // Process closed positions
  if (closedCount > 0) {
    // Select deals from last 30 days
    datetime startTime = TimeCurrent() - (30 * 86400);
    HistorySelect(startTime, TimeCurrent());
    // Iterate through closed positions
    for (int i = 0; i < ArraySize(closedPositions); i++) {
      // Find corresponding deal in history
      for (int j = HistoryDealsTotal() - 1; j >= 0; j--) {
        ulong dealTicket = HistoryDealGetTicket(j);
                
        if (HistoryDealGetInteger(dealTicket, DEAL_POSITION_ID) == closedPositions[i].order_id) {
          // Populate additional details
          closedPositions[i].exit_price = HistoryDealGetDouble(dealTicket, DEAL_PRICE);
          closedPositions[i].profit = HistoryDealGetDouble(dealTicket, DEAL_PROFIT);
          closedPositions[i].created_at = (datetime)HistoryDealGetInteger(dealTicket, DEAL_TIME);
                    
          // Send order to database
          SendOrderToDatabase(closedPositions[i]);
                    
          Print("✅ Closed order sent to database: ", closedPositions[i].order_id);
          break;
        }
      }
    }
  } else {
    Print("⚠️ No positions found to close for symbol: ", symbol);
  }
}

void SendOrderToDatabase(ClosedPosition &position)
{
    // Validate input
    if (position.order_id == 0) {
        Print("❌ Invalid position data");
        return;
    }

    // Ensure global variables are defined (portfolio_id, model_id, token)
    string portfolioId = (portfolio_id == "") ? "DEFAULT" : portfolio_id;
    string modelId = (expert_id == "") ? "DEFAULT_MODEL" : expert_id;
    string authToken = (token == "") ? "NONE" : token;

    // Construct JSON payload with error handling
    string jsonData = StringFormat(
        "{\"type\":\"order\", \"order_id\":%lu, \"portfolio_id\":\"%s\", \"model_id\":\"%s\", \"order_type\":\"%s\", \"symbol\":\"%s\", \"profit\":%.2f, \"volume\":%.2f, \"entry_price\":%.5f, \"exit_price\":%.5f, \"token\":\"%s\", \"created_at\":%d}",
        position.order_id, 
        portfolioId, 
        modelId, 
        position.order_type, 
        position.symbol, 
        position.profit, 
        position.volume, 
        position.entry_price, 
        position.exit_price, 
        authToken, 
        position.created_at
    );

    // ZeroMQ message sending with error handling
    ZmqMsg requestMsg(jsonData);
    
    if (ack_socket.send(requestMsg, ZMQ_DONTWAIT)) {
        Print("✅ Order data sent successfully: ", position.order_id);
    } else {
        int errorCode = GetLastError();
        Print("❌ Failed to send order data. Error Code: ", errorCode);
    }
}