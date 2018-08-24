from dict_recursive_update import recursive_update

from cryptoverse.utilities import strip_empty, strip_none
from .object_list import ObjectList


class Market(object):
    symbol = None  # 'Pair() for spot and margin, Instrument() for funding'
    context = None  # 'spot', 'margin', 'funding'
    exchange = None
    limits = None
    fees = None

    def __init__(self, symbol=None, context='spot', exchange=None, limits=None, fees=None):
        self.set_symbol(symbol)
        self.set_context(context)
        self.set_exchange(exchange)
        self.set_limits(limits)
        self.set_fees(fees)

    def __repr__(self):
        class_name = self.__class__.__name__
        arguments = list()
        for entry in self.as_dict().items():
            arguments.append('{}={!r}'.format(*entry))
        return '{}({})'.format(class_name, ', '.join(arguments))

    def __eq__(self, other):
        if type(other) is self.__class__:
            if (self.symbol, self.context, self.exchange) == (other.symbol, other.context, other.exchange):
                return True
            else:
                return False
        else:
            return False

    def as_dict(self):
        dict_obj = dict()
        for key, value in self.__dict__.items():
            if key in ['symbol', 'context', 'exchange', 'limits', 'fees']:
                value = strip_empty(value)
                value = strip_none(value)
                if value:
                    dict_obj.update({key: value})
        return dict_obj

    def set_symbol(self, symbol):
        from cryptoverse.domain import Pair, Instrument
        if type(symbol) in [Pair, Instrument]:
            self.symbol = symbol
        elif Pair.is_valid_symbol(symbol):
            pair = Pair.from_string(symbol)
            self.symbol = pair

    def set_context(self, context):
        if context in ['spot', 'margin', 'funding']:
            self.context = context
        else:
            raise ValueError("'{:s}' is not a valid option. Choose from ['spot', 'margin', 'funding']".format(context))

    def set_exchange(self, exchange):
        self.exchange = exchange

    def set_limits(self, limits):
        template = {
            'amount': {
                'min': None,
                'max': None,
                'precision': None,
                'significant digits': None,
            },
            'price': {
                'min': None,
                'max': None,
                'precision': None,
                'significant digits': None,
            },
            'total': {
                'min': None,
                'max': None,
                'precision': None,
                'significant digits': None,
            }
        }
        if self.limits is None:
            self.limits = template.copy()
        if type(limits) is dict:
            recursive_update(self.limits, limits)

    def set_fees(self, fees):
        template = {
            'maker': None,
            'taker': None
        }
        if self.fees is None:
            self.fees = template.copy()
        if type(fees) is dict:
            recursive_update(self.fees, fees)

    @property
    def base(self):
        if hasattr(self.symbol, 'base'):
            return self.symbol.base
        else:
            return None

    @property
    def quote(self):
        if hasattr(self.symbol, 'quote'):
            return self.symbol.quote
        else:
            return None


class Markets(ObjectList):

    def __getattr__(self, item):
        return self.get(symbol=item)

    def __getitem__(self, item):
        if type(item) is tuple:
            from cryptoverse.domain import Pair
            return self.get(symbol=Pair(*item))
        if type(item) is int:
            return super(self.__class__, self).__getitem__(item)
        else:
            return self.get(symbol=item)
