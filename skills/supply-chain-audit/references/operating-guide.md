# supply-chain-audit — operating guide

Depth relocated from SKILL.md; load it when the Workflow points here.

## NuGet-Specific Review

For .NET projects, this skill produces management-ready reports combining update analysis with
security findings. Use for "review NuGet packages", "audit .NET dependencies", preparing
compliance/management reports, periodic security reviews, or onboarding to an existing .NET codebase.

**Process:** locate all `.csproj` files → `dotnet list package --outdated` (updates) →
`dotnet list package --vulnerable` (security) → generate the two-part report: Part 1 Packages
Requiring Updates (executive summary, update table, package-by-package business impact), Part 2
Security Vulnerabilities (executive summary, vulnerability table, plain-language risk), plus
Recommendations categorized by urgency (immediate / scheduled / monitor).

**Key references:**
- Report template and review commands: [references/nuget-security-review.md](references/nuget-security-review.md)
- Severity classification and priority matrix: [references/nuget-severity-guidelines.md](references/nuget-severity-guidelines.md)
- Executive summary templates: [references/nuget-executive-summary-templates.md](references/nuget-executive-summary-templates.md)
- Vulnerability databases and scanning tools: [references/vulnerability-sources.md](references/vulnerability-sources.md)
- License compatibility matrix: [references/license-matrix.md](references/license-matrix.md)
