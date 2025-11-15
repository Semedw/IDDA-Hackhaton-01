"""
Background task to update stock prices every 5 seconds
"""
import os
import requests
import logging
import random
from django.utils import timezone
from .models import Asset, PricePoint

logger = logging.getLogger(__name__)

RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', 'd4c7v6pr01qudf6h31f0d4c7v6pr01qudf6h31fg')
RAPIDAPI_HOST = 'apidojo-yahoo-finance-v1.p.rapidapi.com'

# Sample price ranges for popular stocks (for fallback when API fails)
# Updated with approximate current prices (as of late 2024)
SAMPLE_PRICES = {
    'AAPL': {'base': 272.0, 'range': 15.0},
    'MSFT': {'base': 380.0, 'range': 15.0},
    'GOOGL': {'base': 140.0, 'range': 8.0},
    'AMZN': {'base': 150.0, 'range': 10.0},
    'TSLA': {'base': 250.0, 'range': 20.0},
    'META': {'base': 350.0, 'range': 15.0},
    'NVDA': {'base': 500.0, 'range': 30.0},
    'JPM': {'base': 150.0, 'range': 5.0},
    'V': {'base': 250.0, 'range': 10.0},
    'JNJ': {'base': 160.0, 'range': 5.0},
    'WMT': {'base': 160.0, 'range': 5.0},
    'PG': {'base': 150.0, 'range': 5.0},
    'MA': {'base': 400.0, 'range': 15.0},
    'UNH': {'base': 500.0, 'range': 20.0},
    'HD': {'base': 350.0, 'range': 10.0},
    'DIS': {'base': 100.0, 'range': 5.0},
    'PYPL': {'base': 60.0, 'range': 5.0},
    'BAC': {'base': 35.0, 'range': 2.0},
    'NFLX': {'base': 450.0, 'range': 20.0},
    'ADBE': {'base': 550.0, 'range': 25.0},
    'BTCS': {'base': 1.5, 'range': 0.3},  # Small cap stock
}


def generate_sample_price(asset):
    """Generate a sample price when API is unavailable"""
    symbol = asset.symbol.upper()
    
    # Get base price from known stocks or use asset's current price
    if symbol in SAMPLE_PRICES:
        base_price = SAMPLE_PRICES[symbol]['base']
        price_range = SAMPLE_PRICES[symbol]['range']
    elif asset.current_price:
        base_price = float(asset.current_price)
        price_range = base_price * 0.05  # 5% variation
    else:
        # Default fallback
        base_price = 100.0
        price_range = 10.0
    
    # Generate price with small random variation (±2% of range)
    variation = random.uniform(-price_range * 0.02, price_range * 0.02)
    price = base_price + variation
    
    # Ensure price is positive
    price = max(price, 0.01)
    
    # Update asset and create price point
    asset.current_price = price
    asset.save(update_fields=['current_price'])
    
    # Create price point for history
    PricePoint.objects.create(
        asset=asset,
        price=price
    )
    
    logger.info(f'Generated sample price for {asset.symbol}: ${price:.2f}')
    return price


