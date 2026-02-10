---
name: supply-chain-audit
description: Software supply chain vulnerability scanning, license compliance analysis, and CVE correlation across NuGet, npm, and pip ecosystems. Provides vulnerability database references, scanning tool guidance, CVSS severity interpretation, and license compatibility matrices for dependency audits.
---

# Supply Chain Audit

> "Trust, but verify -- and in software supply chains, verify everything twice."
> -- Tanya Janca, *Alice and Bob Learn Application Security*

## Core Philosophy

Software supply chain security is not about avoiding dependencies -- it is about understanding the trust decisions you make with every `install`, `add`, or `restore` command. Every dependency is a delegation of trust: you are trusting that the package author writes secure code, that the registry has not been compromised, that no one has published a malicious version, and that the transitive dependencies you never chose are equally trustworthy.

This skill provides the knowledge framework for auditing that trust. It covers three domains: vulnerability scanning (finding known-bad dependencies), license compliance (finding legally incompatible dependencies), and maintenance health (finding abandoned or declining dependencies). Together, these three domains constitute a complete supply chain audit.

**What this skill is:** A reference framework for conducting dependency audits. It provides vulnerability database knowledge, scanning tool guidance, CVSS interpretation, license compatibility rules, and maintenance health heuristics. It is the knowledge layer that the dependency-audit-agent uses to make informed decisions.

**What this skill is not:** A replacement for running actual scanners. This skill tells you what to look for and how to interpret results. The scanning tools themselves (dotnet list package --vulnerable, npm audit, pip-audit) do the actual work.

**Why supply chain audits matter:** In 2021, the Log4Shell vulnerability (CVE-2021-44228) demonstrated that a single transitive dependency could expose hundreds of thousands of applications. The SolarWinds compromise showed that even trusted vendors can be supply chain attack vectors. The ua-parser-js incident showed that npm packages with millions of weekly downloads can be hijacked. Supply chain attacks are not theoretical -- they are the dominant attack vector for modern applications.

**The three pillars of supply chain audit:**

1. **Vulnerability Scanning** -- Are any of my dependencies known to be vulnerable? Which CVEs apply? Are the vulnerable code paths reachable in my application? What is the actual (not theoretical) risk?

2. **License Compliance** -- Are the licenses of my dependencies compatible with my project's distribution model? Are there copyleft licenses that could require source disclosure? Are there license ambiguities that need legal review?

3. **Maintenance Health** -- Are my dependencies actively maintained? Are security issues being addressed? Is the package at risk of abandonment? Are there signs of compromise or takeover?

## Domain Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Every Dependency Is a Trust Decision** | Adding a dependency means trusting the author, the registry, the build pipeline, and every transitive dependency. Make these trust decisions explicit, not accidental. |
| 2 | **Transitive Dependencies Are Your Dependencies** | You did not choose them, but you ship them. A vulnerability in a transitive dependency is your vulnerability. Audit the full tree, not just the top level. |
| 3 | **CVSS Is Context-Free; Your Risk Is Not** | A CVSS 9.8 in unreachable code is less urgent than a CVSS 6.5 in a code path exposed to the internet. Always compute contextual risk, not just raw severity. |
| 4 | **Licenses Are Legal Obligations** | License violations are not technical debt -- they are legal liability. A GPL-3.0 dependency in proprietary distributed software is not a warning; it is a compliance failure that requires remediation. |
| 5 | **Maintenance Health Predicts Future Risk** | A package with no releases in 3 years and 200 open issues is a ticking time bomb. Even if it has no current CVEs, its inability to respond to future vulnerabilities makes it a risk. |
| 6 | **Scanners Find Known Vulnerabilities Only** | Vulnerability scanners check against databases of known CVEs. They cannot find zero-days, logic flaws, or malicious code without a CVE. Scanning is necessary but not sufficient. |
| 7 | **Upgrade Risk Must Be Assessed** | The fix for a vulnerable dependency is usually an upgrade, but upgrades introduce breaking changes. An upgrade that fixes a CVE but breaks the build is not a fix -- it is a different problem. Assess both risks. |
| 8 | **Private Packages Need Extra Scrutiny** | Packages from private feeds are invisible to public vulnerability databases. They may also lack the community review that popular public packages receive. Apply additional review processes to private dependencies. |
| 9 | **Lock Files Are Security Controls** | Lock files pin exact versions and integrity hashes. Without them, builds are non-reproducible and vulnerable to dependency confusion, version substitution, and registry compromises. Treat lock files as security-critical artifacts. |
| 10 | **Audit Regularly, Not Once** | Dependencies change. New CVEs are published daily. Packages are abandoned, compromised, or deprecated. A clean audit today does not guarantee a clean audit next month. Automate recurring audits. |

