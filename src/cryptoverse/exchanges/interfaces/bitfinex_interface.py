from cryptoverse.domain import Tickers
from ..rest import BitfinexREST
from ..scrape import BitfinexScrape
from ...base.interface import ExchangeInterface
from ...domain import Instrument, Instruments, Market, Markets, Order, Orders, Trades, Offers, Lends, Pair, Pairs, \
    Ticker, Balances, Balance


class BitfinexInterface(ExchangeInterface):
    slug = 'bitfinex'

    def __init__(self):
        self.rest_client = BitfinexREST()
        self.scrape_client = BitfinexScrape()

    def get_spot_instruments(self):
        markets = self.get_spot_markets()
        results = Instruments(markets.get_values('base') + markets.get_values('quote')).get_unique()
        return results

    def get_margin_instruments(self):
        markets = self.get_margin_markets()
        results = Instruments(markets.get_values('base') + markets.get_values('quote')).get_unique()
        return results

    def get_funding_instruments(self):
        instruments = self.get_funding_markets()
        results = Instruments(instruments.get_values('symbol'))
        return results

    def get_all_instruments(self):
        instruments = self.get_spot_instruments() + self.get_margin_instruments() + self.get_funding_instruments()
        return instruments.get_unique()

    def get_spot_pairs(self):
        return Pairs(self.get_spot_markets().get_values('symbol'))

    def get_margin_pairs(self):
        return Pairs(self.get_margin_markets().get_values('symbol'))

    def get_all_pairs(self):
        return Pairs(self.get_spot_pairs() + self.get_margin_pairs()).get_unique()

    def get_spot_markets(self):
        return self.get_all_markets().find(context='spot')

    def get_margin_markets(self):
        return self.get_all_markets().find(context='margin')

    def get_funding_markets(self):
        return self.get_all_markets().find(context='funding')

    def get_all_markets(self):
        from cryptoverse.exchanges import Bitfinex
        symbols_details = self.rest_client.symbols_details()
        fees = self.scrape_client.fees()

        markets = Markets()
        spot_markets = Markets()
        margin_markets = Markets()
        funding_markets = Markets()

        for entry in symbols_details:
            base = Instrument(code=entry['pair'][:3].upper())
            quote = Instrument(code=entry['pair'][3:].upper())
            pair = Pair(base=base, quote=quote)
            exchange = Bitfinex()
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
            spot_market = Market(
                context='spot',
                symbol=pair,
                exchange=exchange,
                limits=order_limits,
                fees=order_fees,
            )
            spot_markets.append(spot_market)
            markets.append(spot_market)
            if entry['margin']:
                margin_market = Market(
                    context='margin',
                    symbol=pair,
                    exchange=exchange,
                    limits=order_limits,
                    fees=order_fees,
                )
                margin_markets.append(margin_market)
                markets.append(margin_market)

                funding_market1 = Market(
                    context='funding',
                    symbol=base,
                    exchange=exchange,
                    fees=margin_funding_fees,
                )
                funding_market2 = Market(
                    context='funding',
                    symbol=quote,
                    exchange=exchange,
                    fees=margin_funding_fees
                )
                if funding_market1 not in funding_markets:
                    funding_markets.append(funding_market1)
                if funding_market2 not in funding_markets:
                    funding_markets.append(funding_market2)
                if funding_market1 not in markets:
                    markets.append(funding_market1)
                if funding_market2 not in markets:
                    markets.append(funding_market2)

        return Markets(spot_markets + margin_markets + funding_markets)

    def get_fees(self):
        result = {
            'orders': dict(),
            'deposits': dict(),
            'withdrawals': dict(),
            'funding': dict(),
        }
        response = self.scrape_client.fees()

        for pair in self.get_all_pairs():
            result['orders'][pair.as_str()] = {
                'maker': float(response['Order Execution'][0]['Maker fees'].rstrip('%')),
                'taker': float(response['Order Execution'][0]['Taker fees'].rstrip('%')),
            }

        for instrument in self.get_all_instruments():
            for entry in response['Deposit']:
                if instrument.code in entry['Small Deposit*']:
                    result['deposits'][instrument.code] = float(entry['Small Deposit*'].split(' ')[0].rstrip('%'))
                    break
            if instrument.code not in result['deposits'].keys():
                result['deposits'][instrument.code] = 0.0

            for entry in response['Withdrawal']:
                if instrument.code in entry['Fee']:
                    result['withdrawals'][instrument.code] = float(entry['Fee'].split(' ')[0].rstrip('%'))
                    break
            if instrument.code not in result['withdrawals'].keys():
                result['withdrawals'][instrument.code] = 0.0

        for instrument in self.get_funding_instruments():
            result['funding'][instrument.code] = {
                'normal': float(response['Margin Funding'][0]['Fee'].split(' ')[0].rstrip('%')),
                'hidden': float(response['Margin Funding'][1]['Fee'].split(' ')[0].rstrip('%')),
            }

        return result

    def get_ticker(self, market):
        if type(market) is Market:
            symbol = '{}{}'.format(market.symbol.base.code.lower(), market.symbol.quote.code.lower())
        elif type(market) is Pair:
            symbol = '{}{}'.format(market.base.code.lower(), market.quote.code.lower())
        elif type(market) is str and Pair.is_valid_symbol(market):
            pair = Pair.from_string(market)
            symbol = '{}{}'.format(pair.base.code.lower(), pair.quote.code.lower())
        else:
            raise ValueError("No valid market supplied: {}".format(market))

        response = self.rest_client.pubticker(symbol=symbol)
        result = Ticker(
            ask=float(response['ask']),
            bid=float(response['bid']),
            high=float(response['high']),
            low=float(response['low']),
            last=float(response['last_price']),
            timestamp=float(response['timestamp']),
            volume=float(response['volume']),
        )
        return result

    def get_tickers(self, markets):
        if type(markets) is Markets:
            markets_symbols = list()
            for market in markets:
                if market.pair is not None:
                    market_str = 't{}{}'.format(market.pair.base.code, market.pair.quote.code)
                elif market.instrument is not None:
                    market_str = 'f{}'.format(market.instrument.code)
                else:
                    market_str = None

                if market_str is not None and market_str not in markets_symbols:
                    markets_symbols.append(market_str)
            markets_text = ','.join(markets_symbols)
        elif type(markets) is str:
            markets_text = markets
        else:
            markets_text = 'ALL'

        response = self.rest_client.tickers(symbols=markets_text)

        result = Tickers()
        for entry in response:
            if entry[0][0] == 't':
                market = self.get_spot_markets()[entry[0][1:4], entry[0][4:7]]
            elif entry[0][0] == 'f':
                market = self.get_funding_markets()[entry[0][1:]]
            else:
                market = None

            if market is not None:
                ticker = Ticker(
                    market=market,
                    bid=float(entry[1]),
                    ask=float(entry[3]),
                    high=float(entry[9]),
                    low=float(entry[10]),
                    last=float(entry[7]),
                    volume=float(entry[8]),
                )
                result.append(ticker)

        return result

    def get_all_tickers(self):
        return self.get_tickers(markets='ALL')

    def get_market_orders(self, market):
        if type(market) is str and Pair.is_valid_symbol(market):
            pair = Pair.from_string(symbol=market)
            market = self.get_spot_markets().get(symbol=pair)
        elif type(market) is Pair:
            pair = market
            market = self.get_spot_markets().get(symbol=pair)
        print(market)
        symbol = '{}{}'.format(market.base.code, market.quote.code)
        book = self.rest_client.book(
            symbol=symbol,
            limit_bids=50,
            limit_asks=50,
            group=0,
        )

        bids, asks = Orders(), Orders()

        for entry in book['bids']:
            order = Order(
                market=market,
                amount=entry['amount'],
                price=entry['price'],
                side='buy',
            )
            bids.append(order)

        for entry in book['asks']:
            order = Order(
                market=market,
                amount=entry['amount'],
                price=entry['price'],
                side='ask',
            )
            asks.append(order)

        return bids, asks

    def get_market_trades(self, market):
        results = Trades()
        return results

    def get_market_offers(self, instrument):
        results = Offers()
        return results

    def get_market_lends(self, instrument):
        results = Lends()
        return results

    def get_market_candles(self, period, market, limit=100):
        response = self.rest_client.candles(
            timeframe=period,
            symbol=market,
            section='hist',
            limit=limit,
        )
        return response

    def get_account_fees(self):
        result = {
            'orders': dict(),
            'deposits': dict(),
            'withdrawals': dict(),
            'funding': dict(),
        }
        public_fee_information = self.get_fees()

        account_infos = self.rest_client.account_infos()
        account_fees = self.rest_client.account_fees()

        for pair in self.get_all_pairs():
            for entry in account_infos[0]['fees']:
                if entry['pairs'] == pair.base:
                    result['orders'][pair.as_str()] = {
                        'maker': float(entry['maker_fees']),
                        'taker': float(entry['taker_fees']),
                    }

        result['deposits'] = public_fee_information['deposits']

        for instrument_code, fee_cost in account_fees['withdraw'].items():
            result['withdrawals'].update({
                instrument_code: float(fee_cost)
            })

        result['funding'] = public_fee_information['funding']

        return result

    def get_account_balances(self):
        response = self.rest_client.balances()
        result = Balances()
        for entry in response:
            amount = float(entry['amount'])
            instrument_code = entry['currency'].upper()
            instrument = self.get_all_instruments()[instrument_code]
            if amount != 0.0:
                balance = Balance(
                    instrument=instrument,
                    amount=amount,
                )
                result.append(balance)
        return result
