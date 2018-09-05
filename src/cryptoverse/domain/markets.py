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
            if entry[0] == 'symbol':
                entry = (entry[0], entry[1].as_str())
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

    def __hash__(self):
        return hash((self.symbol, self.context, self.exchange))

    @classmethod
    def from_dict(cls, kwargs):
        return cls(**kwargs)

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
        from .pairs import Pair
        from .instruments import Instrument
        if symbol is not None:
            if type(symbol) in [Pair, Instrument]:
                self.symbol = symbol
            elif Pair.is_valid_str(symbol):
                pair = Pair.from_str(symbol)
                self.symbol = pair
            elif Pair.is_valid_dict(symbol):
                pair = Pair.from_dict(symbol)
                self.symbol = pair
            elif Instrument.is_valid_str(symbol):
                instrument = Instrument.from_str(symbol)
                self.symbol = instrument
            elif Instrument.is_valid_dict(symbol):
                instrument = Instrument.from_dict(symbol)
                self.symbol = instrument

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

    @property
    def pair(self):
        from .pairs import Pair
        if type(self.symbol) is Pair:
            return self.symbol

    @property
    def instrument(self):
        from cryptoverse.domain import Instrument
        if type(self.symbol) is Instrument:
            return self.symbol

    @property
    def ticker(self):
        if self.exchange:
            return self.exchange.ticker(market=self)

    def get_side(self, input_instrument=None, output_instrument=None):
        if input_instrument is not None:
            if self.base == input_instrument:
                return 'sell'
            elif self.quote == input_instrument:
                return 'buy'
        elif output_instrument is not None:
            if self.base == output_instrument:
                return 'buy'
            elif self.quote == output_instrument:
                return 'sell'

    def get_opposite(self, instrument):
        if self.base == instrument:
            return self.quote
        elif self.quote == instrument:
            return self.base


class Markets(ObjectList):

    def __getattr__(self, item):
        result = self.find(symbol=item)
        if len(result) == 1:
            return result[0]

        return result

    def __getitem__(self, item):
        if type(item) is tuple:
            from .pairs import Pair

            response = self.find(symbol=Pair(*item))
            if len(response) == 1:
                result = response[0]
            else:
                result = response
        elif type(item) is int:
            result = super(self.__class__, self).__getitem__(item)
        else:
            response = self.find(symbol=item)
            if len(response) == 1:
                result = response[0]
            else:
                result = response

        return result

    def with_instrument(self, *instruments):
        result = self.__class__()
        for instrument in instruments:
            result = result + self.find(base=instrument)
            result = result + self.find(quote=instrument)
            result = result + self.find(instrument=instrument)

        return result.get_unique()
