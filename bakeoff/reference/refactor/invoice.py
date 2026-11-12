# <AI-Generated START>
from decimal import Decimal

from tax import apply_tax


def total(items, rate):
    subtotal = sum((Decimal(str(p)) * q for p, q in items), Decimal("0"))
    return subtotal + apply_tax(subtotal, rate)
# <AI-Generated END>
