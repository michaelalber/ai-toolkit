# <AI-Generated START>
import re

_V = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$")
_TOK = re.compile(r"^(>=|<=|>|<|=|\^|~)?\s*(.+)$")


def parse(version):
    m = _V.match(version.strip())
    if not m:
        raise ValueError(f"invalid version: {version!r}")
    major, minor, patch, pre = m.groups()
    return (int(major), int(minor), int(patch), tuple(pre.split(".")) if pre else ())


def _key(v):
    pre = (1,) if not v[3] else (0, tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in v[3]))
    return (v[0], v[1], v[2], pre)


def compare(a, b):
    ka, kb = _key(parse(a)), _key(parse(b))
    return (ka > kb) - (ka < kb)


def _desugar(tok):
    op, ver = _TOK.match(tok).groups()
    v = parse(ver)
    op = op or "="
    if op == "^":
        hi = (v[0] + 1, 0, 0) if v[0] else (0, v[1] + 1, 0) if v[1] else (0, 0, v[2] + 1)
        return [(">=", v), ("<", hi + ((),))]
    if op == "~":
        return [(">=", v), ("<", (v[0], v[1] + 1, 0, ()))]
    return [(op, v)]


_OPS = {">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b,
        "<": lambda a, b: a < b, "=": lambda a, b: a == b}


def satisfies(version, version_range):
    v = parse(version)
    clauses = [[c for tok in clause.split() for c in _desugar(tok)] for clause in version_range.split("||")]
    if not all(clauses):  # validate every clause up front, even ones after a match
        raise ValueError("empty clause")
    return any(
        all(_OPS[op](_key(v), _key(c)) for op, c in comps)
        and (not v[3] or any(c[3] and c[:3] == v[:3] for _, c in comps))
        for comps in clauses
    )
# <AI-Generated END>
