from .instruments import Instrument, Instruments
from .object_list import ObjectList


class Pair(object):
    """
    A pair of instruments.
    """

    _base = None
    _quote = None

    def __init__(self, *args, base=None, quote=None):
        if base is not None:
            self.base = base
        if quote is not None:
            self.quote = quote
        if base is None or quote is None and args:
            from .markets import Market
            if len(args) == 2 and base is None and quote is None:
                self.base = args[0]
                self.quote = args[1]
            elif len(args) == 1 and base is not None and quote is None:
                self.quote = args[0]
            elif len(args) == 1 and base is None and quote is not None:
                self.base = args[0]
            elif len(args) == 1 and base is None and quote is None and type(args[0]) is str:
                base, quote = self._split_string(args[0])
                self.base = base
                self.quote = quote
            elif len(args) == 1 and base is None and quote is None and type(args[0]) is dict:
                self.base = args[0]['base']
                self.quote = args[0]['quote']
            elif len(args) == 1 and base is None and quote is None and type(args[0]) is Market and \
                    args[0].pair is not None:
                self.base = args[0].symbol.base
                self.quote = args[0].symbol.quote
            elif len(args) == 1 and base is None and quote is None and type(args[0]) is Pair:
                self.base = args[0].base
                self.quote = args[0].quote
            else:
                raise ValueError("Invalid values supplied: {}".format((*args, base, quote)))
        if self.base == self.quote:
            raise ValueError("'base' and 'quote' arguments cannot be the same: {}, {}".format(self.base, self.quote))

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, value):
        if type(value) is Instrument:
            self._base = value
        elif type(value) is dict and 'code' in value:
            self._base = Instrument.from_dict(value)
        elif type(value) is str:
            self._base = Instrument.from_str(value)

    @property
    def quote(self):
        return self._quote

    @quote.setter
    def quote(self, value):
        if type(value) is Instrument:
            self._quote = value
        elif type(value) is dict and 'code' in value:
            self._quote = Instrument.from_dict(value)
        elif type(value) is str:
            self._quote = Instrument.from_str(value)

    @property
    def instruments(self):
        return Instruments([self.base, self.quote])

    def as_str(self):
        return '{}/{}'.format(self.base.code, self.quote.code)

    def as_dict(self):
        dict_obj = dict()
        for key in ['base', 'quote']:
            value = getattr(self, key)
            if value is not None:
                dict_obj.update({key: value})
        return dict_obj

    def __repr__(self):
        class_name = self.__class__.__name__
        return '{}({!r})'.format(class_name, self.as_str())

    def __eq__(self, other):
        if type(other) is self.__class__:
            if (self.base, self.quote) == (other.base, other.quote):
                return True
            elif (self.base, self.quote) == (other.quote, other.base):
                return True
            else:
                return False

        if type(other) is str and self.is_valid_str(other):
            instrument1, instrument2 = self._split_string(other)
            if (self.base, self.quote) == (instrument1, instrument2):
                return True
            elif (self.base, self.quote) == (instrument2, instrument1):
                return True
            else:
                return False
        else:
            return False

    def __hash__(self):
        return hash((self.base, self.quote))

    @staticmethod
    def _split_string(symbol, separator=None):
        if type(symbol) is not str:
            raise TypeError("'symbol' must be of type 'str', not {}. Supplied: {}".format(type(symbol), symbol))

        if separator is None:
            separators = ['/', '_', '-']
        else:
            separators = [separator]

        elements = None
        for separator in separators:
            if separator in symbol:
                elements = symbol.split(separator)
                continue

        if elements is None:
            raise ValueError("No valid separator could be found in the supplied 'symbol': %s" % symbol)

        if len(elements) > 2:
            raise ValueError('A pair cannot have more than 2 instruments.')
        elif len(elements) == 1:
            raise ValueError('A pair cannot have only 1 instrument.')

        instrument1 = elements[0]
        instrument2 = elements[1]
        return instrument1, instrument2

    @classmethod
    def from_str(cls, symbol, separator=None):
        base, quote = cls._split_string(symbol, separator=separator)
        return cls(base=base, quote=quote)

    @classmethod
    def is_valid_str(cls, symbol, separator=None):
        if type(symbol) is str:
            try:
                cls._split_string(symbol=symbol, separator=separator)
                return True
            except ValueError:
                return False
        return False

    @classmethod
    def is_valid_dict(cls, kwargs):
        if type(kwargs) is dict:
            if 'base' in kwargs and 'quote' in kwargs:
                return True
        return False

    @classmethod
    def from_dict(cls, kwargs):
        return cls(**kwargs)

    def get_side(self, input_instrument=None, output_instrument=None):
        if input_instrument is not None and output_instrument is not None and input_instrument == output_instrument:
            raise ValueError(
                "'input_instrument' and 'output_instrument' cannot be equal: {}, {}".format(input_instrument,
                                                                                            output_instrument))
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

    def get_input_instrument(self, side):
        if side == 'buy':
            return self.quote
        elif side == 'sell':
            return self.base

    def get_output_instrument(self, side):
        if side == 'buy':
            return self.base
        elif side == 'sell':
            return self.quote


class Pairs(ObjectList):

    def __getattr__(self, item):
        for entry in self:
            if entry == item:
                return entry

    def with_instruments(self, *instruments):
        result = self.__class__()
        for entry in self:
            candidate = entry
            for instrument in instruments:
                if instrument not in entry.instruments:
                    candidate = None
                    break
            if candidate:
                result.append(candidate)
        return result
