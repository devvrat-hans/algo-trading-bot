# Algo Trading Bot for Upstox

## Overview

This project is an algorithmic trading bot designed to execute live trades on the Upstox platform using the Upstox API. The bot is highly configurable, supports robust risk management, and is built for simplicity, modularity, and safety. It is intended for use by traders and developers who want to automate trading strategies with strict controls on risk and trade execution.

---

## Features

- **Live Trading on Upstox**: Connects to your Upstox account and places real trades.
- **Configurable via `.env`**: All trading parameters, credentials, and risk limits are set in a single environment file.
- **No Hardcoded Values**: Instrument keys, quantities, and all limits are loaded from configuration.
- **Risk Management**: Enforces stop loss, take profit, maximum trades per day, and maximum daily loss with immediate position closure.
- **Strategy Modularization**: Trading logic (e.g., EMA crossover) is separated for easy customization.
- **No Logging or Fallbacks**: Clean, simple code with no hidden behaviors.
- **No `.pyc` Files**: Prevents generation of Python bytecode files for a clean workspace.
- **Rich Terminal Output**: Enhanced, readable, and informative terminal logs for real-time monitoring.

---

## Project Structure

```
.
├── A_account_connect.py         # Handles Upstox account authentication
├── B_market_data.py            # Fetches historical and live market data
├── C_strategy.py               # Processes market data and generates trading signals
├── D_order_execution.py        # Places buy/sell orders via Upstox API
├── E_risk_management.py        # Enforces risk management rules
├── F_get_prices.py             # Fetches live prices for instruments
├── G_get_expiry.py             # Calculates expiry dates for options
├── H_get_trading_instrument.py # Finds tradable instruments for options
├── W_trade_manager.py          # Main trading loop and orchestration
├── Y_config.py                 # Loads environment variables
├── Z_account_connect.json      # Stores account connection details (if needed)
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration (user-provided)
├── .env.example                # Example environment configuration
├── __pycache__/                # (Ignored) Python bytecode cache
├── strategies/
│   └── strategy_01.py          # Example EMA crossover strategy
└── indicators/                 # (Optional) Custom indicators
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/devvrat-hans/algo-trading-bot
cd algo-trading-bot
```

### 2. Create and Activate a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

- Copy `.env.example` to `.env`:
  ```bash
  cp .env.example .env
  ```
- Fill in your Upstox API credentials and trading parameters in `.env`:

  ```ini
  UPSTOX_REDIRECT_URI=https://your-redirect-uri
  UPSTOX_API_KEY=your_api_key
  UPSTOX_API_SECRET=your_api_secret
  INSTRUMENT_KEY=NSE_EQ|INE848E01016
  ASSET_SYMBOL=BANKNIFTY
  UNIT=minutes
  INTERVAL=1
  QUANTITY=1
  STOP_LOSS=1000
  TAKE_PROFIT=3000
  MAX_TRADES_PER_DAY=5
  MAX_DAILY_LOSS=1500
  TRADE_CHECK_INTERVAL=60
  MAX_RUNTIME=25200
  ```

---

## Usage

### 1. Start the Trading Bot

```bash
python W_trade_manager.py
```

### 2. Authorize the Application

- On first run, you will be prompted with a URL to authorize the app with Upstox.
- Visit the URL, log in, and authorize the app.
- Copy the redirect URL you are sent to and paste it back into the terminal when prompted.

### 3. Monitor the Terminal Output

- The bot will display real-time logs of:
  - Current positions and P&L
  - Trade signals and executions
  - Risk management actions
  - Session summaries and statistics

### 4. Stopping the Bot

- The bot will automatically stop if any risk limit is hit or the maximum runtime is reached.
- All open positions will be closed before exit.

---

## Risk Management

The bot enforces the following risk controls (all set in `.env`):

- **STOP_LOSS**: Maximum loss per position before immediate closure
- **TAKE_PROFIT**: Target profit per position before immediate closure
- **MAX_TRADES_PER_DAY**: Maximum number of trades allowed per day
- **MAX_DAILY_LOSS**: Maximum cumulative loss allowed per day
- **MAX_RUNTIME**: Maximum session duration (in seconds)

All risk checks are performed before every trade and on every tick. If any limit is breached, the bot will close all open positions and halt trading.

---

## Strategy

The default strategy is a 9-15 EMA crossover with volume and momentum filters, implemented in `strategies/strategy_01.py`. You can modify or replace this strategy as needed. The main trading loop in `W_trade_manager.py` calls the strategy via `C_strategy.py`.

---

## Customization

- **Add New Strategies**: Place new strategy files in the `strategies/` directory and update `C_strategy.py` to use them.
- **Change Instruments**: Update `INSTRUMENT_KEY` and `ASSET_SYMBOL` in `.env`.
- **Adjust Risk Parameters**: Edit `.env` to change stop loss, take profit, and other limits.

---

## Preventing `.pyc` Files

- The bot sets `sys.dont_write_bytecode = True` in the main script to prevent `.pyc` file generation.
- You can also run with `PYTHONDONTWRITEBYTECODE=1 python W_trade_manager.py` or use the `-B` flag.
- The `.gitignore` file excludes `__pycache__/` and `.pyc` files from version control.

---

## Troubleshooting

- **Authentication Issues**: Ensure your Upstox API credentials and redirect URI are correct in `.env`.
- **No Trades Executed**: Check that your strategy is generating signals and that you have sufficient funds in your Upstox account.
- **API Errors**: Review terminal output for error messages. Most API exceptions are printed to the terminal.
- **No Market Data**: Ensure the instrument key is valid and the market is open.

---

## Security & Safety

- **Never share your `.env` file or API credentials.**
- The bot is for educational and research purposes. Use with caution and at your own risk.
- Test thoroughly in a sandbox or with small amounts before live deployment.

---

## License

This project is provided for educational purposes. Use at your own risk. No warranty is provided.

---

## Acknowledgements

- [Upstox API Documentation](https://upstox.com/developer/api-documentation/)
- [pandas](https://pandas.pydata.org/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## Contact

For questions or contributions, please open an issue or pull request on the repository.
