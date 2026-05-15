# License Matrix

Reference for open-source license compatibility, copyleft risk assessment, and corporate policy
considerations. Used by the supply-chain-audit skill and the dependency-audit-agent to evaluate
whether dependency licenses are compatible with a project's distribution model.

---

## License Categories

Open-source licenses fall into three broad categories based on the obligations they impose
on downstream users. Understanding these categories is essential before evaluating individual
license compatibility.

### Permissive Licenses

Permissive licenses allow almost any use, modification, and redistribution with minimal
requirements (typically attribution only). They are compatible with proprietary, open-source,
and SaaS distribution models.

**Key characteristic:** You can use the code in proprietary software without disclosing your
own source code.

**Common permissive licenses:**

| License | SPDX ID | Key Obligations | Notes |
|---------|---------|-----------------|-------|
| MIT License | MIT | Include copyright notice and license text | Most popular OSS license. No patent grant. |
| Apache License 2.0 | Apache-2.0 | Include copyright, license, NOTICE file; state changes | Includes explicit patent grant. Preferred by many corporations. |
| BSD 2-Clause | BSD-2-Clause | Include copyright notice and license text | "Simplified BSD." Similar to MIT. |
| BSD 3-Clause | BSD-3-Clause | Same as 2-Clause + no endorsement clause | "New BSD." The endorsement clause prohibits using the author's name in promotions. |
| ISC License | ISC | Include copyright notice and license text | Functionally equivalent to MIT. Preferred by some Node.js projects. |
| Unlicense | Unlicense | None (public domain dedication) | Effectively places code in the public domain. Some jurisdictions do not recognize public domain dedications. |
| CC0 1.0 | CC0-1.0 | None (public domain dedication) | Creative Commons' public domain tool. More legally robust than Unlicense in some jurisdictions. |
| Zlib License | Zlib | Include copyright in source distributions; altered versions must be marked | Common in game development and compression libraries. |

### Weak Copyleft Licenses

Weak copyleft licenses require that modifications to the licensed library itself be shared
under the same license, but allow the library to be used in proprietary software without
requiring the proprietary code to be disclosed. The boundary is typically at the library/file
level.

**Key characteristic:** You must share changes to the library, but your own code that uses
the library remains proprietary.

| License | SPDX ID | Copyleft Scope | Key Obligations |
|---------|---------|----------------|-----------------|
| LGPL-2.1 | LGPL-2.1-only | Library boundary | Modifications to the library must be LGPL. Proprietary code may link dynamically. Static linking requires providing object files for relinking. |
| LGPL-3.0 | LGPL-3.0-only | Library boundary | Same as LGPL-2.1 plus GPLv3 additional terms (anti-tivoization). |
| MPL-2.0 | MPL-2.0 | File boundary | Modifications to MPL-licensed files must be MPL. New files can be any license. The copyleft scope is per-file, not per-library. |
| EPL-2.0 | EPL-2.0 | Module boundary | Modifications to EPL code must be EPL. Can be combined with proprietary code. Secondary license option allows GPL compatibility. |
| CDDL-1.0 | CDDL-1.0 | File boundary | Similar scope to MPL. Modifications to CDDL files must be CDDL. New files can be any license. NOT compatible with GPL. |

**Dynamic vs Static Linking (LGPL):**

The LGPL distinguishes between dynamic and static linking. This matters primarily for compiled
languages (C, C++, .NET, Rust).

| Linking Method | LGPL Obligation |
|---------------|-----------------|
| Dynamic linking (.dll, .so, .dylib) | No additional obligations for your proprietary code. Must distribute the LGPL library and allow users to replace it. |
| Static linking (.a, .lib, compiled in) | Must provide your object files or source so users can relink with a modified version of the LGPL library. |
| NuGet/npm/pip (interpreted/managed) | Generally treated as dynamic linking because the dependency is a separate distributable unit. Consult legal counsel for edge cases. |

### Strong Copyleft Licenses

Strong copyleft licenses require that any software that incorporates, links to, or is derived
from the licensed code must also be distributed under the same license. This means disclosing
your source code under the copyleft license.

**Key characteristic:** If you distribute software containing strong-copyleft code, you must
distribute your entire application's source code under the same license.

