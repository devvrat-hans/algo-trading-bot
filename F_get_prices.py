import sys
sys.dont_write_bytecode = True

import upstox_client
from upstox_client.rest import ApiException
from Y_config import load_env

def get_live_price(access_token, instrument_key):
    """
    Fetches the latest live price for the specified trading instrument.

    Args:
        access_token (str): The access token for API authentication
        instrument_key (str): The unique identifier for the trading instrument

    Returns:
        float: The most recent traded price of the instrument.
    """
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    api_version = '2.0'

    api_instance = upstox_client.MarketQuoteApi(upstox_client.ApiClient(configuration))

    try:
        api_response = api_instance.get_full_market_quote(instrument_key, api_version)
        
        if api_response.data and len(api_response.data) > 0:
            for key, market_data in api_response.data.items():
                return market_data.last_price
        return None
    except ApiException as e:
        print(f"Exception when calling MarketQuoteApi->get_full_market_quote: {e}")
        return None

if __name__ == "__main__":
    from A_account_connect import account_connect
    config = load_env()
    account_details = account_connect()
    instrument_key = config.get('INSTRUMENT_KEY')
    access_token = account_details.get('access_token')
    
    live_price = get_live_price(access_token, instrument_key)
    print(f"Live price for {instrument_key}: {live_price}")