"""
Configuration file for the Algo Trading Bot
Contains all trading parameters, symbols, and API configurations
"""

import os
from typing import Dict, List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, will use system environment variables
    pass

# =============================================================================
# ALPACA API CONFIGURATION
# =============================================================================
ALPACA_CONFIG = {
    # Paper trading (sandbox) URLs - change to live for production
    'base_url': 'https://paper-api.alpaca.markets',  # Paper trading
    'data_url': 'https://data.alpaca.markets',
    
    # API Keys - Set these as environment variables for security
    'api_key': os.getenv('ALPACA_API_KEY', ''),
    'secret_key': os.getenv('ALPACA_SECRET_KEY', ''),
    
    # Live trading URLs (uncomment for live trading)
    # 'base_url': 'https://api.alpaca.markets',
    
    # Trading settings
    'market': 'us',  # 'us' for US markets, 'crypto' for crypto
    'timeout': 30,  # Request timeout in seconds
}

# =============================================================================
# TRADING INSTRUMENTS CONFIGURATION
# =============================================================================

# Default instrument for trading
DEFAULT_INSTRUMENT = "SPY"  # US market equivalent to Nifty 50

# Index symbols for different markets
INDEX_SYMBOLS = {
    'us': {
        'sp500': 'SPY',      # S&P 500 ETF
        'nasdaq': 'QQQ',     # Nasdaq 100 ETF
        'dow': 'DIA',        # Dow Jones ETF
        'russell': 'IWM',    # Russell 2000 ETF
    },
    'indian': {
        'nifty50': '^NSEI',     # For yfinance data only
        'banknifty': '^NSEBANK',  # For yfinance data only
        'sensex': '^BSESN',     # For yfinance data only
    }
}

# Equity symbols for trading
EQUITY_SYMBOLS = {
    'us_tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA'],
    'us_finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C'],
    'us_healthcare': ['JNJ', 'PFE', 'UNH', 'MRNA', 'ABT'],
    'etfs': ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO']
}

# Futures and Options symbols (Alpaca supports limited F&O)
FNO_SYMBOLS = {
    'futures': {
        # Alpaca supports crypto futures and some commodity futures
        'bitcoin': 'BTCUSD',
        'ethereum': 'ETHUSD',
    },
    'options': {
        # Options on major ETFs and stocks
        'spy_options': 'SPY',
        'qqq_options': 'QQQ',
        'aapl_options': 'AAPL',
    }
}

# =============================================================================
# TRADING PARAMETERS
# =============================================================================

# SuperTrend indicator configuration
SUPERTREND_CONFIG = {
    'default_period': 10,
    'default_multiplier': 3.0,
    'timeframes': ['1m', '5m', '15m', '1h', '1d'],
    'default_timeframe': '5m'
}

# Risk management parameters
RISK_MANAGEMENT = {
    'max_position_size': 1000,      # Maximum position size in USD
    'max_portfolio_risk': 0.02,     # Maximum 2% portfolio risk per trade
    'stop_loss_pct': 0.02,          # 2% stop loss
    'take_profit_pct': 0.04,        # 4% take profit
    'max_daily_trades': 10,         # Maximum trades per day
    'max_open_positions': 5,        # Maximum concurrent positions
}

# Order configuration
ORDER_CONFIG = {
    'default_order_type': 'market',  # 'market', 'limit', 'stop', 'stop_limit'
    'default_time_in_force': 'day',  # 'day', 'gtc', 'ioc', 'fok'
    'default_side': 'buy',           # 'buy', 'sell'
    'default_symbol': DEFAULT_INSTRUMENT,  # Default trading symbol
    'fractional_shares': True,       # Allow fractional shares
    'extended_hours': False,         # Trade during extended hours
}

# Position sizing methods
POSITION_SIZING = {
    'method': 'fixed_amount',        # 'fixed_amount', 'fixed_percentage', 'volatility_based'
    'fixed_amount': 1000,            # Fixed USD amount per trade
    'fixed_percentage': 0.1,         # 10% of portfolio per trade
    'volatility_multiplier': 1.0,    # For volatility-based sizing
}

# =============================================================================
# MARKET HOURS AND TIMING
# =============================================================================

MARKET_HOURS = {
    'us_market': {
        'open': '09:30',    # 9:30 AM ET
        'close': '16:00',   # 4:00 PM ET
        'timezone': 'US/Eastern'
    },
    'premarket': {
        'start': '04:00',   # 4:00 AM ET
        'end': '09:30',     # 9:30 AM ET
    },
    'aftermarket': {
        'start': '16:00',   # 4:00 PM ET
        'end': '20:00',     # 8:00 PM ET
    }
}

