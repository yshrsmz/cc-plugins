"""Observable contracts for the multi-module simplification scenario."""

import unittest

from catalog import labels
from checkout import Receipt, complete_order, invoice_total, shipping_total


class CatalogTests(unittest.TestCase):
    def test_labels_preserve_order_filtering_and_duplicates(self):
        snapshot = {"a": {"label": "A", "visible": True},
                    "b": {"label": "B", "visible": False}}
        self.assertEqual(labels(snapshot, [" A ", "b", "missing", "a"]), ["A", "A"])

    def test_validation_errors_are_preserved(self):
        with self.assertRaises(KeyError):
            labels({"a": {"label": "A"}}, ["a"])

    def test_receipt_is_a_snapshot(self):
        cart = [10, 20]
        receipt = Receipt(cart)
        cart.append(30)
        self.assertEqual(receipt.total_at_purchase, 30)

    def test_separate_pricing_policies(self):
        self.assertEqual(invoice_total(10, 20), 0)
        self.assertEqual(shipping_total(10, 20), 5)


class OrderingTests(unittest.IsolatedAsyncioTestCase):
    async def test_reservation_failure_never_charges(self):
        events = []

        class Inventory:
            async def reserve(self, order):
                events.append("reserve")
                raise ValueError("unavailable")

        class Gateway:
            async def charge(self, order):
                events.append("charge")

        with self.assertRaisesRegex(ValueError, "unavailable"):
            await complete_order(Gateway(), Inventory(), "order")
        self.assertEqual(events, ["reserve"])

    async def test_success_order_and_outputs(self):
        events = []

        class Inventory:
            async def reserve(self, order):
                events.append("reserve")
                return "reserved"

        class Gateway:
            async def charge(self, order):
                events.append("charge")
                return "paid"

        self.assertEqual(await complete_order(Gateway(), Inventory(), "order"),
                         ("reserved", "paid"))
        self.assertEqual(events, ["reserve", "charge"])


if __name__ == "__main__":
    unittest.main()
