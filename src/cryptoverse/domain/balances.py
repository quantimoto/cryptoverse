from .object_list import ObjectList


class Balance(object):
    amount = None
    instrument = None
    exchange = None


class Balances(ObjectList):
    pass
