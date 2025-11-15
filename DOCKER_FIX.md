# Docker Compose Fix

## Problem
`KeyError: 'ContainerConfig'` error when using `docker-compose` (v1.29.2)

## Solution
Use `docker compose` (v2) instead of `docker-compose` (v1)

## Quick Fix

### Option 1: Use Docker Compose v2 directly
```bash
docker compose up --build
```

### Option 2: Create an alias (add to ~/.bashrc)
```bash
alias docker-compose='docker compose'
```

### Option 3: Use the start script
```bash
./start.sh
```

## Commands Comparison

| Old (v1) | New (v2) |
|----------|----------|
| `docker-compose up` | `docker compose up` |
| `docker-compose down` | `docker compose down` |
| `docker-compose build` | `docker compose build` |
| `docker-compose exec` | `docker compose exec` |
| `docker-compose logs` | `docker compose logs` |

## Verify Version
```bash
docker compose version
# Should show: Docker Compose version v2.x.x
```

## Why This Happens
- `docker-compose` v1.29.2 has a bug with event watching in newer Docker versions
- Docker Compose v2 is the modern replacement and doesn't have this issue
- Both commands do the same thing, but v2 is actively maintained

