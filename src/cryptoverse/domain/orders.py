from time import sleep

from termcolor import colored

from .amounts import Amounts, Amount
from .instruments import Instrument, Instruments
from .markets import Market, Markets
from .object_list import ObjectList
from .pairs import Pair, Pairs
from ..utilities import add_as_decimals as add, divide_as_decimals as divide, multiply_as_decimals as multiply, \
    subtract_as_decimals as subtract, float_to_unscientific_string, round_up
from ..utilities import round_significant, strip_none, remove_keys, strip_empty, round_down, filter_keys, side_colored


class Order(object):
    arg_types = {
        'pair': Pair,
        'market': Market,
        'side': str,
        'amount': float,
        'price': float,
        'type': str,
        'context': str,
        'total': float,
        'gross': float,
        'net': float,
        'fees': float,
        'fee_percentage': float,
        'input': float,
        'output': float,
        'timestamp': float,
        'id': str,
        'hidden': bool,
        'active': bool,
        'cancelled': bool,
        'exchange': None,
        'account': None,
        'fee_instrument': Instrument,
        'input_instrument': Instrument,
        'output_instrument': Instrument,
        'metadata': dict,
    }

    _supplied_arguments = None
    _derived_arguments = None

    metadata = None

    trades = None

    def __init__(self, *args, **kwargs):
        self.update_arguments(*args, **kwargs)

    def __repr__(self):
        class_name = self.__class__.__name__
        arguments = list()
        for kw in ['status', 'pair', 'side', 'amount', 'price', 'context', 'type', 'fee_percentage']:
            arg = self._get_argument(kw)
            if kw == 'side':
                arguments.append(side_colored('{}={!r}'.format(kw, arg), arg))
            elif kw == 'status':
                arg = getattr(self, kw)
                arguments.append(self._status_colored('{}={!r}'.format(kw, arg)))
            elif kw == 'amount':
                if kw in self._get_argument('market').limits and 'precision' in self._get_argument('market').limits[kw]:
                    precision = self._get_argument('market').limits[kw]['precision']
                else:
                    precision = None
                arg = float_to_unscientific_string(arg, decimals=precision)
                arguments.append('{}={}'.format(kw, arg))
            elif kw == 'price':
                if kw in self._get_argument('market').limits and 'precision' in self._get_argument('market').limits[kw]:
                    precision = self._get_argument('market').limits[kw]['precision']
                else:
                    precision = None
                arg = float_to_unscientific_string(arg, decimals=precision)
                arguments.append('{}={}'.format(kw, arg))
            else:
                arguments.append('{}={!r}'.format(kw, arg))

        return '{}({})'.format(class_name, ', '.join(arguments))

    def as_dict(self):
        dict_obj = dict()
        for key, value in self._supplied_arguments.items():
            if value is not None:
                dict_obj.update({key: value})
        return dict_obj

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(**dict_obj)

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
        if type(arg) is str and arg.lower() in ['buy', 'sell']:
            return 'side'
        elif type(arg) is str and arg.lower() in ['spot', 'margin']:
            return 'context'
        elif type(arg) is str and arg.lower() in ['limit', 'market', 'trailing stop']:
            return 'type'
        elif type(arg) is str and Pair.is_valid_str(arg):
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
            if kw in cls.arg_types.keys():
                arg_type_obj = cls.arg_types[kw]
                if type(arg) is not arg_type_obj and arg is not None and arg_type_obj is not None:
                    # Try forcing the correct object type
                    try:
                        arg = arg_type_obj(arg)

                    except TypeError:
                        raise TypeError("Invalid type for the argument '{}={}': {}".format(kw, arg, type(arg).__name__))

                if kw == 'side':
                    if arg.lower() in ['buy', 'sell']:
                        arg = arg.lower()
                    else:
                        raise ValueError("Invalid value for '{}' supplied: '{}'".format(kw, arg))

                if kw == 'type':
                    if arg.lower() in ['limit', 'market', 'trailing stop']:
                        arg = arg.lower()
                    else:
                        raise ValueError("Invalid value for '{}' supplied: {}".format(kw, arg))

                if kw == 'context':
                    if arg.lower() in ['spot', 'margin']:
                        arg = arg.lower()
                    else:
                        raise ValueError("Invalid value for '{}' supplied: {}".format(kw, arg))

                result.update({kw: arg})
            else:
                raise TypeError("Got an unexpected keyword argument '{}'".format(kw))

        return result

    @classmethod
    def _replace_shortcuts(cls, kwargs):
        kwargs = kwargs.copy()

        prepare_kwargs = dict()
        for key in ['account', 'exchange', 'market', 'pair', 'side', 'context', 'input_instrument',
                    'output_instrument']:
            if key in kwargs:
                prepare_kwargs.update({key: kwargs[key]})
        prepare_kwargs.update(cls._sanitize_kwargs(prepare_kwargs))
        kwargs.update(cls._derive_missing_kwargs(prepare_kwargs))

        result = dict()
        if 'price' in kwargs and type(kwargs['price']) is str:
            ticker_key = kwargs['price'].lower()
            if ticker_key in ['bid', 'ask', 'last', 'mid']:
                if 'market' in kwargs:
                    market = kwargs['market']
                    result['price'] = market.ticker()[ticker_key]
                else:
                    result['price'] = None

        if 'input' in kwargs and 'account' in kwargs and 'pair' in kwargs and 'side' in kwargs and 'context' in kwargs:
            arg = kwargs['input']
            if type(kwargs['input']) is str and arg[-1:] == '%':
                account = kwargs['account']
                pair = kwargs['pair']
                side = kwargs['side']
                multiplier = multiply(arg[:-1], 0.01)
                input_instrument = pair.get_input_instrument(side)
                balance = account.wallets(kwargs['context']).balances.get(instrument=input_instrument)
                if balance:
                    instrument_balance = balance.amount
                else:
                    instrument_balance = None
                result['input'] = multiply(instrument_balance, multiplier)

        return result

    @classmethod
    def _derive_missing_kwargs(cls, supplied_kwargs):
        new_kwargs = supplied_kwargs.copy()
        for kw in cls.arg_types:
            if kw not in new_kwargs:
                new_kwargs[kw] = None

        def get_amount(kwargs):
            key = 'amount'

            if kwargs[key] is not None:
                value = kwargs[key]

            # amount = total / price
            elif kwargs['price'] is not None and kwargs['total'] is not None:
                value = divide(kwargs['total'], kwargs['price'])

            # when we buy, gross equals amount
            elif kwargs['gross'] is not None and kwargs['side'] == 'buy':
                value = kwargs['gross']

            # when we sell, input equals amount
            elif kwargs['input'] is not None and kwargs['side'] == 'sell':
                value = kwargs['input']

            else:
                value = None

            if kwargs['market'] is not None and kwargs['market'].limits is not None:
                if key in kwargs['market'].limits:
                    if 'precision' in kwargs['market'].limits[key]:
                        precision = kwargs['market'].limits[key]['precision']
                        if precision is not None:
                            value = round_down(value, precision) if value is not None else value

            if kwargs['pair'] is not None and kwargs['pair'].base is not None and \
                    kwargs['pair'].base.precision is not None:
                precision = kwargs['pair'].base.precision
                if precision is not None:
                    value = round_down(value, precision) if value is not None else value

            return value

        def get_price(kwargs):
            key = 'price'

            if kwargs[key] is not None:
                value = kwargs[key]

            # price = total / amount
            elif kwargs['amount'] is not None and kwargs['total'] is not None:
                value = divide(kwargs['total'], kwargs['amount'])

            else:
                value = None

            if kwargs['market'] is not None and kwargs['market'].limits is not None:
                if key in kwargs['market'].limits:
                    if 'significant digits' in kwargs['market'].limits[key]:
                        significant_digits = kwargs['market'].limits[key]['significant digits']
                        if significant_digits is not None:
                            value = round_significant(value, significant_digits) if value is not None else value
                    if 'precision' in kwargs['market'].limits[key]:
                        precision = kwargs['market'].limits[key]['precision']
                        if precision is not None:
                            if kwargs['side'] is not None and kwargs['side'] == 'sell':
                                value = round_up(value, precision) if value is not None else value
                            else:
                                value = round_down(value, precision) if value is not None else value
            return value

        def get_total(kwargs):
            key = 'total'

            if kwargs[key] is not None:
                value = kwargs[key]

            # total = amount * price
            elif kwargs['amount'] is not None and kwargs['price'] is not None:
                value = multiply(kwargs['amount'], kwargs['price'])

            # when we sell, gross equals total
            elif kwargs['gross'] is not None and kwargs['side'] == 'sell':
                value = kwargs['gross']

            # when we buy, input equals total
            elif kwargs['input'] is not None and kwargs['side'] == 'buy':
                value = kwargs['input']

            else:
                value = None

            if kwargs['market'] is not None and kwargs['market'].limits is not None:
                if key in kwargs['market'].limits:
                    if 'precision' in kwargs['market'].limits[key]:
                        precision = kwargs['market'].limits[key]['precision']
                        if precision is not None:
                            value = round_down(value, precision) if value is not None else value

            if kwargs['pair'] is not None and kwargs['pair'].quote is not None and \
                    kwargs['pair'].quote.precision is not None:
                precision = kwargs['pair'].quote.precision
                if precision is not None:
                    value = round_down(value, precision) if value is not None else value

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
                value = add(kwargs['net'], kwargs['fees'])

            # gross = net / (1 - fee_percentage)
            elif kwargs['net'] is not None and kwargs['fee_percentage'] is not None:
                value = divide(kwargs['net'], subtract(1, kwargs['fee_percentage']))

            else:
                value = None

            return value

        def get_fees(kwargs):
            key = 'fees'

            if kwargs[key] is not None:
                value = kwargs[key]

            # fees = gross * fee_percentage
            elif kwargs['gross'] is not None and kwargs['fee_percentage'] is not None:
                value = multiply(kwargs['gross'], kwargs['fee_percentage'])

            # fees = gross - net
            elif kwargs['gross'] is not None and kwargs['net'] is not None:
                value = subtract(kwargs['gross'], kwargs['net'])

            else:
                value = None

            return value

        def get_fee_percentage(kwargs):
            key = 'fee_percentage'

            if kwargs[key] is not None:
                value = kwargs[key]

            # fee_percentage = fees / gross
            elif kwargs['gross'] is not None and kwargs['fees'] is not None:
                value = divide(kwargs['fees'], kwargs['gross'])

            # get fee_percentage for hidden limit order from market fees
            elif kwargs['market'] is not None and kwargs['market'].fees['maker'] is not None \
                    and kwargs['type'] is 'limit' and kwargs['hidden'] is True:
                value = kwargs['market'].fees['taker']

            # get fee_percentage for visible limit order from market fees
            elif kwargs['market'] is not None and kwargs['market'].fees['maker'] is not None \
                    and kwargs['type'] is 'limit' and kwargs['hidden'] is not True:
                value = kwargs['market'].fees['maker']

            # get fee_percentage for market order from market fees
            elif kwargs['market'] is not None and kwargs['market'].fees['taker'] is not None \
                    and kwargs['type'] is 'market':
                value = kwargs['market'].fees['taker']

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
                value = subtract(kwargs['gross'], kwargs['fees'])

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

            # side from input_instrument, output_instrument and exchange
            elif kwargs['input_instrument'] is not None and kwargs['output_instrument'] is not None \
                    and kwargs['exchange'] is not None:
                pairs = kwargs['exchange'].pairs.with_instruments(kwargs['input_instrument'],
                                                                  kwargs['output_instrument'])
                if pairs.first:
                    pair = pairs.first
                    value = pair.get_side(input_instrument=kwargs['input_instrument'])
                else:
                    value = None

            else:
                value = None

            return value

        def get_type(kwargs):
            key = 'type'
            default = 'limit'

            if kwargs[key] is not None:
                value = kwargs[key]

            else:
                value = default

            return value

        def get_context(kwargs):
            key = 'context'
            default = 'spot'

            if kwargs[key] is not None:
                value = kwargs[key]

            else:
                value = default

            return value

        def get_hidden(kwargs):
            key = 'hidden'
            default = False

            if kwargs[key] is not None:
                value = kwargs[key]

            else:
                value = default

            return value

        def get_pair(kwargs):
            key = 'pair'

            if kwargs[key] is not None:
                value = kwargs[key]

            # pair from input_instrument, output_instrument and exchange
            elif kwargs['input_instrument'] is not None and kwargs['output_instrument'] is not None \
                    and kwargs['exchange'] is not None:
                pairs = kwargs['exchange'].pairs.with_instruments(kwargs['input_instrument'],
                                                                  kwargs['output_instrument'])
                if pairs.first:
                    value = pairs.first
                else:
                    value = None

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
                value = kwargs['market'].pair

            else:
                value = None

            return value

        def get_market(kwargs):
            key = 'market'

            if kwargs[key] is not None:
                value = kwargs[key]

            # market from pair, exchange and context
            elif kwargs['pair'] is not None and kwargs['exchange'] is not None and kwargs['context'] is not None \
                    and kwargs['exchange'].markets.find(context=kwargs['context']):
                value = kwargs['exchange'].markets.get(symbol=kwargs['pair'], context=kwargs['context'])

            # market from input_instrument, output_instrument, exchange and context
            elif kwargs['input_instrument'] is not None and kwargs['output_instrument'] is not None \
                    and kwargs['exchange'] is not None and kwargs['context'] is not None \
                    and kwargs['context'] in kwargs['exchange'].markets:
                value = kwargs['exchange'].markets[kwargs['context']] \
                    .with_instruments(kwargs['input_instrument'], kwargs['output_instrument']) \
                    .get(context=kwargs['context'])

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
                kwargs['type'] = get_type(kwargs)
                kwargs['context'] = get_context(kwargs)
                kwargs['hidden'] = get_hidden(kwargs)
                kwargs['pair'] = get_pair(kwargs)
                kwargs['market'] = get_market(kwargs)
                kwargs['exchange'] = get_exchange(kwargs)
                kwargs['fee_instrument'] = get_fee_instrument(kwargs)
                kwargs['input_instrument'] = get_input_instrument(kwargs)
                kwargs['output_instrument'] = get_output_instrument(kwargs)
            return kwargs

        new_kwargs = derive_all(kwargs=new_kwargs)
        new_kwargs = strip_none(data=new_kwargs)

        return new_kwargs

    @classmethod
    def _collect_external_data(cls, kwargs):
        results = dict()
        if 'fees' not in kwargs and 'fee_percentage' not in kwargs:
            if 'account' in kwargs and kwargs['account'] is not None:
                fees = kwargs['account'].fees()
            elif 'exchange' in kwargs and kwargs['exchange'] is not None:
                fees = kwargs['exchange'].fees()
            else:
                fees = None

            if fees is not None and 'pair' in kwargs and kwargs['pair'] is not None:
                pair_str = kwargs['pair'].as_str()
                if pair_str not in fees['orders']:
                    raise ValueError("pair not found in fee information: {}".format(kwargs['pair']))

                if 'type' in kwargs and kwargs['type'] == 'market' or 'hidden' in kwargs and kwargs['hidden'] is True:
                    kwargs['fee_percentage'] = fees['orders'][pair_str]['taker']
                else:
                    kwargs['fee_percentage'] = fees['orders'][pair_str]['maker']

        return results

    def update_arguments(self, *args, **kwargs):

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

        # Merge args with kwargs
        new_arguments = dict()
        new_arguments.update(kwargs_from_args)
        new_arguments.update(kwargs)

        # Retrieve previously supplied arguments
        if self._supplied_arguments is None:
            supplied_arguments = dict()
        else:
            supplied_arguments = self._supplied_arguments.copy()

        # merge stored supplied arguments with newly supplied arguments
        combined_arguments = supplied_arguments.copy()
        combined_arguments.update(new_arguments)

        # Replace shortcut strings with external values
        replaced_arguments = self._replace_shortcuts(combined_arguments)
        new_arguments.update(replaced_arguments)

        # Sanitize new arguments
        new_arguments = self._sanitize_kwargs(new_arguments)

        # Update previously supplied arguments with new arguments
        supplied_arguments.update(new_arguments)

        # Remove any kwargs with None value
        for kw, arg in supplied_arguments.copy().items():
            if arg is None:
                del supplied_arguments[kw]

        # Move metadata away
        if 'metadata' in supplied_arguments:
            self.metadata = supplied_arguments['metadata']
            del supplied_arguments['metadata']

        # Derive missing argument values from supplied arguments
        derived_arguments = self._derive_missing_kwargs(supplied_arguments)

        # Collect external data to further fill in arguments
        collected_arguments = self._collect_external_data(derived_arguments)
        derived_arguments.update(collected_arguments)

        # Derive missing argument values again with newly collected arguments
        all_arguments = self._derive_missing_kwargs(derived_arguments)

        # Derive argument again but only the minimum_arguments. This to ensure precision with calculation priority
        calculation_priority_arguments = filter_keys(all_arguments, keys=['amount', 'price', 'side', 'type', 'context'])
        calculation_priority_arguments = self._derive_missing_kwargs(calculation_priority_arguments)
        all_arguments.update(calculation_priority_arguments)

        # Split arguments into supplied and derived
        derived_arguments = remove_keys(kwargs=all_arguments, keys=supplied_arguments.keys())
        supplied_arguments = remove_keys(kwargs=all_arguments, keys=derived_arguments.keys())

        # Store supplied and derived arguments
        supplied_arguments = strip_empty(supplied_arguments)
        self._supplied_arguments = supplied_arguments if supplied_arguments is not None else dict()
        derived_arguments = strip_none(derived_arguments)
        self._derived_arguments = derived_arguments if derived_arguments is not None else dict()

    @property
    def _all_arguments(self):
        result = dict()

        if self._supplied_arguments is not None:
            result.update(self._supplied_arguments)
        if self._derived_arguments is not None:
            result.update(self._derived_arguments)

        return result

    def _get_argument(self, key):
        if key in self._all_arguments:
            return self._all_arguments[key]
        return None

    @property
    def _minimum_arguments(self):
        result = dict()
        for key in ['pair', 'side', 'amount', 'price', 'fee_percentage']:
            result[key] = self._get_argument(key)
        return result

    @property
    def pair(self):
        return self._get_argument('pair')

    @pair.setter
    def pair(self, value):
        self.update_arguments(pair=value)

    @property
    def market(self):
        return self._get_argument('market')

    @market.setter
    def market(self, value):
        self.update_arguments(market=value)

    @property
    def side(self):
        return self._get_argument('side')

    @side.setter
    def side(self, value):
        self.update_arguments(side=value)

    @property
    def amount(self):
        return self._get_argument('amount')

    @amount.setter
    def amount(self, value):
        self.update_arguments(amount=value)

    @property
    def price(self):
        return self._get_argument('price')

    @price.setter
    def price(self, value):
        self.update_arguments(price=value)

    @property
    def type(self):
        return self._get_argument('type')

    @type.setter
    def type(self, value):
        self.update_arguments(type=value)

    @property
    def context(self):
        return self._get_argument('context')

    @context.setter
    def context(self, value):
        self.update_arguments(context=value)

    @property
    def total(self):
        return self._get_argument('total')

    @total.setter
    def total(self, value):
        self.update_arguments(total=value)

    @property
    def gross(self):
        return self._get_argument('gross')

    @gross.setter
    def gross(self, value):
        self.update_arguments(gross=value)

    @property
    def net(self):
        return self._get_argument('net')

    @net.setter
    def net(self, value):
        self.update_arguments(net=value)

    @property
    def fees(self):
        return self._get_argument('fees')

    @fees.setter
    def fees(self, value):
        self.update_arguments(fees=value)

    @property
    def fee_percentage(self):
        return self._get_argument('fee_percentage')

    @fee_percentage.setter
    def fee_percentage(self, value):
        self.update_arguments(fee_percentage=value)

    @property
    def input(self):
        return self._get_argument('input')

    @input.setter
    def input(self, value):
        self.update_arguments(input=value)

    @property
    def output(self):
        if self.is_executed and self.trades is not None:
            if self.side == 'buy':
                return subtract(self.trades.get_sum('amount'), self.trades.get_sum('fees'))
            elif self.side == 'sell':
                return subtract(self.trades.get_sum('total'), self.trades.get_sum('fees'))

        return self._get_argument('output')

    @output.setter
    def output(self, value):
        self.update_arguments(output=value)

    @property
    def timestamp(self):
        return self._get_argument('timestamp')

    @timestamp.setter
    def timestamp(self, value):
        self.update_arguments(timestamp=value)

    @property
    def id(self):
        return self._get_argument('id')

    @id.setter
    def id(self, value):
        self.update_arguments(id=value)

    @property
    def hidden(self):
        return self._get_argument('hidden') is True

    @hidden.setter
    def hidden(self, value):
        self.update_arguments(hidden=value)

    @property
    def active(self):
        return self._get_argument('active') is True

    @active.setter
    def active(self, value):
        self.update_arguments(active=value)

    @property
    def cancelled(self):
        return self._get_argument('cancelled') is True

    @cancelled.setter
    def cancelled(self, value):
        self.update_arguments(cancelled=value)

    @property
    def exchange(self):
        return self._get_argument('exchange')

    @exchange.setter
    def exchange(self, value):
        self.update_arguments(exchange=value)

    @property
    def account(self):
        return self._get_argument('account')

    @account.setter
    def account(self, value):
        self.update_arguments(account=value)

    @property
    def fee_instrument(self):
        return self._get_argument('fee_instrument')

    @fee_instrument.setter
    def fee_instrument(self, value):
        self.update_arguments(fee_instrument=value)

    @property
    def input_instrument(self):
        return self._get_argument('input_instrument')

    @input_instrument.setter
    def input_instrument(self, value):
        self.update_arguments(input_instrument=value)

    @property
    def output_instrument(self):
        return self._get_argument('output_instrument')

    @output_instrument.setter
    def output_instrument(self, value):
        self.update_arguments(output_instrument=value)

    @property
    def instruments(self):
        return self.pair.instruments

    def place(self):
        if self.account is not None:
            return self.account.place(self)

    def update(self):
        if self.account is not None:
            return self.account.update(self)

    def cancel(self):
        if self.account is not None:
            return self.account.cancel(self)

    def replace_with(self, new_order):
        if self.account is not None:
            return self.account.replace(self, new_order)

    def sleep_while_active(self, interval=5):
        # This method will stop looping as soon is the order is no longer active.
        while self.is_active:
            try:
                sleep(interval)
            except KeyboardInterrupt:
                print()
                print("User cancelled sleep.")
                break
            finally:
                self.update()
        return self

    def sleep_while_unfilled(self, interval=5):
        # This method will stop sleeping as soon as the order is partially filled.
        while self.is_unfilled:
            try:
                sleep(interval)
            except KeyboardInterrupt:
                print()
                print("User cancelled sleep.")
                break
            finally:
                self.update()
        return self

    def followup(self, output='100%'):
        if type(output) is str and output[-1:] == '%':
            if output[:1] in ['+', '-']:
                multiplier = add(1, multiply(output[:-1], 0.01))
                output = multiply(self.input, multiplier)
            else:
                multiplier = multiply(output[:-1], 0.01)
                output = multiply(self.input, multiplier)

        result = self.__class__(
            account=self.account,
            exchange=self.exchange,
            market=self.market,
            pair=self.pair,
            side='sell' if self.side == 'buy' else 'buy',
            input=self.output,
            output=output,
        )
        return result

    @property
    def executed_amount(self):
        if self.trades is not None:
            return self.trades.get_sum('amount')
        else:
            return float()

    @property
    def remaining_amount(self):
        if self.amount is not None and self.executed_amount is not None:
            return subtract(self.amount, self.executed_amount)
        return None

    @property
    def percentage_filled(self):
        return divide(self.remaining_amount, self.amount)

    @property
    def is_draft(self):
        if self.id is None and not self.trades:
            return True
        return False

    @property
    def is_placed(self):
        return self.id is not None

    @property
    def is_unfilled(self):
        return self.executed_amount == 0.0

    @property
    def is_partially_filled(self):
        if self.remaining_amount is not None and self.amount is not None:
            return 0.0 < self.remaining_amount < self.amount
        return False

    @property
    def is_filled(self):
        if self.executed_amount is not None and self.amount is not None:
            return self.executed_amount >= self.amount

    @property
    def is_active(self):
        return self.id is not None and self.active is True

    @property
    def is_cancelled(self):
        return self.cancelled

    @property
    def is_executed(self):
        return self.is_placed and not self.is_active and not self.is_cancelled

    @property
    def has_trades(self):
        if self.trades is not None and len(self.trades) > 0:
            return True
        return False

    @property
    def has_executed_amount(self):
        return self.is_filled or self.is_partially_filled

    @property
    def status(self):
        if self.is_executed:
            return 'executed'
        elif self.is_cancelled:
            return 'cancelled'
        elif self.is_partially_filled:
            return 'partially filled'
        elif self.is_active:
            return 'active'
        elif self.is_draft:
            return 'draft'
        else:
            return None

    def _status_colored(self, value):
        if self.status == 'unknown':
            return colored(value, 'magenta')
        elif self.status == 'executed':
            return colored(value, 'green')
        elif self.status == 'cancelled':
            return colored(value, 'red')
        elif self.status == 'partially filled':
            return colored(value, 'yellow')
        elif self.status == 'active':
            return colored(value, 'cyan')
        else:
            return value


