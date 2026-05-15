# Service Recovery Playbook

Step-by-step recovery procedures for common service failures in development environments. Each procedure includes diagnosis, remediation, verification, and prevention steps.

---

## Database Connection Pool Exhaustion

### Symptoms

- Application logs: "Connection pool exhausted", "Timeout waiting for connection", "Too many connections"
- Database responds to `ping` but queries hang or timeout
- New connections are refused while existing ones remain idle

### Diagnosis

```bash
# PostgreSQL: Check active connections by state
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -p 5432 -U $POSTGRES_USER -d $POSTGRES_DB -c "
SELECT state, count(*), max(now() - state_change) as max_duration
FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY state
ORDER BY count DESC;
"

# PostgreSQL: Find long-running idle-in-transaction sessions
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -p 5432 -U $POSTGRES_USER -d $POSTGRES_DB -c "
SELECT pid, state, now() - state_change as duration, left(query, 80) as query
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - state_change > interval '5 minutes'
ORDER BY duration DESC;
"

# PostgreSQL: Check max connections vs current usage
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -p 5432 -U $POSTGRES_USER -d $POSTGRES_DB -c "
SELECT current_setting('max_connections') as max_conn,
       (SELECT count(*) FROM pg_stat_activity) as current_conn;
"

# MySQL: Check connection count
mysql -h localhost -u $MYSQL_USER -p$MYSQL_PASSWORD -e "
SHOW STATUS LIKE 'Threads_connected';
SHOW VARIABLES LIKE 'max_connections';
SHOW PROCESSLIST;
"
```

### Remediation (Dev Only)

```bash
# PostgreSQL: Terminate idle-in-transaction sessions older than 5 minutes
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -p 5432 -U $POSTGRES_USER -d $POSTGRES_DB -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - state_change > interval '5 minutes'
  AND pid != pg_backend_pid();
"

# Restart the application container (not the database)
docker restart <app_container>

# Verify connections are released
sleep 5
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -p 5432 -U $POSTGRES_USER -d $POSTGRES_DB -c "
SELECT state, count(*) FROM pg_stat_activity WHERE datname = current_database() GROUP BY state;
"
```

### Prevention

```
Application Configuration:
- Set connection pool max_size to (max_connections / number_of_app_instances) - 5
- Set connection pool idle_timeout to 300s (5 minutes)
- Set connection pool max_lifetime to 1800s (30 minutes)
- Enable connection pool health check (test-on-borrow)

Database Configuration:
- Set statement_timeout = '30s' to kill long-running queries
- Set idle_in_transaction_session_timeout = '300s'
- Monitor connection count with alerts at 80% of max_connections
```

---

## Port Conflicts

### Symptoms

- Container exits immediately with "Address already in use"
- Application cannot bind to its configured port
- Two services attempt to use the same port

### Diagnosis

```bash
# Find what is using the conflicting port
ss -tlnp | grep :<PORT>

# Alternative with lsof (shows process name clearly)
lsof -i :<PORT> 2>/dev/null

# Check if it is a Docker container or a host process
PROC_PID=$(ss -tlnp | grep :<PORT> | grep -oP 'pid=\K\d+')
if [ -n "$PROC_PID" ]; then
    echo "PID: $PROC_PID"
    ps -p $PROC_PID -o pid,ppid,comm,args
    # Check if it is inside a container
    cat /proc/$PROC_PID/cgroup 2>/dev/null | grep docker
fi

# Check Docker port mappings for conflicts
docker ps --format "{{.Names}}: {{.Ports}}" | grep "<PORT>"

# Check if a host service is configured to use the same port
systemctl list-units --type=service --state=running | grep -iE "(postgres|mysql|redis|nginx|apache|mongo)"
```

### Remediation (Dev Only)

```bash
# Option 1: Stop the conflicting host service
sudo systemctl stop <conflicting_service>

# Option 2: Kill the conflicting process
kill <PID>
# If it does not stop:
kill -9 <PID>

# Option 3: Change the container port mapping in docker-compose
# Edit docker-compose.yml to use a different host port:
#   ports:
#     - "5433:5432"  # Use 5433 on host instead of 5432

# After clearing the conflict, restart the affected container
docker start <container_name>
# or
docker compose up -d <service_name>

# Verify the port is now correctly bound
ss -tlnp | grep :<PORT>
docker ps --filter name=<container_name>
```

