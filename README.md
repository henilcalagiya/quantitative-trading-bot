# QuantBot - High-Frequency Options Trading System

An automated algorithmic trading system for BANKNIFTY index options on the Indian stock market.

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Chrome browser (for Selenium automation)
- Trading accounts with Fyers, Upstox, or Zerodha

### Installation
```bash
# Clone the repository
git clone <your-repository-url>
cd "Quantitative Trading Bot"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For production (minimal dependencies):
# pip install -r requirements-minimal.txt
```

### Configuration
1. Update `credentials.py` with your API credentials
2. Generate access tokens using the provided scripts
3. See `SETUP.md` for detailed configuration instructions

## Project Structure

```
Quantitative Trading Bot/
├── data/
│   ├── trade_logs/          # Daily trade execution logs
│   │   ├── 29AUG24_Trades.txt
│   │   ├── 30AUG24_Trades.txt
│   │   └── ...
│   ├── tick_data/           # Real-time tick data databases
│   │   ├── tickdata_29AUG24.db
│   │   ├── tickdata_30AUG24.db
│   │   └── ...
│   ├── candle_data/         # Processed candle data databases
│   │   ├── candledata_29AUG24.db
│   │   ├── candledata_30AUG24.db
│   │   └── ...
│   └── realtime.db          # Real-time data database
├── logs/                    # Application logs
│   ├── fyersApi.log
│   ├── fyersDataSocket.log
│   └── fyersRequests.log
├── Core Scripts:
│   ├── functions.py             # Core trading functions
│   ├── process_live_data.py     # Main trading logic
│   ├── process_function.py      # Data processing functions
│   └── 1fetch_tick_data_live.py # Data collection script
├── Setup Scripts:
│   ├── get_access_token.py      # Fyers token generation
│   ├── get_upstox_access_token.py # Upstox token generation
│   ├── credentials.py           # API credentials
│   └── dictionaries.py          # Symbol mappings
├── Configuration:
│   ├── requirements.txt         # Full dependencies
│   ├── requirements-minimal.txt # Minimal dependencies
│   ├── .gitignore              # Git ignore rules
│   └── SETUP.md                # Detailed setup guide
└── README.md                   # This file
```

## System Flow Architecture

### High-Level Data Flow
```
Market Data Sources (NSE/Fyers API)
    ↓ Real-time WebSocket connections
Fyers WebSocket Data Feed (1fetch_tick_data_live.py)
    ↓ Tick data streaming
Real-time Tick Data Processing (functions.py)
    ↓ Data insertion
SQLite Databases (data/tick_data/tickdata_DDMMMYY.db)
    ↓ 5-second aggregation
OHLC Candle Generation (process_function.py)
    ↓ Technical indicators calculation
Technical Analysis Engine
    ├── Heiken Ashi Candles
    ├── Supertrend Indicator
    ├── ATR (Average True Range)
    └── Direction Signals
    ↓ Signal processing
Trading Decision Engine (process_live_data.py)
    ↓ Trade execution logic
Broker Integration Layer
    ├── Zerodha Kite API (kite_trade.py)
    ├── Upstox API (upstox_functions.py)
    └── Fyers API (functions.py)
    ↓ Order placement
Order Management System
    ↓ Position tracking
Active Position Monitoring
    ↓ Trade logging
Trade Logs (data/trade_logs/DDMMMYY_Trades.txt)
    ↓ Performance tracking
Session Storage + JSON Files
    ├── NSE.json (symbol data)
    ├── dictionaries.py (mappings)
    └── credentials.py (API keys)
```

### Detailed Component Flow

#### 1. **Data Collection Layer**
```
Fyers WebSocket → Real-time Tick Data → SQLite Storage
    ↓
NSE Python Library → Expiry Dates → Symbol Generation
    ↓
Market Status Check → Trading Hours Validation
```

#### 2. **Data Processing Pipeline**
```
Raw Tick Data → 5-second OHLC Candles → Heiken Ashi Conversion
    ↓
Technical Indicators → Supertrend Calculation → Direction Signals
    ↓
Signal Validation → Strike Price Selection → Trade Decision
```

#### 3. **Trading Execution Flow**
```
Buy Signal Detection → Position Exit (if any) → New Position Entry
    ↓
Broker API Call → Order Placement → Position Tracking
    ↓
Real-time Monitoring → Exit Signal Detection → Position Closure
```

#### 4. **Data Persistence Architecture**
```
Session Data → SQLite Databases → Daily Partitioning
    ├── Tick Data: tickdata_DDMMMYY.db
    ├── Candle Data: candledata_DDMMMYY.db
    └── Trade Logs: DDMMMYY_Trades.txt
```

## Features

- **Real-time trading** of BANKNIFTY CE and PE options
- **Supertrend indicator** based automated decision making
- **Multi-broker support** (Fyers, Upstox, Zerodha)
- **High-frequency data processing** with 5-second candles
- **Comprehensive trade logging** and performance tracking
- **SQLite database** storage for historical analysis

## Trading Strategy

- **Options straddle/strangle** approach
- **Supertrend-based** entry and exit signals
- **ATR-based** volatility calculations
- **Dynamic strike selection** based on current market price
- **Position size**: 15 lots per trade

## Dependencies

### Core Dependencies
- `fyers-apiv3` - Fyers API for Indian market trading
- `nsepython` - NSE Python library for market data
- `kiteconnect` - Kite Connect for Zerodha trading
- `pandas` & `numpy` - Data processing and analysis
- `requests` - HTTP requests and API calls
- `selenium` - Web automation for token generation
- `pyotp` - Two-factor authentication
- `pytz` - Timezone handling
- `schedule` - Task scheduling

### Optional Dependencies
- `jupyter` - Jupyter notebook support
- `matplotlib` & `seaborn` - Data visualization
- `pytest` - Testing framework
- `python-dotenv` - Environment variable management

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

## Data Organization

- **Trade Logs**: Daily execution records in `data/trade_logs/`
- **Tick Data**: Raw market data in `data/tick_data/`
- **Candle Data**: Processed OHLC data in `data/candle_data/`
- **Application Logs**: System logs in `logs/`

## Security

- ✅ All credentials use placeholder values
- ✅ Sensitive files excluded from version control
- ✅ Access tokens cleared from files
- ✅ Comprehensive `.gitignore` configuration

## Technology Stack

- **Python** with real-time WebSocket connections
- **SQLite** for data storage
- **Fyers/Upstox APIs** for market access
- **NSE Python library** for symbol management
- **Selenium** for automated token generation

## Documentation

- **`SETUP.md`** - Detailed setup and configuration guide
- **`requirements.txt`** - Full dependency list
- **`requirements-minimal.txt`** - Minimal production dependencies

## Support

For detailed setup instructions, troubleshooting, and configuration help, see `SETUP.md`. 
