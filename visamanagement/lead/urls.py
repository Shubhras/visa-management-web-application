from django.urls import path
from .views import *
urlpatterns = [
    path('applicants/create/', ApplicantCreateAPIView.as_view(), name='create-applicant'),
    path('applicants/<uuid:uuid>/', ApplicantUpdateAPIView.as_view(), name='update-applicant'),

]