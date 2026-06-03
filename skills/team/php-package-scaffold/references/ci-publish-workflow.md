# CI & Packagist Publish Workflow

GitHub Actions for a Composer library, plus the one-time Packagist setup. The CI matrix is the release
gate; Packagist publishes on tag via webhook.

## `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    name: PHP ${{ matrix.php }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        php: ['8.1', '8.2', '8.3']

    steps:
      - uses: actions/checkout@v4

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: ${{ matrix.php }}
          coverage: none
          tools: composer:v2

      - name: Validate composer.json
        run: composer validate --strict

      - name: Cache Composer packages
        uses: actions/cache@v4
        with:
          path: ~/.composer/cache
          key: composer-${{ matrix.php }}-${{ hashFiles('composer.json') }}

      - name: Install dependencies
        run: composer install --prefer-dist --no-progress --no-interaction

      - name: Static analysis (PHPStan)
        run: vendor/bin/phpstan analyse src --level=8 --no-progress

      - name: Coding standards (PHP-CS-Fixer)
        run: vendor/bin/php-cs-fixer fix --dry-run --diff

      - name: Tests
        run: vendor/bin/pest   # or: vendor/bin/phpunit
```

Notes:
- The matrix tests **every** PHP version declared in `require.php`. Add `8.4` when you support it; drop a
  version only with a MAJOR bump.
- `composer validate --strict` runs before install so a malformed manifest fails fast.
- Running on `tags: ['v*']` means a release tag is verified by the same gate as a PR.

## Publishing to Packagist

Packagist does not need credentials in CI — it pulls from the repository when a tag is pushed.

**One-time setup:**
1. Push the library to GitHub (public, or use a private Packagist plan).
2. Sign in at <https://packagist.org> and **Submit** the repository URL once.
3. On the GitHub repo, add the Packagist **service hook** (Settings → Webhooks → Packagist), or enable
   auto-update from the package page. This makes every future tag publish automatically.

**Each release:**
```bash
# 1. Ensure CI is green on main.
# 2. Update CHANGELOG.md (move Unreleased → the new version).
# 3. Tag with semver and push.
git tag v1.2.0
git push origin v1.2.0
```
Packagist receives the webhook, reads the tag, and serves `v1.2.0` to `composer require vendor/name`.

## Optional: explicit Packagist update step

If you prefer not to rely on the GitHub webhook, call the Packagist update API from CI on a tag. This
needs a Packagist API token stored as a repository secret:

```yaml
  publish:
    name: Notify Packagist
    needs: test
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Packagist update
        env:
          PACKAGIST_USER: ${{ secrets.PACKAGIST_USER }}
          PACKAGIST_TOKEN: ${{ secrets.PACKAGIST_TOKEN }}
        run: |
          curl -sf -XPOST \
            "https://packagist.org/api/update-package?username=${PACKAGIST_USER}&apiToken=${PACKAGIST_TOKEN}" \
            -H 'Content-Type: application/json' \
            -d '{"repository":{"url":"https://github.com/vendor/name"}}'
```

Store `PACKAGIST_USER` / `PACKAGIST_TOKEN` as GitHub Actions secrets — never in the workflow file or
committed config.

## Pre-publish checklist

- [ ] CI green on `main` across the full PHP matrix
- [ ] `composer validate --strict` passes
- [ ] PHPStan level 8 clean; CS-Fixer dry-run clean
- [ ] CHANGELOG updated for the version
- [ ] Tag is `vX.Y.Z`, semver-correct for the change (MAJOR on any break)
- [ ] `.gitattributes export-ignore` excludes tests/CI from the archive
- [ ] Packagist webhook configured (first release only)
```
