from django.db import models
from django.contrib.auth.models import User
from market.models import Asset


class Recommendation(models.Model):
    ACTIONS = [
        ('BUY', 'Buy'),
        ('HOLD', 'Hold'),
        ('SELL', 'Sell'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='recommendations')
    action = models.CharField(max_length=10, choices=ACTIONS)
    amount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    rationale = models.TextField()
    confidence = models.CharField(max_length=10, choices=CONFIDENCE_LEVELS, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.asset.symbol} - {self.action}"

    class Meta:
        ordering = ['-created_at']

