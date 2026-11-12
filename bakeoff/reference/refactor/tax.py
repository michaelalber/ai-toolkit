# <AI-Generated START>
from decimal import ROUND_HALF_UP, Decimal


def apply_tax(amount, rate):
    return (Decimal(str(amount)) * Decimal(str(rate))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
# <AI-Generated END>
