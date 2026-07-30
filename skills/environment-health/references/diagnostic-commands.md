# Diagnostic Command Catalog

The full command catalog for each Workflow phase. Run probes before diagnosing, diagnose
before remediating, and re-run the detecting probe after every fix.

## Environment Discovery

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

## Docker Health Check Patterns

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

## Service Health Endpoint Checks

```bash
# HTTP health check with timing
curl -sw "\nHTTP_CODE: %{http_code}\nTIME_TOTAL: %{time_total}s\n" http://localhost:PORT/health

# TCP port check
timeout 5 bash -c 'cat < /dev/null > /dev/tcp/localhost/PORT' && echo "Port PORT open" || echo "Port PORT closed"

# Certificate expiry check
echo | openssl s_client -connect hostname:443 -servername hostname 2>/dev/null | openssl x509 -noout -dates
```

## Database Connection Validation

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

## Port Conflict Diagnosis

```bash
# Find what is using a specific port
ss -tlnp | grep :PORT
lsof -i :PORT 2>/dev/null

# Check for duplicate port bindings
ss -tlnp | awk '{print $4}' | sort | uniq -d
```

## Resource Usage Analysis

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

## Dependency Graph Analysis

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
