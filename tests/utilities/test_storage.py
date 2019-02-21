from unittest import TestCase

from cryptoverse.utilities import Storage


class TestStorage(TestCase):

    def test___init__(self):
        self.assertRaises(TypeError, Storage, data=list())
        self.assertRaises(TypeError, Storage, data=str())
        self.assertRaises(TypeError, Storage, data=int())
        s = Storage(data=dict())
        self.assertIsInstance(s._data_store, dict)
        s = Storage(data=None)
        self.assertIsInstance(s._data_store, dict)

    def test___getitem__(self):
        data = {'foo': 'bar'}
        s = Storage(data=data)
        self.assertEqual(s['foo'], 'bar')

    def test___getattr__(self):
        data = {'foo': 'bar'}
        s = Storage(data=data)
        self.assertEqual(s.foo, 'bar')

    def test__setitem__(self):
        s = Storage()
        s['foo'] = 'bar'
        self.assertEqual(s['foo'], 'bar')

    def test_save(self):
        import tempfile
        file = tempfile.mkstemp()[1]
        s1 = Storage(file=file)
        self.assertRaises(KeyError, s1.__getitem__, 'foo')
        s1['foo'] = 'bar'
        s1.save()
        s2 = Storage(file=file)
        s2.load()
        self.assertEqual('bar', s2['foo'])

        from cryptoverse.domain import Instrument, Market, Order

        self.assertRaises(KeyError, s1.__getitem__, 'instrument')
        self.assertRaises(KeyError, s2.__getitem__, 'instrument')
        s1['instrument'] = Instrument('BTC')
        s1.save()
        self.assertEqual(s1.instrument, Instrument('BTC'))
        self.assertRaises(KeyError, s2.__getitem__, 'instrument')
        s2.load()
        self.assertEqual(s2.instrument, Instrument('BTC'))
        self.assertNotEqual(s2.instrument, Instrument('LTC'))

        self.assertRaises(KeyError, s1.__getitem__, 'market')
        self.assertRaises(KeyError, s2.__getitem__, 'market')
        s1['market'] = Market('BTC/USD')
        s1.save()
        self.assertEqual(s1.market, Market('BTC/USD'))
        self.assertRaises(KeyError, s2.__getitem__, 'market')
        s2.load()
        self.assertEqual(s2.market, Market('BTC/USD'))
        self.assertNotEqual(s2.market, Market('LTC/USD'))
