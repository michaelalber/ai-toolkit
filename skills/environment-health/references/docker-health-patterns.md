# Docker Health Patterns

Reference guide for Docker container health checks, log analysis, network debugging, volume verification, and image freshness. All commands are designed for diagnostic use in development environments.

---

## Health Check Authoring

### Health Check Anatomy

Every Docker health check has five parameters:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `test` | (required) | Command to run inside the container |
| `interval` | 30s | Time between health check executions |
| `timeout` | 30s | Maximum time a single check can take before being considered failed |
| `retries` | 3 | Number of consecutive failures before marking unhealthy |
| `start_period` | 0s | Grace period after container start before health checks count as failures |

**Effective start_period**: Set `start_period` to at least the application's cold-start time. A Java Spring Boot app might need 30-60s; a Go binary might need 2s. If `start_period` is too short, the container flaps between `starting` and `unhealthy` on every deploy.

### Health Check Commands by Service Type

**PostgreSQL:**

```dockerfile
HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=30s \
  CMD pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-postgres} || exit 1
```

Why `pg_isready` instead of a TCP check: `pg_isready` verifies the database is accepting connections at the protocol level. A TCP check only confirms the port is open, which happens before PostgreSQL finishes recovery or WAL replay.

**MySQL / MariaDB:**

```dockerfile
HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=30s \
  CMD mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD} || exit 1
```

**Redis:**

```dockerfile
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD redis-cli ping | grep -q PONG || exit 1
```

**HTTP Application:**

```dockerfile
HEALTHCHECK --interval=15s --timeout=5s --retries=3 --start-period=30s \
  CMD curl -f http://localhost:${PORT:-3000}/health || exit 1
```

Note: Ensure `curl` is installed in the container image. For minimal images, use `wget -q --spider` or write a small health check binary.

**gRPC Service:**

```dockerfile
HEALTHCHECK --interval=15s --timeout=5s --retries=3 --start-period=20s \
  CMD grpc_health_probe -addr=:${GRPC_PORT:-50051} || exit 1
```

Install `grpc_health_probe` in the Dockerfile:

```dockerfile
RUN GRPC_HEALTH_PROBE_VERSION=v0.4.25 && \
    wget -qO/bin/grpc_health_probe \
      https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe
```

**RabbitMQ:**

```dockerfile
HEALTHCHECK --interval=15s --timeout=10s --retries=3 --start-period=60s \
  CMD rabbitmq-diagnostics check_port_connectivity || exit 1
```

**Elasticsearch:**

```dockerfile
HEALTHCHECK --interval=20s --timeout=10s --retries=5 --start-period=60s \
  CMD curl -sf http://localhost:9200/_cluster/health | grep -vq '"status":"red"' || exit 1
```

**MongoDB:**

```dockerfile
HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=30s \
  CMD mongosh --quiet --eval "db.runCommand({ping: 1}).ok" | grep -q 1 || exit 1
```

### Compose Health Check with Dependency Ordering

```yaml
services:
  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d appdb"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  api:
    image: myapp:latest
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 30s

  worker:
    image: myapp:latest
    command: ["worker"]
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "pgrep -f worker || exit 1"]
      interval: 15s
      timeout: 5s
      retries: 3
```

---

## Container Log Analysis

### Extracting Error Patterns

```bash
# All errors from a container
docker logs <container> 2>&1 | grep -iE "(error|fatal|panic|exception|failed|refused|timeout|killed)" | tail -30

# Errors with 3 lines of context
docker logs <container> 2>&1 | grep -iE "(error|fatal|panic)" -A 3 -B 1 | tail -50

# Errors since a specific time
docker logs --since "2024-01-15T10:00:00" <container> 2>&1 | grep -i error

# Errors from the last hour
docker logs --since 1h <container> 2>&1 | grep -i error
```

### Common Error Patterns and Their Meanings

