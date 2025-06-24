from fyers_apiv3.FyersWebsocket import data_ws
from fyers_apiv3 import fyersModel
with open('access_token.txt','r') as a:
    access_token=a.read()
import credentials as cd
from nsepython import *
from datetime import datetime
import pytz
import time
import sqlite3

client_id = cd.client_id
access_token = access_token

start_price = None
end_price = None

# Set the timezone to Indian Standard Time (IST)
indian_tz = pytz.timezone('Asia/Kolkata')

# Get the current datetime in IST
now_ist = datetime.now(indian_tz)

# Format the date as DDMMMYY
date_suffix = now_ist.strftime('%d%b%y').upper()

# Create the tick data database name with the date suffix
tick_db_name = f'data/tick_data/tickdata_{date_suffix}.db'
db_tick = sqlite3.connect(tick_db_name, check_same_thread=False)
db_tick.execute('PRAGMA journal_mode=WAL;')  # Enable write-ahead logging
cursor_tick = db_tick.cursor()

# Create the candle data database name with the date suffix
candle_db_name = f'data/candle_data/candledata_{date_suffix}.db'
db_candle = sqlite3.connect(candle_db_name, check_same_thread=False)
cursor_candle = db_candle.cursor()

# def clear_database(db_file):
#     # Connect to the SQLite database
#     db = sqlite3.connect(db_file, check_same_thread=False)
#     c = db.cursor()

#     # Fetch existing tables and drop them
#     c.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     tables = c.fetchall()
#     for table in tables:
#         print(f"Dropping table {table[0]}")
#         c.execute(f'DROP TABLE {table[0]};')
#         print("Old DB Cleared")
    
#     # Commit changes and close connection
#     db.commit()
#     # db.close()

