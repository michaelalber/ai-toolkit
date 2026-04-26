---
name: supply-chain-audit
description: Software supply chain vulnerability scanning, license compliance analysis, and CVE correlation across NuGet, npm, and pip ecosystems. Provides vulnerability database references, scanning tool guidance, CVSS severity interpretation, and license compatibility matrices for dependency audits. Also performs NuGet package security reviews with manager-friendly executive summaries. Use when asked to audit package dependencies, scan for vulnerabilities, check license compliance, or assess supply chain security. Trigger phrases: "review nuget", "package security", "nuget audit", "outdated packages", "vulnerability scan", "check dependencies", "supply chain audit".
---

# Supply Chain Audit

> "Trust, but verify -- and in software supply chains, verify everything twice."
> -- Tanya Janca, *Alice and Bob Learn Application Security*

## Core Philosophy

Software supply chain security is not about avoiding dependencies -- it is about understanding the trust decisions you make with every `install`, `add`, or `restore` command. Every dependency is a delegation of trust: you are trusting that the package author writes secure code, that the registry has not been compromised, that no one has published a malicious version, and that the transitive dependencies you never chose are equally trustworthy.

**The three pillars of supply chain audit:**
1. **Vulnerability Scanning** -- Are any dependencies known to be vulnerable? Which CVEs apply? Are the vulnerable code paths reachable?
2. **License Compliance** -- Are the licenses compatible with the project's distribution model? Are there copyleft licenses that require source disclosure?
3. **Maintenance Health** -- Are dependencies actively maintained? Are security issues being addressed? Is the package at risk of abandonment?

## Domain Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Every Dependency Is a Trust Decision** | Adding a dependency means trusting the author, the registry, the build pipeline, and every transitive dependency. Make these trust decisions explicit, not accidental. |
| 2 | **Transitive Dependencies Are Your Dependencies** | You did not choose them, but you ship them. A vulnerability in a transitive dependency is your vulnerability. Audit the full tree, not just the top level. |
| 3 | **CVSS Is Context-Free; Your Risk Is Not** | A CVSS 9.8 in unreachable code is less urgent than a CVSS 6.5 in a code path exposed to the internet. Always compute contextual risk, not just raw severity. |
| 4 | **Licenses Are Legal Obligations** | A GPL-3.0 dependency in proprietary distributed software is not a warning; it is a compliance failure that requires remediation. |
| 5 | **Maintenance Health Predicts Future Risk** | A package with no releases in 3 years and 200 open issues cannot respond to future vulnerabilities. Even with no current CVEs, it is a risk. |
| 6 | **Scanners Find Known Vulnerabilities Only** | Scanners check against databases of known CVEs. They cannot find zero-days, logic flaws, or malicious code without a CVE. Scanning is necessary but not sufficient. |
| 7 | **Upgrade Risk Must Be Assessed** | The fix for a vulnerable dependency is usually an upgrade, but upgrades introduce breaking changes. Assess both risks before recommending. |
| 8 | **Private Packages Need Extra Scrutiny** | Packages from private feeds are invisible to public vulnerability databases and lack community review. Apply additional review processes. |
| 9 | **Lock Files Are Security Controls** | Without lock files, builds are non-reproducible and vulnerable to dependency confusion, version substitution, and registry compromises. |
| 10 | **Audit Regularly, Not Once** | Dependencies change. New CVEs are published daily. Packages are abandoned, compromised, or deprecated. Automate recurring audits. |

## Knowledge Base Lookups

| Query | When to Call |
|-------|--------------|
| `search_knowledge("OWASP vulnerable outdated components supply chain")` | During Phase 1 — grounding CVE findings in OWASP A06:2021 context |
| `search_knowledge("CVSS score severity vulnerability assessment")` | During Phase 1 — interpreting CVSS scores and contextual risk |
| `search_knowledge("software license MIT Apache GPL compatibility")` | During Phase 2 — classifying license compatibility |
| `search_knowledge("NuGet package security dotnet vulnerable")` | During NuGet review — grounding .NET-specific vulnerability patterns |
| `search_knowledge("npm audit pip-audit dependency scanning")` | During Phase 1 — selecting and interpreting ecosystem-specific scanners |
| `search_knowledge("NIST 800-218 secure software supply chain")` | For federal/compliance context — SSDF supply chain controls |
| `search_code_examples("dotnet list package vulnerable NuGet")` | Before running .NET scans — correct scanner invocation patterns |

**Protocol:** Search `gov` for federal/NIST compliance context. Search `dotnet` for .NET-specific scanner guidance. Search `python` for pip-audit patterns. Cite source paths from KB results.

## Workflow

### Phase 1: Vulnerability Scan

**Objective:** Identify all dependencies with known CVEs.

