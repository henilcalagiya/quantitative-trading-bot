from fyers_apiv3.FyersWebsocket import data_ws
from fyers_apiv3 import fyersModel
import pandas as pd
import datetime as dt
with open('access.txt','r') as a:
    access_token=a.read()
import credentials as cd

client_id = cd.client_id
access_token = access_token

# Initialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,is_async=False, log_path="")


# res = fyers.market_status()
# response = pd.DataFrame(res)
# print(response)


def onmessage(message):
    """
    Callback function to handle incoming messages from the FyersDataSocket WebSocket.

    Parameters:
        message (dict): The received message from the WebSocket.

    """
    # Convert the message to a DataFrame
    df = pd.DataFrame([message])
    
    # Define the CSV file path
    csv_file = 'your_data.csv'
    
    # Append the data to the CSV file
    # Include header only if the file does not exist or is empty
    with open(csv_file, 'a') as f:
        df.to_csv(f, header=f.tell()==0, index=False)

    # Optionally print the DataFrame to console (you can remove this line in production)
    print("Response:", df)



def onerror(message):
    """
    Callback function to handle WebSocket errors.

    Parameters:
        message (dict): The error message received from the WebSocket.


    """
    print("Error:", message)


def onclose(message):
    """
    Callback function to handle WebSocket connection close events.
    """
    print("Connection closed:", message)


def onopen():
    """
    Callback function to subscribe to data type and symbols upon WebSocket connection.

    """
    # Specify the data type and symbols you want to subscribe to
    data_type = "DepthUpdate"

    # Subscribe to the specified symbols and data type
    symbols = ['NSE:BANKNIFTY2461950000CE']
    fyers.subscribe(symbols=symbols, data_type=data_type)

    # Keep the socket running to receive real-time data
    fyers.keep_running()


# Create a FyersDataSocket instance with the provided parameters
fyers = data_ws.FyersDataSocket(
    access_token=access_token,       # Access token in the format "appid:accesstoken"
    log_path="",                     # Path to save logs. Leave empty to auto-create logs in the current directory.
    litemode=False,                  # Lite mode disabled. Set to True if you want a lite response.
    write_to_file=False,              # Save response in a log file instead of printing it.
    reconnect=True,                  # Enable auto-reconnection to WebSocket on disconnection.
    on_connect=onopen,               # Callback function to subscribe to data upon connection.
    on_close=onclose,                # Callback function to handle WebSocket connection close events.
    on_error=onerror,                # Callback function to handle WebSocket errors.
    on_message=onmessage             # Callback function to handle incoming messages from the WebSocket.
)

# Establish a connection to the Fyers WebSocket
fyers.connect()