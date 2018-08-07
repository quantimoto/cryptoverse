from .object_list import ObjectList
from .offers import Offer, Offers
from .orders import Order, Orders


class Account(object):
    interface = None
    credentials = None
    label = None

    def __init__(self, interface=None, credentials=None, label=None):
        self.set_interface(interface)
        self.set_credentials(credentials)
        self.set_label(label)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        class_name = self.__class__.__name__
        attributes = list()
        for key in ['exchange', 'credentials', 'label']:
            value = self.__dict__[key]
            if value is not None:
                attributes.append('{}={!r}'.format(key, value))
        return '{class_name}({attributes})'.format(class_name=class_name, attributes=', '.join(attributes))

    def set_interface(self, interface):
        self.interface = interface

    def get_interface(self):
        return self.interface

    def set_credentials(self, credentials):
        self.credentials = credentials

    def get_credentials(self):
        return self.credentials

    def set_label(self, label):
        self.label = label

    def get_label(self):
        return self.label

    def orders(self):
        raise NotImplementedError

    def trades(self):
        raise NotImplementedError

    def positions(self):
        raise NotImplementedError

    def offers(self):
        raise NotImplementedError

    def lends(self):
        raise NotImplementedError

    def wallets(self):
        raise NotImplementedError

    def balances(self):
        raise NotImplementedError

    def deposits(self):
        raise NotImplementedError

    def withdraws(self):
        raise NotImplementedError

    def create_order(self):
        raise NotImplementedError

    def create_offer(self):
        raise NotImplementedError

    def create_deposit_address(self):
        raise NotImplementedError

    def create_withdraw(self):
        raise NotImplementedError

    def create_transfer(self):
        raise NotImplementedError

    def place(self, obj):
        if type(obj) is Order:
            self.interface.place_single_order(obj)
        elif type(obj) is Orders:
            self.interface.place_multiple_orders(obj)
        elif type(obj) is Offer:
            self.interface.place_single_offer(obj)
        elif type(obj) is Offers:
            self.interface.place_multiple_offers(obj)
        return obj

    def cancel(self, obj):
        if type(obj) is Order:
            self.interface.cancel_single_order(obj)
        elif type(obj) is Orders:
            self.interface.cancel_multiple_orders(obj)
        elif type(obj) is Offer:
            self.interface.cancel_single_offer(obj)
        elif type(obj) is Offers:
            self.interface.cancel_multiple_offers(obj)
        return obj

    def replace(self, obj):
        if type(obj) is Order:
            self.interface.replace_single_order(obj)
        elif type(obj) is Orders:
            self.interface.replace_multiple_orders(obj)
        elif type(obj) is Offer:
            self.interface.replace_single_offer(obj)
        elif type(obj) is Offers:
            self.interface.replace_multiple_offers(obj)
        return obj

    def update(self, obj):
        if type(obj) is Order:
            self.interface.update_single_order(obj)
        elif type(obj) is Orders:
            self.interface.update_multiple_orders(obj)
        elif type(obj) is Offer:
            self.interface.update_single_offer(obj)
        elif type(obj) is Offers:
            self.interface.update_multiple_offers(obj)
        return obj


class Accounts(ObjectList):
    pass
