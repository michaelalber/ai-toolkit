---
name: environment-health
description: Docker health checks, service monitoring, container lifecycle management, connection validation, and environment diagnostics. Use when troubleshooting dev environment issues or performing health audits.
---

# Environment Health

> "Hope is not a strategy. Monitoring is."
> -- Tom Limoncelli, The Practice of Cloud System Administration

## Core Philosophy

This skill provides the diagnostic toolkit for environment health assessment. It covers Docker container health, service endpoint monitoring, connection validation, port conflict resolution, resource usage analysis, and dependency verification. **Every diagnosis is evidence-based** — no assumptions, no guesses, only verified findings.

**Non-Negotiable Constraints:**
1. **Probe before diagnosing** — discover what is actually running before checking health. Stale assumptions about expected services cause missed diagnoses.
2. **Diagnose before remediating** — understand the root cause before applying a fix. Restarting a container that crashes due to a missing volume just creates a restart loop.
3. **Verify after every action** — confirm the fix actually worked. A service that starts is not necessarily healthy.
4. **Log every command and output** — reproducibility is the foundation of debugging. If you cannot replay the steps, you cannot verify the fix.
5. **Respect environment boundaries** — development environments get autonomous fixes; everything else gets a report.

## Domain Principles Table

| Principle | Description | Priority |
|-----------|-------------|----------|
| **Environment Safety** | Verify dev/staging/prod before any write action; default to read-only | Critical |
| **Evidence-Based Diagnosis** | Every finding backed by command output, not assumptions | Critical |
| **Single-Service Remediation** | Fix one thing, verify, then move to the next | Critical |
| **Dependency Awareness** | Understand service dependencies before restarting anything | High |
| **Resource Monitoring** | Track disk, memory, CPU, and Docker disk usage as first-class concerns | High |
| **Graceful Degradation** | Prefer partial service over full restart; prefer restart over rebuild | High |
| **Connection Validation** | Test connections end-to-end, not just port availability | Medium |
| **Log Analysis** | Container logs are the primary diagnostic evidence source | Medium |
| **Health Check Design** | Prefer application-level health checks over simple TCP port checks | Medium |
| **Idempotent Actions** | Every remediation action should be safe to run twice | Low |

## Workflow

### Environment Discovery

Before any health checks, establish what is running and where:

```bash
# Docker containers (all states)
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}\t{{.State}}"

# Docker Compose services (if compose file exists)
docker compose ps -a

# Listening ports
ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null

# Environment type detection
echo "NODE_ENV=$NODE_ENV"
echo "ASPNETCORE_ENVIRONMENT=$ASPNETCORE_ENVIRONMENT"
echo "RAILS_ENV=$RAILS_ENV"
echo "FLASK_ENV=$FLASK_ENV"
hostname
```

### Docker Health Check Patterns

```bash
# Health status for all containers
docker ps --format "{{.Names}}: {{.Status}}"

# Detailed health for a specific container
docker inspect --format='{{json .State.Health}}' <container_name> | python3 -m json.tool

# Health check log (last 5 checks)
docker inspect --format='{{range .State.Health.Log}}{{.Start}}: {{.ExitCode}} {{.Output}}{{end}}' <container_name>

# Live resource stats
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# Container restart count and uptime
docker inspect --format='Restarts: {{.RestartCount}} | Started: {{.State.StartedAt}}' <container_name>

# Errors in logs (last 20 matches)
docker logs <container_name> 2>&1 | grep -iE "(error|fatal|panic|exception|failed|refused|timeout)" | tail -20

# Logs since last restart
docker logs --since "$(docker inspect --format='{{.State.StartedAt}}' <container_name>)" <container_name>
```

### Service Health Endpoint Checks

```bash
# HTTP health check with timing
curl -sw "\nHTTP_CODE: %{http_code}\nTIME_TOTAL: %{time_total}s\n" http://localhost:PORT/health

# TCP port check
timeout 5 bash -c 'cat < /dev/null > /dev/tcp/localhost/PORT' && echo "Port PORT open" || echo "Port PORT closed"

# Certificate expiry check
echo | openssl s_client -connect hostname:443 -servername hostname 2>/dev/null | openssl x509 -noout -dates
```

### Database Connection Validation

```bash
# PostgreSQL
PGPASSWORD=password psql -h localhost -p 5432 -U user -d dbname -c "SELECT 1;" 2>&1

# PostgreSQL connection count by state
PGPASSWORD=password psql -h localhost -p 5432 -U user -d dbname \
  -c "SELECT state, count(*) FROM pg_stat_activity GROUP BY state;"

# MySQL / MariaDB
mysql -h localhost -P 3306 -u user -ppassword -e "SELECT 1;" 2>&1

# Redis
redis-cli -h localhost -p 6379 ping

# MongoDB
mongosh --host localhost --port 27017 --eval "db.runCommand({ping: 1})" 2>&1
```

### Port Conflict Diagnosis

```bash
# Find what is using a specific port
ss -tlnp | grep :PORT
lsof -i :PORT 2>/dev/null

# Check for duplicate port bindings
ss -tlnp | awk '{print $4}' | sort | uniq -d
```

### Resource Usage Analysis

```bash
# Disk space on key mounts
df -h / /var/lib/docker /tmp 2>/dev/null

# Docker disk usage (summary and verbose)
docker system df
docker system df -v

# Largest Docker images
docker images --format "{{.Repository}}:{{.Tag}} {{.Size}}" | sort -k2 -h -r | head -10

# Dangling images and volumes
docker images -f dangling=true -q | wc -l
docker volume ls -f dangling=true -q | wc -l

# Top memory consumers
free -h
ps aux --sort=-%mem | head -10
```

