from django.urls import path
from .views import generate_recommendations, my_recommendations

urlpatterns = [
    path('generate/', generate_recommendations, name='generate-recommendations'),
    path('my/', my_recommendations, name='my-recommendations'),
]