### Prevention

```
- Use explicit host port mappings in docker-compose (do not rely on auto-assignment)
- Document required ports in the project README or .env.example
- Disable host-level services that conflict with Docker containers:
    sudo systemctl disable postgresql redis-server mysql
- Use a .env file for port configuration:
    DB_HOST_PORT=5432
    REDIS_HOST_PORT=6379
    APP_HOST_PORT=3000
```

---

## Certificate Expiry

### Symptoms

- Browser shows "Your connection is not private" or "NET::ERR_CERT_DATE_INVALID"
- Application logs: "TLS handshake failed", "certificate has expired"
- curl returns: "SSL certificate problem: certificate has expired"

### Diagnosis

```bash
# Check certificate expiry date
echo | openssl s_client -connect <hostname>:<port> -servername <hostname> 2>/dev/null | \
  openssl x509 -noout -dates

# Calculate days until expiry
EXPIRY_DATE=$(echo | openssl s_client -connect <hostname>:<port> -servername <hostname> 2>/dev/null | \
  openssl x509 -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))
echo "Days until expiry: $DAYS_LEFT"

# Check full certificate chain
echo | openssl s_client -connect <hostname>:<port> -servername <hostname> -showcerts 2>/dev/null

# Check certificate subject and SANs
echo | openssl s_client -connect <hostname>:<port> -servername <hostname> 2>/dev/null | \
  openssl x509 -noout -subject -ext subjectAltName

# Check if certificate is self-signed
echo | openssl s_client -connect <hostname>:<port> 2>/dev/null | \
  openssl x509 -noout -issuer -subject
```

### Remediation (Dev Only -- Self-Signed Certs)

```bash
# Generate new self-signed certificate for development
openssl req -x509 -newkey rsa:4096 -sha256 -days 365 \
  -nodes -keyout dev.key -out dev.crt \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1"

# Copy into the appropriate location
cp dev.crt /path/to/certs/
cp dev.key /path/to/certs/

# Restart the service using the certificate
docker restart <nginx_or_proxy_container>

# Verify new certificate
echo | openssl s_client -connect localhost:443 2>/dev/null | openssl x509 -noout -dates
```

### Remediation (Non-Dev -- Report Only)

```
CERTIFICATE EXPIRY REPORT:
- Host: <hostname>
- Port: <port>
- Current Expiry: <date>
- Days Remaining: <N>
- Issuer: <issuer>
- Action Required: Renew certificate before expiry
- Urgency: [CRITICAL if < 7 days | HIGH if < 30 days | MEDIUM if < 90 days]
```

### Prevention

```
- Set up certificate expiry monitoring (check daily)
- Use Let's Encrypt with auto-renewal for non-dev environments
- For dev: use mkcert for locally trusted development certificates
- Alert at 30, 14, and 7 days before expiry
- Document certificate renewal procedures per environment
```

---

## DNS Resolution Failures

### Symptoms

- Container logs: "Name or service not known", "Could not resolve hostname"
- `nslookup` or `dig` returns NXDOMAIN or times out
- Service-to-service calls fail but direct IP connections work

### Diagnosis

```bash
# Check host-level DNS resolution
dig +short <hostname>
nslookup <hostname>

# Check Docker internal DNS resolution (from inside a container)
docker exec <container> nslookup <target_service_name>
docker exec <container> cat /etc/resolv.conf

# Check Docker embedded DNS server
docker exec <container> nslookup <target_service_name> 127.0.0.11

# Verify both containers are on the same Docker network
docker network inspect <network_name> --format='{{range .Containers}}{{.Name}} {{end}}'

# Check host DNS configuration
cat /etc/resolv.conf
systemd-resolve --status 2>/dev/null || resolvectl status 2>/dev/null
```

### Remediation (Dev Only)

