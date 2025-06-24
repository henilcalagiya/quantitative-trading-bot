# Define the range and the type of options
start = 54300
end = 51300
option_types = ['CE', 'PE']
expiry_date = '24703'

# Generate the list of symbols
symbols = []
for price in range(start, end - 100, -100):  # Assuming a decrement of 100
    for option_type in option_types:
        symbol = f'NSE:BANKNIFTY{expiry_date}{price}{option_type}'
        symbols.append(symbol)

# Print the list
print(symbols)

# NSE:BANKNIFTY2470352800CE