from django.contrib import admin # type: ignore
from master.models import *


# ---------- BASIC MODELS ----------
@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_active', 'is_deleted')
    ordering = ('name',)


@admin.register(Maritalstatus)
class MaritalstatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_active', 'is_deleted')
    ordering = ('name',)


# ---------- LOCATION MODELS ----------
@admin.register(Continents)
class ContinentsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_active', 'is_deleted')
    ordering = ('name',)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'continent', 'capitalCity', 'currencyCode', 'status', 'is_active', 'is_deleted')
    search_fields = ('name', 'capitalCity', 'currencyCode')
    list_filter = ('continent', 'is_active', 'is_deleted', 'status')
    ordering = ('name',)
    autocomplete_fields = ('continent',)


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('stateName', 'countryName', 'stateshortName', 'description', 'is_active', 'is_deleted')
    search_fields = ('stateName', 'stateshortName')
    list_filter = ('is_active', 'is_deleted', 'countryName')
    ordering = ('stateName',)
    autocomplete_fields = ('countryName',)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('districtName', 'stateName', 'countryName', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('districtName',)
    list_filter = ('is_deleted', 'stateName', 'countryName')
    ordering = ('districtName',)
    autocomplete_fields = ('stateName', 'countryName')


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('cityName', 'districtName', 'stateName', 'countryName', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('cityName',)
    list_filter = ('is_deleted', 'stateName', 'countryName', 'districtName')
    ordering = ('cityName',)
    autocomplete_fields = ('countryName', 'stateName', 'districtName')


# ---------- OTHER MASTER MODELS ----------
@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(Timezone)
class TimezoneAdmin(admin.ModelAdmin):
    list_display = ('Timezone', 'countryName', 'stateName', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('Timezone',)
    list_filter = ('is_deleted', 'countryName', 'stateName')
    ordering = ('Timezone',)
    autocomplete_fields = ('countryName', 'stateName')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(EmployeeType)
class EmployeeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(CompanyType)
class CompanyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(OwnershipType)
class OwnershipTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_type', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted', 'company_type')
    ordering = ('name',)
    autocomplete_fields = ('company_type',)


@admin.register(StakeholderCategory)
class StakeholderCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(StakeholderType)
class StakeholderTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted', 'category')
    ordering = ('name',)
    autocomplete_fields = ('category',)

# ---------- ACCREDITATION ----------
@admin.register(AccreditationCategory)
class AccreditationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)



@admin.register(AccreditationName)
class AccreditationNameAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'short_name',
        'country',
        'category',
        'issuing_authority',
        'valid_type',
        'valid_duration_value',
        'valid_duration_unit',
        'valid_date',
        'is_deleted',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'full_name',
        'short_name',
        'issuing_authority',
        'country__name',
        'category__name',
    )

    list_filter = (
        'country',
        'category',
        'valid_type',
        'valid_duration_unit',
        'is_deleted',
    )

    ordering = (
        'full_name',
    )

    readonly_fields = (
        'uuid',
        'created_at',
        'updated_at',
    )



# ---------- BANK & LICENSE ----------
@admin.register(BankAccountType)
class BankAccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(LicenseName)
class LicenseNameAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'short_name', 'country', 'issuing_authority', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('full_name', 'short_name', 'issuing_authority')
    list_filter = ('is_deleted', 'country')
    ordering = ('full_name',)
    autocomplete_fields = ('country',)


# ---------- LEADS & PRIORITY ----------
@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(InterestLevel)
class InterestLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(LostReason)
class LostReasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(LostReasonB2B)
class LostReasonB2BAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


# ---------- EDUCATION ----------
@admin.register(EducationLevelCode)
class EducationLevelCodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('is_deleted', 'created_at')


