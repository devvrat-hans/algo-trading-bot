import sys
sys.dont_write_bytecode = True

import upstox_client
from upstox_client.rest import ApiException
from A_account_connect import account_connect
from G_get_expiry import get_expiry_weekly_current_week
from Y_config import load_env

def get_instrument_key(access_token, instrument_key, expiry):
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    apiInstance = upstox_client.ExpiredInstrumentApi(upstox_client.ApiClient(configuration))
    try:
        response = apiInstance.get_expired_option_contracts(instrument_key, expiry)
        return response
    except ApiException as e:
        print("Exception when calling expired instrument api: %s\n" % e)

if __name__ == "__main__":
    config = load_env()
    account_details = account_connect()
    access_token = account_details.get('access_token')
    instrument_key = config.get('INSTRUMENT_KEY')
    expiry = get_expiry_weekly_current_week()

    response = get_instrument_key(access_token, instrument_key, expiry)
    print(response)