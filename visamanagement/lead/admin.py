from django.contrib import admin
from .models import Applicant

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