**Scanner Commands:**

```bash
# NuGet (.NET)
dotnet list package --vulnerable --include-transitive
dotnet list package --outdated

# npm (Node.js)
npm audit --json
npm audit --audit-level=moderate
npm outdated --json

# pip (Python)
pip-audit --format=json
pip-audit --fix --dry-run
pip list --outdated --format=json

# Yarn / pnpm
yarn audit --json
pnpm audit --json
```

**CVSS Severity:**

| CVSS Range | Severity | Typical Response |
|------------|----------|-----------------|
| 9.0–10.0 | Critical | Immediate remediation. Escalate to security team. |
| 7.0–8.9 | High | Remediate within current sprint. Assess exploitability. |
| 4.0–6.9 | Medium | Schedule remediation. Verify reachability before prioritizing. |
| 0.1–3.9 | Low | Track and remediate during maintenance cycles. |

**Contextual Risk Adjustment:** Adjust raw CVSS based on reachability (is the vulnerable code path invoked?), exposure (internet-facing vs. internal vs. air-gapped), data sensitivity (PII, financial, credentials), exploitability (public exploit available?), and compensating controls (WAF, network segmentation).

### Phase 2: License Compliance

**Objective:** Verify all dependency licenses are compatible with the project's distribution model.

**License Detection Commands:**

```bash
# npm
npx license-checker --json --production
npx license-checker --onlyAllow "MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC"

# pip
pip-licenses --format=json
pip-licenses --allow-only="MIT License;Apache Software License;BSD License"

# NuGet -- check .nuspec or NuGet gallery manually
dotnet list package --format=json
```

**License Classification:**

| Category | Licenses | Corporate Risk |
|----------|----------|---------------|
| Permissive | MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Unlicense | Low |
| Weak Copyleft | LGPL-2.1, LGPL-3.0, MPL-2.0, EPL-2.0 | Medium — restrictions on modifications to the library itself |
| Strong Copyleft | GPL-2.0, GPL-3.0, AGPL-3.0 | High — may require source disclosure; AGPL extends to network use |
| Proprietary / Custom | Commercial, EULA-based, custom terms | Requires legal review |
| No License / Unknown | Unlisted, NOASSERTION | High — no license means no permission to use |

### Phase 3: Maintenance Health

**Objective:** Assess the ongoing viability and security responsiveness of each dependency.

**Health Indicators:**

| Indicator | Healthy | Concerning | Critical |
|-----------|---------|------------|----------|
| Last release | < 6 months | 6 months–2 years | > 2 years |
| Open security issues | 0 | 1–2 with responses | 3+ or unresponded |
| Contributor count | 5+ active | 2–4 active | 1 or none active |
| Repository status | Active | Reduced activity | Archived or deleted |

**Health Check Commands:**

```bash
# npm
npm view <package> time --json     # release dates
npm view <package> repository      # repo URL for manual review

# pip
pip show <package>                 # basic info

# NuGet
dotnet list package --outdated     # version comparison
```

## Output Templates

| Template | Required Fields |
|----------|----------------|
| Vulnerability Report | Project, Scan Date, Scanners Used; Critical Findings table (CVE / Package / Installed / Fixed In / CVSS / Reachable / Contextual Risk); per-CVE detail (Reachability Analysis, Contextual Risk, Rationale, Remediation) |
| License Compliance Report | Project, Distribution Model, Project License; License Summary table (License / Count / Compatibility / Action); Findings Requiring Review (Package / License / Issue / Risk / Recommendation) |
| Maintenance Health Report | Project, Direct Dependencies count; Health Summary table (Status / Count / Packages); per-concern detail (Last Release, Open Issues, Contributors, Status, Risk, Recommendation, Alternatives) |

Full templates: `references/vulnerability-sources.md` | `references/license-matrix.md` | `references/nuget-security-review.md`

## State Block

```
<supply-chain-state>
mode: scan | license | health | report
project_path: [absolute path to project root]
ecosystems: [NuGet, npm, pip, etc.]
dependencies_scanned: [count]
cves_found: [count]
license_issues: [count]
health_concerns: [count]
last_action: [what was just completed]
next_action: [what should happen next]
</supply-chain-state>
```

## AI Discipline Rules

**Always verify CVE applicability before reporting severity:** A CVE exists in a database. Whether it affects a project depends on the installed version, the code paths used, and the deployment context. Never report raw CVSS as project risk. Include version verification and reachability analysis. When reachability cannot be determined, say so explicitly.

**Always check license compatibility against the actual distribution model:** MIT is compatible with everything. GPL-3.0 compatibility depends on how the software is distributed. A GPL-3.0 dependency in a SaaS application may be acceptable. The same dependency in a desktop application shipped to customers is a compliance issue. Ask about the distribution model before declaring a license incompatible.

