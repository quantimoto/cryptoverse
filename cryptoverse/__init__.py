from .domain import Exchanges
from .exchanges import bitfinex, bl3p, kraken, poloniex

exchanges = Exchanges()
exchanges.append(bitfinex)
exchanges.append(bl3p)
exchanges.append(kraken)
exchanges.append(poloniex)
