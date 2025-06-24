import pandas as pd
from datetime import datetime
from functions import *

def get_dict_of_instrumentkey_and_symbol(date, month, year, is_weekly_expiry):

    # Convert month number to abbreviated month name
    month_name = datetime(year, month, 1).strftime('%b').upper()  

    # Load instruments data
    instruments = pd.read_json('https://assets.upstox.com/market-quote/instruments/exchange/complete.json.gz')
    # print(instruments.columns)

    # Format the expiry string to match "dd MMM yy"
    formatted_date = pd.to_datetime(f'{year}-{month_name}-{date}').strftime('%d %b %y').upper()

    # Define the regex pattern for trading_symbol with expiry
    pattern = f'BANKNIFTY \d+ (CE|PE) {formatted_date}'

    # Filter instruments based on the pattern
    filtered_instruments = instruments[instruments['trading_symbol'].str.contains(pattern, regex=True, na=False)]
    # print(filtered_instruments)

    strike_prices = []

    strike_prices_series = filtered_instruments['strike_price']

    # Iterating over the 'strike_price' column with index
    for index, price in strike_prices_series.items():
        # print(int(price))
        strike_prices.append(int(price))

    strike_prices = set(strike_prices)

    if is_weekly_expiry:
        all_option_symbols = symbols_for_weekly_expiry('BANKNIFTY', year, month, date, strike_prices)
    else:
        all_option_symbols = symbols_for_monthly_expiry('BANKNIFTY', year, month, date, strike_prices)

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

    return all_option_symbols
# Example usage:
# result = get_dict_of_instrumentkey_and_symbol(10, 7, 2024, True)
# print(result)
# print(get_price_range(55020))

# get_symbols_to_trade(46045, 46450)