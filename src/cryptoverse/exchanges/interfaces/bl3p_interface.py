from ...exceptions import ExchangeFunctionalityNotAvailableException
from ..rest import Bl3pREST
from ...base.interface import ExchangeInterface
from ...utilities import multiply_as_decimals as multiply, divide_as_decimals as divide


class Bl3pInterface(ExchangeInterface):
    slug = 'bl3p'

    def __init__(self):
        self.rest_client = Bl3pREST()

    def get_spot_instruments(self):
        response = self.get_spot_markets()
        result = list()
        for entry in response:
            if entry['symbol']['base'] not in result:
                result.append(entry['symbol']['base'])
            if entry['symbol']['quote'] not in result:
                result.append(entry['symbol']['quote'])

        return result

    def get_margin_instruments(self):
        response = self.get_margin_markets()
        result = list()
        for entry in response:
            if entry['symbol']['base'] not in result:
                result.append(entry['symbol']['base'])
            if entry['symbol']['quote'] not in result:
                result.append(entry['symbol']['quote'])

        return result

    def get_funding_instruments(self):
        response = self.get_funding_markets()
        result = list()
        for entry in response:
            if entry['symbol'] not in result:
                result.append(entry['symbol'])

        return result

    def get_all_instruments(self):
        response = self.get_all_markets()
        result = list()
        for entry in response['spot']:
            if entry['symbol']['base'] not in result:
                result.append(entry['symbol']['base'])
            if entry['symbol']['quote'] not in result:
                result.append(entry['symbol']['quote'])
        for entry in response['margin']:
            if entry['symbol']['base'] not in result:
                result.append(entry['symbol']['base'])
            if entry['symbol']['quote'] not in result:
                result.append(entry['symbol']['quote'])
        for entry in response['funding']:
            if entry['symbol'] not in result:
                result.append(entry['symbol'])

        return result

    def get_spot_pairs(self):
        response = self.get_spot_markets()
        result = list()
        for entry in response:
            result.append(entry['symbol'])
        return result

    def get_margin_pairs(self):
        response = self.get_margin_markets()
        result = list()
        for entry in response:
            result.append(entry['symbol'])
        return result

    def get_all_pairs(self):
        response = self.get_all_markets()
        result = list()
        for entry in response['spot']:
            result.append(entry['symbol'])
        for entry in response['margin']:
            if entry['symbol'] not in result:
                result.append(entry['symbol'])
        return result

    def get_spot_markets(self):
        return self.get_all_markets()['spot']

    def get_margin_markets(self):
        return self.get_all_markets()['margin']

    def get_funding_markets(self):
        return self.get_all_markets()['funding']

    def get_all_markets(self):
        markets = {
            'spot': list(),
            'margin': list(),
            'funding': list(),
        }

        for base_code in ['BTC', 'LTC']:
            base = {
                'code': base_code,
                'precision': 8,
            }
            quote = {
                'code': 'EUR',
                'precision': 5,  # todo: figure out real precision
            }
            pair = {'base': base, 'quote': quote}
            spot_market = {
                'context': 'spot',
                'symbol': pair,
            }
            markets['spot'].append(spot_market)

        return markets

    def get_fees(self):  # todo: implement method for order fee calculation, since bl3p has 2 fee-parts
        result = {
            'orders': dict(),
            'deposits': dict(),
            'withdrawals': dict(),
            'offers': dict(),
        }

        result['orders']['BTC/EUR'] = {
            'maker': 0.0025,
            'taker': 0.0025,
        }
        result['orders']['LTC/EUR'] = {
            'maker': 0.0025,
            'taker': 0.0025,
        }

        result['deposits']['BTC'] = 0.0003
        result['deposits']['LTC'] = 0.0
        result['withdrawals']['EUR'] = 0.5

        result['withdrawals']['BTC'] = 0.0003
        result['withdrawals']['LTC'] = 0.001
        result['withdrawals']['EUR'] = 1.0

        return result

    def get_ticker(self, symbol):
        if type(symbol) is str and '/' in symbol:
            response = self.get_spot_pairs()
            allowed_symbols = ['{}/{}'.format(e['base']['code'], e['quote']['code']) for e in response]
            if symbol in allowed_symbols:
                exchange_symbol = '{}{}'.format(*symbol.split('/'))
            else:
                raise ValueError("Supplied market '{}' is not in available markets: {}".format(symbol, allowed_symbols))
        else:
            exchange_symbol = None

        if exchange_symbol is not None:
            response = self.rest_client.ticker(market=exchange_symbol)

            market = {
                'base': {'code': symbol.split('/')[0]},
                'quote': {'code': symbol.split('/')[1]},
            }
            result = {
                'market': market,
                'bid': float(response['bid']),
                'ask': float(response['ask']),
                'last': float(response['last']),
                'high': float(response['high']),
                'low': float(response['low']),
                'volume': float(response['volume']['24h']),
                'timestamp': float(response['timestamp']),
            }
            return result

    def get_tickers(self, *symbols):
        symbols_list = list()
        if len(symbols) == 1 and type(symbols[0]) is list:
            for symbol in symbols[0]:
                if '/' in symbol:
                    symbols_list.append(symbol)
        elif len(symbols) == 1 and type(symbols[0]) is str and symbols[0].lower() == 'all':
            response = self.get_spot_pairs()
            symbols_list = ['{}/{}'.format(e['base']['code'], e['quote']['code']) for e in response]
        elif symbols:
            symbols_list = list()
            for symbol in symbols:
                if '/' in symbol:
                    symbols_list.append(symbol)

        result = list()
        for symbol in symbols_list:
            response = self.get_ticker(symbol)
            result.append(response)

        return result

    def get_all_tickers(self):
        return self.get_tickers('all')

    def get_market_orders(self, pair, limit=100):
        exchange_symbol = '{}{}'.format(*pair.split('/'))
        response = self.rest_client.orderbook(
            market=exchange_symbol,
        )

        result = {
            'bids': list(),
            'asks': list(),
        }

        for entry in response['data']['bids']:
            order = {
                'amount': divide(entry['amount_int'], 1e8),
                'price': divide(entry['price_int'], 1e5),
                'side': 'buy',
                'pair': pair,
                'type': 'limit',
            }
            result['bids'].append(order)
        if limit is not None and len(result) > limit:
            result['bids'] = result['bids'][:limit]

        for entry in response['data']['asks']:
            order = {
                'amount': divide(entry['amount_int'], 1e8),
                'price': divide(entry['price_int'], 1e5),
                'side': 'sell',
                'pair': pair,
                'type': 'limit',
            }
            result['asks'].append(order)
        if limit is not None and len(result) > limit:
            result['asks'] = result['asks'][:limit]

        return result

    def get_market_trades(self, pair, limit=100):
        exchange_symbol = '{}{}'.format(*pair.split('/'))
        response = self.rest_client.trades(
            market=exchange_symbol,
        )

        result = list()
        for entry in response['data']['trades']:
            trade = {
                'amount': divide(entry['amount_int'], 1e8),
                'price': divide(entry['price_int'], 1e5),
                'side': None,
                'id': str(entry['trade_id']),
                'timestamp': float(entry['date']),
            }
            result.append(trade)
        if limit is not None and len(result) > limit:
            result = result[:limit]

        return result

    def get_market_offers(self, instrument, limit=100):
        raise ExchangeFunctionalityNotAvailableException

    def get_market_lends(self, instrument, limit=100):
        raise ExchangeFunctionalityNotAvailableException

    def get_market_candles(self, pair, period, limit=100):
        raise ExchangeFunctionalityNotAvailableException

    def get_account_fees(self, credentials=None):
        result = {
            'orders': dict(),
            'deposits': dict(),
            'withdrawals': dict(),
            'offers': dict(),
        }
        public_fee_information = self.get_fees()

        account_info = self.rest_client.info(credentials=credentials)

        for pair_str, v in public_fee_information['orders'].items():
            result['orders'][pair_str] = {
                'maker': multiply(account_info['data']['trade_fee'], 0.01),
                'taker': multiply(account_info['data']['trade_fee'], 0.01),
            }

        result['deposits'] = public_fee_information['deposits']
        result['withdrawals'] = public_fee_information['withdrawals']
        result['offers'] = public_fee_information['offers']

        return result

    def get_account_wallets(self, credentials=None):
        response = self.rest_client.info(credentials=credentials)

        result = {
            'spot': list(),
            'margin': list(),
            'funding': list(),
        }
        for entry in response['data']['wallets'].values():
            wallet = 'spot'
            instrument = {'code': entry['balance']['currency']}
            amount = float(entry['balance']['value'])
            available = float(entry['available']['value'])
            if amount > 0:
                balance = {
                    'instrument': instrument,
                    'amount': amount,
                    'available': available,
                }
                result[wallet].append(balance)

        return result

    def get_account_active_orders(self, credentials=None):
        spot_pairs = self.get_spot_pairs()

        result = list()
        for spot_pair in spot_pairs:
            exchange_symbol = '{}{}'.format(spot_pair['base']['code'], spot_pair['quote']['code'])
            response = self.rest_client.orders(
                market=exchange_symbol,
                credentials=credentials
            )
            for entry in response['data']['orders']:
                order = {
                    'amount': float(entry['amount']['value']),
                    'price': float(entry['price']['value']),
                    'side': 'sell' if entry['type'] == 'ask' else 'buy',
                    'id': str(entry['order_id']),
                    'timestamp': float(entry['date']),
                    'pair': spot_pair,
                    'context': 'spot',
                    'type': 'limit',
                    'hidden': False,
                    'active': entry['status'] == 'open',
                    'cancelled': False,
                    'metadata': {
                        'amount_executed': entry['amount_executed'],
                        'currency': entry['currency'],
                        'item': entry['item'],
                        'label': entry['label'],
                    },
                }
                result.append(order)

        return result

    def get_account_order_history(self, credentials=None):
        raise NotImplementedError  # todo: implement

    def get_account_trades(self, pair, limit=100, begin=None, end=None, credentials=None):
        raise NotImplementedError  # todo: implement

    def get_account_trades_for_order(self, order_id, pair, credentials=None):
        raise NotImplementedError  # todo: implement

    def get_account_positions(self, credentials=None):
        raise NotImplementedError  # todo: implement

    def get_account_offers(self, credentials=None):
        raise NotImplementedError  # todo: implement

    def get_account_lends(self, instrument, limit=100, credentials=None):
        raise NotImplementedError  # todo: implement

    def get_account_lends_for_offer(self, instrument, offer_id, credentials=None):
        raise NotImplementedError  # todo: implement

    def get_account_deposits(self, *args, credentials=None, **kwargs):
        raise NotImplementedError  # todo: implement

    def get_account_withdrawals(self, *args, credentials=None, **kwargs):
        raise NotImplementedError  # todo: implement

    def place_single_order(self, pair, amount, price, side, context='spot', type_='limit', hidden=False,
                           post_only=None, credentials=None):
        raise NotImplementedError  # todo: implement

    def place_multiple_orders(self, orders, credentials=None):
        raise NotImplementedError  # todo: implement

    def replace_single_order(self, order_id, pair, amount, price, side, context='spot', type_='limit', hidden=False,
                             post_only=None, credentials=None):
        raise NotImplementedError  # todo: implement

    def replace_multiple_orders(self, *args, credentials=None, **kwargs):
        raise NotImplementedError  # todo: implement

    def update_single_order(self, order_id, credentials=None):
        raise NotImplementedError  # todo: implement

    def update_multiple_orders(self, orders, credentials=None):
        raise NotImplementedError  # todo: implement

    def cancel_single_order(self, order_id, credentials=None):
        raise NotImplementedError  # todo: implement

    def cancel_multiple_orders(self, order_ids, credentials=None):
        raise NotImplementedError  # todo: implement

    def cancel_all_orders(self, credentials=None):
        raise NotImplementedError  # todo: implement

    def place_single_offer(self, instrument, amount, annual_rate, duration, side, credentials=None):
        raise ExchangeFunctionalityNotAvailableException

    def place_multiple_offers(self, offers, credentials=None):
        raise ExchangeFunctionalityNotAvailableException

    def replace_single_offer(self, *args, credentials=None, **kwargs):
        raise ExchangeFunctionalityNotAvailableException

    def replace_multiple_offers(self, *args, credentials=None, **kwargs):
        raise ExchangeFunctionalityNotAvailableException

    def update_single_offer(self, offer_id, credentials=None):
        raise ExchangeFunctionalityNotAvailableException

    def update_multiple_offers(self, offer_ids, credentials=None):
        raise ExchangeFunctionalityNotAvailableException

    def cancel_single_offer(self, offer_id, credentials=None):
        raise ExchangeFunctionalityNotAvailableException

    def cancel_multiple_offers(self, offer_ids, credentials=None):
        raise ExchangeFunctionalityNotAvailableException

    def cancel_all_offers(self, credentials=None):
        raise ExchangeFunctionalityNotAvailableException
