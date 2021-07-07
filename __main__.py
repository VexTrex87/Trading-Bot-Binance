PAIR = 'USDT'

import os
from dotenv import load_dotenv
from binance.client import Client
from datetime import datetime
import json

load_dotenv('.env')
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

client = Client(api_key=API_KEY, api_secret=API_SECRET, tld='us')
client.API_URL = 'https://testnet.binance.vision/api'

def get_price(symbol):
    try:
        price = client.get_avg_price(symbol=symbol + PAIR)
        price = round(float(price['price']), 2)
        return price
    except:
        return None

def get_balance(symbol=None):
    balance = {}
    for asset in client.get_account()['balances']:
        if float(asset['free']) == 0:
            continue

        balance[asset['asset']] = float(asset['free'])
    return not symbol and balance or balance.get(symbol)

def buy_shares(symbol, shares=None):
    try:
        if shares:
            try:
                shares = float(shares)
            except ValueError:
                print('Could not convert shares to float')
                return None

            if shares <= 0:
                print('Shares must be greater than 0')
                return None

        price = get_price(symbol)
        if not price:
            print('Could not find crypto')
            return None

        order_shares = shares or get_balance()[PAIR] / price

        order = client.create_order(
            symbol=symbol+PAIR,
            side='BUY',
            type='LIMIT',
            timeInForce='GTC',
            quantity=order_shares,
            price=price,
        )

        return order
    except:
        return None

def sell_shares(symbol, shares=None):
    try:
        if shares:
            try:
                shares = float(shares)
            except ValueError:
                print('Could not convert shares to integer')
                return None

            if shares <= 0:
                print('Shares must be greater than 0')
                return None

        price = get_price(symbol)
        if not price:
            print('Could not find crypto')
            return None

        order_shares = shares or get_balance()[symbol]

        order = client.create_order(
            symbol=symbol+PAIR,
            side='SELL',
            type='LIMIT',
            timeInForce='GTC',
            quantity=order_shares,
            price=price,
        )

        return order
    except:
        return None

def __main__():
    while True:
        input_text = input('$ ')
        arguments = input_text.split(' ')
        if arguments[0] == 'bal':
            if len(arguments) > 1:
                shares = get_balance(arguments[1])
                if not shares:
                    print('Crypto Not Owned')
                    continue

                print(shares)
            else:
                for symbol, shares in get_balance().items():
                    print(symbol, shares)
        elif arguments[0] == 'price':
            if len(arguments) < 2:
                print('Missing argument: symbol')
                continue

            price = get_price(arguments[1])
            if not price:
                print('Invalid symbol')
                continue

            print(f'${price}')
        elif arguments[0] == 'buy':
            shares = None
            if len(arguments) > 2:
                shares = arguments[2]

            order = buy_shares(arguments[1], shares)
            if not order:
                continue

            shares = float(order['origQty']) - float(order['executedQty'])
            symbol = arguments[1]
            price = float(order['price'])
            profit = shares * price

            print(f'Buying {shares} shares of {symbol} at ${price} (-${profit})...')
        elif arguments[0] == 'sell':
            shares = None
            if len(arguments) > 2:
                shares = arguments[2]

            order = sell_shares(arguments[1], shares)
            if not order:
                continue

            shares = float(order['origQty']) - float(order['executedQty'])
            symbol = arguments[1]
            price = float(order['price'])
            profit = shares * price

            print(f'Selling {shares} shares of {symbol} at ${price} (+${profit})...')
        elif arguments[0] == 'orders':
            if len(arguments) < 2:
                print('Missing argument: symbol')
                continue

            for order in client.get_all_orders(symbol=arguments[1] + PAIR, limit=10):
                time = datetime.fromtimestamp(order['time'] / 1000)
                time = time.strftime('%m/%d/%y %I:%M:%U %p')

                print(json.dumps({
                    'time': time,
                    'side': order['side'],
                    'status': order['status'],
                    'origQty': order['origQty'],
                    'executedQty': order['executedQty'],
                    'price': order['price'],
                }, indent=4))
        elif arguments[0] == 'help':
            print('help     Shows this menu')
            print('bal      Shows the user\'s balance')
            print('price    Shows the price of a symbol')
            print('buy      Buys shares of a crypto')
            print('sell     Sells shares of a crypto')
            print('orders   Shows existing orders')
            print('exit     Exits the program')
        elif arguments[0] == 'exit':
            return
        else:
            print('Invalid Command')

if __name__ == '__main__':
    __main__()
