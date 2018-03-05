from .object_list import ObjectList


class Order(object):
    trades = None

    def place(self):
        raise NotImplementedError

    def cancel(self):
        raise NotImplementedError


class Orders(ObjectList):
    pass

    def trades(self):
        raise NotImplementedError

    def totals(self):
        raise NotImplementedError

    def results(self):
        raise NotImplementedError


class OrderChain(Orders):
    pass
