

# class EducationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Education
#         exclude = ("id", "created_at", "updated_at")

# class WorkExperienceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WorkExperience
#         exclude = ("id", "created_at", "updated_at")

# class LanguageAbilitySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LanguageAbility
#         exclude = ("id", "created_at", "updated_at")

# class EntranceTestAbilitySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = EntranceTestAbility
#         exclude = ("id", "created_at", "updated_at")

# class RelativeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Relative
#         exclude = ("id", "created_at", "updated_at")

# class VisitHistorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = VisitHistory
#         exclude = ("id", "created_at", "updated_at")

# class RefusalHistorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RefusalHistory
#         exclude = ("id", "created_at", "updated_at")

# # ------------------------------
# # Main Applicant Serializer
# # ------------------------------

# class ApplicantSerializer(serializers.ModelSerializer):
#     educations = EducationSerializer(many=True, required=False)
#     work_experiences = WorkExperienceSerializer(many=True, required=False)
#     language_abilities = LanguageAbilitySerializer(many=True, required=False)
#     entrance_test_abilities = EntranceTestAbilitySerializer(many=True, required=False)
#     relatives = RelativeSerializer(many=True, required=False)
#     visit_history = VisitHistorySerializer(many=True, required=False)
#     refusal_history = RefusalHistorySerializer(many=True, required=False)

#     class Meta:
#         model = Applicant
#         fields = "__all__"

#     # Ensure email and mobile number are unique
#     def validate(self, data):
#         email = data.get("email")
#         mobile_number = data.get("mobile_number")
#         qs = Applicant.objects.all()
#         if self.instance:
#             qs = qs.exclude(pk=self.instance.pk)

#         if qs.filter(email=email).exists():
#             raise serializers.ValidationError({"email": "Email must be unique."})
#         if qs.filter(mobile_number=mobile_number).exists():
#             raise serializers.ValidationError({"mobile_number": "Mobile number must be unique."})
#         return data

#     def create(self, validated_data):
#         nested_fields = [
#             "educations", "work_experiences", "language_abilities",
#             "entrance_test_abilities", "relatives", "visit_history", "refusal_history"
#         ]
#         nested_data = {field: validated_data.pop(field, []) for field in nested_fields}

#         with transaction.atomic():
#             applicant = Applicant.objects.create(**validated_data)

#             for field in nested_fields:
#                 serializer_class = self._get_serializer_class(field)
#                 for item in nested_data[field]:
#                     serializer_class().Meta.model.objects.create(applicant=applicant, **item)
#         return applicant

#     def update(self, instance, validated_data):
#         nested_fields = [
#             "educations", "work_experiences", "language_abilities",
#             "entrance_test_abilities", "relatives", "visit_history", "refusal_history"
#         ]
#         nested_data = {field: validated_data.pop(field, []) for field in nested_fields}

#         with transaction.atomic():
#             for attr, value in validated_data.items():
#                 setattr(instance, attr, value)
#             instance.save()

#             # Optional: Clear old nested data and create new (simpler than diff update)
#             for field in nested_fields:
#                 serializer_class = self._get_serializer_class(field)
#                 instance_data = getattr(instance, field)
#                 instance_data.all().delete()
#                 for item in nested_data[field]:
#                     serializer_class().Meta.model.objects.create(applicant=instance, **item)

#         return instance

#     def _get_serializer_class(self, field_name):
#         mapping = {
#             "educations": EducationSerializer,
#             "work_experiences": WorkExperienceSerializer,
#             "language_abilities": LanguageAbilitySerializer,
#             "entrance_test_abilities": EntranceTestAbilitySerializer,
#             "relatives": RelativeSerializer,
#             "visit_history": VisitHistorySerializer,
#             "refusal_history": RefusalHistorySerializer,
#         }
#         return mapping[field_name]




from rest_framework import serializers
from lead.models import *
from master.models import *

