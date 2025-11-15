from django.db import models
from market.models import Asset


class AnalysisResult(models.Model):
    SENTIMENTS = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]
    
    RISK_RATINGS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='analyses')
    ai_summary = models.TextField()
    sentiment = models.CharField(max_length=10, choices=SENTIMENTS, default='neutral')
    risk_rating = models.CharField(max_length=10, choices=RISK_RATINGS, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.asset.symbol} - {self.sentiment} ({self.created_at})"

    class Meta:
        ordering = ['-created_at']

