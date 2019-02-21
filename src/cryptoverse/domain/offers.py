from time import sleep

from termcolor import colored

from .instruments import Instrument
from .markets import Market
from .object_list import ObjectList
from ..utilities import add_as_decimals as add, filter_keys
from ..utilities import divide_as_decimals as divide
from ..utilities import multiply_as_decimals as multiply
from ..utilities import strip_none, remove_keys, strip_empty, side_colored
from ..utilities import subtract_as_decimals as subtract


class Offer(object):
    _arg_types = {
        'instrument': Instrument,
        'market': Market,
        'side': str,
        'duration': int,
        'amount': float,
        'daily_rate': float,
        'monthly_rate': float,
        'annual_rate': float,
        'type': str,
        'fees': float,
        'gross': float,
        'net': float,
        'fee_percentage': float,
        'timestamp': float,
        'id': str,
        'active': bool,
        'exchange': None,
        'account': None,
        'metadata': dict,
    }

    _supplied_arguments = None
    _derived_arguments = None

    metadata = None

    lends = None

    def __init__(self, *args, **kwargs):
        self.update_arguments(*args, **kwargs)

    def __repr__(self):
        class_name = self.__class__.__name__
        arguments = list()
        for entry in self._minimum_arguments.items():
            if entry[0] == 'side':
                arguments.append(side_colored('{}={!r}'.format(*entry), entry[1]))
            else:
                arguments.append('{}={!r}'.format(*entry))

        return '{}({})'.format(self._status_colored(class_name), ', '.join(arguments))

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
        >>> Offer('USD', 'bid')

        .. can also be written as:
        >>> Offer('bid', 'USD')

        Both are equal to:
        >>> Offer(side='bid', instrument=Instrument('USD'))
        """
        from .accounts import Account
        from .exchanges import Exchange
        if type(arg) is str and arg.lower() in ['buy', 'sell']:
            return 'side'
        elif type(arg) is str and arg.lower() in ['normal', 'hidden']:
            return 'type'
        elif type(arg) is Instrument:
            return 'instrument'
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
                    if arg.lower() in ['buy', 'sell']:
                        arg = arg.lower()
                    else:
                        raise ValueError("Invalid value for '{}' supplied: '{}'".format(kw, arg))

                if kw == 'type':
                    if arg.lower() in ['normal', 'hidden']:
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
        for key in ['account', 'exchange', 'market', 'instrument', 'side']:
            if key in kwargs:
                prepare_kwargs.update({key: kwargs[key]})
        prepare_kwargs.update(cls._sanitize_kwargs(prepare_kwargs))
        kwargs.update(cls._derive_missing_kwargs(prepare_kwargs))

        result = dict()
        # if 'price' in kwargs and type(kwargs['price']) is str:
        #     ticker_key = kwargs['price'].lower()
        #     if ticker_key in ['bid', 'ask', 'last', 'mid']:
        #         if 'market' in kwargs:
        #             market = kwargs['market']
        #             result['price'] = market.ticker[ticker_key]
        #         else:
        #             result['price'] = None
        #
        # if 'input' in kwargs and 'account' in kwargs and 'pair' in kwargs and 'side' in kwargs:
        #     arg = kwargs['input']
        #     if type(kwargs['input']) is str and arg[-1:] == '%':
        #         account = kwargs['account']
        #         pair = kwargs['pair']
        #         side = kwargs['side']
        #         multiplier = float(arg[:-1]) * 0.01
        #         input_instrument = pair.get_input_instrument(side)
        #         instrument_balance = account.wallets()['exchange'].get_by_instrument(input_instrument).first().amount
        #         result['input'] = instrument_balance * multiplier

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

            else:
                value = None

            return value

        def get_daily_rate(kwargs):
            key = 'daily_rate'

            if kwargs[key] is not None:
                value = kwargs[key]

            # daily_rate = annual_rate / 365
            elif kwargs['annual_rate'] is not None:
                value = divide(kwargs['annual_rate'], 365)

            else:
                value = None

            return value

        def get_monthly_rate(kwargs):
            key = 'monthly_rate'

            if kwargs[key] is not None:
                value = kwargs[key]

            # monthly_rate = annual_rate / 12
            elif kwargs['annual_rate'] is not None:
                value = divide(kwargs['annual_rate'], 12)

            else:
                value = None

            return value

        def get_annual_rate(kwargs):
            key = 'annual_rate'

            if kwargs[key] is not None:
                value = kwargs[key]

            # annual_rate = daily_rate * 365
            elif kwargs['daily_rate'] is not None:
                value = multiply(kwargs['daily_rate'], 365)

            # annual_rate = monthly_rate * 12
            elif kwargs['monthly_rate'] is not None:
                value = multiply(kwargs['monthly_rate'], 365)

            else:
                value = None

            return value

        def get_type(kwargs):
            key = 'type'
            default = 'normal'

            if kwargs[key] is not None:
                value = kwargs[key]

            else:
                value = default

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

        def get_gross(kwargs):
            key = 'gross'

            if kwargs[key] is not None:
                value = kwargs[key]

            # gross = amount * daily_rate * duration
            elif kwargs['amount'] is not None and kwargs['daily_rate'] is not None and kwargs['duration'] is not None:
                value = multiply(multiply(kwargs['amount'], kwargs['daily_rate']), kwargs['duration'])

            # gross = net + fees
            elif kwargs['net'] is not None and kwargs['fees'] is not None:
                value = add(kwargs['net'], kwargs['fees'])

            # gross = net / (1 - fee_percentage)
            elif kwargs['net'] is not None and kwargs['fee_percentage'] is not None:
                value = divide(kwargs['net'], subtract(1, kwargs['fee_percentage']))

            else:
                value = None

            return value

        def get_net(kwargs):
            key = 'net'

            if kwargs[key] is not None:
                value = kwargs[key]

            # net = gross - fees
            elif kwargs['gross'] is not None and kwargs['fees'] is not None:
                value = subtract(kwargs['gross'], kwargs['fees'])

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

            # get fee_percentage for normal offer from market fees
            elif kwargs['market'] is not None and kwargs['market'].fees['normal'] is not None \
                    and kwargs['type'] == 'normal':
                value = kwargs['market'].fees['normal']

            # get fee_percentage for hidden offer from market fees
            elif kwargs['market'] is not None and kwargs['market'].fees['hidden'] is not None \
                    and kwargs['type'] == 'hidden':
                value = kwargs['market'].fees['hidden']

            else:
                value = None

            return value

        def get_side(kwargs):
            key = 'side'

            if kwargs[key] is not None:
                value = kwargs[key]

            else:
                value = None

            return value

        def get_duration(kwargs):
            key = 'duration'

            if kwargs[key] is not None:
                value = kwargs[key]

            else:
                value = None

            return value

        def get_instrument(kwargs):
            key = 'instrument'

            if kwargs[key] is not None:
                value = kwargs[key]

            # instrument from market
            elif kwargs['market'] is not None:
                value = kwargs['market'].instrument

            else:
                value = None

            return value

        def get_market(kwargs):
            key = 'market'

            if kwargs[key] is not None:
                value = kwargs[key]

            # market from instrument and exchange
            elif kwargs['instrument'] is not None and kwargs['exchange'] is not None:
                value = kwargs['exchange'].markets.get(symbol=kwargs['instrument'], context='funding')

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

        def derive_all(kwargs):
            last_hash = 0
            while last_hash != hash(frozenset(kwargs.items())):
                last_hash = hash(frozenset(kwargs.items()))

                kwargs['amount'] = get_amount(kwargs)
                kwargs['daily_rate'] = get_daily_rate(kwargs)
                kwargs['monthly_rate'] = get_monthly_rate(kwargs)
                kwargs['annual_rate'] = get_annual_rate(kwargs)
                kwargs['type'] = get_type(kwargs)
                kwargs['fees'] = get_fees(kwargs)
                kwargs['gross'] = get_gross(kwargs)
                kwargs['net'] = get_net(kwargs)
                kwargs['fee_percentage'] = get_fee_percentage(kwargs)
                kwargs['side'] = get_side(kwargs)
                kwargs['duration'] = get_duration(kwargs)
                kwargs['instrument'] = get_instrument(kwargs)
                kwargs['market'] = get_market(kwargs)
                kwargs['exchange'] = get_exchange(kwargs)
            return kwargs

        new_kwargs = derive_all(kwargs=new_kwargs)
        new_kwargs = strip_none(data=new_kwargs)

        return new_kwargs

    @classmethod
    def _collect_external_data(cls, kwargs):
        results = dict()
        if 'account' in kwargs and kwargs['account'] is not None:
            fees = kwargs['account'].fees()
        elif 'exchange' in kwargs and kwargs['exchange'] is not None:
            fees = kwargs['exchange'].fees()
        else:
            fees = None

        if fees is not None and 'instrument' in kwargs and kwargs['instrument'] is not None:
            instrument = kwargs['instrument'].code
            kwargs['fee_percentage'] = fees['offers'][instrument][kwargs['type']]

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
        calculation_priority_arguments = filter_keys(all_arguments, keys=['amount', 'price', 'side'])
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
    def _minimum_arguments(self):
        combined_arguments = self._supplied_arguments.copy()
        if self._derived_arguments is not None:
            combined_arguments.update(self._derived_arguments)

        result = dict()
        for key in ['instrument', 'side', 'amount', 'annual_rate', 'fee_percentage', 'duration']:
            result[key] = combined_arguments.get(key)
        return result

    @property
    def instrument(self):
        key = 'instrument'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @instrument.setter
    def instrument(self, value):
        self.update_arguments(instrument=value)

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
        self.update_arguments(market=value)

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
        self.update_arguments(side=value)

    @property
    def duration(self):
        key = 'duration'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @duration.setter
    def duration(self, value):
        self.update_arguments(duration=value)

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
        self.update_arguments(amount=value)

    @property
    def daily_rate(self):
        key = 'daily_rate'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @daily_rate.setter
    def daily_rate(self, value):
        self.update_arguments(daily_rate=value)

    @property
    def monthly_rate(self):
        key = 'monthly_rate'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @monthly_rate.setter
    def monthly_rate(self, value):
        self.update_arguments(monthly_rate=value)

    @property
    def annual_rate(self):
        key = 'annual_rate'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @annual_rate.setter
    def annual_rate(self, value):
        self.update_arguments(annual_rate=value)

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
        self.update_arguments(type=value)

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
        self.update_arguments(fees=value)

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
        self.update_arguments(gross=value)

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
        self.update_arguments(net=value)

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
        self.update_arguments(fee_percentage=value)

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
        self.update_arguments(timestamp=value)

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
        self.update_arguments(id=value)

    @property
    def active(self):
        key = 'active'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @active.setter
    def active(self, value):
        self.update_arguments(active=value)

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
        self.update_arguments(exchange=value)

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
        self.update_arguments(account=value)

    def place(self):
        if self.account is not None:
            return self.account.place(self)

    def update(self):
        if self.account is not None:
            return self.account.update(self)

    def cancel(self):
        if self.account is not None:
            return self.account.cancel(self)

    def sleep_while_active(self, interval=15):
        while self.is_active:
            self.update()
            try:
                sleep(interval)
            except KeyboardInterrupt:
                continue
        return self

    @property
    def executed_amount(self):
        if self.lends is not None:
            return self.lends.get_sum('amount')
        else:
            return float()

    @property
    def remaining_amount(self):
        return subtract(self.amount, self.executed_amount)

    @property
    def percentage_filled(self):
        return divide(self.remaining_amount, self.amount)

    @property
    def is_placed(self):
        if self.id is not None:
            return True
        return False

    @property
    def is_active(self):
        if self.id is not None and self.active is True:
            return True
        return False

    @property
    def is_partially_filled(self):
        if self.id is not None and 0.0 < self.remaining_amount < self.amount:
            return True
        return False

    @property
    def is_cancelled(self):
        if self.id is not None and self.active is False and self.remaining_amount > 0.0:
            return True
        return False

    @property
    def is_executed(self):
        if self.id is not None and self.active is False and self.remaining_amount == 0.0:
            return True
        return False

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
        else:
            return 'draft'

    def _status_colored(self, value):
        if self.status == 'executed':
            return colored(value, 'green')
        elif self.status == 'cancelled':
            return colored(value, 'red')
        elif self.status == 'partially filled':
            return colored(value, 'yellow')
        elif self.status == 'active':
            return colored(value, 'cyan')
        else:
            return value


class Offers(ObjectList):

    def lends(self):
        raise NotImplementedError

    def append_offer(self, *args, **kwargs):
        offer = Offer(*args, **kwargs)
        self.append(offer)


class OfferBook(object):
    bids = None
    asks = None

    def __init__(self, bids, asks):
        self.bids = bids
        self.asks = asks