## Workflow

### Phase 1: Vulnerability Scan

**Objective:** Identify all dependencies with known CVEs.

**Steps:**
1. Run ecosystem-specific vulnerability scanners against the project
2. Parse scanner output for CVE identifiers, affected versions, and severity
3. Cross-reference findings with multiple vulnerability databases for completeness
4. Verify that the installed version falls within the affected version range
5. Document each finding with CVE ID, CVSS score, affected package, and installed version

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

# Yarn
yarn audit --json
yarn outdated --json

# pnpm
pnpm audit --json
```

**Interpreting CVSS Scores:**

| CVSS Range | Severity | Typical Response |
|------------|----------|-----------------|
| 9.0 - 10.0 | Critical | Immediate remediation. Escalate to security team. |
| 7.0 - 8.9 | High | Remediate within current sprint. Assess exploitability. |
| 4.0 - 6.9 | Medium | Schedule remediation. Verify reachability before prioritizing. |
| 0.1 - 3.9 | Low | Track and remediate during maintenance cycles. |

**Contextual Risk Adjustment:**

Raw CVSS does not account for your application's context. Adjust based on:

- **Reachability:** Is the vulnerable code path invoked by your application?
- **Exposure:** Is the application internet-facing, internal, or air-gapped?
- **Data sensitivity:** Does the application handle PII, financial data, or credentials?
- **Exploitability:** Does a public exploit exist? Is it weaponized?
- **Compensating controls:** Do WAFs, network segmentation, or other controls mitigate the risk?

### Phase 2: License Compliance

**Objective:** Verify all dependency licenses are compatible with the project's distribution model.

**Steps:**
1. Extract license information for all direct dependencies
2. Classify each license by type (permissive, weak copyleft, strong copyleft, proprietary)
3. Check compatibility against the project's own license and distribution model
4. Flag any license that requires legal review
5. Document each finding with package name, license type, and compliance status

**License Detection Commands:**

```bash
# npm
npx license-checker --json --production
npx license-checker --onlyAllow "MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC"

# pip
pip-licenses --format=json
pip-licenses --allow-only="MIT License;Apache Software License;BSD License"

# NuGet (manual -- check .nuspec or NuGet gallery)
dotnet list package --format=json
# Then check license info on nuget.org for each package

# Yarn
yarn licenses list --json
```

**License Classification:**

| Category | Licenses | Corporate Risk |
|----------|----------|---------------|
| Permissive | MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Unlicense | Low -- generally safe for all distribution models |
| Weak Copyleft | LGPL-2.1, LGPL-3.0, MPL-2.0, EPL-2.0 | Medium -- safe for dynamic linking, restrictions on modifications to the library itself |
| Strong Copyleft | GPL-2.0, GPL-3.0, AGPL-3.0 | High -- may require source disclosure for distributed software, AGPL extends to network use |
| Proprietary / Custom | Commercial, EULA-based, custom terms | Requires legal review -- terms vary by vendor |
| No License / Unknown | Unlisted, NOASSERTION | High -- no license means no permission to use. Treat as proprietary until clarified. |

### Phase 3: Maintenance Health

**Objective:** Assess the ongoing viability and security responsiveness of each dependency.

**Steps:**
1. Check the last release date for each direct dependency
2. Review the issue tracker for open security issues and response times
3. Check for deprecation or archival notices
4. Assess contributor activity (bus factor, corporate backing)
5. Document health status with evidence

**Health Indicators:**

| Indicator | Healthy | Concerning | Critical |
|-----------|---------|------------|----------|
| Last release | < 6 months | 6 months - 2 years | > 2 years |
| Open security issues | 0 | 1-2 with responses | 3+ or unresponded |
| Contributor count | 5+ active | 2-4 active | 1 or none active |
| Download trend | Stable or growing | Declining | Abandoned or forked |
| Repository status | Active | Reduced activity | Archived or deleted |
| Deprecation notice | None | Planned | Announced or in effect |

**Health Check Commands:**

```bash
# npm -- check package metadata
npm view <package> time --json    # release dates
npm view <package> repository     # repo URL for manual review

# pip -- check PyPI metadata
pip show <package>                # basic info
pip index versions <package>      # available versions

