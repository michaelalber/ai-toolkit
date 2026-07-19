# composer.json & Package Layout Template

A complete, publishable Composer library manifest plus the supporting config files. Replace
`vendor/name` and the `Vendor\Name\` namespace throughout.

## `composer.json`

```json
{
    "name": "vendor/name",
    "description": "One-line description of what the library does.",
    "type": "library",
    "license": "MIT",
    "keywords": ["php", "relevant", "topic"],
    "homepage": "https://github.com/vendor/name",
    "authors": [
        { "name": "Author Name", "email": "author@example.com" }
    ],
    "require": {
        "php": "^8.2"
    },
    "require-dev": {
        "pestphp/pest": "^3.0",
        "phpstan/phpstan": "^2.0",
        "friendsofphp/php-cs-fixer": "^3.58"
    },
    "autoload": {
        "psr-4": { "Vendor\\Name\\": "src/" }
    },
    "autoload-dev": {
        "psr-4": { "Vendor\\Name\\Tests\\": "tests/" }
    },
    "scripts": {
        "test": "pest",
        "analyse": "phpstan analyse src --level=8",
        "cs": "php-cs-fixer fix --dry-run --diff",
        "cs:fix": "php-cs-fixer fix"
    },
    "config": {
        "sort-packages": true,
        "allow-plugins": { "pestphp/pest-plugin": true }
    },
    "minimum-stability": "stable",
    "prefer-stable": true
}
```

Notes:
- `type: library` is the default but state it explicitly.
- Keep `require` minimal and caret-bounded; dev tooling goes in `require-dev`.
- `minimum-stability: stable` + `prefer-stable: true` keeps consumers off dev builds.

## `src/Example.php`

```php
<?php

declare(strict_types=1);

namespace Vendor\Name;

final class Example
{
    public function greet(string $who): string
    {
        return "Hello, {$who}";
    }
}
```

Mark anything not part of the supported surface:

```php
/** @internal This class is not covered by the package's backward-compatibility promise. */
final class InternalHelper { /* ... */ }
```

## `tests/ExampleTest.php` (Pest)

```php
<?php

declare(strict_types=1);

use Vendor\Name\Example;

it('greets by name', function (): void {
    expect((new Example())->greet('Ada'))->toBe('Hello, Ada');
});
```

PHPUnit equivalent (if not using Pest):

```php
<?php

declare(strict_types=1);

namespace Vendor\Name\Tests;

use PHPUnit\Framework\TestCase;
use Vendor\Name\Example;

final class ExampleTest extends TestCase
{
    public function test_greets_by_name(): void
    {
        self::assertSame('Hello, Ada', (new Example())->greet('Ada'));
    }
}
```

## `phpstan.neon.dist`

```neon
parameters:
    level: 8
    paths:
        - src
    # Generate a baseline only for legacy code you cannot fix yet:
    # baseline: phpstan-baseline.neon
```

## `.php-cs-fixer.dist.php`

```php
<?php

declare(strict_types=1);

$finder = PhpCsFixer\Finder::create()->in([__DIR__ . '/src', __DIR__ . '/tests']);

return (new PhpCsFixer\Config())
    ->setRiskyAllowed(true)
    ->setRules([
        '@PSR12' => true,
        'declare_strict_types' => true,
        'ordered_imports' => ['sort_algorithm' => 'alpha'],
        'no_unused_imports' => true,
    ])
    ->setFinder($finder);
```

## `.gitignore` (library)

```gitignore
/vendor/
composer.lock
.phpunit.result.cache
.php-cs-fixer.cache
.phpstan.cache
```

A library does **not** commit `composer.lock`. (An application would.)

## `.gitattributes` — keep the published archive lean

```gitattributes
/tests              export-ignore
/.github            export-ignore
/.php-cs-fixer.dist.php export-ignore
/phpstan.neon.dist  export-ignore
/.gitattributes     export-ignore
/.gitignore         export-ignore
/CHANGELOG.md       export-ignore
```

## `CHANGELOG.md` (Keep a Changelog)

```markdown
# Changelog

All notable changes to this project are documented here. Format: Keep a Changelog; versioning: SemVer.

## [Unreleased]

## [1.0.0] - 2026-06-03
### Added
- Initial public release.
```
