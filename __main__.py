UPDATE_DELAY = 60
BOT_INTERVAL = '1m'
DEFAULT_CURRENCY = 'USDT'

import time
import shlex
import os
import math
import Binance

class Terminal():
    def __init__(self):
        self.original_balance = Binance.get_account_worth()
        print(f'Balance: ${self.original_balance}')

    def help(self):
        print('help     Shows this menu')
        print('bal      Shows the user\'s balance')
        print('worth    Shows the user\'s account worth')
        print('price    Shows the price of a symbol')
        print('signal   Shows a recommendation to trade the crypto')
        print('orders   Shows existing orders')
        print('status   Shows session profit')
        print('buy      Buys shares of a crypto')
        print('sell     Sells shares of a crypto')
        print('cancel   Cancels an existing order')
        print('reset    Resets session')
        print('start    Starts the automatic trading bot')
        print('cls      Clears the terminal')
        print('exit     Exits the program')

    def get_account_balance(self, symbol=None):
        try:
            balance = Binance.get_account_balance()
            if symbol:
                shares = balance.get(symbol)
                if shares:
                    print(f'{symbol}: {shares}')
                else:
                    print(f'ERROR: You do not own {symbol}')
            else:
                for symbol, shares in balance.items():
                    print(f'{symbol}: {shares}')
        except Exception as error_message:
            print(f'ERROR: Could not retrieve balance')
            print(error_message)

    def get_account_worth(self):
        try:
            account_worth = Binance.get_account_worth()
            print(f'Account Worth: ${account_worth}')
        except Exception as error_message:
            print(f'ERROR: Could not retrieve account worth')
            print(error_message)

    def get_price(self, symbol=None):
        if not symbol:
            print('ERROR: Missing argument symbol')
            return

        try:
            price = Binance.get_price(symbol)
            if price:
                print(f'{symbol}: ${price}')
            else:
                print(f'ERROR: Could not retrieve price of {symbol}')
        except Exception as error_message:
            print(f'ERROR: Could not retrieve price of {symbol}')
            print(error_message)

    def get_indicator(self, symbol=None, interval=None, indicator=None):
        if not symbol:
            print('ERROR: Missing argument symbol')
            return
        elif not interval:
            print('ERROR: Missing argument interval')
            return

        try:
            indicators = Binance.get_indicator(symbol, interval)
            print(indicator and indicators[indicator] or indicators)
        except Exception as error_message:
            print(f'ERROR: Could not retrieve analysis of {symbol}')
            print(error_message)

    def get_session(self):
        new_balance = Binance.get_account_worth()
        profit = round(new_balance - self.original_balance, 2)
        profit_percent = round(profit / self.original_balance * 100, 2)
        print(f'${profit} ({profit_percent}%)')
 
    def get_orders(self, symbol= None):
        if not symbol:
            print('ERROR: Missing argument symbol')
            return

        try:
            for order in Binance.get_orders(symbol):
                print(order)
        except Exception as error_message:
            print('ERROR: Could not retrieve orders')
            print(error_message)

    def buy_shares(self, symbol=None, shares=None, price=None):
        if not symbol:
            print('Missing argument symbol')
            return
        elif not shares:
            print('Missing argument shares')
            return
        elif not price:
            print('Missing argument price')
            return

        try:
            shares = float(shares)
        except ValueError:
            raise Exception('Could not convert shares to float')

        try:
            price = float(price)
        except ValueError:
            raise Exception('Could not convert price to float')

        try:
            order = Binance.buy_shares(symbol, shares, price)
            if order:
                processed_shares = float(order['executedQty'])
                profit = shares * price
                print(f'Buying {processed_shares}/{shares} shares of {symbol} at ${price} (-${profit})...')
        except Exception as error_message:
            print(f'ERROR: Could not process order')
            print(error_message)

    def sell_shares(self, symbol=None, shares=None, price=None):
        if not symbol:
            print('Missing argument symbol')
            return
        elif not shares:
            print('Missing argument shares')
            return
        elif not price:
            print('Missing argument price')
            return

        try:
            shares = float(shares)
        except ValueError:
            raise Exception('Could not convert shares to float')

        try:
            price = float(price)
        except ValueError:
            raise Exception('Could not convert price to float')

        try:
            order = Binance.sell_shares(symbol, shares, price)
            if order:
                processed_shares = float(order['executedQty'])
                profit = shares * price
                print(f'Selling {processed_shares}/{shares} shares of {symbol} at ${price} (+${profit})...')
        except Exception as error_message:
            print(f'ERROR: Could not process order')
            print(error_message)

    def cancel_order(self, symbol=None, order_id=None):
        if not symbol:
            print('ERROR: Missing argument symbol')
            return
        elif not order_id:
            print('ERROR: Missing argument order_id')
            return

        try:
            Binance.cancel_order(symbol, order_id)
        except Exception as error_message:
            print('ERROR: Could not cancel order')
            print(error_message)

    def reset_session(self):
        self.original_balance = Binance.get_account_worth()
        print(f'Balance: ${self.original_balance}')

    def start_bot(self, symbol=None):
        if not symbol:
            print('ERROR: Missing argument symbol')
            return

        print('Starting bot...')
        while True:
            macd = Binance.get_indicator(symbol, BOT_INTERVAL, 'MACD')
            price = Binance.get_price(symbol)
            balance = Binance.get_account_balance()
            shares_to_buy = math.floor(balance[DEFAULT_CURRENCY] / price)

            if macd >= 0:         
                self.buy_shares(symbol, shares_to_buy, price)
            elif macd < 0:
                self.sell_shares(symbol, shares_to_buy, price)
            time.sleep(UPDATE_DELAY) 

    def cls(self):
        os.system('cls')

def __main__():
    terminal = Terminal()
    while True:
        input_text = input('$ ')
        arguments = shlex.split(input_text, posix=True)
        
        if arguments[0] == 'help':
            terminal.help()
        elif arguments[0] == 'bal':
            terminal.get_account_balance(*arguments[1:])
        elif arguments[0] == 'worth':
            terminal.get_account_worth()
        elif arguments[0] == 'price':
            terminal.get_price(*arguments[1:])
        elif arguments[0] == 'signal':
            terminal.get_indicator(*arguments[1:])
        elif arguments[0] == 'orders':
            terminal.get_orders(*arguments[1:])
        elif arguments[0] == 'status':
            terminal.get_session()
        elif arguments[0] == 'buy':
            terminal.buy_shares(*arguments[1:])
        elif arguments[0] == 'sell':
            terminal.sell_shares(*arguments[1:])
        elif arguments[0] == 'cancel':
            terminal.cancel_order(*arguments[1:])
        elif arguments[0] == 'reset':
            terminal.reset_session()
        elif arguments[0] == 'start':
            terminal.start_bot(*arguments[1:])
        elif arguments[0] == 'cls':
            terminal.cls()
        elif arguments[0] == 'exit':
            return
        else:
            print('Invalid Command')

if __name__ == '__main__':
    __main__()
