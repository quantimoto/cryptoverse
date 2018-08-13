from unittest import TestCase

from cryptoverse.domain import Instrument


class TestInstrument(TestCase):
    def test___eq__(self):
        instrument1 = Instrument('BTC')
        instrument2 = Instrument('BTC')
        instrument3 = Instrument('USD')

        self.assertEqual(instrument1, 'BTC')
        self.assertEqual(instrument1, instrument2)
        self.assertNotEqual(instrument1, instrument3)
        self.assertNotEqual(instrument2, instrument3)
