from .object_list import ObjectList


class Exchange(object):
    # High level exchange access. Simple friendly methods with smart responses
    interface = None
    rest_client = None
    scrape_client = None

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

    def __eq__(self, other):
        if type(other) is self.__class__:
            if self.interface == other.interface:
                return True
        return False

    def set_interface(self, interface):
        if interface is not None:
            self.interface = interface
            self.rest_client = interface.rest_client
            self.scrape_client = interface.scrape_client

    def update_instruments(self):
        instruments = self.interface.get_instruments()
        self.instruments = instruments

    def update_markets(self):
        markets = self.interface.get_markets()
        self.instruments = markets


class Exchanges(ObjectList):

    def __getattr__(self, item):
        for exchange in self:
            if exchange.interface.slug.lower() == item.lower():
                return exchange
        raise AttributeError("'{}' object has no attribute: '{}'".format(self.__class__.__name__, item))

    def __getitem__(self, item):
        for exchange in self:
            if exchange.interface.slug.lower() == item.lower():
                return exchange
        raise KeyError("'{}' object has no item: '{}'".format(self.__class__.__name__, item))

    def get_slugs(self):
        result = list()
        for exchange in self:
            result.append(exchange.interface.slug)
        return result

    def as_dict(self):
        result = dict()
        for exchange in self:
            result.update({
                exchange.interface.slug: exchange
            })
        return result
