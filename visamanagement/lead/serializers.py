from rest_framework import serializers
from .models import Applicant, Education, WorkExperience, LanguageAbility, EntranceTestAbility, Relative, VisitHistory, RefusalHistory
from django.db import transaction



class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        exclude = ("id", "created_at", "updated_at")

class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        exclude = ("id", "created_at", "updated_at")

class LanguageAbilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageAbility
        exclude = ("id", "created_at", "updated_at")

class EntranceTestAbilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = EntranceTestAbility
        exclude = ("id", "created_at", "updated_at")

class RelativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relative
        exclude = ("id", "created_at", "updated_at")

class VisitHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitHistory
        exclude = ("id", "created_at", "updated_at")

class RefusalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RefusalHistory
        exclude = ("id", "created_at", "updated_at")

# ------------------------------
# Main Applicant Serializer
# ------------------------------

class ApplicantSerializer(serializers.ModelSerializer):
    educations = EducationSerializer(many=True, required=False)
    work_experiences = WorkExperienceSerializer(many=True, required=False)
    language_abilities = LanguageAbilitySerializer(many=True, required=False)
    entrance_test_abilities = EntranceTestAbilitySerializer(many=True, required=False)
    relatives = RelativeSerializer(many=True, required=False)
    visit_history = VisitHistorySerializer(many=True, required=False)
    refusal_history = RefusalHistorySerializer(many=True, required=False)

    class Meta:
        model = Applicant
        fields = "__all__"

    # Ensure email and mobile number are unique
    def validate(self, data):
        email = data.get("email")
        mobile_number = data.get("mobile_number")
        qs = Applicant.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email must be unique."})
        if qs.filter(mobile_number=mobile_number).exists():
            raise serializers.ValidationError({"mobile_number": "Mobile number must be unique."})
        return data

    def create(self, validated_data):
        nested_fields = [
            "educations", "work_experiences", "language_abilities",
            "entrance_test_abilities", "relatives", "visit_history", "refusal_history"
        ]
        nested_data = {field: validated_data.pop(field, []) for field in nested_fields}

        with transaction.atomic():
            applicant = Applicant.objects.create(**validated_data)

            for field in nested_fields:
                serializer_class = self._get_serializer_class(field)
                for item in nested_data[field]:
                    serializer_class().Meta.model.objects.create(applicant=applicant, **item)
        return applicant

    def update(self, instance, validated_data):
        nested_fields = [
            "educations", "work_experiences", "language_abilities",
            "entrance_test_abilities", "relatives", "visit_history", "refusal_history"
        ]
        nested_data = {field: validated_data.pop(field, []) for field in nested_fields}

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Optional: Clear old nested data and create new (simpler than diff update)
            for field in nested_fields:
                serializer_class = self._get_serializer_class(field)
                instance_data = getattr(instance, field)
                instance_data.all().delete()
                for item in nested_data[field]:
                    serializer_class().Meta.model.objects.create(applicant=instance, **item)

        return instance

    def _get_serializer_class(self, field_name):
        mapping = {
            "educations": EducationSerializer,
            "work_experiences": WorkExperienceSerializer,
            "language_abilities": LanguageAbilitySerializer,
            "entrance_test_abilities": EntranceTestAbilitySerializer,
            "relatives": RelativeSerializer,
            "visit_history": VisitHistorySerializer,
            "refusal_history": RefusalHistorySerializer,
        }
        return mapping[field_name]


