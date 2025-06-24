# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
import credentials as cd

# Replace these values with your actual API credentials
client_id = cd.client_id
secret_key = cd.secret_key
redirect_uri = cd.redirect_uri
response_type = "code"
grant_type = "authorization_code"
with open('auth_code.txt','r') as a:
    auth_code=a.read()
with open('auth_code.txt', 'w') as file:
    file.write("")


# Create a session object to handle the Fyers API authentication and token generation
session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key, 
    redirect_uri=redirect_uri, 
    response_type=response_type, 
    grant_type=grant_type
)

# Set the authorization code in the session object
session.set_token(auth_code)

# Generate the access token using the authorization code
response = session.generate_token()

# Print the response, which should contain the access token and other details
print(response)

access_token = response['access_token']
try:
    with open('access_token.txt', 'w') as k:
        k.write(access_token)
        print("New Access code written Successfully.")
except IOError as e:
    print(f"An error occurred while writing to the file: {e}")
# ----------------------------------------------------------------------------------
# Sample Success Response               
# ----------------------------------------------------------------------------------          

# {
#   's': 'ok',
#   'code': 200,
#   'message': '',
#   'access_token': 'eyJ0eXAiOi***.eyJpc3MiOiJh***.HrSubihiFKXOpUOj_7***',
#   'refresh_token': 'eyJ0eXAiO***.eyJpc3MiOiJh***.67mXADDLrrleuEH_EE***'
# }