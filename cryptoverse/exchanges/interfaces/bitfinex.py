from ..rest import BitfinexREST
from ...base.interface import ExchangeInterface
from ...domain import Instruments, Pairs, Markets


class BitfinexInterface(ExchangeInterface):
    def __init__(self):
        self.rest = BitfinexREST()

    def instruments(self):
        results = Instruments()
        response = self.rest.symbols_details()
        for entry in response:
            print(entry)
        return results

    def pairs(self):
        results = Pairs()
        return results

    def markets(self):
        results = Markets()
        return results

    def orders(self):
        results = Orders()
        return results

    def trades(self):
        results = Trades()
        return results

    def offers(self):
        results = Offers()
        return results

    def lends(self):
        results = Lends()
        return results
