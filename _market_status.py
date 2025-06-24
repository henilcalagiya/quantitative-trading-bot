from fyers_apiv3.FyersWebsocket import data_ws
from fyers_apiv3 import fyersModel
import pandas as pd
import datetime as dt
with open('access_token.txt','r') as a:
    access_token=a.read()
import credentials as cd

client_id = cd.client_id
access_token = access_token

# Initialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,is_async=False, log_path="")


res = fyers.market_status()
response = pd.DataFrame(res)

if res:
    response.to_csv('_market_status.csv')
    print("Market Status Updated Successfully")
else:
    print("Error !!!")

# print(response)