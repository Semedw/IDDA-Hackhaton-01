#!/bin/bash
# Helper script to use docker compose v2 or work around docker-compose v1 issues

# Try docker compose v2 first (newer)
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "Using Docker Compose v2..."
    docker compose "$@"
# Fall back to docker-compose v1
elif command -v docker-compose &> /dev/null; then
    echo "Using docker-compose v1..."
    # Use --no-deps to avoid event watching issues
    if [[ "$1" == "up" ]]; then
        docker-compose up --no-deps "$@"
    else
        docker-compose "$@"
    fi
else
    echo "Error: Neither 'docker compose' nor 'docker-compose' found"
    exit 1
fi