class UUIDRefField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            return queryset.get(uuid=data)
        except queryset.model.DoesNotExist:
            raise serializers.ValidationError(f"Invalid uuid '{data}' - object does not exist.")

    def to_representation(self, value):
        return str(value.uuid)



class ApplicantSerializer(serializers.ModelSerializer):
    # UUID-based foreign keys
    gender = serializers.SlugRelatedField(
        slug_field='uuid', queryset=Gender.objects.all(), required=True
    )
    marital_status = serializers.SlugRelatedField(
        slug_field='uuid', queryset=Maritalstatus.objects.all(), required=True
    )
    country_of_citizenship = serializers.SlugRelatedField(
        slug_field='uuid', queryset=Country.objects.all(), required=False
    )
    country_of_residency = serializers.SlugRelatedField(
        slug_field='uuid', queryset=Country.objects.all(), required=False
    )
    residency_status = serializers.SlugRelatedField(
        slug_field='uuid', queryset=VisaName.objects.all(), required=False
    )

    country = serializers.SlugRelatedField(
        slug_field='uuid', queryset=Country.objects.all(), required=False
    )
    state = serializers.SlugRelatedField(
        slug_field='uuid', queryset=State.objects.all(), required=False
    )
    district = serializers.SlugRelatedField(
        slug_field='uuid', queryset=District.objects.all(), required=False
    )
    city = serializers.SlugRelatedField(
        slug_field='uuid', queryset=City.objects.all(), required=False
    )

    test_exam_name = serializers.SlugRelatedField(
        slug_field='uuid', queryset=LanguageTest.objects.all(), required=False
    )

    # Many-to-many UUIDs
    interested_visa_categories = serializers.SlugRelatedField(
        slug_field='uuid', queryset=VisaMain.objects.all(), many=True, required=False
    )
    interested_countries = serializers.SlugRelatedField(
        slug_field='uuid', queryset=Country.objects.all(), many=True, required=False
    )

    class Meta:
        model = Applicant
        fields = "__all__"
        extra_kwargs = {
            "email": {"required": True},
            "whatsapp_number": {"required": True},
            "mobile_number": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }




#<------------------------Education-------------------------->

class EducationSerializer(serializers.ModelSerializer):
    # UUID-based foreign keys for creation/updating
    applicant = serializers.SlugRelatedField(slug_field='uuid', queryset=Applicant.objects.all())
    education_level = serializers.SlugRelatedField(slug_field='uuid', queryset=EducationLevel.objects.all())
    education_duration = serializers.SlugRelatedField(slug_field='uuid', queryset=EducationDuration.objects.all())
    study_major_area = serializers.SlugRelatedField(slug_field='uuid', queryset=Studymajorarea.objects.all())
    study_main_area = serializers.SlugRelatedField(slug_field='uuid', queryset=Studymainarea.objects.all(), allow_null=True)
    country = serializers.SlugRelatedField(slug_field='uuid', queryset=Country.objects.all())
    state = serializers.SlugRelatedField(slug_field='uuid', queryset=State.objects.all())
    medium_of_education = serializers.SlugRelatedField(slug_field='uuid', queryset=MediumofEducation.objects.all())
    academic_result_type = serializers.SlugRelatedField(slug_field='uuid', queryset=AcademicResultType.objects.all())
    education_type = serializers.SlugRelatedField(slug_field='uuid', queryset=EducationType.objects.all())
    math_result_type = serializers.SlugRelatedField(slug_field='uuid', queryset=AcademicResultType.objects.all(), allow_null=True)
    english_result_type = serializers.SlugRelatedField(slug_field='uuid', queryset=AcademicResultType.objects.all(), allow_null=True)
    physics_result_type = serializers.SlugRelatedField(slug_field='uuid', queryset=AcademicResultType.objects.all(), allow_null=True)

    # Read-only fields to show related names in response
    applicant_name = serializers.CharField(source='applicant.first_name', read_only=True)
    education_level_name = serializers.CharField(source='education_level.name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    state_name = serializers.CharField(source='state.name', read_only=True)
    study_major_area_name = serializers.CharField(source='study_major_area.name', read_only=True)
    study_main_area_name = serializers.CharField(source='study_main_area.name', read_only=True)
    education_type_name = serializers.CharField(source='education_type.name', read_only=True)

    class Meta:
        model = Education
        fields = "__all__"

    # Custom validation for dates
    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({"end_date": "End date must be greater than start date."})
        return attrs


class WorkExperienceSerializer(serializers.ModelSerializer):

    applicant = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Applicant.objects.all()
    )

    country = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all(),
        required=False,
        allow_null=True
    )

    state = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=State.objects.all(),
        required=False,
        allow_null=True
    )

    designation = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Designation.objects.all(),
        required=False,
        allow_null=True
    )

    salary_mode = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=ModeofSalary.objects.all(),
        required=False,
        allow_null=True
    )

    itr_status = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=ITReturnStatus.objects.all(),
        required=False,
        allow_null=True
    )

    currency = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all(),
        required=False,
        allow_null=True
    )

    job_type = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=JobType.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = WorkExperience
        fields = [
            "uuid",
            "applicant",
            "consider",
            "country",
            "state",
            "employer_name",
            "designation",
            "job_start_date",
            "job_end_date",
            "years",
            "months",
            "monthly_salary",
            "salary_mode",
            "itr_status",
            "currency",
            "job_type",
            "salary_amount",
            "days",
            "amount_numeric",
            "created_at",
            "updated_at"
        ]
    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({"end_date": "End date must be greater than start date."})
        return attrs


