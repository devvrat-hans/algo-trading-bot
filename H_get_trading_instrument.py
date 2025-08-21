import sys
sys.dont_write_bytecode = True

import pandas as pd
from G_get_expiry import get_expiry_weekly_current_week
from Y_config import load_env

def get_trading_instrument():
    """
    Fetches the trading instrument data for the current week's expiry from the Upstox API 
    and returns it as a DataFrame.
        
    Returns:
        pd.DataFrame: DataFrame containing filtered option contracts for the current week.
    """
    config = load_env()
    asset_symbol = config.get('ASSET_SYMBOL') # e.g., BANKNIFTY
    expiry = get_expiry_weekly_current_week()

    instruments_link = 'https://assets.upstox.com/market-quote/instruments/exchange/complete.csv.gz'
    try:
        instruments_df = pd.read_csv(instruments_link)
    except Exception as e:
        print(f"Error fetching instruments file: {e}")
        return pd.DataFrame()
    
    # Filter for NSE options only for the specified underlying asset
    instruments_df = instruments_df[
        (instruments_df['exchange'] == 'NSE_FO') & 
        (instruments_df['instrument_type'].isin(['CE', 'PE'])) &
        (instruments_df['tradingsymbol'].str.startswith(asset_symbol, na=False))
    ]
    
    if instruments_df.empty:
        return pd.DataFrame()

    # Convert expiry to datetime and filter for current week expiry
    instruments_df['expiry'] = pd.to_datetime(instruments_df['expiry']).dt.date
    
    instruments_df = instruments_df[instruments_df['expiry'] == expiry]
    
    return instruments_df

if __name__ == "__main__":
    from A_account_connect import account_connect
    from B_market_data import market_data

    trading_instrument_df = get_trading_instrument()
    
    print("Trading Instrument Data for Current Expiry:")
    print(trading_instrument_df.head())
    print(f"\nExpiry Date Used: {get_expiry_weekly_current_week()}")
    print(f"Total Instruments Found: {len(trading_instrument_df)}")