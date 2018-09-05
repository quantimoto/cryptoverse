from cryptoverse.utilities import remove_keys, strip_empty, strip_none
from .instruments import Instrument
from .markets import Market
from .object_list import ObjectList


class Offer(object):
    _arg_types = {
        'instrument': Instrument,
        'market': Market,
        'side': str,
        'period': int,
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
        'exchange': None,
        'account': None,
    }

    _supplied_arguments = None
    _derived_arguments = None

    lends = None

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
        >>> Offer('USD', 'bid')

        .. can also be written as:
        >>> Offer('bid', 'USD')

        Both are equal to:
        >>> Offer(side='bid', instrument=Instrument('USD'))
        """
        from .accounts import Account
        from .exchanges import Exchange
        if type(arg) is str and arg.lower() in ['buy', 'sell', 'bid', 'ask']:
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
                    if arg.lower() == 'bid':
                        arg = 'buy'
                    elif arg.lower() == 'ask':
                        arg = 'sell'
                    elif arg.lower() in ['buy', 'sell']:
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
                value = kwargs['annual_rate'] / 365

            else:
                value = None

            return value

        def get_monthly_rate(kwargs):
            key = 'monthly_rate'

            if kwargs[key] is not None:
                value = kwargs[key]

            # monthly_rate = annual_rate / 12
            elif kwargs['annual_rate'] is not None:
                value = kwargs['annual_rate'] / 12

            else:
                value = None

            return value

        def get_annual_rate(kwargs):
            key = 'annual_rate'

            if kwargs[key] is not None:
                value = kwargs[key]

            # annual_rate = daily_rate * 365
            elif kwargs['daily_rate'] is not None:
                value = kwargs['daily_rate'] * 365

            # annual_rate = monthly_rate * 12
            elif kwargs['monthly_rate'] is not None:
                value = kwargs['monthly_rate'] * 365

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

            # fees = gross * fee_percentage * 0.01
            elif kwargs['gross'] is not None and kwargs['fee_percentage'] is not None:
                value = kwargs['gross'] * kwargs['fee_percentage'] * 0.01

            # fees = gross - net
            elif kwargs['gross'] is not None and kwargs['net'] is not None:
                value = kwargs['gross'] - kwargs['net']

            else:
                value = None

            return value

        def get_gross(kwargs):
            key = 'gross'

            if kwargs[key] is not None:
                value = kwargs[key]

            # gross = amount * (daily_rate * 0.01) * period
            elif kwargs['amount'] is not None and kwargs['daily_rate'] is not None and kwargs['period'] is not None:
                value = kwargs['amount'] * (kwargs['daily_rate'] * 0.01) * kwargs['period']

            # gross = net + fees
            elif kwargs['net'] is not None and kwargs['fees'] is not None:
                value = kwargs['net'] + kwargs['fees']

            # gross = net / (1 - (fee_percentage * 0.01))
            elif kwargs['net'] is not None and kwargs['fee_percentage'] is not None:
                value = kwargs['net'] / (1 - (kwargs['fee_percentage'] * 0.01))

            else:
                value = None

            return value

        def get_net(kwargs):
            key = 'net'

            if kwargs[key] is not None:
                value = kwargs[key]

            # net = gross - fees
            elif kwargs['gross'] is not None and kwargs['fees'] is not None:
                value = kwargs['gross'] - kwargs['fees']

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

        def get_period(kwargs):
            key = 'period'

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
                kwargs['period'] = get_period(kwargs)
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

        # Retrieve previously supplied arguments
        if self._supplied_arguments is None:
            supplied_arguments = dict()
        else:
            supplied_arguments = self._supplied_arguments.copy()

        # Replace shortcut strings with external values
        combined_arguments = supplied_arguments.copy()
        combined_arguments.update(new_arguments)
        replace_arguments = self._replace_shortcuts(combined_arguments)
        new_arguments.update(replace_arguments)

        # Force type for new arguments
        new_arguments = self._sanitize_kwargs(new_arguments)

        # Update previously supplied arguments with new arguments
        supplied_arguments.update(new_arguments)

        # Remove any kwargs with None value
        for kw, arg in supplied_arguments.copy().items():
            if arg is None:
                del supplied_arguments[kw]

        # Derive missing argument values from supplied arguments
        derived_arguments = self._derive_missing_kwargs(supplied_arguments)

        # Collect external data to further fill in arguments
        collected_arguments = self._collect_external_data(derived_arguments)
        derived_arguments.update(collected_arguments)

        # Derive missing argument values again with newly collected arguments
        derived_arguments = self._derive_missing_kwargs(derived_arguments)

        # Remove supplied arguments from derived arguments
        derived_arguments = remove_keys(kwargs=derived_arguments, keys=supplied_arguments.keys())

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
        for key in ['instrument', 'side', 'amount', 'annual_rate', 'fee_percentage']:
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
        self.update(instrument=value)

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
    def period(self):
        key = 'period'
        if key in self._supplied_arguments:
            return self._supplied_arguments[key]
        elif key in self._derived_arguments:
            return self._derived_arguments[key]
        else:
            return None

    @period.setter
    def period(self, value):
        self.update(period=value)

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
        self.update(daily_rate=value)

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
        self.update(monthly_rate=value)

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
        self.update(annual_rate=value)

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
