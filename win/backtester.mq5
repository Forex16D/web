#include <Zmq/Zmq.mqh>

input string zmq_address = "tcp://127.0.0.1:5557";
input double lot_size = 0.05;
input int magic_number = 1987;
ENUM_TIMEFRAMES timeframe = PERIOD_H1;

Context context("OHCLSender");
Socket req_socket(context, ZMQ_REQ);

int MAX_TICK = 109;

datetime last_bar_time = 0;
struct TickData {
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
  if (N <= 0) return "[]";

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

    if (i < N - 1) json_data += ",";
  }

  json_data += "]";
  return json_data;
}

void sendData()
{
  string json_data = getLastNBarOHLC(109);

  // Send the data via ZeroMQ
  ZmqMsg request_msg(json_data);

  if (req_socket.send(request_msg)) {
    Print("Data sent successfully.");
  } else {
    Print("Failed to send data.");
    return;
  }

  ZmqMsg reply_msg;
  
  if (!req_socket.recv(reply_msg)) {
    Print("No reply received.");
    return;
  }

  string response = reply_msg.getData();
  Print("Received reply: ", response);

  // Set up trade request
  MqlTradeRequest request = {};
  request.action = TRADE_ACTION_DEAL;  // Market execution
  request.magic = magic_number;        // Set magic number for trade identification
  request.symbol = "EURUSD";           // Set symbol
  request.volume = lot_size;           // Set volume in 0.1 lots
  request.sl = 0;                       // No Stop Loss
  request.tp = 0;                       // No Take Profit
  request.deviation = 10;               // Price deviation allowed
  request.type_filling = ORDER_FILLING_IOC; // Fill or kill
  request.type_time = ORDER_TIME_GTC;   // Good till canceled

  MqlTradeResult result = {};

  // Execute trade based on received signal
  if (response == "buy") {
    request.type = ORDER_TYPE_BUY;
    request.price = SymbolInfoDouble("EURUSD", SYMBOL_ASK); // Buy at ask price
  } 
  else if (response == "sell") {
    request.type = ORDER_TYPE_SELL;
    request.price = SymbolInfoDouble("EURUSD", SYMBOL_BID); // Sell at bid price
  } 
  else {
    return;
  }

  // Send trade request
  if (!OrderSend(request, result)) {
    Print("OrderSend failed. Error code: ", GetLastError());
  } else {
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
