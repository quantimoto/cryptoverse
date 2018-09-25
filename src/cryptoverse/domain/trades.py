from .object_list import ObjectList
from ..utilities import side_colored, multiply_as_decimals as multiply, subtract_as_decimals as subtract, \
    divide_as_decimals as divide


class Trade(object):
    amount = None
    price = None
    side = None
    id = None
    fees = None
    fee_instrument = None
    timestamp = None
    account = None
    exchange = None
    pair = None
    order_id = None

    def __init__(self, amount=None, price=None, side=None, id_=None, fees=None, fee_instrument=None, timestamp=None,
                 account=None, exchange=None, pair=None, order_id=None):
        self.amount = amount
        self.price = price
        self.side = side
        self.id = id_
        self.fees = fees
        self.fee_instrument = fee_instrument
        self.timestamp = timestamp
        self.account = account
        self.exchange = exchange
        self.pair = pair
        self.order_id = order_id

    def __repr__(self):
        class_name = self.__class__.__name__
        attrs = list()
        for kw in ['amount', 'price', 'side', 'pair']:
            arg = self.__dict__[kw]
            if kw == 'side':
                attrs.append(side_colored('{}={!r}'.format(kw, arg), arg))
            else:
                attrs.append('{}={!r}'.format(kw, arg))

        return '{}({})'.format(class_name, ', '.join(attrs))

    def as_dict(self):
        result = {
            'amount': self.amount,
            'price': self.price,
            'side': self.side,
            'id': self.id,
            'timestamp': self.timestamp,
            'exchange': self.exchange,
            'pair': self.pair,
            'order_id': self.order_id,
        }
        return result

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(**dict_obj)

    @property
    def total(self):
        return multiply(self.amount, self.price)

    @property
    def input(self):
        if self.side == 'buy':
            return self.total
        elif self.side == 'sell':
            return self.amount

    @property
    def gross(self):
        if self.side == 'buy':
            return self.amount
        elif self.side == 'sell':
            return self.total

    @property
    def net(self):
        return subtract(self.gross, self.fees)

    @property
    def output(self):
        return self.net

    @property
    def fee_percentage(self):
        return multiply(divide(self.fees, self.gross) * 100)


class Trades(ObjectList):
    pass
