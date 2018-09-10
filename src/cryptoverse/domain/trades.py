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

    def __repr__(self):
        attrs = 'amount={amount}, price={price}, pair={pair}'.format(**self.as_dict())
        return '{}({})'.format(self.__class__.__name__, attrs)

    def as_dict(self):
        result = {
            'amount': self.amount,
            'price': self.price,
            'side': self.side,
            'exchange_id': self.exchange_id,
            'timestamp': self.timestamp,
            'exchange': self.exchange,
            'pair': self.pair,
        }
        return result

    @property
    def total(self):
        from decimal import Decimal
        return float(Decimal(str(self.amount)) * Decimal(str(self.price)))


class Trades(ObjectList):
    pass
