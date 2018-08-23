from unittest import TestCase

from cryptoverse.domain import Market, Markets, Instrument, Instruments

m1 = Market('BTC', 'USD')
m2 = Market('BTC', 'EUR')
m3 = Market('LTC', 'USD')
m4 = Market('ETH', 'USD')
m = Markets([m1, m2, m3, m4])

i1 = Instrument('BTC')
i2 = Instrument('LTC')
i3 = Instrument('USD')
i4 = Instrument('EUR')
i5 = Instrument('ETH')
i6 = Instrument('BTC')
i = Instruments([i1, i2, i3, i4, i5, i6])


class TestObjectList(TestCase):
    def test_as_list(self):
        r = m.as_list()
        self.assertIsInstance(r, list)

    def test_copy(self):
        r = m.copy()
        del r[1]
        self.assertNotEqual(r, m)

    def test_first(self):
        self.assertEqual(m[0], m1)

    def test_last(self):
        self.assertEqual(m[-1], m4)

    def test_find(self):
        r = m.find(base='BTC')
        self.assertIsInstance(r, Markets)
        self.assertEqual(len(r), 2)
        self.assertEqual((r[0], r[1]), (m1, m2))

        r = m.find(base='LTC')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], m3)

        r = m.find(base='BTC', quote='USD')
        self.assertEqual(r[0], m1)

        r = m.find(base='BTC', quote='EUR')
        self.assertEqual(r[0], m2)

        r = m.find(base='LTC', quote='USD')
        self.assertEqual(r[0], m3)

        r = m.find(base='LTC', quote='BTC')
        self.assertEqual(len(r), 0)

        self.assertRaises(AttributeError, m.find, base='BTC', nonsense='nonsense')

    def test_get_values(self):
        r = m.get_values('base')
        self.assertEqual(r, ['BTC', 'BTC', 'LTC', 'ETH'])
        self.assertEqual(r.as_list(), [m1.base, m2.base, m3.base, m4.base])

        r = m.get_values('quote')
        self.assertEqual(r, ['USD', 'EUR', 'USD', 'USD'])
        self.assertEqual(r.as_list(), [m1.quote, m2.quote, m3.quote, m4.quote])

    def test_get_unique_values(self):
        r = m.get_unique_values('base')
        self.assertEqual(r, ['BTC', 'LTC', 'ETH'])
        self.assertEqual(r.as_list(), [m1.base, m3.base, m4.base])

        r = m.get_unique_values('quote')
        self.assertEqual(r, ['USD', 'EUR'])
        self.assertEqual(r.as_list(), [m1.quote, m2.quote])

    def test_get_unique(self):
        self.assertEqual(i, ['BTC', 'LTC', 'USD', 'EUR', 'ETH', 'BTC'])
        r = i.get_unique()
        self.assertEqual(r, ['BTC', 'LTC', 'USD', 'EUR', 'ETH'])
