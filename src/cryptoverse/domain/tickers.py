from .object_list import ObjectList


class Ticker(object):
    bid = None
    ask = None
    high = None
    low = None
    last = None
    volume = None
    timestamp = None
    market = None

    def __init__(self, market=market, bid=None, ask=None, high=None, low=None, last=None, volume=None,
                 timestamp=None):
        self.bid = bid
        self.ask = ask
        self.high = high
        self.low = low
        self.last = last
        self.volume = volume
        self.market = market
        self.timestamp = timestamp

    def __repr__(self):
        class_name = self.__class__.__name__
        kwarg_strings = list()
        for kw in self.__dict__:
            kwarg_strings.append('{0}={1!r}'.format(kw, self.__dict__[kw]))
        return '{}({})'.format(class_name, ', '.join(kwarg_strings))

    @property
    def pair(self):
        if hasattr(self.market, 'pair'):
            return self.market.pair
        else:
            return None

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def mid(self):
        return (self.bid + self.ask) / 2

    @property
    def spread(self):
        return self.ask - self.bid


class Tickers(ObjectList):
    pass
