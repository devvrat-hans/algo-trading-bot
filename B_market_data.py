import upstox_client
import pandas as pd
from Y_config import load_env

config = load_env() 
INSTRUMENT_KEY = config.get('INSTRUMENT_KEY')
UNIT = config.get('UNIT')
INTERVAL = config.get('INTERVAL')

def market_data(instrument_key=INSTRUMENT_KEY, unit=UNIT, interval=INTERVAL):
    """
    Fetch historical candle data for a given stock or index. 

    Args:
        instrument_key (str): The instrument key for the stock or index.
        unit (str): The unit of time for the data (e.g., 'minutes', 'days').
        interval (str): The interval for the data (e.g., '1', '5', '15', '30', '60').
        
    Returns:
        pd.DataFrame: A DataFrame containing the historical candle data with columns for Timestamp, Open, High, Low, Close, Volume, and Open Interest.
    """

    apiInstance = upstox_client.HistoryV3Api()
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
    instrument_key='NSE_INDEX|Nifty Bank'
    unit='minutes'
    interval='5'
    data=market_data(instrument_key=instrument_key, unit=unit, interval=interval)
    print(data)