import time
import pytz
import sqlite3
# from input import *
from dictionaries import *
# from kite import *
from upstox_functions import *
from process_function import *
from datetime import datetime, timedelta, timezone
with open('upstox_access_token.txt','r') as a:
    upstox_access_token=a.read()

quantity = 15
active_positions = []

# Function to get the current time in Indian Standard Time (IST)
def get_current_time_ist():
    # Get the current UTC time
    utc_time = datetime.now(timezone.utc)
    # Convert UTC time to IST time (IST is UTC+5:30)
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime('%Y-%m-%d %H:%M:%S')

# Get the current time in IST

current_epoch_time = time.time()

# Set the timezone to Indian Standard Time (IST)
indian_tz = pytz.timezone('Asia/Kolkata')

# Get the current datetime in IST
now_ist = datetime.now(indian_tz)
print("Current Time :", now_ist)

# Format the date as DDMMMYY
date_suffix = now_ist.strftime('%d%b%y').upper()

# Access the tick data database name with the date suffix
tick_db_name = f'data/tick_data/tickdata_{date_suffix}.db'
db_tick = sqlite3.connect(tick_db_name, check_same_thread=False)
cursor_tick = db_tick.cursor()

# Access the candle data database name with the date suffix
candle_db_name = f'data/candle_data/candledata_{date_suffix}.db'
db_candle = sqlite3.connect(candle_db_name, check_same_thread=False)
cursor_candle = db_candle.cursor()


# Get the Name of the Index Tables
index_table = (current_future_index[0])[4:]

# Get the Name of the All Option Tables
symbols = [i[4:] for i in all_option_symbols]

def main():
    call_func_every_5_sec()

