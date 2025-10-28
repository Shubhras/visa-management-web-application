from django.urls import path
from .views import *
from .test import *
from .visamaster import *

urlpatterns = [

    path("login/", MasterTokenLoginAPIView.as_view(), name="master-login"),
    path('genders/create/', GenderCreateAPIView.as_view()),
    path('genders/', GenderListAPIView.as_view()),
    path('genders/<uuid:uuid>/', GenderDetailAPIView.as_view()),
    path('genders/<uuid:uuid>/update/', GenderUpdateAPIView.as_view()),
    path('genders/delete/', GenderDeleteAPIView.as_view()),

    path('Maritalstatus/create/', MaritalstatusCreateAPIView.as_view(),name='Maritalstatus-create'),
    path('Maritalstatus/list/', MaritalstatusListAPIView.as_view(),name='Maritalstatus-list'),
    path('Maritalstatus/<uuid:uuid>/', MaritalstatusDetailAPIView.as_view(), name='Maritalstatus-detail'),
    path('Maritalstatus/<uuid:uuid>/update/', MaritalstatusUpdateAPIView.as_view(),name='Maritalstatus-update'),

    path('continents/create/', ContinentCreateAPIView.as_view(),name='continents-create'),
    path('continents/', ContinentListAPIView.as_view(),name='continents-list'),
    path('continents/<uuid:uuid>/', ContinentRetrieveAPIView.as_view()),
    path('continents/<uuid:uuid>/update/', ContinentUpdateAPIView.as_view(),name='continents-update'),
    path('continents/delete/', ContinentDeleteAPIView.as_view(),name='continents-delete'),
    path('continents/export/', ContinentExportAPIView.as_view(),name='continents-export'),
    path('continents/import/', ContinentImportAPIView.as_view(),name='continents-import'),
    
# 
    path('country/create/', CountryCreateAPIView.as_view(),name='country-create'),
    path('country/', CountryListAPIView.as_view(),name='country-list'),
    path('country/<uuid:uuid>/', StateRetrieveAPIView.as_view(), name='state-detail'),
    path('country/<uuid:uuid>/update/', CountryUpdateAPIView.as_view(),name='country-update'),
    path('country/delete/', CountryDeleteAPIView.as_view(),name='country-delete'),
    path('countries/export/', CountryExportAPIView.as_view(), name='country-export'),
    path('countries/import/', CountryImportAPIView.as_view(), name='country-import'),
    path('countries/by-continent/', CountriesByContinentAPIView.as_view(), name='countries-by-continent'),

    path('state/create/', StateCreateAPIView.as_view(),name='state-create'),
    path('state/', StateListAPIView.as_view(),name='state-list'),
    path('state/<uuid:uuid>/update/', StateUpdateAPIView.as_view(),name='state-update'),
    path('states/<uuid:uuid>/', StateRetrieveAPIView.as_view(), name='state-detail'),
    path('state/delete/', StateDeleteAPIView.as_view(),name='state-delete'),
    path('state/export/', StateExportAPIView.as_view(), name='state-export'),
    path('state/import/', StateImportAPIView.as_view(), name='state-import'),
    path('state/by-country/', StateByCountryAPIView.as_view(), name='state-by-country'),

    
    path('district/create/', DistrictCreateAPIView.as_view(),name='district-create'),
    path('district/', DistrictListAPIView.as_view(),name='district-list'),
    path('districts/<uuid:uuid>/', DistrictRetrieveAPIView.as_view(), name='district-detail'),
    path('district/<uuid:uuid>/update/', DistrictUpdateAPIView.as_view(),name='district-update'),
    path('district/delete/', DistrictDeleteAPIView.as_view(),name='district-delete'),
    path('district/export/', DistrictExportAPIView.as_view(), name='district-export'),
    path('district/import/', DistrictImportAPIView.as_view(), name='district   -import'),
    path('district/by-state/', DistrictByFilterAPIView.as_view(), name='district-by-state'),


    path('city/', CityListAPIView.as_view(), name='city-list'),
    path('city/create/', CityCreateAPIView.as_view(), name='city-create'),
    path('city/<uuid:uuid>/', CityRetrieveAPIView.as_view(), name='city-detail'),
    path('city/update/<uuid:uuid>/', CityUpdateAPIView.as_view(), name='city-update'),
    path('city/delete/', CityDeleteAPIView.as_view(), name='city-delete'),
    path('city/export/', CityExportAPIView.as_view(), name='city-export'),
    path('city/import/', CityImportAPIView.as_view(), name='city-import'),




    path('relations/list/', RelationListAPIView.as_view(), name='relation-list'),
    path('relations/create/', RelationCreateAPIView.as_view(), name='relation-create'),
    path('relations/<uuid:uuid>/', RelationRetrieveAPIView.as_view(), name='relation-detail'),
    path('relations/update/<uuid:uuid>/', RelationUpdateAPIView.as_view(), name='relation-update'),
    path('relations/delete/', RelationDeleteAPIView.as_view(), name='relation-delete'),
    path('relations/export/', RelationExportAPIView.as_view(), name='relation-export'),
    path('relations/import/', RelationImportAPIView.as_view(), name='relation-import'),

    path('timezones/create/', TimezoneCreateAPIView.as_view(), name='timezone-create'),
    path('timezones/list/', TimezoneListAPIView.as_view(), name='timezone-list'),
    path('timezones/update/<uuid:uuid>/', TimezoneUpdateAPIView.as_view(), name='timezone-update'),
    path('timezones/<uuid:uuid>/delete/', TimezoneDeleteAPIView.as_view(), name='timezone-delete'),

    path('departments/', DepartmentListAPIView.as_view(), name='department-list'),
    path('departments/create/', DepartmentCreateAPIView.as_view(), name='department-create'),
    path('departments/<uuid:uuid>/', DepartmentRetrieveAPIView.as_view(), name='department-detail'),
    path('departments/<uuid:uuid>/update/', DepartmentUpdateAPIView.as_view(), name='department-update'),
    path('departments/delete/', DepartmentDeleteAPIView.as_view(), name='department-delete'),
    path('departments/export/', DepartmentExportAPIView.as_view(), name='department-export'),
    path('departments/import/', DepartmentImportAPIView.as_view(), name='department-import'),

    path('employeetype/',EmployeeTypeListAPIView.as_view(), name='employeetype-list'),
    path('employeetype/create/', EmployeeTypeCreateAPIView.as_view(), name='employeetype-create'),
    path('employeetype/<uuid:uuid>/', EmployeeTypeRetrieveAPIView.as_view(), name='employeetype-detail'),
    path('employeetype/<uuid:uuid>/update/', EmployeeTypeUpdateAPIView.as_view(), name='employeetype-update'),
    path('employeetype/delete/', EmployeeTypeDeleteAPIView.as_view(), name='employeetype-delete'),
    path('employeetype/export/', EmployeeTypeExportAPIView.as_view(), name='employeetype-export'),
    path('employeetype/import/', EmployeeTypeImportAPIView.as_view(), name='employeetype-import'),


    path('company-types/', CompanyTypeListAPIView.as_view(), name='companytype-list'),
    path('company-types/create/', CompanyTypeCreateAPIView.as_view(), name='companytype-create'),
    path('company-types/<uuid:uuid>/', CompanyTypeDetailAPIView.as_view(), name='companytype-detail'),
    path('company-types/<uuid:uuid>/update/', CompanyTypeUpdateAPIView.as_view(), name='companytype-update'),
    path('company-types/delete/', CompanyTypeDeleteAPIView.as_view(), name='companytype-delete'),
    path('company-types/export/',  CompanyTypeExportAPIView.as_view(), name='companytype-export'),
    path('company-types/import/',  CompanyTypeImportAPIView.as_view(), name='companytype-import'),


    path('ownership-types/', OwnershipTypeListAPIView.as_view(), name='ownershiptype-list'),
    path('ownership-types/create/', OwnershipTypeCreateAPIView.as_view(), name='ownershiptype-create'),
    path('ownership-types/<uuid:uuid>/', OwnershipTypeDetailAPIView.as_view(), name='ownershiptype-detail'),
    path('ownership-types/<uuid:uuid>/update/', OwnershipTypeUpdateAPIView.as_view(), name='ownershiptype-update'),
    path('ownership-types/delete/', OwnershipTypeDeleteAPIView.as_view(), name='ownershiptype-delete'),
    path('Ownership-types/export/',  OwnershipTypeExportAPIView.as_view(), name='ownershiptype-export'),
    path('Ownership-types/import/',  OwnershipTypeImportAPIView.as_view(), name='ownershiptype-import'),



    path('stakeholder-categories/', StakeholderCategoryListAPIView.as_view(), name='stakeholdercategory-list'),
    path('stakeholder-categories/create/', StakeholderCategoryCreateAPIView.as_view(), name='stakeholdercategory-create'),
    path('stakeholder-categories/<uuid:uuid>/', StakeholderCategoryDetailAPIView.as_view(), name='stakeholdercategory-detail'),
    path('stakeholder-categories/<uuid:uuid>/update/', StakeholderCategoryUpdateAPIView.as_view(), name='stakeholdercategory-update'),
    path('stakeholder-categories/delete/', StakeholderCategoryDeleteAPIView.as_view(), name='stakeholdercategory-delete'),
    path('stakeholder-categories/export/',  StakeholderCategoryExportAPIView.as_view(), name='stakeholdercategory-export'),
    path('stakeholder-categories/import/',  StakeholderCategoryImportAPIView.as_view(), name='stakeholdercategory-import'),

    # Stakeholder Type
    path('stakeholder-types/', StakeholderTypeListAPIView.as_view(), name='stakeholdertype-list'),
    path('stakeholder-types/create/', StakeholderTypeCreateAPIView.as_view(), name='stakeholdertype-create'),
    path('stakeholder-types/<uuid:uuid>/', StakeholderTypeDetailAPIView.as_view(), name='stakeholdertype-detail'),
    path('stakeholder-types/<uuid:uuid>/update/', StakeholderTypeUpdateAPIView.as_view(), name='stakeholdertype-update'),
    path('stakeholder-types/delete/', StakeholderTypeDeleteAPIView.as_view(), name='stakeholdertype-delete'),

    path("accreditation-category/create/", AccreditationCategoryCreateAPIView.as_view(), name='accreditation-list'),
    path("accreditation-category/", AccreditationCategoryListAPIView.as_view(), name='accreditation-create'),
    path("accreditation-category/<uuid:uuid>/", AccreditationCategoryRetrieveAPIView.as_view(), name='accreditation-detail'),
    path("accreditation-category/<uuid:uuid>/update/", AccreditationCategoryUpdateAPIView.as_view(), name='accreditation-update'),
    path("accreditation-category/delete/", AccreditationCategoryDeleteAPIView.as_view(), name='accreditation-delete'),
    path('accreditation-category/export/',  AccreditationCategoryExportAPIView.as_view(), name=' accreditation-export'),
    path('accreditation-category/import/',  AccreditationCategoryImportAPIView.as_view(), name='accreditation-import'),

    # Accreditation Name
    path("accreditation-name/create/", AccreditationNameCreateAPIView.as_view(), name='stakeholdertype-list'),
    path("accreditation-name/", AccreditationNameListAPIView.as_view(), name='stakeholdertype-list'),
    path("accreditation-name/<uuid:uuid>/", AccreditationNameRetrieveAPIView.as_view(), name='stakeholdertype-detail'),
    path("accreditation-name/<uuid:uuid>/update/", AccreditationNameUpdateAPIView.as_view(), name='stakeholdertype-update'),
    path("accreditation-name/delete/", AccreditationNameDeleteAPIView.as_view(), name='stakeholdertype-delete'),


    path("BankAccountType/create/", BankAccountTypeCreateAPIView.as_view(), name='BankAccountType-create'),
    path("BankAccountType/", BankAccountTypeListAPIView.as_view(), name='BankAccountType-list'),
    path("BankAccountType/<uuid:uuid>/", BankAccountTypeRetrieveAPIView.as_view(), name='BankAccountType-detail'),
    path("BankAccountType/<uuid:uuid>/update/", BankAccountTypeUpdateAPIView.as_view(), name='BankAccountType-update'),
    path("BankAccountType/delete/", BankAccountTypeDeleteAPIView.as_view(), name='BankAccountType-delete'),
    path('BankAccountType/export/',   BankAccountTypeExportAPIView.as_view(), name=' BankAccountType-export'),
    path('BankAccountType/import/',   BankAccountTypeImportAPIView.as_view(), name=' BankAccountType-import'),


    path("license-name/create/", LicenseNameCreateAPIView.as_view(),name='licensename-create'),
    path("license-name/", LicenseNameListAPIView.as_view(),name='licensename-list'),
    path("license-name/<uuid:uuid>/", LicenseNameRetrieveAPIView.as_view(),name='licensename-detail'),
    path("license-name/<uuid:uuid>/update/", LicenseNameUpdateAPIView.as_view(),name='licensename-update'),
    path("license-name/delete/", LicenseNameDeleteAPIView.as_view(),name='licensename-delete'),
   
    path("LeadSource/create/", LeadSourceCreateAPIView.as_view(), name='LeadSource-create'),
    path("LeadSource/", LeadSourceListAPIView.as_view(), name='LeadSource-list'),
    path("LeadSource/<uuid:uuid>/", LeadSourceRetrieveAPIView.as_view(), name='LeadSource-detail'),
    path("LeadSource/<uuid:uuid>/update/", LeadSourceUpdateAPIView.as_view(), name='LeadSource-update'),
    path("LeadSource/delete/", LeadSourceDeleteAPIView.as_view(), name='LeadSource-delete'),
    path('LeadSource/export/',   LeadSourceExportAPIView.as_view(), name=' LeadSource-export'),
    path('LeadSource/import/',   LeadSourceImportAPIView.as_view(), name=' LeadSource-import'),

    path("InterestLevel/create/", InterestLevelCreateAPIView.as_view(), name='InterestLevel-create'),
    path("InterestLevel/", InterestLevelListAPIView.as_view(), name='InterestLevel-list'),
    path("InterestLevel/<uuid:uuid>/", InterestLevelRetrieveAPIView.as_view(), name='InterestLevel-detail'),
    path("InterestLevel/<uuid:uuid>/update/", InterestLevelUpdateAPIView.as_view(), name='InterestLevel-update'),
    path("InterestLevel/delete/", InterestLevelDeleteAPIView.as_view(), name='InterestLevel-delete'),
    path('InterestLevel/export/',   InterestLevelExportAPIView.as_view(), name=' InterestLevel-export'),
    path('InterestLevel/import/',  InterestLevelImportAPIView.as_view(), name=' InterestLevel-import'),


    path("Priority/create/", PriorityCreateAPIView.as_view(), name='Priority-create'),
    path("Priority/", PriorityListAPIView.as_view(), name='Priority-list'),
    path("Priority/<uuid:uuid>/", PriorityRetrieveAPIView.as_view(), name='Priority-detail'),
    path("Priority/<uuid:uuid>/update/", PriorityUpdateAPIView.as_view(), name='Priority-update'),
    path("Priority/delete/", PriorityDeleteAPIView.as_view(), name='Priority-delete'),
    path('Priority/export/',   PriorityExportAPIView.as_view(), name=' Priority-export'),
    path('Priority/import/',  PriorityImportAPIView.as_view(), name=' InterPriorityestLevel-import'),

    path("Tags/create/", TagsCreateAPIView.as_view(), name='Tags-create'),
    path("Tags/", TagsListAPIView.as_view(), name='Tags-list'),
    path("Tags/<uuid:uuid>/", TagsRetrieveAPIView.as_view(), name='Tags-detail'),
    path("Tags/<uuid:uuid>/update/", TagsUpdateAPIView.as_view(), name='Tags-update'),
    path("Tags/delete/", TagsDeleteAPIView.as_view(), name='Tags-delete'),
    path('Tags/export/',  TagsExportAPIView.as_view(), name=' Tags-export'),
    path('Tags/import/',  TagsImportAPIView.as_view(), name=' Tags-import'),


    path("ActivityType/create/", ActivityTypeCreateAPIView.as_view(), name='ActivityType-create'),
    path("ActivityType/", ActivityTypeListAPIView.as_view(), name='ActivityType-list'),
    path("ActivityType/<uuid:uuid>/", ActivityTypeRetrieveAPIView.as_view(), name='ActivityType-detail'),
    path("ActivityType/<uuid:uuid>/update/", ActivityTypeUpdateAPIView.as_view(), name='ActivityType-update'),
    path("ActivityType/delete/", ActivityTypeDeleteAPIView.as_view(), name='ActivityType-delete'),
    path('ActivityType/export/', ActivityTypeExportAPIView.as_view(), name=' ActivityType-export'),
    path('ActivityType/import/',  ActivityTypeImportAPIView.as_view(), name=' ActivityType-import'),


    path("LostReason/create/", LostReasonCreateAPIView.as_view(), name='LostReason-create'),
    path("LostReason/", LostReasonListAPIView.as_view(), name='LostReason-list'),
    path("LostReason/<uuid:uuid>/", LostReasonRetrieveAPIView.as_view(), name='LostReason-detail'),
    path("LostReason/<uuid:uuid>/update/", LostReasonUpdateAPIView.as_view(), name='LostReason-update'),
    path("LostReason/delete/", LostReasonDeleteAPIView.as_view(), name='LostReason-delete'),
    path('LostReason/export/', LostReasonExportAPIView.as_view(), name=' LostReason-export'),
    path('LostReason/import/',  LostReasonImportAPIView.as_view(), name=' LostReason-import'),

    path("lostreason/create/", LostReasonB2BCreateAPIView.as_view(), name='LostReason-create'),
    path("lostreason/", LostReasonB2BListAPIView.as_view(), name='LostReason-list'),
    path("lostreason/<uuid:uuid>/", LostReasonB2BRetrieveAPIView.as_view(), name='LostReason-detail'),
    path("lostreason/<uuid:uuid>/update/", LostReasonB2BUpdateAPIView.as_view(), name='LostReason-update'),
    path("lostreason/delete/", LostReasonB2BDeleteAPIView.as_view(), name='LostReason-delete'),
    path('lostreason/export/', LostReasonB2BExportAPIView.as_view(), name=' LostReason-export'),
    path('lostreason/import/',  LostReasonB2BImportAPIView.as_view(), name=' LostReason-import'),


    path('education-level-codes/create/', EducationLevelCodeCreateAPIView.as_view(), name='educationlevelcode-create'),
    path('education-level-codes/<uuid:uuid>/', EducationLevelCodeRetrieveAPIView.as_view(), name='educationlevelcode-retrieve'),
    path('education-level-codes/update/<uuid:uuid>/', EducationLevelCodeUpdateAPIView.as_view(), name='educationlevelcode-update'),
    path('education-level-codes/delete/', EducationLevelCodeDeleteAPIView.as_view(), name='educationlevelcode-delete'),
    path('education-level-codes/export/', EducationLevelCodeExportAPIView.as_view(), name='educationlevelcode-export'),
    path('education-level-codes/import/', EducationLevelCodeImportAPIView.as_view(), name='educationlevelcode-import'),
    
    path('education-level/create/', EducationLevelCreateAPIView.as_view(), name='educationlevel-create'),
    path('education-level/<uuid:uuid>/', EducationLevelRetrieveAPIView.as_view(), name='educationlevel-retrieve'),
    path('education-level/update/<uuid:uuid>/', EducationLevelUpdateAPIView.as_view(), name='educationlevel-update'),
    path('education-level/delete/', EducationLevelDeleteAPIView.as_view(), name='educationlevel-delete'),
    path('education-level/export/', EducationLevelExportAPIView.as_view(), name='educationlevel-export'),
    path('education-level/import/', EducationLevelImportAPIView.as_view(), name='educationlevel-import'),

    path('education-duration/create/', EducationDurationCreateAPIView.as_view(), name='educationduration-create'),
    path('education-duration/<uuid:uuid>/', EducationDurationRetrieveAPIView.as_view(), name='educationduration-retrieve'),
    path('education-duration/update/<uuid:uuid>/', EducationDurationUpdateAPIView.as_view(), name='educationduration-update'),
    path('education-duration/delete/', EducationDurationDeleteAPIView.as_view(), name='educationduration-delete'),
    path('education-duration/export/', EducationDurationExportAPIView.as_view(), name='educationduration-export'),
    path('education-duration/import/', EducationDurationImportAPIView.as_view(), name='educationduration-import'),

    path('studymainarea/create/', StudymainareaCreateAPIView.as_view(), name='studymainarea-create'),
    path('studymainarea/<uuid:uuid>/', StudymainareaRetrieveAPIView.as_view(), name='studymainarea-retrieve'),
    path('studymainarea/update/<uuid:uuid>/', StudymainareaUpdateAPIView.as_view(), name='studymainarea-update'),
    path('studymainarea/delete/', StudymainareaDeleteAPIView.as_view(), name='studymainarea-delete'),
    path('studymainarea/export/', StudymainareaExportAPIView.as_view(), name='studymainarea-export'),
    path('studymainarea/import/', StudymainareaImportAPIView.as_view(), name='studymainarea-import'),

    path('studymajorarea/create/', StudymajorareaCreateAPIView.as_view(), name='studymajorarea-create'),
    path('studymajorarea/<uuid:uuid>/', StudymajorareaRetrieveAPIView.as_view(), name='studymajorarea-retrieve'),
    path('studymajorarea/update/<uuid:uuid>/', StudymajorareaUpdateAPIView.as_view(), name='studymajorarea-update'),
    path('studymajorarea/delete/', StudymajorareaDeleteAPIView.as_view(), name='studymajorarea-delete'),
    path('studymajorarea/export/', StudymajorareaExportAPIView.as_view(), name='studymajorarea-export'),
    path('studymajorarea/import/', StudymajorareaImportAPIView.as_view(), name='studymajorarea-import'),

    path('studyspecialisation/create/', StudySpecialisationCreateAPIView.as_view(), name='studyspecialisation-create'),
    path('studyspecialisation/<uuid:uuid>/', StudySpecialisationRetrieveAPIView.as_view(), name='studyspecialisation-retrieve'),
    path('studyspecialisation/update/<uuid:uuid>/', StudySpecialisationUpdateAPIView.as_view(), name='studyspecialisation-update'),
    path('studyspecialisation/delete/', StudySpecialisationDeleteAPIView.as_view(), name='studyspecialisation-delete'),
    path('studyspecialisation/export/', StudySpecialisationExportAPIView.as_view(), name='studyspecialisation-export'),
    path('studyspecialisation/import/', StudySpecialisationImportAPIView.as_view(), name='studyspecialisation-import'),

    path('academicresulttype/create/', AcademicResultTypeCreateAPIView.as_view(), name='academicresulttype-create'),
    path('academicresulttype/<uuid:uuid>/', AcademicResultTypeRetrieveAPIView.as_view(), name='academicresulttype-retrieve'),
    path('academicresulttype/update/<uuid:uuid>/', AcademicResultTypeUpdateAPIView.as_view(), name='academicresulttype-update'),
    path('academicresulttype/delete/', AcademicResultTypeDeleteAPIView.as_view(), name='academicresulttype-delete'),
    path('academicresulttype/export/', AcademicResultTypeExportAPIView.as_view(), name='academicresulttype-export'),
    path('academicresulttype/import/', AcademicResultTypeImportAPIView.as_view(), name='academicresulttype-import'),

    path('academicresult/create/', AcademicResultCreateAPIView.as_view(), name='academicresult-create'),
    path('academicresult/<uuid:uuid>/', AcademicResultRetrieveAPIView.as_view(), name='academicresult-retrieve'),
    path('academicresult/update/<uuid:uuid>/', AcademicResultUpdateAPIView.as_view(), name='academicresult-update'),
    path('academicresult/delete/', AcademicResultDeleteAPIView.as_view(), name='academicresult-delete'),
    path('academicresult/export/', AcademicResultExportAPIView.as_view(), name='academicresult-export'),
    path('academicresult/import/', AcademicResultImportAPIView.as_view(), name='academicresult-import'),    

    path('educationtype/create/', EducationTypeCreateAPIView.as_view(), name='educationtype-create'),
    path('educationtype/<uuid:uuid>/', EducationTypeRetrieveAPIView.as_view(), name='educationtype-retrieve'),
    path('educationtype/update/<uuid:uuid>/', EducationTypeUpdateAPIView.as_view(), name='educationtype-update'),
    path('educationtype/delete/', EducationTypeDeleteAPIView.as_view(), name='educationtype-delete'),

    path('mediumeducation/create/', MediumofEducationCreateAPIView.as_view(), name='mediumeducation-create'),
    path('mediumeducation/<uuid:uuid>/', MediumofEducationRetrieveAPIView.as_view(), name='mediumeducation-retrieve'),
    path('mediumeducation/update/<uuid:uuid>/', MediumofEducationUpdateAPIView.as_view(), name='mediumeducation-update'),
    path('mediumeducation/delete/', MediumofEducationDeleteAPIView.as_view(), name='mediumeducation-delete'),


    path('language/create/', LanguageCreateAPIView.as_view(), name='language-create'),
    path('language/<uuid:uuid>/', LanguageRetrieveAPIView.as_view(), name='language-retrieve'),
    path('language/update/<uuid:uuid>/', LanguageUpdateAPIView.as_view(), name='language-update'),
    path('language/delete/', LanguageDeleteAPIView.as_view(), name='language-delete'),
    path('language/list/', LanguageListAPIView.as_view(), name='language-list'),
    path('language/export/', LanguageExportAPIView.as_view(), name='language-export'),
    path('language/import/', LanguageImportAPIView.as_view(), name='language-import'),


    # ---------------- LanguageTest ---------------- #
    path('language-tests/', LanguageTestListAPIView.as_view(), name='language-test-list'),
    path('language-tests/create/', LanguageTestCreateAPIView.as_view(), name='language-test-create'),
    path('language-tests/<uuid:uuid>/', LanguageTestRetrieveAPIView.as_view(), name='language-test-retrieve'),
    path('language-tests/<uuid:uuid>/update/', LanguageTestUpdateAPIView.as_view(), name='language-test-update'),
    path('language-tests/delete/', LanguageTestDeleteAPIView.as_view(), name='language-test-delete'),
    path('language-tests/export/', LanguageTestExportAPIView.as_view(), name='language-test-export'),
    path('language-tests/import/', LanguageTestImportAPIView.as_view(), name='language-test-import'),

    # ------------- LanguagetestmoduleName ------------- #
    path('languagetest-modules/', LanguagetestmoduleNameListAPIView.as_view(), name='languagetest-module-list'),
    path('languagetest-modules/create/', LanguagetestmoduleNameCreateAPIView.as_view(), name='languagetest-module-create'),
    path('languagetest-modules/<uuid:uuid>/', LanguagetestmoduleNameRetrieveAPIView.as_view(), name='languagetest-module-retrieve'),
    path('languagetest-modules/<uuid:uuid>/update/', LanguagetestmoduleNameUpdateAPIView.as_view(), name='languagetest-module-update'),
    path('languagetest-modules/delete/', LanguagetestmoduleNameDeleteAPIView.as_view(), name='languagetest-module-delete'),
    path('languagetest-modules/export/', LanguagetestmoduleNameExportAPIView.as_view(), name='languagetest-module-export'),
    path('languagetest-modules/import/', LanguagetestmoduleNameImportAPIView.as_view(), name='languagetest-module-import'),

    # ---------------- CLBLevel ---------------- #
    path('clb-levels/', CLBLevelListAPIView.as_view(), name='clb-level-list'),
    path('clb-levels/create/', CLBLevelCreateAPIView.as_view(), name='clb-level-create'),
    path('clb-levels/<uuid:uuid>/', CLBLevelRetrieveAPIView.as_view(), name='clb-level-retrieve'),
    path('clb-levels/<uuid:uuid>/update/', CLBLevelUpdateAPIView.as_view(), name='clb-level-update'),
    path('clb-levels/delete/', CLBLevelDeleteAPIView.as_view(), name='clb-level-delete'),
    path('clb-levels/export/', CLBLevelExportAPIView.as_view(), name='clb-level-export'),
    path('clb-levels/import/', CLBLevelImportAPIView.as_view(), name='clb-level-import'),

    # --------- StudyLanguageBanchmark --------- #
    path('study-language-banchmarks/', StudyLanguageBanchmarkListAPIView.as_view(), name='study-language-banchmark-list'),
    path('study-language-banchmarks/create/', StudyLanguageBanchmarkCreateAPIView.as_view(), name='study-language-banchmark-create'),
    path('study-language-banchmarks/<uuid:uuid>/', StudyLanguageBanchmarkRetrieveAPIView.as_view(), name='study-language-banchmark-retrieve'),
    path('study-language-banchmarks/<uuid:uuid>/update/', StudyLanguageBanchmarkUpdateAPIView.as_view(), name='study-language-banchmark-update'),
    path('study-language-banchmarks/delete/', StudyLanguageBanchmarkDeleteAPIView.as_view(), name='study-language-banchmark-delete'),
    path('study-language-banchmarks/export/', StudyLanguageBanchmarkExportAPIView.as_view(), name='study-language-banchmark-export'),
    path('study-language-banchmarks/import/', StudyLanguageBanchmarkImportAPIView.as_view(), name='study-language-banchmark-import'),

    # --------- EntranceTestName --------- #
    path('entrance-tests/', EntranceTestNameListAPIView.as_view(), name='entrance-test-list'),
    path('entrance-tests/create/', EntranceTestNameCreateAPIView.as_view(), name='entrance-test-create'),
    path('entrance-tests/<uuid:uuid>/', EntranceTestNameRetrieveAPIView.as_view(), name='entrance-test-retrieve'),
    path('entrance-tests/<uuid:uuid>/update/', EntranceTestNameUpdateAPIView.as_view(), name='entrance-test-update'),
    path('entrance-tests/delete/', EntranceTestNameDeleteAPIView.as_view(), name='entrance-test-delete'),
    path('entrance-tests/export/', EntranceTestNameExportAPIView.as_view(), name='entrance-test-export'),
    path('entrance-tests/import/', EntranceTestNameImportAPIView.as_view(), name='entrance-test-import'),

    path('entrancetestresult/list/', EntranceTestResultListAPIView.as_view(), name='entrancetestresult-list'),
    path('entrancetestresult/create/', EntranceTestResultCreateAPIView.as_view(), name='entrancetestresult-create'),
    path('entrancetestresult/<uuid:uuid>/', EntranceTestResultRetrieveAPIView.as_view(), name='entrancetestresult-retrieve'),
    path('entrancetestresult/<uuid:uuid>/update/', EntranceTestResultUpdateAPIView.as_view(), name='entrancetestresult-update'),
    path('entrancetestresult/delete/', EntranceTestResultDeleteAPIView.as_view(), name='entrancetestresult-delete'),
    path('entrancetestresult/export/', EntranceTestResultExportAPIView.as_view(), name='entrancetestresult-export'),
    path('entrancetestresult/import/', EntranceTestResultImportAPIView.as_view(), name='entrancetestresult-import'),


    path('representingcountry/list/', RepresentingCountryListAPIView.as_view(), name='representingcountry-list'),
    path('representingcountry/create/', RepresentingCountryCreateAPIView.as_view(), name='representingcountry-create'),
    path('representingcountry/<uuid:uuid>/', RepresentingCountryRetrieveAPIView.as_view(), name='representingcountry-retrieve'),
    path('representingcountry/<uuid:uuid>/update/', RepresentingCountryUpdateAPIView.as_view(), name='representingcountry-update'),
    path('representingcountry/delete/', RepresentingCountryDeleteAPIView.as_view(), name='representingcountry-delete'),
    path('representingcountry/export/', RepresentingCountryExportAPIView.as_view(), name='representingcountry-export'),
    path('representingcountry/import/', RepresentingCountryImportAPIView.as_view(), name='representingcountry-import'),

    path('visamain/list/', VisaMainListAPIView.as_view(), name='visamain-list'),
    path('visamain/create/', VisaMainCreateAPIView.as_view(), name='visamain-create'),
    path('visamain/<uuid:uuid>/', VisaMainRetrieveAPIView.as_view(), name='visamain-retrieve'),
    path('visamain/<uuid:uuid>/update/', VisaMainUpdateAPIView.as_view(), name='visamain-update'),
    path('visamain/delete/', VisaMainDeleteAPIView.as_view(), name='visamain-delete'),
    path('visamain/export/', VisaMainExportAPIView.as_view(), name='visamain-export'),
    path('visamain/import/', VisaMainImportAPIView.as_view(), name='visamain-import'),
    
    path('visamajor/', VisaMajorListAPIView.as_view(), name='visamajor-list'),
    path('visamajor/create/', VisaMajorCreateAPIView.as_view(), name='visamajor-create'),
    path('visamajor/<uuid:uuid>/', VisaMajorRetrieveAPIView.as_view(), name='visamajor-retrieve'),
    path('visamajor/<uuid:uuid>/update/', VisaMajorUpdateAPIView.as_view(), name='visamajor-update'),
    path('visamajor/delete/', VisaMajorDeleteAPIView.as_view(), name='visamajor-delete'),
    path('visamajor/export/', VisaMajorExportAPIView.as_view(), name='visamajor-export'),
    path('visamajor/import/', VisaMajorImportAPIView.as_view(), name='visamajor-import'),

    path('visaname/', VisaNameListAPIView.as_view(), name='visaname-list'),
    path('visaname/create/', VisaNameCreateAPIView.as_view(), name='visaname-create'),
    path('visaname/<uuid:uuid>/', VisaNameRetrieveAPIView.as_view(), name='visaname-retrieve'),
    path('visaname/<uuid:uuid>/update/', VisaNameUpdateAPIView.as_view(), name='visaname-update'),
    path('visaname/delete/', VisaNameDeleteAPIView.as_view(), name='visaname-delete'),
    path('visaname/export/', VisaNameExportAPIView.as_view(), name='visaname-export'),
    path('visaname/import/', VisaNameImportAPIView.as_view(), name='visaname-import'),

    path('applicanttype/', ApplicantTypeListAPIView.as_view(), name='applicanttype-list'),
    path('applicanttype/create/', ApplicantTypeCreateAPIView.as_view(), name='applicanttype-create'),
    path('applicanttype/<uuid:uuid>/', ApplicantTypeRetrieveAPIView.as_view(), name='applicanttype-retrieve'),
    path('applicanttype/<uuid:uuid>/update/', ApplicantTypeUpdateAPIView.as_view(), name='applicanttype-update'),
    path('applicanttype/delete/', ApplicantTypeDeleteAPIView.as_view(), name='applicanttype-delete'),
    path('applicanttype/export/', ApplicantTypeExportAPIView.as_view(), name='applicanttype-export'),
    path('applicanttype/import/', ApplicantTypeImportAPIView.as_view(), name='applicanttype-import'),


]


