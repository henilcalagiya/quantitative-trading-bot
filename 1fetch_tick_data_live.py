from fyers_apiv3.FyersWebsocket import data_ws
from fyers_apiv3 import fyersModel
with open('access_token.txt','r') as a:
    access_token=a.read()
import credentials as cd
from nsepython import *
from functions import *
from dictionaries import *

# Initialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,is_async=False, log_path="")

def onmessage(message):
    insert_ticks(message)

def onerror(message):
    print("Error:", message)

def onclose(message):
    print("Connection closed:", message)

def onopen():
    data_type = "SymbolUpdate"
    # Want to call Create Tables here for range of 30%.

    # get ltp of Banknifty from Fyers API
    ltp = get_ltp()
    # print("last traded price of Banknifty : ", ltp)

    # Get Expiry Date to trade from nsepython library
    date, month, year, is_weekly_expiry = determine_expiry_dates()
    print("Expiry Date : ", date, month, year)

    # Get Dictionary of the instrument_tokens and Trading Symbols and write both Dictionaries and all options symbols in dictionaries.py
    get_dict_of_instrumentkey_and_symbol(date, month, year, is_weekly_expiry)

    # get current future index and write into dictionaries.py
    symbol_for_monthly_futures(month, year)

    # Create Tables for all available options strike prices
    create_tables(all_option_symbols)

    # Create Tables for current future index
    create_tables(current_future_index)

    # Now I have all symbols and i want to get just 48 symbols from that which are near the price
    # Plan :
    # - Can make an list named as options_symbols_to_trade
    option_symbols_to_trade = get_symbols_to_trade(ltp,all_option_symbols,current_future_index)

    # banknfity_symbols = get_banknifty_symbols(ltp, trade_expiry, is_weekly_expiry)
    # print("banknfity_symbols",banknfity_symbols)
    
    fyers.subscribe(symbols=option_symbols_to_trade, data_type=data_type)
    print("Symbols Subscribed")
    fyers.keep_running()

# Create a FyersDataSocket instance with the provided parameters
fyers = data_ws.FyersDataSocket(
    access_token=access_token,       
    log_path="",                     
    litemode=True,                  
    write_to_file=False,             
    reconnect=True,                  
    on_connect=onopen,               
    on_close=onclose,                
    on_error=onerror,                
    on_message=onmessage             
)

# Establish a connection to the Fyers WebSocket
fyers.connect()