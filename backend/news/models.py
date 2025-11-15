from django.db import models


class NewsItem(models.Model):
    title = models.CharField(max_length=500)
    link = models.URLField()
    summary = models.TextField(blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_at']

