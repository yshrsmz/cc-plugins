"""Behavior checks for the simple simplification scenario."""

import unittest

from report import report_labels


class ReportTests(unittest.TestCase):
    def test_empty_and_missing_values(self):
        self.assertEqual(report_labels([None, "", "  "]), [])

    def test_format_order_and_duplicates(self):
        self.assertEqual(report_labels(["  A B ", "A B", "C"]), ["a-b", "a-b", "c"])

    def test_invalid_value_still_raises(self):
        with self.assertRaises(AttributeError):
            report_labels([42])


if __name__ == "__main__":
    unittest.main()
