from django.urls import path
from .views import run_analysis, get_analysis

urlpatterns = [
    path('run/', run_analysis, name='run-analysis'),
    path('<int:asset_id>/', get_analysis, name='get-analysis'),
]

