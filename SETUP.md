# Quantitative Trading Bot - Setup Guide

## Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium automation)
- Trading accounts with Fyers, Upstox, or Zerodha

## Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd "Quantitative Trading Bot"
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

#### For Development (includes all dependencies):
```bash
pip install -r requirements.txt
```

#### For Production (minimal dependencies):
```bash
pip install -r requirements-minimal.txt
```

### 4. Install Chrome WebDriver
```bash
# Install webdriver-manager (included in requirements)
pip install webdriver-manager
```

## Configuration

### 1. Set Up Credentials

#### Fyers API Setup:
1. Go to [Fyers Developer Portal](https://fyers.in/developer)
2. Create a new app and get your credentials
3. Update `credentials.py`:
```python
client_id = 'YOUR_CLIENT_ID_HERE'
secret_key = 'YOUR_SECRET_KEY_HERE'
user_name = 'YOUR_USERNAME_HERE'
```

#### Upstox API Setup:
1. Go to [Upstox Developer Portal](https://developer.upstox.com/)
2. Create a new app and get your credentials
3. Update `get_upstox_access_token.py`:
```python
client_id = 'YOUR_CLIENT_ID_HERE'
client_secret = 'YOUR_CLIENT_SECRET_HERE'
mobile_number = "YOUR_MOBILE_NUMBER_HERE"
authenticator_code = 'YOUR_AUTHENTICATOR_CODE_HERE'
pin = 'YOUR_PIN_HERE'
```

#### Zerodha Kite Setup:
1. Get your enctoken from Kite web platform
2. Update `kite.py`:
```python
enctoken = 'YOUR_ENCTOKEN_HERE'
```

### 2. Generate Access Tokens

#### Fyers Token:
```bash
python get_access_token.py
```

#### Upstox Token:
```bash
python get_upstox_access_token.py
```

## Usage

### 1. Start Data Collection
```bash
python 1fetch_tick_data_live.py
```

### 2. Start Trading Bot
```bash
python process_live_data.py
```

### 3. Schedule Tasks (Optional)
```bash
python schedule_task.py
```

## Project Structure

```
Quantitative Trading Bot/
├── data/                    # Data storage
│   ├── trade_logs/         # Daily trade logs
│   ├── tick_data/          # Real-time tick data
│   └── candle_data/        # Processed candle data
├── logs/                   # Application logs
├── Core Scripts:
│   ├── functions.py        # Core trading functions
│   ├── process_live_data.py # Main trading logic
│   └── process_function.py # Data processing
├── Setup Scripts:
│   ├── get_access_token.py # Fyers token generation
│   ├── get_upstox_access_token.py # Upstox token generation
│   └── credentials.py      # API credentials
└── Configuration:
    ├── requirements.txt    # Full dependencies
    ├── requirements-minimal.txt # Minimal dependencies
    └── .gitignore         # Git ignore rules
```

## Environment Variables (Optional)

For enhanced security, you can use environment variables:

```bash
# Create .env file
export FYERS_CLIENT_ID="your_client_id"
export FYERS_SECRET_KEY="your_secret_key"
export UPSTOX_CLIENT_ID="your_upstox_client_id"
export UPSTOX_CLIENT_SECRET="your_upstox_secret"
```

## Troubleshooting

### Common Issues:

1. **Chrome WebDriver Issues:**
   - Ensure Chrome browser is installed
   - Update Chrome to latest version
   - Check webdriver-manager installation

2. **API Authentication Issues:**
   - Verify credentials in `credentials.py`
   - Check if access tokens are valid
   - Ensure proper redirect URIs

3. **Database Issues:**
   - Check SQLite permissions
   - Ensure data directories exist
   - Verify database file paths

### Logs:
- Check `logs/` directory for detailed error logs
- Monitor trade logs in `data/trade_logs/`

## Security Notes

- Never commit real credentials to version control
- Use environment variables for production
- Regularly rotate access tokens
- Monitor trade logs for unauthorized activity

## Support

For issues and questions:
1. Check the logs in `logs/` directory
2. Review trade logs in `data/trade_logs/`
3. Verify all credentials are properly configured
4. Ensure all dependencies are installed correctly 