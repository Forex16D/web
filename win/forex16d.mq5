#include <Zmq/Zmq.mqh>
#include <Trade\Trade.mqh>

#define SERVER_URL "http://127.0.0.1:5000"

input string zmq_address = "tcp://127.0.0.1:5557";
input double lot_size = 0.01;
input int magic_number = 1987;
input string token="MjJhYjg5YTgtMzkzYy00MmEyLThlOTAtYzY3NTRmOTgyZDM4OjA3NTJkMDcxLTc3NjctNDViMS04ZDlkLWYyNGM4OGQyNDdjOTowNzZmY2QzOS1lNmRhLTRkYmMtYjc3Yy1iZmNhMzgxNGYxYmI6MTc0MTAwNzkxNy64Su9hFmtZfGxb4b_F4f8szzR2GqW14sRVXJtnha7qwg==";

string portfolio_id;
string model_id;
string is_expert;

ENUM_TIMEFRAMES timeframe = PERIOD_H1;

Context context("OHCLSender");
Socket req_socket(context, ZMQ_DEALER);

int MAX_TICK = 109;

datetime last_bar_time = 0;
struct TickData
{
  datetime time;
  double open;
  double high;
  double low;
  double close;
  long volume;
};

struct WebResponse {
  string result;
  int code;
};

TickData tick_buffer[109];
int tick_count = 0;

int OnInit()
{
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
 
  model_id = ExtractJsonValue(response.result, "model_id");
  portfolio_id = ExtractJsonValue(response.result, "portfolio_id");
  is_expert = ExtractJsonValue(response.result, "is_expert");

  req_socket.setLinger(100);
 
  if (!req_socket.connect(zmq_address)) {
    Print("Failed to connect to ZeroMQ server at ", zmq_address);
    return INIT_FAILED;
  }
 
  Print("Connected to ZeroMQ server at ", zmq_address);
  ZmqMsg request_msg("init");

  if (req_socket.send(request_msg, ZMQ_DONTWAIT)) {
    Print("Data sent: ", "init");
  } else {
    Print("Failed to send message or operation was non-blocking.");
  }
 
//  ZmqMsg reply_msg;
//  if (req_socket.recv(reply_msg, ZMQ_DONTWAIT)) {
//    Print("Received reply: ", reply_msg.getData());
//  } else {
//    Print("No message available for receive.");
//  }
  
  EventSetTimer(5);
    
  return INIT_SUCCEEDED;
}

void OnTimer(void)
{
  sendData();
}

void OnTick()
{
//  datetime current_bar_time = iTime(Symbol(), timeframe, 0);

//  if (current_bar_time != last_bar_time)
//  {
 //   last_bar_time = current_bar_time;

//    sendData();
//  }
}

void sendData()
{
  string json_data = StringFormat("{\"type\":\"signal_request\", \"portfolio_id\":\"%s\", \"model_id\":\"%s\", \"is_expert\":\"%s\"}", portfolio_id, model_id, is_expert);

  // Send request via ZeroMQ
  ZmqMsg request_msg(json_data);

  if (req_socket.send(request_msg, ZMQ_DONTWAIT))
  {
    Print("Data sent successfully.");
  }
  else
  {
    Print("Failed to send data.");
    return;
  }


  ZmqMsg reply_msg;
  if (req_socket.recv(reply_msg, ZMQ_DONTWAIT)) {
    Print("Received reply: ", reply_msg.getData());
  } else {
    Print("No message received.");
  }
  
  uchar replyMessage[];

  reply_msg.getData(replyMessage);
  string response = CharArrayToString(replyMessage);
  Print(response);
  // Set up trade request
 
  // Handle trade execution
  string action = ExtractJsonValue(response, "action");
  string symbol = ExtractJsonValue(response, "symbol");
  string price_string = ExtractJsonValue(response, "price");
  double price = StringToDouble(price_string);
  
  if (action == "BUY" || action == "SELL")
    ExecuteTrade(action, symbol, price);
  
  else if (action == "close_buy" || action == "close_sell")
  {
    ENUM_POSITION_TYPE closeType = (response == "close_buy") ? POSITION_TYPE_BUY : POSITION_TYPE_SELL;
    ExecuteCloseOrder(closeType);
  }
  else
    return;
}

