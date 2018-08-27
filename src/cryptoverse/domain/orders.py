from .instruments import Instrument
from .markets import Market
from .object_list import ObjectList
from .pairs import Pair


class Order(object):
    _arg_types = {
        'pair': Pair,
        'market': Market,
        'side': str,
        'amount': float,
        'price': float,
        'type': str,
        'total': float,
        'gross': float,
        'net': float,
        'fees': float,
        'fee_percentage': float,
        'input': float,
        'output': float,
        'timestamp': float,
        'id': str,
        'exchange': None,
        'account': None,
        'fee_instrument': Instrument,
        'input_instrument': Instrument,
        'output_instrument': Instrument,
    }

    _supplied_arguments = None
    _minimum_arguments = None
    _derived_arguments = None

    trades = None

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def as_dict(self):
        dict_obj = dict()
        for key, value in self._supplied_arguments.items():
            if value is not None:
                dict_obj.update({key: value})
        return dict_obj

    def __repr__(self):
        class_name = self.__class__.__name__
        arguments = list()
        for entry in self._minimum_arguments.items():
            arguments.append('{}={!r}'.format(*entry))
        return '{}({})'.format(class_name, ', '.join(arguments))

    @staticmethod
    def _get_kw_for_arg(arg):
        """
        For convenience, some arguments can be used without a keyword and in random order. Their values already reflect
        which kw it's represented by.

        For example:
        >>> Order('BTC/USD', 'buy')

        .. can also be written as:
        >>> Order('buy', 'BTC/USD')

        Both are equal to:
        >>> Order(side='buy', pair=Pair('BTC', 'USD'))
        """
        from cryptoverse.domain import Account
        from cryptoverse.domain import Exchange
        if type(arg) is str and arg.lower() in ['buy', 'sell', 'bid', 'ask']:
            return 'side'
        elif type(arg) is str and Pair.is_valid_symbol(arg):
            return 'pair'
        elif type(arg) is Pair:
            return 'pair'
        elif type(arg) is Market:
            return 'market'
        elif type(arg) is Account:
            return 'account'
        elif type(arg) is Exchange:
            return 'exchange'
        else:
            raise ValueError("'{} supplied without keyword, but not recognized.".format(arg))

    @classmethod
    def _sanitize_kwargs(cls, kwargs):
        result = dict()
        for kw, arg in kwargs.items():
            if kw in cls._arg_types.keys():
                arg_type_obj = cls._arg_types[kw]
                if type(arg) is not arg_type_obj and arg is not None and arg_type_obj is not None:
                    # Try forcing the correct object type
                    try:
                        arg = arg_type_obj(arg)

                    except TypeError:
                        raise TypeError("Invalid type for the argument '{}={}': {}".format(kw, arg, type(arg).__name__))

                if kw == 'side':
                    if arg.lower() == 'bid':
                        arg = 'buy'
                    elif arg.lower() == 'ask':
                        arg = 'sell'
                    elif arg.lower() in ['buy', 'sell']:
                        arg = arg.lower()
                    else:
                        raise ValueError("Invalid value for '{}' supplied: '{}'".format(kw, arg))

                if kw == 'type':
                    if arg.lower() in ['limit', 'market']:
                        arg = arg.lower()
                    else:
                        raise ValueError("Invalid value for '{}' supplied: {}".format(kw, arg))

                result.update({kw: arg})
            else:
                raise TypeError("Got an unexpected keyword argument '{}'".format(kw))

        return result

    @classmethod
    def _derive_missing_kwargs(cls, supplied_kwargs):
        new_kwargs = supplied_kwargs.copy()
        for kw in cls._arg_types:
            if kw not in new_kwargs:
                new_kwargs[kw] = None

        def get_amount(kwargs):
            key = 'amount'

            if kwargs[key] is not None:
                value = kwargs[key]

            # amount = total / price
            elif kwargs['price'] is not None and kwargs['total'] is not None:
                value = kwargs['total'] / kwargs['price']

            # when we buy, gross equals amount
            elif kwargs['gross'] is not None and kwargs['side'] == 'buy':
                value = kwargs['gross']

            # when we sell, input equals amount
            elif kwargs['input'] is not None and kwargs['side'] == 'sell':
                value = kwargs['input']

            else:
                value = None

            return value

        def get_price(kwargs):
            key = 'price'

            if kwargs[key] is not None:
                value = kwargs[key]

            # price = total / amount
            elif kwargs['amount'] is not None and kwargs['total'] is not None:
                value = kwargs['total'] / kwargs['amount']

            else:
                value = None

            return value

        def get_total(kwargs):
            key = 'total'

            if kwargs[key] is not None:
                value = kwargs[key]

            # total = amount * price
            elif kwargs['amount'] is not None and kwargs['price'] is not None:
                value = kwargs['amount'] * kwargs['price']

            # when we sell, gross equals total
            elif kwargs['gross'] is not None and kwargs['side'] == 'sell':
                value = kwargs['gross']

            # when we buy, input equals total
            elif kwargs['input'] is not None and kwargs['side'] == 'buy':
                value = kwargs['input']

            else:
                value = None

            return value

        def get_input(kwargs):
            key = 'input'

            if kwargs[key] is not None:
                value = kwargs[key]

            # when we buy, input equals total
            elif kwargs['total'] is not None and kwargs['side'] == 'buy':
                value = kwargs['total']

            # when we sell, input equals amount
            elif kwargs['amount'] is not None and kwargs['side'] == 'sell':
                value = kwargs['amount']

            else:
                value = None

            return value

        def get_gross(kwargs):
            key = 'gross'

            if kwargs[key] is not None:
                value = kwargs[key]

            # when we buy, gross equals amount
            elif kwargs['amount'] is not None and kwargs['side'] == 'buy':
                value = kwargs['amount']

            # when we sell, gross equals total
            elif kwargs['total'] is not None and kwargs['side'] == 'sell':
                value = kwargs['total']

            # gross = net + fees
            elif kwargs['net'] is not None and kwargs['fees'] is not None:
                value = kwargs['net'] + kwargs['fees']

            # gross = net / (1 - (fee_percentage * 0.01))
            elif kwargs['net'] is not None and kwargs['fee_percentage'] is not None:
                value = kwargs['net'] / (1 - (kwargs['fee_percentage'] * 0.01))

            else:
                value = None

            return value

        def get_fees(kwargs):
            key = 'fees'

            if kwargs[key] is not None:
                value = kwargs[key]

            # fees = gross * fee_percentage * 0.01
            elif kwargs['gross'] is not None and kwargs['fee_percentage'] is not None:
                value = kwargs['gross'] * kwargs['fee_percentage'] * 0.01

            # fees = gross - net
            elif kwargs['gross'] is not None and kwargs['net'] is not None:
                value = kwargs['gross'] - kwargs['net']

            else:
                value = None

            return value

        def get_fee_percentage(kwargs):
            key = 'fee_percentage'

            if kwargs[key] is not None:
                value = kwargs[key]

            # fee_percentage = fees / gross / 0.01
            elif kwargs['gross'] is not None and kwargs['fees'] is not None:
                value = kwargs['fees'] / kwargs['gross'] / 0.01

            else:
                value = None

            return value

        def get_net(kwargs):
            key = 'net'

            if kwargs[key] is not None:
                value = kwargs[key]

            # output is the same value as net
            elif kwargs['output'] is not None:
                value = kwargs['output']

            # net = gross - fees
            elif kwargs['gross'] is not None and kwargs['fees'] is not None:
                value = kwargs['gross'] - kwargs['fees']

            else:
                value = None

            return value

        def get_output(kwargs):
            key = 'output'

            if kwargs[key] is not None:
                value = kwargs[key]

            # output is the same value as net
            elif kwargs['net'] is not None:
                value = kwargs['net']

            else:
                value = None

            return value

        def get_side(kwargs):
            key = 'side'

            if kwargs[key] is not None:
                value = kwargs[key]

            # side from input_instrument and pair
            elif kwargs['input_instrument'] is not None and kwargs['pair'] is not None:
                if kwargs['input_instrument'] == kwargs['pair'].quote:
                    value = 'buy'
                elif kwargs['input_instrument'] == kwargs['pair'].base:
                    value = 'sell'
                else:
                    value = None

            # side from output_instrument and pair
            elif kwargs['output_instrument'] is not None and kwargs['pair'] is not None:
                if kwargs['output_instrument'] == kwargs['pair'].base:
                    value = 'buy'
                elif kwargs['output_instrument'] == kwargs['pair'].quote:
                    value = 'sell'
                else:
                    value = None

            else:
                value = None

            return value

        def get_pair(kwargs):
            key = 'pair'

            if kwargs[key] is not None:
                value = kwargs[key]

            # pair from input_instrument, output_instrument and side
            elif kwargs['input_instrument'] is not None \
                    and kwargs['output_instrument'] is not None and kwargs['side'] is not None:
                if kwargs['side'] == 'buy':
                    base = kwargs['output_instrument']
                    quote = kwargs['input_instrument']
                    value = Pair(base=base, quote=quote)
                elif kwargs['side'] == 'sell':
                    base = kwargs['input_instrument']
                    quote = kwargs['output_instrument']
                    value = Pair(base=base, quote=quote)
                else:
                    value = None

            # pair from market
            elif kwargs['market'] is not None:
                value = kwargs['market'].symbol

            else:
                value = None

            return value

        def get_market(kwargs):
            key = 'market'

            if kwargs[key] is not None:
                value = kwargs[key]

            # market from pair and exchange
            elif kwargs['pair'] is not None and kwargs['exchange'] is not None:
                value = Market(
                    symbol=kwargs['pair'],
                    exchange=kwargs['exchange'],
                )

            else:
                value = None

            return value

        def get_exchange(kwargs):
            key = 'exchange'

            if kwargs[key] is not None:
                value = kwargs[key]

            # exchange from market
            elif kwargs['market'] is not None:
                value = kwargs['market'].exchange

            # exchange from account
            elif kwargs['account'] is not None:
                value = kwargs['account'].exchange

            else:
                value = None

            return value

        def get_fee_instrument(kwargs):
            key = 'fee_instrument'

            if kwargs[key] is not None:
                value = kwargs[key]

            elif kwargs['pair'] is not None and kwargs['side'] == 'buy':
                value = kwargs['pair'].base

            elif kwargs['pair'] is not None and kwargs['side'] == 'sell':
                value = kwargs['pair'].quote

            else:
                value = None

            return value

        def get_input_instrument(kwargs):
            key = 'input_instrument'

            if kwargs[key] is not None:
                value = kwargs[key]

            elif kwargs['pair'] is not None and kwargs['side'] == 'buy':
                value = kwargs['pair'].quote

            elif kwargs['pair'] is not None and kwargs['side'] == 'sell':
                value = kwargs['pair'].base

            else:
                value = None

            return value

        def get_output_instrument(kwargs):
            key = 'output_instrument'

            if kwargs[key] is not None:
                value = kwargs[key]

            elif kwargs['pair'] is not None and kwargs['side'] == 'buy':
                value = kwargs['pair'].base

            elif kwargs['pair'] is not None and kwargs['side'] == 'sell':
                value = kwargs['pair'].quote

            else:
                value = None

            return value

        def remove_empty(kwargs):
            kwargs = kwargs.copy()
            for k, v in kwargs.copy().items():
                if v is None:
                    del kwargs[k]
            return kwargs

        def remove_keys(kwargs, keys):
            kwargs = kwargs.copy()
            for k in kwargs.copy().keys():
                if k in keys:
                    del kwargs[k]
            return kwargs

        def derive_all(kwargs):
            last_hash = 0
            while last_hash != hash(frozenset(kwargs.items())):
                last_hash = hash(frozenset(kwargs.items()))

                kwargs['amount'] = get_amount(kwargs)
                kwargs['price'] = get_price(kwargs)
                kwargs['total'] = get_total(kwargs)
                kwargs['input'] = get_input(kwargs)
                kwargs['gross'] = get_gross(kwargs)
                kwargs['fees'] = get_fees(kwargs)
                kwargs['fee_percentage'] = get_fee_percentage(kwargs)
                kwargs['net'] = get_net(kwargs)
                kwargs['output'] = get_output(kwargs)
                kwargs['side'] = get_side(kwargs)
                kwargs['pair'] = get_pair(kwargs)
                kwargs['market'] = get_market(kwargs)
                kwargs['exchange'] = get_exchange(kwargs)
                kwargs['fee_instrument'] = get_fee_instrument(kwargs)
                kwargs['input_instrument'] = get_input_instrument(kwargs)
                kwargs['output_instrument'] = get_output_instrument(kwargs)
            return kwargs

        new_kwargs = derive_all(kwargs=new_kwargs)
        new_kwargs = remove_empty(kwargs=new_kwargs)
        new_kwargs = remove_keys(kwargs=new_kwargs, keys=supplied_kwargs.keys())

        return new_kwargs

    @classmethod
    def _collect_external_data(cls, kwargs):
        results = dict()
        if 'account' in kwargs.keys():
            fees = kwargs['account'].fees()
        elif 'exchange' in kwargs.keys():
            fees = kwargs['exchange'].fees
        else:
            fees = None

        if fees is not None:
            if kwargs['type'] == 'market':
                kwargs['fee_percentage'] = fees['order']['taker']
            else:
                kwargs['fee_percentage'] = fees['order']['taker']

        return results

    @property
    def pair(self):
        key = 'pair'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @pair.setter
    def pair(self, value):
        self.update(pair=value)

    @property
    def market(self):
        key = 'market'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @market.setter
    def market(self, value):
        self.update(market=value)

    @property
    def side(self):
        key = 'side'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @side.setter
    def side(self, value):
        self.update(side=value)

    @property
    def amount(self):
        key = 'amount'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @amount.setter
    def amount(self, value):
        self.update(amount=value)

    @property
    def price(self):
        key = 'price'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @price.setter
    def price(self, value):
        self.update(price=value)

    @property
    def type(self):
        key = 'type'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @type.setter
    def type(self, value):
        self.update(type=value)

    @property
    def total(self):
        key = 'total'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @total.setter
    def total(self, value):
        self.update(total=value)

    @property
    def gross(self):
        key = 'gross'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @gross.setter
    def gross(self, value):
        self.update(gross=value)

    @property
    def net(self):
        key = 'net'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @net.setter
    def net(self, value):
        self.update(net=value)

    @property
    def fees(self):
        key = 'fees'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @fees.setter
    def fees(self, value):
        self.update(fees=value)

    @property
    def fee_percentage(self):
        key = 'fee_percentage'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @fee_percentage.setter
    def fee_percentage(self, value):
        self.update(fee_percentage=value)

    @property
    def input(self):
        key = 'input'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @input.setter
    def input(self, value):
        self.update(input=value)

    @property
    def output(self):
        key = 'output'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @output.setter
    def output(self, value):
        self.update(output=value)

    @property
    def timestamp(self):
        key = 'timestamp'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @timestamp.setter
    def timestamp(self, value):
        self.update(timestamp=value)

    @property
    def id(self):
        key = 'id'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @id.setter
    def id(self, value):
        self.update(id=value)

    @property
    def exchange(self):
        key = 'exchange'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @exchange.setter
    def exchange(self, value):
        self.update(exchange=value)

    @property
    def account(self):
        key = 'account'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @account.setter
    def account(self, value):
        self.update(account=value)

    @property
    def fee_instrument(self):
        key = 'fee_instrument'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @fee_instrument.setter
    def fee_instrument(self, value):
        self.update(fee_instrument=value)

    @property
    def input_instrument(self):
        key = 'input_instrument'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @input_instrument.setter
    def input_instrument(self, value):
        self.update(input_instrument=value)

    @property
    def output_instrument(self):
        key = 'output_instrument'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @output_instrument.setter
    def output_instrument(self, value):
        self.update(output_instrument=value)

    def update(self, *args, **kwargs):

        # Derive keywords for keyword-less args
        kwargs_from_args = dict()
        for arg in args:
            kw = self._get_kw_for_arg(arg)
            if kw not in kwargs.keys():
                kwargs_from_args.update({kw: arg})
            else:
                raise ValueError(
                    "'{kw}' recognized as keyword for '{arg1}' argument, but '{kw}={arg2}' was also supplied.".format(
                        kw=kw, arg1=arg, arg2=kwargs[kw]))

        # Merge newly keyworded args with kwargs
        new_arguments = dict()
        new_arguments.update(kwargs_from_args)
        new_arguments.update(kwargs)

        # Force type for all arguments
        new_arguments = self._sanitize_kwargs(new_arguments)

        # Retrieve previously supplied arguments
        if self._supplied_arguments is None:
            supplied_arguments = dict()
        else:
            supplied_arguments = self._supplied_arguments.copy()

        # Update previously supplied arguments with new arguments
        supplied_arguments.update(new_arguments)

        # Remove any kwargs with None value
        for kw, arg in supplied_arguments.copy().items():
            if arg is None:
                del supplied_arguments[kw]

        # Store supplied arguments
        self._supplied_arguments = supplied_arguments

        # Derive missing argument values from supplied arguments
        derived_arguments = self._derive_missing_kwargs(supplied_arguments)

        # Store derived arguments
        self._derived_arguments = derived_arguments

        combined_arguments = supplied_arguments.copy()
        combined_arguments.update(derived_arguments)

        # Collect external data to further fill in arguments
        # collected_arguments = self._collect_external_data(combined_arguments)

        minimum_arguments = dict()
        for key in ['pair', 'side', 'amount', 'price', 'fee_percentage']:
            minimum_arguments[key] = combined_arguments[key] if key in combined_arguments else None
        self._minimum_arguments = minimum_arguments

    def place(self):
        raise NotImplementedError

    def cancel(self):
        raise NotImplementedError

    def wait_for_completion(self):
        raise NotImplemented

    def followup(self, *args, **kwargs):
        raise NotImplemented


class Orders(ObjectList):

    def trades(self):
        raise NotImplemented

    def totals(self):
        raise NotImplemented

    def results(self):
        raise NotImplemented

    def avg_price(self):
        raise NotImplemented

    def append_order(self, *args, **kwargs):
        order = Order(*args, **kwargs)
        self.append(order)


class OrderChain(Orders):
    pass
