# EF Core Migration Commands Reference

> Complete reference for Entity Framework Core migration CLI and Package Manager Console commands.

## CLI Commands (dotnet ef)

### Prerequisites

Install the EF Core tools globally:

```bash
dotnet tool install --global dotnet-ef
```

Or update to the latest version:

```bash
dotnet tool update --global dotnet-ef
```

Verify installation:

```bash
dotnet ef --version
```

The project must reference `Microsoft.EntityFrameworkCore.Design`:

```bash
dotnet add package Microsoft.EntityFrameworkCore.Design
```

### Common Project Flags

Most commands accept these flags to specify which projects to use:

| Flag | Short | Description |
|------|-------|-------------|
| `--project <PATH>` | `-p` | Path to the project containing the DbContext and migrations |
| `--startup-project <PATH>` | `-s` | Path to the startup project (with configuration and DI) |
| `--context <NAME>` | `-c` | DbContext class name (required when multiple contexts exist) |
| `--configuration <CONFIG>` | | Build configuration (Debug, Release) |
| `--framework <FRAMEWORK>` | | Target framework when multi-targeting |
| `--verbose` | `-v` | Show verbose output |
| `--no-build` | | Skip building the project before running |
| `--no-color` | | Disable colored output |

---

## Migration Management

### Create a Migration

```bash
dotnet ef migrations add <MigrationName> \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

**Naming conventions:**
- Use PascalCase: `AddUserEmailColumn`, `CreateOrdersTable`
- Be descriptive: `SplitAddressFromCustomer`, `AddIndexOnOrderDate`
- Avoid generic names: `Update1`, `Fix`, `Changes`

**Generated files:**
- `Migrations/<Timestamp>_<Name>.cs` -- Up() and Down() methods
- `Migrations/<Timestamp>_<Name>.Designer.cs` -- Snapshot metadata
- `Migrations/<DbContext>ModelSnapshot.cs` -- Current model state

### List Migrations

```bash
dotnet ef migrations list \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

Output shows each migration with status:
- Applied migrations: listed normally
- Pending migrations: marked with `(Pending)`

### Remove Last Migration

Removes the most recent unapplied migration. Cannot remove applied migrations.

```bash
dotnet ef migrations remove \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

**Safety:** This command will refuse to remove a migration that has already been applied to the database. To force removal (dangerous), add `--force`.

```bash
# DANGEROUS: Removes even if applied. Use only when you know what you're doing.
dotnet ef migrations remove --force \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

### Check for Pending Model Changes

Verify whether the model has changes that require a new migration:

```bash
dotnet ef migrations has-pending-model-changes \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

Returns exit code 0 if no changes, non-zero if changes are pending.

---

## Database Operations

### Apply All Pending Migrations

```bash
dotnet ef database update \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

### Apply Up To a Specific Migration

```bash
dotnet ef database update <MigrationName> \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

### Rollback to a Previous Migration

Specify the migration you want to revert TO (not the one you want to revert):

```bash
# Revert to the state after AddUserTable was applied
dotnet ef database update AddUserTable \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

### Rollback All Migrations

Use the special migration name `0` to revert everything:

```bash
dotnet ef database update 0 \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

### Drop the Database

```bash
dotnet ef database drop \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

Add `--force` to skip the confirmation prompt.

### Get Database Connection Info

```bash
dotnet ef dbcontext info \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

---

## Script Generation

### Generate SQL Script (All Migrations)

```bash
dotnet ef migrations script \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web \
  --output migrations.sql
```

### Generate SQL Script (Specific Range)

From one migration to another:

```bash
dotnet ef migrations script <FromMigration> <ToMigration> \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web \
  --output migrations.sql
```

`<FromMigration>` is exclusive (script starts AFTER this migration).
`<ToMigration>` is inclusive (script includes this migration).

Use `0` as `<FromMigration>` to generate from the beginning:

```bash
dotnet ef migrations script 0 AddUserEmailColumn \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web \
  --output migrations.sql
