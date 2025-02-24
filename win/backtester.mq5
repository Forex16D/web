#include <Zmq/Zmq.mqh>
#include <Trade\Trade.mqh>


input string zmq_address = "tcp://127.0.0.1:5557";
input double lot_size = 0.01;
input int magic_number = 1987;
ENUM_TIMEFRAMES timeframe = PERIOD_H1;

Context context("OHCLSender");
Socket req_socket(context, ZMQ_REQ);

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

TickData tick_buffer[109];
int tick_count = 0;

int OnInit()
{
  if (!req_socket.connect(zmq_address)) {
    Print("Failed to connect to ZeroMQ server at ", zmq_address);
    return INIT_FAILED;
  }

  Print("Connected to ZeroMQ server at ", zmq_address);
  ZmqMsg request_msg("init");

  if (req_socket.send(request_msg)) {
    Print("Data sent: ", "init");
  } else {
    Print("Failed to initialize.");
  }
 
  ZmqMsg reply_msg;
  
  if (!req_socket.recv(reply_msg)) {
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
    return "[]";

  string json_data = "[";

  for (int i = 0; i < N; i++)
  {
    datetime time = iTime(Symbol(), timeframe, i);
    double open = iOpen(Symbol(), timeframe, i);
    double high = iHigh(Symbol(), timeframe, i);
    double low = iLow(Symbol(), timeframe, i);
    double close = iClose(Symbol(), timeframe, i);
    long volume = iVolume(Symbol(), timeframe, i);

    json_data += StringFormat("{\"time\":\"%s\", \"open\":%.5f, \"high\":%.5f, \"low\":%.5f, \"close\":%.5f, \"volume\":%d}",
                              TimeToString(time, TIME_DATE | TIME_MINUTES),
                              open, high, low, close, volume);

    if (i < N - 1)
      json_data += ",";
  }

  json_data += "]";
  return json_data;
}

void sendData()
{
  string json_data = getLastNBarOHLC(109);

  // Send the data via ZeroMQ
  ZmqMsg request_msg(json_data);

  if (req_socket.send(request_msg))
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

  // Set up trade request
  MqlTradeRequest request = {};
  request.action = TRADE_ACTION_DEAL;       
  request.magic = magic_number;             
  request.symbol = "EURUSD";               
  request.volume = lot_size;               
  request.sl = 0;                         
  request.tp = 0;                         
  request.deviation = 10;                  
  request.type_filling = ORDER_FILLING_IOC;
  request.type_time = ORDER_TIME_GTC;      
  request.price = iClose(Symbol(), timeframe, 1);
  
  MqlTradeResult result = {};
 
  // Execute trade based on received signal
  if (response == "buy")
  {
    request.type = ORDER_TYPE_BUY;
//    request.price = SymbolInfoDouble("EURUSD", SYMBOL_ASK); // Buy at ask price
  }
  else if (response == "sell")
  {
    request.type = ORDER_TYPE_SELL;
//    request.price = SymbolInfoDouble("EURUSD", SYMBOL_BID); // Sell at bid price
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

  // Send trade request
  if (!OrderSend(request, result))
  {
    Print("OrderSend failed. Error code: ", GetLastError());
  }
  else
  {
    Print("Order placed successfully. Order ID: ", result.order);
  }

  // Debugging trade result details
  Print("Trade Result: retcode = ", result.retcode);
  Print("Trade Details: bid = ", result.bid, " ask = ", result.ask, " price = ", result.price);
}

void OnDeinit(const int reason)
{
  req_socket.disconnect("close");
  Print("ZeroMQ connection closed.");
  EventKillTimer();
}
