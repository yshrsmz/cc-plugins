from datetime import date
from decimal import Decimal
import unittest
from unittest import mock

from shop import orders, pricing
from shop.orders import User
from shop.pricing import Coupon, Item


TODAY = date(2026, 3, 1)
ITEMS = [Item(Decimal("1000"), 1)]
COUPON = Coupon(percent=20, expires=date(2026, 3, 31))


class PlaceOrderTests(unittest.TestCase):
    def test_gateway_returns_receipt(self):
        gateway = mock.Mock()
        gateway.charge.return_value = "receipt-1"
        self.assertEqual(gateway.charge("u1", Decimal("880")), "receipt-1")

    def test_total_includes_discount_and_tax(self):
        gateway = mock.Mock()
        order = orders.place_order(User("u1"), ITEMS, COUPON, gateway, TODAY)
        self.assertEqual(order.total, Decimal("880"))

    def test_charges_gateway_exactly_once_with_total(self):
        gateway = mock.Mock()
        gateway.charge.return_value = "receipt-1"
        order = orders.place_order(User("u1"), ITEMS, COUPON, gateway, TODAY)
        gateway.charge.assert_called_once_with("u1", Decimal("880"))
        self.assertEqual(order.receipt, "receipt-1")

    def test_blocked_user_is_rejected_without_charge(self):
        gateway = mock.Mock()
        with self.assertRaises(PermissionError):
            orders.place_order(User("u1", blocked=True), ITEMS, COUPON, gateway, TODAY)
        gateway.charge.assert_not_called()

    def test_pricing_steps_run_in_order(self):
        calls = []
        with mock.patch.object(pricing, "subtotal", side_effect=lambda items: calls.append("subtotal") or Decimal("1000")), \
                mock.patch.object(pricing, "apply_discount", side_effect=lambda amount, coupon, today: calls.append("discount") or amount), \
                mock.patch.object(pricing, "tax", side_effect=lambda amount: calls.append("tax") or Decimal("0")):
            orders.place_order(User("u1"), ITEMS, COUPON, mock.Mock(), TODAY)
        self.assertEqual(calls, ["subtotal", "discount", "tax"])


if __name__ == "__main__":
    unittest.main()