def call_func_every_5_sec():

    while True:
        current_epoch_time = time.time()

        if current_epoch_time % 5 <= 0.001:

            ohlc_done = []
            print("Current Active Positions ", active_positions)

            # Check the LTP of the Banknifty
            # Can Fetch it with query of tick data table
            ltp = get_latest_index_ltp()

            # Based on the LTP decide the Strike Prices to trade both CE and PE.
            CE_Strike_Price, PE_Strike_Price = choose_strike_prices(ltp[0])   # Here we get value like 52654CE

            # Get Symbols for both strike prices
            CE_symbol = [symbol for symbol in symbols if CE_Strike_Price in symbol][0]
            PE_symbol = [symbol for symbol in symbols if PE_Strike_Price in symbol][0]
            print(CE_symbol, PE_symbol)

            # Now just for that Strike Price do calculate all things. and check if there is an trade then do place trade.
            get_ohlc(CE_symbol)
            get_ohlc(PE_symbol)
            ohlc_done.append(CE_symbol)
            ohlc_done.append(PE_symbol)

            cursor_candle.execute(f"SELECT Direction FROM {CE_symbol}candles ORDER BY Timestamp DESC LIMIT 2")
            directions_CE = cursor_candle.fetchall()  # This will fetch the last two rows

            cursor_candle.execute(f"SELECT Direction FROM {PE_symbol}candles ORDER BY Timestamp DESC LIMIT 2")
            directions_PE = cursor_candle.fetchall()  # This will fetch the last two rows
            # print('PE Directions ',directions_PE)

            # if any of them has Supertrend Changed positively then
            if directions_CE and len(directions_CE) == 2 and directions_PE and len(directions_PE) == 2:
                # Since fetchall returns a list of tuples, and we are interested in the first element of each tuple which is Direction
                last_direction_CE = directions_CE[0][0]
                second_last_direction_CE = directions_CE[1][0]
                last_direction_PE = directions_PE[0][0]
                second_last_direction_PE = directions_PE[1][0]

                if last_direction_CE == 1 and second_last_direction_CE == -1:
                    # IT'S BUY SIGNAL
                    print("Buy CE", CE_symbol)
                    
                    
                    # ZERODHA
                    # exit_all_trades(kite)
                    # place_buy_order(kite=kite, tradingsymbol= CE_symbol)
                    
                    # UPSTOX
                    # exit_all_intraday_positions(upstox_access_token)
                    
                    # Remove all active positions
                    if active_positions:
                        for active_position in active_positions:
                            cursor_tick.execute(f"SELECT price FROM {active_position} ORDER BY Timestamp DESC LIMIT 1")
                            last_price = cursor_tick.fetchone()
                            current_time_ist = get_current_time_ist()
                            try:
                                with open(f'data/trade_logs/{date_suffix}_Trades.txt', 'a') as file:
                                    file.write(f"Sell, Time : {current_time_ist} , {active_position} at {last_price[0]}.\n")
                            except IOError as e:
                                print(f"An error occurred while writing to the file: {e}")
                            active_positions.remove(active_position)

                    # Append CE Symbol in Active Symbols
                    active_positions.append(CE_symbol)

                    # instrument_token = symbol_to_instrument["NSE:"+CE_symbol]
                    # place_order(upstox_access_token, quantity, instrument_token)

                    cursor_tick.execute(f"SELECT price FROM {CE_symbol} ORDER BY Timestamp DESC LIMIT 1")
                    last_price = cursor_tick.fetchone()
                    current_time_ist = get_current_time_ist()
                    try:
                        with open(f'data/trade_logs/{date_suffix}_Trades.txt', 'a') as file:
                            file.write(f"CE Buy, Time : {current_time_ist} , {CE_symbol} at {last_price[0]}.\n")
                    except IOError as e:
                        print(f"An error occurred while writing to the file: {e}")

                elif last_direction_PE == 1 and second_last_direction_PE == -1:
                    # IT'S BUY SIGNAL
                    print("Buy PE", PE_symbol)


                    # ZERODHA
                    # exit_all_trades(kite)
                    # place_buy_order(kite=kite, tradingsymbol=PE_symbol)
                    
                    # UPSTOX
                    # exit_all_intraday_positions(upstox_access_token)

                    if active_positions:
                        for active_position in active_positions:
                            cursor_tick.execute(f"SELECT price FROM {active_position} ORDER BY Timestamp DESC LIMIT 1")
                            last_price = cursor_tick.fetchone()
                            current_time_ist = get_current_time_ist()
                            try:
                                with open(f'data/trade_logs/{date_suffix}_Trades.txt', 'a') as file:
                                    file.write(f"Sell, Time : {current_time_ist} , {active_position} at {last_price[0]}.\n")
                            except IOError as e:
                                print(f"An error occurred while writing to the file: {e}")
                        active_positions.remove(active_position)

                    # Append PE Symbol in Active Symbols
                    active_positions.append(PE_symbol)

                    # instrument_token = symbol_to_instrument["NSE:"+PE_symbol]
                    # place_order(upstox_access_token, quantity, instrument_token)

                    cursor_tick.execute(f"SELECT price FROM {PE_symbol} ORDER BY Timestamp DESC LIMIT 1")
                    last_price = cursor_tick.fetchone()
                    current_time_ist = get_current_time_ist()
                    try:
                        with open(f'data/trade_logs/{date_suffix}_Trades.txt', 'a') as file:
                            file.write(f"PE Buy, Time : {current_time_ist} , {PE_symbol} at {last_price[0]}.\n")
                    except IOError as e:
                        print(f"An error occurred while writing to the file: {e}")

                else:
                    # Now Get the Current Positions
                    # current_positions_keys = fetch_short_term_positions(upstox_access_token)
                    # print("current_positions_keys", current_positions_keys)
                    # Get the corresponding list of trading symbols
                    # current_positions = [instrument_to_symbol[key] for key in current_positions_keys if key in instrument_to_symbol]
                    # print("current_positions",current_positions)

                    # Now Calculate all things for Current Positions Strike Prices.
                    # Now Check if Current Positions is Needed to be closed. If it is then close it.
                    # if current_positions:
                    #     for i in current_positions:
                    #         get_ohlc(i)
                    #         cursor_candle.execute(f"SELECT Direction FROM {i}candles ORDER BY Timestamp DESC LIMIT 1")
                    #         last_direction = cursor_candle.fetchall()
                    #         # print("last_direction", last_direction)
                    #         # print(last_direction[0][0])
                    #         if last_direction[0][0] == -1:
                    #             # print('Nothing')
                    #             # exit_all_trades(kite)
                    #             exit_all_intraday_positions(upstox_access_token)

                    if active_positions:
                        for active_position in active_positions:
                            if active_position != CE_symbol and active_position !=PE_symbol:
                                get_ohlc(active_position)
                                ohlc_done.append(active_position)
                            cursor_candle.execute(f"SELECT Direction FROM {active_position}candles ORDER BY Timestamp DESC LIMIT 1")
                            last_direction = cursor_candle.fetchall()
                            if last_direction[0][0] == -1:
                                cursor_tick.execute(f"SELECT price FROM {active_position} ORDER BY Timestamp DESC LIMIT 1")
                                last_price = cursor_tick.fetchone()
                                current_time_ist = get_current_time_ist()
                                try:
                                    with open(f'data/trade_logs/{date_suffix}_Trades.txt', 'a') as file:
                                        file.write(f"Sell, Time : {current_time_ist} , {active_position} at {last_price[0]}.\n")
                                except IOError as e:
                                    print(f"An error occurred while writing to the file: {e}")
                                active_positions.remove(active_position)
                                ohlc_done.append(active_position)


            # Now we have list of all the tables whose values are not calculated yet.
            # current_positions.append(CE_symbol)
            # current_positions.append(PE_symbol)

            
            print("OHLC Done List :", ohlc_done)
            # symbols_for_ohlc = list(set(symbols) - set(current_positions)).
            symbols_for_ohlc = list(set(symbols) - set(ohlc_done))

            # Now Do Calculate all the things for rest of the tables.
            for i in symbols_for_ohlc:
                get_ohlc(i)
            
            # check_for_new_prices(ltp)

