from unittest import TestCase

from cryptoverse.domain import Market


class TestMarket(TestCase):

    def test___init__(self):
        m = Market('BTC/USD', 'margin', 'bitfinex', {'price': {'precision': 5}}, {'maker': 0.1})
        self.assertEqual(m.base, 'BTC')
        self.assertEqual(m.quote, 'USD')
        self.assertEqual(m.context, 'margin')
        self.assertEqual(m.exchange, 'bitfinex')
        self.assertEqual(m.limits, {'amount': {'max': None,
                                               'min': None,
                                               'precision': None,
                                               'significant digits': None},
                                    'price': {'max': None,
                                              'min': None,
                                              'precision': 5,
                                              'significant digits': None},
                                    'total': {'max': None,
                                              'min': None,
                                              'precision': None,
                                              'significant digits': None}})
        self.assertEqual(m.fees, {'maker': 0.1, 'taker': None})

    def test_as_dict(self):
        m = Market('BTC/USD')
        from cryptoverse.domain import Pair, Instrument
        self.assertEqual(m.as_dict(),
                         {'context': 'spot', 'symbol': Pair(base=Instrument(code='BTC'), quote=Instrument(code='USD'))})

    def test_set_symbol(self):
        from cryptoverse.domain import Pair, Instrument

        m = Market('BTC/USD')
        self.assertEqual(m.base, 'BTC')
        self.assertEqual(m.quote, 'USD')
        self.assertEqual(m.symbol.base, m.base)
        self.assertEqual(m.symbol.quote, m.quote)

        m = Market(Pair('BTC/USD'))
        self.assertEqual(m.base, 'BTC')
        self.assertEqual(m.quote, 'USD')
        self.assertEqual(m.symbol, 'BTC/USD')
        self.assertEqual(m.symbol, Pair('BTC/USD'))

        m = Market(Pair('BTC', 'USD'))
        self.assertEqual(m.base, 'BTC')
        self.assertEqual(m.quote, 'USD')
        self.assertEqual(m.symbol, 'BTC/USD')
        self.assertEqual(m.symbol, Pair('BTC/USD'))

        m = Market(Instrument('BTC'))
        self.assertEqual(m.base, None)
        self.assertEqual(m.quote, None)
        self.assertEqual(m.symbol, 'BTC')

    def test_set_context(self):
        m = Market('BTC/USD')
        self.assertEqual(m.context, 'spot')
        m.set_context('margin')
        self.assertEqual(m.context, 'margin')
        self.assertRaises(ValueError, m.set_context, context='someting-nonexisting')

    def test_set_order_limits(self):
        m = Market('BTC/USD')
        self.assertEqual(m.limits, {'amount': {'max': None,
                                               'min': None,
                                               'precision': None,
                                               'significant digits': None},
                                    'price': {'max': None,
                                              'min': None,
                                              'precision': None,
                                              'significant digits': None},
                                    'total': {'max': None,
                                              'min': None,
                                              'precision': None,
                                              'significant digits': None}})
        m.set_limits({'price': {'precision': 5}})
        self.assertEqual(m.limits, {'amount': {'max': None,
                                               'min': None,
                                               'precision': None,
                                               'significant digits': None},
                                    'price': {'max': None,
                                              'min': None,
                                              'precision': 5,
                                              'significant digits': None},
                                    'total': {'max': None,
                                              'min': None,
                                              'precision': None,
                                              'significant digits': None}})
        m.set_limits({'amount': {'min': 20, 'max': 2000}})
        self.assertEqual(m.limits, {'amount': {'max': 2000,
                                               'min': 20,
                                               'precision': None,
                                               'significant digits': None},
                                    'price': {'max': None,
                                              'min': None,
                                              'precision': 5,
                                              'significant digits': None},
                                    'total': {'max': None,
                                              'min': None,
                                              'precision': None,
                                              'significant digits': None}})

    def test_set_fees(self):
        m = Market('BTC/USD')
        self.assertEqual(m.fees, {'maker': None, 'taker': None})
        m.set_fees({'maker': 0.1})
        self.assertEqual(m.fees, {'maker': 0.1, 'taker': None})
        m.set_fees({'taker': 0.2})
        self.assertEqual(m.fees, {'maker': 0.1, 'taker': 0.2})

    def test___eq__(self):
        m1 = Market('BTC/USD')
        m2 = Market('BTC/USD')
        m3 = Market('LTC/USD')
        m4 = Market('LTC/BTC')
        self.assertEqual(m1, m2)
        self.assertNotEqual(m1, m3)
        self.assertNotEqual(m1, m4)
