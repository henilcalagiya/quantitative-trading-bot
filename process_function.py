import time
import pytz
import datetime
import sqlite3
from dictionaries import *
from datetime import datetime
from upstox_functions import *
from process_live_data import active_positions
from functions import start_price, end_price

with open('upstox_access_token.txt','r') as a:
    upstox_access_token=a.read()

current_epoch_time = time.time()

# Set the timezone to Indian Standard Time (IST)
indian_tz = pytz.timezone('Asia/Kolkata')

# Get the current datetime in IST
now_ist = datetime.now(indian_tz)

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

def get_latest_index_ltp():
    query = f"SELECT price FROM {index_table} ORDER BY Timestamp DESC LIMIT 1"
    cursor_tick.execute(query)
    latest_price = cursor_tick.fetchone()

    return latest_price

def choose_strike_prices(latest_price):
    # Calculate the nearest higher multiple of 100 for the Call option
    previous_hundred = ((latest_price // 100) - 1) * 100
    # Calculate the nearest lower multiple of 100 for the Put option
    next_hundred = ((latest_price // 100)) * 100

    # Format the options as CE and PE
    CE_Strike_Price = f"{int(next_hundred)}CE"
    PE_Strike_Price = f"{int(previous_hundred)}PE"

    return CE_Strike_Price, PE_Strike_Price

def get_ohlc(tick_table_name):
    tick_tables = tick_table_name
    candle_tables = tick_table_name + "candles"

    # Get Current Epoch time
    current_epoch_time = time.time()
    int_time = int(current_epoch_time) - 5

    # Get all prices from last 5 seconds
    query = f"SELECT price FROM {tick_tables} WHERE Timestamp > {int_time}"
    cursor_tick.execute(query)
    prices = [row[0] for row in cursor_tick.fetchall()]
    # print(prices)

    # Get Last Candles Data
    query2 = f"SELECT * FROM {candle_tables} WHERE Timestamp = {int_time}"
    cursor_candle.execute(query2)
    last_row = cursor_candle.fetchone()

    # Only proceed if there are prices available
    if prices:

        # Normal Candle Data
        # Get OHLC for Current Candle
        Open = prices[0]
        High = max(prices)
        Low = min(prices)
        Close = prices[-1]

        # Heiken Ashi Candle Data
        # Get Heiken Ashi for Current Candle
        HA_Close = (Open + High + Low + Close)/4

        if last_row is not None:
            # print("available", last_row[5], last_row[8])
            HA_Open = (last_row[5]+last_row[8])/2
        else:
            # print("not available")
            HA_Open = Open

        HA_High = max(HA_Close, HA_Open, High)
        HA_Low = min(HA_Close, HA_Open, Low)

        # Get True Range for Current Candle
        if last_row is not None:
            tr1 = HA_High - HA_Low
            tr2 = abs(HA_High - last_row[8])
            tr3 = abs(HA_Low - last_row[8])
            TR = max(tr1, tr2, tr3)
        else:
            TR = HA_High - HA_Low

        # Get True Ranges for last 9 Candles.
        cursor_candle.execute(f"""SELECT TR FROM {candle_tables} ORDER BY Timestamp DESC LIMIT 9""")
        rows = cursor_candle.fetchall()

        # Get ATR for Current Candle
        # Calculate Average of TR values
        tr_values = [row[0] for row in rows]
        tr_values.append(TR)
        ATR = sum(tr_values)/len(tr_values)

        # Supertrend = ((HA_High + HA_Low)/2) + 3*ATR
        if last_row is not None:
            prev_close = last_row[8]
            prev_BUB = last_row[11]
            prev_BLB = last_row[12]
            prev_FUB = last_row[13]
            prev_FLB = last_row[14]
            prev_ST = last_row[15]
        else:
            prev_close = None
            prev_BUB = None
            prev_BLB = None
            prev_FLB = None
            prev_FUB = None
            prev_ST = None
        Supertrend, BUB, BLB, FUB, FLB, Direction = calculate_supertrend(HA_High, HA_Low, HA_Close, ATR, prev_close, prev_BUB, prev_BLB, prev_FUB, prev_FLB, prev_ST, multiplier=2)

        # Prepare SQL to insert OHLC data into the OHLC table
        insert_query = f"INSERT INTO {candle_tables} (Timestamp, Open, High, Low, Close, HA_Close, HA_Open, HA_High, HA_Low, TR, ATR, BUB, BLB, FUB, FLB, Supertrend, Direction) VALUES (?, ?, ?, ?, ?, ?, ?, ? ,?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor_candle.execute(insert_query, (int(current_epoch_time), Open, High, Low, Close, HA_Close, HA_Open, HA_High, HA_Low, TR, ATR, BUB, BLB, FUB, FLB, Supertrend, Direction))
        prices = []
        db_candle.commit()  # Commit the changes to the database

        # print(f"OHLC Data Inserted: Open={Open}, High={High}, Low={Low}, Close={Close}")

def calculate_supertrend(HA_High, HA_Low, HA_Close, ATR, prev_close=None, prev_BUB=None, prev_BLB=None, prev_FUB=None, prev_FLB=None, prev_ST=None, multiplier=2):

    avg = (HA_High + HA_Low) / 2
    BUB = avg + (multiplier * ATR)
    BLB = avg - (multiplier * ATR)
    
    if prev_FUB is None or prev_FLB is None:
        FUB = BUB
        FLB = BLB

        if HA_Close > avg:
            ST = FLB
            Direction = 1
        else:
            ST = FUB
            Direction = -1
    else:
        if BUB < prev_FUB or prev_close > prev_FUB:
            FUB = BUB
        else:
            FUB = prev_FUB

        if BLB > prev_FLB or prev_close < prev_FLB:
            FLB = BLB
        else:
            FLB = prev_FLB

        if prev_ST == prev_FUB:
            if HA_Close < FUB:
                ST = FUB
                Direction = -1
            else:
                ST = FLB
                Direction = 1
        else:
            prev_ST == prev_FLB
            if HA_Close > FLB:
                ST = FLB
                Direction = 1
            else:
                ST = FUB
                Direction = -1
    
    return ST, BUB, BLB, FUB, FLB, Direction

def exit_trade():

    # get script name of currently active trades
    # current_positions = get_active_tradingsymbols(kite)

    current_positions_keys = fetch_short_term_positions(upstox_access_token)
    print("current_positions_keys", current_positions_keys)
    # Get the corresponding list of trading symbols
    current_positions = [instrument_to_symbol[key] for key in current_positions_keys if key in instrument_to_symbol]
    print("current_positions",current_positions)

    for i in current_positions:
        print("i", i)
        cursor_candle.execute(f"SELECT Direction FROM {i}candles ORDER BY Timestamp DESC LIMIT 1")
        last_direction = cursor_candle.fetchall()
        print("last_direction", last_direction)
        print(last_direction[0][0])
        if last_direction[0][0] == -1:
            print('Nothing')
            # exit_all_trades(kite)
            exit_all_intraday_positions(upstox_access_token)
    # check if any of them has supertrend direction negative, if it is then do close that trade.

# def check_for_new_prices(ltp):
#     global start_price, end_price
#     if ltp < start_price - 300:
#         print("Executing code for LTP below the lower limit.")
        
        # Get 20 Strike Prices List

        # Get their Symbols

        # Start Data Websocket for that

    # elif ltp > end_price + 300:
    #     print("Executing code for LTP above the upper limit.")
    # else:
    #     print("LTP is within the normal range.")