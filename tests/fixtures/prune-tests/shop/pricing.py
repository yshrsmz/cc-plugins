from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP


TAX_RATE = Decimal("0.10")


@dataclass(frozen=True)
class Item:
    price: Decimal
    qty: int


@dataclass(frozen=True)
class Coupon:
    percent: int
    expires: date


def subtotal(items):
    return sum((item.price * item.qty for item in items), Decimal("0"))


def apply_discount(amount, coupon, today):
    if coupon is None or today > coupon.expires:
        return amount
    discounted = amount - amount * Decimal(coupon.percent) / Decimal("100")
    return max(discounted, Decimal("0"))


def _round(value):
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def tax(amount):
    return _round(amount * TAX_RATE)
