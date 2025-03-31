#include <Zmq/Zmq.mqh>
#include <Trade\Trade.mqh>
#include <Arrays\ArrayObj.mqh>

input string zmq_address = "tcp://127.0.0.1:5557";
input double lot_size = 0.01;
input int magic_number = 1987;
input string model_id = "";

ENUM_TIMEFRAMES timeframe = PERIOD_H1;

Context context("OHCLSender");
Socket req_socket(context, ZMQ_DEALER);

int MAX_TICK = 1;

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

TickData tick_buffer[1];
int tick_count = 0;

int OnInit()
{
  if (!req_socket.connect(zmq_address)) {
    Print("Failed to connect to ZeroMQ server at ", zmq_address);
    return INIT_FAILED;
  }

  Print("Connected to ZeroMQ server at ", zmq_address);
  ZmqMsg request_msg("init");

  if (req_socket.send(request_msg, ZMQ_DONTWAIT)) {
    Print("Data sent: ", "init");
  } else {
    Print("Failed to initialize.");
  }
 
  ZmqMsg reply_msg;
  
  if (!req_socket.recv(reply_msg, ZMQ_DONTWAIT)) {
    Print("No reply received.");
  }

  EventSetTimer(1);
  
  return INIT_SUCCEEDED;
}

void OnTick()
{

  datetime current_bar_time = iTime(Symbol(), timeframe, 0);

  if (current_bar_time != last_bar_time)
  {
    last_bar_time = current_bar_time;

    sendData();
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

void sendData()
{
  string ohlc_data = getLastNBarOHLC(109, Symbol());
  string json_data = StringFormat("{\"type\":\"backtest\", \"portfolio_id\":\"%s\", \"model_id\":\"%s\", \"is_expert\":\"%s\", \"market_data\":\"%s\"}", "b58da0de-08f8-47bc-89df-1d98958cffed", model_id, "true", ohlc_data);

  // Send the data via ZeroMQ
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

  if (!req_socket.recv(reply_msg))
  {
    Print("No reply received.");
    return;
  }

  string response = reply_msg.getData();
  Print("Received reply: ", response);
 
  string action = ExtractJsonValue(response, "action");
  //  string symbol = ExtractJsonValue(response, "symbol");

  if (action == "open_long" || action == "open_short") {
    ExecuteCloseOrder(action, Symbol());
    ExecuteTrade(action, Symbol());
  }
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
    if (symbol == "") {
        Print("❌ Invalid input parameters for closing order");
        return;
    }

    // Determine position type to close based on action
    ENUM_POSITION_TYPE positionTypeToClose = (action == "open_long") ? POSITION_TYPE_SELL : POSITION_TYPE_BUY;
    
    CTrade trade;
    trade.SetDeviationInPoints(10);  // Set acceptable price deviation

    int closedPositionsCount = 0;

    // Iterate through all positions
    for (int i = 0; i < PositionsTotal(); i++) {
        // Select position by index
        ulong ticket = PositionGetTicket(i);
        
        if (ticket == 0) {
            Print("⚠️ Failed to get position ticket at index ", i);
            continue;
        }

        // Check if position matches the specified symbol and type to close
        if (PositionSelectByTicket(ticket) && 
            PositionGetString(POSITION_SYMBOL) == symbol && 
            PositionGetInteger(POSITION_TYPE) == positionTypeToClose) {
            
            // Attempt to close position
            if (trade.PositionClose(ticket)) {
                Print("Closed position: Ticket ", ticket, 
                      " Type: ", EnumToString(positionTypeToClose));
                closedPositionsCount++;
            } else {
                Print("❌ Failed to close position: ", ticket, 
                      " Error: ", trade.ResultRetcode(), " ", trade.ResultRetcodeDescription());
            }
        }
    }

    Print("Total positions closed: ", closedPositionsCount);
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