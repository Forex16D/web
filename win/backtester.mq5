#include <Zmq/Zmq.mqh>
#include <Trade\Trade.mqh>


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

string getLastNBarOHLC(int N)
{
  if (N <= 0)
    return "\"[]\""; // Return an escaped empty array

  string json_data = "[";
  
  for (int i = 0; i < N; i++)
  {
    datetime time = iTime(Symbol(), timeframe, i);
    double open = iOpen(Symbol(), timeframe, i);
    double high = iHigh(Symbol(), timeframe, i);
    double low = iLow(Symbol(), timeframe, i);
    double close = iClose(Symbol(), timeframe, i);
    long volume = iVolume(Symbol(), timeframe, i);

    // Manually escape double quotes by wrapping with backslashes
    json_data += StringFormat("{\\\"time\\\":\\\"%s\\\", \\\"open\\\":%.5f, \\\"high\\\":%.5f, \\\"low\\\":%.5f, \\\"close\\\":%.5f, \\\"volume\\\":%d}",
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
  string ohlc_data = getLastNBarOHLC(1);
  string json_data = StringFormat("{\"type\":\"signal_request\", \"model_id\": \"%s\", \"data\": \"%s\"}", model_id, ohlc_data);
  

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

  if (!req_socket.recv(reply_msg, ZMQ_DONTWAIT))
  {
    Print("No reply received.");
    return;
  }

  string response = reply_msg.getData();
  Print("Received reply: ", response);
 
  // Execute trade based on received signal
  if (response == "buy")
  {
    ExecuteTrade("BUY", "EURUSD", 0);
  }
  else if (response == "sell")
  {
    ExecuteTrade("SELL", "EURUSD", 0);
  }
  else if (response == "close_buy" || response == "close_sell")
  {
    ENUM_POSITION_TYPE closeType = (response == "close_buy") ? POSITION_TYPE_BUY : POSITION_TYPE_SELL;
    ulong oldestTicket = 0;
    datetime oldestTime = INT_MAX;

    // Loop through positions to find the oldest buy/sell position
    for(int i = 0; i < PositionsTotal(); i++)
    {
      ulong ticket = PositionGetTicket(i);
      if(PositionSelectByTicket(ticket))
      {
        if (PositionGetInteger(POSITION_TYPE) == closeType)
        {
          datetime openTime = PositionGetInteger(POSITION_TIME);
          if (openTime < oldestTime)
          { // Find the oldest trade
            oldestTime = openTime;
            oldestTicket = PositionGetInteger(POSITION_TICKET);
          }
        }
      }
    }
    // If an old position was found, close it
    if (oldestTicket > 0)
    {
      CTrade trade;
      trade.PositionClose(oldestTicket);
    }
  }
  else
  {
    return;
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

  Print("Trade Result: retcode = ", result.retcode);
  Print("Trade Details: bid = ", result.bid, " ask = ", result.ask, " price = ", result.price);
}