### Docker Compose Health Checks

For Docker Compose health check patterns by service type (PostgreSQL, Redis, MySQL, RabbitMQ, Elasticsearch, HTTP apps with `depends_on: condition: service_healthy`), see `references/docker-health-patterns.md`.

### Dependency Graph Analysis

```bash
# Parse depends_on from docker-compose
docker compose config --format json | python3 -c "
import sys, json
config = json.load(sys.stdin)
for name, svc in config.get('services', {}).items():
    deps = svc.get('depends_on', {})
    if deps:
        for dep in deps: print(f'{name} -> {dep}')
    else:
        print(f'{name} (no dependencies)')
"
```

## State Block Format

```
<env-health-state>
phase: DIAGNOSE
environment: dev
services_total: 5
services_healthy: 3
services_degraded: 1
services_failing: 1
issues_found: 2
issues_resolved: 0
last_action: Checked container logs for app-worker
last_verified: Database connection healthy on port 5432
blockers: none
</env-health-state>
```

## Output Templates

```markdown
## Environment Health Audit: [Project Name]
**Environment**: [dev/staging/prod] | **Date**: [date]

| Service | Status | Health Check | Uptime | Restarts |
|---------|--------|--------------|--------|----------|
| [name]  | [running/stopped] | [healthy/unhealthy/none] | [duration] | [N] |

| Resource | Current | Threshold | Status |
|----------|---------|-----------|--------|
| Disk (/) | [N]% | 80% | [ok/warn/critical] |

| # | Severity | Component | Issue | Status |
|---|----------|-----------|-------|--------|
```

Full templates (Port Mapping table, Dependency Health Map, Remediation Actions log): `references/service-recovery-playbook.md`

## Anti-Patterns Table

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|------------------|
| Restarting all containers at once | Masks root cause, creates race conditions on startup | Restart one service at a time, verify health between restarts |
| Checking port availability without testing connection | Port may be open but service not accepting queries | Test with protocol-level checks (SQL query, Redis PING, HTTP GET) |
| Assuming container "Up" means "healthy" | Container can be running with a crashing application inside | Use Docker health checks and verify application-level endpoints |
| Running docker-compose down/up as first resort | Destroys volumes, resets state, causes data loss in dev | Restart individual containers; only recreate as last resort |
| Ignoring Docker disk usage | Build cache and dangling images consume disk silently | Check `docker system df` regularly; prune in dev environments |
| Hardcoding connection strings | Prevents discovery when services move or ports change | Read from env vars or config files; discover dynamically |
| Skipping dependency order on restart | Dependent services fail to connect during startup | Start dependencies first, wait for health, then start dependents |
| Killing processes by PID without identifying them | May kill the wrong process; PID reuse is real | Verify process identity with `ps -p PID -o comm=` before killing |

## AI Discipline Rules

**Probe before diagnosing.** Run `docker inspect` and read its output before forming any diagnosis. Parse `State.Health.Status` from actual command output — never assume container state. Assumptions about expected services that are not verified from actual command output produce wrong diagnoses and misdirected remediation.

**Never modify production resources.** Always confirm the target environment before running any mutating command. Verify `DOCKER_HOST` is pointing to the local daemon and check container labels (`docker inspect <id> --format='{{json .Config.Labels}}'`) to confirm `environment=dev` before any restart, reconfigure, or rebuild action.

**Verify after every remediation.** Re-run the same probe that detected the problem after applying a fix. Reporting "fixed" based solely on the remediation command succeeding — without re-probing — is a false positive. After `docker start <container>`, wait 5 seconds and check `docker inspect <container> --format='{{.State.Health.Status}}'` before reporting healthy.

## Error Recovery

**Docker daemon not running** ("Cannot connect to the Docker daemon"): Check `systemctl status docker` and `ls -la /var/run/docker.sock`. Check user groups: `groups | grep docker`. In dev: `sudo systemctl start docker`. Wait for daemon: `until docker info >/dev/null 2>&1; do sleep 1; done`.

**Container restart loop** (RestartCount > 5): Check exit code and OOM status (`docker inspect --format='{{.State.ExitCode}} {{.State.OOMKilled}}' <name>`). Read logs from last run (`docker logs --tail 100 <name>`). Check mounts and env vars via `docker inspect`. If OOM: increase memory limit in compose file. If config error: fix config, then `docker compose up -d <service>`.

**Network connectivity between containers** (cannot reach another container by name): Verify both are on the same network (`docker network inspect <network> --format='{{range .Containers}}{{.Name}} {{end}}'`). Test DNS from inside: `docker exec <container> nslookup <target>`. Test connectivity: `docker exec <container> curl -s http://<target>:<port>/health`. If DNS fails: recreate the network (dev only).

**Volume mount failures** (container exits, mount path not found): Check mount config with `docker inspect --format='{{json .Mounts}}' <name>`. Verify host path exists (`ls -la /path`) and permissions (`stat /path`). For named volumes: `docker volume inspect <volume_name>`. If volume corrupted in dev: `docker volume rm <name> && docker compose up -d`.

## Integration with Other Skills

This is a standalone skill designed for the environment-health-agent. It provides the diagnostic commands, health check patterns, and recovery procedures that the agent executes during its PROBE, DIAGNOSE, REMEDIATE, and MONITOR phases.

Reference files: `references/docker-health-patterns.md` (Docker Compose health checks by service type, container log analysis, network debugging, volume mount verification) | `references/service-recovery-playbook.md` (database connection pool exhaustion, port conflicts, certificate expiry, DNS failures, memory leaks, zombie processes)