```

### Generate Idempotent Script

Safe to run multiple times. Essential for production deployments:

```bash
dotnet ef migrations script --idempotent \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web \
  --output migrations-idempotent.sql
```

The generated script wraps each migration in an existence check:

```sql
IF NOT EXISTS (
    SELECT * FROM [__EFMigrationsHistory]
    WHERE [MigrationId] = N'20250115120000_AddUserEmail'
)
BEGIN
    ALTER TABLE [Users] ADD [Email] nvarchar(256) NULL;

    INSERT INTO [__EFMigrationsHistory] ([MigrationId], [ProductVersion])
    VALUES (N'20250115120000_AddUserEmail', N'8.0.0');
END;
GO
```

### Generate Rollback Script

Generate SQL to revert from current to a previous state:

```bash
dotnet ef migrations script <CurrentMigration> <TargetMigration> \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web \
  --output rollback.sql
```

---

## Migration Bundles

Self-contained executables for applying migrations without the .NET SDK installed. Ideal for production deployments.

### Create a Bundle

```bash
dotnet ef migrations bundle \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web \
  --output ./efbundle
```

### Create a Self-Contained Bundle

```bash
dotnet ef migrations bundle \
  --self-contained \
  --target-runtime linux-x64 \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web \
  --output ./efbundle
```

### Run a Bundle

```bash
# Apply all pending migrations
./efbundle --connection "Server=prod;Database=MyApp;..."

# Apply up to a specific migration
./efbundle --connection "Server=prod;Database=MyApp;..." \
  --migration AddUserEmail
```

### Bundle Flags

| Flag | Description |
|------|-------------|
| `--output <PATH>` | Output file path for the bundle |
| `--force` | Overwrite existing bundle file |
| `--self-contained` | Bundle .NET runtime (no SDK needed on target) |
| `--target-runtime <RID>` | Target runtime identifier (`linux-x64`, `win-x64`, etc.) |
| `--configuration <CONFIG>` | Build configuration |

---

## Package Manager Console (PMC) Commands

For use in Visual Studio's Package Manager Console.

### Create Migration

```powershell
Add-Migration <MigrationName> -Project MyApp.Data -StartupProject MyApp.Web
```

### Remove Last Migration

```powershell
Remove-Migration -Project MyApp.Data -StartupProject MyApp.Web
```

### Apply Migrations

```powershell
Update-Database -Project MyApp.Data -StartupProject MyApp.Web
```

### Rollback to Specific Migration

```powershell
Update-Database -Migration <MigrationName> -Project MyApp.Data -StartupProject MyApp.Web
```

### Generate SQL Script

```powershell
Script-Migration -Project MyApp.Data -StartupProject MyApp.Web
```

### Generate Idempotent Script

```powershell
Script-Migration -Idempotent -Project MyApp.Data -StartupProject MyApp.Web
```

### Generate Script for Specific Range

```powershell
Script-Migration -From <FromMigration> -To <ToMigration> -Project MyApp.Data -StartupProject MyApp.Web
```

### List Migrations (PMC)

```powershell
Get-Migration -Project MyApp.Data -StartupProject MyApp.Web
```

### PMC vs CLI Comparison

| Operation | CLI (`dotnet ef`) | PMC (Visual Studio) |
|-----------|-------------------|---------------------|
| Add migration | `migrations add` | `Add-Migration` |
| Remove migration | `migrations remove` | `Remove-Migration` |
| List migrations | `migrations list` | `Get-Migration` |
| Update database | `database update` | `Update-Database` |
| Drop database | `database drop` | `Drop-Database` |
| Generate script | `migrations script` | `Script-Migration` |
| Create bundle | `migrations bundle` | `Bundle-Migration` |
| DbContext info | `dbcontext info` | `Get-DbContext` |

---

## Environment-Specific Commands

### Development

```bash
# Apply all migrations (direct connection via appsettings.Development.json)
dotnet ef database update \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web

