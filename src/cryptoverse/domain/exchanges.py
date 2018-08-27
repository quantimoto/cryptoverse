from memoized_property import memoized_property

from .object_list import ObjectList


class Exchange(object):
    # High level exchange access. Simple friendly methods with smart responses
    interface = None

    def __init__(self, interface=None):
        self.set_interface(interface)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        class_name = self.__class__.__name__
        kwarg_strings = list()
        for kw in []:
            kwarg_strings.append('{0}={1!r}'.format(kw, self.__dict__[kw]))
        return '{}({})'.format(class_name, ', '.join(kwarg_strings))

    def __eq__(self, other):
        if type(other) is self.__class__:
            if self.interface == other.interface:
                return True
        return False

    def __hash__(self):
        return hash(self.interface)

    def set_interface(self, value=None):
        if value is not None:
            self.interface = value

    def copy(self):
        interface = self.interface.copy()
        obj = self.__class__(interface=interface)
        return obj

    @property
    def rest_client(self):
        if self.interface:
            return self.interface.rest_client

    @property
    def scrape_client(self):
        if self.interface:
            return self.interface.scrape_client

    @memoized_property
    def fees(self):
        return self.interface.get_fees()

    @memoized_property
    def instruments(self):
        return self.interface.get_all_instruments()

    @memoized_property
    def pairs(self):
        return self.interface.get_all_pairs()

    @memoized_property
    def markets(self):
        return self.interface.get_all_markets()

    @memoized_property
    def spot_markets(self):
        return self.interface.get_spot_markets()

    @memoized_property
    def margin_markets(self):
        return self.interface.get_margin_markets()

    @memoized_property
    def funding_markets(self):
        return self.interface.get_funding_markets()


class Exchanges(ObjectList):

    def __getattr__(self, item):
        for exchange in self:
            if str(exchange.interface.slug).lower() == str(item).lower():
                return exchange
        raise AttributeError("'{}' object has no attribute: '{}'".format(self.__class__.__name__, item))

    def __getitem__(self, item):
        for exchange in self:
            if str(exchange.interface.slug).lower() == str(item).lower():
                return exchange
        raise KeyError("'{}' object has no item: '{}'".format(self.__class__.__name__, item))

    @property
    def slugs(self):
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
