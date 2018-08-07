from unittest import TestCase

from cryptoverse.domain import Market


class TestMarket(TestCase):

    def test___init__(self):
        m = Market('BTC', 'USD', 'margin', 'bitfinex', {'price': {'precision': 5}}, {'maker': 0.1})
        self.assertEqual(m.base, 'BTC')
        self.assertEqual(m.quote, 'USD')
        self.assertEqual(m.context, 'margin')
        self.assertEqual(m.exchange, 'bitfinex')
        self.assertEqual(m.order_limits, {'amount': {'max': None, 'min': None, 'precision': None},
                                          'price': {'max': None, 'min': None, 'precision': 5},
                                          'total': {'max': None, 'min': None, 'precision': None}})
        self.assertEqual(m.fees, {'maker': 0.1, 'taker': None})

    def test_to_dict(self):
        m = Market('BTC', 'USD')
        self.assertEqual(m.to_dict(), {'base': 'BTC',
                                       'context': 'spot',
                                       'fees': {'maker': None, 'taker': None},
                                       'order_limits': {'amount': {'max': None, 'min': None, 'precision': None},
                                                        'price': {'max': None, 'min': None, 'precision': None},
                                                        'total': {'max': None, 'min': None, 'precision': None}},
                                       'quote': 'USD'})

    def test_set_base(self):
        m = Market('BTC', 'USD')
        self.assertEqual(m.base, 'BTC')
        m.set_base('ETH')
        self.assertEqual(m.base, 'ETH')

    def test_set_quote(self):
        m = Market('BTC', 'USD')
        self.assertEqual(m.quote, 'USD')
        m.set_quote('EUR')
        self.assertEqual(m.quote, 'EUR')

    def test_set_context(self):
        m = Market('BTC', 'USD')
        self.assertEqual(m.context, 'spot')
        m.set_context('margin')
        self.assertEqual(m.context, 'margin')
        self.assertRaises(ValueError, m.set_context, context='someting-nonexisting')

    def test_set_order_limits(self):
        m = Market('BTC', 'USD')
        self.assertEqual(m.order_limits, {'amount': {'max': None, 'min': None, 'precision': None},
                                          'price': {'max': None, 'min': None, 'precision': None},
                                          'total': {'max': None, 'min': None, 'precision': None}})
        m.set_order_limits({'price': {'precision': 5}})
        self.assertEqual(m.order_limits, {'amount': {'max': None, 'min': None, 'precision': None},
                                          'price': {'max': None, 'min': None, 'precision': 5},
                                          'total': {'max': None, 'min': None, 'precision': None}})
        m.set_order_limits({'amount': {'min': 20, 'max': 2000}})
        self.assertEqual(m.order_limits, {'amount': {'max': 2000, 'min': 20, 'precision': None},
                                          'price': {'max': None, 'min': None, 'precision': 5},
                                          'total': {'max': None, 'min': None, 'precision': None}})

    def test_set_fees(self):
        m = Market('BTC', 'USD')
        print(m.fees)
        self.assertEqual(m.fees, {'maker': None, 'taker': None})
        m.set_fees({'maker': 0.1})
        self.assertEqual(m.fees, {'maker': 0.1, 'taker': None})
        m.set_fees({'taker': 0.2})
        self.assertEqual(m.fees, {'maker': 0.1, 'taker': 0.2})
