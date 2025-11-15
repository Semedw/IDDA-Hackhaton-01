"""
Celery tasks for market data updates
"""
import os
import requests
import logging
from celery import shared_task
from django.utils import timezone
from .models import Asset, PricePoint

logger = logging.getLogger(__name__)

RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', 'd4c7v6pr01qudf6h31f0d4c7v6pr01qudf6h31fg')
RAPIDAPI_HOST = 'apidojo-yahoo-finance-v1.p.rapidapi.com'


@shared_task
def update_stock_details(asset_id):
    """Update detailed information for a single stock"""
    try:
        asset = Asset.objects.get(id=asset_id, type='stock')
        
        # Use the same approach as price_updater.py which works
        # fetch_stock_price already updates asset.current_price and creates PricePoint
        from .price_updater import fetch_stock_price
        current_price = fetch_stock_price(asset)
        
        if current_price:
            logger.info(f'Updated stock details for {asset.symbol}: ${current_price}')
            return f'Updated {asset.symbol}'
        else:
            logger.warning(f'Could not fetch price for {asset.symbol}')
            return None
            
    except Asset.DoesNotExist:
        logger.warning(f'Asset {asset_id} not found')
        return None
    except Exception as e:
        logger.error(f'Error updating stock {asset_id}: {str(e)}')
        import traceback
        logger.error(traceback.format_exc())
        return None


@shared_task
def update_all_stock_details():
    """Update details for all stocks"""
    stocks = Asset.objects.filter(type='stock')
    updated_count = 0
    
    for stock in stocks:
        try:
            result = update_stock_details.delay(stock.id)
            updated_count += 1
        except Exception as e:
            logger.error(f'Error queuing update for {stock.symbol}: {str(e)}')
    
    logger.info(f'Queued {updated_count} stock detail updates')
    return f'Queued {updated_count} updates'
