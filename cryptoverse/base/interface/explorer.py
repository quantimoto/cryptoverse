
class ExchangePublicInterface(object):

    def __init__(self):
        pass

    def instruments(self):
        raise NotImplementedError

    def pairs(self):
        raise NotImplementedError

    def markets(self):
        raise NotImplementedError

    def fees(self):
        raise NotImplementedError

    def orderbook(self):
        raise NotImplementedError

    def fundingbook(self):
        raise NotImplementedError

    def trades(self):
        raise NotImplementedError

    def lends(self):
        raise NotImplementedError


class ExchangeAuthenticatedInterface(object):

    def place(self):
        raise NotImplementedError

    def cancel(self):
        raise NotImplementedError

    def replace(self):
        raise NotImplementedError

    def status(self):
        raise NotImplementedError

    def place_order(self):
        raise NotImplementedError

    def cancel_order(self):
        raise NotImplementedError

    def replace_order(self):
        raise NotImplementedError

    def order_status(self):
        raise NotImplementedError

    def cancel_all_orders(self):
        raise NotImplementedError

    def place_orders(self):
        raise NotImplementedError

    def cancel_orders(self):
        raise NotImplementedError

    def replace_orders(self):
        raise NotImplementedError

    def orders(self):
        raise NotImplementedError

    def update_orders(self):
        raise NotImplementedError

    def balances(self):
        raise NotImplementedError

    def deposits(self):
        raise NotImplementedError
    
    def withdraws(self):
        raise NotImplementedError
