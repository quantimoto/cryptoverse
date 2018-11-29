import math

from ..rest import BitfinexREST
from ..scrape import BitfinexScrape
from ...base.interface import ExchangeInterface
from ...utilities import multiply_as_decimals as multiply, subtract_as_decimals as subtract


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
            base = {
                'code': entry['pair'][:3].upper(),
                'precision': 8,
            }
            quote = {
                'code': entry['pair'][3:].upper(),
                'precision': 8,
            }
            pair = {'base': base, 'quote': quote}
            order_limits = {
                'amount': {'min': float(entry['minimum_order_size']),
                           'max': float(entry['maximum_order_size']),
                           'precision': 8},
                'price': {'significant digits': int(entry['price_precision'])},
                'total': {'precision': 8},
            }
            order_fees = {
                'maker': float(fees['Order Execution'][0]['Maker fees'].rstrip('%')),
                'taker': float(fees['Order Execution'][0]['Taker fees'].rstrip('%')),
            }
            offer_limits = {
                'period': {'min': 2.0, 'max': 30.0},
            }
            offer_fees = {
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
                    'limits': offer_limits,
                    'fees': offer_fees,
                }
                funding_market2 = {
                    'context': 'funding',
                    'symbol': quote,
                    'limits': offer_limits,
                    'fees': offer_fees
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
                'side': 'buy',
                'pair': pair,
                'type': 'limit',
            }
            result['bids'].append(order)

        for entry in response['asks']:
            order = {
                'amount': float(entry['amount']),
                'price': float(entry['price']),
                'side': 'sell',
                'pair': pair,
                'type': 'limit',
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
                'side': 'buy',
                'timestamp': float(entry['timestamp']),
            }
            result['bids'].append(offer)

        for entry in response['asks']:
            offer = {
                'amount': float(entry['amount']),
                'annual_rate': float(entry['rate']),
                'period': int(entry['period']),
                'side': 'sell',
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

    def get_account_fees(self, credentials=None):
        result = {
            'orders': dict(),
            'deposits': dict(),
            'withdrawals': dict(),
            'offers': dict(),
        }
        public_fee_information = self.get_fees()

        account_infos = self.rest_client.account_infos(credentials=credentials)
        account_fees = self.rest_client.account_fees(credentials=credentials)

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

    def get_account_wallets(self, credentials=None):
        response = self.rest_client.balances(credentials=credentials)

        result = {
            'spot': list(),
            'margin': list(),
            'funding': list(),
        }
        for entry in response:
            wallet = None
            if entry['type'] == 'exchange':
                wallet = 'spot'
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
                }
                result[wallet].append(balance)

        return result

    def get_account_active_orders(self, credentials=None):
        response = self.rest_client.orders(credentials=credentials)

        result = list()
        for entry in response:
            pair = '{}/{}'.format(entry['symbol'][:3].upper(), entry['symbol'][3:].upper())

            if 'exchange ' in entry['type']:
                context = 'spot'
                type_ = entry['type'].split(' ', 1)[1]
            else:
                context = 'margin'
                type_ = entry['type']

            order = {
                'amount': float(entry['original_amount']),
                'price': float(entry['price']),
                'side': str(entry['side']),
                'id': str(entry['id']),
                'timestamp': float(entry['timestamp']),
                'pair': pair,
                'context': context,
                'type': type_,
                'hidden': entry['is_hidden'],
                'active': entry['is_live'],
                'cancelled': entry['is_cancelled'],
                'metadata': {
                    'avg_execution_price': entry['avg_execution_price'],
                    'cid': entry['cid'],
                    'cid_date': entry['cid_date'],
                    'exchange': entry['exchange'],
                    'executed_amount': entry['executed_amount'],
                    'gid': entry['gid'],
                    'oco_order': entry['oco_order'],
                    'remaining_amount': entry['remaining_amount'],
                    'src': entry['src'],
                    'was_forced': entry['was_forced'],
                }
            }
            result.append(order)

        return result

    def get_account_order_history(self, credentials=None):
        raise NotImplementedError

    def get_account_trades(self, pair, limit=100, begin=None, end=None, credentials=None):
        symbol = '{}{}'.format(*pair.split('/'))
        response = self.rest_client.mytrades(symbol=symbol, limit_trades=limit, timestamp=begin, until=end,
                                             credentials=credentials)

        result = list()
        for entry in response:
            trade = {
                'pair': pair,
                'amount': float(entry['amount']),
                'fees': max(float(entry['fee_amount']), -float(entry['fee_amount'])),
                'fee_instrument': 'USD',
                'order_id': str(entry['order_id']),
                'price': float(entry['price']),
                'id': str(entry['tid']),
                'timestamp': float(entry['timestamp']),
                'side': str(entry['type']).lower(),
            }
            result.append(trade)

        return result

    def get_account_trades_for_order(self, pair, order_id, credentials=None):
        symbol = 't{}{}'.format(*pair.split('/'))
        response = self.rest_client.auth_order_trades(symbol=symbol, order_id=order_id, credentials=credentials)

        trades = list()
        for entry in response:
            trade = {
                'id': str(entry[0]),
                'pair': '{}/{}'.format(entry[1][1:4], entry[1][4:]),
                'timestamp': float(entry[2]) / 1000,
                'order_id': str(entry[3]),
                'amount': float(entry[4]),
                'side': 'buy' if entry[4] > 0 else 'sell',
                'price': float(entry[5]),
                'maker': True if entry[8] == 1 else False,
                'type': 'market' if entry[8] > 0 else 'limit',
                'fee': max(float(entry[9]), -float(entry[9])),
                'fee_instrument': entry[10],
            }

            trades.append(trade)

        if not trades:
            symbol = '{}{}'.format(*pair.split('/'))
            response = self.rest_client.mytrades(symbol=symbol, limit_trades=1000, credentials=credentials)

            for entry in response:
                if str(entry['order_id']) == str(order_id):
                    trade = {
                        'pair': pair,
                        'amount': float(entry['amount']),
                        'fees': max(float(entry['fee_amount']), -float(entry['fee_amount'])),
                        'fee_instrument': 'USD',
                        'order_id': str(entry['order_id']),
                        'price': float(entry['price']),
                        'id': str(entry['tid']),
                        'timestamp': float(entry['timestamp']),
                        'side': str(entry['type']).lower(),
                    }
                    trades.append(trade)

        return trades

    def get_account_positions(self, credentials=None):
        raise NotImplementedError

    def get_account_offers(self, credentials=None):
        response = self.rest_client.offers(credentials=credentials)

        result = list()
        for entry in response:
            offer = {
                'amount': float(entry['original_amount']),
                'instrument': str(entry['currency']),
                'side': 'sell' if entry['direction'] == 'lend' else 'buy',
                'id': str(entry['id']),
                'period': entry['period'],
                'annual_rate': float(entry['rate']),
                'timestamp': float(entry['timestamp']),
                'active': entry['is_live'],
                'cancelled': entry['is_cancelled'],
                'metadata': {
                    'executed_amount': entry['executed_amount'],
                    'remaining_amount': entry['remaining_amount'],
                },
            }
            result.append(offer)
        return result

    def get_account_lends(self, instrument, limit=100, credentials=None):
        symbol = '{}'.format(instrument)
        response = self.rest_client.mytrades_funding(symbol=symbol, limit_trades=limit, credentials=credentials)

        result = list()
        for entry in response:
            lend = {
                'amount': float(entry['amount']),
                'period': float(entry['period']),
                'daily_rate': multiply(float(entry['rate']), 100),
                'timestamp': float(entry['timestamp']),
                'side': str(entry['type']).lower(),
                'id': str(entry['tid']),
                'offer_id': str(entry['offer_id']),
            }
            result.append(lend)

        return result

    def get_account_lends_for_offer(self, instrument, offer_id, credentials=None):
        raise NotImplementedError

    def get_account_deposits(self, *args, credentials=None, **kwargs):
        raise NotImplementedError

    def get_account_withdrawals(self, *args, credentials=None, **kwargs):
        raise NotImplementedError

    def place_single_order(self, pair, amount, price, side, context='spot', type_='limit', hidden=False,
                           post_only=None, credentials=None):
        if context not in ['spot', 'margin']:
            raise ValueError("'context' attribute must be either 'spot' or 'margin', not: {}".format(context))
        if type_ not in ['limit', 'market']:
            raise ValueError("'type_' attritube must be either 'limit' or 'market', not: {}".format(type_))
        if type_ == 'limit' and post_only is None:
            post_only = True

        if context == 'spot':
            context = 'exchange'
        elif context == 'margin':
            context = 'margin'
        elif context == 'funding':
            context = 'funding'
        else:
            context = None

        response = self.rest_client.order_new(
            symbol='{}{}'.format(*pair.split('/')),
            amount=amount,
            price=price,
            side=side,
            type_='{} {}'.format(context, type_),
            exchange='bitfinex',
            is_hidden=hidden,
            is_postonly=post_only,
            credentials=credentials,
        )

        pair = '{}/{}'.format(response['symbol'][:3].upper(), response['symbol'][3:].upper())

        if response['type'] == 'market':
            context = 'margin'
            type_ = 'market'
        elif response['type'] == 'limit':
            context = 'margin'
            type_ = 'limit'
        elif response['type'] == 'stop':
            context = 'margin'
            type_ = 'stop'
        elif response['type'] == 'trailing-stop':
            context = 'margin'
            type_ = 'trailing-stop'
        elif response['type'] == 'fill-or-kill':
            context = 'margin'
            type_ = 'fill-or-kill'
        elif response['type'] == 'exchange market':
            context = 'spot'
            type_ = 'market'
        elif response['type'] == 'exchange limit':
            context = 'spot'
            type_ = 'limit'
        elif response['type'] == 'exchange stop':
            context = 'spot'
            type_ = 'stop'
        elif response['type'] == 'exchange trailing-stop':
            context = 'spot'
            type_ = 'trailing-stop'
        elif response['type'] == 'exchange fill-or-kill':
            context = 'spot'
            type_ = 'fill-or-kill'
        else:
            context = None
            type_ = None

        result = {
            'amount': float(response['original_amount']),
            'price': float(response['price']),
            'side': str(response['side']),
            'id': str(response['id']),
            'timestamp': float(response['timestamp']),
            'pair': pair,
            'context': context,
            'type': type_,
            'hidden': response['is_hidden'],
            'active': response['is_live'],
            'cancelled': response['is_cancelled'],
            'metadata': {
                'avg_execution_price': response['avg_execution_price'],
                'cid': response['cid'],
                'cid_date': response['cid_date'],
                'exchange': response['exchange'],
                'executed_amount': response['executed_amount'],
                'gid': response['gid'],
                'oco_order': response['oco_order'],
                'remaining_amount': response['remaining_amount'],
                'src': response['src'],
                'was_forced': response['was_forced'],
            }
        }

        return result

    def place_multiple_orders(self, orders, credentials=None):
        response = self.get_account_wallets(credentials=credentials)

        available_balances = dict()

        order_list = list()
        for entry in orders:
            if entry['context'] == 'spot':
                context = 'exchange'
            elif entry['context'] == 'margin':
                context = 'margin'
            elif entry['funding'] == 'funding':
                context = 'funding'
            else:
                context = None

            instruments = entry['pair'].split('/')
            input_instrument = instruments[0] if entry['side'] == 'sell' else instruments[1]
            if entry['context'] == 'spot':
                if input_instrument not in available_balances:
                    available_balance = [e['available'] for e in response[entry['context']] if
                                         e['instrument']['code'] == input_instrument]
                    available_balance = float(available_balance[0]) if available_balance else float()
                    available_balances[input_instrument] = available_balance

            if available_balances[input_instrument] and available_balances[input_instrument] > 0:
                order = {  # todo: can we add postonly here?
                    'symbol': '{}{}'.format(*entry['pair'].split('/')),
                    'amount': str(entry['amount']),
                    'price': str(entry['price']),
                    'exchange': 'bitfinex',
                    'side': entry['side'],
                    'type': '{} {}'.format(context, entry['type']),
                }
                remaining = subtract(
                    available_balances[input_instrument],
                    order['amount'] if order['side'] == 'sell' else order['total']
                )
                if remaining > 0:
                    order_list.append(order)
                    available_balances[input_instrument] = subtract(
                        available_balances[input_instrument],
                        order['amount'] if order['side'] == 'sell' else order['total']
                    )

        max_orders = 10
        result = list()
        for i in range(math.ceil(len(order_list) / max_orders)):
            begin = i * max_orders
            end = begin + max_orders
            response = self.rest_client.order_new_multi(order_list[begin:end], credentials=credentials)
            # todo: confirm with bitfinex that you can only post 10 orders at a time

            for entry in response['order_ids']:
                pair = '{}/{}'.format(entry['symbol'][:3].upper(), entry['symbol'][3:].upper())
                if ' ' in entry['type']:
                    context = 'spot'
                    type_ = entry['type'].split(' ')[1]
                else:
                    context = 'margin'
                    type_ = entry['type']

                order = {
                    'id': entry['id'],
                    'hidden': entry['is_hidden'],
                    'active': entry['is_live'],
                    'amount': entry['original_amount'],
                    'price': entry['price'],
                    'side': entry['side'],
                    'pair': pair,
                    'timestamp': entry['timestamp'],
                    'type': type_,
                    'context': context,
                    'cancelled': entry['is_cancelled'],
                    'metadata': {
                        'was_forced': entry['was_forced'],
                        'avg_execution_price': entry['avg_execution_price'],
                        'cid': entry['cid'],
                        'cid_date': entry['cid_date'],
                        'exchange': entry['exchange'],
                        'executed_amount': entry['executed_amount'],
                        'gid': entry['gid'],
                        'oco_order': entry['oco_order'],
                        'remaining_amount': entry['remaining_amount'],
                        'src': entry['src'],
                    }
                }
                result.append(order)

        return result

    def replace_single_order(self, order_id, pair, amount, price, side, context='spot', type_='limit', hidden=False,
                             post_only=None, credentials=None):
        if context not in ['spot', 'margin']:
            raise ValueError("'context' attribute must be either 'spot' or 'margin', not: {}".format(context))
        if type_ not in ['limit', 'market']:
            raise ValueError("'type_' attritube must be either 'limit' or 'market', not: {}".format(type_))
        if type_ == 'limit' and post_only is None:
            post_only = True

        if context == 'spot':
            context = 'exchange'
        elif context == 'margin':
            context = 'margin'
        elif context == 'funding':
            context = 'funding'
        else:
            context = None

        response = self.rest_client.order_cancel_replace(
            order_id=order_id,
            symbol='{}{}'.format(*pair.split('/')),
            amount=amount,
            price=price,
            side=side,
            type_='{} {}'.format(context, type_),
            exchange='bitfinex',
            is_hidden=hidden,
            is_postonly=post_only,
            credentials=credentials,
        )

        pair = '{}/{}'.format(response['symbol'][:3].upper(), response['symbol'][3:].upper())

        if response['type'] == 'market':
            context = 'margin'
            type_ = 'market'
        elif response['type'] == 'limit':
            context = 'margin'
            type_ = 'limit'
        elif response['type'] == 'stop':
            context = 'margin'
            type_ = 'stop'
        elif response['type'] == 'trailing-stop':
            context = 'margin'
            type_ = 'trailing-stop'
        elif response['type'] == 'fill-or-kill':
            context = 'margin'
            type_ = 'fill-or-kill'
        elif response['type'] == 'exchange market':
            context = 'spot'
            type_ = 'market'
        elif response['type'] == 'exchange limit':
            context = 'spot'
            type_ = 'limit'
        elif response['type'] == 'exchange stop':
            context = 'spot'
            type_ = 'stop'
        elif response['type'] == 'exchange trailing-stop':
            context = 'spot'
            type_ = 'trailing-stop'
        elif response['type'] == 'exchange fill-or-kill':
            context = 'spot'
            type_ = 'fill-or-kill'
        else:
            context = None
            type_ = None

        result = {
            'amount': float(response['original_amount']),
            'price': float(response['price']),
            'side': str(response['side']),
            'id': str(response['id']),
            'timestamp': float(response['timestamp']),
            'pair': pair,
            'context': context,
            'type': type_,
            'hidden': response['is_hidden'],
            'active': response['is_live'],
            'cancelled': response['is_cancelled'],
            'metadata': {
                'avg_execution_price': response['avg_execution_price'],
                'cid': response['cid'],
                'cid_date': response['cid_date'],
                'exchange': response['exchange'],
                'executed_amount': response['executed_amount'],
                'gid': response['gid'],
                'oco_order': response['oco_order'],
                'remaining_amount': response['remaining_amount'],
                'src': response['src'],
                'was_forced': response['was_forced'],
            }
        }

        return result

    def replace_multiple_orders(self, *args, credentials=None, **kwargs):
        raise NotImplementedError

    def update_single_order(self, order_id, credentials=None):
        response = self.rest_client.order_status(order_id=int(order_id), credentials=credentials)

        pair = '{}/{}'.format(response['symbol'][:3].upper(), response['symbol'][3:].upper())

        if response['type'] == 'market':
            context = 'margin'
            type_ = 'market'
        elif response['type'] == 'limit':
            context = 'margin'
            type_ = 'limit'
        elif response['type'] == 'stop':
            context = 'margin'
            type_ = 'stop'
        elif response['type'] == 'trailing-stop':
            context = 'margin'
            type_ = 'trailing-stop'
        elif response['type'] == 'fill-or-kill':
            context = 'margin'
            type_ = 'fill-or-kill'
        elif response['type'] == 'exchange market':
            context = 'spot'
            type_ = 'market'
        elif response['type'] == 'exchange limit':
            context = 'spot'
            type_ = 'limit'
        elif response['type'] == 'exchange stop':
            context = 'spot'
            type_ = 'stop'
        elif response['type'] == 'exchange trailing-stop':
            context = 'spot'
            type_ = 'trailing-stop'
        elif response['type'] == 'exchange fill-or-kill':
            context = 'spot'
            type_ = 'fill-or-kill'
        else:
            context = None
            type_ = None

        result = {
            'amount': float(response['original_amount']),
            'price': float(response['price'] or response['avg_execution_price']),
            'side': str(response['side']),
            'id': str(response['id']),
            'timestamp': float(response['timestamp']),
            'pair': pair,
            'context': context,
            'type': type_,
            'hidden': response['is_hidden'],
            'active': response['is_live'],
            'cancelled': response['is_cancelled'],
            'metadata': {
                'price': response['price'],
                'avg_execution_price': response['avg_execution_price'],
                'cid': response['cid'],
                'cid_date': response['cid_date'],
                'exchange': response['exchange'],
                'executed_amount': response['executed_amount'],
                'gid': response['gid'],
                'oco_order': response['oco_order'],
                'remaining_amount': response['remaining_amount'],
                'src': response['src'],
                'was_forced': response['was_forced'],
            }
        }

        return result

    def update_multiple_orders(self, orders, credentials=None):
        active_orders = self.rest_client.orders(credentials=credentials)
        order_history = self.rest_client.orders_hist(limit=100, credentials=credentials)

        result = list()
        for order in orders:
            active_entries_for_id = [entry for entry in active_orders if str(entry['id']) == order['id']]
            try:
                history_entries_for_id = [entry for entry in order_history if str(entry['id']) == order['id']]
            except TypeError as e:
                print(order_history)
                raise TypeError(e)

            entry = None
            if len(active_entries_for_id) == 1:
                entry = active_entries_for_id[0]
            elif len(history_entries_for_id) == 1:
                entry = history_entries_for_id[0]

            if entry:
                pair = '{}/{}'.format(entry['symbol'][:3].upper(), entry['symbol'][3:].upper())
                if ' ' in entry['type']:
                    context = 'spot'
                    type_ = entry['type'].split(' ')[1]
                else:
                    context = 'margin'
                    type_ = entry['type']

                order = {
                    'amount': float(entry['original_amount']),
                    'price': float(entry['price']),
                    'side': str(entry['side']),
                    'id': str(entry['id']),
                    'timestamp': float(entry['timestamp']),
                    'pair': pair,
                    'context': context,
                    'type': type_,
                    'hidden': entry['is_hidden'],
                    'active': entry['is_live'],
                    'cancelled': entry['is_cancelled'],
                    'metadata': {
                        'avg_execution_price': entry['avg_execution_price'],
                        'cid': entry['cid'],
                        'cid_date': entry['cid_date'],
                        'exchange': entry['exchange'],
                        'executed_amount': entry['executed_amount'],
                        'gid': entry['gid'],
                        'oco_order': entry['oco_order'],
                        'remaining_amount': entry['remaining_amount'],
                        'src': entry['src'],
                        'was_forced': entry['was_forced'],
                    }
                }
                result.append(order)
            else:
                order = self.update_single_order(order_id=order['id'], credentials=credentials)
                result.append(order)

        return result

    def cancel_single_order(self, order_id, credentials=None):
        response = self.rest_client.order_cancel(order_id=int(order_id), credentials=credentials)

        pair = '{}/{}'.format(response['symbol'][:3].upper(), response['symbol'][3:].upper())

        if response['type'] == 'market':
            context = 'margin'
            type_ = 'market'
        elif response['type'] == 'limit':
            context = 'margin'
            type_ = 'limit'
        elif response['type'] == 'stop':
            context = 'margin'
            type_ = 'stop'
        elif response['type'] == 'trailing-stop':
            context = 'margin'
            type_ = 'trailing-stop'
        elif response['type'] == 'fill-or-kill':
            context = 'margin'
            type_ = 'fill-or-kill'
        elif response['type'] == 'exchange market':
            context = 'spot'
            type_ = 'market'
        elif response['type'] == 'exchange limit':
            context = 'spot'
            type_ = 'limit'
        elif response['type'] == 'exchange stop':
            context = 'spot'
            type_ = 'stop'
        elif response['type'] == 'exchange trailing-stop':
            context = 'spot'
            type_ = 'trailing-stop'
        elif response['type'] == 'exchange fill-or-kill':
            context = 'spot'
            type_ = 'fill-or-kill'
        else:
            context = None
            type_ = None

        result = {
            'amount': float(response['original_amount']),
            'price': float(response['price']),
            'side': str(response['side']),
            'id': str(response['id']),
            'timestamp': float(response['timestamp']),
            'pair': pair,
            'context': context,
            'type': type_,
            'hidden': response['is_hidden'],
            'active': response['is_live'],
            'cancelled': response['is_cancelled'],
            'metadata': {
                'avg_execution_price': response['avg_execution_price'],
                'cid': response['cid'],
                'cid_date': response['cid_date'],
                'exchange': response['exchange'],
                'executed_amount': response['executed_amount'],
                'gid': response['gid'],
                'oco_order': response['oco_order'],
                'remaining_amount': response['remaining_amount'],
                'src': response['src'],
                'was_forced': response['was_forced'],
            }
        }

        return result

    def cancel_multiple_orders(self, order_ids, credentials=None):
        response = self.rest_client.order_cancel_multi(order_ids=order_ids, credentials=credentials)

        result = list()
        if 'result' in response:
            expected_response = 'All ({}) submitted for cancellation; waiting for confirmation.'.format(len(order_ids))
            if response['result'] == expected_response:
                for order_id in order_ids:
                    order = {
                        'id': order_id,
                        'cancelled': True,
                    }
                    result.append(order)
            elif response['result'] == 'None to cancel':
                pass

        return result

    def cancel_all_orders(self, credentials=None):
        response = self.rest_client.order_cancel_all(credentials=credentials)
        return response

    def place_single_offer(self, instrument, amount, annual_rate, period, side, credentials=None):
        response = self.rest_client.offer_new(
            currency=instrument,
            amount=amount,
            rate=annual_rate,
            period=period,
            direction='lend' if side == 'sell' else 'loan',
            credentials=credentials,
        )

        result = {
            'instrument': response['currency'],
            'side': 'sell' if response['direction'] == 'lend' else 'buy',
            'amount': response['original_amount'],
            'annual_rate': response['rate'],
            'period': response['period'],
            'id': response['id'],
            'active': response['is_live'],
            'timestamp': response['timestamp'],
            'cancelled': response['is_cancelled'],
            'metadata': {
                'offer_id': response['offer_id'],
                'executed_amount': response['executed_amount'],
                'remaining_amount': response['remaining_amount'],
            },
        }

        return result

    def place_multiple_offers(self, offers, credentials=None):
        raise NotImplementedError

    def replace_single_offer(self, *args, credentials=None, **kwargs):
        raise NotImplementedError

    def replace_multiple_offers(self, *args, credentials=None, **kwargs):
        raise NotImplementedError

    def update_single_offer(self, offer_id, credentials=None):
        response = self.rest_client.offer_status(offer_id=int(offer_id), credentials=credentials)

        result = {
            'amount': float(response['original_amount']),
            'instrument': str(response['currency']),
            'side': 'sell' if response['direction'] == 'lend' else 'buy',
            'id': str(response['id']),
            'period': float(response['period']),
            'annual_rate': float(response['rate']),
            'timestamp': float(response['timestamp']),
            'active': response['is_live'],
            'cancelled': response['is_cancelled'],
            'metadata': {
                'executed_amount': response['executed_amount'],
                'remaining_amount': response['remaining_amount'],
            },
        }

        return result

    def update_multiple_offers(self, offer_ids, credentials=None):
        raise NotImplementedError

    def cancel_single_offer(self, offer_id, credentials=None):
        response = self.rest_client.offer_cancel(offer_id=int(offer_id), credentials=credentials)

        result = {
            'amount': float(response['original_amount']),
            'instrument': str(response['currency']),
            'side': 'sell' if response['direction'] == 'lend' else 'buy',
            'id': str(response['id']),
            'period': float(response['period']),
            'annual_rate': float(response['rate']),
            'timestamp': float(response['timestamp']),
            'active': response['is_live'],
            'cancelled': response['is_cancelled'],
            'metadata': {
                'executed_amount': response['executed_amount'],
                'remaining_amount': response['remaining_amount'],
            },
        }

        return result

    def cancel_multiple_offers(self, offer_ids, credentials=None):
        raise NotImplementedError

    def cancel_all_offers(self, credentials=None):
        raise NotImplementedError
