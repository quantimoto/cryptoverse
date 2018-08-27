from .object_list import ObjectList


class Balance(object):
    amount = None
    instrument = None
    exchange = None

    def valued_in(self, instrument):
        raise NotImplemented


class Balances(ObjectList):

    def get_by_instrument(self, *args):
        raise NotImplemented

    def weights(self):
        raise NotImplemented
