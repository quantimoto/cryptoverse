from .instruments import Instrument
from .object_list import ObjectList


class Pair(object):
    """
    A pair of instruments.
    """

    base = None
    quote = None

    def __init__(self, *args, base=None, quote=None):
        if base is not None:
            self.set_base(base)
        if quote is not None:
            self.set_quote(quote)
        if base is None or quote is None and args:
            if len(args) == 2:
                self.set_base(args[0])
                self.set_quote(args[1])
            elif len(args) == 1 and base is not None:
                self.set_quote(args[0])
            elif len(args) == 1 and quote is not None:
                self.set_base(args[0])
            elif len(args) == 1 and base is None and quote is None:
                base, quote = self._split_string(args[0])
                self.set_base(base)
                self.set_quote(quote)
        if self.base == self.quote:
            raise ValueError("'base' and 'quote' arguments cannot be the same.")

    def set_base(self, value):
        if type(value) is Instrument:
            self.base = value
        else:
            self.base = Instrument(code=value)

    def set_quote(self, value):
        if type(value) is Instrument:
            self.quote = value
        else:
            self.quote = Instrument(code=value)

    def as_str(self):
        return '{}/{}'.format(self.base.code, self.quote.code)

    def as_dict(self):
        dict_obj = dict()
        for key, value in self.__dict__.items():
            if key in ['base', 'quote']:
                if value is not None:
                    dict_obj.update({key: value})
        return dict_obj

    def __repr__(self):
        class_name = self.__class__.__name__
        arguments = list()
        for entry in self.as_dict().items():
            arguments.append('{}={!r}'.format(*entry))
        return '{}({})'.format(class_name, ', '.join(arguments))

    def __eq__(self, other):
        if type(other) is self.__class__:
            if (self.base, self.quote) == (other.base, other.quote):
                return True
            elif (self.base, self.quote) == (other.quote, other.base):
                return True
            else:
                return False

        if type(other) is str and self.is_valid_symbol(other):
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
            raise TypeError("'symbol' must be of type 'str'")

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
    def from_string(cls, symbol, separator=None):
        base, quote = cls._split_string(symbol, separator=separator)
        return cls(base=base, quote=quote)

    @classmethod
    def is_valid_symbol(cls, symbol, separator=None):
        try:
            cls._split_string(symbol=symbol, separator=separator)
            return True
        except ValueError:
            return False


class Pairs(ObjectList):
    def __getattr__(self, item):
        for entry in self:
            if entry == item:
                return entry
