---
name: environment-health
description: Docker health checks, service monitoring, container lifecycle management, connection validation, and environment diagnostics. Use when troubleshooting dev environment issues or performing health audits.
---

# Environment Health

> "Hope is not a strategy. Monitoring is."
> -- Tom Limoncelli, The Practice of Cloud System Administration

## Core Philosophy

This skill provides the diagnostic toolkit for environment health assessment. It covers Docker container health, service endpoint monitoring, connection validation, port conflict resolution, resource usage analysis, and dependency verification. **Every diagnosis is evidence-based** -- no assumptions, no guesses, only verified findings.

**Non-Negotiable Constraints:**
1. **Probe before diagnosing** -- discover what is actually running before checking health. Stale assumptions about expected services cause missed diagnoses.
2. **Diagnose before remediating** -- understand the root cause before applying a fix. Restarting a container that crashes due to a missing volume just creates a restart loop.
3. **Verify after every action** -- confirm the fix actually worked. A service that starts is not necessarily healthy.
4. **Log every command and output** -- reproducibility is the foundation of debugging. If you cannot replay the steps, you cannot verify the fix.
5. **Respect environment boundaries** -- development environments get autonomous fixes; everything else gets a report.

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

**Check container health status:**

```bash
# Health status for all containers
docker ps --format "{{.Names}}: {{.Status}}"

# Detailed health for a specific container
docker inspect --format='{{json .State.Health}}' <container_name> | python3 -m json.tool

# Health check log (last 5 checks)
docker inspect --format='{{range .State.Health.Log}}{{.Start}}: {{.ExitCode}} {{.Output}}{{end}}' <container_name>
```

**Check container resource usage:**

```bash
# Live resource stats
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# Container restart count
docker inspect --format='{{.RestartCount}}' <container_name>

# Container uptime
docker inspect --format='{{.State.StartedAt}}' <container_name>
```

**Analyze container logs:**

```bash
# Last 50 lines with timestamps
docker logs --tail 50 --timestamps <container_name>

# Errors only (common patterns)
docker logs <container_name> 2>&1 | grep -iE "(error|fatal|panic|exception|failed|refused|timeout)" | tail -20

# Logs since last restart
docker logs --since "$(docker inspect --format='{{.State.StartedAt}}' <container_name>)" <container_name>
```

### Service Health Endpoint Checks

```bash
# HTTP health check with timing
curl -sw "\nHTTP_CODE: %{http_code}\nTIME_TOTAL: %{time_total}s\n" http://localhost:PORT/health

# TCP port check (is the port open?)
timeout 5 bash -c 'cat < /dev/null > /dev/tcp/localhost/PORT' && echo "Port PORT open" || echo "Port PORT closed"

# DNS resolution
dig +short hostname
nslookup hostname

# Certificate expiry check
echo | openssl s_client -connect hostname:443 -servername hostname 2>/dev/null | openssl x509 -noout -dates
```

### Database Connection Validation

```bash
# PostgreSQL
PGPASSWORD=password psql -h localhost -p 5432 -U user -d dbname -c "SELECT 1;" 2>&1

# PostgreSQL connection count
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

# Find all Docker container port mappings
docker ps --format "{{.Names}}: {{.Ports}}" | grep -v "^$"

# Check for duplicate port bindings
ss -tlnp | awk '{print $4}' | sort | uniq -d
```

### Resource Usage Analysis

```bash
# Disk space on key mounts
df -h / /var/lib/docker /tmp 2>/dev/null

# Docker disk usage breakdown
docker system df

# Docker disk usage (verbose -- shows per-image and per-container)
docker system df -v

# Largest Docker images
docker images --format "{{.Repository}}:{{.Tag}} {{.Size}}" | sort -k2 -h -r | head -10

# Dangling images and volumes
docker images -f dangling=true -q | wc -l
docker volume ls -f dangling=true -q | wc -l

# Memory usage
free -h

# Top memory consumers
ps aux --sort=-%mem | head -10
```

### Docker Compose Health Checks

Writing effective health checks in docker-compose:

```yaml
# PostgreSQL health check
services:
  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

# Redis health check
  redis:
    image: redis:7
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

# HTTP application health check
  api:
    image: myapp:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 30s
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

# MySQL health check
  mysql:
    image: mysql:8
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

# RabbitMQ health check
  rabbitmq:
    image: rabbitmq:3-management
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "check_port_connectivity"]
      interval: 15s
      timeout: 10s
      retries: 3
      start_period: 60s

# Elasticsearch health check
  elasticsearch:
    image: elasticsearch:8.12.0
    healthcheck:
      test: ["CMD-SHELL", "curl -s http://localhost:9200/_cluster/health | grep -vq '\"status\":\"red\"'"]
      interval: 20s
      timeout: 10s
      retries: 5
      start_period: 60s
```

### Dependency Graph Analysis

```bash
# Parse depends_on from docker-compose
docker compose config --format json | python3 -c "
import sys, json
config = json.load(sys.stdin)
for name, svc in config.get('services', {}).items():
    deps = svc.get('depends_on', {})
    if deps:
        for dep in deps:
            print(f'{name} -> {dep}')
    else:
        print(f'{name} (no dependencies)')
"
```

## State Block Format

Maintain state across conversation turns:

