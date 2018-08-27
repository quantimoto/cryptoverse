from unittest import TestCase

from cryptoverse.domain import Order


class TestOrder(TestCase):

    def test__get_kw_for_arg(self):
        from cryptoverse.domain import Pair
        arg = Pair('BTC', 'USD')
        self.assertEqual(Order._get_kw_for_arg(arg), 'pair')

        from cryptoverse.domain import Market
        arg = Market(Pair('BTC', 'USD'))
        self.assertEqual(Order._get_kw_for_arg(arg), 'market')

        from cryptoverse.base.interface import ExchangeInterface
        from cryptoverse.domain import Exchange
        arg = Exchange(interface=ExchangeInterface())
        self.assertEqual(Order._get_kw_for_arg(arg), 'exchange')

        from cryptoverse.domain import Account
        arg = Account()
        self.assertEqual(Order._get_kw_for_arg(arg), 'account')

        arg = 'buy'
        self.assertEqual(Order._get_kw_for_arg(arg), 'side')

        arg = 'BUY'
        self.assertEqual(Order._get_kw_for_arg(arg), 'side')

        arg = 'sell'
        self.assertEqual(Order._get_kw_for_arg(arg), 'side')

        arg = 'SELL'
        self.assertEqual(Order._get_kw_for_arg(arg), 'side')

    def test__sanitize_kwargs(self):
        kwargs = {}
        self.assertEqual(Order._sanitize_kwargs(kwargs), {})

        kwargs = {'side': 'buy'}
        self.assertEqual(Order._sanitize_kwargs(kwargs), {'side': 'buy'})
        self.assertIsInstance(Order._sanitize_kwargs(kwargs)['side'], Order._arg_types['side'])

        kwargs = {'foo': 'bar'}
        self.assertRaises(TypeError, Order._sanitize_kwargs, kwargs)

        kwargs = {'side': 'buy', 'foo': 'bar'}
        self.assertRaises(TypeError, Order._sanitize_kwargs, kwargs)

        kwargs = {'fee_instrument': 'USD'}
        from cryptoverse.domain import Instrument
        self.assertEqual(Order._sanitize_kwargs(kwargs), {'fee_instrument': Instrument(code='USD')})
        self.assertIsInstance(Order._sanitize_kwargs(kwargs)['fee_instrument'], Order._arg_types['fee_instrument'])

        kwargs = {'pair': 'BTC/USD'}
        from cryptoverse.domain import Pair
        self.assertEqual(Order._sanitize_kwargs(kwargs),
                         {'pair': Pair(base=Instrument(code='BTC'), quote=Instrument(code='USD'))})
        self.assertIsInstance(Order._sanitize_kwargs(kwargs)['pair'], Order._arg_types['pair'])

        kwargs = {'side': 'BuY'}
        self.assertEqual(Order._sanitize_kwargs(kwargs), {'side': 'buy'})

        kwargs = {'side': 'sElL'}
        self.assertEqual(Order._sanitize_kwargs(kwargs), {'side': 'sell'})

        kwargs = {'side': 'bid'}
        self.assertEqual(Order._sanitize_kwargs(kwargs), {'side': 'buy'})

        kwargs = {'side': 'ask'}
        self.assertEqual(Order._sanitize_kwargs(kwargs), {'side': 'sell'})

        kwargs = {'side': 'nonsense'}
        self.assertRaises(ValueError, Order._sanitize_kwargs, kwargs)

        kwargs = {'pair': Instrument('USD')}
        self.assertRaises(ValueError, Order._sanitize_kwargs, kwargs)

        from cryptoverse.domain import Market
        kwargs = {'pair': Market('BTC/USD')}
        self.assertEqual(Order._sanitize_kwargs(kwargs), {'pair': 'BTC/USD'})

        kwargs = {'pair': None, 'amount': 1, 'side': 'buy'}
        self.assertEqual(Order._sanitize_kwargs(kwargs), {'pair': None, 'amount': 1, 'side': 'buy'})

        kwargs = {'account': None, 'exchange': None}
        self.assertEqual(Order._sanitize_kwargs(kwargs), {'account': None, 'exchange': None})

        from cryptoverse.domain import Account
        from cryptoverse.domain import Exchange
        from cryptoverse.base.interface import ExchangeInterface
        kwargs = {'account': Account(), 'exchange': Exchange(interface=ExchangeInterface())}
        self.assertIsInstance(Order._sanitize_kwargs(kwargs)['account'], Account)
        self.assertIsInstance(Order._sanitize_kwargs(kwargs)['exchange'], Exchange)
        self.assertEqual(Order._sanitize_kwargs(kwargs),
                         {'account': Account(), 'exchange': Exchange(interface=ExchangeInterface())})

        kwargs = {'amount': 1, 'price': '2', 'timestamp': 1234567890}
        self.assertEqual(Order._sanitize_kwargs(kwargs), {'amount': 1.0, 'price': 2.0, 'timestamp': 1234567890.0})
        self.assertIsInstance(Order._sanitize_kwargs(kwargs)['amount'], Order._arg_types['amount'])
        self.assertIsInstance(Order._sanitize_kwargs(kwargs)['price'], Order._arg_types['price'])
        self.assertIsInstance(Order._sanitize_kwargs(kwargs)['timestamp'], Order._arg_types['timestamp'])

    def test__derive_missing_kwargs(self):
        # amount
        kwargs = {'total': 2000, 'price': 1000}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['amount'], 2.0)
        kwargs = {'side': 'buy', 'gross': 2}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['amount'], 2.0)
        kwargs = {'side': 'sell', 'input': 2}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['amount'], 2.0)

        # price
        kwargs = {'total': 2000, 'amount': 2}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['price'], 1000.0)

        # total
        kwargs = {'amount': 2, 'price': 1000}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['total'], 2000.0)
        kwargs = {'side': 'sell', 'gross': 2000}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['total'], 2000.0)
        kwargs = {'side': 'buy', 'input': 2000}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['total'], 2000.0)

        # input
        kwargs = {'side': 'buy', 'total': 2000}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['input'], 2000.0)
        kwargs = {'side': 'sell', 'amount': 2}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['input'], 2.0)

        # gross
        kwargs = {'amount': 2, 'side': 'buy'}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['gross'], 2.0)
        kwargs = {'total': 2000, 'side': 'sell'}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['gross'], 2000.0)
        kwargs = {'net': 1998, 'fees': 2}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['gross'], 2000.0)
        kwargs = {'net': 1998, 'fee_percentage': 0.1}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['gross'], 2000.0)

        # fees
        kwargs = {'gross': 2000, 'fee_percentage': 0.1}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['fees'], 2)
        kwargs = {'gross': 2000, 'net': 1998}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['fees'], 2)

        # fee_percentage
        kwargs = {'fees': 2, 'gross': 2000}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['fee_percentage'], 0.1)

        # net
        kwargs = {'output': 1998}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['net'], 1998)
        kwargs = {'gross': 2000, 'fees': 2}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['net'], 1998)

        # output
        kwargs = {'net': 1998}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['output'], 1998)

        # side
        from cryptoverse.domain import Pair
        from cryptoverse.domain import Instrument
        kwargs = {'input_instrument': Instrument('BTC'), 'pair': Pair('BTC', 'USD')}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['side'], 'sell')
        kwargs = {'input_instrument': Instrument('BTC'), 'pair': Pair('BTC', 'USD')}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['side'], 'sell')

        # pair
        kwargs = {'input_instrument': 'BTC', 'output_instrument': 'USD', 'side': 'sell'}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['pair'], Pair('BTC/USD'))
        kwargs = {'input_instrument': 'USD', 'output_instrument': 'BTC', 'side': 'buy'}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['pair'], Pair('BTC/USD'))

        # fee_instrument
        kwargs = {'pair': Pair('BTC', 'USD'), 'side': 'buy'}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['fee_instrument'], 'BTC')
        kwargs = {'pair': Pair('BTC', 'USD'), 'side': 'sell'}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['fee_instrument'], 'USD')

        # input_instrument
        kwargs = {'pair': Pair('BTC', 'USD'), 'side': 'buy'}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['input_instrument'], 'USD')
        kwargs = {'pair': Pair('BTC', 'USD'), 'side': 'sell'}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['input_instrument'], 'BTC')

        # output_instrument
        kwargs = {'pair': Pair('BTC', 'USD'), 'side': 'buy'}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['output_instrument'], 'BTC')
        kwargs = {'pair': Pair('BTC', 'USD'), 'side': 'sell'}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['output_instrument'], 'USD')

        # General testing
        kwargs = {'pair': Pair('BTC', 'USD'), 'side': 'buy', 'amount': 2.0, 'price': 1000.0, 'fee_percentage': 0.1}
        self.assertEqual(Order._derive_missing_kwargs(kwargs), {'fee_instrument': Instrument(code='BTC'),
                                                                'fees': 0.002,
                                                                'gross': 2,
                                                                'input': 2000,
                                                                'input_instrument': Instrument(code='USD'),
                                                                'net': 1.998,
                                                                'output': 1.998,
                                                                'output_instrument': Instrument(code='BTC'),
                                                                'total': 2000,
                                                                'type': 'limit'})

    def test_update(self):
        order = Order()
        self.assertEqual(order._supplied_arguments, {})
        from cryptoverse.domain import Pair
        order.update('buy', Pair('BTC/USD'), amount=1)
        self.assertEqual(list(order._supplied_arguments.keys()), ['side', 'pair', 'amount'])
        self.assertRaises(ValueError, order.update, 'buy', side='sell')

        self.assertRaises(ValueError, order.update, 'foobar')

        self.assertRaises(TypeError, order.update, foo='bar')
        self.assertEqual(order._supplied_arguments['pair'], 'BTC/USD')
        self.assertIsInstance(order._supplied_arguments['pair'], Pair)
        order.update(pair=None)
        self.assertFalse('pair' in order._supplied_arguments.keys())
        self.assertEqual(list(order._supplied_arguments.keys()), ['side', 'amount'])

        order = Order('BTC/USD')
        self.assertEqual(repr(order),
                         "Order(pair=Pair(base=Instrument(code='BTC'), quote=Instrument(code='USD')), side=None, "
                         "amount=None, price=None, fee_percentage=None)")
        order = Order('BTC/USD', 'buy')
        self.assertEqual(repr(order),
                         "Order(pair=Pair(base=Instrument(code='BTC'), quote=Instrument(code='USD')), side='buy', "
                         "amount=None, price=None, fee_percentage=None)")
        order = Order('BTC/USD', 'buy', fee_percentage=0.1)
        self.assertEqual(repr(order),
                         "Order(pair=Pair(base=Instrument(code='BTC'), quote=Instrument(code='USD')), side='buy', "
                         "amount=None, price=None, fee_percentage=0.1)")
        order = Order('BTC/USD', 'buy', fee_percentage=0.1, input=2000)
        self.assertEqual(repr(order),
                         "Order(pair=Pair(base=Instrument(code='BTC'), quote=Instrument(code='USD')), side='buy', "
                         "amount=None, price=None, fee_percentage=0.1)")
        order = Order('BTC/USD', 'buy', fee_percentage=0.1, input=2000, price=1000)
        self.assertEqual(repr(order),
                         "Order(pair=Pair(base=Instrument(code='BTC'), quote=Instrument(code='USD')), side='buy', "
                         "amount=2.0, price=1000.0, fee_percentage=0.1)")
