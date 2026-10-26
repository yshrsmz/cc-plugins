from datetime import date
from decimal import Decimal
import unittest
from unittest import mock

from shop import orders
from shop.orders import User
from shop.pricing import Coupon, Item


class CheckoutFlowTests(unittest.TestCase):
    def test_order_total_with_coupon(self):
        coupon = Coupon(percent=20, expires=date(2026, 3, 31))
        order = orders.place_order(User("u1"), [Item(Decimal("1000"), 1)], coupon,
                                   mock.Mock(), date(2026, 3, 1))
        self.assertEqual(order.total, Decimal("880"))

    def test_order_total_after_coupon_expired(self):
        coupon = Coupon(percent=20, expires=date(2026, 3, 31))
        order = orders.place_order(User("u1"), [Item(Decimal("1000"), 1)], coupon,
                                   mock.Mock(), date(2026, 4, 1))
        self.assertEqual(order.total, Decimal("1100"))


if __name__ == "__main__":
    unittest.main()
