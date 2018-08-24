from unittest import TestCase

from cryptoverse.domain import Market, Pair, Markets, Instrument

m1 = Market(Pair('BTC/USD'))
m2 = Market(Pair('LTC/USD'))
m3 = Market(Pair('LTC/BTC'))
m4 = Market(Instrument('BTC'))
m5 = Market(Instrument('USD'))
m = Markets([m1, m2, m3, m4, m5])


class TestMarkets(TestCase):
    def test__attr__(self):
        self.assertEqual(m.BTC_USD, m1)
        self.assertNotEqual(m.BTC_USD, m2)
        self.assertNotEqual(m.BTC_USD, m3)
        self.assertNotEqual(m.BTC_USD, m4)
        self.assertNotEqual(m.BTC_USD, m5)
        self.assertEqual(m.LTC_USD, m2)
        self.assertEqual(m.LTC_BTC, m3)
        self.assertEqual(m.BTC, m4)
        self.assertEqual(m.USD, m5)

    def test___getitem__(self):
        self.assertEqual(m['BTC/USD'], m1)
        self.assertEqual(m['BTC_USD'], m1)
        self.assertEqual(m['BTC-USD'], m1)
        self.assertNotEqual(m['BTC/USD'], m2)
        self.assertNotEqual(m['BTC/USD'], m3)
        self.assertNotEqual(m['BTC/USD'], m4)
        self.assertNotEqual(m['BTC/USD'], m5)
        self.assertEqual(m['LTC/USD'], m2)
        self.assertEqual(m['LTC/BTC'], m3)
        self.assertEqual(m['BTC'], m4)
        self.assertEqual(m['USD'], m5)
