import upstox_client
from upstox_client.rest import ApiException
from Y_config import load_env
from A_account_connect import account_connect

config = load_env()
account_details = account_connect()

INSTRUMENT_KEY = config.get('INSTRUMENT_KEY')
QUANTITY = config.get('QUANTITY')
ACCESS_TOKEN = account_details.get('access_token')


def execute_buy_order(instrument_key=INSTRUMENT_KEY, quantity=QUANTITY):
    """
    Places a buy order on Upstox based on the trading signal.
    
    Args:
        instrument_key (str): The instrument key for the stock or index to trade.
        quantity (int): Number of shares or contracts to trade.
        
    Returns:
        dict: Order details including:
              - order_id (str): Unique identifier for the placed order
              - status (str): Status of the order ('COMPLETE', 'REJECTED', etc.)
              - average_price (float): Execution price if filled
              - quantity (int): Quantity that was ordered
    """

    configuration = upstox_client.Configuration()
    configuration.access_token = ACCESS_TOKEN
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

def execute_sell_order(instrument_key=INSTRUMENT_KEY, quantity=QUANTITY):
    """
    Places a sell order on Upstox based on the trading signal.
    
    Args:
        instrument_key (str): The instrument key for the stock or index to trade.
        quantity (int): Number of shares or contracts to trade.
        
    Returns:
        dict: Order details including:
              - order_id (str): Unique identifier for the placed order
              - status (str): Status of the order ('COMPLETE', 'REJECTED', etc.)
              - average_price (float): Execution price if filled
              - quantity (int): Quantity that was ordered
    """

    configuration = upstox_client.Configuration()
    configuration.access_token = ACCESS_TOKEN
    api_instance = upstox_client.OrderApiV3(upstox_client.ApiClient(configuration))
    body = upstox_client.PlaceOrderV3Request(quantity=quantity, product="D", validity="DAY", 
        price=0, tag="string", instrument_token=instrument_key, 
        order_type="MARKET", transaction_type="SELL", disclosed_quantity=0, 
        trigger_price=0.0, is_amo=False, slice=True)

    try:
        api_response = api_instance.place_order(body)
        return api_response
    except ApiException as e:
        print("Exception when calling OrderApiV3->place_order: %s\n" % e)


if __name__ == "__main__":
    buy_order_stats = execute_buy_order(instrument_key=INSTRUMENT_KEY, quantity=QUANTITY)
    sell_order_stats = execute_sell_order(instrument_key=INSTRUMENT_KEY, quantity=QUANTITY)
    if buy_order_stats:
        print(f"Buy Order ID: {buy_order_stats.data.order_ids}, Status: {buy_order_stats.status}, "
              f"Latency: {buy_order_stats.metadata.latency}")
    else:
        print("Failed to execute buy order.")
    if sell_order_stats:
        print(f"Sell Order ID: {sell_order_stats.data.order_ids}, Status: {sell_order_stats.status}, "
              f"Latency: {sell_order_stats.metadata.latency}")
    else:
        print("Failed to execute sell order.")
    print("Orders executed successfully.")