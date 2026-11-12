# <AI-Generated START>
from decimal import Decimal


def total(items, rate):
    """items: list of (price, qty). Returns subtotal + tax."""
    subtotal = sum((Decimal(str(p)) * q for p, q in items), Decimal("0"))
    tax = round(subtotal * Decimal(str(rate)), 2)
    return subtotal + tax
# <AI-Generated END>
