from unittest import TestCase

from cryptoverse.utilities import round_down


class TestRoundDown(TestCase):

    def test_round_down(self):
        value = 2.9115832281587436e-09
        self.assertEqual(2.9115832281e-09, round_down(value, 19))
        self.assertEqual(2.911e-09, round_down(value, 12))
        self.assertEqual(2.91e-09, round_down(value, 11))
        self.assertEqual(2.9e-09, round_down(value, 10))
        self.assertEqual(2e-09, round_down(value, 9))
        self.assertEqual(0.0, round_down(value, 8))

        value = 1e-6
        self.assertEqual(1e-6, round_down(value, 8))
