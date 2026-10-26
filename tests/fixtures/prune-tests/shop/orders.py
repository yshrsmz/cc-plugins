from dataclasses import dataclass

from shop import pricing


@dataclass(frozen=True)
class User:
    id: str
    blocked: bool = False


@dataclass(frozen=True)
class Order:
    user_id: str
    total: object
    receipt: str


def place_order(user, items, coupon, gateway, today):
    if user.blocked:
        raise PermissionError("blocked user")
    discounted = pricing.apply_discount(pricing.subtotal(items), coupon, today)
    total = discounted + pricing.tax(discounted)
    receipt = gateway.charge(user.id, total)
    return Order(user.id, total, receipt)
