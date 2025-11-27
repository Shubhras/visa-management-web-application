from django.urls import path
from .views import *
urlpatterns = [
    path('applicants/create/', ApplicantCreateAPIView.as_view(), name='create-applicant'),
    path("applicant/get/", ApplicantGetAPIView.as_view(), name='get-applicant'),
    path("applicant/detail/<uuid:uuid>/", ApplicantDetailAPIView.as_view(), name='detail-by-uuid-applicant'),
    path('applicants/<uuid:uuid>/', ApplicantUpdateAPIView.as_view(), name='update-applicant'),

]