| Log Pattern | Likely Cause | Diagnostic Step |
|-------------|--------------|-----------------|
| `Connection refused` | Dependency not running or not ready | Check if target container is healthy |
| `Name or service not known` | DNS resolution failure in Docker network | Verify containers are on the same network |
| `Address already in use` | Port conflict with host process or another container | Run `ss -tlnp \| grep :PORT` on the host |
| `OOM killed` or `Killed` | Container exceeded memory limit | Check `docker inspect --format='{{.State.OOMKilled}}'` |
| `Permission denied` | Volume mount ownership mismatch | Check `stat` on host path, compare with container user |
| `No space left on device` | Disk full (host or container layer) | Run `df -h` and `docker system df` |
| `Connection pool exhausted` | Too many open connections to database | Check active connections in database |
| `TLS handshake timeout` | Certificate issue or network latency | Test with `openssl s_client` |
| `SIGTERM` / `SIGKILL` | Container was stopped or killed externally | Check `docker events` for stop/kill signals |
| `exec format error` | Wrong platform (ARM image on x86 or vice versa) | Check `docker inspect --format='{{.Architecture}}'` |

### Structured Log Parsing

```bash
# JSON logs -- extract error messages
docker logs <container> 2>&1 | python3 -c "
import sys, json
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        entry = json.loads(line)
        level = entry.get('level', entry.get('severity', '')).lower()
        if level in ('error', 'fatal', 'critical', 'panic'):
            msg = entry.get('message', entry.get('msg', line))
            ts = entry.get('timestamp', entry.get('time', entry.get('ts', '')))
            print(f'{ts} [{level.upper()}] {msg}')
    except json.JSONDecodeError:
        if any(kw in line.lower() for kw in ('error', 'fatal', 'panic')):
            print(line)
" | tail -20

# Count errors by type in last 1000 lines
docker logs --tail 1000 <container> 2>&1 | grep -ioE "(connection refused|timeout|oom|permission denied|no space)" | sort | uniq -c | sort -rn
```

---

## Network Connectivity Debugging

### Container-to-Container Connectivity

```bash
# Verify containers share a network
docker network inspect <network_name> --format='{{range .Containers}}{{.Name}} {{end}}'

# DNS resolution from inside a container
docker exec <container> nslookup <target_service_name>

# Ping between containers (if ping is installed)
docker exec <container> ping -c 3 <target_service_name>

# HTTP check from inside a container
docker exec <container> curl -sf http://<target_service_name>:<port>/health

# TCP port check from inside a container (no curl needed)
docker exec <container> timeout 5 bash -c 'cat < /dev/null > /dev/tcp/<target>/<port>' && echo "OK" || echo "FAILED"
```

### Docker Network Diagnostics

```bash
# List all Docker networks
docker network ls

# Inspect a network (shows connected containers and their IPs)
docker network inspect <network_name>

# Find which network a container is on
docker inspect --format='{{range $net, $conf := .NetworkSettings.Networks}}{{$net}} ({{$conf.IPAddress}}) {{end}}' <container>

# Check for orphaned networks
docker network ls --filter "dangling=true"

# Create a debug container on the same network for manual testing
docker run --rm -it --network <network_name> nicolaka/netshoot bash
```

### Port Mapping Verification

```bash
# All published ports for all running containers
docker ps --format "{{.Names}}: {{.Ports}}"

# Specific container port mappings
docker port <container>

# Verify host port is reachable
curl -sf http://localhost:<host_port>/health || echo "Port <host_port> not reachable from host"

# Check if host port is bound to 0.0.0.0 (all interfaces) or 127.0.0.1 only
ss -tlnp | grep :<port>
```

---

## Volume Mount Verification

### Diagnosing Volume Issues

```bash
# List all mounts for a container
docker inspect --format='{{json .Mounts}}' <container> | python3 -m json.tool

# Check named volume details
docker volume inspect <volume_name>

# Verify host path exists and check permissions
ls -la /host/path
stat /host/path

# Check who owns files inside the container
docker exec <container> ls -la /container/path

# Compare host UID with container UID
echo "Host UID: $(stat -c '%u' /host/path)"
docker exec <container> id
```

### Common Volume Problems

| Problem | Symptom | Fix |
|---------|---------|-----|
| Host path does not exist | Container exits immediately or mount is empty | Create the host directory before starting container |
| Permission mismatch | `Permission denied` in container logs | Set `user:` in compose or `chown` host path to match container UID |
| Named volume stale data | Container starts with old config or data | `docker volume rm <name>` then recreate (dev only) |
| Bind mount overwrites container files | Application files missing after mount | Use named volume or restructure mount to avoid overwriting |
| Volume full | `No space left on device` inside container | Check `docker system df`, prune unused volumes |

