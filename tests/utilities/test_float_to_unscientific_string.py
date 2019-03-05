from unittest import TestCase

from cryptoverse.utilities import float_to_unscientific_string


class TestFloat_to_unscientific_string(TestCase):

    def test_float_to_unscientific_string(self):
        value = 6.1e-06
        self.assertEqual('0.0000061', float_to_unscientific_string(value))

        value = 6e-06
        self.assertEqual('0.000006', float_to_unscientific_string(value))

        value = 6.14e-06
        self.assertEqual('0.00000614', float_to_unscientific_string(value))

        value = 4.16008373582688e+47
        self.assertEqual('416008373582688023166889316751193910123459248128.0', float_to_unscientific_string(value))

        value = 3850
        self.assertEqual('3850.0', float_to_unscientific_string(value))

        value = 3850.0
        self.assertEqual('3850.0', float_to_unscientific_string(value))

        value = 0.033971
        self.assertEqual('0.033971',
                         float_to_unscientific_string(value))
        self.assertEqual('0.033971', float_to_unscientific_string(value, decimals=8))

        value = 0.034379
        self.assertEqual('0.034379',
                         float_to_unscientific_string(value))
        self.assertEqual('0.034379', float_to_unscientific_string(value, decimals=8))

        value = 3799.9
        self.assertEqual('3799.9', float_to_unscientific_string(value))
        self.assertEqual('3799.9', float_to_unscientific_string(value, decimals=8))

        value = 3754.8
        self.assertEqual('3754.8', float_to_unscientific_string(value))
        self.assertEqual('3754.8', float_to_unscientific_string(value, decimals=8))

        value = 2e-07
        self.assertEqual('0.0000002', float_to_unscientific_string(value))

        value = 2.024e-07
        self.assertEqual('0.0000002024', float_to_unscientific_string(value))

        value = 0.01866632
        self.assertEqual('0.01866632', float_to_unscientific_string(value))

        value = 0.8150695
        self.assertEqual('0.8150695', float_to_unscientific_string(value))

        value = 0.00244052
        self.assertEqual('0.00244052', float_to_unscientific_string(value))

        value = 3.3000000000000003
        self.assertEqual('3.3000000000000003', float_to_unscientific_string(value))
        self.assertEqual('3.3', float_to_unscientific_string(value, decimals=8))
