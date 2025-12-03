from django.contrib import admin
from lead.models import *

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "lead_id",
        "first_name",
        "last_name",
        "email",
        "mobile_number",
        "lead_for",
        "lead_datetime",
        "created_at",
    )

    list_filter = (
        "lead_for",
        "gender",
        "marital_status",
        "along_with",
        "country_of_citizenship",
        "country_of_residency",
        "test_exam_name",
    )

    search_fields = ("lead_id", "first_name", "last_name", "email", "mobile_number")

    readonly_fields = ("id", "uuid", "created_at", "updated_at")

    filter_horizontal = ("interested_visa_categories", "interested_countries")

    fieldsets = (
        ("Lead Information", {
            "fields": ("lead_datetime", "lead_id", "lead_for")
        }),
        ("Personal Details", {
            "fields": ("first_name", "last_name", "gender", "date_of_birth", "marital_status", "along_with")
        }),
        ("Citizenship & Residency", {
            "fields": ("country_of_citizenship", "country_of_residency", "residency_status")  
        }),
        ("Contact Details", {
            "fields": ("mobile_country_code", "mobile_number", "whatsapp_country_code", "whatsapp_number", "email")
        }),
        ("Address Details", {
            "fields": ("address_line_1", "address_line_2", "landmark_area", "country", "state", "district", "city", "village", "pin_zip")
        }),
        ("Interest Details", {
            "fields": ("test_exam_name", "interested_visa_categories", "interested_countries")
        }),
        ("System Fields", {
            "fields": ("id", "uuid", "created_at", "updated_at")
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            "interested_visa_categories",
            "interested_countries"
        )



@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    # Important columns in list view
    list_display = (
    'id',
    'applicant',
    'education_level',
    'education_type',
    'country',
    'state',
    'created_at',
    )

    # Useful filters
    list_filter = (
        'education_level',
        'education_type',
        'country',
    )

    # Searchable fields
    search_fields = (
        'applicant__first_name',
        'applicant__last_name',
        'education_level__name',
        'education_type__name',
        'country__name',
    )

    # Read-only fields for display
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # Minimal fieldsets
    fieldsets = (
        ('Applicant & Education', {
            'fields': (
                'applicant',
                'education_level',
                'education_type',
                'education_duration',
            )
        }),
        ('Location', {
            'fields': (
                'country',
                'state',
            )
        }),
        ('Results & Medium', {
            'fields': (
                'medium_of_education',
                'academic_result_type',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    # Important columns in list view
    list_display = (
    'id',
    'applicant',
    'employer_name',
    'designation',
    'country',
    'state',
    'job_start_date',
    'job_end_date',
    'monthly_salary',
    'created_at',
    )

    # Useful filters
    list_filter = (
        'country',
        'state',
        'designation',
        'job_type',
    )

    # Searchable fields
    search_fields = (
        'applicant__first_name',
        'applicant__last_name',
        'employer_name',
        'designation__name',
    )

    # Read-only fields
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # Minimal fieldsets for clean admin form
    fieldsets = (
        ('Applicant & Job Info', {
            'fields': (
                'applicant',
                'consider',
                'employer_name',
                'designation',
                'job_type',
            )
        }),
        ('Location', {
            'fields': (
                'country',
                'state',
            )
        }),
        ('Salary & ITR', {
            'fields': (
                'monthly_salary',
                'salary_amount',
                'salary_mode',
                'currency',
                'itr_status',
                'years',
                'months',
                'days',
                'amount_numeric',
            )
        }),
        ('Job Duration', {
            'fields': (
                'job_start_date',
                'job_end_date',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(LanguageAbility)
class LanguageAbilityAdmin(admin.ModelAdmin):
# Important columns in list view
    list_display = (
    'id',
    'applicant',
    'language',
    'test_name',
    'test_level',
    'overall_score',
    'test_date',
    'first_or_second_language',
    'created_at',
    )

    # Useful filters
    list_filter = (
        'language',
        'test_level',
        'first_or_second_language',
    )

    # Searchable fields
    search_fields = (
        'applicant__first_name',
        'applicant__last_name',
        'language__name',
        'test_name',
    )

    # Read-only fields
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # Minimal fieldsets for organized admin form
    fieldsets = (
        ('Applicant & Language', {
            'fields': (
                'applicant',
                'language',
                'consider',
                'first_or_second_language',
            )
        }),
        ('Test Details', {
            'fields': (
                'test_name',
                'test_short_name',
                'test_level',
                'listening_score',
                'speaking_score',
                'reading_score',
                'writing_score',
                'overall_score',
                'test_date',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(EntranceTestAbility)
class EntranceTestAbilityAdmin(admin.ModelAdmin):
# Important columns in list view
    list_display = (
    'id',
    'applicant',
    'appeared_test',
    'entrance_test_name',
    'total_score',
    'test_date',
    'created_at',
    )

    # Useful filters
    list_filter = (
        'appeared_test',
        'entrance_test_name',
    )

    # Searchable fields
    search_fields = (
        'applicant__first_name',
        'applicant__last_name',
        'entrance_test_name',
    )

    # Read-only fields
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # Minimal fieldsets for organized admin form
    fieldsets = (
        ('Applicant & Test Info', {
            'fields': (
                'applicant',
                'appeared_test',
                'entrance_test_name',
                'entrance_test_short_name',
            )
        }),
        ('Test Scores', {
            'fields': (
                'module_01_score',
                'module_02_score',
                'module_03_score',
                'total_score',
                'test_date',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Relative)
class RelativeAdmin(admin.ModelAdmin):
# Important columns in list view
    list_display = (
    'id',
    'applicant',
    'applicant_type',
    'relation',
    'country',
    'state',
    'city',
    'visa_category',
    'created_at',
    )

    # Useful filters
    list_filter = (
        'applicant_type',
        'relation',
        'country',
        'state',
    )

    # Searchable fields
    search_fields = (
        'applicant__first_name',
        'applicant__last_name',
        'relation__name',
    )

    # Read-only fields
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # Minimal fieldsets for organized admin form
    fieldsets = (
        ('Applicant & Relation', {
            'fields': (
                'applicant',
                'applicant_type',
                'relation',
                'visa_category',
            )
        }),
        ('Location', {
            'fields': (
                'country',
                'state',
                'city',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(VisitHistory)
class VisitHistoryAdmin(admin.ModelAdmin):
# Important columns in list view
    list_display = (
    'id',
    'applicant',
    'applicant_type',
    'country',
    'visa_category',
    'issue_date',
    'travel_from',
    'travel_to',
    'purpose_of_visit',
    'created_at',
    )

    # Useful filters
    list_filter = (
        'applicant_type',
        'country',
        'visa_category',
        'purpose_of_visit',
    )

    # Searchable fields
    search_fields = (
        'applicant__first_name',
        'applicant__last_name',
        'visa_category__name',
    )

    # Read-only fields
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # Minimal fieldsets for organized admin form
    fieldsets = (
        ('Applicant & Visa Info', {
            'fields': (
                'applicant',
                'applicant_type',
                'country',
                'visa_category',
                'purpose_of_visit',
            )
        }),
        ('Travel Dates', {
            'fields': (
                'issue_date',
                'travel_from',
                'travel_to',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(RefusalHistory)
class RefusalHistoryAdmin(admin.ModelAdmin):
# Important columns in list view
    list_display = (
    'id',
    'applicant',
    'applicant_type',
    'country',
    'visa_category',
    'refusal_date',
    'created_at',
    )

    # Useful filters
    list_filter = (
        'applicant_type',
        'country',
        'visa_category',
    )

    # Searchable fields
    search_fields = (
        'applicant__first_name',
        'applicant__last_name',
        'visa_category__name',
    )

    # Read-only fields
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # Minimal fieldsets for organized admin form
    fieldsets = (
        ('Applicant & Visa Info', {
            'fields': (
                'applicant',
                'applicant_type',
                'country',
                'visa_category',
            )
        }),
        ('Refusal Details', {
            'fields': (
                'refusal_date',
                'refusal_reason',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
@admin.register(BusinessExperience)
class BusinessExperienceAdmin(admin.ModelAdmin):
# Columns to display in admin list view
    list_display = (
    'id',
    'applicant',
    'company_name',
    'company_type',
    'country',
    'share_percent',
    'start_date',
    'end_date',
    'turnover',
    'created_at',
    )

    # Filters in sidebar
    list_filter = (
        'country',
        'company_type',
    )

    # Searchable fields
    search_fields = (
        'applicant__first_name',
        'applicant__last_name',
        'company_name',
    )

    # Read-only fields
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # Organized form sections
    fieldsets = (
        ('Applicant & Company Info', {
            'fields': (
                'applicant',
                'company_name',
                'company_type',
                'country',
                'share_percent',
            )
        }),
        ('Business Duration & Turnover', {
            'fields': (
                'start_date',
                'end_date',
                'turnover',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Networth)
class NetworthAdmin(admin.ModelAdmin):
# Columns to display in admin list view
    list_display = (
    'id',
    'applicant',
    'applicant_type',
    'country',
    'currency',
    'immovable_property',
    'movable_property',
    'liquid_amount',
    'total_networth',
    'created_at',
    )

    # Filters in sidebar
    list_filter = (
        'applicant_type',
        'country',
        'currency',
    )

    # Searchable fields
    search_fields = (
        'applicant__first_name',
        'applicant__last_name',
    )

    # Read-only fields
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # Organized form sections
    fieldsets = (
        ('Applicant & Location', {
            'fields': (
                'applicant',
                'applicant_type',
                'country',
                'currency',
            )
        }),
        ('Assets & Networth', {
            'fields': (
                'immovable_property',
                'movable_property',
                'liquid_amount',
                'total_networth',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(EligibilityFlags)
class EligibilityFlagsAdmin(admin.ModelAdmin):
# Columns to display in admin list view
    list_display = (
    'id',
    'applicant',
    'trade_certificate',
    'educational_credential_assessment',
    'ita_province',
    'tech_startup_founder',
    'reside_outside_greater_city',
    'created_at',
    )

    # Filters in sidebar
    list_filter = (
        'trade_certificate',
        'educational_credential_assessment',
        'ita_province',
        'tech_startup_founder',
        'reside_outside_greater_city',
    )

    # Searchable fields
    search_fields = (
        'applicant__first_name',
        'applicant__last_name',
    )

    # Read-only fields
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # Organized form sections
    fieldsets = (
        ('Applicant & Flags', {
            'fields': (
                'applicant',
                'trade_certificate',
                'educational_credential_assessment',
                'ita_province',
                'tech_startup_founder',
                'reside_outside_greater_city',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )