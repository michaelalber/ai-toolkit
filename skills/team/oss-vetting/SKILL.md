---
name: oss-vetting
description: >
  OSS library vetting and SBOM analysis for federal contractor environments (LANL/DOE/CUI).
  Use this skill when evaluating any open-source or third-party package for use in a federal
  contractor project — including NuGet packages, npm, PyPI, or any OSS library. Triggers include:
  vet this library, can we use X in LANL, is X approved for CUI systems, evaluate this NuGet
  package, generate an SBOM, supply chain risk, check this dependency, OSS assessment,
  800-171 compliance for this package, C-SCRM review. Also trigger for any question about
  whether a library is safe, compliant, or appropriate for use on a government contract or
  CUI-adjacent system.
---

# OSS Vetting Skill

Produces a structured OSS Vetting Assessment Report for federal contractor use, covering security posture, supply chain risk, license compliance, and CUI suitability. Output is Confluence-ready Markdown.

## Governing Frameworks

Every assessment is evaluated against four frameworks. Understanding *why* each matters prevents shallow checkbox compliance:

| Framework | Role |
|---|---|
| **EO 14028** | Creates the legal obligation — software on federal systems must be verifiably secure |
| **NIST SP 800-218 (SSDF)** | Defines the process — how maintainers should build and respond to vulnerabilities |
| **NIST SP 800-171 Rev 2** | Sets the data-protection stakes — 110 controls for CUI systems; a vulnerable dep is a direct compliance liability |
| **NIST SP 800-161 (C-SCRM)** | Governs provenance — where the software came from, who maintains it, and whether the supply chain is auditable |

---

## Assessment Workflow

### Step 1 — Gather inputs

Before starting, collect:
- Package name, version, ecosystem (NuGet / PyPI / npm / other)
- The system it will be deployed to (CUI-adjacent? Yellow Network? Air-gapped?)
- Intended use (what does this library do in the application?)
- Any constraints (license type requirements, air-gap tooling limits)

If context is missing, ask. A vague request produces a shallow report.

### Step 2 — Research the package

Research across these dimensions. Use web search if available; note limitations if air-gapped.

**Identity and provenance**
- Official source URL (NuGet.org, PyPI, GitHub)
- License (SPDX identifier — see License Evaluation below)
- Primary maintainer(s): individual, company, foundation?
- Funding/ownership: is there foreign government or high-risk-jurisdiction involvement?
- First published and last updated
- Download/adoption stats (proxy for community health)

**Security posture**
- Known CVEs: check NVD (nvd.nist.gov) and the ecosystem's advisory DB
- Time-to-patch history: how quickly are vulnerabilities addressed?
- Vulnerability disclosure policy: is there a SECURITY.md or equivalent?
- Release signing: are releases signed or hash-verified?
- Dependency count and depth (transitive attack surface)

**Development health (SSDF alignment)**
- Active maintainership: recent commits, responsive issues?
- Changelog / release notes maintained?
- CI/CD visible in repo (green builds = active hygiene)?
- Contributor diversity or bus-factor risk (single-maintainer = high risk)?

**Supply chain factors (C-SCRM)**
- Build reproducibility: can the binary be verified against source?
- Dependency pinning practices
- Known typosquatting or name-confusion risk
- Published SBOM (CycloneDX or SPDX)? If yes, attach or reference.

### Step 3 — Score each dimension

Use this 1–5 scale (5 = lowest risk):

| Score | Meaning |
|---|---|
| 5 | No concerns identified |
| 4 | Minor concerns, low impact |
| 3 | Moderate concerns, mitigations available |
| 2 | Significant concerns, requires documented exception |
| 1 | Disqualifying — do not use without explicit waiver |

Score these dimensions:
- Security posture (CVE history, patch cadence)
- Supply chain integrity (provenance, signing, reproducibility)
- Maintainership health (activity, bus factor, disclosure policy)
- License compatibility (see below)
- CUI suitability (does the library handle, transmit, or log data in ways that touch CUI?)

### Step 4 — License Evaluation

License risk is a separate compliance dimension from security. For federal contractor work:

