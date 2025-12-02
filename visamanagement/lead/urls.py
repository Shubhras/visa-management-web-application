from django.urls import path
from .views import *
urlpatterns = [
    path('applicants/create/', ApplicantCreateAPIView.as_view(), name='create-applicant'),
    path("applicant/get/", ApplicantGetAPIView.as_view(), name='get-applicant'),
    path("applicant/detail/<uuid:uuid>/", ApplicantDetailAPIView.as_view(), name='detail-by-uuid-applicant'),
    path('applicants/<uuid:uuid>/', ApplicantUpdateAPIView.as_view(), name='update-applicant'),
    path('applicant/delete/',ApplicantDeleteAPIView.as_view(),name='applicant-delete'),
    
    #<--------------Education--------------------->
    path('education/create/',EducationCreateAPIView.as_view()),
    path('education/get/',EducationListAPIView.as_view()),
    path('education/<uuid:uuid>/',EducationDetailAPIView.as_view()),
    path('education/<uuid:uuid>/update/',EducationUpdateAPIView.as_view()),
    path('education/delete/',EducationDeleteAPIView.as_view()),

    #<------------------Work_Experience--------------->
    path('workexperience/create/',WorkExperienceCreateAPIView.as_view(),name = 'create-experience'),
    path('workexperience/get/',WorkExperienceListAPIView.as_view()),
    path('workexperience/<uuid:uuid>/',WorkExperienceDetailAPIView().as_view()),
    path('workexperience/<uuid:uuid>/update/',WorkExperienceUpdateAPIView.as_view()),
    path('workexperience/delete/',WorkExperiencenDeleteAPIView.as_view()),

    #<------------------Language_Ability------------------->
    path('languageability/create/',LanguageAbilityCreateAPIView.as_view(),name='create-ability'),
    path('languageability/get/',LanguageAbilityListAPIView.as_view(),name='abilit-list'),
    path('languageability/<uuid:uuid>/',LanguageAbilityDetailAPIView.as_view(),name='language-get-uuid'),
    path('languageability/<uuid:uuid>/update/',LanguageAbilityUpdateAPIView.as_view(),name='language-update'),
    path('languageability/delete/',LanguageAbilityDeleteAPIView.as_view(),name='language-delete'),

    #<-------------------- Entrance Test Abiity--------------->
    path('entracetestability/create/',EntranceTestAbiityCreateAPIView.as_view(),name = 'entrence-create'),
    path('entracetestability/get/',EntranceTestAbilityListAPIView.as_view()),
    path('entracetestability/<uuid:uuid>/',EntranceTestAbilityDetailAPIView.as_view()),
    path('entracetestability/<uuid:uuid>/update/',EntranceTestAbilityUpdateAPIView.as_view()),
    path('entracetestability/delete/',EntranceTestAbilityDeleteAPIView.as_view()),
    
    #<-------------------------Relative-------------------->
    path('relative/create/',RelativeCreateAPTView.as_view(),name='relative-create')
]