```bash
# If Docker DNS is failing, restart the Docker daemon
sudo systemctl restart docker
# WARNING: This restarts all containers

# If containers are on different networks, connect them
docker network connect <network_name> <container_name>

# If Docker Compose network is corrupted, recreate it
docker compose down
docker compose up -d

# If host DNS is failing, check and restart systemd-resolved
sudo systemctl restart systemd-resolved

# Add explicit hosts entry as a workaround (inside container)
docker exec <container> sh -c 'echo "172.18.0.5 target-service" >> /etc/hosts'

# Verify resolution works
docker exec <container> nslookup <target_service_name>
```

### Prevention

```
- Always use Docker Compose service names for inter-service communication
- Never hardcode container IP addresses
- Use depends_on with condition: service_healthy to ensure dependencies start first
- Test DNS resolution as part of container health checks
- Keep Docker and Docker Compose updated (DNS bugs are fixed regularly)
```

---

## Memory Leaks

### Symptoms

- Container memory usage grows continuously over time
- OOM kills appear in `docker events` or container inspect
- Application becomes slower over time, then crashes
- `docker stats` shows memory climbing toward the limit

### Diagnosis

```bash
# Check current memory usage for all containers
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Check if container was OOM killed
docker inspect --format='OOMKilled: {{.State.OOMKilled}} | ExitCode: {{.State.ExitCode}}' <container>

# Check container memory limit
docker inspect --format='Memory Limit: {{.HostConfig.Memory}}' <container>

# Monitor memory usage over time (sample every 5 seconds for 1 minute)
for i in $(seq 1 12); do
    MEM=$(docker stats --no-stream --format "{{.MemUsage}}" <container>)
    echo "$(date '+%H:%M:%S') $MEM"
    sleep 5
done

# Check host-level memory
free -h
cat /proc/meminfo | grep -E "(MemTotal|MemAvailable|SwapTotal|SwapFree)"

# Find memory-heavy processes on the host
ps aux --sort=-%mem | head -10
```

### Remediation (Dev Only)

```bash
# Restart the leaking container
docker restart <container>

# If the container has a memory limit, increase it temporarily in compose:
#   deploy:
#     resources:
#       limits:
#         memory: 512M

# Recreate with new memory limit
docker compose up -d <service>

# Clear host-level caches if memory pressure is severe
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches

# Verify memory is released
docker stats --no-stream --format "{{.Name}}: {{.MemUsage}}" <container>
```

### Prevention

```
- Set memory limits in docker-compose for all services:
    deploy:
      resources:
        limits:
          memory: 256M
- Monitor memory trends over time, not just point-in-time values
- For Java: set -Xmx to 75% of container memory limit
- For Node.js: set --max-old-space-size
- For Python: use tracemalloc or memory_profiler to find leaks
- Schedule periodic container restarts for known-leaky services in dev
```

---

## Zombie Processes

### Symptoms

- `ps` shows processes in `Z` (zombie) state
- Container PID namespace fills up
- "fork: Cannot allocate memory" errors despite available memory
- `docker top <container>` shows zombie entries

### Diagnosis

```bash
# Check for zombie processes on the host
ps aux | grep -w Z | grep -v grep

# Check for zombies inside a specific container
docker exec <container> ps aux | grep -w Z

# Count zombies system-wide
ps aux | awk '$8=="Z"' | wc -l

# Find the parent of zombie processes
ps aux | awk '$8=="Z" {print $2}' | while read ZPID; do
    PPID=$(ps -o ppid= -p $ZPID 2>/dev/null | tr -d ' ')
    PNAME=$(ps -o comm= -p $PPID 2>/dev/null)
    echo "Zombie PID=$ZPID, Parent PID=$PPID ($PNAME)"
done

# Check if the container uses an init system
docker inspect --format='Init: {{.HostConfig.Init}}' <container>
```

### Remediation (Dev Only)

```bash
# Option 1: Restart the container (zombies are reaped on process exit)
docker restart <container>

# Option 2: If zombies are on the host, kill the parent process
# First identify the parent:
PPID=$(ps -o ppid= -p <zombie_pid> | tr -d ' ')
kill $PPID
# This forces the parent to exit, and init (PID 1) reaps the zombies

# Option 3: Enable tini init in docker-compose to prevent future zombies
# Add to docker-compose.yml:
#   services:
#     myservice:
#       init: true

# Verify zombies are gone
ps aux | awk '$8=="Z"' | wc -l
```

