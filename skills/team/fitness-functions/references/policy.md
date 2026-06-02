# Fitness Functions — Policy (Conftest / OPA Rego)

Tool: **Conftest** (OPA's Rego engine) — stack-agnostic policy gates over structured config:
Dockerfiles, Kubernetes manifests, Terraform plans, CI YAML, `*.json`/`*.yaml`. Use this when the
architectural rule lives in *configuration* rather than source code.

## 1. Minimal check

Enforce a deployment ADR — containers must not run as root and must pin an image digest:

```rego
# policy/deployment.rego — gates ADR-0007: non-root, pinned images.
package main

deny[msg] {
    input.spec.containers[i].securityContext.runAsNonRoot != true
    msg := sprintf("container %v must set runAsNonRoot: true", [input.spec.containers[i].name])
}

deny[msg] {
    image := input.spec.containers[_].image
    not contains(image, "@sha256:")
    msg := sprintf("image %v must be pinned by digest", [image])
}
```

Install: `brew install conftest` / download the release binary. Test:
`conftest test deploy/*.yaml` (each `deny` rule that matches → non-zero exit).

## 2. CI wiring (GitHub Actions)

```yaml
# .github/workflows/ci.yml
  - name: Policy fitness functions (gates ADR-0007)
    run: conftest test deploy/*.yaml --policy policy/
```

Conftest prints each `deny` message and exits 1 on any failure → the job fails → merge blocked.

## 3. Prove it gates

1. Run `conftest test deploy/*.yaml --policy policy/` → must report all tests passed today.
2. Deliberate violation: set a container `runAsNonRoot: false`, or use an unpinned `:latest` tag.
   Re-run → must FAIL with the matching `deny` message.
3. Revert. Commit only the green state.

## When to reach for policy gates instead of code gates

- The constraint is about *deployment/runtime* (containers, network, IAM), not source structure.
- The constraint must hold across multiple languages in one repo (uniform Rego over all manifests).
- Use `--combine` to write rules that span multiple files (e.g. every Deployment has a matching
  NetworkPolicy).
