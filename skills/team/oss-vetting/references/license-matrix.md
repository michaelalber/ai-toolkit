# License Compatibility Matrix — Federal Contractor Use

For use in OSS vetting assessments involving LANL or other federal contractor environments. Covers proprietary/closed-source deliverables. Consult legal for novel situations.

---

## Tier 1 — Generally Acceptable

No additional review required for standard contractor use.

| License | SPDX ID | Notes |
|---|---|---|
| MIT | `MIT` | No conditions beyond attribution. Explicit patent grant: No. |
| Apache 2.0 | `Apache-2.0` | Explicit patent grant. Requires NOTICE file preservation. |
| BSD 2-Clause | `BSD-2-Clause` | Minimal conditions. No patent grant. |
| BSD 3-Clause | `BSD-3-Clause` | Adds non-endorsement clause. No patent grant. |
| ISC | `ISC` | Functionally equivalent to MIT. |
| Unlicense | `Unlicense` | Public domain dedication. |
| CC0 1.0 | `CC0-1.0` | Public domain dedication. Rarely used for code. |
| WTFPL | `WTFPL` | Permissive. Not OSI-approved but legally permissive. |
| 0BSD | `0-BSD` | Zero-clause BSD. No attribution required. |
| Boost 1.0 | `BSL-1.0` | Common in C++ ecosystem. Permissive. |
| MS-PL | `MS-PL` | Microsoft Permissive License. Acceptable for dynamic use. |

---

## Tier 2 — Requires Review

Acceptable in many cases but conditions must be documented.

| License | SPDX ID | Key condition | Guidance |
|---|---|---|---|
| LGPL 2.1 | `LGPL-2.1-only` | Copyleft applies to library itself | Acceptable as dynamic dependency; review if statically linked or modified |
| LGPL 3.0 | `LGPL-3.0-only` | Same as 2.1 + additional user freedom reqs | Same guidance; note GPLv3 compatibility |
| MPL 2.0 | `MPL-2.0` | File-level copyleft | Acceptable if MPL files not modified; modified MPL files must be released |
| EPL 1.0 | `EPL-1.0` | Weak copyleft | Review for commercial deliverables; Eclipse ecosystem common |
| EPL 2.0 | `EPL-2.0` | Weak copyleft + secondary licenses | More flexible than 1.0; check secondary license compatibility |
| EUPL 1.2 | `EUPL-1.2` | EU public license, copyleft | Compatible with several other copyleft licenses; review carefully |
| CDDL 1.0 | `CDDL-1.0` | File-level copyleft | Sun/Oracle heritage; review for modified use |
| MS-RL | `MS-RL` | Microsoft Reciprocal License | Weak copyleft; acceptable for unmodified dynamic use |
| OSL 3.0 | `OSL-3.0` | Strong copyleft including network use | Treat as near-AGPL for web-facing services |

---

## Tier 3 — Likely Disqualifying for Proprietary Deliverables

Requires explicit legal waiver or re-architecture to avoid.

| License | SPDX ID | Reason |
|---|---|---|
| GPL 2.0 | `GPL-2.0-only` | Strong copyleft — contaminates all linked code |
| GPL 3.0 | `GPL-3.0-only` | Same + anti-tivoization, patent retaliation |
| GPL 2.0+ | `GPL-2.0-or-later` | Strong copyleft |
| GPL 3.0+ | `GPL-3.0-or-later` | Strong copyleft |
| AGPL 3.0 | `AGPL-3.0-only` | Network use = distribution; extremely broad copyleft |
| AGPL 3.0+ | `AGPL-3.0-or-later` | Same |
| SSPL 1.0 | `SSPL-1.0` | MongoDB license; not OSI-approved; extremely broad service provision clause |
| Commons Clause | N/A (addendum) | Restricts commercial use; often added on top of other licenses |

---

## Special Cases

### No License Stated
All rights reserved by default under copyright law. **Do not use.** Contact the maintainer to request a license or find an alternative.

### Dual-Licensed
Some packages offer two licenses (e.g., GPL for open-source use, commercial license for proprietary use). In these cases:
- Identify which license applies to the Denali/LANL use case
- If the commercial license applies, confirm procurement and document it
- Example: Qt (GPL + commercial), MySQL Connector (GPL + commercial)

### Custom / Bespoke Licenses
Treat as Tier 2 minimum. Read carefully. Flag any of: commercial use restrictions, field-of-use restrictions, government use restrictions, or military/defense use restrictions.

### Creative Commons (Non-Code)
CC licenses are designed for creative works, not software. If encountered on a code library:
- CC BY, CC BY-SA: may be acceptable — review carefully
- CC BY-NC, CC BY-ND: non-commercial or no-derivatives restrictions — likely disqualifying
- Do not use CC-NC variants on any contractor deliverable

---

## Attribution Requirements

Even Tier 1 licenses may require attribution. Track and fulfill these:

| Requirement | Licenses | Action |
|---|---|---|
| Include copyright notice | MIT, BSD, Apache 2.0, ISC | Include in NOTICE file or equivalent |
| Include NOTICE file | Apache 2.0 | Preserve and include upstream NOTICE content |
| Attribution in documentation | Some custom licenses | Read license text |
| Non-endorsement clause | BSD-3-Clause | Cannot use project name in promotional materials |

---

## Patent Considerations

| License | Explicit Patent Grant |
|---|---|
| Apache 2.0 | Yes — terminates if recipient sues for patent infringement |
| MIT | No |
| BSD variants | No |
| LGPL 3.0 / GPL 3.0 | Yes (implicit via patent retaliation clause) |
| EPL 2.0 | Yes |

When using libraries in security-sensitive or IP-sensitive LANL deliverables, prefer Apache 2.0 or EPL 2.0 over MIT/BSD for explicit patent protection.