# Quick reset: drop and recreate
dotnet ef database drop --force \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
dotnet ef database update \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

### Staging

```bash
# Generate idempotent script for staging deployment
dotnet ef migrations script --idempotent \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web \
  --output deploy/staging-migration.sql

# Or use a bundle
dotnet ef migrations bundle \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web \
  --output deploy/efbundle

# Apply with staging connection string
./deploy/efbundle --connection "$STAGING_CONNECTION_STRING"
```

### Production

```bash
# ALWAYS generate an idempotent script for production
dotnet ef migrations script --idempotent \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web \
  --output deploy/production-migration.sql

# Review the script before applying
cat deploy/production-migration.sql

# Or create a deployment bundle
dotnet ef migrations bundle \
  --self-contained \
  --target-runtime linux-x64 \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web \
  --configuration Release \
  --output deploy/efbundle

# Apply with production connection string (via environment variable)
./deploy/efbundle --connection "$PRODUCTION_CONNECTION_STRING"
```

### Using Environment Variables for Connection Strings

Specify the environment via `ASPNETCORE_ENVIRONMENT`:

```bash
ASPNETCORE_ENVIRONMENT=Staging dotnet ef database update \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

Or use `IDesignTimeDbContextFactory` for design-time configuration:

```csharp
public class DesignTimeDbContextFactory : IDesignTimeDbContextFactory<AppDbContext>
{
    public AppDbContext CreateDbContext(string[] args)
    {
        var environment = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT")
            ?? "Development";

        var configuration = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json")
            .AddJsonFile($"appsettings.{environment}.json", optional: true)
            .AddEnvironmentVariables()
            .Build();

        var optionsBuilder = new DbContextOptionsBuilder<AppDbContext>();
        optionsBuilder.UseSqlServer(
            configuration.GetConnectionString("DefaultConnection"));

        return new AppDbContext(optionsBuilder.Options);
    }
}
```

---

## Common Workflows

### Workflow: Create and Apply a Migration

```bash
# 1. Create the migration
dotnet ef migrations add AddUserPreferences \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web

# 2. Review the generated SQL
dotnet ef migrations script --idempotent \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web \
  --output review.sql

# 3. Inspect the SQL
cat review.sql

# 4. Apply to dev database
dotnet ef database update \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web

# 5. Test rollback
dotnet ef database update PreviousMigrationName \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web

# 6. Re-apply
dotnet ef database update \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

### Workflow: Fix a Bad Migration (Not Yet Applied)

```bash
# Remove the bad migration
dotnet ef migrations remove \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web

# Fix the model code, then recreate
dotnet ef migrations add CorrectMigrationName \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

### Workflow: Fix a Bad Migration (Already Applied)

```bash
# DO NOT delete the migration file!

# Option 1: Create a corrective migration
dotnet ef migrations add FixPreviousMigration \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web

# Edit the new migration to fix the issue, then apply
dotnet ef database update \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web

# Option 2: Rollback, remove, and recreate (dev only)
dotnet ef database update PreviousGoodMigration \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web

dotnet ef migrations remove \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web

# Fix the model, recreate
dotnet ef migrations add CorrectedMigration \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web

dotnet ef database update \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

### Workflow: Merge Conflict in Migrations

When two developers add migrations simultaneously:

