from ..rest import BitfinexREST
from ..scrape import BitfinexScrape
from ...base.interface import ExchangeInterface
from ...domain import Instrument, Instruments, Market, Markets, Orders, Trades, Offers, Lends, Pair, Pairs


class BitfinexInterface(ExchangeInterface):
    slug = 'bitfinex'

    def __init__(self):
        self.rest_client = BitfinexREST()
        self.scrape_client = BitfinexScrape()
        # self._markets = dict()

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
        symbols_details = self.rest_client.symbols_details().json()
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
            order_limits = {'amount': {'min': entry['minimum_order_size'], 'max': entry['maximum_order_size']},
                            'price': {'significant digits': entry['price_precision']}}
            order_fees = fees['order']
            margin_funding_fees = fees['funding']
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
        return self.scrape_client.fees()

    def get_market_orders(self, market):
        results = Orders()
        return results

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
        results = response.json()
        return results
