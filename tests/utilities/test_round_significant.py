from unittest import TestCase

from cryptoverse.utilities import round_significant


class TestRoundSignificant(TestCase):
    def test_round_significant(self):
        self.assertEqual(round_significant(1987.654321, 5), 1987.7)
        self.assertEqual(round_significant(198.7654321, 5), 198.77)
        self.assertEqual(round_significant(19.87654321, 5), 19.877)
        self.assertEqual(round_significant(1.987654321, 5), 1.9877)
        self.assertEqual(round_significant(0.1987654321, 5), 0.19877)
        self.assertEqual(round_significant(0.01987654321, 5), 0.019877)

        self.assertEqual(round_significant(1.0234, 5), 1.0234)
        self.assertEqual(round_significant(10.234, 5), 10.234)
        self.assertEqual(round_significant(102.34, 5), 102.34)
        self.assertEqual(round_significant(1234.5, 5), 1234.5)
        self.assertEqual(round_significant(0.012345, 5), 0.012345)
        self.assertEqual(round_significant(0.00012340, 5), 0.00012340)

        self.assertEqual(round_significant(1.02349, 5), 1.0235)
        self.assertEqual(round_significant(10.2349, 5), 10.235)
        self.assertEqual(round_significant(102.349, 5), 102.35)
        self.assertEqual(round_significant(1234.59, 5), 1234.6)
        self.assertEqual(round_significant(0.0123459, 5), 0.012346)
        self.assertEqual(round_significant(0.000123409, 5), 0.00012341)

        self.assertEqual(round_significant(1.023499, 6), 1.0235)
        self.assertEqual(round_significant(10.23499, 6), 10.235)
        self.assertEqual(round_significant(102.3499, 6), 102.35)
        self.assertEqual(round_significant(1234.599, 6), 1234.6)
        self.assertEqual(round_significant(0.01234599, 6), 0.012346)
        self.assertEqual(round_significant(0.0001234099, 6), 0.00012341)

        self.assertEqual(round_significant(0.012345, 7), 0.012345)
        self.assertEqual(round_significant(0.012345, 6), 0.012345)
        self.assertEqual(round_significant(0.012345, 5), 0.012345)
        self.assertEqual(round_significant(0.012345, 4), 0.01235)
        self.assertEqual(round_significant(0.012345, 3), 0.0123)
        self.assertEqual(round_significant(0.012345, 2), 0.012)
        self.assertEqual(round_significant(0.012345, 1), 0.01)
        self.assertEqual(round_significant(0.012345, 0), None)
