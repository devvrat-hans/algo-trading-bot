import pandas as pd
from G_get_expiry import get_expiry_weekly_next_week
from strategies.strategy_01 import generate_signal

def get_trading_instrument(req_market_data):

    """
    Fetches the trading instrument data from the Upstox API and returns it as a DataFrame.
    """
    expiry = get_expiry_weekly_next_week()

    instruments_link = 'https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz'
    instruments_df = pd.read_json(instruments_link)
    instruments_df['expiry'] = pd.to_datetime(instruments_df['expiry'], unit='ms', errors='coerce')
    instruments_df['expiry'] = instruments_df['expiry'].dt.date
    instruments_df['expiry'] = pd.to_datetime(instruments_df['expiry'])

    instruments_df = instruments_df[instruments_df['expiry'] == expiry]

    if generate_signal(req_market_data) == 'BUY':
        instruments_df = instruments_df[instruments_df['instrument_type'] == 'CE']
    elif generate_signal(req_market_data) == 'SELL':
        instruments_df = instruments_df[instruments_df['instrument_type'] == 'PE']
    
    return instruments_df


if __name__ == "__main__":
    from A_account_connect import account_connect
    from B_market_data import market_data
    from Y_config import load_env

    config = load_env()
    account_details = account_connect()
    access_token = account_details.get('access_token')

    instrument_key = config.get('INSTRUMENT_KEY')
    unit = config.get('UNIT')
    interval = config.get('INTERVAL')

    req_market_data = market_data(access_token, instrument_key, unit, interval)
    
    trading_instrument_df = get_trading_instrument(req_market_data)
    
    print("Trading Instrument Data:")
    print(trading_instrument_df.head())
    print(f"Expiry Date: {get_expiry_weekly_next_week()}")
