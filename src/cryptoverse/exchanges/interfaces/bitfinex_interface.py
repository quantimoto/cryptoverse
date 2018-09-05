from ..rest import BitfinexREST
from ..scrape import BitfinexScrape
from ...base.interface import ExchangeInterface


class BitfinexInterface(ExchangeInterface):
    slug = 'bitfinex'

    def __init__(self):
        self.rest_client = BitfinexREST()
        self.scrape_client = BitfinexScrape()

    def get_spot_instruments(self):
        response = self.get_all_markets()
        result = list()
        for entry in response['spot']:
            if entry['symbol']['base'] not in result:
                result.append(entry['symbol']['base'])
            if entry['symbol']['quote'] not in result:
                result.append(entry['symbol']['quote'])

        return result

    def get_margin_instruments(self):
        response = self.get_all_markets()
        result = list()
        for entry in response['margin']:
            if entry['symbol']['base'] not in result:
                result.append(entry['symbol']['base'])
            if entry['symbol']['quote'] not in result:
                result.append(entry['symbol']['quote'])

        return result

    def get_funding_instruments(self):
        response = self.get_all_markets()
        result = list()
        for entry in response['funding']:
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
        response = self.get_all_markets()
        result = list()
        for entry in response['spot']:
            result.append(entry['symbol'])
        return result

    def get_margin_pairs(self):
        response = self.get_all_markets()
        result = list()
        for entry in response['margin']:
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
        symbols_details = self.rest_client.symbols_details()
        fees = self.scrape_client.fees()

        markets = {
            'spot': list(),
            'margin': list(),
            'funding': list(),
        }

        for entry in symbols_details:
            base = {'code': entry['pair'][:3].upper()}
            quote = {'code': entry['pair'][3:].upper()}
            pair = {'base': base, 'quote': quote}
            order_limits = {
                'amount': {'min': float(entry['minimum_order_size']),
                           'max': float(entry['maximum_order_size'])},
                'price': {'significant digits': float(entry['price_precision'])}}
            order_fees = {
                'maker': float(fees['Order Execution'][0]['Maker fees'].rstrip('%')),
                'taker': float(fees['Order Execution'][0]['Taker fees'].rstrip('%')),
            }
            margin_funding_fees = {
                'normal': float(fees['Margin Funding'][0]['Fee'].split(' ')[0].rstrip('%')),
                'hidden': float(fees['Margin Funding'][1]['Fee'].split(' ')[0].rstrip('%')),
            }
            spot_market = {
                'context': 'spot',
                'symbol': pair,
                'limits': order_limits,
                'fees': order_fees,
            }
            markets['spot'].append(spot_market)
            if entry['margin']:
                margin_market = {
                    'context': 'margin',
                    'symbol': pair,
                    'limits': order_limits,
                    'fees': order_fees,
                }
                markets['margin'].append(margin_market)

                funding_market1 = {
                    'context': 'funding',
                    'symbol': base,
                    'fees': margin_funding_fees,
                }
                funding_market2 = {
                    'context': 'funding',
                    'symbol': quote,
                    'fees': margin_funding_fees
                }
                if funding_market1 not in markets['funding']:
                    markets['funding'].append(funding_market1)
                if funding_market2 not in markets['funding']:
                    markets['funding'].append(funding_market2)

        return markets

    def get_fees(self):
        result = {
            'orders': dict(),
            'deposits': dict(),
            'withdrawals': dict(),
            'offers': dict(),
        }
        response = self.scrape_client.fees()

        for pair in self.get_all_pairs():
            pair_str = '{}/{}'.format(pair['base']['code'], pair['quote']['code'])
            result['orders'][pair_str] = {
                'maker': float(response['Order Execution'][0]['Maker fees'].rstrip('%')),
                'taker': float(response['Order Execution'][0]['Taker fees'].rstrip('%')),
            }

        for instrument_code in [i['code'] for i in self.get_all_instruments()]:
            for entry in response['Deposit']:
                if instrument_code in entry['Small Deposit*']:
                    result['deposits'][instrument_code] = float(entry['Small Deposit*'].split(' ')[0].rstrip('%'))
                    break
            if instrument_code not in result['deposits'].keys():
                result['deposits'][instrument_code] = 0.0

            for entry in response['Withdrawal']:
                if instrument_code in entry['Fee']:
                    result['withdrawals'][instrument_code] = float(entry['Fee'].split(' ')[0].rstrip('%'))
                    break
            if instrument_code not in result['withdrawals'].keys():
                result['withdrawals'][instrument_code] = 0.0

        for instrument_code in [i['code'] for i in self.get_funding_instruments()]:
            result['offers'][instrument_code] = {
                'normal': float(response['Margin Funding'][0]['Fee'].split(' ')[0].rstrip('%')),
                'hidden': float(response['Margin Funding'][1]['Fee'].split(' ')[0].rstrip('%')),
            }

        return result

    def get_ticker(self, symbol):
        if type(symbol) is str and '/' in symbol:
            symbol = '{}{}'.format(*symbol.split('/'))
        else:
            symbol = None
        if symbol is not None:
            response = self.rest_client.pubticker(symbol=symbol)
            result = {
                'ask': float(response['ask']),
                'bid': float(response['bid']),
                'high': float(response['high']),
                'low': float(response['low']),
                'last': float(response['last_price']),
                'volume': float(response['volume']),
                'timestamp': float(response['timestamp']),
            }
            return result

    def get_tickers(self, *symbols):
        if len(symbols) == 1 and type(symbols[0]) is list:
            symbols_list = list()
            for symbol in symbols[0]:
                if '/' in symbol:
                    new_symbol = 't{}{}'.format(*symbol.split('/'))
                else:
                    new_symbol = 'f{}'.format(symbol)
                symbols_list.append(new_symbol)
            symbols_text = ','.join(symbols_list)
        elif len(symbols) == 1 and type(symbols[0]) is str and symbols[0].lower() == 'all':
            symbols_text = 'ALL'
        elif symbols:
            symbols_list = list()
            for symbol in symbols:
                if '/' in symbol:
                    new_symbol = 't{}{}'.format(*symbol.split('/'))
                else:
                    new_symbol = 'f{}'.format(symbol)
                symbols_list.append(new_symbol)
            symbols_text = ','.join(symbols_list)
        else:
            symbols_text = ''

        response = self.rest_client.tickers(symbols=symbols_text)

        result = list()
        for entry in response:
            if entry[0][0] == 't':
                market = {
                    'base': {'code': entry[0][1:4]},
                    'quote': {'code': entry[0][4:7]}
                }
            elif entry[0][0] == 'f':
                market = {'code': entry[0][1:]}
            else:
                market = None

            if market is not None:
                ticker = {
                    'market': market,
                    'bid': float(entry[1]),
                    'ask': float(entry[3]),
                    'high': float(entry[9]),
                    'low': float(entry[10]),
                    'last': float(entry[7]),
                    'volume': float(entry[8]),
                }
                result.append(ticker)

        return result

    def get_all_tickers(self):
        return self.get_tickers('all')

    def get_market_orders(self, pair, limit=100):
        symbol = '{}{}'.format(*pair.split('/'))
        response = self.rest_client.book(
            symbol=symbol,
            limit_bids=limit,
            limit_asks=limit,
            group=0,
        )

        result = {
            'bids': list(),
            'asks': list(),
        }

        for entry in response['bids']:
            order = {
                'amount': float(entry['amount']),
                'price': float(entry['price']),
                'side': 'bid',
            }
            result['bids'].append(order)

        for entry in response['asks']:
            order = {
                'amount': float(entry['amount']),
                'price': float(entry['price']),
                'side': 'ask',
            }
            result['asks'].append(order)

        return result

    def get_market_trades(self, pair, limit=100):
        symbol = '{}{}'.format(*pair.split('/'))
        response = self.rest_client.trades(
            symbol=symbol,
            limit_trades=limit,
        )
        result = list()
        for entry in response:
            trade = {
                'amount': float(entry['amount']),
                'price': float(entry['price']),
                'side': str(entry['type']),
                'id': str(entry['tid']),
                'timestamp': float(entry['timestamp']) * 0.001,
            }
            result.append(trade)

        return result

    def get_market_offers(self, instrument, limit=100):
        response = self.rest_client.lendbook(
            currency=instrument,
            limit_bids=limit,
            limit_asks=limit,
        )

        result = {
            'bids': list(),
            'asks': list(),
        }
        for entry in response['bids']:
            offer = {
                'amount': float(entry['amount']),
                'annual_rate': float(entry['rate']),
                'period': int(entry['period']),
                'side': 'bid',
                'timestamp': float(entry['timestamp']),
            }
            result['bids'].append(offer)

        for entry in response['asks']:
            offer = {
                'amount': float(entry['amount']),
                'annual_rate': float(entry['rate']),
                'period': int(entry['period']),
                'side': 'ask',
                'timestamp': float(entry['timestamp']),
            }
            result['asks'].append(offer)

        return result

    def get_market_lends(self, instrument, limit=100):
        symbol = 'f{}'.format(instrument)
        response = self.rest_client.trades_hist(
            symbol=symbol,
            limit=limit,
        )
        result = list()
        for entry in response:
            lend = {
                'amount': max(float(entry[2]), -float(entry[2])),
                'daily_rate': float(entry[3]) * 100,
                'period': int(entry[4]),
                'id': str(entry[0]),
                'timestamp': float(entry[1]) * 0.001,
                'side': 'sell' if float(entry[2]) > 0.0 else 'buy',
            }
            result.append(lend)
        return result

    def get_market_candles(self, period, pair, limit=100):
        if '/' in pair:
            symbol = 't{}{}'.format(*pair.split('/'))
        else:
            symbol = None

        if symbol is not None:
            response = self.rest_client.candles(
                timeframe=period,
                symbol=symbol,
                section='hist',
                limit=limit,
            )
            result = list()
            for entry in response:
                candle = {
                    'timestamp': float(entry[0]) * 0.001,
                    'open': float(entry[1]),
                    'close': float(entry[2]),
                    'high': float(entry[3]),
                    'low': float(entry[4]),
                    'volume': float(entry[5]),
                }
                result.append(candle)

            return result

    def get_account_fees(self):
        result = {
            'orders': dict(),
            'deposits': dict(),
            'withdrawals': dict(),
            'offers': dict(),
        }
        public_fee_information = self.get_fees()

        account_infos = self.rest_client.account_infos()
        account_fees = self.rest_client.account_fees()

        for pair in self.get_all_pairs():
            pair_str = '{}/{}'.format(pair['base']['code'], pair['quote']['code'])
            for entry in account_infos[0]['fees']:
                if entry['pairs'] == pair['base']['code']:
                    result['orders'][pair_str] = {
                        'maker': float(entry['maker_fees']),
                        'taker': float(entry['taker_fees']),
                    }

        result['deposits'] = public_fee_information['deposits']

        for instrument_code, fee_cost in account_fees['withdraw'].items():
            result['withdrawals'].update({
                instrument_code: float(fee_cost)
            })

        result['offers'] = public_fee_information['offers']

        return result

    def get_account_balances(self):
        response = self.rest_client.balances()

        result = {
            'exchange': list(),
            'margin': list(),
            'funding': list(),
        }
        for entry in response:
            wallet = None
            if entry['type'] == 'exchange':
                wallet = 'exchange'
            elif entry['type'] == 'trading':
                wallet = 'margin'
            elif entry['type'] == 'deposit':
                wallet = 'funding'
            instrument = {'code': entry['currency'].upper()}
            amount = float(entry['amount'])
            available = float(entry['available'])
            if amount != 0.0:
                balance = {
                    'instrument': instrument,
                    'amount': amount,
                    'available': available,
                    'wallet': wallet,
                }
                result[wallet].append(balance)

        return result

    def get_account_orders(self, *args, **kwargs):
        raise NotImplementedError

    def get_account_trades(self, *args, **kwargs):
        raise NotImplementedError

    def get_account_positions(self, *args, **kwargs):
        raise NotImplementedError

    def get_account_offers(self, *args, **kwargs):
        raise NotImplementedError

    def get_account_lends(self, *args, **kwargs):
        raise NotImplementedError

    def get_account_deposits(self, *args, **kwargs):
        raise NotImplementedError

    def get_account_withdrawals(self, *args, **kwargs):
        raise NotImplementedError

    def place_single_order(self, *args, **kwargs):
        raise NotImplementedError

    def place_multiple_orders(self, *args, **kwargs):
        raise NotImplementedError

    def replace_single_order(self, *args, **kwargs):
        raise NotImplementedError

    def replace_multiple_orders(self, *args, **kwargs):
        raise NotImplementedError

    def update_single_order(self, *args, **kwargs):
        raise NotImplementedError

    def update_multiple_orders(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_single_order(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_multiple_orders(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_all_orders(self, *args, **kwargs):
        raise NotImplementedError

    def place_single_offer(self, *args, **kwargs):
        raise NotImplementedError

    def place_multiple_offers(self, *args, **kwargs):
        raise NotImplementedError

    def replace_single_offer(self, *args, **kwargs):
        raise NotImplementedError

    def replace_multiple_offers(self, *args, **kwargs):
        raise NotImplementedError

    def update_single_offer(self, *args, **kwargs):
        raise NotImplementedError

    def update_multiple_offers(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_single_offer(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_multiple_offers(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_all_offers(self, *args, **kwargs):
        raise NotImplementedError
