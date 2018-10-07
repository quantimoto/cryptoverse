from unittest import TestCase

from cryptoverse.domain import Pair, Pairs, Instrument, Instruments

p1 = Pair('BTC', 'USD')
p2 = Pair('BTC', 'EUR')
p3 = Pair('LTC', 'USD')
p4 = Pair('ETH', 'USD')
p = Pairs([p1, p2, p3, p4])

i1 = Instrument('BTC')
i2 = Instrument('LTC')
i3 = Instrument('USD')
i4 = Instrument('EUR')
i5 = Instrument('ETH')
i6 = Instrument('BTC')
i = Instruments([i1, i2, i3, i4, i5, i6])


class TestObjectList(TestCase):
    def test_as_list(self):
        r = p.as_list()
        self.assertIsInstance(r, list)

    def test_copy(self):
        r = p.copy()
        del r[1]
        self.assertNotEqual(r, p)

    def test_first(self):
        self.assertEqual(p[0], p1)

    def test_last(self):
        self.assertEqual(p[-1], p4)

    def test_find(self):
        r = p.find(base='BTC')
        self.assertIsInstance(r, Pairs)
        self.assertEqual(len(r), 2)
        self.assertEqual((r[0], r[1]), (p1, p2))

        r = p.find(base='LTC')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], p3)

        r = p.find(base='BTC', quote='USD')
        self.assertEqual(r[0], p1)

        r = p.find(base='BTC', quote='EUR')
        self.assertEqual(r[0], p2)

        r = p.find(base='LTC', quote='USD')
        self.assertEqual(r[0], p3)

        r = p.find(base='LTC', quote='BTC')
        self.assertEqual(len(r), 0)

        self.assertRaises(AttributeError, p.find, base='BTC', nonsense='nonsense')

    def test_get_values(self):
        r = p.get_values('base')
        self.assertEqual(r, ['BTC', 'BTC', 'LTC', 'ETH'])
        self.assertEqual(r.as_list(), [p1.base, p2.base, p3.base, p4.base])

        r = p.get_values('quote')
        self.assertEqual(r, ['USD', 'EUR', 'USD', 'USD'])
        self.assertEqual(r.as_list(), [p1.quote, p2.quote, p3.quote, p4.quote])

    def test_get_unique_values(self):
        r = p.get_unique_values('base')
        self.assertEqual(r, ['BTC', 'LTC', 'ETH'])
        self.assertEqual(r.as_list(), [p1.base, p3.base, p4.base])

        r = p.get_unique_values('quote')
        self.assertEqual(r, ['USD', 'EUR'])
        self.assertEqual(r.as_list(), [p1.quote, p2.quote])

    def test_get_unique(self):
        self.assertEqual(i, ['BTC', 'LTC', 'USD', 'EUR', 'ETH', 'BTC'])
        r = i.get_unique()
        self.assertEqual(r, ['BTC', 'LTC', 'USD', 'EUR', 'ETH'])

    def test_sorted_by(self):
        self.assertEqual(Instruments([Instrument('BTC'),
                                      Instrument('BTC'),
                                      Instrument('ETH'),
                                      Instrument('EUR'),
                                      Instrument('LTC'),
                                      Instrument('USD')]), i.sorted_by(key='code', reverse=False))
        self.assertEqual(Instruments([Instrument('USD'),
                                      Instrument('LTC'),
                                      Instrument('EUR'),
                                      Instrument('ETH'),
                                      Instrument('BTC'),
                                      Instrument('BTC')]), i.sorted_by(key='code', reverse=True))
        self.assertEqual(Instruments([Pair('BTC/USD'),
                                      Pair('BTC/EUR'),
                                      Pair('ETH/USD'),
                                      Pair('LTC/USD')]), p.sorted_by(key='base', reverse=False))
        self.assertEqual(Instruments([Pair('LTC/USD'),
                                      Pair('ETH/USD'),
                                      Pair('BTC/USD'),
                                      Pair('BTC/EUR')]), p.sorted_by(key='base', reverse=True))
        self.assertEqual(Instruments([Pair('BTC/EUR'),
                                      Pair('BTC/USD'),
                                      Pair('LTC/USD'),
                                      Pair('ETH/USD')]), p.sorted_by(key='quote', reverse=False))
        self.assertEqual(Instruments([Pair('BTC/USD'),
                                      Pair('LTC/USD'),
                                      Pair('ETH/USD'),
                                      Pair('BTC/EUR')]), p.sorted_by(key='quote', reverse=True))
