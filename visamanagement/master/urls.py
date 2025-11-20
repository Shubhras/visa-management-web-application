from django.urls import path
from .views import *
from .test import *
from .visamaster import *
from .process import*
from .visacondition import *
from .institutemasters import *
from .occupation import  *
from .educationmaster import *
from .process import  *
from .studyfactor  import *

urlpatterns = [

    path("login/", MasterTokenLoginAPIView.as_view(), name="master-login"),

    path('genders/create/', GenderCreateAPIView.as_view(),name='genders-create'),
    path('genders/', GenderListAPIView.as_view(),name='genders-list'),
    path('genders/<uuid:uuid>/', GenderDetailAPIView.as_view(),name='genders-detail'),
    path('genders/<uuid:uuid>/update/', GenderUpdateAPIView.as_view(),name='genders-update'),
    path('genders/delete/', GenderDeleteAPIView.as_view(),name='genders-export'),
    path('genders/export/', GenderExportAPIView.as_view(), name='genders-export'),
    path('genders/import/', GenderImportAPIView.as_view(), name='genders-import'),

    path('maritalstatus/', MaritalstatusListAPIView.as_view(),name='Maritalstatus-list'),
    path('maritalstatus/delete/', MaritalstatusDeleteAPIView.as_view(),name='Maritalstatus-delete'),
    path('maritalstatus/create/', MaritalstatusCreateAPIView.as_view(),name='Maritalstatus-create'),
    path('maritalstatus/list/', MaritalstatusListAPIView.as_view(),name='Maritalstatus-list'),
    path('maritalstatus/<uuid:uuid>/', MaritalstatusDetailAPIView.as_view(), name='Maritalstatus-detail'),
    path('maritalstatus/<uuid:uuid>/update/', MaritalstatusUpdateAPIView.as_view(),name='Maritalstatus-update'),
    path('maritalstatus/export/', MaritalstatusExportAPIView.as_view(), name='Maritalstatus-export'),
    path('maritalstatus/import/', MaritalstatusImportAPIView.as_view(), name='Maritalstatus-import'),

    path('continents/create/', ContinentCreateAPIView.as_view(),name='continents-create'),
    path('continents/', ContinentListAPIView.as_view(),name='continents-list'),
    path('continents/<uuid:uuid>/', ContinentRetrieveAPIView.as_view()),
    path('continents/<uuid:uuid>/update/', ContinentUpdateAPIView.as_view(),name='continents-update'),
    path('continents/delete/', ContinentDeleteAPIView.as_view(),name='continents-delete'),
    path('continents/export/', ContinentExportAPIView.as_view(),name='continents-export'),
    path('continents/import/', ContinentImportAPIView.as_view(),name='continents-import'),
    

    path('country/create/', CountryCreateAPIView.as_view(),name='country-create'),
    path('country/', CountryListAPIView.as_view(),name='country-list'),
    path('country/<uuid:uuid>/', StateRetrieveAPIView.as_view(), name='state-detail'),
    path('country/<uuid:uuid>/update/', CountryUpdateAPIView.as_view(),name='country-update'),
    path('country/delete/', CountryDeleteAPIView.as_view(),name='country-delete'),
    path('country/export/', CountryExportAPIView.as_view(), name='country-export'),
    path('country/import/', CountryImportAPIView.as_view(), name='country-import'),
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
    path('city/<uuid:uuid>/update/', CityUpdateAPIView.as_view(), name='city-update'),
    path('city/delete/', CityDeleteAPIView.as_view(), name='city-delete'),
    path('city/export/', CityExportAPIView.as_view(), name='city-export'),
    path('city/import/', CityImportAPIView.as_view(), name='city-import'),




    path('relations/', RelationListAPIView.as_view(), name='relation-list'),
    path('relations/create/', RelationCreateAPIView.as_view(), name='relation-create'),
    path('relations/<uuid:uuid>/', RelationRetrieveAPIView.as_view(), name='relation-detail'),
    path('relations/<uuid:uuid>/update/', RelationUpdateAPIView.as_view(), name='relation-update'),
    path('relations/delete/', RelationDeleteAPIView.as_view(), name='relation-delete'),
    path('relations/export/', RelationExportAPIView.as_view(), name='relation-export'),
    path('relations/import/', RelationImportAPIView.as_view(), name='relation-import'),

   
    path("civil-id-name/create/", CivilIdNameCreateAPIView.as_view(), name="civil_id_name_create"),
    path("civil-id-name/", CivilIdNameListAPIView.as_view(), name="civil_id_name_list"),
    path("civil-id-name/<uuid:uuid>/", CivilIdNameRetrieveAPIView.as_view(), name="civil_id_name_retrieve"),
    path("civil-id-name/<uuid:uuid>/update/", CivilIdNameUpdateAPIView.as_view(), name="civil_id_name_update"),
    path("civil-id-name/delete/",CivilIdNameDeleteAPIView.as_view(),name="civil_id_name_delete_single"),
    path("civil-id-name/export/", CivilIdNameExportAPIView.as_view(), name="civil_id_name_export"),
    path("civil-id-name/import/", CivilIdNameImportAPIView.as_view(), name="civil_id_name_import"),
 
   
   
    path('timezones/create/', TimezoneCreateAPIView.as_view(), name='timezone-create'),
    path('timezones/', TimezoneListAPIView.as_view(), name='timezone-list'),
    path('timezones/<uuid:uuid>/', TimezoneRetrieveAPIView.as_view(), name='timezone-details'),
    path('timezones/<uuid:uuid>/update/', TimezoneUpdateAPIView.as_view(), name='timezone-update'),
    path('timezones/delete/', TimezoneDeleteAPIView.as_view(), name='timezone-delete'),
    path('timezones/export/', TimezoneExportAPIView.as_view(), name='timezone-export'),
    path('timezones/import/', TimezoneImportAPIView.as_view(), name='timezone-import'),


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
    path('ownership-types/export/',  OwnershipTypeExportAPIView.as_view(), name='ownershiptype-export'),
    path('ownership-types/import/',  OwnershipTypeImportAPIView.as_view(), name='ownershiptype-import'),



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
    path('stakeholder-types/<uuid:uuid>/', StakeholderTypeRetrieveAPIView.as_view(), name='stakeholdertype-detail'),
    path('stakeholder-types/<uuid:uuid>/update/', StakeholderTypeUpdateAPIView.as_view(), name='stakeholdertype-update'),
    path('stakeholder-types/delete/', StakeholderTypeDeleteAPIView.as_view(), name='stakeholdertype-delete'),
    path('stakeholder-types/export/',  StakeholderTypeExportAPIView.as_view(), name='stakeholdercategory-export'),
    path('stakeholder-types/import/',  StakeholderTypeImportAPIView.as_view(), name='stakeholdercategory-import'),


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
    path('accreditation-name/export/',  AccreditationNameExportAPIView.as_view(), name=' accreditation-export'),
    path('accreditation-name/import/',  AccreditationNameImportAPIView.as_view(), name='accreditation-import'),


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
    path('license-name/export/',   LicenseNameExportAPIView.as_view(), name=' LicenseName-export'),
    path('license-name/import/',   LicenseNameImportAPIView.as_view(), name=' LicenseName-import'),
    

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

    path("lostreasonB2B/create/", LostReasonB2BCreateAPIView.as_view(), name='LostReason-create'),
    path("lostreasonB2B/", LostReasonB2BListAPIView.as_view(), name='LostReason-list'),
    path("lostreasonB2B/<uuid:uuid>/", LostReasonB2BRetrieveAPIView.as_view(), name='LostReason-detail'),
    path("lostreasonB2B/<uuid:uuid>/update/", LostReasonB2BUpdateAPIView.as_view(), name='LostReason-update'),
    path("lostreasonB2B/delete/", LostReasonB2BDeleteAPIView.as_view(), name='LostReason-delete'),
    path('lostreasonB2B/export/', LostReasonB2BExportAPIView.as_view(), name=' LostReason-export'),
    path('lostreasonB2B/import/',  LostReasonB2BImportAPIView.as_view(), name=' LostReason-import'),


    path('education-level-codes/create/', EducationLevelCodeCreateAPIView.as_view(), name='educationlevelcode-create'),
    path("education-level-codes/", EducationLevelCodeListAPIView.as_view(), name='educationlevelcode-list'),
    path('education-level-codes/<uuid:uuid>/', EducationLevelCodeRetrieveAPIView.as_view(), name='educationlevelcode-retrieve'),
    path('education-level-codes/<uuid:uuid>/update/', EducationLevelCodeUpdateAPIView.as_view(), name='educationlevelcode-update'),
    path('education-level-codes/delete/', EducationLevelCodeDeleteAPIView.as_view(), name='educationlevelcode-delete'),
    path('education-level-codes/export/', EducationLevelCodeExportAPIView.as_view(), name='educationlevelcode-export'),
    path('education-level-codes/import/', EducationLevelCodeImportAPIView.as_view(), name='educationlevelcode-import'),
    
    path('education-level/create/', EducationLevelCreateAPIView.as_view(), name='educationlevel-create'),
    path("education-level/", EducationLevelListAPIView.as_view(), name='educationlevelcode-list'),
    path('education-level/<uuid:uuid>/', EducationLevelRetrieveAPIView.as_view(), name='educationlevel-retrieve'),
    path('education-level/<uuid:uuid>/update/', EducationLevelUpdateAPIView.as_view(), name='educationlevel-update'),
    path('education-level/delete/', EducationLevelDeleteAPIView.as_view(), name='educationlevel-delete'),
    path('education-level/export/', EducationLevelExportAPIView.as_view(), name='educationlevel-export'),
    path('education-level/import/', EducationLevelImportAPIView.as_view(), name='educationlevel-import'),

    path("education-duration/", EducationDurationListAPIView.as_view(), name='Educationduration-list'),
    path('education-duration/create/', EducationDurationCreateAPIView.as_view(), name='educationduration-create'),
    path('education-duration/<uuid:uuid>/', EducationDurationRetrieveAPIView.as_view(), name='educationduration-retrieve'),
    path('education-duration/<uuid:uuid>/update/', EducationDurationUpdateAPIView.as_view(), name='educationduration-update'),
    path('education-duration/delete/', EducationDurationDeleteAPIView.as_view(), name='educationduration-delete'),
    path('education-duration/export/', EducationDurationExportAPIView.as_view(), name='educationduration-export'),
    path('education-duration/import/', EducationDurationImportAPIView.as_view(), name='educationduration-import'),
    

    path('education-type/', EducationTypeListAPIView.as_view(), name='education-type-list'),
    path('education-type/create/', EducationTypeCreateAPIView.as_view(), name='education-type-create'),
    path('education-type/<uuid:uuid>/', EducationTypeRetrieveAPIView.as_view(), name='education-type-detail'),
    path('education-type/<uuid:uuid>/update/', EducationTypeUpdateAPIView.as_view(), name='education-type-update'),
    path('education-type/delete/', EducationTypeDeleteAPIView.as_view(), name='education-type-delete'),
    path('education-type/export/', EducationTypeExportAPIView.as_view(), name='education-type-export'),
    path('education-type/import/', EducationTypeImportAPIView.as_view(), name='education-type-import'),
 
    path("studymainarea/", StudymainareaListAPIView.as_view(), name='studymainarea-list'),
    path('studymainarea/create/', StudymainareaCreateAPIView.as_view(), name='studymainarea-create'),
    path('studymainarea/<uuid:uuid>/', StudymainareaRetrieveAPIView.as_view(), name='studymainarea-retrieve'),
    path('studymainarea/<uuid:uuid>/update/', StudymainareaUpdateAPIView.as_view(), name='studymainarea-update'),
    path('studymainarea/delete/', StudymainareaDeleteAPIView.as_view(), name='studymainarea-delete'),
    path('studymainarea/export/', StudymainareaExportAPIView.as_view(), name='studymainarea-export'),
    path('studymainarea/import/', StudymainareaImportAPIView.as_view(), name='studymainarea-import'),
    
    path("studymajorarea/", StudyMajorAreaListAPIView.as_view(), name='studymajorarea-list'),
    path('studymajorarea/create/', StudyMajorAreaCreateAPIView.as_view(), name='studymajorarea-create'),
    path('studymajorarea/<uuid:uuid>/', StudyMajorAreaRetrieveAPIView.as_view(), name='studymajorarea-retrieve'),
    path('studymajorarea/<uuid:uuid>/update/',StudyMajorAreaUpdateAPIView.as_view(), name='studymajorarea-update'),
    path('studymajorarea/delete/', StudyMajorAreaDeleteAPIView.as_view(), name='studymajorarea-delete'),
    path('studymajorarea/export/', StudyMajorAreaExportAPIView.as_view(), name='studymajorarea-export'),
    path('studymajorarea/import/', StudyMajorAreaImportAPIView.as_view(), name='studymajorarea-import'),
    path('study-major-by-main/', StudyMajorAreaByMainUUIDAPIView.as_view(), name='study-main-by-major-uuid'),

    path("studyspecialisation/",StudySpecialisationListAPIView.as_view(), name='studyspecialisation-list'),
    path('studyspecialisation/create/', StudySpecialisationCreateAPIView.as_view(), name='studyspecialisation-create'),
    path('studyspecialisation/<uuid:uuid>/', StudySpecialisationRetrieveAPIView.as_view(), name='studyspecialisation-retrieve'),
    path('studyspecialisation/<uuid:uuid>/update/', StudySpecialisationUpdateAPIView.as_view(), name='studyspecialisation-update'),
    path('studyspecialisation/delete/', StudySpecialisationDeleteAPIView.as_view(), name='studyspecialisation-delete'),
    path('studyspecialisation/export/', StudySpecialisationExportAPIView.as_view(), name='studyspecialisation-export'),
    path('studyspecialisation/import/', StudySpecialisationImportAPIView.as_view(), name='studyspecialisation-import'),

    path('academicresulttype/', AcademicResultTypeListAPIView.as_view(), name='academicresulttype-list'),
    path('academicresulttype/create/', AcademicResultTypeCreateAPIView.as_view(), name='academicresulttype-create'),
    path('academicresulttype/<uuid:uuid>/', AcademicResultTypeRetrieveAPIView.as_view(), name='academicresulttype-retrieve'),
    path('academicresulttype/<uuid:uuid>/update/', AcademicResultTypeUpdateAPIView.as_view(), name='academicresulttype-update'),
    path('academicresulttype/delete/', AcademicResultTypeDeleteAPIView.as_view(), name='academicresulttype-delete'),
    path('academicresulttype/export/', AcademicResultTypeExportAPIView.as_view(), name='academicresulttype-export'),
    path('academicresulttype/import/', AcademicResultTypeImportAPIView.as_view(), name='academicresulttype-import'),


    #Education Type
    path('education-type/', EducationTypeListAPIView.as_view(), name='education-type-list'),
    path('education-type/create/', EducationTypeCreateAPIView.as_view(), name='education-type-create'),
    path('education-type/<uuid:uuid>/', EducationTypeRetrieveAPIView.as_view(), name='education-type-detail'),
    path('education-type/update/<uuid:uuid>/', EducationTypeUpdateAPIView.as_view(), name='education-type-update'),
    path('education-type/delete/', EducationTypeDeleteAPIView.as_view(), name='education-type-delete'),
    path('education-type/export/', EducationTypeExportAPIView.as_view(), name='education-type-export'),
    path('education-type/import/', EducationTypeImportAPIView.as_view(), name='education-type-import'),


    path('academicresult/', AcademicResultListAPIView.as_view(), name='academicresult-list'),
    path('academicresult/create/', AcademicResultCreateAPIView.as_view(), name='academicresult-create'),
    path('academicresult/<uuid:uuid>/', AcademicResultRetrieveAPIView.as_view(), name='academicresult-retrieve'),
    path('academicresult/<uuid:uuid>/update/', AcademicResultUpdateAPIView.as_view(), name='academicresult-update'),
    path('academicresult/delete/', AcademicResultDeleteAPIView.as_view(), name='academicresult-delete'),
    path('academicresult/export/', AcademicResultExportAPIView.as_view(), name='academicresult-export'),
    path('academicresult/import/', AcademicResultImportAPIView.as_view(), name='academicresult-import'),    

   
    
    path('academic-result-comparison/', AcademicResultComparisonListAPIView.as_view(), name='academic-result-comparison-list'),
    path('academic-result-comparison/create/', AcademicResultComparisonCreateAPIView.as_view(), name='academic-result-comparison-create'),
    path('academic-result-comparison/<uuid:uuid>/', AcademicResultComparisonRetrieveAPIView.as_view(), name='academic-result-comparison-retrieve'),
    path('academic-result-comparison/<uuid:uuid>/update/', AcademicResultComparisonUpdateAPIView.as_view(), name='academic-result-comparison-update'),
    path('academic-result-comparison/delete/', AcademicResultComparisonDeleteAPIView.as_view(), name='academic-result-comparison-delete'),
    path('academic-result-comparison/export/', AcademicResultComparisonExportAPIView.as_view(), name='academic-result-comparison-export'),


    path('mediumeducation/',MediumofEducationListAPIView.as_view(), name='educationlevel-list'),
    path('mediumeducation/create/', MediumofEducationCreateAPIView.as_view(), name='mediumeducation-create'),
    path('mediumeducation/<uuid:uuid>/', MediumofEducationRetrieveAPIView.as_view(), name='mediumeducation-retrieve'),
    path('mediumeducation/<uuid:uuid>/update/', MediumofEducationUpdateAPIView.as_view(), name='mediumeducation-update'),
    path('mediumeducation/delete/', MediumofEducationDeleteAPIView.as_view(), name='mediumeducation-delete'),
    path('mediumeducation/export/', MediumofEducationExportAPIView.as_view(), name='educationlevel-export'),
    path('mediumeducation/import/',MediumofEducationImportAPIView.as_view(), name='educationlevel-import'),

    path('eca-for/',ECAForListAPIView.as_view(), name='ecs-for-list'),
    path('eca-for/create/',ECAForCreateAPIView.as_view(), name='ecs-for-create'),
    path('eca-for/<uuid:uuid>/',ECAForRetrieveAPIView.as_view(), name='ecs-for-retrieve'),
    path('eca-for/<uuid:uuid>/update/',ECAForUpdateAPIView.as_view(), name='ecs-for-update'),
    path('eca-for/delete/',ECAForDeleteAPIView.as_view(), name='ecs-for-delete-multiple'),
    path('eca-for/export/',ECAForExportAPIView.as_view(), name='ecs-for-export'),
    path('eca-for/import/',ECAForImportAPIView.as_view(), name='ecs-for-import'),

    path('language-test-results/', LanguageTestResultListAPIView.as_view(), name='language_test_result_list'),
    path('language-test-results/create/', LanguageTestResultCreateAPIView.as_view(), name='language_test_result_create'),
    path('language-test-results/<uuid:uuid>/', LanguageTestResultRetrieveAPIView.as_view(), name='language_test_result_retrieve'),
    path('language-test-results/<uuid:uuid>/update/', LanguageTestResultUpdateAPIView.as_view(), name='language_test_result_update'),
    path('language-test-results/delete/', LanguageTestResultDeleteAPIView.as_view(), name='language_test_result_delete'),
    path('language-test-results/import/', LanguageTestResultImportAPIView.as_view(), name='language_test_result_import'),
    path('language-test-results/export/', LanguageTestResultExportAPIView.as_view(), name='language_test_result_export'),

   
    path('eca-awarding-bodies/', ECAAwardingBodyListAPIView.as_view(), name='eca-awarding-body-list'),
    path('eca-awarding-bodies/create/', ECAAwardingBodyCreateAPIView.as_view(), name='eca-awarding-body-create'),
    path('eca-awarding-bodies/<uuid:uuid>/', ECAAwardingBodyRetrieveAPIView.as_view(), name='eca-awarding-body-retrieve'),
    path('eca-awarding-bodies/<uuid:uuid>/update/', ECAAwardingBodyUpdateAPIView.as_view(), name='eca-awarding-body-update'),
    path('eca-awarding-bodies/delete/', ECAAwardingBodyDeleteAPIView.as_view(), name='eca-awarding-body-delete'),
    path('eca-awarding-bodies/export/', ECAAwardingBodyExportAPIView.as_view(), name='eca-awarding-body-export'),
    path('eca-awarding-bodies/import/', ECAAwardingBodyImportAPIView.as_view(), name='eca-awarding-body-import'),

    path('degree-awarded-by/', DegreeAwardedByListAPIView.as_view(), name='degree-awarded-by-list'),
    path('degree-awarded-by/create/', DegreeAwardedByCreateAPIView.as_view(), name='degree-awarded-by-create'),
    path('degree-awarded-by/<uuid:uuid>/', DegreeAwardedByRetrieveAPIView.as_view(), name='degree-awarded-by-retrieve'),
    path('degree-awarded-by/<uuid:uuid>/update/', DegreeAwardedByUpdateAPIView.as_view(), name='degree-awarded-by-update'),
    path('degree-awarded-by/delete/', DegreeAwardedByDeleteAPIView.as_view(), name='degree-awarded-by-delete'),
    path('degree-awarded-by/export/', DegreeAwardedByExportAPIView.as_view(), name='degree-awarded-by-export'),
    path('degree-awarded-by/import/', DegreeAwardedByImportAPIView.as_view(), name='degree-awarded-by-import'),


    path('degree-awarded-institute/', DegreeAwardedInstituteListAPIView.as_view(), name='degree_awarded_institute_list'),
    path('degree-awarded-institute/create/', DegreeAwardedInstituteCreateAPIView.as_view(), name='degree_awarded_institute_create'),
    path('degree-awarded-institute/<uuid:uuid>/retrieve/', DegreeAwardedInstituteRetrieveAPIView.as_view(), name='degree_awarded_institute_retrieve'),
    path('degree-awarded-institute/<uuid:uuid>/update/', DegreeAwardedInstituteUpdateAPIView.as_view(), name='degree_awarded_institute_update'),    path('degree-awarded-institute/delete/', DegreeAwardedInstituteDeleteAPIView.as_view(), name='degree_awarded_institute_delete_bulk'),
    path('degree-awarded-institute/export/', DegreeAwardedInstituteExportAPIView.as_view(), name='degree_awarded_institute_export'),
    path('degree-awarded-institute/import/', DegreeAwardedInstituteImportAPIView.as_view(), name='degree_awarded_institute_import'),
    path('degrees-by-education-level/', DegreeAwardedByEducationLevelAPIView.as_view(), name='degrees-by-education-level'),

    path('language/create/', LanguageCreateAPIView.as_view(), name='language-create'),
    path('language/<uuid:uuid>/', LanguageRetrieveAPIView.as_view(), name='language-retrieve'),
    path('language/<uuid:uuid>/update', LanguageUpdateAPIView.as_view(), name='language-update'),
    path('language/delete/', LanguageDeleteAPIView.as_view(), name='language-delete'),
    path('language/', LanguageListAPIView.as_view(), name='language-list'),
    path('language/export/', LanguageExportAPIView.as_view(), name='language-export'),
    path('language/import/', LanguageImportAPIView.as_view(), name='language-import'),
    path('language-tests-by-language/', LanguageTestsAPIView.as_view(), name='language-tests'),
    path('entrance-test-modules/', EntranceTestModulesAPIView.as_view(), name='entrance-test-modules'),
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
    path('study-language-banchmarks/export/', StudyLanguageBenchmarkExportAPIView.as_view(), name='study-language-banchmark-export'),
    path('study-language-banchmarks/import/', StudyLanguageBenchmarkImportAPIView.as_view(), name='study-language-banchmark-import'),

    # --------- EntranceTestName --------- #
    path('entrance-tests/', EntranceTestNameListAPIView.as_view(), name='entrance-test-list'),
    path('entrance-tests/create/', EntranceTestNameCreateAPIView.as_view(), name='entrance-test-create'),
    path('entrance-tests/<uuid:uuid>/', EntranceTestNameRetrieveAPIView.as_view(), name='entrance-test-retrieve'),
    path('entrance-tests/<uuid:uuid>/update/', EntranceTestNameUpdateAPIView.as_view(), name='entrance-test-update'),
    path('entrance-tests/delete/', EntranceTestNameDeleteAPIView.as_view(), name='entrance-test-delete'),
    path('entrance-tests/export/', EntranceTestNameExportAPIView.as_view(), name='entrance-test-export'),
    path('entrance-tests/import/', EntranceTestNameImportAPIView.as_view(), name='entrance-test-import'),

    path('entrance-tests-module/', EntranceTestModuleNameListAPIView.as_view(), name='entrance-test-list'),
    path('entrance-tests-module/create/', EntranceTestModuleNameCreateAPIView.as_view(), name='entrance-test-create'),
    path('entrance-tests-module/<uuid:uuid>/', EntranceTestModuleNameRetrieveAPIView.as_view(), name='entrance-test-retrieve'),
    path('entrance-tests-module/<uuid:uuid>/update/', EntranceTestModuleNameUpdateAPIView.as_view(), name='entrance-test-update'),
    path('entrance-tests-module/delete/', EntranceTestModuleNameDeleteAPIView.as_view(), name='entrance-test-delete'),
    path('entrance-tests-module/export/', EntranceTestModuleExportAPIView.as_view(), name='entrance-test-export'),
    path('entrance-tests-module/import/', EntranceTestModuleImportAPIView.as_view(), name='entrance-test-import'),

    path('entrancetestresult/', EntranceTestResultListAPIView.as_view(), name='entrancetestresult-list'),
    path('entrancetestresult/create/', EntranceTestResultCreateAPIView.as_view(), name='entrancetestresult-create'),
    path('entrancetestresult/<uuid:uuid>/', EntranceTestResultRetrieveAPIView.as_view(), name='entrancetestresult-retrieve'),
    path('entrancetestresult/<uuid:uuid>/update/', EntranceTestResultUpdateAPIView.as_view(), name='entrancetestresult-update'),
    path('entrancetestresult/delete/', EntranceTestResultDeleteAPIView.as_view(), name='entrancetestresult-delete'),
    path('entrancetestresult/export/', EntranceTestResultExportAPIView.as_view(), name='entrancetestresult-export'),
    path('entrancetestresult/import/', EntranceTestResultImportAPIView.as_view(), name='entrancetestresult-import'),

   #----------------------- process.py------------------
    path("documentcategory/create/", DocumentCategoryCreateAPIView.as_view(), name='DocumentCategory-create'),
    path("documentcategory/", DocumentCategoryListAPIView.as_view(), name='DocumentCategory-list'),
    path("documentcategory/<uuid:uuid>/", DocumentCategoryRetrieveAPIView.as_view(), name='DocumentCategory-detail'),
    path("documentcategory/<uuid:uuid>/update/", DocumentCategoryUpdateAPIView.as_view(), name='DocumentCategory-update'),
    path("documentcategory/delete/", DocumentCategoryDeleteAPIView.as_view(), name='DocumentCategory-delete'),
    path("documentcategory/export/", DocumentCategoryExportAPIView.as_view(), name='DocumentCategory-export'),
    path("documentcategory/import/", DocumentCategoryImportAPIView.as_view(), name='DocumentCategory-import'),

    path('documenttype/create/', DocumentTypeCreateAPIView.as_view(), name='document_type_create'),
    path('documenttype/', DocumentTypeListAPIView.as_view(), name='document_type_list'),
    path('documenttype/<uuid:uuid>/', DocumentTypeRetrieveAPIView.as_view(), name='document_type_retrieve'),
    path('documenttype/<uuid:uuid>/update/', DocumentTypeUpdateAPIView.as_view(), name='document_type_update'),
    path('documenttype/delete/', DocumentTypeDeleteAPIView.as_view(), name='document_type_delete'),
    path('documenttype/export/', DocumentTypeExportAPIView.as_view(), name='document-type-export'),
    path('documenttype/import/', DocumentTypeImportAPIView.as_view(), name='document-type-import'),

    path('documentname/create/',DocumentNameCreateAPIView.as_view(), name='document_name_create'),
    path('documentname/', DocumentNameListAPIView.as_view(), name='document_name_list'),
    path('documentname/<uuid:uuid>/', DocumentNameRetrieveAPIView.as_view(), name='document_name_retrieve'),
    path('documentname/<uuid:uuid>/update/', DocumentNameUpdateAPIView.as_view(), name='document_name_update'),
    path('documentname/delete/', DocumentNameDeleteAPIView.as_view(), name='document_name_delete'),
    path('documentname/export/', DocumentNameExportAPIView.as_view(), name='document_name_export'),
    path('documentname/import/', DocumentNameImportAPIView.as_view(), name='document_name_import'),

    path('purpose-of-visit/create/',PurposeOfVisitCreateAPIView.as_view(), name='purpose_create'),
    path('purpose-of-visit/', PurposeOfVisitListAPIView.as_view(), name='purpose_list'),
    path('purpose-of-visit/<uuid:uuid>/', PurposeOfVisitRetrieveAPIView.as_view(), name='purpose_retrieve'),
    path('purpose-of-visit/<uuid:uuid>/update/', PurposeOfVisitUpdateAPIView.as_view(), name='purpose_update'),
    path('purpose-of-visit/delete/', PurposeOfVisitDeleteAPIView.as_view(), name='purpose_delete'),
    path('purpose-of-visit/export/', PurposeOfVisitExportAPIView.as_view(), name='purpose_export'),
    path('purpose-of-visit/import/', PurposeOfVisitImportAPIView.as_view(), name='purpose_import'),


    path("documentsfor/", DocumentsForListAPIView.as_view(), name='DocumentsFor-list'),
    path("documentsfor/create/", DocumentsForCreateAPIView.as_view(), name='DocumentsFor-create'),
    path("documentsfor/<uuid:uuid>/", DocumentsForRetrieveAPIView.as_view(), name='DocumentsFor-detail'),
    path("documentsfor/<uuid:uuid>/update/", DocumentsForUpdateAPIView.as_view(), name='DocumentsFor-update'),
    path("documentsfor/delete/", DocumentsForDeleteAPIView.as_view(), name='DocumentsFor-delete'),
    path("documentsfor/export/", DocumentsForExportAPIView.as_view(), name='DocumentsFor-export'),
    path("documentsfor/import/", DocumentsForImportAPIView.as_view(), name='DocumentsFor-import'),


    path('requireddocument/create/', RequiredDocumentCreateAPIView.as_view(), name='required_document_create'),
    path('requireddocument/', RequiredDocumentListAPIView.as_view(), name='required_document_list'),
    path('requireddocument/<uuid:uuid>/', RequiredDocumentRetrieveAPIView.as_view(), name='required_document_retrieve'),
    path('requireddocument/<uuid:uuid>/update/', RequiredDocumentUpdateAPIView.as_view(), name='required_document_update'),
    path('requireddocument/delete/', RequiredDocumentDeleteAPIView.as_view(), name='required_document_delete'),
    path('requireddocument/export/', RequiredDocumentExportAPIView.as_view(), name='required_document_export'),
    path('requireddocument/import/', RequiredDocumentImportAPIView.as_view(), name='required_document_import'),

    path('process-status-name/create/', ProcessStatusCreateAPIView.as_view(), name='process_status_create'),
    path('process-status-name/', ProcessStatusListAPIView.as_view(), name='process_status_list'),
    path('process-status-name/<uuid:uuid>/', ProcessStatusRetrieveAPIView.as_view(), name='process_status_retrieve'),
    path('process-status-name/<uuid:uuid>/update/', ProcessStatusUpdateAPIView.as_view(), name='process_status_update'),
    path('process-status-name/delete/', ProcessStatusDeleteAPIView.as_view(), name='process_status_delete'),
    path('process-status-name/export/', ProcessStatusExportAPIView.as_view(), name='process_status_export'),
    path('process-status-name/import/', ProcessStatusImportAPIView.as_view(), name='process_status_import'),

    path('process-substatus-name/create/', ProcessSubStatusCreateAPIView.as_view(), name='process_sub_status_create'),
    path('process-substatus-name/', ProcessSubStatusListAPIView.as_view(), name='process_sub_status_list'),
    path('process-substatus-name/<uuid:uuid>/', ProcessSubStatusRetrieveAPIView.as_view(), name='process_sub_status_retrieve'),
    path('process-substatus-name/<uuid:uuid>/update/', ProcessSubStatusUpdateAPIView.as_view(), name='process_sub_status_update'),
    path('process-substatus-name/delete/', ProcessSubStatusDeleteAPIView.as_view(), name='process_sub_status_delete'),
    path('process-substatus-name/export/', ProcessSubStatusExportAPIView.as_view(), name='process_sub_status_export'),
    path('process-substatus-name/import/', ProcessSubStatusImportAPIView.as_view(), name='process_sub_status_import'),

    path("process-type/create/", ProcessTypeCreateAPIView.as_view(), name="process_type_create"),
    path("process-type/", ProcessTypeListAPIView.as_view(), name="process_type_list"),
    path("process-type/<uuid:uuid>/", ProcessTypeRetrieveAPIView.as_view(), name="process_type_retrieve"),
    path("process-type/<uuid:uuid>/update/", ProcessTypeUpdateAPIView.as_view(), name="process_type_update"),
    path("process-type/delete/", ProcessTypeDeleteAPIView.as_view(), name="process_type_delete"),
    path("process-type/export/", ProcessTypeExportAPIView.as_view(), name="process_type_export"),
    path("process-type/import/", ProcessTypeImportAPIView.as_view(), name="process_type_import"),

    path("payment-to/create/", PaymentToCreateAPIView.as_view(), name="payment_to_create"),
    path("payment-to/", PaymentToListAPIView.as_view(), name="payment_to_list"),
    path("payment-to/<uuid:uuid>/", PaymentToRetrieveAPIView.as_view(), name="payment_to_retrieve"),
    path("payment-to/<uuid:uuid>/update/", PaymentToUpdateAPIView.as_view(), name="payment_to_update"),
    path("payment-to/delete/", PaymentToDeleteAPIView.as_view(), name="payment_to_delete"),
    path("payment-to/export/", PaymentToExportAPIView.as_view(), name="payment_to_export"),
    path("payment-to/import/", PaymentToImportAPIView.as_view(), name="payment_to_import"),

    path("paymentcategory/create/", PaymentCategoryCreateAPIView.as_view(), name="payment_category_create"),
    path("paymentcategory/", PaymentCategoryListAPIView.as_view(), name="payment_category_list"),
    path("paymentcategory/<uuid:uuid>/", PaymentCategoryRetrieveAPIView.as_view(), name="payment_category_retrieve"),
    path("paymentcategory/<uuid:uuid>/update/", PaymentCategoryUpdateAPIView.as_view(), name="payment_category_update"),
    path("paymentcategory/delete/", PaymentCategoryDeleteAPIView.as_view(), name="payment_category_delete"),
    path("paymentcategory/export/", PaymentCategoryExportAPIView.as_view(), name="payment_category_export"),
    path("paymentcategory/import/", PaymentCategoryImportAPIView.as_view(), name="payment_category_import"),


    path('representingcountry/', RepresentingCountryListAPIView.as_view(), name='representingcountry-list'),
    path('representingcountry/create/', RepresentingCountryCreateAPIView.as_view(), name='representingcountry-create'),
    path('representingcountry/<uuid:uuid>/', RepresentingCountryRetrieveAPIView.as_view(), name='representingcountry-retrieve'),
    path('representingcountry/<uuid:uuid>/update/', RepresentingCountryUpdateAPIView.as_view(), name='representingcountry-update'),
    path('representingcountry/delete/', RepresentingCountryDeleteAPIView.as_view(), name='representingcountry-delete'),
    path('representingcountry/export/', RepresentingCountryExportAPIView.as_view(), name='representingcountry-export'),
    path('representingcountry/import/', RepresentingCountryImportAPIView.as_view(), name='representingcountry-import'),

    path('visamain/', VisaMainListAPIView.as_view(), name='visamain-list'),
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

    path('visa-status/', VisaStatusListAPIView.as_view(), name='visastatus-list'),
    path('visa-status/create/', VisaStatusCreateAPIView.as_view(), name='visastatus-create'),
    path('visa-status/<uuid:uuid>/', VisaStatusRetrieveAPIView.as_view(), name='visastatus-retrieve'),
    path('visa-status/<uuid:uuid>/update/', VisaStatusUpdateAPIView.as_view(), name='visastatus-update'),
    path('visa-status/delete/', VisaStatusDeleteAPIView.as_view(), name='visastatus-delete'),
    path('visa-status/export/', VisaStatusExportAPIView.as_view(), name='visastatus-export'),
    path('visa-status/import/', VisaStatusImportAPIView.as_view(), name='visastatus-import'),


    path('visa-eligibility-type/', VisaEligibilityTypeListAPIView.as_view(), name='visaeligibility-list'),
    path('visa-eligibility-type/create/', VisaEligibilityTypeCreateAPIView.as_view(), name='visaeligibility-create'),
    path('visa-eligibility-type/<uuid:uuid>/', VisaEligibilityTypeRetrieveAPIView.as_view(), name='visaeligibility-retrieve'),
    path('visa-eligibility-type/<uuid:uuid>/update/', VisaEligibilityTypeUpdateAPIView.as_view(), name='visaeligibility-update'),
    path('visa-eligibility-type/delete/', VisaEligibilityTypeDeleteAPIView.as_view(), name='visaeligibility-delete-multiple'),
    path('visa-eligibility-type/export/', VisaEligibilityTypeExportAPIView.as_view(), name='visaeligibility-export'),
    path('visa-eligibility-type/import/', VisaEligibilityTypeImportAPIView.as_view(), name='visaeligibility-import'),
    
    path('possibility-level/', PossibilityLevelListAPIView.as_view(), name='possibilitylevel-list'),
    path('possibility-level/create/', PossibilityLevelCreateAPIView.as_view(), name='possibilitylevel-create'),
    path('possibility-level/<uuid:uuid>/', PossibilityLevelRetrieveAPIView.as_view(), name='possibilitylevel-retrieve'),
    path('possibility-level/<uuid:uuid>/update/', PossibilityLevelUpdateAPIView.as_view(), name='possibilitylevel-update'),
    path('possibility-level/<uuid:uuid>/delete/', PossibilityLevelDeleteAPIView.as_view(), name='possibilitylevel-delete'),
    path('possibility-level/delete/', PossibilityLevelDeleteAPIView.as_view(), name='possibilitylevel-delete-multiple'),
    path('possibility-level/export/', PossibilityLevelExportAPIView.as_view(), name='possibilitylevel-export'),
    path('possibility-level/import/', PossibilityLevelImportAPIView.as_view(), name='possibilitylevel-import'),

    path('applicanttype/', ApplicantTypeListAPIView.as_view(), name='applicanttype-list'),
    path('applicanttype/create/', ApplicantTypeCreateAPIView.as_view(), name='applicanttype-create'),
    path('applicanttype/<uuid:uuid>/', ApplicantTypeRetrieveAPIView.as_view(), name='applicanttype-retrieve'),
    path('applicanttype/<uuid:uuid>/update/', ApplicantTypeUpdateAPIView.as_view(), name='applicanttype-update'),
    path('applicanttype/delete/', ApplicantTypeDeleteAPIView.as_view(), name='applicanttype-delete'),
    path('applicanttype/export/', ApplicantTypeExportAPIView.as_view(), name='applicanttype-export'),
    path('applicanttype/import/', ApplicantTypeImportAPIView.as_view(), name='applicanttype-import'),
    
    path('jobtype/', JobTypeListAPIView.as_view(), name='jobtype-list'),
    path('jobtype/create/', JobTypeCreateAPIView.as_view(), name='jobtype-create'),
    path('jobtype/<uuid:uuid>/', JobTypeRetrieveAPIView.as_view(), name='jobtype-retrieve'),
    path('jobtype/<uuid:uuid>/update/', JobTypeUpdateAPIView.as_view(), name='jobtype-update'),
    path('jobtype/<uuid:uuid>/delete/', JobTypeDeleteAPIView.as_view(), name='jobtype-delete'),
    path('jobtype/delete/', JobTypeDeleteAPIView.as_view(), name='jobtype-bulk-delete'),
    path('jobtype/export/', JobTypeExportAPIView.as_view(), name='jobtype-export'),
    path('jobtype/import/', JobTypeImportAPIView.as_view(), name='jobtype-import'),

    path('modeofsalary/', ModeofSalaryListAPIView.as_view(), name='modeofsalary-list'),
    path('modeofsalary/create/', ModeofSalaryCreateAPIView.as_view(), name='modeofsalary-create'),
    path('modeofsalary/<uuid:uuid>/', ModeofSalaryRetrieveAPIView.as_view(), name='modeofsalary-retrieve'),
    path('modeofsalary/<uuid:uuid>/update/', ModeofSalaryUpdateAPIView.as_view(), name='modeofsalary-update'),
    path('modeofsalary/<uuid:uuid>/delete/', ModeofSalaryDeleteAPIView.as_view(), name='modeofsalary-delete'),
    path('modeofsalary/delete/', ModeofSalaryDeleteAPIView.as_view(), name='modeofsalary-bulk-delete'),
    path('modeofsalary/export/', ModeofSalaryExportAPIView.as_view(), name='modeofsalary-export'),
    path('modeofsalary/import/', ModeofSalaryImportAPIView.as_view(), name='modeofsalary-import'),

    path('itreturnstatus/', ITReturnStatusListAPIView.as_view(), name='itreturnstatus-list'),
    path('itreturnstatus/create/', ITReturnStatusCreateAPIView.as_view(), name='itreturnstatus-create'),
    path('itreturnstatus/<uuid:uuid>/', ITReturnStatusRetrieveAPIView.as_view(), name='itreturnstatus-retrieve'),
    path('itreturnstatus/<uuid:uuid>/update/', ITReturnStatusUpdateAPIView.as_view(), name='itreturnstatus-update'),
    path('itreturnstatus/<uuid:uuid>/delete/', ITReturnStatusDeleteAPIView.as_view(), name='itreturnstatus-delete'),
    path('itreturnstatus/delete/', ITReturnStatusDeleteAPIView.as_view(), name='itreturnstatus-bulk-delete'),
    path('itreturnstatus/export/', ITReturnStatusExportAPIView.as_view(), name='itreturnstatus-export'),
    path('itreturnstatus/import/', ITReturnStatusImportAPIView.as_view(), name='itreturnstatus-import'),

     # ------------------ OccupationVersion ------------------ #
    path('occupation-version/', OccupationVersionListAPIView.as_view(), name='occupation-version-list'),
    path('occupation-version/create/', OccupationVersionCreateAPIView.as_view(), name='occupation-version-create'),
    path('occupation-version/<uuid:uuid>/', OccupationVersionRetrieveAPIView.as_view(), name='occupation-version-retrieve'),
    path('occupation-version/<uuid:uuid>/update/', OccupationVersionUpdateAPIView.as_view(), name='occupation-version-update'),
    path('occupation-version/delete/', OccupationVersionDeleteAPIView.as_view(), name='occupation-version-delete'),
    path('occupation-version/export/', OccupationVersionExportAPIView.as_view(), name='occupation-version-export'),
    path('occupation-version/import/', OccupationVersionImportAPIView.as_view(), name='occupation-version-import'),

    # ------------------ OccupationCategory ------------------ #
    path('occupation-category/', OccupationCategoryListAPIView.as_view(), name='occupation-category-list'),
    path('occupation-category/create/', OccupationCategoryCreateAPIView.as_view(), name='occupation-category-create'),
    path('occupation-category/<uuid:uuid>/', OccupationCategoryRetrieveAPIView.as_view(), name='occupation-category-retrieve'),
    path('occupation-category/<uuid:uuid>/update/', OccupationCategoryUpdateAPIView.as_view(), name='occupation-category-update'),
    path('occupation-category/delete/', OccupationCategoryDeleteAPIView.as_view(), name='occupation-category-delete'),
    path('occupation-category/export/', OccupationCategoryExportAPIView.as_view(), name='occupation-category-export'),
    path('occupation-category/import/', OccupationCategoryImportAPIView.as_view(), name='occupation-category-import'),

    # ------------------ OccupationLevelCode ------------------ #
    path('occupation-level-code/', OccupationLevelCodeListAPIView.as_view(), name='occupation-level-code-list'),
    path('occupation-level-code/create/', OccupationLevelCodeCreateAPIView.as_view(), name='occupation-level-code-create'),
    path('occupation-level-code/<uuid:uuid>/', OccupationLevelCodeRetrieveAPIView.as_view(), name='occupation-level-code-retrieve'),
    path('occupation-level-code/<uuid:uuid>/update/', OccupationLevelCodeUpdateAPIView.as_view(), name='occupation-level-code-update'),
    path('occupation-level-code/delete/', OccupationLevelCodeDeleteAPIView.as_view(), name='occupation-level-code-delete'),
    path('occupation-level-code/export/', OccupationLevelCodeExportAPIView.as_view(), name='occupation-level-code-export'),
    path('occupation-level-code/import/', OccupationLevelCodeImportAPIView.as_view(), name='occupation-level-code-import'),

    # ------------------ OccupationLevel ------------------ #
    path('occupation-level/', OccupationLevelListAPIView.as_view(), name='occupation-level-list'),
    path('occupation-level/create/', OccupationLevelCreateAPIView.as_view(), name='occupation-level-create'),
    path('occupation-level/<uuid:uuid>/', OccupationLevelRetrieveAPIView.as_view(), name='occupation-level-retrieve'),
    path('occupation-level/<uuid:uuid>/update/', OccupationLevelUpdateAPIView.as_view(), name='occupation-level-update'),
    path('occupation-level/delete/', OccupationLevelDeleteAPIView.as_view(), name='occupation-level-delete'),
    path('occupation-level/export/', OccupationLevelExportAPIView.as_view(), name='occupation-level-export'),
    path('occupation-level/import/', OccupationLevelImportAPIView.as_view(), name='occupation-level-import'),

    # ------------------ OccupationCode ------------------ #
    path('occupation-code/', OccupationCodeListAPIView.as_view(), name='occupation-code-list'),
    path('occupation-code/create/', OccupationCodeCreateAPIView.as_view(), name='occupation-code-create'),
    path('occupation-code/<uuid:uuid>/', OccupationCodeRetrieveAPIView.as_view(), name='occupation-code-retrieve'),
    path('occupation-code/<uuid:uuid>/update/', OccupationCodeUpdateAPIView.as_view(), name='occupation-code-update'),
    path('occupation-code/delete/', OccupationCodeDeleteAPIView.as_view(), name='occupation-code-delete'),
    path('occupation-code/export/', OccupationCodeExportAPIView.as_view(), name='occupation-code-export'),
    path('occupation-code/import/', OccupationCodeImportAPIView.as_view(), name='occupation-code-import'),

    # -------------------- OccupationType --------------------
    path('occupationtype/', OccupationTypeListAPIView.as_view(), name='occupationtype-list'),
    path('occupationtype/create/', OccupationTypeCreateAPIView.as_view(), name='occupationtype-create'),
    path('occupationtype/<uuid:uuid>/', OccupationTypeRetrieveAPIView.as_view(), name='occupationtype-retrieve'),
    path('occupationtype/<uuid:uuid>/update/', OccupationTypeUpdateAPIView.as_view(), name='occupationtype-update'),
    path('occupationtype/delete/', OccupationTypeDeleteAPIView.as_view(), name='occupationtype-delete'),
    path('occupationtype/export/', OccupationTypeExportAPIView.as_view(), name='occupationtype-export'),
    path('occupationtype/import/', OccupationTypeImportAPIView.as_view(), name='occupationtype-import'),

    # -------------------- OccupationProspect --------------------
    path('occupationprospect/', OccupationProspectListAPIView.as_view(), name='occupationprospect-list'),
    path('occupationprospect/create/', OccupationProspectCreateAPIView.as_view(), name='occupationprospect-create'),
    path('occupationprospect/<uuid:uuid>/', OccupationProspectRetrieveAPIView.as_view(), name='occupationprospect-retrieve'),
    path('occupationprospect/<uuid:uuid>/update/', OccupationProspectUpdateAPIView.as_view(), name='occupationprospect-update'),
    path('occupationprospect/delete/', OccupationProspectDeleteAPIView.as_view(), name='occupationprospect-delete'),
    path('occupationprospect/export/', OccupationProspectExportAPIView.as_view(), name='occupationprospect-export'),
    path('occupationprospect/import/', OccupationProspectImportAPIView.as_view(), name='occupationprospect-import'),

    path('occupation-names/',OccupationNameListAPIView.as_view(),name='occupationname-list'),
    path('occupation-names/create/',OccupationNameCreateAPIView.as_view(),name='occupationname-create'),
    path('occupation-names/<uuid:uuid>/',OccupationNameRetrieveAPIView.as_view(),name='occupationname-retrieve'),
    path('occupation-names/<uuid:uuid>/update/',OccupationNameUpdateAPIView.as_view(),name='occupationname-update'),
    path('occupation-names/<uuid:uuid>/delete/',OccupationNameDeleteAPIView.as_view(),name='occupationname-delete'),
    path('occupation-names/export/',OccupationNameExportAPIView.as_view(),name='occupationname-delete'),
    path('occupation-names/import/',OccupationNameImportAPIView.as_view(),name='occupationname-delete'),

    path('jobprospect/', JobProspectListAPIView.as_view(), name='JobProspect-list'),
    path('jobprospect/create/', JobProspectCreateAPIView.as_view(), name='JobProspect-create'),
    path('jobprospect/<uuid:uuid>/', JobProspectRetrieveAPIView.as_view(), name='JobProspect-retrieve'),
    path('jobprospect/<uuid:uuid>/update/', JobProspectUpdateAPIView.as_view(), name='JobProspect-update'),
    path('jobprospect/delete/', JobProspectDeleteAPIView.as_view(), name='JobProspect-delete'),
    path('jobprospect/export/', JobProspectExportAPIView.as_view(), name='JobProspect-export'),
    path('jobprospect/import/', JobProspectImportAPIView.as_view(), name='JobProspect-import'),


    path('workrights/', WorkRightsListAPIView.as_view(), name='workrights-list'),
    path('workrights/create/', WorkRightsCreateAPIView.as_view(), name='workrights-create'),
    path('workrights/<uuid:uuid>/', WorkRightsRetrieveAPIView.as_view(), name='workrights-retrieve'),
    path('workrights/<uuid:uuid>/update/', WorkRightsUpdateAPIView.as_view(), name='workrights-update'),
    path('workrights/<uuid:uuid>/delete/', WorkRightsDeleteAPIView.as_view(), name='workrights-delete'),
    path('workrights/delete/', WorkRightsDeleteAPIView.as_view(), name='workrights-bulk-delete'),
    path('workrights/export/', WorkRightsExportAPIView.as_view(), name='workrights-export'),
    path('workrights/import/', WorkRightsImportAPIView.as_view(), name='workrights-import'),

    path('workrights-during-study/', WorkRightsDuringStudyListAPIView.as_view(), name='workrights_during_study_list'),
    path('workrights-during-study/create/', WorkRightsDuringStudyCreateAPIView.as_view(), name='workrights_during_study_create'),
    path('workrights-during-study/<uuid:uuid>/', WorkRightsDuringStudyRetrieveAPIView.as_view(), name='workrights_during_study_retrieve'),
    path('workrights-during-study/<uuid:uuid>/update/', WorkRightsDuringStudyUpdateAPIView.as_view(), name='workrights_during_study_update'),
    path('workrights-during-study/delete/', WorkRightsDuringStudyDeleteAPIView.as_view(), name='workrights_during_study_delete'),
    path('workrights-during-study/export/', WorkRightsDuringStudyExportAPIView.as_view(), name='workrights_during_study_export'),
    path('workrights-during-study/import/', WorkRightsDuringStudyImportAPIView.as_view(), name='workrights_during_study_import'),

    path('workrights-during-vacation/', WorkRightsDuringVacationListAPIView.as_view(), name='workrights_during_vacation_list'),
    path('workrights-during-vacation/create/', WorkRightsDuringVacationCreateAPIView.as_view(), name='workrights_during_vacation_create'),
    path('workrights-during-vacation/<uuid:uuid>/', WorkRightsDuringVacationRetrieveAPIView.as_view(), name='workrights_during_vacation_retrieve'),
    path('workrights-during-vacation/<uuid:uuid>/update/', WorkRightsDuringVacationUpdateAPIView.as_view(), name='workrights_during_vacation_update'),
    path('workrights-during-vacation/delete/', WorkRightsDuringVacationDeleteAPIView.as_view(), name='workrights_during_vacation_delete'),
    path('workrights-during-vacation/export/', WorkRightsDuringVacationExportAPIView.as_view(), name='workrights_during_vacation_export'),
    path('workrights-during-vacation/import/', WorkRightsDuringVacationImportAPIView.as_view(), name='workrights_during_vacation_import'),

    path('workrights-after-study/', WorkRightsAfterStudyListAPIView.as_view(), name='workrights_after_study_list'),
    path('workrights-after-study/create/', WorkRightsAfterStudyCreateAPIView.as_view(), name='workrights_after_study_create'),
    path('workrights-after-study/<uuid:uuid>/', WorkRightsAfterStudyRetrieveAPIView.as_view(), name='workrights_after_study_retrieve'),
    path('workrights-after-study/<uuid:uuid>/update/', WorkRightsAfterStudyUpdateAPIView.as_view(), name='workrights_after_study_update'),
    path('workrights-after-study/delete/', WorkRightsAfterStudyDeleteAPIView.as_view(), name='workrights_after_study_delete'),
    path('workrights-after-study/export/', WorkRightsAfterStudyExportAPIView.as_view(), name='workrights_after_study_export'),
    path('workrights-after-study/import/', WorkRightsAfterStudyImportAPIView.as_view(), name='workrights_after_study_import'),

    path('pr-possibility/', PRPossibilityListAPIView.as_view(), name='pr_possibility_list'),
    path('pr-possibility/create/', PRPossibilityCreateAPIView.as_view(), name='pr_possibility_create'),
    path('pr-possibility/<uuid:uuid>/', PRPossibilityRetrieveAPIView.as_view(), name='pr_possibility_retrieve'),
    path('pr-possibility/<uuid:uuid>/update/', PRPossibilityUpdateAPIView.as_view(), name='pr_possibility_update'),
    path('pr-possibility/delete/', PRPossibilityDeleteAPIView.as_view(), name='pr_possibility_delete'),
    path('pr-possibility/export/', PRPossibilityExportAPIView.as_view(), name='pr_possibility_export'),
    path('pr-possibility/import/', PRPossibilityImportAPIView.as_view(), name='pr_possibility_import'),

    path('spouse-can-apply/', SpouseCanApplyListAPIView.as_view(), name='spouse_can_apply_list'),
    path('spouse-can-apply/create/', SpouseCanApplyCreateAPIView.as_view(), name='spouse_can_apply_create'),
    path('spouse-can-apply/<uuid:uuid>/', SpouseCanApplyRetrieveAPIView.as_view(), name='spouse_can_apply_retrieve'),
    path('spouse-can-apply/<uuid:uuid>/update/', SpouseCanApplyUpdateAPIView.as_view(), name='spouse_can_apply_update'),
    path('spouse-can-apply/delete/', SpouseCanApplyDeleteAPIView.as_view(), name='spouse_can_apply_delete'),
    path('spouse-can-apply/export/', SpouseCanApplyExportAPIView.as_view(), name='spouse_can_apply_export'),
    path('spouse-can-apply/import/', SpouseCanApplyImportAPIView.as_view(), name='spouse_can_apply_import'),

    path('spouse-visa-category/', SpouseVisaCategoryListAPIView.as_view(), name='spouse_visa_category_list'),
    path('spouse-visa-category/create/', SpouseVisaCategoryCreateAPIView.as_view(), name='spouse_visa_category_create'),
    path('spouse-visa-category/<uuid:uuid>/', SpouseVisaCategoryRetrieveAPIView.as_view(), name='spouse_visa_category_retrieve'),
    path('spouse-visa-category/<uuid:uuid>/update/', SpouseVisaCategoryUpdateAPIView.as_view(), name='spouse_visa_category_update'),
    path('spouse-visa-category/delete/', SpouseVisaCategoryDeleteAPIView.as_view(), name='spouse_visa_category_delete'),
    path('spouse-visa-category/export/', SpouseVisaCategoryExportAPIView.as_view(), name='spouse_visa_category_export'),
    path('spouse-visa-category/import/', SpouseVisaCategoryImportAPIView.as_view(), name='spouse_visa_category_import'),

    path('spouse-workrights/', SpouseWorkRightsListAPIView.as_view(), name='spouse_workrights_list'),
    path('spouse-workrights/create/', SpouseWorkRightsCreateAPIView.as_view(), name='spouse_workrights_create'),
    path('spouse-workrights/<uuid:uuid>/', SpouseWorkRightsRetrieveAPIView.as_view(), name='spouse_workrights_retrieve'),
    path('spouse-workrights/<uuid:uuid>/update/', SpouseWorkRightsUpdateAPIView.as_view(), name='spouse_workrights_update'),
    path('spouse-workrights/<uuid:uuid>/delete/', SpouseWorkRightsDeleteAPIView.as_view(), name='spouse_workrights_delete'),
    path('spouse-workrights/delete/', SpouseWorkRightsDeleteAPIView.as_view(), name='spouse_workrights_delete_bulk'),
    path('spouse-workrights/export/', SpouseWorkRightsExportAPIView.as_view(), name='spouse_workrights_export'),
    path('spouse-workrights/import/', SpouseWorkRightsImportAPIView.as_view(), name='spouse_workrights_import'),

    path('children-can-apply/', ChildrenCanApplyListAPIView.as_view(), name='children_can_apply_list'),
    path('children-can-apply/create/', ChildrenCanApplyCreateAPIView.as_view(), name='children_can_apply_create'),
    path('children-can-apply/<uuid:uuid>/', ChildrenCanApplyRetrieveAPIView.as_view(), name='children_can_apply_retrieve'),
    path('children-can-apply/<uuid:uuid>/update/', ChildrenCanApplyUpdateAPIView.as_view(), name='children_can_apply_update'),
    path('children-can-apply/delete/', ChildrenCanApplyDeleteAPIView.as_view(), name='children_can_apply_delete_bulk'),
    path('children-can-apply/export/', ChildrenCanApplyExportAPIView.as_view(), name='children_can_apply_export'),
    path('children-can-apply/import/', ChildrenCanApplyImportAPIView.as_view(), name='children_can_apply_import'),

    path('children-study-work-rights/', ChildrenStudyWorkRightsListAPIView.as_view(), name='children-study-work-rights-list'),
    path('children-study-work-rights/create/', ChildrenStudyWorkRightsCreateAPIView.as_view(), name='children-study-work-rights-create'),
    path('children-study-work-rights/<uuid:uuid>/', ChildrenStudyWorkRightsRetrieveAPIView.as_view(), name='children-study-work-rights-retrieve'),
    path('children-study-work-rights/<uuid:uuid>/update/', ChildrenStudyWorkRightsUpdateAPIView.as_view(), name='children-study-work-rights-update'),
    path('children-study-work-rights/delete/', ChildrenStudyWorkRightsDeleteAPIView.as_view(), name='children-study-work-rights-delete-multiple'),
    path('children-study-work-rights/export/', ChildrenStudyWorkRightsExportAPIView.as_view(), name='children-study-work-rights-export'),
    path('children-study-work-rights/import/', ChildrenStudyWorkRightsImportAPIView.as_view(), name='children-study-work-rights-import'),


    path('institutetype/', InstituteTypeListAPIView.as_view(), name='institutetype-list'),
    path('institutetype/create/', InstituteTypeCreateAPIView.as_view(), name='institutetype-create'),
    path('institutetype/<uuid:uuid>/', InstituteTypeRetrieveAPIView.as_view(), name='institutetype-retrieve'),
    path('institutetype/<uuid:uuid>/update/', InstituteTypeUpdateAPIView.as_view(), name='institutetype-update'),
    path('institutetype/delete/', InstituteTypeDeleteAPIView.as_view(), name='institutetype-delete'),
    path('institutetype/export/', InstituteTypeExportAPIView.as_view(), name='institutetype-export'),
    path('institutetype/import/', InstituteTypeImportAPIView.as_view(), name='institutetype-import'),

    # ------------------ InstituteGroupName ------------------
    path('institutegroupname/', InstituteGroupNameListAPIView.as_view(), name='institutegroupname-list'),
    path('institutegroupname/create/', InstituteGroupNameCreateAPIView.as_view(), name='institutegroupname-create'),
    path('institutegroupname/<uuid:uuid>/', InstituteGroupNameRetrieveAPIView.as_view(), name='institutegroupname-retrieve'),
    path('institutegroupname/<uuid:uuid>/update/', InstituteGroupNameUpdateAPIView.as_view(), name='institutegroupname-update'),
    path('institutegroupname/delete/', InstituteGroupNameDeleteAPIView.as_view(), name='institutegroupname-delete'),
    path('institutegroupname/export/', InstituteGroupNameExportAPIView.as_view(), name='institutegroupname-export'),
    path('institutegroupname/import/', InstituteGroupNameImportAPIView.as_view(), name='institutegroupname-import'),

    # ------------------ InstituteStatus ------------------
    path('institutestatus/', InstituteStatusListAPIView.as_view(), name='institutestatus-list'),
    path('institutestatus/create/', InstituteStatusCreateAPIView.as_view(), name='institutestatus-create'),
    path('institutestatus/<uuid:uuid>/', InstituteStatusRetrieveAPIView.as_view(), name='institutestatus-retrieve'),
    path('institutestatus/<uuid:uuid>/update/', InstituteStatusUpdateAPIView.as_view(), name='institutestatus-update'),
    path('institutestatus/delete/', InstituteStatusDeleteAPIView.as_view(), name='institutestatus-delete'),
    path('institutestatus/export/', InstituteStatusExportAPIView.as_view(), name='institutestatus-export'),
    path('institutestatus/import/', InstituteStatusImportAPIView.as_view(), name='institutestatus-import'),

    # ------------------ InstitutePriority ------------------
    path('institutepriority/', InstitutePriorityListAPIView.as_view(), name='institutepriority-list'),
    path('institutepriority/create/', InstitutePriorityCreateAPIView.as_view(), name='institutepriority-create'),
    path('institutepriority/<uuid:uuid>/', InstitutePriorityRetrieveAPIView.as_view(), name='institutepriority-retrieve'),
    path('institutepriority/<uuid:uuid>/update/', InstitutePriorityUpdateAPIView.as_view(), name='institutepriority-update'),
    path('institutepriority/delete/', InstitutePriorityDeleteAPIView.as_view(), name='institutepriority-delete'),
    path('institutepriority/export/', InstitutePriorityExportAPIView.as_view(), name='institutepriority-export'),
    path('institutepriority/import/', InstitutePriorityImportAPIView.as_view(), name='institutepriority-import'),

    # ------------------ InstituteDepartment ------------------
    path('institutedepartment/', InstituteDepartmentListAPIView.as_view(), name='institutedepartment-list'),
    path('institutedepartment/create/', InstituteDepartmentCreateAPIView.as_view(), name='institutedepartment-create'),
    path('institutedepartment/<uuid:uuid>/', InstituteDepartmentRetrieveAPIView.as_view(), name='institutedepartment-retrieve'),
    path('institutedepartment/<uuid:uuid>/update/', InstituteDepartmentUpdateAPIView.as_view(), name='institutedepartment-update'),
    path('institutedepartment/delete/', InstituteDepartmentDeleteAPIView.as_view(), name='institutedepartment-delete'),
    path('institutedepartment/export/', InstituteDepartmentExportAPIView.as_view(), name='institutedepartment-export'),
    path('institutedepartment/import/', InstituteDepartmentImportAPIView.as_view(), name='institutedepartment-import'),

    # ------------------ BankAccountFor ------------------
    path('bankaccountfor/', BankAccountForListAPIView.as_view(), name='bankaccountfor-list'),
    path('bankaccountfor/create/', BankAccountForCreateAPIView.as_view(), name='bankaccountfor-create'),
    path('bankaccountfor/<uuid:uuid>/', BankAccountForRetrieveAPIView.as_view(), name='bankaccountfor-retrieve'),
    path('bankaccountfor/<uuid:uuid>/update/', BankAccountForUpdateAPIView.as_view(), name='bankaccountfor-update'),
    path('bankaccountfor/delete/', BankAccountForDeleteAPIView.as_view(), name='bankaccountfor-delete'),
    path('bankaccountfor/<uuid:uuid>/delete/', BankAccountForDeleteAPIView.as_view(), name='bankaccountfor-delete-uuid'),
    path('bankaccountfor/export/', BankAccountForExportAPIView.as_view(), name='bankaccountfor-export'),
    path('bankaccountfor/import/', BankAccountForImportAPIView.as_view(), name='bankaccountfor-import'),

    # ------------------ WhenCommissionIssue ------------------
    path('whencommissionissue/', WhenCommissionIssueListAPIView.as_view(), name='whencommissionissue-list'),
    path('whencommissionissue/create/', WhenCommissionIssueCreateAPIView.as_view(), name='whencommissionissue-create'),
    path('whencommissionissue/<uuid:uuid>/', WhenCommissionIssueRetrieveAPIView.as_view(), name='whencommissionissue-retrieve'),
    path('whencommissionissue/<uuid:uuid>/update/', WhenCommissionIssueUpdateAPIView.as_view(), name='whencommissionissue-update'),
    path('whencommissionissue/delete/', WhenCommissionIssueDeleteAPIView.as_view(), name='whencommissionissue-delete'),
    path('whencommissionissue/export/', WhenCommissionIssueExportAPIView.as_view(), name='whencommissionissue-export'),
    path('whencommissionissue/import/', WhenCommissionIssueImportAPIView.as_view(), name='whencommissionissue-import'),

    # ------------------ CourseLevelCode ------------------
    path('courselevelcode/', CourseLevelCodeListAPIView.as_view(), name='courselevelcode-list'),
    path('courselevelcode/create/', CourseLevelCodeCreateAPIView.as_view(), name='courselevelcode-create'),
    path('courselevelcode/<uuid:uuid>/', CourseLevelCodeRetrieveAPIView.as_view(), name='courselevelcode-retrieve'),
    path('courselevelcode/<uuid:uuid>/update/', CourseLevelCodeUpdateAPIView.as_view(), name='courselevelcode-update'),
    path('courselevelcode/delete/', CourseLevelCodeDeleteAPIView.as_view(), name='courselevelcode-delete'),
    path('courselevelcode/export/', CourseLevelCodeExportAPIView.as_view(), name='courselevelcode-export'),
    path('courselevelcode/import/', CourseLevelCodeImportAPIView.as_view(), name='courselevelcode-import'),

    # ------------------ CourseDividedIn ------------------
    path('coursedividedin/', CourseDividedInListAPIView.as_view(), name='coursedividedin-list'),
    path('coursedividedin/create/', CourseDividedInCreateAPIView.as_view(), name='coursedividedin-create'),
    path('coursedividedin/<uuid:uuid>/', CourseDividedInRetrieveAPIView.as_view(), name='coursedividedin-retrieve'),
    path('coursedividedin/<uuid:uuid>/update/', CourseDividedInUpdateAPIView.as_view(), name='coursedividedin-update'),
    path('coursedividedin/delete/', CourseDividedInDeleteAPIView.as_view(), name='coursedividedin-delete'),
    path('coursedividedin/export/', CourseDividedInExportAPIView.as_view(), name='coursedividedin-export'),
    path('coursedividedin/import/', CourseDividedInImportAPIView.as_view(), name='coursedividedin-import'),

    path('course-durations/', CourseDurationListAPIView.as_view(), name='course-duration-list'),
    path('course-durations/create/', CourseDurationCreateAPIView.as_view(), name='course-duration-create'),
    path('course-durations/<uuid:uuid>/', CourseDurationRetrieveAPIView.as_view(), name='course-duration-retrieve'),
    path('course-durations/<uuid:uuid>/update/', CourseDurationUpdateAPIView.as_view(), name='course-duration-update'),
    path('course-durations/delete/', CourseDurationDeleteAPIView.as_view(), name='course-duration-delete-bulk'),
    path('course-durations/export/', CourseDurationExportAPIView.as_view(), name='course-duration-export'),
    path('course-durations/import/', CourseDurationImportAPIView.as_view(), name='course-duration-import'),


    path('course-level/', CourseLevelListAPIView.as_view(), name='course-Level-list'),
    path('course-level/create/', CourseLevelCreateAPIView.as_view(), name='course-Level-create'),
    path('course-level/<uuid:uuid>/',CourseLevelRetrieveAPIView.as_view(), name='course-Level-retrieve'),
    path('course-level/<uuid:uuid>/update/', CourseLevelUpdateAPIView.as_view(), name='course-Level-update'),
    path('course-level/delete/', CourseLevelDeleteAPIView.as_view(), name='course-Level-delete-bulk'),
    path('course-level/export/', CourseLevelExportAPIView.as_view(), name='course-Level-export'),
    path('course-level/import/', CourseLevelImportAPIView.as_view(), name='course-Level-import'),



    # ------------------ CourseStatus ------------------
    path('coursestatus/', CourseStatusListAPIView.as_view(), name='coursestatus-list'),
    path('coursestatus/create/', CourseStatusCreateAPIView.as_view(), name='coursestatus-create'),
    path('coursestatus/<uuid:uuid>/', CourseStatusRetrieveAPIView.as_view(), name='coursestatus-retrieve'),
    path('coursestatus/<uuid:uuid>/update/', CourseStatusUpdateAPIView.as_view(), name='coursestatus-update'),
    path('coursestatus/delete/', CourseStatusDeleteAPIView.as_view(), name='coursestatus-delete'),
    path('coursestatus/export/', CourseStatusExportAPIView.as_view(), name='coursestatus-export'),
    path('coursestatus/import/', CourseStatusImportAPIView.as_view(), name='coursestatus-import'),

    # ------------------ IntakeName ------------------
    path('intakename/', IntakeNameListAPIView.as_view(), name='intakename-list'),
    path('intakename/create/', IntakeNameCreateAPIView.as_view(), name='intakename-create'),
    path('intakename/<uuid:uuid>/', IntakeNameRetrieveAPIView.as_view(), name='intakename-retrieve'),
    path('intakename/<uuid:uuid>/update/', IntakeNameUpdateAPIView.as_view(), name='intakename-update'),
    path('intakename/delete/', IntakeNameDeleteAPIView.as_view(), name='intakename-delete'),
    path('intakename/export/', IntakeNameExportAPIView.as_view(), name='intakename-export'),
    path('intakename/import/', IntakeNameImportAPIView.as_view(), name='intakename-import'),

    # ------------------ CourseStatusIntake ------------------
    path('coursestatusintake/', CourseStatusIntakeListAPIView.as_view(), name='coursestatusintake-list'),
    path('coursestatusintake/create/', CourseStatusIntakeCreateAPIView.as_view(), name='coursestatusintake-create'),
    path('coursestatusintake/<uuid:uuid>/', CourseStatusIntakeRetrieveAPIView.as_view(), name='coursestatusintake-retrieve'),
    path('coursestatusintake/<uuid:uuid>/update/', CourseStatusIntakeUpdateAPIView.as_view(), name='coursestatusintake-update'),
    path('coursestatusintake/delete/', CourseStatusIntakeDeleteAPIView.as_view(), name='coursestatusintake-delete'),
    path('coursestatusintake/export/', CourseStatusIntakeExportAPIView.as_view(), name='coursestatusintake-export'),
    path('coursestatusintake/import/', CourseStatusIntakeImportAPIView.as_view(), name='coursestatusintake-import'),

    # ------------------ ScholorshipBasedOn ------------------
    path('scholorshipbasedon/', ScholorshipBasedOnListAPIView.as_view(), name='scholorshipbasedon-list'),
    path('scholorshipbasedon/create/', ScholorshipBasedOnCreateAPIView.as_view(), name='scholorshipbasedon-create'),
    path('scholorshipbasedon/<uuid:uuid>/', ScholorshipBasedOnRetrieveAPIView.as_view(), name='scholorshipbasedon-retrieve'),
    path('scholorshipbasedon/<uuid:uuid>/update/', ScholorshipBasedOnUpdateAPIView.as_view(), name='scholorshipbasedon-update'),
    path('scholorshipbasedon/delete/', ScholorshipBasedOnDeleteAPIView.as_view(), name='scholorshipbasedon-delete'),
    path('scholorshipbasedon/export/', ScholorshipBasedOnExportAPIView.as_view(), name='scholorshipbasedon-export'),
    path('scholorshipbasedon/import/', ScholorshipBasedOnImportAPIView.as_view(), name='scholorshipbasedon-import'),

    #----------------------study-Factor------------------------
    path('factor-for/', FactorForListAPIView.as_view(), name='factorfor-list'),
    path('factor-for/create/', FactorForCreateAPIView.as_view(), name='factorfor-create'),
    path('factor-for/<uuid:uuid>/', FactorForRetrieveAPIView.as_view(), name='factorfor-retrieve'),
    path('factor-for/<uuid:uuid>/update/', FactorForUpdateAPIView.as_view(), name='factorfor-update'),
    path('factor-for/delete/', FactorForDeleteAPIView.as_view(), name='factorfor-delete'),
    path('factor-for/<uuid:uuid>/delete/', FactorForDeleteAPIView.as_view(), name='factorfor-delete-single'),
    path('factor-for/export/', FactorForExportAPIView.as_view(), name='factorfor-export'),
    path('factor-for/import/', FactorForImportAPIView.as_view(), name='factorfor-import'),

    path('age-groups/', AgeGroupListAPIView.as_view(), name='agegroup-list'),
    path('age-groups/create/', AgeGroupCreateAPIView.as_view(), name='agegroup-create'),
    path('age-groups/<uuid:uuid>/', AgeGroupRetrieveAPIView.as_view(), name='agegroup-retrieve'),
    path('age-groups/<uuid:uuid>/update/', AgeGroupUpdateAPIView.as_view(), name='agegroup-update'),
    path('age-groups/delete/', AgeGroupDeleteAPIView.as_view(), name='agegroup-delete'),
    path('age-groups/<uuid:uuid>/delete/', AgeGroupDeleteAPIView.as_view(), name='agegroup-delete-single'),
    path('age-groups/export/', AgeGroupExportAPIView.as_view(), name='agegroup-export'),
    path('age-groups/import/', AgeGroupImportAPIView.as_view(), name='agegroup-import'),


    path('academic-result-groups/', AcademicResultGroupListAPIView.as_view(), name='academicresultgroup-list'),
    path('academic-result-groups/create/', AcademicResultGroupCreateAPIView.as_view(), name='academicresultgroup-create'),
    path('academic-result-groups/<uuid:uuid>/', AcademicResultGroupRetrieveAPIView.as_view(), name='academicresultgroup-retrieve'),
    path('academic-result-groups/<uuid:uuid>/update/', AcademicResultGroupUpdateAPIView.as_view(), name='academicresultgroup-update'),
    path('academic-result-groups/delete/', AcademicResultGroupDeleteAPIView.as_view(), name='academicresultgroup-delete'),
    path('academic-result-groups/export/', AcademicResultGroupExportAPIView.as_view(), name='academicresultgroup-export'),
    path('academic-result-groups/import/', AcademicResultGroupImportAPIView.as_view(), name='academicresultgroup-import'),



    path('backlogs-group/list/', BacklogsGroupListAPIView.as_view(), name='backlogsgroup-list'),
    path('backlogs-group/create/', BacklogsGroupCreateAPIView.as_view(), name='backlogsgroup-create'),
    path('backlogs-group/<uuid:uuid>/', BacklogsGroupRetrieveAPIView.as_view(), name='backlogsgroup-retrieve'),
    path('backlogs-group/<uuid:uuid>/update/', BacklogsGroupUpdateAPIView.as_view(), name='backlogsgroup-update'),
    path('backlogs-group/delete/', BacklogsGroupDeleteAPIView.as_view(), name='backlogsgroup-delete'),
    path('backlogs-group/<uuid:uuid>/delete/', BacklogsGroupDeleteAPIView.as_view(), name='backlogsgroup-delete-single'),
    path('backlogs-group/export/', BacklogsGroupExportAPIView.as_view(), name='backlogsgroup-export'),
    path('backlogs-group/import/', BacklogsGroupImportAPIView.as_view(), name='backlogsgroup-import'),

    # ---------------- GAPGroup ----------------
    path('gap-group/list/', GAPGroupListAPIView.as_view(), name='gapgroup-list'),
    path('gap-group/create/', GAPGroupCreateAPIView.as_view(), name='gapgroup-create'),
    path('gap-group/<uuid:uuid>/', GAPGroupRetrieveAPIView.as_view(), name='gapgroup-retrieve'),
    path('gap-group/<uuid:uuid>/update/', GAPGroupUpdateAPIView.as_view(), name='gapgroup-update'),
    path('gap-group/delete/', GAPGroupDeleteAPIView.as_view(), name='gapgroup-delete'),
    path('gap-group/<uuid:uuid>/delete/', GAPGroupDeleteAPIView.as_view(), name='gapgroup-delete-single'),
    path('gap-group/export/', GAPGroupExportAPIView.as_view(), name='gapgroup-export'),
    path('gap-group/import/', GAPGroupImportAPIView.as_view(), name='gapgroup-import'),

    # ---------------- LanguageAbilityGroup ----------------
    path('language-ability-group/list/', LanguageAbilityGroupListAPIView.as_view(), name='languageabilitygroup-list'),
    path('language-ability-group/create/', LanguageAbilityGroupCreateAPIView.as_view(), name='languageabilitygroup-create'),
    path('language-ability-group/<uuid:uuid>/', LanguageAbilityGroupRetrieveAPIView.as_view(), name='languageabilitygroup-retrieve'),
    path('language-ability-group/<uuid:uuid>/update/', LanguageAbilityGroupUpdateAPIView.as_view(), name='languageabilitygroup-update'),
    path('language-ability-group/delete/', LanguageAbilityGroupDeleteAPIView.as_view(), name='languageabilitygroup-delete'),
    path('language-ability-group/<uuid:uuid>/delete/', LanguageAbilityGroupDeleteAPIView.as_view(), name='languageabilitygroup-delete-single'),
    path('language-ability-group/export/', LanguageAbilityGroupExportAPIView.as_view(), name='languageabilitygroup-export'),
    path('language-ability-group/import/', LanguageAbilityGroupImportAPIView.as_view(), name='languageabilitygroup-import'),

    # ---------------- EntranceTestAbilityGroup ----------------
    path('entrance-test-ability-group/list/', EntranceTestAbilityGroupListAPIView.as_view(), name='entrancetestabilitygroup-list'),
    path('entrance-test-ability-group/create/', EntranceTestAbilityGroupCreateAPIView.as_view(), name='entrancetestabilitygroup-create'),
    path('entrance-test-ability-group/<uuid:uuid>/', EntranceTestAbilityGroupRetrieveAPIView.as_view(), name='entrancetestabilitygroup-retrieve'),
    path('entrance-test-ability-group/<uuid:uuid>/update/', EntranceTestAbilityGroupUpdateAPIView.as_view(), name='entrancetestabilitygroup-update'),
    path('entrance-test-ability-group/delete/', EntranceTestAbilityGroupDeleteAPIView.as_view(), name='entrancetestabilitygroup-delete'),
    path('entrance-test-ability-group/<uuid:uuid>/delete/', EntranceTestAbilityGroupDeleteAPIView.as_view(), name='entrancetestabilitygroup-delete-single'),
    path('entrance-test-ability-group/export/', EntranceTestAbilityGroupExportAPIView.as_view(), name='entrancetestabilitygroup-export'),
    path('entrance-test-ability-group/import/', EntranceTestAbilityGroupImportAPIView.as_view(), name='entrancetestabilitygroup-import'),


    path('study-factor-age/create/', StudyFactorAgeCreateAPIView.as_view(),name='age-create'),
    path('study-factor-age/list/', StudyFactorAgeListAPIView.as_view(),name='age-list'),
    path('study-factor-age/<uuid:uuid>/', StudyFactorAgeRetrieveAPIView.as_view(),name='age-retrieve'),
    path('study-factor-age/<uuid:uuid>/update/', StudyFactorAgeUpdateAPIView.as_view(),name='age-update'),
    path('study-factor-age/<uuid:uuid>/delete/', StudyFactorAgeDeleteAPIView.as_view(),name='age-delete'),
    path('study-factor-age/export/', StudyFactorAgeExportAPIView.as_view(),name='age-export'),
    path('study-factor-age/import/', StudyFactorAgeImportAPIView.as_view(),name='age-import'),



    path('academic-result/list/', StudyFactorAcademicResultListAPIView.as_view(), name='academic-result-list'),
    path('academic-result/create/', StudyFactorAcademicResultCreateAPIView.as_view(), name='academic-result-create'),
    path('academic-result/detail/<uuid:uuid>/', StudyFactorAcademicResultRetrieveAPIView.as_view(), name='academic-result-retrieve'),
    path('academic-result/<uuid:uuid>/update/', StudyFactorAcademicResultUpdateAPIView.as_view(), name='academic-result-update'),
    path('academic-result/<uuid:uuid>/delete/', StudyFactorAcademicResultDeleteAPIView.as_view(), name='academic-result-delete'),
    path('academic-result/<uuid:uuid>/export/', StudyFactorAcademicResultExportAPIView.as_view(), name='academic-result-export'),
    path('academic-result/<uuid:uuid>/import/', StudyFactorAcademicResultImportAPIView.as_view(), name='academic-result-import'),
    



    path('study-factor-backlogs/list/',StudyFactorBacklogsListAPIView.as_view(),name="study_factor_backlogs_list"),
    path('study-factor-backlogs/create/',StudyFactorBacklogsCreateAPIView.as_view(),name="study_factor_backlogs_create"),
    path('study-factor-backlogs/<uuid:uuid>/',StudyFactorBacklogsRetrieveAPIView.as_view(),name="study_factor_backlogs_retrieve"),
    path('study-factor-backlogs/delete/', StudyFactorBacklogsDeleteAPIView.as_view(), name="study_factor_backlogs_delete_bulk"),
    path('study-factor-backlogs/export/', StudyFactorBacklogsExportAPIView.as_view(), name="study_factor_backlogs_export"),
    path('study-factor-backlogs/import/', StudyFactorBacklogsImportAPIView.as_view(), name="study_factor_backlogs_import"),


    path('study-factor-gap/list/', StudyFactorGAPListAPIView.as_view(), name="study_factor_gap_list"),
    path('study-factor-gap/create/', StudyFactorGAPCreateAPIView.as_view(), name="study_factor_gap_create"),
    path('study-factor-gap/<uuid:uuid>/', StudyFactorGAPRetrieveAPIView.as_view(), name="study_factor_gap_retrieve"),
    path('study-factor-gap/update/<uuid:uuid>/', StudyFactorGAPUpdateAPIView.as_view(), name="study_factor_gap_update"),
    path('study-factor-gap/delete/<uuid:uuid>/', StudyFactorGAPDeleteAPIView.as_view(), name="study_factor_gap_delete"),
    path('study-factor-gap/export/', StudyFactorGAPExportAPIView.as_view(), name="study_factor_gap_export"),
    path('study-factor-gap/import/', StudyFactorGAPImportAPIView.as_view(), name="study_factor_gap_import"),

    path('study-factor-language-ability/', StudyFactorLanguageAbilityListAPIView.as_view()),
    path('study-factor-language-ability/create/', StudyFactorLanguageAbilityCreateAPIView.as_view()),
    path('study-factor-language-ability/<uuid:uuid>/', StudyFactorLanguageAbilityRetrieveAPIView.as_view()),
    path('study-factor-language-ability/<uuid:uuid>/update/', StudyFactorLanguageAbilityUpdateAPIView.as_view()),
    path('study-factor-language-ability/delete/', StudyFactorLanguageAbilityDeleteAPIView.as_view()),
    path('study-factor-language-ability/export/', StudyFactorLanguageAbilityExportAPIView.as_view(), name='studyfactor-languageability-export'),
    path('study-factor-language-ability/import/', StudyFactorLanguageAbilityImportAPIView.as_view(), name='studyfactor-languageability-import'),


    path('study-factor-entrance-test-ability/', StudyFactorEntranceTestAbilityListAPIView.as_view()),
    path('study-factor-entrance-test-ability/create/', StudyFactorEntranceTestAbilityCreateAPIView.as_view()),
    path('study-factor-entrance-test-ability/<uuid:uuid>/', StudyFactorEntranceTestAbilityRetrieveAPIView.as_view()),
    path('study-factor-entrance-test-ability/update/<uuid:uuid>/', StudyFactorEntranceTestAbilityUpdateAPIView.as_view()),
    path('study-factor-entrance-test-ability/delete/', StudyFactorEntranceTestAbilityDeleteAPIView.as_view()),
    path('study-factor-entrance-test-ability/export/', StudyFactorEntranceTestAbilityExportAPIView.as_view()),
    path('study-factor-entrance-test-ability/import/', StudyFactorEntranceTestAbilityImportAPIView.as_view()),

]