# -------------------- EducationLevel --------------------
@admin.register(EducationLevel)
class EducationLevelAdmin(admin.ModelAdmin):
    list_display = ('educationlevel', 'level_code', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('educationlevel', 'description', 'level_code__name')
    list_filter = ('level_code', 'is_deleted')


# -------------------- EducationDuration --------------------
@admin.register(EducationDuration)
class EducationDurationAdmin(admin.ModelAdmin):
    list_display = ('durations', 'educationlevel', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('durations', 'description', 'educationlevel__educationlevel')
    list_filter = ('educationlevel', 'is_deleted')


# -------------------- Studymainarea --------------------
@admin.register(Studymainarea)
class StudymainareaAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('is_deleted',)


# -------------------- Studymajorarea --------------------
@admin.register(Studymajorarea)
class StudymajorareaAdmin(admin.ModelAdmin):
    list_display = ('majorarea', 'mainarea', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('majorarea', 'description', 'mainarea__name')
    list_filter = ('mainarea', 'is_deleted')


# -------------------- StudySpecialisation --------------------
@admin.register(StudySpecialisation)
class StudySpecialisationAdmin(admin.ModelAdmin):
    list_display = ('studyspecialisation', 'mainarea', 'majorarea', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('studyspecialisation', 'description', 'mainarea__name', 'majorarea__majorarea')
    list_filter = ('mainarea', 'majorarea', 'is_deleted')


# -------------------- AcademicResultType --------------------
@admin.register(AcademicResultType)
class AcademicResultTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('is_deleted',)


# -------------------- AcademicResult --------------------
@admin.register(AcademicResult)
class AcademicResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'AcademicResulttype', 'Academicresult', 'description', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('AcademicResulttype', 'is_deleted', 'created_at')
    search_fields = ('Academicresult', 'description')
    readonly_fields = ('uuid', 'created_at', 'updated_at')


# -------------------- EducationType --------------------
@admin.register(EducationType)
class EducationTypeAdmin(admin.ModelAdmin):
    list_display = ('educationType', 'Perticulars', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('educationType', 'Perticulars')
    list_filter = ('is_deleted',)


# -------------------- MediumofEducation --------------------
@admin.register(MediumofEducation)
class MediumofEducationAdmin(admin.ModelAdmin):
    list_display = ('name', 'perticulars', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name', 'perticulars')
    list_filter = ('is_deleted',)

# -------------------- ECAAwardingBody --------------------
@admin.register(ECAAwardingBody)
class ECAAwardingBodyAdmin(admin.ModelAdmin):
    list_display = ('eca_body_full_name', 'eca_body_short_name', 'country', 'valid_duration_value', 'created_at', 'updated_at')
    search_fields = ('eca_body_full_name', 'eca_body_short_name', 'country__country_name')


# -------------------- DegreeAwardedBy --------------------
@admin.register(DegreeAwardedBy)
class DegreeAwardedByAdmin(admin.ModelAdmin):
    list_display = ('degree_name', 'country', 'education_level', 'description', 'created_at', 'updated_at')
    search_fields = ('degree_name', 'country__country_name', 'education_level__educationlevel')
    list_filter = ('country', 'education_level')


# -------------------- DegreeAwardedInstitute --------------------
@admin.register(DegreeAwardedInstitute)
class DegreeAwardedInstituteAdmin(admin.ModelAdmin):
    list_display = ('name', 'degree_awarded_by', 'education_level', 'country', 'state', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'degree_awarded_by__degree_name', 'education_level__educationlevel', 'country__country_name', 'state__name')
    list_filter = ('degree_awarded_by', 'education_level', 'country', 'state')



# ---------------------- Language ----------------------
# @admin.register(Language)
# class LanguageAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
#     search_fields = ('name',)
#     list_filter = ('is_deleted',)
#     ordering = ('name',)


# ---------------------- LanguageTest ----------------------
# @admin.register(LanguageTest)
# class LanguageTestAdmin(admin.ModelAdmin):
#     list_display = ('name', 'fullname', 'language', 'description', 'is_deleted', 'created_at', 'updated_at')
#     search_fields = ('name', 'fullname')
#     list_filter = ('is_deleted', 'language')
#     ordering = ('name',)


# ---------------------- LanguagetestmoduleName ----------------------
# @admin.register(LanguagetestmoduleName)
# class LanguagetestmoduleNameAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
#     search_fields = ('name',)
#     list_filter = ('is_deleted',)
#     ordering = ('name',)


# ---------------------- CLBLevel ----------------------
# @admin.register(CLBLevel)
# class CLBLevelAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
#     search_fields = ('name',)
#     list_filter = ('is_deleted',)
#     ordering = ('name',)


# ---------------------- LanguageTestResult ----------------------
@admin.register(LanguageTestResult)
class LanguageTestResultAdmin(admin.ModelAdmin):
    list_display = (
        'language', 'language_test', 'module_name', 'clb_level',
        'numeric_score', 'description', 'is_deleted', 'created_at', 'updated_at'
    )
    search_fields = ('language__name', 'language_test__name', 'module_name__name')
    list_filter = ('is_deleted', 'language', 'language_test', 'module_name', 'clb_level')
    ordering = ('language',)


# ---------------------- StudyLanguageBanchmark ----------------------
@admin.register(StudyLanguageBanchmark)
class StudyLanguageBanchmarkAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


# ---------------------- EntranceTestName ----------------------
@admin.register(EntranceTestName)
class EntranceTestNameAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'shortname', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('fullname', 'shortname')
    list_filter = ('is_deleted',)
    ordering = ('fullname',)


# ---------------------- EntranceTestModuleName ----------------------
@admin.register(EntranceTestModuleName)
class EntranceTestModuleNameAdmin(admin.ModelAdmin):
    list_display = ('entrancetest', 'moduleName', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('moduleName', 'entrancetest__fullname')
    list_filter = ('is_deleted', 'entrancetest')
    ordering = ('moduleName',)


# ---------------------- EntranceTestResult ----------------------
@admin.register(EntranceTestResult)
class EntranceTestResultAdmin(admin.ModelAdmin):
    list_display = ('entrancetest', 'moduleName', 'testresult', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('testresult', 'entrancetest__fullname', 'moduleName__moduleName')
    list_filter = ('is_deleted', 'entrancetest', 'moduleName')
    ordering = ('entrancetest',)


# ---------------------- JobType ----------------------
@admin.register(JobType)
class JobTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


# ---------------------- ModeofSalary ----------------------
@admin.register(ModeofSalary)
class ModeofSalaryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


# ---------------------- ITReturnStatus ----------------------
@admin.register(ITReturnStatus)
class ITReturnStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(OccupationVersion)
class OccupationVersionAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'occupation_version', 'country', 'effect_from', 'valid_upto', 'is_deleted')
    search_fields = ('uuid', 'occupation_version')
    list_filter = ('country', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OccupationCategory)
class OccupationCategoryAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'occupationcategory', 'occupationcategorycode', 'country', 'occupationversion', 'is_deleted')
    search_fields = ('uuid', 'occupationcategory', 'occupationcategorycode')
    list_filter = ('country', 'occupationversion', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OccupationLevelCode)
class OccupationLevelCodeAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'occupationlevelcode', 'country', 'occupationversion', 'is_deleted')
    search_fields = ('uuid', 'occupationlevelcode')
    list_filter = ('country', 'occupationversion', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OccupationLevel)
class OccupationLevelAdmin(admin.ModelAdmin):
    list_display = (
        'uuid',
        'occupationlevel',
        'occupationcategory',
        'occupationlevelcode',
        'country',
        'occupationversion',
        'is_deleted'
    )
    search_fields = ('uuid', 'occupationlevel')
    list_filter = ('country', 'occupationversion', 'occupationcategory', 'occupationlevelcode', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OccupationCode)
class OccupationCodeAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'occupationcode', 'country', 'occupationversion', 'is_deleted')
    search_fields = ('uuid', 'occupationcode')
    list_filter = ('country', 'occupationversion', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OccupationName)
class OccupationNameAdmin(admin.ModelAdmin):
    list_display = (
        'occupationname',
        'country',
        'occupationversion',
        'occupationcategory',
        'occupationlevel',
        'occupationlevelcode',
        'occupationcode',
        'is_deleted',
        'created_at',
        'updated_at'
    )

    search_fields = (
        'occupationname',
        'country__name',
        'occupationcategory__name',
        'occupationcode__name',
    )

    list_filter = (
        'is_deleted',
        'country',
        'occupationversion',
        'occupationcategory',
        'occupationlevel',
        'occupationlevelcode',
        'occupationcode',
    )

    ordering = ('occupationname',)


@admin.register(OccupationType)
class OccupationTypeAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OccupationProspect)
class OccupationProspectAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')



@admin.register(JobProspect)
class JobProspectAdmin(admin.ModelAdmin):
    list_display = (
        'occupationname',
        'country',
        'occupationversion',
        'occupationlevelcode',
        'occupationtype',
        'occupationcode',
        'occupationprospect',
        'salarycurrency',
        'salaryamount',
        'duration',
        'is_deleted',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'occupationname',
        'country__name',
        'occupationtype__name',
        'occupationcode__name',
        'occupationprospect__name',
    )

    list_filter = (
        'is_deleted',
        'country',
        'occupationversion',
        'occupationlevelcode',
        'occupationtype',
        'occupationcode',
        'occupationprospect',
        'duration',
    )

    ordering = ('occupationname',)




@admin.register(RelatedOccupation)
class RelatedOccupationAdmin(admin.ModelAdmin):
    list_display = (
        'relatedoccupation',
        'country',
        'occupationversion',
        'occupationcode',
        'occupationname',
        'is_deleted',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'relatedoccupation',
        'country__name',
        'occupationcode__name',
        'occupationname__occupationname',
    )

    list_filter = (
        'is_deleted',
        'country',
        'occupationversion',
        'occupationcode',
        'occupationname',
    )

    ordering = ('relatedoccupation',)




@admin.register(OccupationToOccupation)
class OccupationToOccupationAdmin(admin.ModelAdmin):
    list_display = (
        'country',
        'occupationversion',
        'occupationcode',
        'occupationname',
        'comparecountry',
        'compareoccupationversion',
        'compareoccupationcode',
        'compareoccupationname',
        'is_deleted',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'country__name',
        'occupationcode__name',
        'occupationname__occupationname',
        'comparecountry__name',
        'compareoccupationcode__name',
        'compareoccupationname__occupationname',
    )

    list_filter = (
        'is_deleted',
        'country',
        'occupationversion',
        'occupationcode',
        'occupationname',
        'comparecountry',
        'compareoccupationversion',
        'compareoccupationcode',
        'compareoccupationname',
    )

    ordering = ('country',)



@admin.register(RepresentingCountry)
class RepresentingCountryAdmin(admin.ModelAdmin):
    list_display = (
        'uuid',
        'country',
        'continent',
        'short_name',
        'full_name',
        'official_name',
        'capital_city',
        'population',
        'status',
        'is_active',
        'is_deleted',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'continent',
        'status',
        'is_active',
        'is_deleted',
        'country',
    )

    search_fields = (
        'uuid',
        'full_name',
        'short_name',
        'official_name',
        'capital_city',
        'country__name',
    )

    ordering = ('-created_at',)
    readonly_fields = ('uuid', 'created_at', 'updated_at')



@admin.register(VisaMain)
class VisaMainAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(VisaMajor)
class VisaMajorAdmin(admin.ModelAdmin):
    list_display = ('name', 'visamain', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name', 'visamain__name')
    list_filter = ('is_deleted', 'visamain')
    ordering = ('name',)



@admin.register(VisaName)
class VisaNameAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'short_name',
        'country',
        'visamain',
        'visamajor',
        'description',
        'is_deleted',
        'created_at',
        'updated_at'
    )

    search_fields = (
        'full_name',
        'short_name',
        'country__country_name',
        'visamain__name',
        'visamajor__name',
    )

    list_filter = (
        'is_deleted',
        'country',
        'visamain',
        'visamajor',
    )

    ordering = ('full_name',)


@admin.register(ApplicantType)
class ApplicantTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)



@admin.register(VisaEligibilityType)
class VisaEligibilityTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)



@admin.register(VisaStatus)
class VisaStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)



