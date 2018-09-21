from unittest import TestCase

from cryptoverse.utilities import round_down


class TestRoundDown(TestCase):

    def test_round_down(self):
        x = 2.9115832281587436e-09
        self.assertEqual(2.9115832281e-09, round_down(x, 19))
        self.assertEqual(2.911e-09, round_down(x, 12))
        self.assertEqual(2.91e-09, round_down(x, 11))
        self.assertEqual(2.9e-09, round_down(x, 10))
        self.assertEqual(2e-09, round_down(x, 9))
        self.assertEqual(0.0, round_down(x, 8))
