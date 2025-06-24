from nsepython import *

# Fetch the futures data for BankNifty
banknifty_futures = nse_fno("BANKNIFTY")
# print(banknifty_futures)
# Get the next expiry future data
next_expiry_data = banknifty_futures.keys  # This assumes that the expiries are sorted in ascending order
print(next_expiry_data)
# Print the next expiry future data
print("Next Expiry for BankNifty Future:", next_expiry_data)
