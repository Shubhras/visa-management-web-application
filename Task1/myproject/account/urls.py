from django.urls import path
from .views import users_api

urlpatterns = [
    path('users',users_api),
]