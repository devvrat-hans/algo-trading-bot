import upstox_client
import pandas as pd
from Y_config import load_env

def market_data(access_token, instrument_key, unit, interval):
    """
    Fetch historical candle data for a given stock or index. 

    Args:
        access_token (str): The access token for API authentication
        instrument_key (str): The instrument key for the stock or index.
        unit (str): The unit of time for the data (e.g., 'minutes', 'days').
        interval (str): The interval for the data (e.g., '1', '5', '15', '30', '60').
        
    Returns:
        pd.DataFrame: A DataFrame containing the historical candle data.
    """
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    
    apiInstance = upstox_client.HistoryV3Api(upstox_client.ApiClient(configuration))
    try:
        response = apiInstance.get_intra_day_candle_data(instrument_key=instrument_key,
                                                        unit=unit,
                                                        interval=interval)
        if response.status == 'success' and response.data and response.data.candles:
            candles_data = response.data.candles
            df = pd.DataFrame(candles_data, columns=[
            'Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest'
            ])
            
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

if __name__ == "__main__":
    from A_account_connect import account_connect
    config = load_env()
    account_details = account_connect()
    access_token = account_details.get('access_token')
    instrument_key='NSE_INDEX|Nifty Bank'
    unit='minutes'
    interval='5'
    data=market_data(access_token, instrument_key, unit, interval)
    print(data)