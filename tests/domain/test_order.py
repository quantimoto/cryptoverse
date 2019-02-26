from unittest import TestCase

from cryptoverse.domain import Order, Market


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
        self.assertIsInstance(Order._sanitize_kwargs(kwargs)['side'], Order.arg_types['side'])

        kwargs = {'foo': 'bar'}
        self.assertRaises(TypeError, Order._sanitize_kwargs, kwargs)

        kwargs = {'side': 'buy', 'foo': 'bar'}
        self.assertRaises(TypeError, Order._sanitize_kwargs, kwargs)

        kwargs = {'fee_instrument': 'USD'}
        from cryptoverse.domain import Instrument
        self.assertEqual(Order._sanitize_kwargs(kwargs), {'fee_instrument': Instrument(code='USD')})
        self.assertIsInstance(Order._sanitize_kwargs(kwargs)['fee_instrument'], Order.arg_types['fee_instrument'])

        kwargs = {'pair': 'BTC/USD'}
        from cryptoverse.domain import Pair
        self.assertEqual(Order._sanitize_kwargs(kwargs),
                         {'pair': Pair(base=Instrument(code='BTC'), quote=Instrument(code='USD'))})
        self.assertIsInstance(Order._sanitize_kwargs(kwargs)['pair'], Order.arg_types['pair'])

        kwargs = {'side': 'BuY'}
        self.assertEqual(Order._sanitize_kwargs(kwargs), {'side': 'buy'})

        kwargs = {'side': 'sElL'}
        self.assertEqual(Order._sanitize_kwargs(kwargs), {'side': 'sell'})

        kwargs = {'side': 'bid'}
        self.assertRaises(ValueError, Order._sanitize_kwargs, kwargs)

        kwargs = {'side': 'ask'}
        self.assertRaises(ValueError, Order._sanitize_kwargs, kwargs)

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
        self.assertIsInstance(Order._sanitize_kwargs(kwargs)['amount'], Order.arg_types['amount'])
        self.assertIsInstance(Order._sanitize_kwargs(kwargs)['price'], Order.arg_types['price'])
        self.assertIsInstance(Order._sanitize_kwargs(kwargs)['timestamp'], Order.arg_types['timestamp'])

    def test__replace_shortcuts(self):
        kwargs = {'account': None, 'exchange': None, 'pair': 'BTC/USD', 'side': 'buy', 'price': 'bid'}
        self.assertEqual({'price': None}, Order._replace_shortcuts(kwargs))

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

        market = Market('BTC/USD', limits={'price': {'significant digits': 5}})
        kwargs = {'price': 1.0234, 'market': market}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['price'], 1.0234)
        kwargs = {'price': 10.234, 'market': market}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['price'], 10.234)
        kwargs = {'price': 120.34, 'market': market}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['price'], 120.34)
        kwargs = {'price': 1234.5, 'market': market}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['price'], 1234.5)
        kwargs = {'price': 0.012345, 'market': market}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['price'], 0.012345)
        kwargs = {'price': 0.00012340, 'market': market}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['price'], 0.00012340)

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
        kwargs = {'net': 1998, 'fee_percentage': 0.001}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['gross'], 2000.0)

        # fees
        kwargs = {'gross': 2000, 'fee_percentage': 0.001}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['fees'], 2)
        kwargs = {'gross': 2000, 'net': 1998}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['fees'], 2)

        # fee_percentage
        kwargs = {'fees': 2, 'gross': 2000}
        self.assertEqual(Order._derive_missing_kwargs(kwargs)['fee_percentage'], 0.001)

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
        kwargs = {'pair': Pair('BTC', 'USD'), 'side': 'buy', 'amount': 2.0, 'price': 1000.0, 'fee_percentage': 0.001}
        self.assertEqual({'amount': 2.0,
                          'context': 'spot',
                          'fee_instrument': Instrument(code='BTC'),
                          'fee_percentage': 0.001,
                          'fees': 0.002,
                          'gross': 2.,
                          'hidden': False,
                          'input': 2000.,
                          'input_instrument': Instrument(code='USD'),
                          'net': 1.998,
                          'output': 1.998,
                          'output_instrument': Instrument(code='BTC'),
                          'pair': Pair(base=Instrument(code='BTC'),
                                       quote=Instrument(code='USD')),
                          'price': 1000.0,
                          'side': 'buy',
                          'total': 2000.0,
                          'type': 'limit'}, Order._derive_missing_kwargs(kwargs))

        # Calculations
        kwargs = {'amount': 1.1, 'price': 2.2}
        self.assertEqual(2.42, Order._derive_missing_kwargs(kwargs)['total'])
        self.assertIsInstance(Order._derive_missing_kwargs(kwargs)['total'], float)
        self.assertNotEqual(kwargs['amount'] * kwargs['price'], Order._derive_missing_kwargs(kwargs)['total'])

        kwargs = {'total': 2.42, 'price': 2.2}
        self.assertEqual(1.1, Order._derive_missing_kwargs(kwargs)['amount'])
        self.assertIsInstance(Order._derive_missing_kwargs(kwargs)['amount'], float)
        self.assertNotEqual(kwargs['total'] / kwargs['price'], Order._derive_missing_kwargs(kwargs)['amount'])

        kwargs = {'gross': 3.3, 'fees': 1.1}
        self.assertEqual(2.2, Order._derive_missing_kwargs(kwargs)['net'])
        self.assertIsInstance(Order._derive_missing_kwargs(kwargs)['net'], float)
        self.assertNotEqual(kwargs['gross'] - kwargs['fees'], Order._derive_missing_kwargs(kwargs)['net'])

        kwargs = {'net': 2.2, 'fees': 1.1}
        self.assertEqual(3.3, Order._derive_missing_kwargs(kwargs)['gross'])
        self.assertIsInstance(Order._derive_missing_kwargs(kwargs)['gross'], float)
        self.assertNotEqual(kwargs['net'] + kwargs['fees'], Order._derive_missing_kwargs(kwargs)['gross'])

    def test_update_arguments(self):
        order = Order()
        self.assertEqual(order._supplied_arguments, {})
        from cryptoverse.domain import Pair
        order.update_arguments('buy', Pair('BTC/USD'), amount=1)
        self.assertEqual(list(order._supplied_arguments.keys()), ['side', 'pair', 'amount'])
        self.assertRaises(ValueError, order.update_arguments, 'buy', side='sell')

        self.assertRaises(ValueError, order.update_arguments, 'foobar')

        self.assertRaises(TypeError, order.update_arguments, foo='bar')
        self.assertEqual(order._supplied_arguments['pair'], 'BTC/USD')
        self.assertIsInstance(order._supplied_arguments['pair'], Pair)
        order.update_arguments(pair=None)
        self.assertFalse('pair' in order._supplied_arguments.keys())
        self.assertEqual(list(order._supplied_arguments.keys()), ['side', 'amount'])

        order = Order('BTC/USD')
        self.assertEqual("Order(status='draft', pair=Pair('BTC/USD'), side=None, amount=None, price=None, "
                         "context='spot', type='limit', fee_percentage=None)",
                         repr(order))
        order = Order('BTC/USD', 'buy')
        self.assertEqual("Order(status='draft', pair=Pair('BTC/USD'), [32mside='buy'[0m, amount=None, price=None, "
                         "context='spot', type='limit', fee_percentage=None)",
                         repr(order))
        order = Order('BTC/USD', 'buy', fee_percentage=0.001)
        self.assertEqual("Order(status='draft', pair=Pair('BTC/USD'), [32mside='buy'[0m, amount=None, price=None, "
                         "context='spot', type='limit', fee_percentage=0.001)",
                         repr(order))
        order = Order('BTC/USD', 'buy', fee_percentage=0.001, input=2000)
        self.assertEqual("Order(status='draft', pair=Pair('BTC/USD'), [32mside='buy'[0m, amount=None, price=None, "
                         "context='spot', type='limit', fee_percentage=0.001)",
                         repr(order))
        order = Order('BTC/USD', 'buy', fee_percentage=0.001, input=2000, price=1000)
        self.assertEqual("Order(status='draft', pair=Pair('BTC/USD'), [32mside='buy'[0m, amount=2.0, price=1000.0, "
                         "context='spot', type='limit', fee_percentage=0.001)",
                         repr(order))
