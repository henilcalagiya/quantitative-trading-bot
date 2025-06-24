# import requests
# with open('upstox_access_token.txt','r') as a:
#     upstox_access_token=a.read()

# access_token = upstox_access_token

import requests

def place_order(access_token, quantity, instrument_token, order_type='MARKET', transaction_type='BUY',product= 'I', price=0, validity='DAY', tag='string', disclosed_quantity=0, trigger_price=0, is_amo=False):

    url = 'https://api.upstox.com/v2/order/place'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }

    data = {
        'quantity': quantity,
        'product': product,
        'validity': validity,
        'price': price,
        'tag': tag,
        'instrument_token': instrument_token,
        'order_type': order_type,
        'transaction_type': transaction_type,
        'disclosed_quantity': disclosed_quantity,
        'trigger_price': trigger_price,
        'is_amo': is_amo,
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        return {'Status Code': response.status_code, 'Response Body': response.json()}
    except Exception as e:
        return {'Error': str(e)}

# Example usage:
# response = place_order(access_token, 1, 'I', 'NSE_EQ|INE528G01035', 'MARKET', 'BUY')
# print(response)


def fetch_short_term_positions(access_token):
    url = 'https://api.upstox.com/v2/portfolio/short-term-positions'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        # Extract only the 'instrument_token' from each position and return the list
        # instrument_tokens = [item['instrument_token'] for item in data.get('data', [])]
        return data
    except Exception as e:
        return {'Error': str(e)}

# Usage example (assuming you have a valid access token):
# access_token = 'your_access_token_here'
# print(fetch_short_term_positions(access_token))


# Example usage:
# positions = fetch_short_term_positions(access_token)
# print(positions)


def exit_all_intraday_positions(access_token):

    # Fetch all current positions
    positions = fetch_short_term_positions(access_token)
    print("positions",positions)
    print(type(positions))

    # Initialize an empty list to store responses
    responses = []

    # Check if the fetch was successful
    if positions['status'] == 'success':
        # Iterate over each position data
        for position in positions['data']:
            if position['product'] == 'I':  # Assuming 'I' represents Intraday positions
                # Determine the transaction type (BUY to SELL and vice versa)
                transaction_type = 'SELL' if position['transaction_type'] == 'BUY' else 'BUY'

                # Place order to exit this position
                response = place_order(
                    access_token=access_token,
                    quantity=position['quantity'],
                    product=position['product'],
                    instrument_token=position['instrument_token'],
                    order_type='MARKET',  # Assuming you want to exit at market price
                    transaction_type=transaction_type,
                    price=0  # Market price
                )
                responses.append(response)
            else:
                # If not intraday, log that no action was taken
                responses.append({"message": "No action taken, not an intraday position", "instrument_token": position['instrument_token']})
    else:
        # If the fetch failed, return the original response
        return positions

    return responses

# Example usage:
# exit_responses = exit_all_intraday_positions(access_token)
# for response in exit_responses:
#     print(response)


