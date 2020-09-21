import pyetrade
import os
import requests

def get_tokens():
    consumer_key = os.environ.get("ETRADE_ACCESS_KEY")
    consumer_secret = os.environ.get("ETRADE_SECRET")

    oauth = pyetrade.ETradeOAuth(consumer_key, consumer_secret)
    print(oauth.get_request_token())  # Use the printed URL

    verifier_code = input("Enter verification code: ")
    tokens = oauth.get_access_token(verifier_code)
    print(tokens)

def handler():
    consumer_key = os.environ.get("ETRADE_ACCESS_KEY_PROD")
    consumer_secret = os.environ.get("ETRADE_SECRET_PROD")
    oauth_token = os.environ.get("oauth_token")
    oauth_token_secret = os.environ.get("oauth_token_secret")
    print(oauth_token, oauth_token_secret)

    accounts = pyetrade.ETradeAccounts(
        consumer_key,
        consumer_secret,
        oauth_token,
        oauth_token_secret
    )
    accountsList = accounts.list_accounts()['AccountListResponse']
    for x in accountsList['Accounts']['Account']:
        print(x['accountIdKey'], x['accountMode'], x['accountDesc'], x['accountId'])
    
    account_id_key = '6_Dpy0rmuQ9cu9IbTfvF2A'
    # res = requests.get(f"https://apisb.etrade.com/v1/accounts/{account_id_key}/balance?realTimeNAV=true")

    balance = accounts.get_account_balance(account_id_key=account_id_key, account_type="CASH")['BalanceResponse']

    print(balance)
    # account_id_key='xj1Dc18FTqWPqkEEVUr5rw'
    # balance = accounts.get_account_balance(account_id_key)['BalanceResponse']
    fundsForOpenOrdersCash = balance['Cash']['fundsForOpenOrdersCash']
    print(fundsForOpenOrdersCash)

    return {"fundsForOpenOrdersCash": fundsForOpenOrdersCash}


if __name__ == "__main__":
    get_tokens()
