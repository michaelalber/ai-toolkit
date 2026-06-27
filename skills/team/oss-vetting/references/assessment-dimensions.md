# Assessment Dimensions, Scoring, and Operational Notes

Operational depth for the `oss-vetting` skill. Loaded just-in-time during the RESEARCH,
SCORE, and SBOM phases. SKILL.md carries the lean workflow; this file carries the detail.

---

## Step inputs — gather before starting

- Package name, version, ecosystem (NuGet / PyPI / npm / other)
- Target system: CUI-adjacent? Yellow Network? Air-gapped?
- Intended use — what does this library do in the application?
- Constraints — license-type requirements, air-gap tooling limits

If context is missing, ask. A vague request produces a shallow report.

---

## Research dimensions

Research across these dimensions. Use web search if available; note limitations if air-gapped.

### Identity and provenance (C-SCRM)
- Official source URL (NuGet.org, PyPI, GitHub)
- License — SPDX identifier (see `license-matrix.md`)
- Primary maintainer(s): individual, company, or foundation?
- Funding / ownership: any foreign-government or high-risk-jurisdiction involvement?
- First published and last updated
- Download / adoption stats (proxy for community health)

### Security posture
- Known CVEs — check NVD (nvd.nist.gov) and the ecosystem's advisory DB
- Time-to-patch history: how quickly are vulnerabilities addressed?
- Vulnerability disclosure policy: is there a `SECURITY.md` or equivalent?
- Release signing: are releases signed or hash-verified?
- Dependency count and depth (transitive attack surface)

### Development health (SSDF alignment)
- Active maintainership: recent commits, responsive issues?
- Changelog / release notes maintained?
- CI/CD visible in repo (green builds = active hygiene)?
- Contributor diversity or bus-factor risk (single-maintainer = high risk)?

### Supply chain factors (C-SCRM)
- Build reproducibility: can the binary be verified against source?
- Dependency pinning practices
- Known typosquatting or name-confusion risk
- Published SBOM (CycloneDX or SPDX)? If yes, attach or reference.

---

## Scoring scale

Score each dimension 1–5 (5 = lowest risk):

| Score | Meaning |
|---|---|
| 5 | No concerns identified |
| 4 | Minor concerns, low impact |
| 3 | Moderate concerns, mitigations available |
| 2 | Significant concerns, requires documented exception |
| 1 | Disqualifying — do not use without explicit waiver |

Score these dimensions:
- **Security posture** — CVE history, patch cadence
- **Supply chain integrity** — provenance, signing, reproducibility
- **Maintainership health** — activity, bus factor, disclosure policy
- **License compatibility** — see `license-matrix.md`
- **CUI suitability** — does the library handle, transmit, or log data in ways that touch CUI?

---

## SBOM considerations

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

For Yellow Network / air-gapped environments: pre-download vulnerability DB snapshots and use
offline mode. `grype` and `syft` both support `--db-only` and offline snapshot patterns.

---

## Air-Gap and Yellow Network notes

When operating on or producing artifacts for the LANL Yellow Network:

- Do not include external URLs in the report body that imply live connectivity
  (e.g., badge URLs, shield.io links)
- NVD lookups should reference the CVE ID only; assessor verifies via approved internal tooling
- SBOM generation must use pre-approved, offline-capable tooling
- No cloud-based dependency scanning services (Snyk, Dependabot) — these require outbound connectivity
- Flag any library that requires internet access at runtime as a potential CUI exfiltration risk

---

## Quick reference: red flags

Flag these immediately — each may be disqualifying or require escalation:

- Active unpatched CVE with CVSS ≥ 7.0
- No response to disclosed vulnerabilities in >90 days
- Primary maintainer is a foreign national from a CISA-designated high-risk jurisdiction
- License is GPL, AGPL, or "no license stated"
- Single-maintainer project with no commits in >12 months
- Dependency on a package with a known typosquatting history
- Binary artifacts in the repo that don't match source (build integrity failure)
- Library makes outbound network calls not documented in its API
