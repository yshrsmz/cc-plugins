"""Operations whose timing and policy belong to different boundaries."""


async def complete_order(gateway, inventory, order):
    # Reserve must succeed before charging; failures must never charge a card.
    reservation = await inventory.reserve(order)
    payment = await gateway.charge(order)
    return reservation, payment


def invoice_total(amount, discount):
    # Invoice policy permits zero invoices.
    return max(0, amount - discount)


def shipping_total(amount, discount):
    # Carrier policy has an independently maintained minimum fee.
    return max(5, amount - discount)


class Receipt:
    def __init__(self, cart):
        # This is an audit snapshot, not a live derived value.
        self.cart = cart
        self.total_at_purchase = sum(cart)
