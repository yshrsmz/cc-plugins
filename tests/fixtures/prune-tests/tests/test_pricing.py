from datetime import date
from decimal import Decimal
import unittest
from unittest import mock

from shop import pricing
from shop.pricing import Coupon, Item


class SubtotalTests(unittest.TestCase):
    def test_subtotal_matches_formula(self):
        items = [Item(Decimal("120"), 2), Item(Decimal("55"), 3)]
        expected = sum((item.price * item.qty for item in items), Decimal("0"))
        self.assertEqual(pricing.subtotal(items), expected)

    def test_subtotal_of_several_items(self):
        items = [Item(Decimal("100"), 2), Item(Decimal("50"), 3)]
        self.assertEqual(pricing.subtotal(items), Decimal("350"))

    def test_subtotal_of_empty_cart_is_zero(self):
        self.assertEqual(pricing.subtotal([]), Decimal("0"))

    def test_subtotal_single_item_qty_1(self):
        self.assertEqual(pricing.subtotal([Item(Decimal("100"), 1)]), Decimal("100"))

    def test_subtotal_single_item_qty_2(self):
        self.assertEqual(pricing.subtotal([Item(Decimal("100"), 2)]), Decimal("200"))

    def test_subtotal_single_item_qty_3(self):
        self.assertEqual(pricing.subtotal([Item(Decimal("100"), 3)]), Decimal("300"))

    def test_subtotal_single_item_qty_4(self):
        self.assertEqual(pricing.subtotal([Item(Decimal("100"), 4)]), Decimal("400"))

    def test_subtotal_single_item_qty_5(self):
        self.assertEqual(pricing.subtotal([Item(Decimal("100"), 5)]), Decimal("500"))


class DiscountTests(unittest.TestCase):
    coupon = Coupon(percent=20, expires=date(2026, 3, 31))

    def test_valid_coupon_reduces_amount(self):
        self.assertEqual(pricing.apply_discount(Decimal("1000"), self.coupon, date(2026, 3, 1)),
                         Decimal("800"))

    def test_coupon_still_applies_on_expiry_day(self):
        self.assertEqual(pricing.apply_discount(Decimal("1000"), self.coupon, date(2026, 3, 31)),
                         Decimal("800"))

    def test_expired_coupon_is_ignored(self):
        self.assertEqual(pricing.apply_discount(Decimal("1000"), self.coupon, date(2026, 4, 1)),
                         Decimal("1000"))

    def test_discount_never_makes_amount_negative(self):
        coupon = Coupon(percent=150, expires=date(2026, 3, 31))
        self.assertEqual(pricing.apply_discount(Decimal("1000"), coupon, date(2026, 3, 1)),
                         Decimal("0"))


class TaxTests(unittest.TestCase):
    def test_tax_rounds_half_up(self):
        # Regression: banker's rounding charged 0 tax on an amount of 5 (0.5 rounded to even).
        self.assertEqual(pricing.tax(Decimal("5")), Decimal("1"))

    def test_tax_uses_round_helper(self):
        with mock.patch.object(pricing, "_round", return_value=Decimal("7")) as rounding:
            pricing.tax(Decimal("70"))
        rounding.assert_called_once_with(Decimal("7.00"))


class LibraryTests(unittest.TestCase):
    def test_item_stores_fields(self):
        item = Item(Decimal("100"), 2)
        self.assertEqual(item.price, Decimal("100"))
        self.assertEqual(item.qty, 2)

    def test_decimal_addition_is_exact(self):
        self.assertEqual(Decimal("0.1") + Decimal("0.2"), Decimal("0.3"))


if __name__ == "__main__":
    unittest.main()
