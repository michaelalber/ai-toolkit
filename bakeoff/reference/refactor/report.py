# <AI-Generated START>
from decimal import Decimal

from tax import apply_tax


def line_tax(amount, rate):
    return apply_tax(amount, rate)


def summary(amounts, rate):
    return {"count": len(amounts), "tax": sum((apply_tax(a, rate) for a in amounts), Decimal("0"))}
# <AI-Generated END>
