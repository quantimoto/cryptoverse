from .object_list import ObjectList


class Instrument(object):
    code = None  # Example: 'USD'
    name = None  # Example: 'US Dollar'
    symbol = None  # Example: '$'
    precision = None  # Example: 2

    def __init__(self, code, name=None, symbol=None, precision=None):
        self.code = code
        self.name = name
        self.symbol = symbol
        self.precision = precision

    def __repr__(self):
        class_name = self.__class__.__name__
        return '{}({!r})'.format(class_name, self.code)

    def __eq__(self, other):
        if type(other) is self.__class__ and self.code == other.code:
            return True
        elif type(other) is str and self.code == other:
            return True

        return False

    def __hash__(self):
        return hash((self.code, self.name))

    def __ge__(self, other):
        return self.as_str().__ge__(other.as_str())

    def __gt__(self, other):
        return self.as_str().__gt__(other.as_str())

    def __le__(self, other):
        return self.as_str().__le__(other.as_str())

    def __lt__(self, other):
        return self.as_str().__lt__(other.as_str())

    def as_str(self):
        return self.code

    def as_dict(self):
        dict_obj = dict()
        for key, value in self.__dict__.items():
            if key in ['code', 'name', 'symbol', 'precision']:
                if value is not None:
                    dict_obj.update({key: value})
        return dict_obj

    @staticmethod
    def is_valid_dict(kwargs):
        if 'code' in kwargs:
            return True
        return False

    @staticmethod
    def is_valid_str(arg):
        if type(arg) is str:
            return True
        return False

    @classmethod
    def from_dict(cls, kwargs):
        return cls(**kwargs)

    @classmethod
    def from_str(cls, arg):
        return cls(code=arg)


class Instruments(ObjectList):

    def __getattr__(self, item):
        for entry in self:
            if entry.code.lower() == item.lower():
                return entry

    def __getitem__(self, item):
        if type(item) is int:
            return super(self.__class__, self).__getitem__(item)
        else:
            for entry in self:
                if entry.code == item:
                    return entry
