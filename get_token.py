from tdameritrade.auth import TDAConfigProvider, access_token
auth_response = access_token("bad_refresh_token_to_invoke_web_auth", TDAConfigProvider.get_config().api_key)
print("export TDAMERITRADE_REFRESH_TOKEN=", auth_response['refresh_token'])
