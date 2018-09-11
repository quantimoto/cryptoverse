from cryptoverse.utilities import side_colored
from .object_list import ObjectList


class Lend(object):
    amount = None
    daily_rate = None
    annual_rate = None
    period = None
    id = None
    timestamp = None
    side = None
    account = None
    exchange = None
    pair = None
    offer_id = None

    def __init__(self, amount=None, daily_rate=None, annual_rate=None, period=None, id_=None, timestamp=None, side=None,
                 account=None, exchange=None, instrument=None, offer_id=None):
        self.amount = amount
        self.daily_rate = daily_rate
        self.annual_rate = annual_rate
        self.period = period
        self.id = id_
        self.timestamp = timestamp
        self.side = side
        self.account = account
        self.exchange = exchange
        self.instrument = instrument
        self.offer_id = offer_id

    def __repr__(self):
        class_name = self.__class__.__name__
        attrs = list()
        for kw in ['amount', 'daily_rate', 'period', 'side', 'instrument']:
            arg = self.__dict__[kw]
            if kw == 'side':
                attrs.append(side_colored('{}={!r}'.format(kw, arg), arg))
            else:
                attrs.append('{}={!r}'.format(kw, arg))

        return '{}({})'.format(class_name, ', '.join(attrs))

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(**dict_obj)


class Lends(ObjectList):
    pass