@admin.register(PossibilityLevel)
class PossibilityLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)



@admin.register(WorkRights)
class WorkRightsAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WorkRightsDuringStudy)
class WorkRightsDuringStudyAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WorkRightsDuringVacation)
class WorkRightsDuringVacationAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WorkRightsAfterStudy)
class WorkRightsAfterStudyAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PRPossibility)
class PRPossibilityAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')






@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "name",
        "description",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_deleted", "created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ('name',)

@admin.register(DocumentName)
class DocumentNameAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "document_category",
        "document_name",
        "description",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_deleted", "created_at", "updated_at", "document_category")
    search_fields = ("document_name", "description", "document_category__name")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ('document_name',)



@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "name",
        "description",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_deleted", "created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ('name',)


@admin.register(PurposeOfVisit)
class PurposeOfVisitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "name",
        "description",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_deleted", "created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("name",)



@admin.register(DocumentsFor)
class DocumentsForAdmin(admin.ModelAdmin):
    list_display = ("uuid", "name", "description", "is_deleted", "created_at", "updated_at")
    list_filter = ("is_deleted", "created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("name",)



@admin.register(RequiredDocument)
class RequiredDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "country",
        "visa_main_category",
        "visa_major_category",
        "visa_name",
        "document_category",
        "document_name",
        "description",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_deleted", "created_at", "updated_at", "country", "visa_main_category", "visa_major_category")
    search_fields = (
        "country__name",
        "visa_main_category__name",
        "visa_major_category__name",
        "visa_name__name",
        "document_category__name",
        "document_name__document_name",
        "description",
    )
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(ProcessStatusName)
class ProcessStatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "country",
        "visa_main_category",
        "process_status_name",
        "description",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_deleted", "created_at", "updated_at", "country", "visa_main_category")
    search_fields = (
        "country__name",
        "visa_main_category__name",
        "process_status_name__name",
        "description",
    )
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("-created_at",)



@admin.register(ProcessSubStatusName)
class ProcessSubStatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "country",
        "visa_main_category",
        "process_status_name",
        "process_sub_status_name",
        "description",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_deleted", "country", "visa_main_category", "process_status_name")
    search_fields = (
        "country__name",
        "visa_main_category__name",
        "process_status_name__name",
        "process_sub_status_name",
        "description",
    )
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("-created_at",)



@admin.register(ProcessType)
class ProcessTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "name",
        "description",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_deleted", "created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("name",)


@admin.register(PaymentTo)
class PaymentToAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "name",
        "description",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_deleted", "created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("name",)




@admin.register(PaymentCategory)
class PaymentCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id","uuid","payment_to","payment_category","description",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_deleted", "created_at", "updated_at", "payment_to")
    search_fields = ("payment_category", "description", "payment_to__name")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("payment_category",)



