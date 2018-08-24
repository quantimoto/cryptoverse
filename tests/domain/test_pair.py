from unittest import TestCase

from cryptoverse.domain import Pair, Instrument


class TestPair(TestCase):

    def test___init__(self):
        base, quote = 'BTC', 'USD'
        p1 = Pair(base, quote)
        self.assertIsInstance(p1.base, Instrument)
        self.assertIsInstance(p1.quote, Instrument)
        self.assertEqual(p1.base.code, base)
        self.assertEqual(p1.quote.code, quote)

        p2 = Pair(base=base, quote=quote)
        self.assertEqual(p2.base.code, base)
        self.assertEqual(p2.quote.code, quote)

        p3 = Pair(base, quote=quote)
        self.assertEqual(p3.base.code, base)
        self.assertEqual(p3.quote.code, quote)

        p4 = Pair(quote, base=base)
        self.assertEqual(p4.base.code, base)
        self.assertEqual(p4.quote.code, quote)

        p5 = Pair('BTC/USD')
        self.assertEqual(p5.base.code, 'BTC')
        self.assertEqual(p5.quote.code, 'USD')

        self.assertRaises(ValueError, Pair, base='BTC', quote='BTC')

    def test__set_base(self):
        base1 = 'BTC'
        base2 = Instrument('BTC')
        p = Pair(base1, 'USD')
        self.assertIsInstance(p.base, Instrument)
        self.assertNotIsInstance(p.base, type(base1))
        p = Pair(base2, 'USD')
        self.assertIsInstance(p.base, Instrument)
        self.assertIsInstance(p.base, type(base2))

    def test__set_quote(self):
        quote1 = 'USD'
        quote2 = Instrument('USD')
        p = Pair('BTC', quote1)
        self.assertNotIsInstance(p.quote, type(quote1))
        self.assertIsInstance(p.quote, Instrument)
        p = Pair('BTC', quote2)
        self.assertIsInstance(p.quote, type(quote2))
        self.assertIsInstance(p.quote, Instrument)

    def test__split_string(self):
        base, quote = Pair._split_string('BTC/USD')
        self.assertEqual(base, 'BTC')
        self.assertEqual(quote, 'USD')
        base, quote = Pair._split_string('BTC_USD')
        self.assertEqual(base, 'BTC')
        self.assertEqual(quote, 'USD')
        base, quote = Pair._split_string('BTC-USD')
        self.assertEqual(base, 'BTC')
        self.assertEqual(quote, 'USD')

        self.assertRaises(ValueError, Pair._split_string, 'BTC+USD')
        base, quote = Pair._split_string('BTC+USD', separator='+')
        self.assertEqual(base, 'BTC')
        self.assertEqual(quote, 'USD')

    def test_from_string(self):
        p = Pair.from_string('BTC/USD')
        self.assertIsInstance(p.base, Instrument)
        self.assertEqual(p.base.code, 'BTC')
        self.assertIsInstance(p.quote, Instrument)
        self.assertEqual(p.quote.code, 'USD')
        p = Pair.from_string('BTC_USD')
        self.assertIsInstance(p.base, Instrument)
        self.assertEqual(p.base.code, 'BTC')
        self.assertIsInstance(p.quote, Instrument)
        self.assertEqual(p.quote.code, 'USD')
        p = Pair.from_string('BTC-USD')
        self.assertIsInstance(p.base, Instrument)
        self.assertEqual(p.base.code, 'BTC')
        self.assertIsInstance(p.quote, Instrument)
        self.assertEqual(p.quote.code, 'USD')

        self.assertRaises(ValueError, Pair.from_string, 'BTC+USD')
        p = Pair.from_string('BTC+USD', separator='+')
        self.assertIsInstance(p.base, Instrument)
        self.assertEqual(p.base.code, 'BTC')
        self.assertIsInstance(p.quote, Instrument)
        self.assertEqual(p.quote.code, 'USD')

    def test___eq__(self):
        pair = Pair('BTC', 'USD')

        self.assertEqual(pair, Pair('BTC/USD'))
        self.assertNotEqual(pair, Pair('BTC/EUR'))
        self.assertNotEqual(pair, Pair('LTC/USD'))
        self.assertNotEqual(pair, Pair('LTC/EUR'))
        self.assertEqual(pair, 'BTC/USD')
        self.assertEqual(pair, Pair('USD', 'BTC'))
        self.assertEqual(pair, 'USD/BTC')
        self.assertNotEqual(pair, 'LTC/USD')
        self.assertNotEqual(pair, 'EUR/LTC')
        self.assertNotEqual(pair, 'BTC/BTC')
        self.assertNotEqual(pair, 'USD/USD')

    def test___hash__(self):
        pair = Pair('BTC', 'USD')
        hash1 = hash(pair)

        pair.set_base('BTC')
        hash2 = hash(pair)
        self.assertEqual(hash1, hash2)

        pair.set_base('LTC')
        hash3 = hash(pair)
        self.assertNotEqual(hash1, hash3)

        pair.set_base('BTC')
        hash4 = hash(pair)
        self.assertEqual(hash1, hash4)

        pair2 = Pair('LTC', 'EUR')
        hash5 = hash(pair2)
        self.assertNotEqual(hash1, hash5)
        pair2.set_base('BTC')
        pair2.set_quote('USD')
        hash6 = hash(pair2)
        self.assertEqual(hash1, hash6)

    def test_as_str(self):
        p = Pair('BTC', 'USD')
        self.assertEqual(p.as_str(), 'BTC/USD')
        self.assertIsInstance(p.as_str(), str)

    def test_as_dict(self):
        p = Pair('BTC', 'USD')
        self.assertEqual(p.as_dict(), {'base': Instrument(code='BTC'), 'quote': Instrument(code='USD')})
        self.assertIsInstance(p.as_dict(), dict)
