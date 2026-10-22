"""Stable identifier formatting shared by application modules."""


def normalize_id(value):
    return value.strip().lower()
