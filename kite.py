from kite_trade import *

# TODO: Replace with your actual enctoken from Kite
# You can get this from your browser's developer tools after logging into Kite
enctoken = 'YOUR_ENCTOKEN_HERE'
kite = KiteApp(enctoken=enctoken)

def exit_all_trades(kite):
    # Fetch current positions
    current_positions = kite.positions()
    # print(current_positions)

    # Check for positions in the 'net' section of the response
    if current_positions is not None:
        for position in current_positions['net']:
            # Determine transaction type based on the quantity
            if position['quantity'] > 0:
                transaction_type = KiteApp.TRANSACTION_TYPE_SELL
            elif position['quantity'] < 0:
                transaction_type = KiteApp.TRANSACTION_TYPE_BUY
            else:
                continue  # Skip if no position to exit

            # Determine the quantity to exit
            quantity = abs(position['quantity'])

            # Place the order to exit the trade
            try:
                order_id = kite.place_order(
                    variety=KiteApp.VARIETY_REGULAR,
                    exchange=position['exchange'],
                    tradingsymbol=position['tradingsymbol'],
                    transaction_type=transaction_type,
                    quantity=quantity,
                    product=position['product'],
                    order_type=KiteApp.ORDER_TYPE_MARKET
                )
                print(f"Order placed to exit {position['tradingsymbol']}. Order ID: {order_id}")
            except Exception as e:
                print(f"Failed to exit {position['tradingsymbol']}: {str(e)}")

# exit_all_trades(kite)

def get_active_tradingsymbols(kite):
    # Fetch current positions
    current_positions = kite.positions()
    # print(current_positions)

    # Initialize a list to hold the trading symbols of active positions
    active_tradingsymbols = []

    # Loop through the positions in the 'net' section of the positions data
    if current_positions is not None:
        for position in current_positions['net']:
            # Check if the position is active, i.e., quantity is not zero
            if position['quantity'] != 0:
                # Add the trading symbol to the list
                active_tradingsymbols.append(position['tradingsymbol'])

    return active_tradingsymbols


# active_symbols = get_active_tradingsymbols(kite)
# print("Active Trading Symbols:", active_symbols)
# print(kite.profile())

def place_buy_order(kite, tradingsymbol):
    # Here Before Buy check if current position is not in Same side. If it's on same side then do not place buy order.
    # current_positions = get_active_tradingsymbols(kite)
    try:
        current_positions = get_active_tradingsymbols(kite)
    except Exception as e:
        print(f"Failed to retrieve current positions: {e}")
        return  # Exit the function if we can't retrieve positions
    
    if current_positions:
        current_position_symbol = current_positions[0]
        if tradingsymbol[-2:] == current_position_symbol[-2:]:
            print("The last two characters of both strings are the same.")
        else:
            execute_order(kite,tradingsymbol)
    else:
        execute_order(kite,tradingsymbol)

def execute_order(kite,tradingsymbol):
    print("The last two characters of both strings are different.")
    print("Attempting to place order...")

    if not kite:
        print("Error: Kite instance is None.")
        return
    try:
        print("Placing order for:", tradingsymbol, type(tradingsymbol))
        order_id = kite.place_order(
            variety=KiteApp.VARIETY_REGULAR,
            exchange=KiteApp.EXCHANGE_NFO,
            tradingsymbol=tradingsymbol,
            transaction_type=KiteApp.TRANSACTION_TYPE_BUY,
            quantity=15,
            product=KiteApp.PRODUCT_MIS,
            order_type=KiteApp.ORDER_TYPE_MARKET
        )
        print(f"Order placed successfully. Order ID: {order_id}")
    except Exception as e:
        print(f"Failed to place order for {tradingsymbol}: {e}")