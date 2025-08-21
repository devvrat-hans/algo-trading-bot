import sys
sys.dont_write_bytecode = True

import upstox_client
from upstox_client.rest import ApiException
from Y_config import load_env

def execute_buy_order(access_token, instrument_key, quantity):
    """
    Places a buy order on Upstox based on the trading signal.
    
    Args:
        access_token (str): The access token for API authentication
        instrument_key (str): The instrument key for the stock or index to trade.
        quantity (int): Number of shares or contracts to trade.
        
    Returns:
        dict: Order details including order_id, status, etc.
    """
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    api_instance = upstox_client.OrderApiV3(upstox_client.ApiClient(configuration))
    body = upstox_client.PlaceOrderV3Request(quantity=quantity, product="D", validity="DAY", 
        price=0, tag="string", instrument_token=instrument_key, 
        order_type="MARKET", transaction_type="BUY", disclosed_quantity=0, 
        trigger_price=0.0, is_amo=False, slice=True)

    try:
        api_response = api_instance.place_order(body)
        return api_response
    except ApiException as e:
        print("Exception when calling OrderApiV3->place_order: %s\n" % e)
        return None

def execute_sell_order(access_token, instrument_key, quantity):
    """
    Places a sell order on Upstox based on the trading signal.
    
    Args:
        access_token (str): The access token for API authentication
        instrument_key (str): The instrument key for the stock or index to trade.
        quantity (int): Number of shares or contracts to trade.
        
    Returns:
        dict: Order details including order_id, status, etc.
    """
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    api_instance = upstox_client.OrderApiV3(upstox_client.ApiClient(configuration))
    body = upstox_client.PlaceOrderV3Request(quantity=quantity, product="D", validity="DAY", 
        price=0, tag="string", instrument_token=instrument_key, 
        order_type="MARKET", transaction_type="SELL", disclosed_quantity=0, 
        trigger_price=0.0, is_amo=False, slice=True)

    try:
        api_response = api_instance.place_order(body)
        return api_response
    except ApiException as e:
        print(f"Exception when calling OrderApiV3->place_order: {e}")
        return None

if __name__ == "__main__":
    from A_account_connect import account_connect
    config = load_env()
    account_details = account_connect()
    instrument_key = config.get('INSTRUMENT_KEY')
    quantity = config.get('QUANTITY')
    access_token = account_details.get('access_token')
    
    buy_order_stats = execute_buy_order(access_token, instrument_key, quantity)
    sell_order_stats = execute_sell_order(access_token, instrument_key, quantity)
    if buy_order_stats:
        print(f"Buy Order ID: {buy_order_stats.data.order_ids}, Status: {buy_order_stats.status}, "
              f"Latency: {buy_order_stats.metadata.latency}")
        print("Order executed successfully.")
    else:
        print("Failed to execute buy order.")
    if sell_order_stats:
        print(f"Sell Order ID: {sell_order_stats.data.order_ids}, Status: {sell_order_stats.status}, "
              f"Latency: {sell_order_stats.metadata.latency}")
        print("Order executed successfully.")
    else:
        print("Failed to execute sell order.")
    