def create_tables(tokens):
    # Connect to tickdata.db

    # Create tables in both databases based on tokens
    for i in tokens:
        token_short = i[4:]  # Assuming you want to strip the first four characters

        # Tick data table
        cursor_tick.execute(f"""CREATE TABLE IF NOT EXISTS {token_short} (
            Timestamp real PRIMARY KEY, price real)""")
        
        # Candle data table
        table_name = token_short + "candles"
        cursor_candle.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
            Timestamp INTEGER PRIMARY KEY,
            Open real, High real, Low real, Close real,
            HA_Open real, HA_High real, HA_Low real, HA_Close real,
            TR real, ATR real, BUB real, BLB real,
            FUB real, FLB real, Supertrend real, Direction INTEGER, 
            datachanged INTEGER)""")

    # Commit changes to both databases
    try:
        db_tick.commit()
        db_candle.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        db_tick.rollback()
        db_candle.rollback()

def insert_ticks(msg):
    try:
        ltp = str(msg["ltp"])
        symbol = str(msg["symbol"][4:])
        # symbol = str(msg["symbol"])
        # ltt = time.strftime('%Y-%M-%D %H:%M:%S', time.localtime(timestamp))
        ltt = time.time()
        data = (ltt,ltp)
        cursor_tick.execute(f"INSERT INTO {symbol} VALUES{data};")

        db_tick.commit()
    except:
        db_tick.rollback()

# Initialize the FyersModel
def get_ltp():
    fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, is_async=False, log_path="")

    data = {
        "symbols": "NSE:NIFTYBANK-INDEX"
    }

    attempt_count = 0
    while attempt_count < 3:
        response = fyers.quotes(data=data)
        # Check if the response code is 200 and process the data
        if response.get('code') == 200 and response['s'] == 'ok':
            # Assuming the data structure is consistent with the sample provided
            last_price = response['d'][0]['v']['lp']
            return last_price
        else:
            attempt_count += 1
            print(f"Attempt {attempt_count}: Failed to fetch data, retrying in 3 seconds...")
            time.sleep(3)

    # If all retries fail, raise an error
    raise Exception("Failed to fetch LTP after 3 attempts.")

def determine_expiry_dates():
    # Fetch the list of expiry dates for BANKNIFTY
    list_of_expiry = expiry_list('BANKNIFTY')
    if not list_of_expiry or len(list_of_expiry) < 2:
        raise ValueError("Expiry list is insufficient.")

    # Get the current date in IST
    ist_timezone = pytz.timezone('Asia/Kolkata')
    current_date = datetime.now(ist_timezone).strftime('%d-%b-%Y')

    # Determine the current expiry based on today's date
    if current_date == list_of_expiry[0]:
        trade_expiry = list_of_expiry[1]
        next_expiry = list_of_expiry[2]
    else:
        trade_expiry = list_of_expiry[0]
        next_expiry = list_of_expiry[1]

    # Convert expiry dates from string to datetime objects
    try:
        trade_expiry_dt = datetime.strptime(trade_expiry, '%d-%b-%Y')
        print(trade_expiry_dt)
        next_expiry_dt = datetime.strptime(next_expiry, '%d-%b-%Y')
    except ValueError as e:
        raise ValueError(f"Error parsing dates: {e}")

    # Extracting day, month, and year from the expiry dates
    # trade_expiry_day = trade_expiry_dt.day
    trade_expiry_day = f"{trade_expiry_dt.day:02d}"
    print("trade_expiry_day", trade_expiry_day)
    trade_expiry_month = trade_expiry_dt.month
    trade_expiry_year = trade_expiry_dt.year

    # Check if there is a next expiry and extract month
    if next_expiry_dt:
        next_expiry_month = next_expiry_dt.month
    else:
        raise ValueError("Next expiry date is not available.")

    # Check if trade_expiry and next_expiry are within the same month
    is_weekly_expiry = trade_expiry_month == next_expiry_month

    # Ensure no value is None
    if None in [trade_expiry_day, trade_expiry_month, trade_expiry_year, is_weekly_expiry]:
        raise ValueError("One or more expiry details are None.")

    print("is_weekly_expiry", is_weekly_expiry)
    return trade_expiry_day, trade_expiry_month, trade_expiry_year, is_weekly_expiry

def get_banknifty_symbols(ltp, trade_expiry, is_weekly_expiry):

    # # Parse the dates to get the day, month, and year
    trade_expiry_dt = datetime.strptime(trade_expiry, '%d-%b-%Y')
    # next_expiry_dt = datetime.strptime(next_expiry, '%d-%b-%Y')

    # Extracting day, month, and year from the first expiry
    trade_expiry_day = trade_expiry_dt.day
    # trade_expiry_day = f"{trade_expiry_dt.day:02d}"
    # print("trade_expiry_day", trade_expiry_day)
    trade_expiry_month = trade_expiry_dt.month
    trade_expiry_year = trade_expiry_dt.year

    # Get Price range for getting strike prices
    start_price, end_price = get_price_range(ltp)

    current_future_index = symbol_for_monthly_futures('BANKNIFTY', trade_expiry_year, trade_expiry_month)

    # Determine if it's a weekly or monthly expiry
    if is_weekly_expiry:
        option_symbols = symbols_for_weekly_expiry('BANKNIFTY', trade_expiry_year, trade_expiry_month, trade_expiry_day, start_price, end_price)
    else:
        option_symbols = symbols_for_monthly_expiry('BANKNIFTY', trade_expiry_year, trade_expiry_month, start_price, end_price)
    print("option_symbols", option_symbols)
    get_dict_of_instrumentkey_and_symbol(trade_expiry_day, trade_expiry_month, trade_expiry_year, option_symbols)
    option_symbols.append(current_future_index)
    banknfity_symbols = option_symbols
    # print(banknfity_symbols)
    return banknfity_symbols

def symbols_for_weekly_expiry(symbol, year, month, day, prices):
    print(year, month, day)
    option_symbols = []
    for price in prices:
        ce_symbol = f'NSE:{symbol}{year%100}{month}{day}{price}CE'
        pe_symbol = f'NSE:{symbol}{year%100}{month}{day}{price}PE'
        option_symbols.append(ce_symbol)
        option_symbols.append(pe_symbol)
    return option_symbols

def symbols_for_monthly_expiry(symbol, year, month, prices):
    # Month names dictionary to convert month number to three-letter abbreviation
    month_names = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN",
                   7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    month_name = month_names[month]
    option_symbols = []
    for price in prices:
        ce_symbol = f'NSE:{symbol}{year%100}{month_name}{price}CE'
        pe_symbol = f'NSE:{symbol}{year%100}{month_name}{price}PE'
        option_symbols.append(ce_symbol)
        option_symbols.append(pe_symbol)
    return option_symbols

def symbol_for_monthly_futures(month, year):
    symbol = "BANKNIFTY"
    # Month names dictionary to convert month number to three-letter abbreviation
    month_names = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN",
                   7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
    month_name = month_names[month]
    # Generate the futures symbol
    futures_symbol = f'NSE:{symbol}{year%100}{month_name}FUT'
    
    with open('dictionaries.py', 'a') as file:
        file.write(f'current_future_index = ["{futures_symbol}"]\n')

def get_price_range(ltp):
    price = int(int(ltp)/100)
    start_price = (price - 11)*100
    end_price = (price + 12)*100

    return start_price, end_price

def get_dict_of_instrumentkey_and_symbol(date, month, year, is_weekly_expiry):
    print("date", date)

    try:
        # Convert month number to abbreviated month name
        month_name = datetime(year, month, 1).strftime('%b').upper()  
    except ValueError as e:
        print(f"Invalid date parameters: {e}")
        return

    try:
        # Load instruments data
        instruments = pd.read_json('https://assets.upstox.com/market-quote/instruments/exchange/complete.json.gz')
    except Exception as e:
        print(f"Failed to load or parse JSON data: {e}")
        return

    if 'trading_symbol' not in instruments.columns or 'strike_price' not in instruments.columns:
        print("Required columns are missing in the data.")
        return

    try:
        # Format the expiry string to match "dd MMM yy"
        formatted_date = pd.to_datetime(f'{year}-{month_name}-{date}').strftime('%d %b %y').upper()
    except ValueError as e:
        print(f"Invalid date format or parameters: {e}")
        return

    # Define the regex pattern for trading_symbol with expiry
    pattern = f'BANKNIFTY \d+ (CE|PE) {formatted_date}'

    try:
        # Filter instruments based on the pattern
        filtered_instruments = instruments[instruments['trading_symbol'].str.contains(pattern, regex=True, na=False)]
    except re.error as e:
        print(f"Regex error: {e}")
        return

    strike_prices = []

    strike_prices_series = filtered_instruments['strike_price']

    # Iterating over the 'strike_price' column with index
    for index, price in strike_prices_series.items():
        # print(int(price))
        strike_prices.append(int(price))

    strike_prices = set(strike_prices)

    if is_weekly_expiry:
        all_option_symbols = symbols_for_weekly_expiry('BANKNIFTY', year, month, date, strike_prices)
        all_option_symbols.sort()
    else:
        all_option_symbols = symbols_for_monthly_expiry('BANKNIFTY', year, month, strike_prices)
        all_option_symbols.sort()

    symbol_to_instrument = {}
    instrument_to_symbol = {}

    
    for symbol in all_option_symbols:
        instrument_type_from_symbol = symbol[-2:]  # Last two characters
        strike_price_from_symbol = symbol[-7:-2]  # Characters from -7 to -2

        filtered_df = filtered_instruments[(filtered_instruments['instrument_type'] == instrument_type_from_symbol) & (filtered_instruments['strike_price'] == int(strike_price_from_symbol))]

        if not filtered_df.empty:
            instrument_key = filtered_df['instrument_key'].iloc[0]  # Get the first instrument key
            symbol_to_instrument[symbol] = instrument_key  # Add symbol and instrument_key to the dictionary
            instrument_to_symbol[instrument_key] = symbol
        else:
            print(f"No instrument key found for symbol: {symbol}")
    
    # Write dictionaries to a Python file
    with open('dictionaries.py', 'w') as file:
        file.write("symbol_to_instrument = " + str(symbol_to_instrument) + "\n")
        file.write("instrument_to_symbol = " + str(instrument_to_symbol) + "\n")
        file.write("all_option_symbols = " + str(all_option_symbols) + "\n")
        
def get_symbols_to_trade(ltp,all_option_symbols,current_future_index):
    print("ltp",ltp,", current_future_index",current_future_index)

    price = int(int(ltp)/100)
    start_price = (price - 11)*100
    end_price = (price + 12)*100
    strike_prices = list(range(start_price,end_price + 100, 100))
    print("strike_prices", strike_prices)

    # Convert strike prices from integer to strings for comparison
    strike_prices = [str(price) for price in strike_prices]

    option_symbols_to_trade = [item for item in all_option_symbols if any(sub in item for sub in strike_prices)]
    print("option_symbols_to_trade", option_symbols_to_trade)
    option_symbols_to_trade = current_future_index + option_symbols_to_trade
    # with open('dictionaries.py', 'a') as file:
    #     file.write("option_symbols_to_trade = " + str(option_symbols_to_trade) + "\n")

    return option_symbols_to_trade

# If ltp is beyond a specific price

# do write a code to fire a new websocket which contains more 10 strike prices.