| License | SPDX ID | Copyleft Scope | Key Considerations |
|---------|---------|----------------|-------------------|
| GPL-2.0 | GPL-2.0-only | Entire program | Any program that links to or incorporates GPL-2.0 code must be GPL-2.0 when distributed. "Or later" variant (GPL-2.0-or-later) allows upgrading to GPL-3.0. |
| GPL-3.0 | GPL-3.0-only | Entire program | Same as GPL-2.0 plus: anti-tivoization provisions, explicit patent grant, improved compatibility with other licenses. |
| AGPL-3.0 | AGPL-3.0-only | Entire program + network use | Extends GPL-3.0 to cover network interaction. If users interact with the software over a network (e.g., SaaS), source code must be made available. This is the strictest common copyleft license. |

---

## Compatibility Matrix

This matrix shows whether a dependency's license is compatible with a project's distribution
model. Compatibility means you can legally use the dependency in your project as distributed.

### By Distribution Model

**SaaS / Server-Side Only (not distributed to end users):**

| Dependency License | Compatible | Notes |
|-------------------|------------|-------|
| MIT, Apache-2.0, BSD, ISC | Yes | No restrictions for server-side use. |
| LGPL-2.1, LGPL-3.0 | Yes | No distribution occurs, so copyleft is not triggered. |
| MPL-2.0 | Yes | No distribution; file-level copyleft not triggered. |
| GPL-2.0, GPL-3.0 | Yes* | *Controversial. Most interpretations say no distribution = no copyleft obligation. Conservative legal counsel may disagree. Clarify with legal. |
| AGPL-3.0 | **NO** | AGPL specifically extends to network use. Source disclosure may be required even without distribution. |

**On-Premise / Desktop (distributed to customers):**

| Dependency License | Compatible with Proprietary | Notes |
|-------------------|-----------------------------|-------|
| MIT, Apache-2.0, BSD, ISC | Yes | Include notices per license terms. |
| LGPL-2.1, LGPL-3.0 | Yes (with conditions) | Must allow library replacement. Dynamic linking preferred. Static linking requires object file distribution. |
| MPL-2.0 | Yes (with conditions) | Modifications to MPL files must be shared. Your own files are unaffected. |
| GPL-2.0, GPL-3.0 | **NO** | Requires disclosing your entire application source under GPL. |
| AGPL-3.0 | **NO** | Even stricter than GPL. Source disclosure required. |

**Open-Source Library (distributed as a library for others to use):**

| Dependency License | Compatible with MIT | Compatible with Apache-2.0 | Compatible with GPL-3.0 |
|-------------------|--------------------|-----------------------------|------------------------|
| MIT | Yes | Yes | Yes |
| Apache-2.0 | Yes* | Yes | Yes |
| BSD-2/3-Clause | Yes | Yes | Yes |
| LGPL-2.1/3.0 | Yes (dynamic) | Yes (dynamic) | Yes |
| MPL-2.0 | Yes (separate files) | Yes (separate files) | Yes |
| GPL-2.0 | **NO** | **NO** | Only if GPL-2.0-or-later |
| GPL-3.0 | **NO** | **NO** | Yes |
| AGPL-3.0 | **NO** | **NO** | **NO** (unless AGPL) |

*Apache-2.0 in MIT-licensed code: Apache-2.0's patent clause and NOTICE requirement survive.
The resulting combined work must comply with Apache-2.0 terms even if your project is MIT.

---

## Corporate Policy Considerations

### Common Corporate License Policies

Most corporations maintain an approved license list. The following represents a typical
enterprise policy:

**Approved (no review required):**
- MIT
- Apache-2.0
- BSD-2-Clause
- BSD-3-Clause
- ISC
- CC0-1.0
- Unlicense
- Zlib

**Conditional (review recommended):**
- LGPL-2.1, LGPL-3.0 (review linking model)
- MPL-2.0 (review modification scope)
- EPL-2.0 (review module boundaries)
- CC-BY-4.0 (ensure attribution is maintained)

**Restricted (legal review required):**
- GPL-2.0, GPL-3.0 (copyleft scope analysis needed)
- AGPL-3.0 (network use clause analysis needed)
- SSPL (Server Side Public License -- MongoDB)
- BSL (Business Source License -- MariaDB, HashiCorp)
- Proprietary / Commercial (check agreement terms)

**Prohibited:**
- WTFPL (legally unenforceable in some jurisdictions)
- No license specified (no permission granted)
- NOASSERTION (unknown license -- treat as no license)

### Multi-License Packages

Some packages offer multiple license options (e.g., "MIT OR Apache-2.0"). When a package
offers a choice:
1. Select the license most compatible with your project
2. Document which license you selected and why
3. Ensure all downstream obligations of the selected license are met

