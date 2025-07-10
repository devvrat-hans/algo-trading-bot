from Y_config import load_env
import upstox_client
from upstox_client.rest import ApiException

config = load_env() 
UPSTOX_API_KEY = config.get('UPSTOX_API_KEY')
UPSTOX_API_SECRET = config.get('UPSTOX_API_SECRET')
UPSTOX_REDIRECT_URI = config.get('UPSTOX_REDIRECT_URI')

def account_connect():
    """
    Connects to Upstox account and obtains authentication tokens.
    
    Args:
        None
        
    Returns:
        dict: Authentication data including:
            - email (str): User's email address
            - exchanges (list): List of exchanges the user is connected to
            - products (list): List of products the user is subscribed to
            - broker (str): Name of the broker
            - user_id (str): Upstox user ID
            - user_name (str): Name of the user
            - order_types (list): List of order types available
            - user_type (str): Type of user account (e.g., 'individual')
            - poa (str): Power of Attorney status
            - is_active (bool): Whether the account is active
            - access_token (str): Access token for API authentication
            - extended_token (str): Extended access token for API authentication
    """

    url=f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={UPSTOX_API_KEY}&redirect_uri={UPSTOX_REDIRECT_URI}&state=aback"

    print("Please visit the following URL to authorize the application:")
    print(url)

    output_url = input("After authorizing, please enter the URL you were redirected to: ")

    if UPSTOX_REDIRECT_URI not in output_url:
        print("The URL does not match the expected redirect URI.")
    else:   
        code = output_url.split("code=")[-1].split("&")[0]

        api_instance = upstox_client.LoginApi()
        try:
            api_response = api_instance.token('2.0', code=code, client_id=UPSTOX_API_KEY, client_secret=UPSTOX_API_SECRET,
                                            redirect_uri=UPSTOX_REDIRECT_URI, grant_type='authorization_code')
            return {
                "email": api_response.email,
                "exchanges": api_response.exchanges,
                "products": api_response.products,
                "broker": api_response.broker,
                "user_id": api_response.user_id,
                "user_name": api_response.user_name,
                "order_types": api_response.order_types,
                "user_type": api_response.user_type,
                "poa": api_response.poa,
                "is_active": api_response.is_active,
                "access_token": api_response.access_token,
                "extended_token": api_response.extended_token
            }
        except ApiException as e:
            print("Exception when calling LoginApi->token: %s\n" % e)

if __name__ == "__main__":
    account_details = account_connect()
    for key, value in account_details.items():
        print(f"{key}: {value}")

