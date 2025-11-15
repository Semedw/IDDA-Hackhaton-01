"""
URL configuration for verbix_ai project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    """API root endpoint"""
    return JsonResponse({
        'message': 'verbai API',
        'version': '1.0',
        'endpoints': {
            'auth': '/api/auth/',
            'assets': '/api/assets/',
            'analysis': '/api/analysis/',
            'chat': '/api/chat/',
            'recommendations': '/api/recommendations/',
            'news': '/api/news/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    path('api/auth/', include('accounts.urls')),
    path('api/assets/', include('market.urls')),
    path('api/analysis/', include('analysis.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/recommendations/', include('recommendations.urls')),
    path('api/news/', include('news.urls')),
]

