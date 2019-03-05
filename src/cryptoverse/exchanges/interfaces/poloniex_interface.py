import time

from ..rest import PoloniexREST
from ...base.interface import ExchangeInterface
from ...exceptions import ExchangeOrderNotFoundException, ExchangeFunctionalityNotAvailableException, \
    ExchangeInvalidOrderException
from ...utilities import add_as_decimals as add, date_string_to_timestamp
from ...utilities.decorators import Memoize


class PoloniexInterface(ExchangeInterface):
    slug = 'poloniex'

    def __init__(self):
        self.rest_client = PoloniexREST()

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
        tickers = self.rest_client.return_ticker()
        currencies = self.rest_client.return_currencies()

        result = list()

        order_limits = {
            'amount': {'min': 0.000001,
                       'precision': 8},
            'price': {'min': 0.00000001,
                      'precision': 8},
            'total': {'min': 0.0001,
                      'precision': 8}
        }
        order_fees = {
            'maker': 0.001,
            'taker': 0.002,
        }

        for market_symbol, entry in tickers.items():
            base_code = market_symbol.split('_')[1]
            quote_code = market_symbol.split('_')[0]
            base = {
                'name': currencies[base_code]['name'],
                'code': base_code,
                'precision': 8,
            }
            quote = {
                'name': currencies[quote_code]['name'],
                'code': quote_code,
                'precision': 8,
            }
            pair = {'base': base, 'quote': quote}
            spot_market = {
                'context': 'spot',
                'symbol': pair,
                'limits': order_limits,
                'fees': order_fees,
            }
            if spot_market not in result:
                result.append(spot_market)

        return result

    def get_margin_markets(self):
        funding_instruments = self.get_funding_instruments()
        funding_codes = [instrument['code'] for instrument in funding_instruments]
        tickers = self.rest_client.return_ticker()
        currencies = self.rest_client.return_currencies()

        order_limits = {
            'amount': {'min': 0.000001,
                       'precision': 8},
            'price': {'min': 0.00000001,
                      'precision': 8},
            'total': {'min': 0.0001,
                      'precision': 8}
        }
        order_fees = {
            'maker': 0.001,
            'taker': 0.002,
        }

        result = list()
        for market_symbol, entry in tickers.items():
            base_code = market_symbol.split('_')[1]
            quote_code = market_symbol.split('_')[0]
            base = {
                'name': currencies[base_code]['name'],
                'code': base_code,
                'precision': 8,
            }
            quote = {
                'name': currencies[quote_code]['name'],
                'code': quote_code,
                'precision': 8,
            }
            pair = {'base': base, 'quote': quote}
            if base_code in funding_codes and quote_code in funding_codes:
                margin_market = {
                    'context': 'margin',
                    'symbol': pair,
                    'limits': order_limits,
                    'fees': order_fees,
                }
                if margin_market not in result:
                    result.append(margin_market)

        return result

    @Memoize(expires=3600, persistent=True, instance_bound=False)
    # Retrieving available funding markets has to be done by brute-force. It takes a long time.
    def get_funding_markets(self):
        currencies = self.rest_client.return_currencies()

        result = list()

        offer_limits = {
            'duration': {'min': 2, 'max': 60, 'precision': 0},
            'amount': {'min': 0.01, 'precision': 8},
            'rate': {'min': 0.0001, 'max': 5.0, 'precision': 4},
        }
        offer_fees = {
            'normal': 0.15,
        }

        for code, entry in currencies.items():
            loan_orders = self.rest_client.return_loan_orders(currency=code)
            if loan_orders['offers'] or loan_orders['demands']:
                funding_market = {
                    'context': 'funding',
                    'symbol': {
                        'name': entry['name'],
                        'code': code,
                        'precision': 8,
                    },
                    'limits': offer_limits,
                    'fees': offer_fees,
                }
                if funding_market not in result:
                    result.append(funding_market)

        return result

    def get_all_markets(self):
        result = {
            'spot': self.get_spot_markets(),
            'margin': self.get_margin_markets(),
            'funding': self.get_funding_markets(),
        }

        return result

    def get_fees(self):
        currencies = self.rest_client.return_currencies()
        markets = self.get_all_markets()

        result = {
            'orders': dict(),
            'deposits': dict(),
            'withdrawals': dict(),
            'offers': dict(),
        }

        for code, entry in currencies.items():
            result['deposits'][code] = 0.0
            result['withdrawals'][code] = entry['txFee']
        for market in markets['spot']:
            code = '{}/{}'.format(market['symbol']['base']['code'], market['symbol']['quote']['code'])
            result['orders'][code] = market['fees']
        for market in markets['funding']:
            code = market['symbol']['code']
            result['offers'][code] = market['fees']

        return result

    def get_ticker(self, symbol):
        response = self.get_tickers(symbol)

        base_code, quote_code = None, None
        if '/' in symbol:
            base_code = symbol.split('/')[0]
            quote_code = symbol.split('/')[1]

        result = None
        for entry in response:
            if 'base' in entry['market'] and 'quote' in entry['market'] \
                    and entry['market']['base']['code'] == base_code \
                    and entry['market']['quote']['code'] == quote_code:
                result = entry
                break
            elif entry['market']['code'] == symbol:
                result = entry
                break

        return result

    def get_tickers(self, *symbols):
        if len(symbols) == 0:
            return None

        all_symbols = False
        if len(symbols) == 1 and type(symbols[0]) is str and symbols[0] == 'all':
            all_symbols = True

        symbols_list = list()
        for entry in symbols:
            if type(entry) is list or type(entry) is set:
                symbols_list += list(entry)
            elif type(entry) is str:
                symbols_list.append(entry)

        exchange_symbols = list()
        funding_symbols = list()
        for entry in symbols_list:
            if '/' in entry:
                exchange_symbols.append(entry)
            else:
                funding_symbols.append(entry)

        response = self.rest_client.return_ticker()

        result = list()
        for market_symbol, entry in response.items():
            market = {
                'base': {'code': market_symbol.split('_')[1]},
                'quote': {'code': market_symbol.split('_')[0]},
            }

            ticker = {
                'market': market,
                'bid': float(entry['highestBid']),
                'ask': float(entry['lowestAsk']),
                'high': float(entry['high24hr']),
                'low': float(entry['low24hr']),
                'last': float(entry['last']),
                'volume': float(entry['baseVolume']),
            }

            pair = '{}/{}'.format(market['base']['code'], market['quote']['code'])

            if pair in exchange_symbols or all_symbols is True:
                result.append(ticker)

        if all_symbols is True:
            funding_symbols = [entry['code'] for entry in self.get_funding_instruments()]

        for entry in funding_symbols:
            response = self.rest_client.return_loan_orders(currency=entry)
            if 'error' not in response:
                market = {
                    'code': entry
                }

                demands = response['demands']
                offers = response['offers']

                if len(offers) > 0:
                    ask = float(offers[0]['rate'])
                else:
                    ask = None

                if len(demands) > 0:
                    # Because of a bug at poloniex, the demand book is untrustworthy.
                    # https://twitter.com/brutesque/status/1098660728620371969
                    # We need to manually check that demand rates don't exceed offer rates.
                    bid = None
                    for demand in demands:
                        rate = float(demand['rate'])
                        if ask is not None and rate < ask:
                            bid = rate
                            break
                else:
                    bid = None

                ticker = {
                    'market': market,
                    'bid': bid,
                    'ask': ask,
                    'high': None,
                    'low': None,
                    'last': None,
                    'volume': None,
                }

                result.append(ticker)

        return result

    def get_all_tickers(self):
        return self.get_tickers('all')

    def get_market_orders(self, pair, limit=100):
        symbol = '{}_{}'.format(*list(pair.split('/').__reversed__()))
        response = self.rest_client.return_order_book(
            currency_pair=symbol,
            depth=limit,
        )

        result = {
            'bids': list(),
            'asks': list(),
        }

        for entry in response['bids']:
            order = {
                'amount': float(entry[1]),
                'price': float(entry[0]),
                'side': 'buy',
                'pair': pair,
                'type': 'limit',
            }
            result['bids'].append(order)

        for entry in response['asks']:
            order = {
                'amount': float(entry[1]),
                'price': float(entry[0]),
                'side': 'sell',
                'pair': pair,
                'type': 'limit',
            }
            result['asks'].append(order)

        return result

    def get_market_trades(self, pair, limit=100):
        symbol = '{}_{}'.format(*list(pair.split('/').__reversed__()))
        response = self.rest_client.return_trade_history_public(
            currency_pair=symbol,
            limit=limit,
        )

        result = list()
        for entry in response:
            trade = {
                'amount': entry['amount'],
                'price': entry['rate'],
                'side': entry['type'],
                'id': entry['tradeID'],
                'timestamp': entry['date'],
            }
            result.append(trade)

        return result

    def get_market_offers(self, instrument, limit=100):
        response = self.rest_client.return_loan_orders(
            currency=instrument,
            limit=limit,
        )

        result = {
            'bids': list(),
            'asks': list(),
        }

        for entry in response['offers']:
            offer = {
                'amount': float(entry['amount']),
                'daily_rate': float(entry['rate']),
                'duration': float(entry['rangeMin']),
                'side': 'sell',
            }
            result['asks'].append(offer)

        for entry in response['demands']:
            offer = {
                'amount': float(entry['amount']),
                'daily_rate': float(entry['rate']),
                'duration': float(entry['rangeMin']),
                'side': 'buy',
            }

            if offer['daily_rate'] < result['asks'][0]['daily_rate']:
                # Because of a bug at poloniex, the demand book is untrustworthy.
                # https://twitter.com/brutesque/status/1098660728620371969
                # We need to manually check that demand rates don't exceed offer rates.
                result['bids'].append(offer)

        return result

    def get_market_lends(self, instrument, limit=100):
        raise ExchangeFunctionalityNotAvailableException

    def get_market_candles(self, pair, period, limit=100):  # todo: add start and end
        if '/' in pair:
            symbol = '{}_{}'.format(*list(pair.split('/').__reversed__()))
        else:
            symbol = None

        allowed_periods = {
            '5m': 300,
            '15m': 900,
            '30m': 1800,
            '2h': 7200,
            '4h': 14400,
            '1D': 86400,
        }
        if period not in allowed_periods.keys():
            raise ValueError("'period' argument must be one of: {}".format(list(allowed_periods.keys())))

        end = int(time.time())
        start = end - (allowed_periods[period] * limit)

        if symbol is not None:
            response = self.rest_client.return_chart_data(
                currency_pair=symbol,
                period=allowed_periods[period],
                start=start,
                end=end,
            )

            result = list()
            for entry in response:
                candle = {
                    'timestamp': int(entry['date']),
                    'open': float(entry['open']),
                    'close': float(entry['close']),
                    'high': float(entry['high']),
                    'low': float(entry['low']),
                    'volume': float(entry['volume']),
                }
                result.append(candle)

            if len(result) == limit + 1:
                return result[1:]
            return result

    def get_account_fees(self, credentials=None):
        result = {
            'orders': dict(),
            'deposits': dict(),
            'withdrawals': dict(),
            'offers': dict(),
        }
        public_fee_information = self.get_fees()

        account_fee_info = self.rest_client.return_fee_info(credentials=credentials)

        for pair in public_fee_information['orders']:
            result['orders'][pair] = {
                'maker': float(account_fee_info['makerFee']),
                'taker': float(account_fee_info['takerFee']),
            }

        result['deposits'] = public_fee_information['deposits']
        result['withdrawals'] = public_fee_information['withdrawals']
        result['offers'] = public_fee_information['offers']

        return result
