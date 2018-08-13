from unittest import TestCase

from cryptoverse.base.interface import ExchangeInterface
from cryptoverse.domain import Exchange, Exchanges

interface1 = ExchangeInterface()
interface1.slug = 'dummy'
exchange1 = Exchange(interface=interface1)

interface2 = ExchangeInterface()
interface2.slug = 'foo'
exchange2 = Exchange(interface=interface2)

interface3 = ExchangeInterface()
interface3.slug = 'bar'
exchange3 = Exchange(interface=interface3)

exchanges = Exchanges()
exchanges.append(exchange1)
exchanges.append(exchange2)
exchanges.append(exchange3)


class TestExchanges(TestCase):
    def test___getattr__(self):
        self.assertEqual(exchanges.dummy, exchange1)
        self.assertNotEqual(exchanges.dummy, exchange2)
        self.assertEqual(exchanges.foo, exchange2)
        self.assertNotEqual(exchanges.foo, exchange1)
        self.assertEqual(exchanges.bar, exchange3)
        self.assertNotEqual(exchanges.bar, exchange1)
        self.assertRaises(AttributeError, exchanges.__getattr__, 'nonexisting')

    def test___getitem__(self):
        self.assertEqual(exchanges['dummy'], exchange1)
        self.assertNotEqual(exchanges['dummy'], exchange2)
        self.assertEqual(exchanges['foo'], exchange2)
        self.assertNotEqual(exchanges['foo'], exchange1)
        self.assertEqual(exchanges['bar'], exchange3)
        self.assertNotEqual(exchanges['bar'], exchange1)
        self.assertRaises(KeyError, exchanges.__getitem__, 'nonexisting')

    def test_get_slugs(self):
        self.assertEqual(exchanges.get_slugs(), ['dummy', 'foo', 'bar'])

    def test_as_dict(self):
        self.assertEqual(list(exchanges.as_dict().keys()), ['dummy', 'foo', 'bar'])

    def test_as_list(self):
        self.assertEqual(exchanges.as_list(), [exchange1, exchange2, exchange3])
