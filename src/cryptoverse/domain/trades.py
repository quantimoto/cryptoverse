from .object_list import ObjectList


class Trade(object):
    amount = None
    price = None
    side = None
    exchange_id = None
    timestamp = None
    exchange = None
    pair = None

    def __init__(self, amount, price, side, exchange_id, timestamp, exchange, pair):
        self.amount = amount
        self.price = price
        self.side = side
        self.exchange_id = exchange_id
        self.timestamp = timestamp
        self.exchange = exchange
        self.pair = pair


class Trades(ObjectList):
    pass
