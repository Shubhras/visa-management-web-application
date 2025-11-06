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


@admin.register(AccreditationName)
class AccreditationNameAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'short_name', 'country', 'category', 'issuing_authority', 'valid_upto', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('full_name', 'short_name', 'issuing_authority')
    list_filter = ('is_deleted', 'country', 'category')
    ordering = ('full_name',)
    autocomplete_fields = ('country', 'category')


# ---------- BANK & LICENSE ----------
@admin.register(BankAccountType)
class BankAccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(LicenseName)
class LicenseNameAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'short_name', 'country', 'issuing_authority', 'valid_upto', 'is_deleted', 'created_at', 'updated_at')
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
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)


@admin.register(EducationLevel)
class EducationLevelAdmin(admin.ModelAdmin):
    list_display = ('level_code', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('level_code__level_code',)
    list_filter = ('is_deleted',)
    ordering = ('level_code__level_code',)
    autocomplete_fields = ('level_code',)


@admin.register(EducationDuration)
class EducationDurationAdmin(admin.ModelAdmin):
    list_display = ('durations', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('durations',)
    list_filter = ('is_deleted',)
    ordering = ('durations',)

@admin.register(Studymainarea)
class StudymainareaAdmin(admin.ModelAdmin):
    list_display = ('uuid','name', 'description', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_deleted',)
    ordering = ('name',)

@admin.register(Studymajorarea)
class StudymajorareaAdmin(admin.ModelAdmin):
    list_display = ('uuid','mainarea', 'description', 'majorarea','is_deleted', 'created_at', 'updated_at')
    search_fields = ('majorarea',)
    list_filter = ('is_deleted',)
    ordering = ('majorarea',)