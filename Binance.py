from logging import error
import os
from datetime import datetime
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException
from tradingview_ta import TA_Handler

load_dotenv('.env')
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

client = Client(api_key=API_KEY, api_secret=API_SECRET, tld='us')
client.API_URL = 'https://testnet.binance.vision/api'

def get_price(symbol):
    try:
        price = client.get_avg_price(symbol=symbol)
        price = float(price['price'])
        return price
    except BinanceAPIException as error_message:
        if error_message.message == 'Invalid symbol.':
            return None
        else:
            raise BinanceAPIException(error_message.response, error_message.status_code, error_message.message)

def get_indicator(symbol, interval):
    crypto = TA_Handler(
        symbol=symbol,
        screener='crypto',
        exchange='binance',
        interval=interval,
    )

    analysis = crypto.get_analysis()
    indicators = analysis.indicators
    return indicators

def get_account_balance():
    balance = {}
    for asset in client.get_account()['balances']:
        symbol = asset['asset']
        shares = float(asset['free'])
        if shares != 0:
            balance[symbol] = shares
    return balance
    
def get_account_worth():
    total_balance = 0
    for symbol, shares in get_account_balance().items():
        price = get_price(symbol) or 1
        if price:
            total_balance += price * shares
    return total_balance

def get_orders(symbol):
    orders = client.get_all_orders(symbol=symbol, limit=None)
    formatted_orders = []
    for order in orders:
        time = datetime.fromtimestamp(order['time'] / 1000)
        time = time.strftime('%m/%d/%y %I:%M:%U %p')
        formatted_orders.append({
            'time': time,
            'orderId': order['orderId'],
            'side': order['side'],
            'status': order['status'],
            'origQty': order['origQty'],
            'executedQty': order['executedQty'],
            'price': order['price'],
        })
    return formatted_orders

def buy_shares(symbol, shares, price):
    order = client.create_order(
        symbol=symbol,
        side='BUY',
        type='LIMIT',
        timeInForce='GTC',
        quantity=shares,
        price=price,
    )

    return order

def sell_shares(symbol, shares, price):
    order = client.create_order(
        symbol=symbol,
        side='SELL',
        type='LIMIT',
        timeInForce='GTC',
        quantity=shares,
        price=price,
    )

    return order

def cancel_order(symbol, order_id):
    result = client.cancel_order(symbol=symbol, orderId=order_id)
    if result['status'] == 'CANCELED':
        print(f'Canceled {symbol} {order_id}')
    else:
        print(f'Could not cancel {symbol} {order_id}')
