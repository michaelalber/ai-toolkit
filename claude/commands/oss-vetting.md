---
description: Vets an open-source / third-party package for federal contractor use (LANL/DOE/CUI) — security posture, supply chain risk, license compliance, CUI suitability — and produces a Confluence-ready Approve / Approve-with-conditions / Reject report. Use to vet a library, check if a dependency is approved for CUI systems, or run a C-SCRM / 800-171 review. Usage: /oss-vetting <package@version>
allowed-tools: Read, Glob, Grep, Bash(dotnet list package:*), Bash(find:*)
---

<project_dependencies>
!`find . -maxdepth 3 \( -name "*.csproj" -o -name "packages.config" -o -name "requirements*.txt" -o -name "pyproject.toml" -o -name "package.json" -o -name "Cargo.toml" \) 2>/dev/null | grep -v node_modules | head -20`
</project_dependencies>

Use the oss-vetting skill to assess: $ARGUMENTS

If no package is given in $ARGUMENTS, ask which package (name, version, ecosystem) to vet — and the deployment context (CUI-adjacent / Yellow Network / air-gapped / standard) and intended use. The manifests above are context for where the dependency would land; do not assume the deployment classification from them.

Score all five dimensions (security posture, supply chain integrity, maintainership health, license compatibility, CUI suitability) against EO 14028, SSDF, 800-171, and 800-161, resolve the license SPDX ID to a risk tier, note SBOM availability and context-appropriate tooling, run the red-flag checklist, and produce the Confluence-ready report from `references/report-template.md` ending in Approve / Approve with conditions / Reject. Honor air-gap / Yellow Network rules when that is the context.
