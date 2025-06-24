import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyotp as tp
import time


# TODO: Replace with your Upstox API credentials
# Get these from your Upstox developer account at https://developer.upstox.com/
client_id = 'YOUR_CLIENT_ID_HERE'
client_secret = 'YOUR_CLIENT_SECRET_HERE'
redirect_uri = 'YOUR_REDIRECT_URI_HERE'

# TODO: Replace with your Upstox account details
mobile_number = "YOUR_MOBILE_NUMBER_HERE"  # Your registered mobile number
authenticator_code = 'YOUR_AUTHENTICATOR_CODE_HERE'  # Your 2FA authenticator secret
pin = 'YOUR_PIN_HERE'  # Your Upstox account PIN
url = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"

def authenticate_and_fetch_token(url, mobile_number, authenticator_code, pin, client_id, client_secret, redirect_uri):
    # Set up the browser with Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome()
    
    try:
        # Navigate to the URL
        driver.get(url)

        # Enter mobile number
        mobile_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="mobileNum"]')))
        mobile_input.send_keys(mobile_number)
        mobile_input.send_keys(Keys.RETURN)

        # Generate OTP using the provided authenticator code
        time_otp = tp.TOTP(authenticator_code).now()

        # Enter OTP
        otp_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="otpNum"]')))
        otp_input.send_keys(time_otp)
        otp_input.send_keys(Keys.RETURN)

        # Enter PIN
        pin_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="pinCode"]')))
        pin_input.send_keys(pin)
        pin_input.send_keys(Keys.RETURN)

        # Wait for redirect and extract the code
        WebDriverWait(driver, 10).until(EC.url_contains("code="))
        code = driver.current_url.partition("code=")[2]

        # Post request to obtain access token
        token_url = 'https://api.upstox.com/v2/login/authorization/token'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        response = requests.post(token_url, headers=headers, data=data)
        access_token = response.json()['access_token']

        # Write access token to a file
        with open('upstox_access_token.txt', 'w') as file:
            file.write(access_token)
            print("New Access code written Successfully.")
        return access_token
    except Exception as e:
        # print(f"An error occurred: {e}")
        print("An Error Occured ...")
        print("Retrying ...")
        time.sleep(5)
        authenticate_and_fetch_token(url, mobile_number, authenticator_code, pin, client_id, client_secret, redirect_uri)
    finally:
        driver.quit()

# Example usage:
authenticate_and_fetch_token(url, mobile_number, authenticator_code, pin, client_id, client_secret, redirect_uri)