from django.urls import path
from .views import *

urlpatterns = [

    path("login/", MasterTokenLoginAPIView.as_view(), name="master-login"),
    path('genders/create/', GenderCreateAPIView.as_view()),
    path('gender/list/', GenderListAPIView.as_view()),
    path('genders/<uuid:uuid>/', GenderDetailAPIView.as_view()),
    path('genders/update/<uuid:uuid>/', GenderUpdateAPIView.as_view()),
    path('genders/<uuid:uuid>/delete/', GenderDeleteAPIView.as_view()),

    path('Maritalstatus/create/', MaritalstatusCreateAPIView.as_view(),name='Maritalstatus-create'),
    path('Maritalstatus/list/', MaritalstatusListAPIView.as_view(),name='Maritalstatus-list'),
    path('Maritalstatus/<uuid:uuid>/', MaritalstatusDetailAPIView.as_view(), name='Maritalstatus-detail'),
    path('Maritalstatus/<uuid:uuid>/update/', MaritalstatusUpdateAPIView.as_view(),name='Maritalstatus-update'),

    path('continents/create/', ContinentsCreateAPIView.as_view(),name='continents-create'),
    path('continents/list/', ContinentsListAPIView.as_view(),name='continents-list'),
    # path('continents/<uuid:uuid>/', ContinentsDetailAPIView.as_view()),
    path('continents/update/<uuid:uuid>/', ContinentsUpdateAPIView.as_view(),name='continents-update'),
    path('continents/<uuid:uuid>/delete/', ContinentsDeleteAPIView.as_view(),name='continents-delete'),
# 
    path('country/create/', CountryCreateAPIView.as_view(),name='country-create'),
    path('country/list/', CountryListAPIView.as_view(),name='country-list'),
    path('country/update/<uuid:uuid>/', CountryUpdateAPIView.as_view(),name='country-update'),
    path('country/<uuid:uuid>/delete/', CountryDeleteAPIView.as_view(),name='country-delete'),
    path('countries/by-continent/', CountriesByContinentAPIView.as_view(), name='countries-by-continent'),


    path('state/create/', StateCreateAPIView.as_view(),name='state-create'),
    path('state/list/', StateListAPIView.as_view(),name='state-list'),
    path('state/update/<uuid:uuid>/', StateUpdateAPIView.as_view(),name='state-update'),
    path('state/<uuid:uuid>/delete/', StateDeleteAPIView.as_view(),name='state-delete'),
    path('state/by-country/', StateByCountryAPIView.as_view(), name='state-by-country'),

    
    path('district/create/', DistrictCreateAPIView.as_view(),name='district-create'),
    path('district/list/', DistrictListAPIView.as_view(),name='district-list'),
    path('district/update/<uuid:uuid>/', DistrictUpdateAPIView.as_view(),name='district-update'),
    path('district/<uuid:uuid>/delete/', DistrictDeleteAPIView.as_view(),name='district-delete'),
    path('district/by-state/', DistrictByFilterAPIView.as_view(), name='district-by-state'),


    path('city/create/', CityCreateAPIView.as_view(),name='city-create'),
    path('city/list/', CityListAPIView.as_view(),name='city-list'),
    path('city/update/<uuid:uuid>/', CityUpdateAPIView.as_view(),name='city-update'),
    path('city/<uuid:uuid>/delete/', CityDeleteAPIView.as_view(),name='city-delete'),
    
    path('relation/create/', RelationCreateAPIView.as_view(),name='relation-create'),
    path('relation/list/', RelationListAPIView.as_view(),name='relation-list'),
    path('relation/update/<uuid:uuid>/', RelationUpdateAPIView.as_view(),name='relation-update'),
    path('relation/<uuid:uuid>/delete/', RelationDeleteAPIView.as_view(),name='relation-delete'),

    path('timezones/create/', TimezoneCreateAPIView.as_view(), name='timezone-create'),
    path('timezones/list/', TimezoneListAPIView.as_view(), name='timezone-list'),
    path('timezones/update/<uuid:uuid>/', TimezoneUpdateAPIView.as_view(), name='timezone-update'),
    path('timezones/<uuid:uuid>/delete/', TimezoneDeleteAPIView.as_view(), name='timezone-delete'),

    path('departments/', DepartmentListAPIView.as_view(), name='department-list'),
    path('departments/create/', DepartmentCreateAPIView.as_view(), name='department-create'),
    path('departments/<uuid:uuid>/', DepartmentRetrieveAPIView.as_view(), name='department-detail'),
    path('departments/<uuid:uuid>/update/', DepartmentUpdateAPIView.as_view(), name='department-update'),
    path('departments/<uuid:uuid>/delete/', DepartmentDeleteAPIView.as_view(), name='department-delete'),

    path('employeetype/',EmployeeTypeListAPIView.as_view(), name='employeetype-list'),
    path('employeetype/create/', EmployeeTypeCreateAPIView.as_view(), name='employeetype-create'),
    path('employeetype/<uuid:uuid>/', EmployeeTypeRetrieveAPIView.as_view(), name='employeetype-detail'),
    path('employeetype/<uuid:uuid>/update/', EmployeeTypeUpdateAPIView.as_view(), name='employeetype-update'),
    path('employeetype/<uuid:uuid>/delete/', EmployeeTypeDeleteAPIView.as_view(), name='employeetype-delete'),

    path('company-types/', CompanyTypeListAPIView.as_view(), name='companytype-list'),
    path('company-types/create/', CompanyTypeCreateAPIView.as_view(), name='companytype-create'),
    path('company-types/<uuid:uuid>/', CompanyTypeDetailAPIView.as_view(), name='companytype-detail'),
    path('company-types/<uuid:uuid>/update/', CompanyTypeUpdateAPIView.as_view(), name='companytype-update'),
    path('company-types/<uuid:uuid>/delete/', CompanyTypeDeleteAPIView.as_view(), name='companytype-delete'),

    path('ownership-types/', OwnershipTypeListAPIView.as_view(), name='ownershiptype-list'),
    path('ownership-types/create/', OwnershipTypeCreateAPIView.as_view(), name='ownershiptype-create'),
    path('ownership-types/<uuid:uuid>/', OwnershipTypeDetailAPIView.as_view(), name='ownershiptype-detail'),
    path('ownership-types/<uuid:uuid>/update/', OwnershipTypeUpdateAPIView.as_view(), name='ownershiptype-update'),
    path('ownership-types/<uuid:uuid>/delete/', OwnershipTypeDeleteAPIView.as_view(), name='ownershiptype-delete'),

    path('stakeholder-categories/', StakeholderCategoryListAPIView.as_view(), name='stakeholdercategory-list'),
    path('stakeholder-categories/create/', StakeholderCategoryCreateAPIView.as_view(), name='stakeholdercategory-create'),
    path('stakeholder-categories/<uuid:uuid>/', StakeholderCategoryDetailAPIView.as_view(), name='stakeholdercategory-detail'),
    path('stakeholder-categories/<uuid:uuid>/update/', StakeholderCategoryUpdateAPIView.as_view(), name='stakeholdercategory-update'),
    path('stakeholder-categories/<uuid:uuid>/delete/', StakeholderCategoryDeleteAPIView.as_view(), name='stakeholdercategory-delete'),

    # Stakeholder Type
    path('stakeholder-types/', StakeholderTypeListAPIView.as_view(), name='stakeholdertype-list'),
    path('stakeholder-types/create/', StakeholderTypeCreateAPIView.as_view(), name='stakeholdertype-create'),
    path('stakeholder-types/<uuid:uuid>/', StakeholderTypeDetailAPIView.as_view(), name='stakeholdertype-detail'),
    path('stakeholder-types/<uuid:uuid>/update/', StakeholderTypeUpdateAPIView.as_view(), name='stakeholdertype-update'),
    path('stakeholder-types/<uuid:uuid>/delete/', StakeholderTypeDeleteAPIView.as_view(), name='stakeholdertype-delete'),

    path("accreditation-category/create/", AccreditationCategoryCreateAPIView.as_view(), name='accreditation-list'),
    path("accreditation-category/", AccreditationCategoryListAPIView.as_view(), name='accreditation-create'),
    path("accreditation-category/<uuid:uuid>/", AccreditationCategoryRetrieveAPIView.as_view(), name='accreditation-detail'),
    path("accreditation-category/<uuid:uuid>/update/", AccreditationCategoryUpdateAPIView.as_view(), name='accreditation-update'),
    path("accreditation-category/delete/<uuid:uuid>/", AccreditationCategoryDeleteAPIView.as_view(), name='accreditation-delete'),

    # Accreditation Name
    path("accreditation-name/create/", AccreditationNameCreateAPIView.as_view(), name='stakeholdertype-list'),
    path("accreditation-name/", AccreditationNameListAPIView.as_view(), name='stakeholdertype-list'),
    path("accreditation-name/<uuid:uuid>/", AccreditationNameRetrieveAPIView.as_view(), name='stakeholdertype-detail'),
    path("accreditation-name/<uuid:uuid>/update/", AccreditationNameUpdateAPIView.as_view(), name='stakeholdertype-update'),
    path("accreditation-name/delete/<uuid:uuid>/", AccreditationNameDeleteAPIView.as_view(), name='stakeholdertype-delete'),


    path("BankAccountType/create/", BankAccountTypeCreateAPIView.as_view(), name='BankAccountType-create'),
    path("BankAccountType/", BankAccountTypeListAPIView.as_view(), name='BankAccountType-list'),
    path("BankAccountType/<uuid:uuid>/", BankAccountTypeRetrieveAPIView.as_view(), name='BankAccountType-detail'),
    path("BankAccountType/<uuid:uuid>/update/", BankAccountTypeUpdateAPIView.as_view(), name='BankAccountType-update'),
    path("BankAccountType/delete/<uuid:uuid>/", BankAccountTypeDeleteAPIView.as_view(), name='BankAccountType-delete'),

    path("license-name/create/", LicenseNameCreateAPIView.as_view(),name='licensename-create'),
    path("license-name/", LicenseNameListAPIView.as_view(),name='licensename-list'),
    path("license-name/<uuid:uuid>/", LicenseNameRetrieveAPIView.as_view(),name='licensename-detail'),
    path("license-name/update/<uuid:uuid>/", LicenseNameUpdateAPIView.as_view(),name='licensename-update'),
    path("license-name/delete/<uuid:uuid>/", LicenseNameDeleteAPIView.as_view(),name='licensename-delete'),

    path("LeadSource/create/", LeadSourceCreateAPIView.as_view(), name='LeadSource-create'),
    path("LeadSource/", LeadSourceListAPIView.as_view(), name='LeadSource-list'),
    path("LeadSource/<uuid:uuid>/", LeadSourceRetrieveAPIView.as_view(), name='LeadSource-detail'),
    path("LeadSource/<uuid:uuid>/update/", LeadSourceUpdateAPIView.as_view(), name='LeadSource-update'),
    path("LeadSource/delete/<uuid:uuid>/", LeadSourceDeleteAPIView.as_view(), name='LeadSource-delete'),

    path("InterestLevel/create/", InterestLevelCreateAPIView.as_view(), name='InterestLevel-create'),
    path("InterestLevel/list/", InterestLevelListAPIView.as_view(), name='InterestLevel-list'),
    path("InterestLevel/<uuid:uuid>/", InterestLevelRetrieveAPIView.as_view(), name='InterestLevel-detail'),
    path("InterestLevel/<uuid:uuid>/update/", InterestLevelUpdateAPIView.as_view(), name='InterestLevel-update'),
    path("InterestLevel/delete/<uuid:uuid>/", InterestLevelDeleteAPIView.as_view(), name='InterestLevel-delete'),


    path("Priority/create/", PriorityCreateAPIView.as_view(), name='Priority-create'),
    path("Priority/list/", PriorityListAPIView.as_view(), name='Priority-list'),
    path("Priority/<uuid:uuid>/", PriorityRetrieveAPIView.as_view(), name='Priority-detail'),
    path("Priority/<uuid:uuid>/update/", PriorityUpdateAPIView.as_view(), name='Priority-update'),
    path("Priority/delete/<uuid:uuid>/", PriorityDeleteAPIView.as_view(), name='Priority-delete'),

    path("Tags/create/", TagsCreateAPIView.as_view(), name='Tags-create'),
    path("Tags/list/", TagsListAPIView.as_view(), name='Tags-list'),
    path("Tags/<uuid:uuid>/", TagsRetrieveAPIView.as_view(), name='Tags-detail'),
    path("Tags/<uuid:uuid>/update/", TagsUpdateAPIView.as_view(), name='Tags-update'),
    path("Tags/delete/<uuid:uuid>/", TagsDeleteAPIView.as_view(), name='Tags-delete'),

    path("ActivityType/create/", ActivityTypeCreateAPIView.as_view(), name='ActivityType-create'),
    path("ActivityType/list/", ActivityTypeListAPIView.as_view(), name='ActivityType-list'),
    path("ActivityType/<uuid:uuid>/", ActivityTypeRetrieveAPIView.as_view(), name='ActivityType-detail'),
    path("ActivityType/<uuid:uuid>/update/", ActivityTypeUpdateAPIView.as_view(), name='ActivityType-update'),
    path("ActivityType/delete/<uuid:uuid>/", ActivityTypeDeleteAPIView.as_view(), name='ActivityType-delete'),

    path("LostReason/create/", LostReasonCreateAPIView.as_view(), name='LostReason-create'),
    path("LostReason/list/", LostReasonListAPIView.as_view(), name='LostReason-list'),
    path("LostReason/<uuid:uuid>/", LostReasonRetrieveAPIView.as_view(), name='LostReason-detail'),
    path("LostReason/<uuid:uuid>/update/", LostReasonUpdateAPIView.as_view(), name='LostReason-update'),
    path("LostReason/delete/<uuid:uuid>/", LostReasonDeleteAPIView.as_view(), name='LostReason-delete'),



]

