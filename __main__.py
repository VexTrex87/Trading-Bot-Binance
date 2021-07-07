PAIR = 'USDT'

import os
from dotenv import load_dotenv
from binance.client import Client
import binance

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

def sell_all_shares(symbol):
    try:
        price = get_price(symbol)
        if not price:
            return None

        order_shares = get_balance()[symbol]
        if float(order_shares) == 0:
            return None

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
                print('Missing argument symbol')
                continue

            price = get_price(arguments[1])
            if not price:
                print('Invalid symbol')
                continue

            print(f'${price}')
        elif arguments[0] == 'sell':
            order = sell_all_shares(arguments[1])
            if not order:
                print('Could not execute trade')
                continue

            shares = order['origQty'] - order['executedQty']
            symbol = arguments[1]
            price = order[price]
            profit = shares * price

            print(f'Sold {shares} shares of {symbol} at ${price} (+${profit})')
        elif arguments[0] == 'help':
            print('help     Shows this menu')
            print('bal      Shows the user\'s balance')
            print('price    Shows the price of a symbol')
            print('sell     Sells all shares of a crypto')
            print('exit     Exits the program')
        elif arguments[0] == 'exit':
            return
        else:
            print('Invalid Command')

if __name__ == '__main__':
    __main__()
