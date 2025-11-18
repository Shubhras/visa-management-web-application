from django.contrib import admin
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


# @admin.register(AccreditationName)
# class AccreditationNameAdmin(admin.ModelAdmin):
#     list_display = ('full_name', 'short_name', 'country', 'category', 'issuing_authority', 'valid_upto', 'is_deleted', 'created_at', 'updated_at')
#     search_fields = ('full_name', 'short_name', 'issuing_authority')
#     list_filter = ('is_deleted', 'country', 'category')
#     ordering = ('full_name',)
#     autocomplete_fields = ('country', 'category')


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
    list_display = ('Academicresult', 'AcademicResulttype', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('Academicresult', 'description', 'AcademicResulttype__name')
    list_filter = ('AcademicResulttype', 'is_deleted')


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



@admin.register(RepresentingCountry)
class RepresentingCountryAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'short_name', 'continent', 'status', 'is_active', 'is_deleted')
    search_fields = ('full_name', 'short_name', 'country__name')
    list_filter = ('continent', 'status', 'is_active', 'is_deleted')

@admin.register(OccupationVersion)
class OccupationVersionAdmin(admin.ModelAdmin):
    list_display = ('occupation_version', 'country', 'effect_from', 'valid_upto', 'is_deleted', 'created_at')
    search_fields = ('occupation_version',)
    list_filter = ('country', 'is_deleted')

@admin.register(OccupationCategory)
class OccupationCategoryAdmin(admin.ModelAdmin):
    list_display = ('occupationcategory', 'occupationversion', 'country', 'occupationcategorycode', 'is_deleted')
    search_fields = ('occupationcategory', 'occupationcategorycode')
    list_filter = ('country', 'occupationversion', 'is_deleted')

@admin.register(OccupationLevelCode)
class OccupationLevelCodeAdmin(admin.ModelAdmin):
    list_display = ('occupationlevelcode', 'occupationversion', 'country', 'is_deleted')
    search_fields = ('occupationlevelcode',)
    list_filter = ('country', 'occupationversion', 'is_deleted')

@admin.register(OccupationLevel)
class OccupationLevelAdmin(admin.ModelAdmin):
    list_display = ('occupationlevel', 'occupationcategory', 'occupationlevelcode', 'occupationversion', 'country', 'is_deleted')
    search_fields = ('occupationlevel',)
    list_filter = ('country', 'occupationversion', 'occupationcategory', 'occupationlevelcode', 'is_deleted')

@admin.register(OccupationCode)
class OccupationCodeAdmin(admin.ModelAdmin):
    list_display = ('occupationcode', 'occupationversion', 'country', 'is_deleted')
    search_fields = ('occupationcode',)
    list_filter = ('country', 'occupationversion', 'is_deleted')

@admin.register(OccupationName)
class OccupationNameAdmin(admin.ModelAdmin):
    list_display = ('occupationname', 'occupationcategory', 'occupationlevel', 'occupationlevelcode', 'occupationcode', 'occupationversion', 'country', 'is_deleted')
    search_fields = ('occupationname',)
    list_filter = ('country', 'occupationversion', 'occupationcategory', 'occupationlevel', 'occupationlevelcode', 'occupationcode', 'is_deleted')

@admin.register(OccupationType)
class OccupationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)

@admin.register(OccupationProspect)
class OccupationProspectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('designation', 'occupationname', 'occupationcode', 'occupationversion', 'country', 'is_deleted')
    search_fields = ('designation',)
    list_filter = ('country', 'occupationversion', 'occupationname', 'occupationcode', 'is_deleted')

@admin.register(JobProspect)
class JobProspectAdmin(admin.ModelAdmin):
    list_display = ('occupationname', 'occupationtype', 'occupationlevelcode', 'salaryamount', 'salarycurrency', 'duration', 'country', 'is_deleted')
    search_fields = ('occupationname',)
    list_filter = ('country', 'occupationversion', 'occupationtype', 'occupationlevelcode', 'is_deleted')

@admin.register(RelatedOccupation)
class RelatedOccupationAdmin(admin.ModelAdmin):
    list_display = ('relatedoccupation', 'occupationname', 'occupationcode', 'occupationversion', 'country', 'is_deleted')
    search_fields = ('relatedoccupation',)
    list_filter = ('country', 'occupationversion', 'occupationcode', 'occupationname', 'is_deleted')

@admin.register(OccupationToOccupation)
class OccupationToOccupationAdmin(admin.ModelAdmin):
    list_display = ('country', 'occupationname', 'occupationcode', 'occupationversion', 'comparecountry', 'compareoccupationname', 'compareoccupationcode', 'compareoccupationversion', 'is_deleted')
    search_fields = ('country__full_name', 'comparecountry__full_name')
    list_filter = ('country', 'comparecountry', 'occupationversion', 'compareoccupationversion', 'is_deleted')


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



@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('is_deleted', 'created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(LanguageTest)
class LanguageTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'fullname', 'language', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name', 'fullname', 'description', 'language__name')
    list_filter = ('is_deleted', 'created_at', 'updated_at', 'language')
    ordering = ('-created_at',)



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
