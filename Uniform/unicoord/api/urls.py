from django.urls import path
from .views import Module3DCreateView,Module3DUpdateView

urlpatterns = [
    path("module/create/", Module3DCreateView.as_view()),
    path('module/<int:pk>/',Module3DUpdateView.as_view())
]
