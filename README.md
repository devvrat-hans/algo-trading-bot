# Algo Trading Bot with SuperTrend Strategy

A Python-based algorithmic trading bot that uses the SuperTrend indicator to generate buy/sell signals and automatically executes trades using the Alpaca API.

## Features

- **SuperTrend Strategy**: Implements the SuperTrend technical indicator for trend-following trades
- **Alpaca Integration**: Seamless integration with Alpaca's commission-free trading API
- **Risk Management**: Built-in stop-loss, take-profit, and position sizing controls
- **Paper Trading**: Test strategies with simulated trading before going live
- **Real-time Monitoring**: Continuous market monitoring with configurable check intervals
- **Comprehensive Logging**: Detailed logging and trade history tracking
- **Modular Design**: Clean, extensible architecture for adding new strategies

## Project Structure

```
algo-trading-bot/
├── config.py                    # Configuration settings
├── get_candles.py               # Market data provider using yfinance
├── place_order.py               # Order execution using Alpaca API
├── trading_bot.py               # Main integrated trading bot
├── setup.py                     # Setup and installation script
├── requirements.txt             # Python dependencies
├── indicators/
│   └── superTrend.py           # SuperTrend indicator implementation
└── signalGenerators/
    └── signalSuperTrend.py     # SuperTrend signal generator
```

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Alpaca brokerage account (free at [alpaca.markets](https://alpaca.markets))
- Basic understanding of trading concepts

### 2. Installation

Clone the repository and run the setup script:

```bash
git clone <repository-url>
cd algo-trading-bot
python setup.py
```

The setup script will:
- Install all required Python packages
- Help you configure your Alpaca API credentials
- Test the connection to Alpaca
- Create necessary configuration files

### 3. Get Alpaca API Credentials

1. Sign up for a free Alpaca account at [alpaca.markets](https://alpaca.markets)
2. Go to your dashboard and generate API keys
3. Use the paper trading keys for testing (recommended)

### 4. Run the Bot

```bash
python trading_bot.py
```

The bot provides an interactive menu with options to:
- Run single signal checks
- Start continuous trading
- View current positions
- Check account information

## Configuration

### Main Configuration (`config.py`)

Key settings you can customize:

```python
# Trading Symbol
DEFAULT_INSTRUMENT = "SPY"  # Default to S&P 500 ETF

# SuperTrend Parameters
SUPERTREND_CONFIG = {
    'default_period': 10,      # ATR period
    'default_multiplier': 3.0, # ATR multiplier
    'default_timeframe': '5m'  # 5-minute candles
}

# Risk Management
RISK_MANAGEMENT = {
    'max_position_size': 1000,    # Max $1000 per position
    'max_portfolio_risk': 0.02,   # Max 2% portfolio risk
    'stop_loss_pct': 0.02,        # 2% stop loss
    'take_profit_pct': 0.04,      # 4% take profit
    'max_daily_trades': 10,       # Max 10 trades per day
}
```

### Environment Variables (`.env`)

```bash
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ENVIRONMENT=paper  # Use 'live' for live trading
```

## SuperTrend Strategy

The SuperTrend indicator is a trend-following indicator that provides:

- **Buy Signal**: When price crosses above the SuperTrend line
- **Sell Signal**: When price crosses below the SuperTrend line
- **Trend Direction**: Uptrend (green) or downtrend (red)

### Parameters

- **Period (default: 10)**: Number of periods for ATR calculation
- **Multiplier (default: 3.0)**: Multiplier for the ATR to create the bands

### How It Works

1. **Data Collection**: Fetches 5-minute candlestick data
2. **Indicator Calculation**: Computes SuperTrend values
3. **Signal Generation**: Identifies buy/sell crossovers
4. **Risk Assessment**: Calculates position size and risk parameters
5. **Order Execution**: Places market orders with stop-loss and take-profit
6. **Monitoring**: Continuously monitors for new signals

## Risk Management Features

### Position Sizing
- **Fixed Amount**: Trade a fixed dollar amount per position
- **Percentage Based**: Trade a percentage of portfolio value
- **Volatility Based**: Adjust size based on market volatility

### Stop Loss & Take Profit
- Automatic stop-loss orders at configurable percentage below entry
- Take-profit orders at configurable percentage above entry
- Good-till-canceled (GTC) orders for continuous protection

### Daily Limits
- Maximum number of trades per day
- Maximum number of open positions
- Portfolio risk limits

## Usage Examples

### Basic Usage

```python
from trading_bot import AlgoTradingBot

# Initialize bot
bot = AlgoTradingBot(symbol="SPY", paper_trading=True)

# Run single check
result = bot.run_single_cycle()

# Start continuous trading (5-minute intervals)
bot.run_bot(check_interval=300, max_runtime_hours=8)
```

### Custom Signal Generation

```python
from signalGenerators.signalSuperTrend import SuperTrendSignalGenerator

# Create signal generator with custom parameters
signal_gen = SuperTrendSignalGenerator(period=14, multiplier=2.5)

# Get latest signals
signals = signal_gen.get_latest_signal()
signal_gen.display_signal_summary(signals)
```

### Manual Order Execution

```python
from place_order import AlpacaOrderManager

# Initialize order manager
order_manager = AlpacaOrderManager()

# Place market order
order = order_manager.place_market_order("SPY", 10, "buy")

# Place limit order
order = order_manager.place_limit_order("SPY", 10, "buy", 400.00)

# Check positions
positions = order_manager.get_positions()
```

## Monitoring and Logging

### Console Output
The bot provides real-time status updates including:
- Current prices and trends
- Signal generation
- Order execution
- Portfolio performance
- Risk metrics

### Log Files
- `trading_bot.log`: Detailed application logs
- `trades.csv`: Trade history and performance data

### Example Output
```
🤖 ALGO TRADING BOT STATUS - 2024-01-15 14:30:00
================================================================================
💰 Account Value: $100,000.00
💵 Buying Power: $99,500.00
📊 Daily Trades: 2/10
📈 Position: 25 shares @ $402.50
💹 P&L: $125.00 (1.24%)
🎯 Symbol: SPY
💲 Current Price: $402.50
📈 SuperTrend: $398.75
📊 Trend: UP
🟢 Signal: BUY
✅ Status: Trade Executed
⏱️ Runtime: 2:15:30
📊 Total Trades: 5
================================================================================
```

## Safety Features

### Paper Trading Mode
- All trades are simulated using Alpaca's paper trading environment
- No real money is risked
- Full functionality for testing strategies

### Dry Run Mode
- Simulate order placement without executing actual trades
- Perfect for strategy backtesting and debugging

### Connection Monitoring
- Automatic connection health checks
- Graceful error handling and recovery
- API rate limit management

## Advanced Features

### Multiple Strategies
The architecture supports multiple trading strategies:

```python
# Add new strategies to config
STRATEGY_CONFIG = {
    'active_strategies': ['supertrend', 'rsi', 'macd'],
    'strategy_weights': {
        'supertrend': 0.5,
        'rsi': 0.3,
        'macd': 0.2
    }
}
```

### Custom Indicators
Create new indicators in the `indicators/` directory:

```python
def my_custom_indicator(df, param1, param2):
    # Implement your indicator logic
    return signals
```

### Extended Market Hours
Configure trading during pre-market and after-hours:

```python
ORDER_CONFIG = {
    'extended_hours': True,  # Enable extended hours trading
}

MARKET_HOURS = {
    'premarket': {'start': '04:00', 'end': '09:30'},
    'aftermarket': {'start': '16:00', 'end': '20:00'}
}
```

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check your API credentials in `.env` file
   - Ensure you're using the correct environment (paper vs live)
   - Verify internet connection

2. **No Data Available**
   - Check if the symbol is valid and tradeable
   - Verify market hours
   - Check for API rate limits

3. **Orders Not Executing**
   - Ensure account has sufficient buying power
   - Check if the symbol is tradeable
   - Verify order parameters

4. **High Memory Usage**
   - Reduce the data history period
   - Increase check intervals
   - Monitor for memory leaks in custom code

### Debug Mode

Enable debug mode for detailed logging:

```python
ENVIRONMENT = {
    'debug': True,
    'dry_run': True,  # Enable for testing
}
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-strategy`)
3. Commit your changes (`git commit -am 'Add new strategy'`)
4. Push to the branch (`git push origin feature/new-strategy`)
5. Create a Pull Request

## Disclaimer

**⚠️ Important Risk Warning ⚠️**

This software is for educational and informational purposes only. Trading involves substantial risk and is not suitable for all investors. Past performance does not guarantee future results.

- **Test First**: Always test strategies with paper trading before using real money
- **Risk Management**: Never risk more than you can afford to lose
- **No Guarantees**: No trading strategy guarantees profits
- **Your Responsibility**: You are solely responsible for your trading decisions
- **Market Risks**: Markets can be unpredictable and volatile

The authors and contributors are not responsible for any financial losses incurred through the use of this software.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues, or feature requests:
1. Check the existing issues on GitHub
2. Create a new issue with detailed information
3. Join our community discussions

## Acknowledgments

- [Alpaca Markets](https://alpaca.markets) for providing commission-free trading API
- [yfinance](https://github.com/ranaroussi/yfinance) for market data
- SuperTrend indicator concept by Olivier Seban
- Python trading community for inspiration and best practices
