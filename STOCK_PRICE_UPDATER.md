# Stock Price Updater Setup

This document explains how to set up and use the automatic stock price updater that fetches real-time prices from Yahoo Finance API every 5 seconds.

## Features

- ✅ Fetches real stock prices from Yahoo Finance API
- ✅ Updates prices every 5 seconds automatically
- ✅ Adds 30 popular stocks to database
- ✅ Background scheduler runs continuously

## Setup

### 1. Add API Key to Environment

Add your RapidAPI key to `.env`:

```bash
RAPIDAPI_KEY=115497db44mshf29fcb7003a8abbp17d6bfjsne041e514ecd1
```

### 2. Install Dependencies

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Add Popular Stocks to Database

```bash
python manage.py add_stocks
```

This will add 30 popular stocks (AAPL, MSFT, GOOGL, etc.) to the database.

### 5. Start Price Updater

**Option A: Automatic (Recommended)**
The price updater starts automatically when you run the Django server:

```bash
python manage.py runserver
```

**Option B: Manual**
Start it separately:

```bash
python manage.py start_price_updater
```

## How It Works

1. **Price Fetcher** (`market/price_updater.py`):
   - Fetches prices from Yahoo Finance API
   - Parses multiple response formats
   - Creates PricePoint records in database

2. **Scheduler** (`market/price_scheduler.py`):
   - Uses APScheduler to run updates every 5 seconds
   - Runs in background thread
   - Automatically starts with Django server

3. **Management Commands**:
   - `add_stocks`: Adds popular stocks to database
   - `start_price_updater`: Manually start the scheduler

## API Endpoint Used

```
GET https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-timeseries
Headers:
  x-rapidapi-host: apidojo-yahoo-finance-v1.p.rapidapi.com
  x-rapidapi-key: YOUR_API_KEY
Params:
  symbol: STOCK_SYMBOL (e.g., AAPL)
  region: US
```

## Popular Stocks Added

The `add_stocks` command adds these 30 popular stocks:
- AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA, JPM, V, JNJ
- WMT, PG, MA, UNH, HD, DIS, BAC, ADBE, NFLX, CRM
- PYPL, INTC, CMCSA, PEP, COST, TMO, AVGO, CSCO, ABT, NKE

## Monitoring

Check the Django server logs to see price updates:

```
Updated price for AAPL: $150.25
Updated price for MSFT: $350.10
Updated 25/30 stock prices
```

## Troubleshooting

### Prices not updating?
1. Check API key is set in `.env`
2. Check server logs for errors
3. Verify stocks exist: `python manage.py shell` → `from market.models import Asset; Asset.objects.filter(type='stock').count()`

### API rate limits?
- The API may have rate limits
- Errors will be logged but won't crash the scheduler
- Consider increasing interval if needed (edit `price_scheduler.py`)

### Scheduler not starting?
- Check Django server is running
- Check logs for errors
- Try manual start: `python manage.py start_price_updater`

## Customization

### Change Update Interval

Edit `backend/market/price_scheduler.py`:

```python
trigger=IntervalTrigger(seconds=10)  # Change from 5 to 10 seconds
```

### Add More Stocks

Edit `backend/market/management/commands/add_stocks.py`:

```python
POPULAR_STOCKS = [
    'AAPL', 'MSFT', 'YOUR_STOCK', ...
]
```

Then run: `python manage.py add_stocks`

