from .markets import Markets
from .object_list import ObjectList
from .orders import Order


class Balance(object):
    amount = None
    available = None
    instrument = None
    account = None
    wallet = None

    def __init__(self, instrument=None, amount=None, available=None, account=None, wallet=None):
        self.instrument = instrument
        self.amount = amount
        self.available = available
        self.account = account
        self.wallet = wallet

    def __repr__(self):
        class_name = self.__class__.__name__
        arguments = list()
        for entry in self.as_dict().items():
            arguments.append('{}={!r}'.format(*entry))
        return '{}({})'.format(class_name, ', '.join(arguments))

    def as_dict(self):
        dict_obj = dict()
        for key in ['amount', 'instrument', 'account']:
            value = getattr(self, key)
            if value is not None:
                dict_obj.update({key: value})
        return dict_obj

    def valued_in(self, quote_instrument):
        if self.account is not None:

            market = self.account.exchange.spot_markets[self.instrument.code, quote_instrument]
            if type(market) is Markets and len(market) > 0:
                market = market.first()
            if market:
                side = market.get_side(input_instrument=self.instrument)
                price = market.ticker.bid if side == 'ask' else market.ticker.ask
                order = Order(
                    pair=market.symbol,
                    side=side,
                    input=self.amount,
                    price=price,
                ).output
                return order

    def value_at(self, price):
        return self.amount * price


class Balances(ObjectList):

    def get_by_instrument(self, *instruments):
        result = self.__class__()
        for instrument in instruments:
            result = result + self.find(instrument=instrument)
        return result

    def values(self, value_instrument='USD'):
        quote_instrument = value_instrument
        values = dict()
        for balance in self:
            if balance.instrument == quote_instrument:
                values.update({
                    balance.instrument.code: balance.amount
                })
            else:
                values.update({
                    balance.instrument.code: balance.valued_in(quote_instrument=quote_instrument)
                })
        return values

    def weights(self):
        values = self.values()
        total_value = sum(values.values())
        weights = dict()
        for instrument_code, value in values.items():
            weights.update({
                instrument_code: value / total_value
            })
        return weights
