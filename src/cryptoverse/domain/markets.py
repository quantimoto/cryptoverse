from dict_recursive_update import recursive_update

from .object_list import ObjectList


class Market(object):
    context = None  # 'spot', 'margin', 'funding'
    base = None
    quote = None
    exchange = None
    order_limits = None
    fees = None

    def __init__(self, base, quote, context='spot', exchange=None, order_limits=None, fees=None):
        self.set_base(base)
        self.set_quote(quote)
        self.set_context(context)
        self.set_exchange(exchange)
        self.set_order_limits(order_limits)
        self.set_fees(fees)

    def __repr__(self):
        class_name = self.__class__.__name__
        arguments = list()
        for entry in self.as_dict().items():
            arguments.append('{}={!r}'.format(*entry))
        return '{}({})'.format(class_name, ', '.join(arguments))

    def as_dict(self):
        dict_obj = dict()
        for key, value in self.__dict__.items():
            if key in ['context', 'base', 'quote', 'price_precision', 'order_limits', 'fees']:
                if value is not None:
                    dict_obj.update({key: value})
        return dict_obj

    def set_base(self, base):
        self.base = base

    def set_quote(self, quote):
        self.quote = quote

    def set_context(self, context):
        if context in ['spot', 'margin']:
            self.context = context
        else:
            raise ValueError("'{:s}' is not a valid option. Choose from ['spot', 'margin']".format(context))

    def set_exchange(self, exchange):
        self.exchange = exchange

    def set_order_limits(self, order_limits):
        template = {
            'amount': {
                'min': None,
                'max': None,
                'precision': None,
                'significant digits': None,
            },
            'price': {
                'min': None,
                'max': None,
                'precision': None,
                'significant digits': None,
            },
            'total': {
                'min': None,
                'max': None,
                'precision': None,
                'significant digits': None,
            }
        }
        if self.order_limits is None:
            self.order_limits = template.copy()
        if type(order_limits) is dict:
            recursive_update(self.order_limits, order_limits)

    def set_fees(self, fees):
        template = {'maker': None, 'taker': None}
        if self.fees is None:
            self.fees = template.copy()
        if type(fees) is dict:
            recursive_update(self.fees, fees)


class Markets(ObjectList):
    pass