### Volume Cleanup (Dev Only)

```bash
# List dangling volumes (not attached to any container)
docker volume ls -f dangling=true

# Remove dangling volumes
docker volume prune -f

# Remove a specific named volume (data will be lost)
docker volume rm <volume_name>

# Check total volume disk usage
docker system df -v | grep "Local Volumes" -A 100 | head -20
```

---

## Image Freshness Checks

### Identifying Stale Images

```bash
# List images sorted by creation date (oldest first)
docker images --format "{{.Repository}}:{{.Tag}}\t{{.CreatedSince}}\t{{.Size}}" | sort -t$'\t' -k2

# Check if local image matches remote registry
docker pull --dry-run <image:tag> 2>/dev/null || \
  echo "Check manually: docker pull <image:tag>"

# Compare image digests (local vs remote)
LOCAL_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' <image:tag> 2>/dev/null)
echo "Local digest: $LOCAL_DIGEST"

# List images older than 30 days
docker images --format "{{.Repository}}:{{.Tag}} {{.CreatedAt}}" | while read img date rest; do
    created=$(date -d "$date" +%s 2>/dev/null)
    now=$(date +%s)
    age_days=$(( (now - created) / 86400 ))
    if [ "$age_days" -gt 30 ]; then
        echo "STALE ($age_days days): $img"
    fi
done

# Dangling images (untagged)
docker images -f dangling=true --format "{{.ID}} {{.CreatedSince}} {{.Size}}"
```

### Image Cleanup (Dev Only)

```bash
# Remove dangling images
docker image prune -f

# Remove all unused images (not just dangling)
docker image prune -a -f

# Remove images older than 7 days
docker image prune -a -f --filter "until=168h"

# Full Docker cleanup (images, containers, networks, build cache)
docker system prune -a -f --volumes
```

**Warning:** `docker system prune -a --volumes` removes ALL stopped containers, ALL unused images, ALL unused volumes, and ALL build cache. Only run this in development environments where data loss is acceptable.

---

## Docker Compose Diagnostics

### Service Status and Dependencies

```bash
# All services with status
docker compose ps -a

# Service configuration (resolved)
docker compose config

# Dependency tree
docker compose config --format json | python3 -c "
import sys, json
config = json.load(sys.stdin)
for name, svc in sorted(config.get('services', {}).items()):
    deps = list(svc.get('depends_on', {}).keys())
    if deps:
        print(f'{name} depends on: {', '.join(deps)}')
    else:
        print(f'{name} (no dependencies)')
"

# Recreate a single service without affecting others
docker compose up -d --no-deps --force-recreate <service_name>

# View logs for a specific service
docker compose logs --tail 50 --timestamps <service_name>

# View events for a service
docker compose events <service_name>
```

### Compose Environment Variable Resolution

```bash
# Show resolved environment variables for a service
docker compose config --format json | python3 -c "
import sys, json
config = json.load(sys.stdin)
for name, svc in sorted(config.get('services', {}).items()):
    env = svc.get('environment', {})
    if env:
        print(f'\n--- {name} ---')
        for k, v in sorted(env.items()):
            # Mask passwords
            display = '***' if any(s in k.lower() for s in ('password', 'secret', 'key', 'token')) else v
            print(f'  {k}={display}')
"
```

---

## Quick Reference: Diagnostic Commands

| What to Check | Command |
|---------------|---------|
| Container health | `docker inspect --format='{{.State.Health.Status}}' <name>` |
| Container exit code | `docker inspect --format='{{.State.ExitCode}}' <name>` |
| Container OOM killed | `docker inspect --format='{{.State.OOMKilled}}' <name>` |
| Container restart count | `docker inspect --format='{{.RestartCount}}' <name>` |
| Container IP address | `docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <name>` |
| Container start time | `docker inspect --format='{{.State.StartedAt}}' <name>` |
| Listening ports (host) | `ss -tlnp` |
| Disk space | `df -h / /var/lib/docker` |
| Docker disk usage | `docker system df` |
| Memory usage | `free -h` |
| Top processes | `ps aux --sort=-%mem \| head -10` |
| DNS resolution | `dig +short <hostname>` |
| Certificate expiry | `echo \| openssl s_client -connect host:443 2>/dev/null \| openssl x509 -noout -enddate` |
