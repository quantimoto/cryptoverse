from ...domain import Order, Offer, Orders, Offers


class ExchangeInterface(object):
    # Methods names in this class should to be very explicit
    rest = None

    def place_single_order(self):
        raise NotImplementedError

    def place_multiple_orders(self):
        raise NotImplementedError

    def update_single_order(self):
        raise NotImplementedError

    def update_multiple_orders(self):
        raise NotImplementedError

    def get_open_orders(self):
        raise NotImplementedError

    def get_instruments(self):
        raise NotImplementedError

    def __str__(self):
        return repr(self)

    def __repr__(self):
        class_name = self.__class__.__name__
        return '{}()'.format(class_name)

    def instruments(self, *args, **kwargs):
        raise NotImplementedError

    def pairs(self, *args, **kwargs):
        raise NotImplementedError

    def markets(self, *args, **kwargs):
        raise NotImplementedError

    def fees(self, *args, **kwargs):
        raise NotImplementedError

    def ticker(self, *args, **kwargs):
        raise NotImplementedError

    def orders(self, *args, **kwargs):
        raise NotImplementedError

    def offers(self, *args, **kwargs):
        raise NotImplementedError

    def trades(self, *args, **kwargs):
        raise NotImplementedError

    def lends(self, *args, **kwargs):
        raise NotImplementedError

    def place_order(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_order(self, *args, **kwargs):
        raise NotImplementedError

    def replace_order(self, *args, **kwargs):
        raise NotImplementedError

    def update_order(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_all_orders(self, *args, **kwargs):
        raise NotImplementedError

    def place_offer(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_offer(self, *args, **kwargs):
        raise NotImplementedError

    def replace_offer(self, *args, **kwargs):
        raise NotImplementedError

    def update_offer(self, *args, **kwargs):
        raise NotImplementedError

    def cancel_all_offers(self, *args, **kwargs):
        raise NotImplementedError

    def place(self, obj):
        if type(obj) is Order or type(obj) is Orders:
            self.place_order(obj)
        elif type(obj) is Offer or type(obj) is Offers:
            self.place_offer(obj)
        return obj

    def cancel(self, obj):
        if type(obj) is Order or type(obj) is Orders:
            self.cancel_order(obj)
        elif type(obj) is Offer or type(obj) is Offers:
            self.cancel_offer(obj)
        return obj

    def replace(self, obj):
        if type(obj) is Order or type(obj) is Orders:
            self.replace_order(obj)
        elif type(obj) is Offer or type(obj) is Offers:
            self.replace_offer(obj)
        return obj

    def update(self, obj):
        if type(obj) is Order or type(obj) is Orders:
            self.update_order(obj)
        elif type(obj) is Offer or type(obj) is Offers:
            self.update_offer(obj)
        return obj

    def my_orders(self, *args, **kwargs):
        raise NotImplementedError

    def my_trades(self, *args, **kwargs):
        raise NotImplementedError

    def my_offers(self, *args, **kwargs):
        raise NotImplementedError

    def my_lends(self, *args, **kwargs):
        raise NotImplementedError

    def my_balances(self, *args, **kwargs):
        raise NotImplementedError

    def my_deposits(self, *args, **kwargs):
        raise NotImplementedError

    def my_withdraws(self, *args, **kwargs):
        raise NotImplementedError