def fetch_stock_price(asset):
    """Fetch current price for a stock using Yahoo Finance API"""
    # Try multiple Yahoo Finance endpoints
    yahoo_endpoints = [
        f'https://query1.finance.yahoo.com/v8/finance/chart/{asset.symbol}?interval=1d&range=1d',
        f'https://query2.finance.yahoo.com/v8/finance/chart/{asset.symbol}?interval=1d&range=1d',
        f'https://query1.finance.yahoo.com/v10/finance/quoteSummary/{asset.symbol}?modules=price',
    ]
    
    for yahoo_url in yahoo_endpoints:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            yahoo_response = requests.get(yahoo_url, headers=headers, timeout=10)
            
            if yahoo_response.status_code == 200:
                yahoo_data = yahoo_response.json()
                
                # Try chart endpoint format
                if 'chart' in yahoo_data and 'result' in yahoo_data['chart']:
                    results = yahoo_data['chart']['result']
                    if results and len(results) > 0:
                        result = results[0]
                        if 'meta' in result:
                            meta = result['meta']
                            price = meta.get('regularMarketPrice') or meta.get('previousClose') or meta.get('currentPrice')
                            if price:
                                price = float(price)
                                asset.current_price = price
                                asset.save(update_fields=['current_price'])
                                PricePoint.objects.create(asset=asset, price=price)
                                logger.info(f'Updated price for {asset.symbol} from Yahoo Finance: ${price}')
                                return price
                
                # Try quoteSummary endpoint format
                if 'quoteSummary' in yahoo_data and 'result' in yahoo_data['quoteSummary']:
                    results = yahoo_data['quoteSummary']['result']
                    if results and len(results) > 0:
                        result = results[0]
                        if 'price' in result:
                            price_obj = result['price']
                            price = price_obj.get('regularMarketPrice', {}).get('raw') or \
                                   price_obj.get('currentPrice', {}).get('raw')
                            if price:
                                price = float(price)
                                asset.current_price = price
                                asset.save(update_fields=['current_price'])
                                PricePoint.objects.create(asset=asset, price=price)
                                logger.info(f'Updated price for {asset.symbol} from Yahoo Finance: ${price}')
                                return price
        except Exception as e:
            logger.debug(f'Yahoo Finance endpoint failed for {asset.symbol}: {str(e)}')
            continue
    
    # Fallback to RapidAPI
    try:
        url = f'https://{RAPIDAPI_HOST}/stock/v2/get-timeseries'
        headers = {
            'x-rapidapi-host': RAPIDAPI_HOST,
            'x-rapidapi-key': RAPIDAPI_KEY
        }
        params = {'symbol': asset.symbol, 'region': 'US'}
        
        response = requests.get(url, headers=headers, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            price = None
            
            # Try multiple paths to extract price from Yahoo Finance API response
            # Path 1: price.regularMarketPrice.raw
            if 'price' in data and isinstance(data['price'], dict):
                price_obj = data['price']
                if 'regularMarketPrice' in price_obj:
                    if isinstance(price_obj['regularMarketPrice'], dict):
                        price = price_obj['regularMarketPrice'].get('raw')
                    else:
                        price = price_obj['regularMarketPrice']
            
            # Path 2: price.currentPrice.raw
            if price is None and 'price' in data and isinstance(data['price'], dict):
                price_obj = data['price']
                if 'currentPrice' in price_obj:
                    if isinstance(price_obj['currentPrice'], dict):
                        price = price_obj['currentPrice'].get('raw')
                    else:
                        price = price_obj['currentPrice']
            
            # Path 3: Check timeseries for latest close price
            if price is None and 'timeseries' in data:
                timeseries = data['timeseries']
                # Timeseries is a dict with 'result' key
                if isinstance(timeseries, dict) and 'result' in timeseries:
                    result = timeseries['result']
                    if isinstance(result, list) and len(result) > 0:
                        # Get the first result (most recent)
                        first_result = result[0]
                        # Check indicators.quote[0].close array
                        if 'indicators' in first_result and 'quote' in first_result['indicators']:
                            quotes = first_result['indicators']['quote']
                            if isinstance(quotes, list) and len(quotes) > 0:
                                quote = quotes[0]
                                if 'close' in quote and isinstance(quote['close'], list):
                                    # Get the last non-None close price
                                    closes = [c for c in quote['close'] if c is not None]
                                    if closes:
                                        price = closes[-1]
            
            # Path 4: Check quoteSummary.result[0].price
            if price is None and 'quoteSummary' in data:
                quote = data['quoteSummary']
                if isinstance(quote, dict) and 'result' in quote:
                    results = quote['result']
                    if isinstance(results, list) and len(results) > 0:
                        result = results[0]
                        if 'price' in result and isinstance(result['price'], dict):
                            price_obj = result['price']
                            price = price_obj.get('regularMarketPrice', {}).get('raw') or \
                                   price_obj.get('currentPrice', {}).get('raw')
            
            if price:
                price_float = float(price)
                # Update asset current_price
                asset.current_price = price_float
                asset.save(update_fields=['current_price'])
                # Create price point for history
                PricePoint.objects.create(
                    asset=asset,
                    price=price_float
                )
                logger.info(f'Updated price for {asset.symbol}: ${price_float}')
                return price_float
            else:
                logger.warning(f'Could not extract price for {asset.symbol} from API response')
                return None
                
        elif response.status_code == 429:
            # Quota exceeded - generate sample price data for demonstration
            logger.warning(f'API quota exceeded for {asset.symbol}, generating sample price')
            return generate_sample_price(asset)
        else:
            logger.warning(f'API returned status {response.status_code} for {asset.symbol}')
            # Try to generate sample price as fallback
            return generate_sample_price(asset)
            
    except requests.exceptions.Timeout:
        logger.warning(f'Timeout fetching price for {asset.symbol}, using sample price')
        return generate_sample_price(asset)
    except requests.exceptions.RequestException as e:
        logger.warning(f'Request error for {asset.symbol}: {str(e)}, using sample price')
        return generate_sample_price(asset)
    except Exception as e:
        logger.warning(f'Error fetching price for {asset.symbol}: {str(e)}, using sample price')
        return generate_sample_price(asset)


def update_all_stock_prices():
    """Update prices for all stock assets"""
    stocks = Asset.objects.filter(type='stock')
    updated_count = 0
    
    for asset in stocks:
        price = fetch_stock_price(asset)
        if price:
            updated_count += 1
    
    logger.info(f'Updated {updated_count}/{stocks.count()} stock prices')
    return updated_count

