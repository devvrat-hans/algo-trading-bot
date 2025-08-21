import sys
sys.dont_write_bytecode = True

from strategies.strategy_01 import generate_signal
from Y_config import load_env

def process_market_data(market_data_df):
    """
    Process market data and generate trading signals.
    
    Args:
        market_data_df (pd.DataFrame): DataFrame containing OHLCV data
        
    Returns:
        str: Trading signal ('buy', 'sell', or 'hold')
    """
    if market_data_df is None or market_data_df.empty:
        return 'hold'
    
    signal = generate_signal(market_data_df)
    return signal

if __name__ == "__main__":
    from A_account_connect import account_connect
    from B_market_data import market_data
    
    config = load_env()
    account_details = account_connect()
    access_token = account_details.get('access_token')
    
    instrument_key = config.get('INSTRUMENT_KEY')
    unit = config.get('UNIT')
    interval = config.get('INTERVAL')
    
    req_market_data = market_data(access_token, instrument_key, unit, interval)
    signal = process_market_data(req_market_data)
    print(f"Generated signal: {signal}")
    
    if req_market_data is not None and not req_market_data.empty and len(req_market_data) >= 20:
        latest = req_market_data.iloc[-1]
        print(f"Latest Close: {latest['Close']}")
        print(f"EMA 9: {latest['EMA_9']:.2f}")
        print(f"EMA 15: {latest['EMA_15']:.2f}")
        print(f"Volume: {latest['Volume']}")
        print(f"Avg Volume (10): {latest['Avg_Volume_10']:.0f}")