class LanguageAbilitySerializer(serializers.ModelSerializer):

    # UUID Based Foreign Keys (POST/PUT/PATCH me UUID doge)
    applicant = serializers.SlugRelatedField(slug_field='uuid', queryset=Applicant.objects.all())
    language = serializers.SlugRelatedField(slug_field='uuid', queryset=Language.objects.all(), allow_null=True)

    listening_score = serializers.SlugRelatedField(slug_field='uuid', queryset=LanguagetestmoduleName.objects.all())
    speaking_score = serializers.SlugRelatedField(slug_field='uuid', queryset=LanguagetestmoduleName.objects.all())
    reading_score = serializers.SlugRelatedField(slug_field='uuid', queryset=LanguagetestmoduleName.objects.all())
    writing_score = serializers.SlugRelatedField(slug_field='uuid', queryset=LanguagetestmoduleName.objects.all())
    overall_score = serializers.SlugRelatedField(slug_field='uuid', queryset=LanguagetestmoduleName.objects.all())

    # Read Only Display Fields
    applicant_name = serializers.CharField(source='applicant.first_name', read_only=True)
    language_name = serializers.CharField(source='language.name', read_only=True)
    listening_score_name = serializers.CharField(source='listening_score.name', read_only=True)
    speaking_score_name = serializers.CharField(source='speaking_score.name', read_only=True)
    reading_score_name = serializers.CharField(source='reading_score.name', read_only=True)
    writing_score_name = serializers.CharField(source='writing_score.name', read_only=True)
    overall_score_name = serializers.CharField(source='overall_score.name', read_only=True)

    class Meta:
        model = LanguageAbility
        fields = "__all__"


class EntranceTestAbilitySerializer(serializers.ModelSerializer):
    applicant = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Applicant.objects.all()
    )

    module_01_score = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=EntranceTestModuleName.objects.all()
    )
    module_02_score = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=EntranceTestModuleName.objects.all()
    )
    module_03_score = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=EntranceTestModuleName.objects.all()
    )
    total_score = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=EntranceTestModuleName.objects.all()
    )

    class Meta:
        model = EntranceTestAbility
        fields = "__all__"

    def validate(self, data):
        appeared_test = data.get("appeared_test")

        if appeared_test == "Yes":
        
            required_fields = [
                "entrance_test_name",
                "entrance_test_short_name",
                "module_01_score",
                "module_02_score",
                "module_03_score",
                "total_score"
            ]

            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError(
                        {field: f"{field.replace('_',' ')} is required when appeared_test is Yes."}
        )
        return data
    
    
