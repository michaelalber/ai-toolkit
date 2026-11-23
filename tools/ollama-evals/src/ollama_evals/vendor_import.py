# <AI-Generated START>
"""Convert pinned upstream datasets into ollama-evals cases (run once; output is committed).

    python -m ollama_evals.vendor_import bfcl BFCL_v3_irrelevance.json \
        datasets/bfcl_irrelevance.jsonl --commit SHA --limit 60
    python -m ollama_evals.vendor_import ifeval ifeval_input_data.jsonl \
        datasets/ifeval.jsonl --commit SHA

Input files are untrusted data: they are parsed as JSON and never executed. Every case keeps a
``source`` block (dataset, file, commit, license, upstream id) for attribution.
"""

from __future__ import annotations

import argparse
import copy
import json
import random
from pathlib import Path

from .scorers.ifeval import CHECKS

BFCL = {"dataset": "gorilla-llm/Berkeley-Function-Calling-Leaderboard",
        "file": "BFCL_v3_irrelevance.json", "license": "Apache-2.0"}
IFEVAL = {"dataset": "google/IFEval", "file": "ifeval_input_data.jsonl", "license": "Apache-2.0"}

# BFCL writes Python type names; tool schemas sent to Ollama need JSON Schema names.
_TYPES = {"dict": "object", "float": "number", "tuple": "array", "integer": "integer",
          "string": "string", "boolean": "boolean", "array": "array", "object": "object",
          "number": "number"}


def _json_schema(node):
    if isinstance(node, list):
        return [_json_schema(n) for n in node]
    if not isinstance(node, dict):
        return node
    out: dict = {}
    for key, value in node.items():
        if key == "type" and isinstance(value, str):
            if value in _TYPES:
                out["type"] = _TYPES[value]
            # "any" and unknown names: leave the type unconstrained
        elif key in ("properties",):
            out[key] = {k: _json_schema(v) for k, v in value.items()}
        else:
            out[key] = _json_schema(value)
    return out


def bfcl_case(row: dict, commit: str) -> dict:
    tools = [{"type": "function", "function": {
        "name": fn["name"].replace(".", "_"),
        "description": fn.get("description", ""),
        "parameters": _json_schema(copy.deepcopy(fn["parameters"])),
    }} for fn in row["function"]]
    return {
        "id": f"bfcl-{row['id']}",
        "category": "tool_use",
        "messages": row["question"][0],
        "tools": tools,
        "scorer": {"type": "tool_use", "expected": {"no_call": True}},
        "tags": ["bfcl", "irrelevance"],
        "source": {**BFCL, "commit": commit, "upstream_id": row["id"]},
    }


def ifeval_case(row: dict, commit: str) -> dict | None:
    """None when the prompt uses an instruction this subset cannot check."""
    if any(i not in CHECKS for i in row["instruction_id_list"]):
        return None
    instructions = [{"id": i, "kwargs": {k: v for k, v in (kw or {}).items() if v is not None}}
                    for i, kw in zip(row["instruction_id_list"], row["kwargs"], strict=True)]
    return {
        "id": f"ifeval-{row['key']}",
        "category": "instruction_following",
        "prompt": row["prompt"],
        "scorer": {"type": "ifeval", "instructions": instructions},
        "tags": ["ifeval", *sorted({i.split(":")[0] for i in row["instruction_id_list"]})],
        "source": {**IFEVAL, "commit": commit, "upstream_id": row["key"]},
    }


def sample(rows: list, limit: int, seed: int = 7) -> list:
    """A fixed-seed sample of `limit` rows, in source order (all rows if limit >= len)."""
    if limit >= len(rows):
        return list(rows)
    keep = sorted(random.Random(seed).sample(range(len(rows)), limit))
    return [rows[i] for i in keep]


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("kind", choices=["bfcl", "ifeval"])
    ap.add_argument("src", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--commit", required=True, help="upstream commit the file was downloaded at")
    ap.add_argument("--limit", type=int, default=10_000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--exclude", default="",
                    help="comma-separated upstream ids dropped after review (after sampling)")
    a = ap.parse_args(argv)
    rows = [json.loads(line) for line in a.src.read_text().splitlines() if line.strip()]
    convert = bfcl_case if a.kind == "bfcl" else ifeval_case
    cases = [c for c in (convert(r, a.commit) for r in rows) if c is not None]
    excluded = {x.strip() for x in a.exclude.split(",") if x.strip()}
    picked = [c for c in sample(cases, a.limit, a.seed)
              if str(c["source"]["upstream_id"]) not in excluded]
    a.out.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in picked))
    print(f"{len(rows)} rows -> {len(cases)} convertible -> wrote {len(picked)} to {a.out}")


if __name__ == "__main__":
    main()
# <AI-Generated END>
