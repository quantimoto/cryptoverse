from unittest import TestCase

from cryptoverse.utilities import round_up


class TestRound_up(TestCase):
    def test_round_up(self):
        value = 2.024e-07
        self.assertEqual(2.1e-07, round_up(value))

        value = 2.024e-08
        self.assertEqual(3e-08, round_up(value))

