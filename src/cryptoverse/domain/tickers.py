from .object_list import ObjectList


class Ticker(object):
    bid = None
    ask = None
    high = None
    low = None
    last = None
    volume = None
    timestamp = None

    def __init__(self, bid, ask, high, low, last, volume, timestamp):
        self.bid = bid
        self.ask = ask
        self.high = high
        self.low = low
        self.last = last
        self.volume = volume
        self.timestamp = timestamp


class Tickers(ObjectList):
    pass
