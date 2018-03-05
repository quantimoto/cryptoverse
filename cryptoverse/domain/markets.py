from .object_list import ObjectList


class Market(object):
    context = None  # 'Spot', 'Margin', 'Funding'
    pair = None
    exchange = None
    order_mininum = {
        'amount': None,
        'price': None,
        'total': None,
    }
    order_maximum = {
        'amount': None,
        'price': None,
        'total': None,
    }
    fees = {
        'maker': None,
        'taker': None,
    }


class Markets(ObjectList):
    pass