```
<env-health-state>
phase: [PROBE | DIAGNOSE | REMEDIATE | MONITOR]
environment: [dev | staging | production | unknown]
services_total: [number]
services_healthy: [number]
services_degraded: [number]
services_failing: [number]
issues_found: [number]
issues_resolved: [number]
last_action: [what was just done]
last_verified: [what was just confirmed]
blockers: [any issues preventing progress]
</env-health-state>
```

**Example:**

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

### Health Audit Report

```markdown
## Environment Health Audit: [Project Name]

**Date**: [date]
**Environment**: [dev / staging / production]
**Docker Version**: [version]
**Compose File**: [path]

### Service Health Summary

| Service | Container | Status | Health Check | Uptime | Restarts |
|---------|-----------|--------|--------------|--------|----------|
| [name]  | [container] | [running/stopped] | [healthy/unhealthy/none] | [duration] | [count] |

### Port Mapping

| Port | Service | Container | Status |
|------|---------|-----------|--------|
| [n]  | [name]  | [name]    | [ok/conflict] |

### Resource Usage

| Resource | Current | Threshold | Status |
|----------|---------|-----------|--------|
| Disk (/) | [n]%    | 80%       | [ok/warn/critical] |
| Disk (/var/lib/docker) | [n]% | 80% | [ok/warn/critical] |
| Memory   | [n]%    | 85%       | [ok/warn/critical] |
| Docker images | [n] ([size]) | -- | -- |
| Docker volumes | [n] ([size]) | -- | -- |
| Build cache | [size] | -- | -- |

### Issues

| # | Severity | Component | Issue | Status |
|---|----------|-----------|-------|--------|
| 1 | [CRITICAL/HIGH/MEDIUM/LOW] | [component] | [description] | [open/resolved] |

### Remediation Actions Taken

| # | Action | Target | Result | Rollback |
|---|--------|--------|--------|----------|
| 1 | [action] | [target] | [success/failed] | [rollback command] |
```

### Dependency Health Map

```markdown
## Service Dependency Map

```
                    ┌──────────┐
                    │  nginx   │ :80, :443
                    └────┬─────┘
                         │
                    ┌────┴─────┐
                    │   api    │ :3000
                    └────┬─────┘
                    ┌────┼─────┐
               ┌────┴──┐ │  ┌─┴──────┐
               │  db   │ │  │ redis  │
               │:5432  │ │  │ :6379  │
               └───────┘ │  └────────┘
                    ┌────┴─────┐
                    │ worker   │
                    └──────────┘
```

**Dependency Health:**
- nginx -> api: [ok / degraded / broken]
- api -> db: [ok / degraded / broken]
- api -> redis: [ok / degraded / broken]
- worker -> db: [ok / degraded / broken]
- worker -> redis: [ok / degraded / broken]
```

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

## Error Recovery

### Docker Daemon Not Running

```
Problem: "Cannot connect to the Docker daemon"
Actions:
1. Check systemd status: systemctl status docker
2. Check socket: ls -la /var/run/docker.sock
3. Check user groups: groups | grep docker
4. In dev: sudo systemctl start docker
5. Wait for daemon: until docker info >/dev/null 2>&1; do sleep 1; done
6. Verify: docker ps
```

### Container Restart Loop

```
Problem: Container keeps restarting (RestartCount > 5)
Actions:
1. Check exit code: docker inspect --format='{{.State.ExitCode}}' <name>
2. Check OOM kill: docker inspect --format='{{.State.OOMKilled}}' <name>
3. Read logs from last run: docker logs --tail 100 <name>
4. Check mounts exist: docker inspect --format='{{json .Mounts}}' <name>
5. Check env vars: docker inspect --format='{{json .Config.Env}}' <name>
6. If OOM: increase memory limit in compose file
7. If config error: fix config, then docker compose up -d <service>
```

### Network Connectivity Between Containers

```
Problem: Container cannot reach another container by name
Actions:
1. Verify both containers on same network:
   docker network inspect <network> --format='{{range .Containers}}{{.Name}} {{end}}'
2. Test DNS resolution from inside container:
   docker exec <container> nslookup <target_name>
3. Test connectivity:
   docker exec <container> curl -s http://<target_name>:<port>/health
4. Check if target container is healthy:
   docker inspect --format='{{.State.Health.Status}}' <target_name>
5. If DNS fails: recreate the network (dev only)
```

### Volume Mount Failures

```
Problem: Container exits because mount path does not exist or is not accessible
Actions:
1. Check mount config: docker inspect --format='{{json .Mounts}}' <name> | python3 -m json.tool
2. Verify host path exists: ls -la /path/on/host
3. Check permissions: stat /path/on/host
4. For named volumes: docker volume inspect <volume_name>
5. If volume corrupted in dev: docker volume rm <name> && docker compose up -d
```

## Integration with Other Skills

This is a standalone skill designed for the environment-health-agent. It provides the diagnostic commands, health check patterns, and recovery procedures that the agent executes during its PROBE, DIAGNOSE, REMEDIATE, and MONITOR phases.

## Reference Files

- [Docker Health Patterns](references/docker-health-patterns.md) -- Docker compose health checks, container log analysis, network connectivity debugging, volume mount verification, image freshness checks
- [Service Recovery Playbook](references/service-recovery-playbook.md) -- Common service recovery procedures for database connection pool exhaustion, port conflicts, certificate expiry, DNS resolution failures, memory leaks, zombie processes
