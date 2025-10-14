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



# class BankAccountTypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BankAccountType
#         fields = ['uuid', 'name', 'description', 'created_at', 'updated_at']


