# Diagnostic Discipline

Domain principles, AI discipline rules, anti-patterns, and error-recovery procedures
for environment-health work. Load before diagnosing or remediating.

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

## AI Discipline Rules

**Probe before diagnosing.** Run `docker inspect` and read its output before forming any diagnosis. Parse `State.Health.Status` from actual command output — never assume container state. Assumptions about expected services that are not verified from actual command output produce wrong diagnoses and misdirected remediation.

**Never modify production resources.** Always confirm the target environment before running any mutating command. Verify `DOCKER_HOST` is pointing to the local daemon and check container labels (`docker inspect <id> --format='{{json .Config.Labels}}'`) to confirm `environment=dev` before any restart, reconfigure, or rebuild action.

**Verify after every remediation.** Re-run the same probe that detected the problem after applying a fix. Reporting "fixed" based solely on the remediation command succeeding — without re-probing — is a false positive. After `docker start <container>`, wait 5 seconds and check `docker inspect <container> --format='{{.State.Health.Status}}'` before reporting healthy.

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

**Docker daemon not running** ("Cannot connect to the Docker daemon"): Check `systemctl status docker` and `ls -la /var/run/docker.sock`. Check user groups: `groups | grep docker`. In dev: `sudo systemctl start docker`. Wait for daemon: `until docker info >/dev/null 2>&1; do sleep 1; done`.

**Container restart loop** (RestartCount > 5): Check exit code and OOM status (`docker inspect --format='{{.State.ExitCode}} {{.State.OOMKilled}}' <name>`). Read logs from last run (`docker logs --tail 100 <name>`). Check mounts and env vars via `docker inspect`. If OOM: increase memory limit in compose file. If config error: fix config, then `docker compose up -d <service>`.

**Network connectivity between containers** (cannot reach another container by name): Verify both are on the same network (`docker network inspect <network> --format='{{range .Containers}}{{.Name}} {{end}}'`). Test DNS from inside: `docker exec <container> nslookup <target>`. Test connectivity: `docker exec <container> curl -s http://<target>:<port>/health`. If DNS fails: recreate the network (dev only).

**Volume mount failures** (container exits, mount path not found): Check mount config with `docker inspect --format='{{json .Mounts}}' <name>`. Verify host path exists (`ls -la /path`) and permissions (`stat /path`). For named volumes: `docker volume inspect <volume_name>`. If volume corrupted in dev: `docker volume rm <name> && docker compose up -d`.
