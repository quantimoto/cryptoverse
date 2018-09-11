from .object_list import ObjectList
from ..utilities import side_colored


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
        from decimal import Decimal
        return float(Decimal(str(self.amount)) * Decimal(str(self.price)))


class Trades(ObjectList):
    pass
