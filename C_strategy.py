from B_market_data import market_data 
from Y_config import load_env

config = load_env() 
INSTRUMENT_KEY = config.get('INSTRUMENT_KEY')
UNIT = config.get('UNIT')
INTERVAL = config.get('INTERVAL')

req_market_data = market_data(instrument_key=INSTRUMENT_KEY, unit=UNIT, interval=INTERVAL)

def generate_signal(req_market_data):
    """
    Analyzes market data and generates a trading signal.

    Args:
        market_data (pd.DataFrame): DataFrame containing OHLCV data with columns for
                                   Timestamp, Open, High, Low, Close, Volume, and Open Interest.

    Returns:
        str: Trading signal, one of:
             - 'buy': Recommendation to enter a long position
             - 'sell': Recommendation to enter a short position or exit long
             - 'hold': Recommendation to maintain current position
    """


    if req_market_data is None or req_market_data.empty:
        return 'hold'

    latest_candle = req_market_data.iloc[-1]
    
    if latest_candle['Close'] > latest_candle['Open']:
        return 'buy'
    elif latest_candle['Close'] < latest_candle['Open']:
        return 'sell'
    else:
        return 'hold'


if __name__ == "__main__":
    signal = generate_signal(req_market_data=None)
    print(f"Generated signal: {signal}")