**Generally acceptable (confirm with legal if in doubt)**
- MIT, Apache 2.0, BSD-2/3-Clause, ISC, WTFPL, Unlicense, CC0

**Requires review**
- LGPL — copyleft applies to the library itself; acceptable if used as a dynamic dependency, review if statically linked
- MPL 2.0 — file-level copyleft; acceptable in most cases
- EPL 1.0/2.0 — review required, especially for commercial deliverables

**Likely disqualifying for proprietary LANL deliverables**
- GPL v2/v3 — strong copyleft, contaminates linked code
- AGPL v3 — network-use copyleft, extremely broad
- SSPL — controversial, may not be OSI-approved
- No license stated — all rights reserved by default; do not use

**Also check:**
- Commercial use restrictions (some "open source" licenses prohibit it)
- Attribution requirements (some require NOTICE file propagation)
- Patent clauses (Apache 2.0 includes an explicit patent grant; MIT does not)

### Step 5 — SBOM Considerations

An SBOM makes the assessment continuous rather than point-in-time. Note in the report:

- Does the library publish its own SBOM?
- Has an SBOM been generated for the consuming project?
- What tooling is available given the deployment context?

**Recommended tooling by context:**

| Context | Tool | Notes |
|---|---|---|
| .NET / NuGet (online) | `dotnet sbom-tool` (Microsoft) | Generates CycloneDX or SPDX; runs offline after install |
| .NET / NuGet (Yellow Network) | `dotnet list package --vulnerable` | Built-in, no external calls; lower fidelity |
| Python (online) | `syft` + `grype` (Anchore) | Full SBOM + CVE scan; supports offline DB snapshots |
| Any (CI/CD) | `syft` in pipeline | Artifact attached to each build |

For Yellow Network / air-gapped environments: pre-download vulnerability DB snapshots and use offline mode. `grype` and `syft` both support `--db-only` and offline snapshot patterns.

### Step 6 — Write the report

Use the template in `references/report-template.md`. Key sections:

1. **Header** — package, version, date, classification marking, assessor
2. **Executive summary** — recommendation (Approve / Approve with conditions / Reject) and one-paragraph rationale
3. **Dimension scores** — scored table with brief justification per dimension
4. **Findings** — detailed narrative per dimension
5. **License analysis** — SPDX ID, risk tier, and compatibility notes
6. **Supply chain notes** — SBOM availability, provenance summary
7. **Mitigations** (if Approve with conditions) — specific controls required before use
8. **References** — NVD links, repo URL, advisory DB entries

---

## Output Format

The report is Confluence-ready Markdown. Use:
- `##` for section headers (renders as H2 in Confluence)
- Markdown tables for scores and license data
- Inline code for package names, CVE IDs, SPDX identifiers
- Blockquote `>` for executive summary callout
- Classification marking as a bold header line at the top

---

## Air-Gap and Yellow Network Notes

When operating on or producing artifacts for the LANL Yellow Network:

- Do not include external URLs in the report body that imply live connectivity (e.g., badge URLs, shield.io links)
- NVD lookups should reference the CVE ID only; assessor verifies via approved internal tooling
- SBOM generation must use pre-approved, offline-capable tooling
- No cloud-based dependency scanning services (Snyk, Dependabot) — these require outbound connectivity
- Flag any library that requires internet access at runtime as a potential CUI exfiltration risk

---

## Quick Reference: Red Flags

Flag these immediately — each may be disqualifying or require escalation:

- Active unpatched CVE with CVSS ≥ 7.0
- No response to disclosed vulnerabilities in >90 days
- Primary maintainer is a foreign national from a CISA-designated high-risk jurisdiction
- License is GPL, AGPL, or "no license stated"
- Single-maintainer project with no commits in >12 months
- Dependency on a package with a known typosquatting history
- Binary artifacts in the repo that don't match source (build integrity failure)
- Library makes outbound network calls not documented in its API

---

## Reference Files

- `references/report-template.md` — full Confluence-ready report template
- `references/framework-glossary.md` — plain-language explanations of EO 14028, SSDF, 800-171, 800-161 for stakeholder briefings
- `references/license-matrix.md` — detailed license compatibility matrix for federal contractor use
