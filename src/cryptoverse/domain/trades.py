from .object_list import ObjectList
from ..utilities import side_colored, multiply_as_decimals as multiply, subtract_as_decimals as subtract, \
    divide_as_decimals as divide, add_as_decimals as add


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

    def __init__(self, **kwargs):
        self.update_arguments(kwargs)

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

    def update_arguments(self, kwargs):
        if 'amount' in kwargs:
            self.amount = kwargs['amount']
        if 'price' in kwargs:
            self.price = kwargs['price']
        if 'side' in kwargs:
            self.side = kwargs['side']
        if 'id' in kwargs:
            self.id = kwargs['id']
        if 'fees' in kwargs:
            self.fees = kwargs['fees']
        if 'fee_instrument' in kwargs:
            from cryptoverse.domain import Instrument
            self.fee_instrument = Instrument(kwargs['fee_instrument'])
        if 'timestamp' in kwargs:
            self.timestamp = kwargs['timestamp']
        if 'account' in kwargs:
            self.account = kwargs['account']
        if 'exchange' in kwargs:
            self.exchange = kwargs['exchange']
        if 'pair' in kwargs:
            from cryptoverse.domain import Pair
            self.pair = Pair(kwargs['pair'])
        if 'order_id' in kwargs:
            self.order_id = kwargs['order_id']

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(**dict_obj)

    @property
    def total(self):
        return multiply(self.amount, self.price)

    @property
    def input(self):
        if self.side == 'buy' and self.fee_instrument == self.pair.base:
            return self.total
        elif self.side == 'sell' and self.fee_instrument == self.pair.quote:
            return self.amount
        elif self.side == 'buy' and self.fee_instrument == self.pair.quote:
            return add(self.total, self.fees)
        elif self.side == 'sell' and self.fee_instrument == self.pair.base:
            return add(self.amount, self.fees)

    @property
    def gross(self):
        if self.side == 'buy':
            return self.amount
        elif self.side == 'sell':
            return self.total

    @property
    def net(self):
        # If the fee instrument is not the same as the instrument we receive, then the fee is added to the input
        # instead of subtracted from the output
        if self.side == 'buy' and self.fee_instrument == self.pair.base or \
                self.side == 'sell' and self.fee_instrument == self.pair.quote:
            return subtract(self.gross, self.fees)
        elif self.side == 'buy' and self.fee_instrument == self.pair.quote or \
                self.side == 'sell' and self.fee_instrument == self.pair.base:
            return self.gross

    @property
    def output(self):
        return self.net

    @property
    def fee_percentage(self):
        return multiply(divide(self.fees, self.gross), 100)


class Trades(ObjectList):
    pass
