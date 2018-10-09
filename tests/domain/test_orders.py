from unittest import TestCase

from cryptoverse.domain import Orders, Order


class TestOrders(TestCase):

    def test___init__(self):
        orders = Orders()
        self.assertIsInstance(orders, Orders)
        self.assertEqual(0, len(orders))

        orders.append_order()
        orders.append_order()
        self.assertEqual(2, len(orders))

        orders = Orders(orders.as_list())
        self.assertIsInstance(orders, Orders)
        self.assertEqual(2, len(orders))

        orders = Orders(amount=1, price=[10, 20, 30])
        self.assertIsInstance(orders, Orders)
        self.assertEqual(3, len(orders))
        self.assertIsInstance(orders[0], Order)
        self.assertIsInstance(orders[1], Order)
        self.assertIsInstance(orders[2], Order)
        self.assertEqual(10, orders[0].price)
        self.assertEqual(20, orders[1].price)
        self.assertEqual(30, orders[2].price)
