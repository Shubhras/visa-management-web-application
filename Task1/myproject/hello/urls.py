from django.contrib import admin
from django.urls import path
from .views import hello_view

urlpatterns = [
    path('view',hello_view),
]