When a package uses dual licensing with an AND condition (e.g., "MIT AND BSD-3-Clause"),
both sets of obligations apply simultaneously.

---

## Copyleft Risk Assessment

### Risk Levels

| Risk Level | Trigger | Action Required |
|------------|---------|-----------------|
| **NONE** | Permissive license (MIT, Apache-2.0, BSD, ISC) | Include notices. No further action. |
| **LOW** | Weak copyleft, dynamic linking (LGPL via NuGet/npm/pip) | Ensure library can be replaced by end user. Typically satisfied by package manager distribution. |
| **MEDIUM** | Weak copyleft, unclear linking model or file-scope copyleft (MPL-2.0) | Review how the library is integrated. Ensure modifications to library files are shareable. |
| **HIGH** | Strong copyleft in server-only deployment (GPL in SaaS) | Legal review recommended. Most interpretations favor no obligation without distribution, but risk exists. |
| **CRITICAL** | Strong copyleft in distributed software (GPL in on-prem) or AGPL in any deployment | Source disclosure likely required. This is a blocking issue requiring legal review and remediation. |

### Copyleft Boundary Analysis

When evaluating copyleft risk, determine where the copyleft boundary falls:

```
Your Application Code
       |
       |--- [Direct dependency: MIT]         --> No copyleft risk
       |
       |--- [Direct dependency: LGPL-3.0]    --> Copyleft applies to THIS library only
       |         |
       |         +--- [Transitive: MIT]       --> No copyleft risk
       |
       |--- [Direct dependency: GPL-3.0]     --> Copyleft applies to ENTIRE APPLICATION
       |         |
       |         +--- [Transitive: MIT]       --> Now effectively GPL-3.0 in this context
       |
       +--- [Direct dependency: AGPL-3.0]    --> Copyleft applies to entire application
                                                  INCLUDING network-served usage
```

### Remediation Strategies for License Issues

| Situation | Strategy |
|-----------|----------|
| GPL dependency in proprietary distributed software | Replace with permissive-licensed alternative. If no alternative exists, isolate into a separate process communicating via IPC (process-boundary defense). |
| AGPL dependency in SaaS application | Replace with permissive-licensed alternative. AGPL cannot be isolated by process boundaries if the AGPL component is part of the user-facing service. |
| LGPL with static linking concern | Switch to dynamic linking if possible. Provide object files for relinking if static linking is required. |
| Unknown/missing license | Contact the package author to clarify. If no response, treat as proprietary and find an alternative. Do NOT assume MIT or public domain. |
| License changed between versions | Pin to the last version with the acceptable license. Monitor for security patches on the older version. Plan migration to an alternative if the new license is incompatible. |

---

## License Detection Approaches

### Automated Tools

| Tool | Ecosystems | Command | Output |
|------|-----------|---------|--------|
| license-checker (npm) | npm | `npx license-checker --json --production` | Package name, license, repository |
| pip-licenses (Python) | pip | `pip-licenses --format=json` | Package name, version, license |
| dotnet-project-licenses | NuGet | `dotnet-project-licenses --input <sln>` | Package name, version, license URL |
| FOSSA | All | `fossa analyze` | Comprehensive license compliance |
| ScanCode | All | `scancode --license --json output.json <path>` | File-level license detection |

### Manual Verification

When automated tools report "UNKNOWN" or "CUSTOM" licenses:

1. Check the package's repository for a `LICENSE`, `LICENCE`, `COPYING`, or `LICENSE.md` file
2. Check the package registry page (nuget.org, npmjs.com, pypi.org) for license metadata
3. Check the package manifest (`package.json` "license" field, `setup.py` "license" kwarg, `.nuspec` "license" element)
4. If the license text exists but is not a standard SPDX identifier, read the text and classify it
5. If no license information exists anywhere, the package has no license -- which means no permission to use it

### SPDX License Identifiers

Always use SPDX identifiers (https://spdx.org/licenses/) for consistent license reporting.
Common mappings for ambiguous license names:

| Informal Name | SPDX Identifier |
|--------------|-----------------|
| "BSD" (unspecified) | Check text -- likely BSD-2-Clause or BSD-3-Clause |
| "Apache" (unspecified) | Likely Apache-2.0 |
| "GPL" (unspecified) | Check version -- GPL-2.0-only or GPL-3.0-only |
| "Public Domain" | Check if CC0-1.0 or Unlicense applies |
| "Free" or "Open Source" | NOT a license. Requires investigation. |
| "" (empty) or "UNLICENSED" | No license. No permission granted. |