# NuGet -- check nuget.org
dotnet list package --outdated    # version comparison
# Manual: check nuget.org/<package> for deprecation banners
```

## Output Templates

### Vulnerability Report

```markdown
## Vulnerability Scan Results

**Project:** [path]
**Scan Date:** [date]
**Scanners Used:** [list]

### Critical Findings

| CVE | Package | Installed | Fixed In | CVSS | Reachable | Contextual Risk |
|-----|---------|-----------|----------|------|-----------|-----------------|
| [id] | [pkg@ver] | [ver] | [ver] | [score] | [yes/no/unknown] | [CRITICAL/HIGH/MEDIUM/LOW] |

### Finding Detail: [CVE-ID]

**Package:** [name] v[version]
**Vulnerability:** [brief description]
**CVSS Score:** [score] ([vector string])
**Affected Versions:** [range]
**Fixed Version:** [version]

**Reachability Analysis:**
- Import locations: [files that import the package]
- Vulnerable component: [specific module/class/function]
- Usage in project: [how the project uses the vulnerable component]
- Code path reachable: [yes/no with reasoning]

**Contextual Risk:** [CRITICAL/HIGH/MEDIUM/LOW]
**Rationale:** [why the contextual risk differs from raw CVSS, if applicable]

**Remediation:**
- Upgrade to [version]: [breaking change risk assessment]
- Alternative: [if upgrade is not straightforward]
```

### License Compliance Report

```markdown
## License Compliance Report

**Project:** [path]
**Distribution Model:** [SaaS / On-premise / Library / Open Source]
**Project License:** [license]

### License Summary

| License | Count | Compatibility | Action |
|---------|-------|---------------|--------|
| MIT | [N] | Compatible | None |
| Apache-2.0 | [N] | Compatible (notice required) | Verify NOTICE file |
| GPL-3.0 | [N] | REVIEW REQUIRED | See details |

### Findings Requiring Review

**Package:** [name]
**License:** [license]
**Issue:** [specific compatibility concern]
**Risk:** [BLOCKING / WARNING / ACCEPTABLE]
**Recommendation:** [specific action]
```

### Maintenance Health Report

```markdown
## Dependency Health Report

**Project:** [path]
**Direct Dependencies:** [N]

### Health Summary

| Status | Count | Packages |
|--------|-------|----------|
| Healthy | [N] | [list] |
| Aging | [N] | [list] |
| Stale | [N] | [list] |
| Deprecated | [N] | [list] |

### Concern: [Package Name]

