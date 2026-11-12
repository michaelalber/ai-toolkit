# <AI-Generated START>
import inspect
from decimal import Decimal

import invoice
import report
import tax


def test_apply_tax_rounds_half_up():
    assert tax.apply_tax(Decimal("2.50"), "0.01") == Decimal("0.03")


def test_apply_tax_plain_case():
    assert tax.apply_tax(Decimal("10.05"), "0.05") == Decimal("0.50")


def test_invoice_total_uses_half_up():
    assert invoice.total([(Decimal("2.50"), 1)], "0.01") == Decimal("2.53")


def test_report_line_tax_uses_half_up():
    assert report.line_tax(Decimal("2.50"), "0.01") == Decimal("0.03")


def test_report_summary():
    s = report.summary([Decimal("2.50"), Decimal("2.50")], "0.01")
    assert s == {"count": 2, "tax": Decimal("0.06")}


def test_no_duplicated_rounding_logic():
    for mod in (invoice, report):
        src = inspect.getsource(mod)
        assert "apply_tax" in src
        assert "round(" not in src
# <AI-Generated END>
