from cryptoverse.utilities import side_colored
from .object_list import ObjectList


class Lend(object):
    amount = None
    daily_rate = None
    annual_rate = None
    duration = None
    id = None
    timestamp = None
    side = None
    account = None
    exchange = None
    pair = None
    offer_id = None

    def __init__(self, **kwargs):
        self.update_arguments(kwargs)

    def __repr__(self):
        class_name = self.__class__.__name__
        attrs = list()
        for kw in ['amount', 'daily_rate', 'duration', 'side', 'instrument']:
            arg = self.__dict__[kw]
            if kw == 'side':
                attrs.append(side_colored('{}={!r}'.format(kw, arg), arg))
            else:
                attrs.append('{}={!r}'.format(kw, arg))

        return '{}({})'.format(class_name, ', '.join(attrs))

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(**dict_obj)

    def update_arguments(self, kwargs):
        if 'amount' in kwargs:
            self.amount = kwargs['amount']
        if 'daily_rate' in kwargs:
            self.daily_rate = kwargs['daily_rate']
        if 'annual_rate' in kwargs:
            self.annual_rate = kwargs['annual_rate']
        if 'duration' in kwargs:
            self.duration = kwargs['duration']
        if 'id' in kwargs:
            self.id = kwargs['id']
        if 'timestamp' in kwargs:
            self.timestamp = kwargs['timestamp']
        if 'side' in kwargs:
            self.side = kwargs['side']
        if 'account' in kwargs:
            self.account = kwargs['account']
        if 'exchange' in kwargs:
            self.exchange = kwargs['exchange']
        if 'pair' in kwargs:
            self.pair = kwargs['pair']
        if 'offer_id' in kwargs:
            self.offer_id = kwargs['offer_id']


class Lends(ObjectList):
    pass
