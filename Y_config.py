import os
from dotenv import load_dotenv
load_dotenv(override=True)

def load_env():
    """
    Load environment variables from a .env file.
    """
    config = {
        "UPSTOX_REDIRECT_URI": os.getenv("UPSTOX_REDIRECT_URI"),
        "UPSTOX_API_KEY": os.getenv("UPSTOX_API_KEY"),
        "UPSTOX_API_SECRET": os.getenv("UPSTOX_API_SECRET"),
        "INSTRUMENT_KEY": os.getenv("INSTRUMENT_KEY"),
        "ASSET_SYMBOL": os.getenv("ASSET_SYMBOL"),
        "UNIT": os.getenv("UNIT"),
        "INTERVAL": os.getenv("INTERVAL"),
        "QUANTITY": int(os.getenv("QUANTITY")),
        "STOP_LOSS": float(os.getenv("STOP_LOSS")),
        "TAKE_PROFIT": float(os.getenv("TAKE_PROFIT")),
        "MAX_TRADES_PER_DAY": int(os.getenv("MAX_TRADES_PER_DAY")),
        "MAX_DAILY_LOSS": float(os.getenv("MAX_DAILY_LOSS")),
        "TRADE_CHECK_INTERVAL": float(os.getenv("TRADE_CHECK_INTERVAL")),
        "MAX_RUNTIME": float(os.getenv("MAX_RUNTIME")),
    }
    return config

if __name__ == '__main__':
    config = load_env()
    for key, value in config.items():
        print(f"{key}: {value}")
        