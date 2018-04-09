from .object_list import ObjectList


class Exchange(object):
    # High level exchange access. Simple friendly methods with smart responses
    interface = None
    rest_client = None

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
        self.rest_client = obj.rest_client

    def set_rest_client(self):
        if self.interface is not None:
            self.rest_client = self.interface.rest_client

    def update_instruments(self):
        instruments = self.interface.get_instruments()
        self.instruments = instruments

    def update_markets(self):
        markets = self.interface.get_markets()
        self.instruments = markets


class Exchanges(ObjectList):

    def __getattr__(self, item):
        for exchange in self:
            if exchange.interface.slug == item:
                return exchange

    def __getitem__(self, item):
        for exchange in self:
            if exchange.interface.slug == item:
                return exchange
