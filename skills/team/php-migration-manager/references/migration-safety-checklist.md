# Laravel Migration Safety Checklist

Column-by-column and operation-by-operation guidance. Use during the REVIEW phase. All migrations begin
with `declare(strict_types=1);`.

## Anatomy of a safe migration

```php
<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('orders', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->unsignedInteger('quantity');
            $table->string('status')->default('pending')->index();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('orders');
    }
};
```

## Pre-apply checklist

- [ ] `down()` exists and reverses `up()` exactly
- [ ] New columns on existing tables are `nullable()` or have `->default(...)`
- [ ] No column is renamed in the same migration code that still reads the old name
- [ ] Foreign keys declare `onDelete` behavior (`cascadeOnDelete` / `nullOnDelete` / `restrictOnDelete`)
- [ ] Indexes intended for a large table use a concurrent path (see dangerous-operations.md)
- [ ] Data backfill, if any, is a **separate** migration and is batched
- [ ] No `migrate:fresh` / `migrate:refresh` / `db:wipe` anywhere near shared data
- [ ] Rollback rehearsed in a scratch DB (`migrate` → `migrate:rollback --step=1`)

## Column operation matrix

| Operation | Safe form | Watch out |
|-----------|-----------|-----------|
| Add column | `->nullable()` or `->default(...)` | Non-null no-default breaks inserts from old code |
| Drop column | Only after no code reads it (contract phase) | Irreversible data loss; `down()` cannot restore values |
| Rename column | Expand-contract (add new, dual-write, drop old) | A single `renameColumn` breaks running code mid-deploy |
| Change type | `->change()` restating ALL attributes | `change()` replaces the definition; needs doctrine/dbal on <11 |
| Add index | Small table: inline. Large: concurrent | Inline index on a big table = long write lock |
| Add unique | Validate no dupes first | Fails the migration if duplicates exist |
| Add FK | `->constrained()` + `onDelete` | Existing orphan rows fail the constraint |

## Reversible `down()` ordering

`down()` must undo `up()` in reverse dependency order:

```php
public function down(): void
{
    Schema::table('orders', function (Blueprint $table): void {
        $table->dropForeign(['user_id']);   // 1. constraint first
        $table->dropIndex(['status']);      // 2. indexes
        $table->dropColumn(['user_id', 'status']); // 3. columns last
    });
}
```

## Batched backfill (separate migration)

Never one unbounded `UPDATE`. Chunk and let replicas catch up.

```php
public function up(): void
{
    \App\Models\User::query()
        ->whereNull('email_verified_at')
        ->where('legacy_verified', true)
        ->chunkById(1000, function ($users): void {
            foreach ($users as $user) {
                $user->forceFill(['email_verified_at' => $user->created_at])->save();
            }
            usleep(50_000); // brief pause to ease replication lag
        });
}

public function down(): void
{
    // Data backfills are often irreversible — document it explicitly.
    // Here we can null the field we set, if that is acceptable:
    \App\Models\User::query()->whereNotNull('email_verified_at')->update(['email_verified_at' => null]);
}
```

## Environment guards

Keep destructive commands out of shared environments. In a deploy script:

```bash
if [ "$APP_ENV" = "production" ]; then
  php artisan migrate --force --step      # never fresh/refresh
else
  php artisan migrate --step
fi
```

`--force` is required to run migrations non-interactively in production; it does **not** make
`migrate:fresh` safe — that command is still forbidden against real data.

## Rollback test loop

```bash
php artisan migrate --database=scratch
php artisan migrate:rollback --database=scratch --step=1
php artisan migrate:status --database=scratch   # the migration shows as "Pending" again, cleanly
```

If the table or columns linger after rollback, `down()` is incomplete — fix before applying anywhere real.