class RelativeSerializer(serializers.ModelSerializer):

    applicant = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Applicant.objects.all()
    )
    applicant_type = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=ApplicantType.objects.all()
    )
    country = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all()
    )
    state = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=State.objects.all(),
        required=False,
        allow_null=True
    )
    city = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=City.objects.all(),
        required=False,
        allow_null=True
    )
    relation = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Relation.objects.all()
    )
    visa_category = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=VisaMain.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Relative
        fields = '__all__'

    def validate(self, attrs):
        applicant = attrs.get("applicant")
        relation = attrs.get("relation")

        # Prevent duplicate relation entries for same applicant
        if Relative.objects.filter(applicant=applicant, relation=relation).exists():
            raise serializers.ValidationError(
               {"relation": "This relation already exists for this applicant."}
            )

        return attrs


class VisitHistorySerializer(serializers.ModelSerializer):
        # UUID-based foreign keys for readability
    applicant = serializers.SlugRelatedField(
       slug_field='uuid',
        queryset=Applicant.objects.all()
    )
    applicant_type = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=ApplicantType.objects.all(),
        required=False, # Optional field
        allow_null=True
    )
    country = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all(),
        required=False,
        allow_null=True
    )
    visa_category = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=VisaMain.objects.all(),
        required=False,
        allow_null=True
    )
    purpose_of_visit = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=PurposeOfVisit.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = VisitHistory
        fields = [
            'uuid', 'applicant', 'applicant_type', 'country', 'visa_category',
            'issue_date', 'travel_from', 'travel_to', 'purpose_of_visit',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class RefusalHistorySerializer(serializers.ModelSerializer):

    applicant = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Applicant.objects.all()
    )

    applicant_type = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=ApplicantType.objects.all(),
        required=False,
        allow_null=True
    )

    country = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all(),
        required=False,
        allow_null=True
    )

    visa_category = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=VisaMain.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = RefusalHistory
        fields = [
            'uuid', 'applicant', 'applicant_type', 'country', 'visa_category',
            'refusal_date', 'refusal_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']

    def validate(self, data):
        import datetime

        refusal_date = data.get('refusal_date')
        refusal_reason = data.get('refusal_reason')

        # Future date not allowed
        if refusal_date and refusal_date > datetime.date.today():
            raise serializers.ValidationError({
                "refusal_date": "Refusal date cannot be in the future."
            })

        # Reason length validation
        if refusal_reason and len(refusal_reason.strip()) < 10:
            raise serializers.ValidationError({
                "refusal_reason": "Refusal reason must be at least 10 characters long."
            })

        return data


class BusinessExperienceSerializer(serializers.ModelSerializer):
    applicant = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Applicant.objects.all()
    )

    country = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all(),
        allow_null=True,
        required=False
    )

    company_type = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=CompanyType.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = BusinessExperience
        fields = [
            "uuid",
            "applicant",
            "country",
            "company_name",
            "company_type",
            "share_percent",
            "start_date",
            "end_date",
            "turnover",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        # End date must be after start date
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                "end_date": "End date cannot be earlier than start date."
            })
        return attrs
    