# Trading session configuration
TRADING_SESSIONS = {
    'regular_hours_only': True,      # Trade only during regular market hours
    'allow_premarket': False,        # Allow pre-market trading
    'allow_afterhours': False,       # Allow after-hours trading
}

# =============================================================================
# DATA AND BACKTESTING CONFIGURATION
# =============================================================================

DATA_CONFIG = {
    'data_provider': 'alpaca',       # 'alpaca', 'yfinance', 'polygon'
    'backup_provider': 'yfinance',   # Backup data source
    'default_period': '1d',          # Default historical data period
    'default_interval': '5m',        # Default data interval
    'max_bars': 1000,               # Maximum bars to fetch
}

BACKTESTING_CONFIG = {
    'initial_capital': 100000,       # Starting capital for backtesting
    'commission': 0.0,              # Commission per trade (Alpaca is commission-free)
    'slippage': 0.001,              # 0.1% slippage assumption
    'start_date': '2023-01-01',     # Backtest start date
    'end_date': '2024-12-31',       # Backtest end date
}

# =============================================================================
# NOTIFICATION AND LOGGING
# =============================================================================

NOTIFICATION_CONFIG = {
    'enable_email': False,
    'enable_slack': False,
    'enable_telegram': False,
    'enable_console': True,          # Always log to console
    'log_level': 'INFO',            # DEBUG, INFO, WARNING, ERROR
}

LOGGING_CONFIG = {
    'log_file': 'trading_bot.log',
    'max_file_size': '10MB',
    'backup_count': 5,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# =============================================================================
# STRATEGY CONFIGURATION
# =============================================================================

STRATEGY_CONFIG = {
    'active_strategies': ['supertrend'],  # List of active strategies
    'strategy_weights': {                 # Weight allocation for each strategy
        'supertrend': 1.0,
    },
    'rebalance_frequency': 'daily',       # How often to rebalance
}

# =============================================================================
# ENVIRONMENT SETTINGS
# =============================================================================

ENVIRONMENT = {
    'mode': 'paper',                # 'paper' or 'live'
    'debug': True,                  # Enable debug mode
    'dry_run': False,               # If True, don't place actual orders
    'save_trades': True,            # Save trade history
    'trade_log_file': 'trades.csv', # Trade log file
}

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check API keys
    if not ALPACA_CONFIG['api_key']:
        errors.append("ALPACA_API_KEY environment variable not set")
    
    if not ALPACA_CONFIG['secret_key']:
        errors.append("ALPACA_SECRET_KEY environment variable not set")
    
    # Check risk management parameters
    if RISK_MANAGEMENT['max_portfolio_risk'] > 0.1:
        errors.append("Portfolio risk too high (>10%)")
    
    if RISK_MANAGEMENT['stop_loss_pct'] > 0.1:
        errors.append("Stop loss too wide (>10%)")
    
    # Check position sizing
    if POSITION_SIZING['method'] not in ['fixed_amount', 'fixed_percentage', 'volatility_based']:
        errors.append("Invalid position sizing method")
    
    return errors

def get_trading_symbol(market='us', category='index', symbol_key='sp500'):
    """Get trading symbol based on market and category"""
    if market == 'us':
        if category == 'index':
            return INDEX_SYMBOLS['us'].get(symbol_key, 'SPY')
        elif category == 'equity':
            return EQUITY_SYMBOLS.get(symbol_key, ['SPY'])[0]
    
    return DEFAULT_INSTRUMENT

def is_market_open():
    """Check if the market is currently open (placeholder)"""
    # This would implement actual market hours checking
    return True

# =============================================================================
# EXPORT COMMONLY USED CONFIGURATIONS
# =============================================================================

# Quick access to frequently used configs
API_KEY = ALPACA_CONFIG['api_key']
SECRET_KEY = ALPACA_CONFIG['secret_key']
BASE_URL = ALPACA_CONFIG['base_url']
DEFAULT_SYMBOL = DEFAULT_INSTRUMENT
MAX_POSITION_SIZE = RISK_MANAGEMENT['max_position_size']
STOP_LOSS_PCT = RISK_MANAGEMENT['stop_loss_pct']

if __name__ == "__main__":
    # Test configuration
    print("Configuration Test")
    print("=" * 50)
    
    # Validate config
    errors = validate_config()
    if errors:
        print("Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Configuration is valid")
    
    print(f"\nDefault Trading Symbol: {DEFAULT_SYMBOL}")
    print(f"Market Mode: {ENVIRONMENT['mode']}")
    print(f"Max Position Size: ${MAX_POSITION_SIZE}")
    print(f"Stop Loss: {STOP_LOSS_PCT*100}%")
