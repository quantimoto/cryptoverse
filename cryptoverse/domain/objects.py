class Instrument(object):
    code = None
    symbol = None
    precision = None


class Instruments(object):
    pass


class Pair(object):

    base = None
    quote = None


class Pairs(object):
    pass


class Market(object):
    context = None  # 'Spot', 'Margin', 'Funding'
    pair = None
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


class Markets(object):
    pass


class Order(object):
    pass


class Orders(object):
    trades = None


class Trade(object):
    pass


class Trades(object):
    pass


class Position(object):
    orders = None
    trades = None


class Positions(object):
    pass


class Offer(object):
    pass


class Offers(object):
    pass


class Lend(objects):
    pass


class Lends(objects):
    pass


class Balance(object):
    amount = None
    instrument = None
    exchange = None



class Balances(object):
    pass


class Exchange(object):
    pass


class Account(object):
    exchange = None

    def orders(self):
        raise NotImplemented

    def trades(self):
        raise NotImplemented

    def positions(self):
        raise NotImplemented

    def offers(self):
        raise NotImplemented

    def lends(self):
        raise NotImplemented

    def balances(self):
        raise NotImplemented

class Portfolio(object):
    pass
