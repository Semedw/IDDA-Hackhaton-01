"""
Management command to add popular stocks to the database
"""
from django.core.management.base import BaseCommand
from market.models import Asset
import requests
import os

# Popular stocks to add
POPULAR_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'JNJ',
    'WMT', 'PG', 'MA', 'UNH', 'HD', 'DIS', 'BAC', 'ADBE', 'NFLX', 'CRM',
    'PYPL', 'INTC', 'CMCSA', 'PEP', 'COST', 'TMO', 'AVGO', 'CSCO', 'ABT', 'NKE'
]

RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', 'd4c7v6pr01qudf6h31f0d4c7v6pr01qudf6h31fg')
RAPIDAPI_HOST = 'apidojo-yahoo-finance-v1.p.rapidapi.com'


class Command(BaseCommand):
    help = 'Add popular stocks to the database'

    def handle(self, *args, **options):
        self.stdout.write('Adding popular stocks to database...')
        
        added_count = 0
        skipped_count = 0
        
        for symbol in POPULAR_STOCKS:
            try:
                # Try to get stock name from API
                url = f'https://{RAPIDAPI_HOST}/stock/v2/get-timeseries'
                headers = {
                    'x-rapidapi-host': RAPIDAPI_HOST,
                    'x-rapidapi-key': RAPIDAPI_KEY
                }
                params = {'symbol': symbol, 'region': 'US'}
                
                try:
                    response = requests.get(url, headers=headers, params=params, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        name = data.get('quoteType', {}).get('longName', symbol) or symbol
                    else:
                        name = symbol
                except:
                    name = symbol
                
                asset, created = Asset.objects.get_or_create(
                    symbol=symbol,
                    defaults={
                        'type': 'stock',
                        'name': name
                    }
                )
                
                if created:
                    added_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ Added {symbol} - {name}'))
                else:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(f'⊘ Skipped {symbol} (already exists)'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error adding {symbol}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\nCompleted! Added: {added_count}, Skipped: {skipped_count}'
        ))