### Prevention

```
- Use init: true in docker-compose for all services
  This runs tini as PID 1, which properly reaps zombie children
- Alternatively, use --init flag: docker run --init ...
- In Dockerfiles, avoid CMD patterns that create orphan process trees:
    WRONG: CMD node server.js & node worker.js
    RIGHT: Use a process manager (supervisord, s6) or separate containers
- If writing a custom entrypoint, handle SIGCHLD signals
- Prefer one process per container (12-factor app principle)
```

---

## Disk Space Exhaustion

### Symptoms

- "No space left on device" errors in container logs or host
- Docker cannot pull images or create containers
- Build commands fail with disk space errors

### Diagnosis

```bash
# Host disk usage
df -h / /var/lib/docker /tmp

# Docker-specific disk usage
docker system df
docker system df -v

# Largest Docker images
docker images --format "{{.Size}}\t{{.Repository}}:{{.Tag}}" | sort -h -r | head -10

# Dangling resources
echo "Dangling images: $(docker images -f dangling=true -q | wc -l)"
echo "Dangling volumes: $(docker volume ls -f dangling=true -q | wc -l)"
echo "Stopped containers: $(docker ps -a -f status=exited -q | wc -l)"

# Build cache size
docker builder prune --dry-run 2>/dev/null || echo "Check: docker buildx du"

# Largest files on the host
du -sh /var/lib/docker/* 2>/dev/null | sort -h -r

# Largest log files
find /var/lib/docker/containers -name "*-json.log" -exec du -sh {} + 2>/dev/null | sort -h -r | head -5
```

### Remediation (Dev Only)

```bash
# Step 1: Remove stopped containers
docker container prune -f

# Step 2: Remove dangling images
docker image prune -f

# Step 3: Remove unused volumes (WARNING: data loss)
docker volume prune -f

# Step 4: Remove build cache
docker builder prune -f

# Step 5: If still low, remove all unused images (not just dangling)
docker image prune -a -f

# Step 6: Nuclear option -- remove everything unused
# docker system prune -a -f --volumes

# Step 7: Truncate large container log files
for LOG in $(find /var/lib/docker/containers -name "*-json.log" -size +100M 2>/dev/null); do
    echo "Truncating: $LOG ($(du -sh $LOG | cut -f1))"
    sudo truncate -s 0 "$LOG"
done

# Verify space recovered
df -h / /var/lib/docker
docker system df
```

### Prevention

```
- Set container log size limits in docker daemon config (/etc/docker/daemon.json):
    {
      "log-driver": "json-file",
      "log-opts": {
        "max-size": "10m",
        "max-file": "3"
      }
    }
- Schedule weekly docker system prune in dev environments
- Use .dockerignore to reduce build context size
- Use multi-stage builds to reduce final image size
- Monitor disk usage with alerts at 70% and 85%
- Pin image tags (avoid pulling latest repeatedly)
```

---

## Quick Reference: Recovery Decision Tree

```
Service is failing
├── Container not running?
│   ├── Exit code 0 → Stopped normally. Start it: docker start <name>
│   ├── Exit code 1 → Application error. Check logs: docker logs <name>
│   ├── Exit code 137 → OOM killed. Increase memory limit.
│   └── Exit code 139 → Segfault. Check for platform mismatch or corrupt image.
├── Container running but unhealthy?
│   ├── Health check failing → Check health check command: docker inspect <name>
│   ├── Dependency unavailable → Check dependency containers first
│   └── Port not responding → Check port mapping and internal binding
├── Connection refused?
│   ├── Target not running → Start the target service
│   ├── Port conflict → Resolve with ss -tlnp | grep :<port>
│   └── Wrong address → Check connection string / environment variables
├── Disk full?
│   ├── Docker images → docker image prune -a -f
│   ├── Build cache → docker builder prune -f
│   ├── Log files → Truncate or configure rotation
│   └── Volumes → docker volume prune -f (dev only, data loss)
└── Memory exhausted?
    ├── Container OOM → Increase limit or fix leak
    ├── Host memory low → Check for runaway processes
    └── Swap thrashing → Add swap or reduce workload
```