if __name__ == "__main__":
    main()

# def find_trade():
#     # get latest traded price of index
#     # Step 1 : Getting Data of Index with Websoket and Saving that in DB.
#     query = f"SELECT price FROM {index_table} ORDER BY Timestamp DESC LIMIT 1"
#     cursor_tick.execute(query)
#     latest_price = cursor_tick.fetchone()
#     # print(latest_price)

#     # based on index price decide Strike prices for CE and PE
#     CE_Strike_Price, PE_Strike_Price = choose_strike_prices(latest_price[0])
#     # print(CE_Strike_Price, PE_Strike_Price)

#     # get last 2 line data of both CE and PE
#     CE_symbol = [symbol for symbol in symbols if CE_Strike_Price in symbol][0]
#     PE_symbol = [symbol for symbol in symbols if PE_Strike_Price in symbol][0]
#     print(CE_symbol, PE_symbol)

#     cursor_candle.execute(f"SELECT Direction FROM {CE_symbol}candles ORDER BY Timestamp DESC LIMIT 2")
#     directions_CE = cursor_candle.fetchall()  # This will fetch the last two rows
#     # print('CE Directions ',directions_CE)

#     # if any of them has Supertrend Changed positively then
#     if directions_CE and len(directions_CE) == 2:
#         # Since fetchall returns a list of tuples, and we are interested in the first element of each tuple which is Direction
#         last_direction = directions_CE[0][0]
#         second_last_direction = directions_CE[1][0]
#         if last_direction == 1 and second_last_direction == -1:
#             # exit_all_trades(kite)
#             print("Buy CE", CE_symbol)
#             instrument_token = symbol_to_instrument[CE_symbol]
#             # place_buy_order(kite=kite, tradingsymbol= CE_symbol)
#             exit_all_intraday_positions(upstox_access_token)
#             place_order(upstox_access_token, quantity, instrument_token)

#             cursor_tick.execute(f"SELECT price FROM {CE_symbol} ORDER BY Timestamp DESC LIMIT 1")
#             last_price = cursor_tick.fetchone()
#             current_time_ist = get_current_time_ist()
#             try:
#                 with open('1JulyTrades.txt', 'a') as file:
#                     file.write(f"CE Buy, Time : {current_time_ist} , {CE_symbol} at {last_price[0]}.\n")
#             except IOError as e:
#                 print(f"An error occurred while writing to the file: {e}")

#     cursor_candle.execute(f"SELECT Direction FROM {PE_symbol}candles ORDER BY Timestamp DESC LIMIT 2")
#     directions_PE = cursor_candle.fetchall()  # This will fetch the last two rows
#     # print('PE Directions ',directions_PE)

#     if directions_PE and len(directions_PE) == 2:
#         # Since fetchall returns a list of tuples, and we are interested in the first element of each tuple which is Direction
#         last_direction = directions_PE[0][0]
#         second_last_direction = directions_PE[1][0]
#         if last_direction == 1 and second_last_direction == -1:
#             # exit_all_trades(kite)
#             print("Buy PE", PE_symbol)
#             # place_buy_order(kite=kite, tradingsymbol=PE_symbol)

#             exit_all_intraday_positions(upstox_access_token)
#             instrument_token = symbol_to_instrument[PE_symbol]
#             place_order(upstox_access_token, quantity, instrument_token)

#             cursor_tick.execute(f"SELECT price FROM {PE_symbol} ORDER BY Timestamp DESC LIMIT 1")
#             last_price = cursor_tick.fetchone()
#             current_time_ist = get_current_time_ist()
#             try:
#                 with open('1JulyTrades.txt', 'a') as file:
#                     file.write(f"PE Buy, Time : {current_time_ist} , {PE_symbol} at {last_price[0]}.\n")
#             except IOError as e:
#                 print(f"An error occurred while writing to the file: {e}")