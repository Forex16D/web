#include <Zmq/Zmq.mqh>
#include <Trade\Trade.mqh>
#include <Arrays\ArrayObj.mqh>

#define SERVER_URL "http://127.0.0.1:5000"

input string zmq_address = "tcp://127.0.0.1:5557";
input double lot_size = 0.01;
input int magic_number = 1987;
input string token="";

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

TickData tick_buffer[109];
int tick_count = 0;

int OnInit()
{
  WebResponse response = webRequest("GET", SERVER_URL + "/v1/mt/auth");
 
  if (response.code == 401) {
    Print("Invalid Token!");
    Deinit();
    return INIT_FAILED;
  }

  if (response.code == 403) {
    Print("Access denied!");
    Deinit();
    return INIT_FAILED;
  }
  
  if (response.code != 200) {
    Print("Request failed. Response code: ", response.code);
    Deinit();
    return INIT_FAILED;
  }
  
  Print("Request succeeded. Response: ", response.result);
 
  model_id = ExtractJsonValue(response.result, "model_id");
  portfolio_id = ExtractJsonValue(response.result, "portfolio_id");
  is_expert = ExtractJsonValue(response.result, "is_expert");

  req_socket.setLinger(100);
 
  if (!req_socket.connect(zmq_address)) {
    Print("Failed to connect to ZeroMQ server at ", zmq_address);
    Deinit();
    return INIT_FAILED;
  }
 
  Print("Connected to ZeroMQ server at ", zmq_address);
  
  ZmqMsg request_msg("init " + portfolio_id);

  if (req_socket.send(request_msg, ZMQ_DONTWAIT)) {
    Print("Data sent: ", "init " + portfolio_id);
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
//  ZmqMsg request_msg("heartbeat " + portfolio_id);

//  if (req_socket.send(request_msg, ZMQ_DONTWAIT)) {
//    Print("Data sent: ", "heartbeat " + portfolio_id);
//  } else {
//    Print("Failed to send message or operation was non-blocking.");
//  }
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
  string ohlc = getLastNBarOHLC(109, Symbol());
  string json_data = StringFormat("{\"type\":\"signal_request\", \"portfolio_id\":\"%s\", \"model_id\":\"%s\", \"is_expert\":\"%s\", \"market_data\":\"%s\"}", portfolio_id, model_id, is_expert, ohlc);

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
  
  if (response == "User is banned!") {
    Print("User is banned, stopping EA!");
    ExpertRemove();
  }
  // Set up trade request
 
  // Handle trade execution
  string action = ExtractJsonValue(response, "action");
//  string symbol = ExtractJsonValue(response, "symbol");
  Print(action);
  if (action == "open_long" || action == "open_short")
    ExecuteTrade(action, Symbol());
  
  else if (action == "close_buy" || action == "close_sell")
  {
    ENUM_POSITION_TYPE closeType = (response == "close_buy") ? POSITION_TYPE_BUY : POSITION_TYPE_SELL;
    ExecuteCloseOrder(closeType, Symbol());
  }
  else
    return;
}

void OnDeinit(const int reason)
{
  Deinit();
}

void Deinit() {
  ZmqMsg request_msg("end "  + portfolio_id);
  
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

void ExecuteCloseOrder(ENUM_POSITION_TYPE closeType, string symbol)
{
    // Validate input
    if (symbol == "" || (closeType != POSITION_TYPE_BUY && closeType != POSITION_TYPE_SELL)) {
        Print("❌ Invalid input parameters for closing order");
        return;
    }

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
            closedPositions[lastIndex].order_type = (closeType == POSITION_TYPE_BUY) ? "BUY" : "SELL";
            
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
    string modelId = (model_id == "") ? "DEFAULT_MODEL" : model_id;
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
    
    if (req_socket.send(requestMsg, ZMQ_DONTWAIT)) {
        Print("✅ Order data sent successfully: ", position.order_id);
    } else {
        int errorCode = GetLastError();
        Print("❌ Failed to send order data. Error Code: ", errorCode);
    }
}

string getLastNBarOHLC(int N, string symbol)
{
  if (N <= 0)
    return "\"[]\""; // Return an escaped empty array

  string json_data = "[";
  
  for (int i = 0; i < N; i++)
  {
    datetime time = iTime(symbol, timeframe, i);
    double open = iOpen(symbol, timeframe, i);
    double high = iHigh(symbol, timeframe, i);
    double low = iLow(symbol, timeframe, i);
    double close = iClose(symbol, timeframe, i);
    long volume = iVolume(symbol, timeframe, i);

    // Manually escape double quotes by wrapping with backslashes
    json_data += StringFormat("{\\\"time\\\":\\\"%s\\\", \\\"open\\\":%.5f, \\\"high\\\":%.5f, \\\"low\\\":%.5f, \\\"close\\\":%.5f, \\\"tick_volume\\\":%d}",
                              TimeToString(time, TIME_DATE | TIME_MINUTES),
                              open, high, low, close, volume);

    if (i < N - 1)
      json_data += ",";
  }

  json_data += "]";

  // Wrap the entire JSON data in escaped double quotes for correct formatting
  return json_data;
}
