import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode

from api_keys import API_KEY, SECRET_KEY

api_key = API_KEY
secret_key = SECRET_KEY

# -----------------------------------------------------------------------------------------------------

def get_all_trading_pairs():
    url = 'https://api.binance.com/api/v3/exchangeInfo'
    response = requests.get(url)
    data = response.json()
    return data['symbols']

def get_trade_history(symbol):
    print(symbol)
    sym = symbol.replace("/", "%2F")
    timestamp = int(time.time() * 1000)
    query_string = f"symbol={symbol}&timestamp={timestamp}"
    signature = hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    url = f"https://api.binance.com/api/v3/myTrades?{query_string}&signature={signature}"
    headers = {'X-MBX-APIKEY': API_KEY}
    response = requests.get(url, headers=headers)
    trades = response.json()
    return trades

def get_symbols_on_stable():
    data = []
    all_trading_pairs = get_all_trading_pairs()
    for pair in all_trading_pairs:
        symbol = pair['symbol']
        if symbol[-4:] == "USDT":
            data.append(symbol)
    return data

def get_token_balance():
    data = []
    url = 'https://api.binance.com/api/v3/account'
    params = {'timestamp': int(time.time() * 1000)}
    params['signature'] = hmac.new(secret_key.encode('utf-8'), urlencode(params).encode('utf-8'), hashlib.sha256).hexdigest()
    headers = {'X-MBX-APIKEY': api_key}
    response = requests.get(url, params=params, headers=headers)
    account_info = response.json()

    for balance in account_info['balances']:
        if float(balance['free']) > 0:
            data.append(balance)
    return data

# -----------------------------------------------------------------------------------------------------

coins_on_stable = get_symbols_on_stable()
token_on_wallet = get_token_balance()

symbols = []

for coin in coins_on_stable:
    for token in token_on_wallet:
        if coin[:4] == token['asset']:
            symbols.append(coin)

for symbol in symbols:
    my_trades = get_trade_history(symbol)

    total_buy_quantity = 0
    total_buy_cost = 0

    for trade in my_trades:
        if trade['isBuyer']:
            total_buy_quantity += float(trade['qty'])
            total_buy_cost += float(trade['quoteQty']) - float(trade['commission'])

        if not trade['isBuyer']:
            total_buy_quantity -= float(trade['qty'])
            total_buy_cost -= float(trade['quoteQty']) - float(trade['commission'])

        if total_buy_quantity == 0:
            total_buy_cost = 0
            average_buy_price = 0

        else:
            average_buy_price = total_buy_cost / total_buy_quantity
    # -----------------------------------------------------------------------------------------------------

    print(f'Средняя цена покупки: {average_buy_price}')
    print(f'Количество: {total_buy_quantity}')


