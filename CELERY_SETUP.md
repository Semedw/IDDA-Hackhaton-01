# Celery & Redis Setup for Stock Updates

This document explains how to set up Celery and Redis for automatic stock detail updates every 5 seconds.

## Architecture

- **Redis**: Message broker and result backend
- **Celery Worker**: Processes background tasks
- **Celery Beat**: Scheduler that triggers tasks every 5 seconds
- **Django**: Main application

## Setup

### 1. Install Dependencies

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Redis

**Option A: Using Docker Compose (Recommended)**
```bash
docker-compose up redis
```

**Option B: Local Redis**
```bash
# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Start Redis
redis-server
```

### 3. Run Migrations

```bash
python manage.py migrate
```

This will create the `django_celery_beat` tables for scheduling.

### 4. Start Services

**Terminal 1: Django Server**
```bash
python manage.py runserver
```

**Terminal 2: Celery Worker**
```bash
celery -A verbix_ai worker --loglevel=info
```

**Terminal 3: Celery Beat (Scheduler)**
```bash
celery -A verbix_ai beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### 5. Using Docker Compose (All Services)

```bash
docker-compose up
```

This starts:
- PostgreSQL database
- Redis
- Django backend
- Celery worker
- Celery beat scheduler

## Stock Details Updated

Every 5 seconds, the following stock details are updated:

- **Current Price**: Latest market price
- **Previous Close**: Previous day's closing price
- **Market Cap**: Market capitalization
- **Volume**: Trading volume
- **Day High/Low**: Today's high and low prices
- **Year High/Low**: 52-week high and low
- **PE Ratio**: Price-to-earnings ratio
- **Dividend Yield**: Dividend yield percentage
- **Price Change**: Absolute price change
- **Price Change %**: Percentage price change

## Configuration

### Environment Variables

Add to `.env`:

```bash
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Update Interval

To change the update interval, edit `backend/verbix_ai/settings.py`:

```python
CELERY_BEAT_SCHEDULE = {
    'update-stock-details-every-5-seconds': {
        'task': 'market.tasks.update_all_stock_details',
        'schedule': 10.0,  # Change to 10 seconds
    },
}
```

## Monitoring

### Check Celery Worker Status

```bash
celery -A verbix_ai inspect active
```

### Check Scheduled Tasks

```bash
celery -A verbix_ai inspect scheduled
```

### View Logs

Check the terminal where Celery worker/beat is running for update logs.

## Troubleshooting

### Redis Connection Error

- Ensure Redis is running: `redis-cli ping` (should return "PONG")
- Check `CELERY_BROKER_URL` in settings

### Tasks Not Running

- Verify Celery Beat is running
- Check database migrations: `python manage.py migrate`
- Check logs for errors

### High API Rate Limits

- Consider increasing update interval
- Add rate limiting to tasks
- Use task retries with exponential backoff

## Manual Task Execution

You can manually trigger updates:

```python
from market.tasks import update_stock_details, update_all_stock_details

# Update single stock
update_stock_details.delay(asset_id=1)

# Update all stocks
update_all_stock_details.delay()
```

## API Response

Stock details are now included in the API response:

```json
{
  "id": 1,
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "current_price": 150.25,
  "previous_close": 149.50,
  "market_cap": 2500000000000,
  "volume": 50000000,
  "day_high": 151.00,
  "day_low": 149.00,
  "year_high": 180.00,
  "year_low": 120.00,
  "pe_ratio": 28.5,
  "dividend_yield": 0.5,
  "price_change": 0.75,
  "price_change_percent": 0.5,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

