from django.urls import path
from .views import SignupView, LoginView, profile_view

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', profile_view, name='profile'),
]

