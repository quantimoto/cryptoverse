from .interfaces import BitfinexInterface, Bl3pInterface, KrakenInterface, PoloniexInterface
from ..domain import Exchange

bitfinex = Exchange(interface=BitfinexInterface())
bl3p = Exchange(interface=Bl3pInterface())
kraken = Exchange(interface=KrakenInterface())
poloniex = Exchange(interface=PoloniexInterface())
