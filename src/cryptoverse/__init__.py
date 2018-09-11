from .domain import Accounts, Exchanges
from .exchanges import Bitfinex, Bl3p, Kraken, Poloniex

exchanges = Exchanges()
accounts = Accounts()


def load_exchanges():
    exchanges.append(Bitfinex())
    exchanges.append(Bl3p())
    exchanges.append(Kraken())
    exchanges.append(Poloniex())


def load_accounts():
    global accounts
    from cryptoverse.domain import Keepassx
    accounts = Accounts.from_keystore(keystore=Keepassx('default'), exchanges=exchanges)


load_exchanges()
