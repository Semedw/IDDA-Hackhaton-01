#!/bin/bash
# Script to start Celery worker and beat

echo "Starting Celery services..."

# Start Redis if not running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Starting Redis..."
    redis-server --daemonize yes
fi

# Start Celery Worker
echo "Starting Celery Worker..."
celery -A verbix_ai worker --loglevel=info &

# Start Celery Beat
echo "Starting Celery Beat..."
celery -A verbix_ai beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

echo "Celery services started!"
echo "Worker PID: $!"
echo "Beat PID: $!"

wait