@admin.register(CivilIdName)
class CivilIdNameAdmin(admin.ModelAdmin):
    list_display = (
        "civil_id_name",
        "authority_full_name",
        "authority_short_name",
        "valid_type",
        "valid_duration_value",
        "valid_duration_unit",
        "is_deleted",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "civil_id_name",
        "authority_full_name",
        "authority_short_name",
    )

    list_filter = (
        "valid_type",
        "valid_duration_unit",
        # "is_deleted",
    )



@admin.register(SpouseCanApplywithCandidate)
class SpouseCanApplywithCandidateAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SpouseVisaCategory)
class SpouseVisaCategoryAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SpouseWorkRights)
class SpouseWorkRightsAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ChildrenCanApplywithCandidate)
class ChildrenCanApplywithCandidateAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ChildrenVisaCategory)
class ChildrenVisaCategoryAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ChildrenStudyWorkRights)
class ChildrenStudyWorkRightsAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(InstituteType)
class InstituteTypeAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(InstituteGroupName)
class InstituteGroupNameAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(InstituteStatus)
class InstituteStatusAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(InstitutePriority)
class InstitutePriorityAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(InstituteDepartment)
class InstituteDepartmentAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BankAccountFor)
class BankAccountForAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WhenCommissionIssue)
class WhenCommissionIssueAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CourseLevelCode)
class CourseLevelCodeAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CourseLevel)
class CourseLevelAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'courselevelcode', 'is_deleted')
    search_fields = ('uuid', 'name', 'courselevelcode__name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CourseDuration)
class CourseDurationAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'courselevel', 'valid_duration_value', 'valid_duration_unit', 'is_deleted')
    search_fields = ('uuid', 'courselevel__name')
    list_filter = ('is_deleted', 'valid_duration_unit')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CourseDividedIn)
class CourseDividedInAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CourseStatus)
class CourseStatusAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'is_deleted')
    search_fields = ('uuid', 'name')
    list_filter = ('is_deleted',)
    readonly_fields = ('created_at', 'updated_at')
    
    
    
@admin.register(IntakeName)
class IntakeNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)

    
    
@admin.register(CourseStatusIntake)
class CourseStatusIntakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)

    
    
@admin.register(ScholorshipBasedOn)
class ScholorshipBasedOnAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)

        
    
        



@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('is_deleted', 'created_at', 'updated_at')


@admin.register(LanguageTest)
class LanguageTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'fullname', 'language', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name', 'fullname', 'description', 'language__name')
    list_filter = ('is_deleted', 'created_at', 'updated_at', 'language')




@admin.register(LanguagetestmoduleName)
class LanguagetestmoduleNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid','name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('is_deleted', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CLBLevel)
class CLBLevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('is_deleted', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StudyLanguageBanchmark)
class StudyLanguageBanchmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid','name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('is_deleted', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')



@admin.register(FactorFor)
class FactorForAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('is_deleted', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
    
    

@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('is_deleted', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('uuid', 'created_at', 'updated_at')



