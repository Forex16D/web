#include <Zmq/Zmq.mqh>
#include <Trade\Trade.mqh>

#define SERVER_URL "http://127.0.0.1:5000"

input string zmq_address = "tcp://127.0.0.1:5557";
input double lot_size = 0.01;
input int magic_number = 1987;
input string   token="MjJhYjg5YTgtMzkzYy00MmEyLThlOTAtYzY3NTRmOTgyZDM4OjA3NTJkMDcxLTc3NjctNDViMS04ZDlkLWYyNGM4OGQyNDdjOTowNzZmY2QzOS1lNmRhLTRkYmMtYjc3Yy1iZmNhMzgxNGYxYmI6MTc0MTAwNzkxNy64Su9hFmtZfGxb4b_F4f8szzR2GqW14sRVXJtnha7qwg==";
string portfolio_id;
string model_id;

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

TickData tick_buffer[109];
int tick_count = 0;



int OnInit()
{
  string headers = StringFormat("Authorization: Bearer %s\r\n", token);
  char result[];
  char response_body[];
  string response_headers;
  
  int timeout = 5000;

  int response_code = WebRequest("GET", SERVER_URL + "/v1/mt/auth", headers, timeout, response_body, result, response_headers);
  
  if (response_code == 403) {
    Print("Pay! you prick!");
    return INIT_FAILED;
  }
  
  if (response_code != 200) {
    Print("Request failed. Response code: ", response_code);
    return INIT_FAILED;
  }
  
  string jsonString = CharArrayToString(result);
  Print("Request succeeded. Response: ", jsonString);
 
  model_id = ExtractJsonValue(jsonString, "model_id");
  portfolio_id = ExtractJsonValue(jsonString, "portfolio_id");
  
  Print(model_id);
  Print(portfolio_id);
 
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
 
  ZmqMsg reply_msg;
  if (req_socket.recv(reply_msg, ZMQ_DONTWAIT)) {
    Print("Received reply: ", reply_msg.getData());
  } else {
    Print("No message available for receive.");
  }
  
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
//    last_bar_time = current_bar_time;

//    sendData();
//  }
}

void sendData()
{
  string json_data = StringFormat("{\"type\":\"signal_request\", \"portfolio_id\":\"%s\", \"model_id\":\"%s\"}", portfolio_id, model_id);

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
  Print(response == "buy");
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
 
  // Handle trade execution
  if (StringCompare(response, "buy"))
  {
    request.type = ORDER_TYPE_BUY;
  }
  else if (response == "sell")
  {
    request.type = ORDER_TYPE_SELL;
  }
  else if (response == "close_buy" || response == "close_sell")
  {
    ENUM_POSITION_TYPE closeType = (response == "close_buy") ? POSITION_TYPE_BUY : POSITION_TYPE_SELL;
    ulong oldestTicket = 0;
    datetime oldestTime = INT_MAX;
    double entry_price, exit_price, volume, profit;
    string symbol;

    // Find the oldest position to close
    for(int i = 0; i < PositionsTotal(); i++)
    {
      ulong ticket = PositionGetTicket(i);
      if(PositionSelectByTicket(ticket))
      {
        if (PositionGetInteger(POSITION_TYPE) == closeType)
        {
          datetime openTime = PositionGetInteger(POSITION_TIME);
          if (openTime < oldestTime)
          { 
            oldestTime = openTime;
            oldestTicket = PositionGetInteger(POSITION_TICKET);
            symbol = PositionGetString(POSITION_SYMBOL);
            volume = PositionGetDouble(POSITION_VOLUME);
            entry_price = PositionGetDouble(POSITION_PRICE_OPEN);
          }
        }
      }
    }

    // If an old position was found, close it
    if (oldestTicket > 0)
    {
      CTrade trade;
      if (trade.PositionClose(oldestTicket))
      {
        // Get closed order details
        Sleep(1000); // Wait for trade to close before fetching history

        for(int i = 0; i < HistoryDealsTotal(); i++)
        {
          ulong dealTicket = HistoryDealGetTicket(i);
          if (HistoryDealSelect(dealTicket))
          {
            ulong dealOrder = HistoryDealGetInteger(dealTicket, DEAL_POSITION_ID);
            if (dealOrder == oldestTicket)
            {
              exit_price = HistoryDealGetDouble(dealTicket, DEAL_PRICE);
              profit = HistoryDealGetDouble(dealTicket, DEAL_PROFIT);
              datetime close_time = (datetime)HistoryDealGetInteger(dealTicket, DEAL_TIME);

              // Send closed order details
              string close_json = StringFormat(
                "{\"order_id\":\"%d\", \"portfolio_id\":\"%s\", \"model_id\":\"%s\", \"order_type\":\"%s\", \"symbol\":\"%s\", \"profit\":%f, \"volume\":%f, \"entry_price\":%f, \"exit_price\":%f, \"created_at\":%d}",
                oldestTicket, portfolio_id, model_id, (closeType == POSITION_TYPE_BUY ? "BUY" : "SELL"),
                symbol, profit, volume, entry_price, exit_price, close_time
              );

              ZmqMsg close_msg(close_json);
              req_socket.send(close_msg);
              Print("Closed order sent to database: ", oldestTicket);
              break;
            }
          }
        }
      }
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

