from django.contrib.auth import authenticate,get_user_model
from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()

class AdminUserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # Look up user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        # Authenticate using username (Django default)
        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        # Only allow superuser/staff
        if not (user.is_staff or user.is_superuser):
            raise serializers.ValidationError("User is not an admin.")

        data['user'] = user
        return data

class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = ['uuid', 'text', 'description', 'created_at', 'updated_at', 'is_active', 'is_deleted']
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'is_deleted']


class MaritalstatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maritalstatus
        fields = ['uuid', 'text', 'description', 'created_at', 'updated_at', 'is_active', 'is_deleted']
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'is_deleted']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']



class EmployeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeType
        fields = ['uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']



class CompanyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyType
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'is_deleted']


class OwnershipTypeSerializer(serializers.ModelSerializer):
    company_type_name = serializers.CharField(source='company_type.name', read_only=True)

    class Meta:
        model = OwnershipType
        fields = ['uuid', 'company_type', 'company_type_name', 'name', 'description', 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'is_deleted']




class StakeholderCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StakeholderCategory
        fields = ["uuid", "name", "description", "created_at", "updated_at"]


class StakeholderTypeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = StakeholderType
        fields = ["uuid", "name", "description", "category", "category_name", "created_at", "updated_at"]



class AccreditationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccreditationCategory
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at']


class AccreditationNameSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = AccreditationName
        fields = [
            'uuid', 'country', 'country_name', 'category', 'category_name',
            'full_name', 'short_name', 'issuing_authority', 'valid_upto',
            'description', 'created_at', 'updated_at'
        ]


class BankAccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccountType
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at']



class LicenseNameSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = LicenseName
        fields = [
            'uuid', 'id', 'country', 'country_name',
            'full_name', 'short_name', 'issuing_authority',
            'description', 'valid_upto',
            'created_at', 'updated_at'
        ]
    


class LeadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadSource
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at']

class InterestLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestLevel
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at']

class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at']

class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at']

class ActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityType
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at']

class LostReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostReason
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at']


class EducationLevelCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationLevelCode
        fields = ['uuid', 'Levelcode', 'description', 'created_at', 'updated_at']




class EducationLevelSerializer(serializers.ModelSerializer):
    # Optionally display the related LevelCode's code
    level_code_detail = serializers.CharField(
        source='level_code.Levelcode', read_only=True
    )

    class Meta:
        model = EducationLevel
        fields = [
            'uuid', 
            'level_code', 
            'level_code_detail',  # optional for easy read
            'educationlevel', 
            'description', 
            'is_deleted',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class EducationDurationSerializer(serializers.ModelSerializer):
    # Optionally display the related EducationLevel's name
    educationlevel_detail = serializers.CharField(
        source='educationlevel.educationlevel', read_only=True
    )

    class Meta:
        model = EducationDuration
        fields = [
            'uuid',
            'educationlevel',
            'educationlevel_detail',  # optional for easy read
            'durations',
            'description',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']



class StudymainareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Studymainarea
        fields = [
            'id',
            'uuid',
            'Mainarea',
            'description',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']




class StudymajorareaSerializer(serializers.ModelSerializer):
    mainarea = StudymainareaSerializer(read_only=True)
    mainarea_id = serializers.PrimaryKeyRelatedField(
        queryset=Studymainarea.objects.all(),
        source='mainarea',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Studymajorarea
        fields = [
            'id',
            'uuid',
            'mainarea',
            'mainarea_id',
            'Majorarea',
            'description',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']




class StudySpecialisationSerializer(serializers.ModelSerializer):
    mainarea = StudymainareaSerializer(read_only=True)
    mainarea_id = serializers.PrimaryKeyRelatedField(
        queryset=Studymainarea.objects.all(),
        source='mainarea',
        write_only=True,
        required=False,
        allow_null=True
    )

    Majorarea = StudymajorareaSerializer(read_only=True)
    Majorarea_id = serializers.PrimaryKeyRelatedField(
        queryset=Studymajorarea.objects.all(),
        source='Majorarea',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = StudySpecialisation
        fields = [
            'id',
            'uuid',
            'mainarea',
            'mainarea_id',
            'Majorarea',
            'Majorarea_id',
            'studyspecialisation',
            'description',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']



class AcademicResultTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicResultType
        fields = [
            'id',
            'uuid',
            'Academicresulttype',
            'description',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class AcademicResultSerializer(serializers.ModelSerializer):
    AcademicResulttype = serializers.SerializerMethodField()
    AcademicResulttype_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicResultType.objects.all(),
        source='AcademicResulttype',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = AcademicResult
        fields = [
            'id',
            'uuid',
            'AcademicResulttype',
            'AcademicResulttype_id',
            'Academicresult',
            'description',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']

    def get_AcademicResulttype(self, obj):
        """Return a minimal representation of AcademicResultType."""
        if obj.AcademicResulttype:
            return {
                "id": obj.AcademicResulttype.id,
                "Academicresulttype": obj.AcademicResulttype.Academicresulttype
            }
        return None


class EducationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationType
        fields = [
            'uuid',
            'educationType',
            'Perticulars',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']

class MediumofEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediumofEducation
        fields = [
            'uuid',  
            'name',
            'Perticulars',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']



class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = [
            'uuid',  
            'name',
            'description',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']