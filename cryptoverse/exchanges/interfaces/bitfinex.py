from ..rest import BitfinexREST
from ...base.interface import ExchangeInterface
from ...domain import Instruments, Markets, Orders, Trades, Offers, Lends


class BitfinexInterface(ExchangeInterface):
    slug = 'bitfinex'

    def __init__(self):
        self.rest_client = BitfinexREST()

    def get_spot_instruments(self):
        results = Instruments()
        return results

    def get_spot_markets(self):
        results = Markets()
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
