from .object_list import ObjectList


class Lend(object):
    amount = None
    daily_rate = None
    period = None
    exchange_id = None
    timestamp = None
    side = None
    exchange = None
    pair = None

    def __init__(self, amount, daily_rate, period, exchange_id, timestamp, side, exchange, instrument):
        self.amount = amount
        self.daily_rate = daily_rate
        self.period = period
        self.exchange_id = exchange_id
        self.timestamp = timestamp
        self.side = side
        self.exchange = exchange
        self.instrument = instrument


class Lends(ObjectList):
    pass
