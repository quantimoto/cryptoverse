from unittest import TestCase

from cryptoverse.domain import Instruments, Pairs, Markets
from cryptoverse.exchanges import BitfinexInterface

interface = BitfinexInterface()


class TestBitfinexInterface(TestCase):

    def test_get_spot_instruments(self):
        results = interface.get_spot_instruments()
        self.assertIsInstance(results, Instruments)

    def test_get_margin_instruments(self):
        results = interface.get_margin_instruments()
        self.assertIsInstance(results, Instruments)

    def test_get_funding_instruments(self):
        results = interface.get_funding_instruments()
        self.assertIsInstance(results, Instruments)

    def test_get_all_instruments(self):
        results = interface.get_all_instruments()
        self.assertIsInstance(results, Instruments)

    def test_get_spot_pairs(self):
        results = interface.get_spot_pairs()
        self.assertIsInstance(results, Pairs)

    def test_get_margin_pairs(self):
        results = interface.get_margin_pairs()
        self.assertIsInstance(results, Pairs)

    def test_get_all_pairs(self):
        results = interface.get_all_pairs()
        self.assertIsInstance(results, Pairs)

    def test_get_spot_markets(self):
        results = interface.get_spot_markets()
        self.assertIsInstance(results, Markets)

    def test_get_margin_markets(self):
        results = interface.get_margin_markets()
        self.assertIsInstance(results, Markets)

    def test_get_funding_markets(self):
        results = interface.get_funding_markets()
        self.assertIsInstance(results, Markets)

    def test_get_all_markets(self):
        results = interface.get_all_markets()
        self.assertIsInstance(results, Markets)
