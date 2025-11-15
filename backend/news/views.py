import feedparser
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import NewsItem
from .serializers import NewsItemSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_news(request):
    limit = int(request.query_params.get('limit', 10))
    
    # Try to fetch from RSS feeds
    rss_feeds = [
        'https://feeds.finance.yahoo.com/rss/2.0/headline?s=TSLA&region=US&lang=en-US',
        'https://www.coindesk.com/arc/outboundfeeds/rss/',
    ]
    
    news_items = []
    
    # Try to parse RSS feeds
    for feed_url in rss_feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:  # Limit per feed
                news_item, created = NewsItem.objects.get_or_create(
                    link=entry.link,
                    defaults={
                        'title': entry.title,
                        'summary': entry.get('summary', ''),
                        'source': feed.feed.get('title', 'Unknown')
                    }
                )
                if created:
                    news_items.append(news_item)
        except Exception as e:
            print(f"Error fetching RSS feed {feed_url}: {e}")
            continue
    
    # If no news from RSS, return sample data
    if not news_items:
        # Create sample news items if none exist
        if not NewsItem.objects.exists():
            sample_news = [
                {
                    'title': 'Bitcoin Reaches New All-Time High',
                    'link': 'https://example.com/news1',
                    'summary': 'Bitcoin has reached a new all-time high, driven by institutional adoption.',
                    'source': 'Crypto News'
                },
                {
                    'title': 'Tech Stocks Rally on Strong Earnings',
                    'link': 'https://example.com/news2',
                    'summary': 'Major tech companies report strong quarterly earnings, driving market gains.',
                    'source': 'Market Watch'
                },
                {
                    'title': 'Federal Reserve Holds Interest Rates Steady',
                    'link': 'https://example.com/news3',
                    'summary': 'The Fed maintains current interest rates, citing stable economic conditions.',
                    'source': 'Financial Times'
                },
            ]
            for item in sample_news:
                NewsItem.objects.create(**item)
    
    # Return latest news
    news = NewsItem.objects.all()[:limit]
    serializer = NewsItemSerializer(news, many=True)
    return Response(serializer.data)

