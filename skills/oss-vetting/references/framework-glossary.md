# Governing Framework Glossary

Plain-language explanations for manager and stakeholder briefings. These can be copied directly into Confluence pages or email summaries.

---

## EO 14028 — Executive Order on Improving the Nation's Cybersecurity

**Issued:** May 2021  
**Scope:** National policy mandate

EO 14028 is the federal government's top-level cybersecurity directive, issued in the aftermath of high-profile software supply chain attacks (SolarWinds, Log4Shell). It holds every federal agency and their contractors responsible for the security posture of the software they use and ship.

**Why it matters for Denali:** This is the authority that makes OSS vetting non-optional. It directed NIST and CISA to define minimum SBOM elements and pushed "secure by design" requirements down to contractors. Without EO 14028, vetting would be a best practice. With it, it's a contractual obligation.

---

## NIST SP 800-218 — Secure Software Development Framework (SSDF)

**Scope:** Development process and practice

The SSDF defines how development teams should behave across four areas:

1. **Prepare the organization** — policies, roles, tooling
2. **Protect the software** — source control, build pipeline integrity
3. **Produce well-secured software** — design, testing, vulnerability response
4. **Respond to vulnerabilities** — disclosure policy, patching cadence

When evaluating an OSS library, we check whether its maintainers follow practices consistent with the SSDF — things like whether they maintain a changelog, sign releases, respond to CVEs, and have a public vulnerability disclosure process.

**Key practices referenced in vetting:**
- `PS.3` — Track and document the provenance of all software components
- `PW.4` — Reuse existing, well-secured software where possible
- `RV.1` — Identify and confirm vulnerabilities
- `RV.2` — Assess, prioritize, and remediate vulnerabilities

---

## NIST SP 800-171 Rev 2 — Protecting CUI in Nonfederal Systems

**Scope:** Data protection controls for contractor systems

CUI (Controlled Unclassified Information) covers most of what LANL handles — personnel records, training data, organizational structures, location data, and similar. This standard defines **110 security controls** across 14 control families that any contractor whose systems touch CUI must implement.

**Why it matters for OSS vetting:** A library with known vulnerabilities, poor update cadence, or opaque ownership is a direct 110-control compliance liability. The question the vetting report answers is: *does this library introduce risk to the systems that store or process CUI?*

**Relevant control families:**
- SI (System and Information Integrity) — covers malicious code protection, security alerts, software flaws
- SA (System and Services Acquisition) — covers supply chain protection, external system services
- CM (Configuration Management) — covers software usage restrictions and user-installed software

---

## NIST SP 800-161 — Cybersecurity Supply Chain Risk Management (C-SCRM)

**Scope:** Third-party and open-source component provenance

C-SCRM asks: Where did this software come from? Who maintains it? Is there a single point of failure in its dependency chain? Could a compromised maintainer or nation-state actor push malicious code into it?

This framework makes OSS provenance — origin, ownership, contributor geography, license terms, maintainership health — a compliance question, not just a preference.

**Why it matters for OSS vetting:** It is why the assessment looks at:
- Whether a library has active, responsive maintainership
- Whether its primary maintainers or funding sources introduce geopolitical risk
- Whether its dependency chain is auditable
- Whether the license is compatible with federal contractor use
- Whether build artifacts can be verified against source (reproducible builds)

---

## Classification Marking: UNCLASSIFIED // FOR OFFICIAL USE — CONTRACTOR SENSITIVE

This is not boilerplate. It signals that the document contains vendor evaluation details, internal risk scoring, and procurement-relevant analysis that should not circulate outside the Denali/LANL working relationship — even though the content is not classified in the national security sense.

Distribution should be limited to Denali staff working on LANL contracts and authorized LANL counterparts.

---

## What is an SBOM?

A Software Bill of Materials (SBOM) is a formal, machine-readable inventory of every software component inside an application — first-party code, open-source libraries, transitive dependencies, and the relationships between them.

**The analogy that works:** A nutrition label for software. Just as a food manufacturer must list every ingredient and its origin, EO 14028 effectively requires software suppliers to disclose every component and its provenance.

**Why it matters:** Without an SBOM, the OSS vetting report is a point-in-time snapshot. With one, it becomes a living, queryable record. When a new CVE drops against a transitive dependency six months later, an SBOM tells you in seconds whether you're affected and in which systems.

**Standard formats:**
- **CycloneDX** (OWASP) — preferred for security-focused use cases
- **SPDX** (Linux Foundation, ISO/IEC 5962:2021) — broader adoption, strong license data

**Minimum SBOM elements (per NTIA/CISA):**
- Component name and version
- Supplier name
- Unique identifier (package URL / PURL)
- Dependency relationships
- Author and timestamp
- SBOM format and version
