from .interfaces import BitfinexInterface, Bl3pInterface, KrakenInterface, PoloniexInterface
from ..domain import Exchange


class Bitfinex(Exchange):
    interface = BitfinexInterface()


class Bl3p(Exchange):
    interface = Bl3pInterface()


class Kraken(Exchange):
    interface = KrakenInterface()


class Poloniex(Exchange):
    interface = PoloniexInterface()