**Never recommend upgrades without assessing breaking change risk:** A recommendation includes the specific target version, the semantic versioning delta, known breaking changes from the changelog, impact on other dependencies in the tree, and an honest risk assessment. If the upgrade is riskier than the vulnerability, say so.

**Always distinguish between scanner limitations and clean results:** "No vulnerabilities found" is not "no vulnerabilities exist." When reporting a clean scan, note what was scanned, what was not, and what the scanner cannot detect (zero-days, logic flaws, malicious code without CVE entries).

**Present maintenance health with evidence, not judgment:** Say "this package has not had a release since March 2023, has 47 open issues including 3 labeled 'security,' and its sole maintainer has not committed in 8 months" — not "this package is poorly maintained." Evidence allows the human to make their own judgment.

**Treat lock files as security-critical artifacts:** If a project lacks lock files, flag this as a supply chain risk before any other analysis. Without lock files, builds are non-reproducible and vulnerable to dependency confusion attacks.

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|------------------|
| **CVSS-Only Prioritization** | Ignores reachability, exposure, and compensating controls | Compute contextual risk using CVSS as one input alongside reachability and data sensitivity |
| **License Panic** | Flagging every non-MIT license creates noise; LGPL, MPL, Apache-2.0 are safe for most commercial use | Classify by category, check against actual distribution model, flag genuine incompatibilities only |
| **Upgrade Everything** | Mass-upgrades introduce unnecessary breaking change risk | Prioritize upgrades by contextual risk; patch for CVE fixes, plan for outdated packages |
| **Ignoring Transitives** | Most vulnerabilities are in transitive dependencies | Audit the full tree with `--include-transitive` flags; distinguish direct from transitive in reporting |
| **One-Time Audit** | Dependencies change and new CVEs are published daily | Establish recurring audits (weekly or on every CI build) |
| **Scanner as Oracle** | Scanners miss zero-days, have false positives, and may not cover all ecosystems | Cross-reference multiple databases; apply manual review for critical dependencies |

## Error Recovery

**Scanner Fails to Run:** Check if the tool is installed (`which dotnet`, `which npm`, `which pip-audit`). Try alternative scanners for the same ecosystem. Continue with available tools and note the gap in the report. Never skip an ecosystem entirely due to a single tool failure.

**Conflicting CVE Data Across Databases:** Report all severity ratings with their sources. Use the highest severity for initial prioritization. Note the discrepancy for human review. If the CVE is disputed, include the dispute context. Let the human make the final severity determination.

**License Information Unavailable:** Check the package repository for a LICENSE file. Check the registry page (nuget.org, npmjs.com, pypi.org) for license info. If truly unlicensed, flag as HIGH risk — no license means no permission. If a custom license, flag for legal review with a link to the license text. Never assume a license.

## Integration

- **dependency-mapper** -- use to understand structural implications of dependencies before auditing. Coupling metrics reveal which dependencies are most deeply embedded and hardest to replace.
- **technical-debt-assessor** -- outdated packages, license risks, and abandoned dependencies are quantifiable debt items with cost-to-fix and cost-to-carry.
- **security-review-trainer** -- supply chain vulnerabilities (OWASP A06:2021) from a code review perspective; this skill covers them from a dependency audit perspective.
- **architecture-review** -- dependency choices are architectural decisions that constrain the system's evolution.

## NuGet-Specific Review

For .NET projects, this skill produces management-ready reports combining update analysis with security findings.

**When to use:** "review NuGet packages", "audit .NET dependencies", preparing reports for management or compliance, periodic security reviews, onboarding to an existing .NET codebase.

**Process:**
1. Locate all `.csproj` files in the solution
2. Run `dotnet list package --outdated` for update analysis
3. Run `dotnet list package --vulnerable` for security analysis
4. Generate the two-part report using the template in [nuget-security-review.md](references/nuget-security-review.md)

**Report structure:** Part 1: Packages Requiring Updates (executive summary, update details table, package-by-package summaries with business impact) | Part 2: Security Vulnerabilities (executive summary, vulnerability details table, risk explanations in plain language) | Summary & Recommendations (categorized by urgency: immediate / scheduled / monitor).

**Key references:**
- Report template and review commands: [references/nuget-security-review.md](references/nuget-security-review.md)
- Severity classification and priority matrix: [references/nuget-severity-guidelines.md](references/nuget-severity-guidelines.md)
- Executive summary templates: [references/nuget-executive-summary-templates.md](references/nuget-executive-summary-templates.md)
- Vulnerability databases and scanning tools: [references/vulnerability-sources.md](references/vulnerability-sources.md)
- License compatibility matrix: [references/license-matrix.md](references/license-matrix.md)
