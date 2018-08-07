from ..rest import BitfinexREST
from ..scrape import BitfinexScrape
from ...base.interface import ExchangeInterface
from ...domain import Instrument, Instruments, Market, Markets, Orders, Trades, Offers, Lends


class BitfinexInterface(ExchangeInterface):
    slug = 'bitfinex'

    def __init__(self):
        self.rest_client = BitfinexREST()
        self.scrape_client = BitfinexScrape()

    def get_spot_instruments(self):
        results = Instruments()
        return results

    def get_spot_markets(self):
        symbol_details = self.rest_client.symbol_details().json()
        fees = self.scrape_client.fees()
        results = Markets()
        for entry in symbol_details:
            base = Instrument(code=entry['pair'][:3].upper())
            quote = Instrument(code=entry['pair'][3:].upper())
            exchange = None
            price_precision = entry['price_precision']
            order_minimum = {
                'amount': entry['minimum_order_size'],
            }
            order_maximum = {
                'amount': entry['maximum_order_size'],
            }
            order_execution_fees = {
                'maker': fees['order execution']['maker'],
                'taker': fees['order execution']['taker'],
            }
            if entry['margin'] is False:
                market = Market(
                    context='spot',
                    base=base,
                    quote=quote,
                    exchange=exchange,
                    price_precision=price_precision,
                    order_minimum=order_minimum,
                    order_maximum=order_maximum,
                    fees=order_execution_fees,
                )
                results.append(market)
        return results

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