**Last Release:** [date] ([N] months ago)
**Open Issues:** [N] total, [N] security-related
**Contributors:** [N] active in last 12 months
**Status:** [HEALTHY / DECLINING / ABANDONED]
**Risk:** [description of what happens if a vulnerability is found]
**Recommendation:** [continue using / plan migration / migrate immediately]
**Alternatives:** [list of actively maintained alternatives, if applicable]
```

## State Block

Maintain state across conversation turns:

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

### ALWAYS verify CVE applicability before reporting severity

A CVE exists in a database. Whether it affects your project depends on the installed version, the code paths used, and the deployment context. Never report raw CVSS as project risk. Always include version verification and reachability analysis. When reachability cannot be determined, say so explicitly rather than assuming worst case.

### ALWAYS check license compatibility against the actual distribution model

MIT is compatible with everything. GPL-3.0 is compatible with some things. But compatibility depends on how the software is distributed. A GPL-3.0 dependency in a SaaS application that is never distributed may be acceptable. The same dependency in a desktop application that ships to customers is a compliance issue. Ask about the distribution model before declaring a license incompatible.

### NEVER recommend upgrades without assessing breaking change risk

"Upgrade to the latest version" is not a recommendation -- it is a wish. A recommendation includes: the specific target version, the semantic versioning delta (patch/minor/major), known breaking changes from the changelog, impact on other dependencies in the tree, and an honest risk assessment. If the upgrade is riskier than the vulnerability, say so.

### ALWAYS distinguish between scanner limitations and clean results

"No vulnerabilities found" is not the same as "no vulnerabilities exist." Scanners check against known CVE databases. Zero-days, logic flaws, and malicious code without CVE entries will not be detected. When reporting a clean scan, always note what was scanned, what was not, and what the scanner cannot detect.

### Present maintenance health with evidence, not judgment

Do not say "this package is poorly maintained." Say "this package has not had a release since March 2023, has 47 open issues including 3 labeled 'security,' and its sole maintainer has not committed in 8 months." Evidence allows the human to make their own judgment about acceptable risk.

### Treat lock files as security-critical artifacts

If a project lacks lock files, flag this as a supply chain risk before proceeding with any other analysis. Without lock files, builds are non-reproducible, dependency resolution is non-deterministic, and the project is vulnerable to dependency confusion and version substitution attacks.

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|------------------|
| **CVSS-Only Prioritization** | Sorting by CVSS score ignores reachability, exposure, and compensating controls. A CVSS 9.8 in dead code is less urgent than a CVSS 6.5 in a public API. | Compute contextual risk using CVSS as one input alongside reachability, exposure, and data sensitivity. |
| **License Panic** | Flagging every non-MIT license as a problem creates noise and erodes trust in the audit. LGPL, MPL, and Apache-2.0 are safe for most commercial use. | Classify licenses by category, check against the actual distribution model, and only flag genuine incompatibilities. |
| **Upgrade Everything** | Mass-upgrading all dependencies to latest introduces unnecessary breaking change risk and testing burden. | Prioritize upgrades by vulnerability severity and contextual risk. Patch upgrades for CVE fixes. Planned upgrades for outdated packages. |
| **Ignoring Transitives** | Auditing only direct dependencies misses the vast majority of the dependency tree. Most vulnerabilities are in transitive dependencies. | Audit the full tree. Use lock files and --include-transitive flags. Distinguish direct from transitive in reporting. |
| **One-Time Audit** | A single audit provides a snapshot. Dependencies change, new CVEs are published daily, and packages are compromised over time. | Establish recurring audits (weekly or on every CI build). Track trends, not just point-in-time results. |
| **Scanner as Oracle** | Treating scanner output as the complete truth. Scanners miss zero-days, have false positives, and may not cover all ecosystems. | Use scanners as one input. Cross-reference multiple databases. Apply manual review for critical dependencies. |

## Error Recovery

### Scanner Fails to Run

**Symptoms:** Command not found, permission denied, network timeout.

**Recovery:**
1. Check if the tool is installed: `which dotnet`, `which npm`, `which pip-audit`
2. If missing, report the gap and suggest installation
3. Try alternative scanners for the same ecosystem
4. Continue with available tools; note the gap in the report
5. Never skip an ecosystem entirely due to a single tool failure

### Conflicting CVE Data Across Databases

**Symptoms:** NVD says CRITICAL, GitHub Advisory says HIGH, or one database has the CVE and another does not.

**Recovery:**
1. Report all severity ratings with their sources
2. Use the highest severity for initial prioritization
3. Note the discrepancy for human review
4. If the CVE is disputed, include the dispute context
5. Let the human make the final severity determination

### License Information Unavailable

**Symptoms:** Package has no license metadata, or license field says "UNLICENSED" or "SEE LICENSE IN LICENSE".

**Recovery:**
1. Check the package repository for a LICENSE file
2. Check the registry page (nuget.org, npmjs.com, pypi.org) for license info
3. If truly unlicensed: flag as HIGH risk -- no license means no permission
4. If custom license: flag for legal review with a link to the license text
5. Never assume a license; absence of license is not MIT

## Integration

### Cross-Skill References

- **dependency-mapper** -- Use dependency-mapper to understand the structural implications of dependencies before auditing them. Coupling metrics reveal which dependencies are most deeply embedded and hardest to replace, which affects remediation planning.

- **technical-debt-assessor** -- Dependency debt is one of the six categories in the debt taxonomy. Outdated packages, license risks, and abandoned dependencies are quantifiable debt items with cost-to-fix and cost-to-carry. Use the debt assessor framework to build business cases for dependency upgrades.

- **security-review-trainer** -- Supply chain vulnerabilities (A06:2021 - Vulnerable and Outdated Components) are part of the OWASP Top 10. The security review trainer covers these from a code review perspective; this skill covers them from a dependency audit perspective.

- **architecture-review** -- Dependency choices are architectural decisions. A decision to depend on a specific framework or library constrains the system's evolution. Use architecture-review to evaluate whether a dependency aligns with the system's architectural direction.

### Stack-Specific Guidance

Detailed reference materials for applying these concepts:

- [Vulnerability Sources](references/vulnerability-sources.md) -- Vulnerability databases (NVD, GitHub Advisory, OSV), scanning tools per ecosystem, CVE severity scoring with CVSS, and cross-database correlation techniques
- [License Matrix](references/license-matrix.md) -- License compatibility matrix for common open-source licenses, corporate policy considerations, copyleft risk assessment, and distribution model analysis
