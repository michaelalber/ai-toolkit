# OSS Vetting Assessment Report Template

Use this template verbatim. Replace all `[bracketed]` fields.

---

**UNCLASSIFIED // FOR OFFICIAL USE — CONTRACTOR SENSITIVE**

# OSS Vetting Assessment Report

| Field | Value |
|---|---|
| **Package** | `[package-name]` v`[version]` |
| **Ecosystem** | [NuGet / PyPI / npm / other] |
| **Assessment date** | [YYYY-MM-DD] |
| **Assessor** | [Name], Denali Data Systems |
| **Target system** | [System name / LANL Yellow Network / etc.] |
| **Governing frameworks** | EO 14028 · NIST SP 800-218 (SSDF) · NIST SP 800-171 Rev 2 · NIST SP 800-161 |

---

## Executive Summary

> **Recommendation: [APPROVE / APPROVE WITH CONDITIONS / REJECT]**
>
> [One paragraph. State the recommendation, the primary reason, and any material conditions or caveats. Write for a non-technical manager.]

---

## Dimension Scores

| Dimension | Score (1–5) | Summary |
|---|---|---|
| Security posture | [1–5] | [One line] |
| Supply chain integrity | [1–5] | [One line] |
| Maintainership health | [1–5] | [One line] |
| License compatibility | [1–5] | [One line] |
| CUI suitability | [1–5] | [One line] |
| **Overall** | [avg or lowest] | |

*Score key: 5 = no concerns · 4 = minor · 3 = moderate, mitigations available · 2 = significant, exception required · 1 = disqualifying*

---

## Findings

### Security Posture

**Known vulnerabilities:**
- [CVE-YYYY-XXXXX — CVSS X.X — [Fixed in vX.X / Unpatched] — [Brief description]]
- None identified as of assessment date.

**Patch cadence:** [Description — e.g., "Last CVE patched within 14 days of disclosure."]

**Vulnerability disclosure policy:** [SECURITY.md present / GitHub security advisories enabled / No formal policy]

**Release signing:** [Signed with [key/cert] / Hash-verified on NuGet / Not signed]

### Supply Chain Integrity

**Source:** [`[repo URL]`] — [GitHub / GitLab / self-hosted]

**Publisher:** [Individual / Company / Foundation] — [Name]

**Geopolitical risk:** [None identified / Note if primary maintainer or funding is from CISA-designated jurisdiction]

**Reproducible builds:** [Yes / No / Unknown]

**Published SBOM:** [Yes — CycloneDX [link] / SPDX [link] / No]

**Transitive dependency count:** [N direct, ~N transitive]

### Maintainership Health

**Last commit:** [Date]

**Contributor count:** [N] — [Bus factor assessment: e.g., "Single maintainer — elevated bus factor risk"]

**Issue responsiveness:** [Description]

**CI/CD:** [Visible / Not visible]

**SSDF alignment notes:** [Any notable gaps vs. SSDF PS.3, PW.4, RV.1, etc.]

### License Analysis

**SPDX identifier:** `[MIT / Apache-2.0 / GPL-3.0-only / etc.]`

**Risk tier:** [Acceptable / Requires review / Likely disqualifying]

**Compatibility notes:** [Any conditions — e.g., attribution required, static linking restrictions]

**Patent clause:** [Explicit grant (Apache 2.0) / No explicit grant (MIT) / N/A]

### CUI Suitability

[Does this library touch, transmit, log, or store data at runtime? Does it make network calls? Does it write to disk? Assess whether use in a CUI-adjacent system introduces data handling risk.]

---

## SBOM Notes

| Item | Status |
|---|---|
| Library publishes own SBOM | [Yes / No] |
| Project SBOM generated | [Yes — attached / Pending / Not applicable] |
| SBOM format | [CycloneDX / SPDX / N/A] |
| Tooling used | [`dotnet sbom-tool` / `syft` / other] |
| Offline-capable | [Yes / No — note if Yellow Network constraint applies] |

---

## Mitigations (if Approve with Conditions)

List specific controls that must be in place before this library is used:

1. [e.g., Pin to version X.X.X and lock in lockfile — do not allow floating version]
2. [e.g., Review CVE-YYYY-XXXXX — confirm application code does not exercise the affected code path]
3. [e.g., Generate and attach SBOM to build artifact before deployment]
4. [e.g., Schedule re-assessment in 90 days or on next major release]

---

## References

| Source | Link / Identifier |
|---|---|
| Package source | `[URL]` |
| NVD CVE entries | `[CVE-YYYY-XXXXX]`, `[CVE-YYYY-XXXXX]` |
| Advisory DB | `[GHSA-XXXX-XXXX-XXXX]` |
| License text | `[SPDX license URL]` |
| SBOM artifact | `[Path or N/A]` |

---

*This document contains vendor evaluation details and internal risk scoring. Distribution limited to Denali Data Systems staff on LANL contracts and authorized LANL counterparts.*
