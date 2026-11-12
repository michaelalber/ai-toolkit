# <AI-Generated START>
from decimal import Decimal


def line_tax(amount, rate):
    return round(Decimal(str(amount)) * Decimal(str(rate)), 2)


def summary(amounts, rate):
    return {
        "count": len(amounts),
        "tax": sum((line_tax(a, rate) for a in amounts), Decimal("0")),
    }
# <AI-Generated END>