void OnDeinit(const int reason)
{
  ZmqMsg request_msg("end");

  if (req_socket.send(request_msg))
  {
    Print("End message sent successfully.");
  }
  else
  {
    Print("Failed to send message.");
    return;
  }
  req_socket.disconnect("close");
  Print("ZeroMQ connection closed.");
  EventKillTimer();
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

void ExecuteCloseOrder(ENUM_POSITION_TYPE closeType)
{
    ulong oldestTicket = 0;
    datetime oldestTime = LONG_MAX;
    double entry_price = 0.0, exit_price = 0.0, volume = 0.0, profit = 0.0;
    string symbol;

    // Find the oldest position matching the close type
    for (int i = 0; i < PositionsTotal(); i++) {
      
      if (PositionSelect(Symbol())) {
        datetime openTime = PositionGetInteger(POSITION_TIME);
        if (openTime < oldestTime) {
            oldestTime = openTime;
            oldestTicket = PositionGetInteger(POSITION_TICKET);
            symbol = PositionGetString(POSITION_SYMBOL);
            volume = PositionGetDouble(POSITION_VOLUME);
            entry_price = PositionGetDouble(POSITION_PRICE_OPEN);
        }
      }
    }
    
    
    if (oldestTicket > 0) {
        CTrade trade;
        if (trade.PositionClose(oldestTicket)) {
            Sleep(1000); // Allow history to update

            for (int i = 0; i < HistoryDealsTotal(); i++) {
                ulong dealTicket = HistoryDealGetTicket(i);
                if (HistoryDealSelect(dealTicket) && HistoryDealGetInteger(dealTicket, DEAL_POSITION_ID) == oldestTicket) {
                    exit_price = HistoryDealGetDouble(dealTicket, DEAL_PRICE);
                    profit = HistoryDealGetDouble(dealTicket, DEAL_PROFIT);
                    datetime close_time = (datetime)HistoryDealGetInteger(dealTicket, DEAL_TIME);

                    sendOrder(oldestTicket, closeType == POSITION_TYPE_BUY ? "BUY" : "SELL", symbol, profit, volume, entry_price, exit_price, close_time);
                    Print("✅ Closed order sent to database: ", oldestTicket);
                    break;
                }
            }
        } else {
            Print("❌ Failed to close position: ", oldestTicket);
        }
    } else {
        Print("⚠ No position found to close.");
    }
}


void sendOrder(ulong order_id, string order_type, string symbol, 
               double profit, double volume, double entry_price, double exit_price, datetime created_at) 
{
  string json_data = StringFormat(
    "{\"type\":\"order\", \"order_id\":%d, \"portfolio_id\":\"%s\", \"model_id\":\"%s\", \"order_type\":\"%s\", \"symbol\":\"%s\", \"profit\":%.2f, \"volume\":%.2f, \"entry_price\":%.5f, \"exit_price\":%.5f, \"created_at\":%d}",
    order_id, portfolio_id, model_id, order_type, symbol, profit, volume, entry_price, exit_price, created_at
  );

  ZmqMsg request_msg(json_data);
  
  if (req_socket.send(request_msg, ZMQ_DONTWAIT)) {
    Print("Order data sent successfully.");
  } else {
    Print("Failed to send order data.");
  }
}

double FindEntryPrice(ulong position_id)
{
  for (int i = 0; i < HistoryDealsTotal(); i++)
  {
    ulong dealTicket = HistoryDealGetTicket(i);
    if (HistoryDealSelect(dealTicket))
    {
      ulong dealOrder = HistoryDealGetInteger(dealTicket, DEAL_POSITION_ID);
      int dealEntryType = HistoryDealGetInteger(dealTicket, DEAL_ENTRY);
      
      // Check if it's the same position AND it's an entry deal
      if (dealOrder == position_id && dealEntryType == DEAL_ENTRY_IN)
      {
        return HistoryDealGetDouble(dealTicket, DEAL_PRICE);
      }
    }
  }
  return 0.0; // Default if not found
}