class Orders(ObjectList):

    def __init__(self, *args, **kwargs):
        obj_list = list()
        if len(args) == 1 and type(args[0]) is list:
            obj_list = args[0]
        elif not args and not kwargs:
            pass
        elif args and type(args[0]) is Order:
            for arg in args:
                if type(arg) is Order:
                    obj_list.append(arg)
        else:
            listable_keywords = Order.arg_types.keys()
            value_lists = dict()
            for kw in listable_keywords:
                if kw in kwargs and type(kwargs[kw]) is list:
                    value_lists.update({kw: kwargs[kw]})
            lists_len = [len(values) for kw, values in value_lists.items()]

            iterations = sum(lists_len) / float(len(lists_len))
            if lists_len[0] == iterations:
                iterations = int(iterations)
                for i in range(iterations):
                    order_kwargs = kwargs.copy()
                    for kw, values in value_lists.items():
                        order_kwargs[kw] = values[i]
                    obj_list.append(Order(*args, **order_kwargs))
            else:
                raise ValueError("List lengths must match")

        super(ObjectList, self).__init__(obj_list)

    @property
    def instruments(self):
        result = Instruments()
        for pair in self.get_unique_values('pair'):
            for instrument in pair.instruments:
                if instrument not in result:
                    result.append(instrument)
        return result

    @property
    def pairs(self):
        return Pairs(self.get_unique_values('pair'))

    @property
    def markets(self):
        return Markets(self.get_unique_values('market'))

    @property
    def trades(self):
        from cryptoverse.domain import Trades
        result = Trades()
        for entry in self:
            if entry.trades is not None:
                result += entry.trades
        return result

    def avg_price(self):
        raise NotImplemented

    def append_order(self, *args, **kwargs):
        order = Order(*args, **kwargs)
        self.append(order)

    def place(self):
        accounts = self.get_unique_values('account')
        if len(accounts) > 1:
            for account in accounts:
                orders_for_account = self.find(account=account, is_draft=True)
                orders_for_account.place()
        elif len(accounts) == 1:
            account = accounts.first
            account.place(self.find(is_draft=True))

        return self

    def update(self):
        accounts = self.get_unique_values('account')
        if len(accounts) > 1:
            for account in accounts:
                orders_for_account = self.find(account=account, is_executed=False, is_placed=True)
                orders_for_account.update()
        elif len(accounts) == 1:
            account = accounts.first
            account.update(self.find(is_active=True))

        return self

    def cancel(self):
        accounts = self.get_unique_values('account')
        if len(accounts) > 1:
            for account in accounts:
                orders_for_account = self.find(account=account, is_active=True)
                orders_for_account.cancel()
        elif len(accounts) == 1:
            account = accounts.first
            account.cancel(self.find(is_active=True))

        return self

    def collapse(self):
        result = Orders()
        for account in self.get_unique_values('account'):
            for exchange in self.find(account=account).get_unique_values('exchange'):
                for market in self.find(account=account, exchange=exchange).get_unique_values('market'):
                    for side in self.find(account=account, exchange=exchange).get_unique_values('side'):
                        selected_orders = self.find(account=account, exchange=exchange, market=market, side=side)
                        if selected_orders:
                            result.append_order(
                                account=account,
                                exchange=exchange,
                                market=market,
                                side=side,
                                input=selected_orders.get_sum('input'),
                                output=selected_orders.get_sum('output'),
                            )
        return result

    def inputs(self):
        result = dict()
        for instrument in self.get_unique_values('input_instrument'):
            order_selection = self.find(input_instrument=instrument)
            result[instrument.as_str()] = order_selection.get_sum('input')
        return result

    def outputs(self):
        result = dict()
        for instrument in self.get_unique_values('output_instrument'):
            order_selection = self.find(output_instrument=instrument)
            result[instrument.as_str()] = order_selection.get_sum('output')
        return result

    def totals(self):
        result = dict()
        for key, value in self.inputs().items():
            if key not in result:
                result[key] = float()
            result[key] = subtract(result[key], value)
        for key, value in self.outputs().items():
            if key not in result:
                result[key] = float()
            result[key] = add(result[key], value)

        amounts = Amounts()
        for key, value in result.items():
            amounts.append(Amount(value=value, instrument=key))

        return amounts

    def results(self):
        return self.find(is_executed=True).totals()


class OrderChain(Orders):

    def has_active(self):
        return len(self.find(is_active=True)) > 0

    def get_next(self):
        if self.find(is_cancelled=True):
            raise Exception("OrderChain can't continue, because it contains a cancelled order.")

        if self.find(is_placed=False):
            return self.find(is_placed=False).first

    def place(self):
        # In the OrderChain object, only 1 order can be active at a time. This method only places a new order if no
        # other order is active. If a previous order has not been successfully executed, the next order will not be
        # placed.

        if self.find(is_active=False):
            unplaced_orders = self.find(is_placed=False)
            placed_orders = self.find(is_placed=True)
            if placed_orders and not placed_orders.last.is_executed:
                return self
            elif unplaced_orders:
                unplaced_orders.first.place()

        return self

    @property
    def is_idle(self):
        return not self.has_active()

    @property
    def is_completed(self):
        return len(self.find(is_executed=True)) == len(self)

    @property
    def is_cancelled(self):
        return self.find(is_placed=True).last.is_cancelled


class OrderBook(object):
    bids = None
    asks = None

    def __init__(self, bids, asks):
        self.bids = bids
        self.asks = asks
