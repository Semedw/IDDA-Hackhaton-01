from django.db import models
from django.contrib.auth.models import User


class Asset(models.Model):
    ASSET_TYPES = [
        ('stock', 'Stock'),
        ('crypto', 'Cryptocurrency'),
    ]
    
    type = models.CharField(max_length=10, choices=ASSET_TYPES)
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    users = models.ManyToManyField(User, related_name='tracked_assets', blank=True)
    
    # Stock details
    current_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    previous_close = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    market_cap = models.BigIntegerField(null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    day_high = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    day_low = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    year_high = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    year_low = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    pe_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dividend_yield = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    price_change = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    price_change_percent = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} ({self.name})"

    class Meta:
        ordering = ['symbol']


class PricePoint(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='prices')
    timestamp = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=20, decimal_places=8)

    def __str__(self):
        return f"{self.asset.symbol} - {self.price} @ {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