class NetworthSerializer(serializers.ModelSerializer):
    # UUID-based foreign keys
    applicant = serializers.SlugRelatedField(slug_field='uuid', queryset=Applicant.objects.all())
    applicant_type = serializers.SlugRelatedField(slug_field='uuid', queryset=ApplicantType.objects.all(), allow_null=True)
    country = serializers.SlugRelatedField(slug_field='uuid', queryset=Country.objects.all(), allow_null=True)
    currency = serializers.SlugRelatedField(slug_field='uuid', queryset=Country.objects.all(), allow_null=True)

    # Read-only fields for names
    applicant_name = serializers.CharField(source='applicant.first_name', read_only=True)
    applicant_type_name = serializers.CharField(source='applicant_type.name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    currency_name = serializers.CharField(source='currency.name', read_only=True)

    class Meta:
        model = Networth
        fields = [
            'uuid',
            'applicant',
            'applicant_name',
            'applicant_type',
            'applicant_type_name',
            'country',
            'country_name',
            'currency',
            'currency_name',
            'immovable_property',
            'movable_property',
            'liquid_amount',
            'total_networth',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']

class EligibilityFlagsSerializer(serializers.ModelSerializer):
    # UUID-based foreign key
    applicant = serializers.SlugRelatedField(slug_field='uuid', queryset=Applicant.objects.all())

    # Read-only field for related name
    applicant_name = serializers.CharField(source='applicant.first_name', read_only=True)

    class Meta:
        model = EligibilityFlags
        fields = [
            'uuid',
            'applicant',
            'applicant_name',
            'trade_certificate',
            'educational_credential_assessment',
            'ita_province',
            'tech_startup_founder',
            'reside_outside_greater_city',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']

class SpouseEducationleadSerializer(serializers.ModelSerializer):
# UUID-based foreign keys
    applicant = serializers.SlugRelatedField(slug_field='uuid', queryset=Applicant.objects.all())
    education_level = serializers.SlugRelatedField(slug_field='uuid', queryset=EducationLevel.objects.all(), allow_null=True)
    duration = serializers.SlugRelatedField(slug_field='uuid', queryset=EducationDuration.objects.all(), allow_null=True)
    study_main_area = serializers.SlugRelatedField(slug_field='uuid', queryset=Studymainarea.objects.all(), allow_null=True)
    edu_type = serializers.SlugRelatedField(slug_field='uuid', queryset=EducationType.objects.all(), allow_null=True)

    # Read-only related names
    applicant_name = serializers.CharField(source='applicant.first_name', read_only=True)
    education_level_name = serializers.CharField(source='education_level.name', read_only=True)
    duration_name = serializers.CharField(source='duration.name', read_only=True)
    study_main_area_name = serializers.CharField(source='study_main_area.name', read_only=True)
    edu_type_name = serializers.CharField(source='edu_type.name', read_only=True)

    class Meta:
        model = SpouseEducationlead
        fields = [
            'uuid',
            'applicant',
            'applicant_name',
            'education_level',
            'education_level_name',
            'duration',
            'duration_name',
            'study_main_area',
            'study_main_area_name',
            'edu_type',
            'edu_type_name',
            'start_date',
            'end_date',
            'result',
        ]
        read_only_fields = ['uuid']

class SpouseEducationleadSerializer(serializers.ModelSerializer):
# UUID-based foreign keys
    applicant = serializers.SlugRelatedField(slug_field='uuid', queryset=Applicant.objects.all())
    education_level = serializers.SlugRelatedField(slug_field='uuid', queryset=EducationLevel.objects.all(), allow_null=True)
    duration = serializers.SlugRelatedField(slug_field='uuid', queryset=EducationDuration.objects.all(), allow_null=True)
    study_main_area = serializers.SlugRelatedField(slug_field='uuid', queryset=Studymainarea.objects.all(), allow_null=True)
    edu_type = serializers.SlugRelatedField(slug_field='uuid', queryset=EducationType.objects.all(), allow_null=True)

    # Read-only fields for related names
    applicant_name = serializers.CharField(source='applicant.first_name', read_only=True)
    education_level_name = serializers.CharField(source='education_level.name', read_only=True)
    duration_name = serializers.CharField(source='duration.name', read_only=True)
    study_main_area_name = serializers.CharField(source='study_main_area.name', read_only=True)
    edu_type_name = serializers.CharField(source='edu_type.name', read_only=True)

    class Meta:
        model = SpouseEducationlead
        fields = [
            'uuid',
            'applicant',
            'applicant_name',
            'education_level',
            'education_level_name',
            'duration',
            'duration_name',
            'study_main_area',
            'study_main_area_name',
            'edu_type',
            'edu_type_name',
            'start_date',
            'end_date',
            'result',
        ]
        read_only_fields = ['uuid']
        