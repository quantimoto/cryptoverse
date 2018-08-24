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
        attributes = list()
        for entry in self.as_dict().items():
            attributes.append('{}={!r}'.format(*entry))
        return '{}({})'.format(class_name, ', '.join(attributes))

    def __eq__(self, other):
        if type(other) is self.__class__ and self.code == other.code:
            return True
        elif type(other) is str and self.code == other:
            return True

        return False

    def __hash__(self):
        return hash((self.code, self.name))

    def as_dict(self):
        dict_obj = dict()
        for key, value in self.__dict__.items():
            if key in ['code', 'name', 'symbol', 'precision']:
                if value is not None:
                    dict_obj.update({key: value})
        return dict_obj

    @classmethod
    def from_dict(cls, data):
        obj = cls(
            code=data['code'] if 'code' in data.keys() else None,
            name=data['name'] if 'name' in data.keys() else None,
            symbol=data['symbol'] if 'symbol' in data.keys() else None,
            precision=data['precision'] if 'precision' in data.keys() else None,
        )
        return obj


class Instruments(ObjectList):

    def __getattr__(self, item):
        for entry in self:
            if entry.code.lower() == item.lower():
                return entry

    def __getitem__(self, item):
        for entry in self:
            if entry.code == item:
                return entry
