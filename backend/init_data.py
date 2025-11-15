"""
Script to initialize sample data for development
Run with: python manage.py shell < init_data.py
Or: python manage.py shell, then exec(open('init_data.py').read())
"""
from django.contrib.auth.models import User
from accounts.models import UserProfile
from market.models import Asset, PricePoint
import random

# Create sample assets if they don't exist
sample_assets = [
    {'symbol': 'AAPL', 'name': 'Apple Inc.', 'type': 'stock'},
    {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'type': 'stock'},
    {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'type': 'stock'},
    {'symbol': 'bitcoin', 'name': 'Bitcoin', 'type': 'crypto'},
    {'symbol': 'ethereum', 'name': 'Ethereum', 'type': 'crypto'},
]

for asset_data in sample_assets:
    asset, created = Asset.objects.get_or_create(
        symbol=asset_data['symbol'],
        defaults=asset_data
    )
    if created:
        # Add some sample price points
        for i in range(10):
            base_price = random.uniform(50, 500) if asset.type == 'stock' else random.uniform(20000, 50000)
            price = base_price + random.uniform(-10, 10)
            PricePoint.objects.create(asset=asset, price=round(price, 2))
        print(f"Created asset: {asset.symbol}")

print("Sample data initialization complete!")

