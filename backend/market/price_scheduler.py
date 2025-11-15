"""
Scheduler to update stock prices every 5 seconds
"""
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

scheduler = None


def start_price_scheduler():
    """Start the background scheduler for price updates"""
    global scheduler
    
    if scheduler and scheduler.running:
        logger.info('Price scheduler already running')
        return
    
    try:
        scheduler = BackgroundScheduler()
        
        # Add job to update prices every 5 seconds
        scheduler.add_job(
            update_prices_job,
            trigger=IntervalTrigger(seconds=5),
            id='update_stock_prices',
            name='Update stock prices every 5 seconds',
            replace_existing=True,
        )
        
        scheduler.start()
        logger.info('Price scheduler started - updating prices every 5 seconds')
        print('✅ Price updater started - updating prices every 5 seconds')
        
    except Exception as e:
        logger.error(f'Error starting price scheduler: {str(e)}')
        print(f'❌ Error starting price scheduler: {str(e)}')


def update_prices_job():
    """Job function to update prices"""
    try:
        from .price_updater import update_all_stock_prices
        update_all_stock_prices()
    except Exception as e:
        logger.error(f'Error in price update job: {str(e)}')


def stop_price_scheduler():
    """Stop the price scheduler"""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info('Price scheduler stopped')