```bash
# 1. Pull latest changes
git pull origin main

# 2. If ModelSnapshot.cs conflicts, take theirs:
git checkout --theirs src/MyApp.Data/Migrations/AppDbContextModelSnapshot.cs

# 3. Remove your migration
dotnet ef migrations remove \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web

# 4. Apply their migrations
dotnet ef database update \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web

# 5. Recreate your migration (on top of theirs)
dotnet ef migrations add YourMigrationName \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

---

## Troubleshooting

### Error: "No DbContext was found in assembly"

**Cause:** The project does not contain a DbContext, or it cannot be instantiated at design time.

**Fix:**
- Ensure the DbContext is in the `--project` assembly
- Add an `IDesignTimeDbContextFactory<T>` if DI is complex
- Ensure `Microsoft.EntityFrameworkCore.Design` is referenced in the startup project

### Error: "More than one DbContext was found"

**Cause:** Multiple DbContext classes exist without specifying which to use.

**Fix:**
```bash
dotnet ef migrations add MyMigration --context MySpecificDbContext \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web
```

### Error: "The migration has already been applied"

**Cause:** Attempting to remove a migration that exists in `__EFMigrationsHistory`.

**Fix:**
- Roll back first: `dotnet ef database update <PreviousMigration>`
- Then remove: `dotnet ef migrations remove`

### Error: "Build failed"

**Cause:** The project does not compile.

**Fix:**
- Run `dotnet build` first to see compilation errors
- Fix build errors, then retry the EF command
- Use `--no-build` only if the project is already built

### Error: "Unable to create an object of type 'DbContext'"

**Cause:** Design-time instantiation fails due to missing configuration.

**Fix:** Implement `IDesignTimeDbContextFactory`:

```csharp
public class DesignTimeDbContextFactory : IDesignTimeDbContextFactory<AppDbContext>
{
    public AppDbContext CreateDbContext(string[] args)
    {
        var optionsBuilder = new DbContextOptionsBuilder<AppDbContext>();
        optionsBuilder.UseSqlServer(
            "Server=(localdb)\\mssqllocaldb;Database=MyApp_Design;Trusted_Connection=True;");
        return new AppDbContext(optionsBuilder.Options);
    }
}
```

### Error: "Migration has pending model changes"

**Cause:** The EF model has changed since the last migration was created.

**Fix:**
- Create a new migration to capture the changes
- Or, if the changes are unintended, revert your model code

### Warning: "An operation was scaffolded that may result in the loss of data"

**Cause:** The migration includes operations that could destroy data.

**Fix:**
- Review the generated migration carefully
- Consult the [Data Loss Matrix](data-loss-matrix.md)
- Add data preservation steps before destructive operations
- See the SKILL.md AI Discipline Rule: "Never Ignore Data Loss Warnings"

---

## Safety Flags and Options

| Flag/Option | Command | Purpose |
|-------------|---------|---------|
| `--idempotent` | `migrations script` | Generates safe-to-rerun SQL with existence checks |
| `--no-transactions` | `migrations script` | Omits transaction wrappers (for DDL that cannot run in transactions) |
| `--force` | `migrations remove` | Forces removal even if applied (dangerous) |
| `--force` | `database drop` | Skips confirmation prompt |
| `--dry-run` | `migrations bundle` | Shows what the bundle would do without executing |
| `--verbose` | All commands | Shows detailed output including SQL being executed |
| `--connection` | `database update`, bundle | Override connection string (avoid hardcoding secrets) |
| `--no-build` | Most commands | Skip build step (use when project is already built) |
| `--no-connect` | `migrations has-pending-model-changes` | Check without connecting to database |

### Recommended Safety Practices

1. **Always use `--idempotent` for production scripts** -- ensures re-runnability
2. **Never use `--force` on applied migrations in shared environments** -- corrupts history for all developers
3. **Use `--verbose` when debugging** -- shows the exact SQL being sent to the database
4. **Use `--connection` with environment variables** -- never hardcode production connection strings in commands
5. **Use `--no-transactions` only when necessary** -- some DDL (e.g., `CREATE INDEX CONCURRENTLY` in PostgreSQL) cannot run in transactions, but most migrations benefit from transactional wrapping

```bash
# Safe production deployment pattern
dotnet ef migrations script \
  --idempotent \
  --project src/MyApp.Data \
  --startup-project src/MyApp.Web \
  --output deploy/migration.sql

# Review the script
less deploy/migration.sql

# Apply via your preferred SQL tool (sqlcmd, psql, etc.)
sqlcmd -S prodserver -d MyAppDb -i deploy/migration.sql -U deploy_user -P "$DB_PASSWORD"
```
