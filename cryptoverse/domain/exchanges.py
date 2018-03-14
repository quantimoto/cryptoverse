from .object_list import ObjectList


class Exchange(object):
    interface = None

    instruments = None
    pairs = None
    markets = None

    def __init__(self, interface):
        self.set_interface(interface)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        class_name = self.__class__.__name__
        kwarg_strings = list()
        for kw in ['interface']:
            kwarg_strings.append('{0}={1!r}'.format(kw, self.__dict__[kw]))
        return '{}({})'.format(class_name, ', '.join(kwarg_strings))

    def set_interface(self, obj):
        self.interface = obj

    def set_instruments(self):
        instruments = self.interface.get_instruments()
        self.instruments = instruments

    def set_pairs(self):
        pairs = self.interface.get_pairs()
        self.instruments = pairs

    def set_markets(self):
        markets = self.interface.get_markets()
        self.instruments = markets


class Exchanges(ObjectList):
    pass
