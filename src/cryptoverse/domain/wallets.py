from .object_list import ObjectList


class ExchangeWallet(object):
    account = None
    label = None
    balances = None

    def __init__(self, account, label, balances):
        self.account = account
        self.label = label
        self.balances = balances

    def __repr__(self):
        kwargs = 'label={}'.format(self.label)
        return '{}({}):\n{}'.format(self.__class__.__name__, kwargs, self.balances)

    @property
    def instruments(self):
        return self.balances.instruments

    def markets(self, quote_instrument):
        return self.balances.markets(quote_instrument=quote_instrument)

    def values_in(self, quote_instrument, tickers=None):
        if tickers is None:
            markets = self.account.exchange.markets(quote_instrument=quote_instrument)
            tickers = self.account.exchange.tickers(markets)

        return self.balances.values_in(quote_instrument=quote_instrument, tickers=tickers)

    def value_in(self, quote_instrument, tickers=None):
        if tickers is None:
            markets = self.account.exchange.markets(quote_instrument=quote_instrument)
            tickers = self.account.exchange.tickers(markets)

        return self.balances.value_in(quote_instrument=quote_instrument, tickers=tickers)


class Wallet(object):
    seed = None
    public_master_key = None
    instrument = None

    def __init__(self, instrument=None, public_master_key=None, seed=None):
        self.instrument = instrument
        self.seed = seed
        self.public_master_key = public_master_key


class Wallets(ObjectList):
    def __getitem__(self, item):
        if type(item) is int:
            return super(self.__class__, self).__getitem__(item)
        else:
            return self.find(label=item).first

    @property
    def balances(self):
        from .balances import Balances
        result = Balances()
        for entry in self:
            result = result + entry.balances
        return result

    @property
    def instruments(self):
        from .instruments import Instruments
        result = Instruments()
        for entry in self:
            result += entry.instruments
        return result.get_unique()

    def markets(self, quote_instrument):
        from .markets import Markets
        result = Markets()
        for entry in self:
            result += entry.markets(quote_instrument=quote_instrument)
        return result.get_unique()

    def values_in(self, quote_instrument, tickers=None):
        if tickers is None:
            markets = self.markets(quote_instrument=quote_instrument)
            from .tickers import Tickers
            tickers = Tickers()
            for exchange in markets.get_unique_values('exchange'):
                exchange_markets = markets.find(exchange=exchange)
                tickers += exchange.tickers(exchange_markets)

        result = dict()
        for entry in self:
            result.update({entry.label: entry.values_in(quote_instrument=quote_instrument, tickers=tickers)})

        return result

    def value_in(self, quote_instrument, tickers=None):
        if tickers is None:
            markets = self.markets(quote_instrument=quote_instrument)
            from .tickers import Tickers
            tickers = Tickers()
            for exchange in markets.get_unique_values('exchange'):
                exchange_markets = markets.find(exchange=exchange)
                tickers += exchange.tickers(exchange_markets)

        values = self.values_in(quote_instrument=quote_instrument, tickers=tickers)
        return sum([sum(entries.values()) for kw, entries in values.items()])
