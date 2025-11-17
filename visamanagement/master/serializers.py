from django.contrib.auth import authenticate,get_user_model
from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
# from .process import*

User = get_user_model()

# class AdminUserLoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         email = data.get("email")
#         password = data.get("password")

#         # Look up user by email
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             raise serializers.ValidationError("Invalid email or password.")

#         # Authenticate using username (Django default)
#         user = authenticate(username=user.username, password=password)
#         if not user:
#             raise serializers.ValidationError("Invalid email or password.")

#         # Only allow superuser/staff
#         if not (user.is_staff or user.is_superuser):
#             raise serializers.ValidationError("User is not an admin.")

#         data['user'] = user
#         return data



class AdminUserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # Look up users by email (use filter instead of get to avoid crash)
        users = User.objects.filter(email=email)
        if not users.exists():
            raise serializers.ValidationError("Invalid email or password.")

        # Handle multiple users with same email
        if users.count() > 1:
            raise serializers.ValidationError(
                "Multiple users found with this email. Please contact the administrator."
            )

        user = users.first()

        # Authenticate using username (Django default)
        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        # Allow only admin/staff
        if not (user.is_staff or user.is_superuser):
            raise serializers.ValidationError("User is not an admin.")

        data["user"] = user
        return data



class GenderSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False, allow_blank=True)  

    class Meta:
        model = Gender
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at', 'is_active', 'is_deleted']
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'is_deleted']


class MaritalstatusSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False, allow_blank=True)  

    class Meta:
        model = Maritalstatus
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at', 'is_active', 'is_deleted']
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'is_deleted']


class ContinentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Continents
        fields = [
            'uuid', 'name', 'description',
            'is_active', 'is_deleted',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']



class CountrySerializer(serializers.ModelSerializer):
    continent = ContinentSerializer(read_only=True)
    continent_id = serializers.PrimaryKeyRelatedField(
        queryset=Continents.objects.all(),
        source='continent',
        write_only=True,
        required=False
    )

    class Meta:
        model = Country
        fields = [
            'uuid', 'name', 'continent', 'continent_id',
            'currencyfullname','currencyshortname','description',
            'shortName', 'fullName', 'officialName', 'capitalCity',
            'dialCodes', 'currencyCode', 'status',
            'is_active', 'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']



class StateSerializer(serializers.ModelSerializer):
    countryName = serializers.CharField(source='countryName.name', read_only=True)
    country_id = serializers.SlugRelatedField(
        queryset=Country.objects.all(),
        slug_field='uuid',
        source='countryName',
        required=False
    )
    state_display = serializers.CharField(source='get_state_display', read_only=True)  # shows "State"/"Territory"

    class Meta:
        model = State
        fields = [
            'uuid', 'countryName', 'country_id',
            'stateName', 'state', 'state_display',  # <-- state is input, state_display is output
            'stateshortName', 'description',
            'is_active', 'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']

    

class DistrictSerializer(serializers.ModelSerializer):
    # Flat read-only fields for response
    countryName = serializers.CharField(source='countryName.name', read_only=True)
    country_uuid = serializers.UUIDField(source='countryName.uuid', read_only=True)

    stateName = serializers.CharField(source='stateName.stateName', read_only=True)
    state_uuid = serializers.UUIDField(source='stateName.uuid', read_only=True)

    # UUID input fields for write operations
    country_id = serializers.SlugRelatedField(
        queryset=Country.objects.all(),
        slug_field='uuid',
        source='countryName',
        write_only=True
    )
    state_id = serializers.SlugRelatedField(
        queryset=State.objects.all(),
        slug_field='uuid',
        source='stateName',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = District
        fields = [
            'uuid',
            'countryName', 'country_uuid', 'country_id',
            'stateName', 'state_uuid', 'state_id',
            'districtName', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class CitySerializer(serializers.ModelSerializer):
    countryName = serializers.CharField(source='countryName.name', read_only=True)
    country_uuid = serializers.UUIDField(source='countryName.uuid', read_only=True)
    
    stateName = serializers.CharField(source='stateName.stateName', read_only=True)
    state_uuid = serializers.UUIDField(source='stateName.uuid', read_only=True)
    
    districtName = serializers.CharField(source='districtName.districtName', read_only=True)
    district_uuid = serializers.UUIDField(source='districtName.uuid', read_only=True)

    # UUID input fields
    country_id = serializers.SlugRelatedField(
        queryset=Country.objects.all(),
        slug_field='uuid',
        source='countryName',
        write_only=True
    )
    state_id = serializers.SlugRelatedField(
        queryset=State.objects.all(),
        slug_field='uuid',
        source='stateName',
        write_only=True,
        required=False,
        allow_null=True 
    )
    district_id = serializers.SlugRelatedField(
        queryset=District.objects.all(),
        slug_field='uuid',
        source='districtName',
        write_only=True,
        allow_null=True ,
        required=False
    )

    class Meta:
        model = City
        fields = [
            'uuid',
            'countryName', 'country_uuid', 'country_id',
            'stateName', 'state_uuid', 'state_id',
            'districtName', 'district_uuid', 'district_id',
            'cityName', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class RelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relation
        fields = [
            'uuid', 'name', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class TimezoneSerializer(serializers.ModelSerializer):
    countryName = serializers.CharField(source='countryName.name', read_only=True)
    stateName = serializers.CharField(source='stateName.stateName', read_only=True)

    # write-only UUID input
    country_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    state_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    # read-only IDs
    country_uuid = serializers.UUIDField(source='countryName.uuid', read_only=True)
    state_uuid = serializers.UUIDField(source='stateName.uuid', read_only=True)

    timezone = serializers.CharField(source='Timezone')

    class Meta:
        model = Timezone
        fields = [
            'uuid', 'countryName', 'country_uuid', 'country_id',
            'stateName', 'state_uuid', 'state_id',
            'timezone', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'countryName', 'stateName', 'country_uuid', 'state_uuid']

    def create(self, validated_data):
        country_uuid = validated_data.pop('country_id', None)
        state_uuid = validated_data.pop('state_id', None)

        country = Country.objects.filter(uuid=country_uuid).first() if country_uuid else None
        state = State.objects.filter(uuid=state_uuid).first() if state_uuid else None

        return Timezone.objects.create(
            countryName=country,
            stateName=state,
            **validated_data
        )

    def update(self, instance, validated_data):
        # Handle country_id / state_id updates
        country_uuid = validated_data.pop('country_id', None)
        state_uuid = validated_data.pop('state_id', None)

        if country_uuid is not None:
            instance.countryName = Country.objects.filter(uuid=country_uuid).first()
        if state_uuid is not None:
            instance.stateName = State.objects.filter(uuid=state_uuid).first()

        # Update other fields normally
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class CivilIdNameSerializer(serializers.ModelSerializer):
    # Show choice label for valid_type
    valid_type_detail = serializers.SerializerMethodField()
 
    # Show choice label for valid_duration_unit
    valid_duration_unit_detail = serializers.SerializerMethodField()
 
    class Meta:
        model = CivilIdName
        fields = [
            'uuid',
            'civil_id_name',
            'authority_full_name',
            'authority_short_name',
 
            'valid_type',
            'valid_type_detail',
 
            'valid_duration_value',
            'valid_duration_unit',
            'valid_duration_unit_detail',
            'valid_date',
            'description',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at','is_deleted']
 
    def get_valid_type_detail(self, obj):
        return obj.get_valid_type_display() if obj.valid_type else None
 
    def get_valid_duration_unit_detail(self, obj):
        return obj.get_valid_duration_unit_display() if obj.valid_duration_unit else None

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
    
    validtype_display = serializers.CharField(source='get_valid_type_display', read_only=True)  # shows "State"/"Territory"

    validunit_display = serializers.CharField(source='get_valid_duration_unit_display', read_only=True)  # shows "State"/"Territory"

    class Meta:
        model = AccreditationName
        fields = [
            'uuid', 'country', 'country_name', 'category', 'category_name',
            'valid_type',
            'valid_date',
            'validtype_display',
            'validunit_display',
            'valid_duration_value',
            'valid_duration_unit',
            'full_name', 'short_name', 'issuing_authority',
            'description', 'created_at', 'updated_at'
        ]


class BankAccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccountType
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at']



class LicenseNameSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)

    validtype_display = serializers.CharField(source='get_valid_type_display', read_only=True)  # shows "State"/"Territory"

    validunit_display = serializers.CharField(source='get_valid_duration_unit_display', read_only=True)  # shows "State"/"Territory"

    class Meta:
        model = LicenseName
        fields = [
            'uuid',
            'id',
            'country',
            'country_name',
            'full_name',
            'short_name',
            'validtype_display',
            'issuing_authority',
            'description',
            'validunit_display',
            'valid_type',
            'valid_date',
            'valid_duration_value',
            'valid_duration_unit',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
    extra_kwargs = {
            'valid_type': {'required': False, 'allow_null': True},
            'valid_duration_unit': {'required': False, 'allow_null': True},
            'valid_date': {'required': False, 'allow_null': True},
            'valid_duration_value': {'required': False, 'allow_null': True},
            'short_name': {'required': False, 'allow_blank': True, 'allow_null': True},
            'issuing_authority': {'required': False, 'allow_blank': True, 'allow_null': True},
            'description': {'required': False, 'allow_blank': True, 'allow_null': True},
        }


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

class LostReasonB2BSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostReasonB2B
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at']



class EducationLevelCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationLevelCode
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at']




class EducationLevelSerializer(serializers.ModelSerializer):
    level_code = serializers.SlugRelatedField(
        queryset=EducationLevelCode.objects.all(),
        slug_field='uuid',  # Use UUID field in EducationLevelCode
        allow_null=True,
        required=False
    )
    level_code_detail = serializers.CharField(
        source='level_code.name', read_only=True
    )

    class Meta:
        model = EducationLevel
        fields = [
            'uuid', 
            'level_code', 
            'level_code_detail',
            'educationlevel', 
            'description', 
            'is_deleted',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class EducationDurationSerializer(serializers.ModelSerializer):
    # Optionally display the related EducationLevel's name
    educationlevel=serializers.SlugRelatedField(
        queryset=EducationLevel.objects.all(),
        slug_field='uuid', 
        allow_null=True,
        required=False
    )

    educationlevel_detail = serializers.CharField(
        source='educationlevel.educationlevel', read_only=True
    )

    class Meta:
        model = EducationDuration
        fields = [
            'uuid',
            'educationlevel',
            'educationlevel_detail',  
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
            'name',
            'description',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']




class StudyMajorAreaSerializer(serializers.ModelSerializer):
    mainarea = serializers.SlugRelatedField(
        queryset=Studymainarea.objects.all(),
        slug_field='uuid',  
        allow_null=True,
        required=False
    )
    mainarea_name = serializers.CharField(source='mainarea.name', read_only=True)

    class Meta:
        model = Studymajorarea
        fields = [
            'id',
            'uuid',
            'mainarea',
            'mainarea_name',
            'majorarea',
            'description',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']



class StudySpecialisationSerializer(serializers.ModelSerializer):
    
    # Write-only UUID fields for input
    mainarea_id = serializers.SlugRelatedField(
        queryset=Studymainarea.objects.all(),
        slug_field='uuid',
        source='mainarea',
        write_only=True,
        required=False,
        allow_null=True
    )
    majorarea_id = serializers.SlugRelatedField(
        queryset=Studymajorarea.objects.all(),
        slug_field='uuid',
        source='majorarea',
        write_only=True,
        required=False,
        allow_null=True
    )

    # Read-only flat fields for output
    mainarea_uuid = serializers.UUIDField(source='mainarea.uuid', read_only=True)
    mainarea_name = serializers.CharField(source='mainarea.name', read_only=True)
    majorarea_uuid = serializers.UUIDField(source='majorarea.uuid', read_only=True)
    majorarea_name = serializers.CharField(source='majorarea.majorarea', read_only=True)

    class Meta:
        model = StudySpecialisation
        fields = [
            'id',
            'uuid',
            'mainarea_uuid',
            'mainarea_name',
            'mainarea_id',
            'majorarea_uuid',
            'majorarea_name',
            'majorarea_id',
            'studyspecialisation',
            'description',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]

    def get_mainarea_uuid(self, obj):
        try:
            return obj.mainarea.uuid if obj.mainarea else None
        except:
            return None

    def get_majorarea_uuid(self, obj):
        try:
            return obj.majorarea.uuid if obj.majorarea else None
        except:
            return None


class AcademicResultTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicResultType
        fields = [
            'id',
            'uuid',
            'name',
            'datatype',
            'description',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']



class AcademicResultSerializer(serializers.ModelSerializer):
    # Show type details as separate keys
    AcademicResulttype_uuid = serializers.SerializerMethodField()
    AcademicResulttype_name = serializers.SerializerMethodField()

    # Accept UUID to set the relation
    AcademicResulttype_id = serializers.SlugRelatedField(
        queryset=AcademicResultType.objects.all(),
        slug_field='uuid',
        source='AcademicResulttype',
        # slug_field='uuid',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = AcademicResult
        fields = [
            'id',
            'uuid',
            'AcademicResulttype_id',      # for input only
            'AcademicResulttype_uuid',    # separate key for output
            'AcademicResulttype_name',    # separate key for output
            'Academicresult',
            'description',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 
                            'AcademicResulttype_uuid', 'AcademicResulttype_name']

    def get_AcademicResulttype_uuid(self, obj):
        if obj.AcademicResulttype:
            return obj.AcademicResulttype.uuid
        return None

    def get_AcademicResulttype_name(self, obj):
        if obj.AcademicResulttype:
            return obj.AcademicResulttype.name
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
            'perticulars',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id','uuid', 'created_at', 'updated_at']



class ECAAwardingBodySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)  # Display country name
    selection_type_display = serializers.CharField(source='get_selection_type_display', read_only=True)

    class Meta:
        model = ECAAwardingBody
        fields = [
            'uuid',
            'id',
            'country',
            'country_name',
            'description',
            'selection_type',
            'selection_type_display',
            'valid_duration_value',
            'eca_body_full_name',
            'eca_body_short_name',
            'eca_valid_period',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class DegreeAwardedBySerializer(serializers.ModelSerializer):
    country = serializers.SlugRelatedField(queryset=Country.objects.all(), slug_field='uuid')
    education_level = serializers.SlugRelatedField(queryset=EducationLevel.objects.all(), slug_field='uuid')

    country_name = serializers.CharField(source='country.name', read_only=True)
    education_level_name = serializers.CharField(source='education_level.educationlevel', read_only=True)
   
    class Meta:
        model = DegreeAwardedBy
        fields = [
            'uuid', 'id',
            'country', 'country_name',
            'education_level', 'education_level_name',
            'degree_name', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']



class DegreeAwardedInstituteSerializer(serializers.ModelSerializer):
    # Accept UUIDs for related fields
    degree_awarded_by_id = serializers.SlugRelatedField(
        queryset=DegreeAwardedBy.objects.all(),
        source='degree_awarded_by',
        slug_field='uuid',
        write_only=True
    )
    country_id = serializers.SlugRelatedField(
        queryset=Country.objects.all(),
        source='country',
        slug_field='uuid',
        write_only=True,
        required=False,
        allow_null=True
    )
    state_id = serializers.SlugRelatedField(
        queryset=State.objects.all(),
        source='state',
        slug_field='uuid',
        write_only=True,
        required=False,
        allow_null=True
    )
    education_level_id = serializers.SlugRelatedField(
        queryset=EducationLevel.objects.all(),
        source='education_level',
        slug_field='uuid',
        write_only=True,
        required=False,
        allow_null=True
    )


    # For output: show readable names
    degree_awarded_by_name = serializers.CharField(source='degree_awarded_by.degree_name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    state_name = serializers.CharField(source='state.stateName', read_only=True)
    education_level_name = serializers.CharField(source='education_level.educationlevel', read_only=True)
    
    degree_awarded_by_uuid = serializers.CharField(source='degree_awarded_by.uuid', read_only=True)
    country_uuid= serializers.CharField(source='country.uuid', read_only=True)
    state_uuid = serializers.CharField(source='state.uuid', read_only=True)
    education_level_uuid = serializers.CharField(source='education_level.uuid', read_only=True)


    class Meta:
        model = DegreeAwardedInstitute
        fields = [
            'id', 'uuid', 'name', 'description','degree_awarded_by_uuid','country_uuid','state_uuid','education_level_uuid',
            'degree_awarded_by_id', 'degree_awarded_by_name',
            'country_id', 'country_name',
            'state_id', 'state_name',
            'education_level_id', 'education_level_name'
        ]
        read_only_fields = ['id', 'uuid', 'degree_awarded_by_name', 'country_name', 'state_name', 'education_level_name']





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


class LanguageTestSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(read_only=True)

    class Meta:
        model = LanguageTest
        fields = [
            'id', 'uuid', 'language', 'name', 'fullname', 'description', 
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


        

class LanguagetestmoduleNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguagetestmoduleName
        fields = [
            'id',
            'uuid',
            'name',
            'description',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']

class CLBLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CLBLevel
        fields = [
            'id',
            'uuid',
            'name',
            'description',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']        



class LanguageTestResultSerializer(serializers.ModelSerializer):
    
    language = LanguageSerializer(read_only=True)
    language_test = LanguageTestSerializer(read_only=True)
    module_name = LanguagetestmoduleNameSerializer(read_only=True)
    clb_level = CLBLevelSerializer(read_only=True)


    language_id = serializers.PrimaryKeyRelatedField(
        queryset=Language.objects.all(), source='language', write_only=True
    )
    language_test_id = serializers.PrimaryKeyRelatedField(
        queryset=LanguageTest.objects.all(), source='language_test', write_only=True
    )
    module_name_id = serializers.PrimaryKeyRelatedField(
        queryset=LanguagetestmoduleName.objects.all(), source='languagetest_module_name', write_only=True
    )
    clb_level_id = serializers.PrimaryKeyRelatedField(
        queryset=CLBLevel.objects.all(), source='clb_level', write_only=True
    )

    class Meta:
        model = LanguageTestResult
        fields = [
            'id', 'uuid',
            'language', 'language_id',
            'language_test', 'language_test_id',
            'module_name', 'module_name_id',
            'clb_level', 'clb_level_id',
            'numeric_score', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class StudyLanguageBanchmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyLanguageBanchmark
        fields = ['id', 'uuid', 'name', 'description', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']

class EntranceTestNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntranceTestName
        fields = ['id', 'uuid', 'fullname', 'shortname', 'description', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']

class EntranceTestModuleNameSerializer(serializers.ModelSerializer):
    entrancetest = EntranceTestNameSerializer(read_only=True)
    entrancetest_id = serializers.SlugRelatedField(
        queryset=EntranceTestName.objects.all(),slug_field='uuid', source='entrancetest', write_only=True
    )

    class Meta:
        model = EntranceTestModuleName
        fields = ['id', 'uuid', 'entrancetest', 'entrancetest_id', 'moduleName', 'description', 
                  'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']



class EntranceTestResultSerializer(serializers.ModelSerializer):
    entrancetest = EntranceTestNameSerializer(read_only=True)
    moduleName = EntranceTestModuleNameSerializer(read_only=True)
    entrancetest_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=EntranceTestName.objects.all(),
        source='entrancetest',
        write_only=True
    )
    moduleName_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=EntranceTestModuleName.objects.all(),
        source='moduleName',
        write_only=True
    )
    moduleName_uuid=serializers.CharField(source='moduleName.uuid', read_only=True)


    class Meta:
        model = EntranceTestResult
        fields = ['id', 'uuid', 
                  'entrancetest', 'entrancetest_id', 
                  'moduleName', 'moduleName_id','moduleName_uuid', 
                  'testresult', 'description',
                  'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class OccupationVersionSerializer(serializers.ModelSerializer):
    country = serializers.CharField(read_only=True, source='country.country_name')  # optional display field
    country_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all(),
        source='country',
        write_only=True
    )
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_uuid = serializers.UUIDField(source='country.uuid', read_only=True)

    class Meta:
        model = OccupationVersion
        fields = [
            'id',
            'uuid',
            'country',
            'country_id',
            'country_name',
            'country_uuid',
            'occupation_version',
            'effect_from',
            'valid_upto',
            'description',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']



class OccupationCategorySerializer(serializers.ModelSerializer):

    # Country (display)
    country = serializers.CharField(read_only=True, source='country.name')
    
    # Country (write)
    country_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all(),
        source='country',
        write_only=True
    )

    # Occupation Version (display)
    occupation_version = serializers.CharField(
        read_only=True,
        source='occupationversion.occupation_version'
    )

    # Occupation Version (write)
    occupation_version_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationVersion.objects.all(),
        source='occupationversion',   # ✅ Correct
        write_only=True
    )

    # Additional display fields
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_uuid = serializers.UUIDField(source='country.uuid', read_only=True)

    occupation_version_name = serializers.CharField(source='occupationversion.occupation_version', read_only=True)
    occupation_version_uuid = serializers.UUIDField(source='occupationversion.uuid', read_only=True)

    class Meta:
        model = OccupationCategory
        fields = [
            'id',
            'uuid',

            'country',
            'country_id',
            'country_name',
            'country_uuid',

            'occupation_version',
            'occupation_version_id',
            'occupation_version_name',
            'occupation_version_uuid',

            'occupationcategory',
            'occupationcategorycode',
            'description',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class OccupationLevelCodeSerializer(serializers.ModelSerializer):
    country = serializers.CharField(read_only=True, source='country.name')
    
    # Country (write)
    country_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all(),
        source='country',
        write_only=True
    )
    country_uuid = serializers.UUIDField(source='country.uuid', read_only=True)

    occupation_version = serializers.CharField(read_only=True, source='occupationversion.occupation_version')
    occupation_version_uuid = serializers.UUIDField(source='occupationversion.uuid', read_only=True)

    occupation_version_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationVersion.objects.all(),
        source='occupationversion',
        write_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = OccupationLevelCode
        fields = [
            'id', 'uuid',
            'country', 'country_id','country_uuid',
            'occupation_version', 'occupation_version_id','occupation_version_uuid',
            'occupationlevelcode', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']

# ------------------- OccupationLevel Serializer ------------------- #
class OccupationLevelSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(read_only=True, source='country.name')
    country_uuid = serializers.CharField(read_only=True, source='country.uuid')

    country_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all(),
        source='country',
        write_only=True,
        allow_null=True,
        required=False
    )

    occupationversion = serializers.CharField(read_only=True, source='occupationversion.occupation_version')
    occupationversion_uuid = serializers.CharField(read_only=True, source='occupationversion.uuid')
    occupationversion_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationVersion.objects.all(),
        source='occupationversion',
        write_only=True,
        allow_null=True,
        required=False
    )

    occupationcategory = serializers.CharField(read_only=True, source='occupationcategory.occupationcategory')
    occupationcategory_uuid = serializers.CharField(read_only=True, source='occupationcategory.uuid')

    occupationcategory_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationCategory.objects.all(),
        source='occupationcategory',
        write_only=True,
        allow_null=True,
        required=False
    )

    occupationlevelcode = serializers.CharField(read_only=True, source='occupationlevelcode.occupationlevelcode')
    occupationlevelcode_uuid = serializers.CharField(read_only=True, source='occupationlevelcode.uuid')

    occupationlevelcode_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationLevelCode.objects.all(),
        source='occupationlevelcode',
        write_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = OccupationLevel
        fields = [
            'id', 'uuid',
            'country_name', 'country_id','country_uuid',
            'occupationversion', 'occupationversion_id','occupationversion_uuid',
            'occupationcategory', 'occupationcategory_id','occupationcategory_uuid',
            'occupationlevelcode', 'occupationlevelcode_id','occupationlevelcode_uuid',
            'occupationlevel', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']

# ------------------- OccupationCode Serializer ------------------- #
class OccupationCodeSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(read_only=True, source='country.name')
    country_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all(),
        source='country',
        write_only=True,
        allow_null=True,
        required=False
    )

    occupationversion_name = serializers.CharField(read_only=True, source='occupationversion.occupation_version')
    occupationversion_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationVersion.objects.all(),
        source='occupationversion',
        write_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = OccupationCode
        fields = [
            'id', 'uuid',
            'country_name', 'country_id',
            'occupationversion_name', 'occupationversion_id',
            'occupationcode', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class OccupationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OccupationType
        fields = [
            'id', 'uuid', 'name', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']

# ------------------- OccupationProspect Serializer ------------------- #
class OccupationProspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = OccupationProspect
        fields = [
            'id', 'uuid', 'name', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class OccupationNameSerializer(serializers.ModelSerializer):

    # -------------------- READ ONLY DISPLAY FIELDS -------------------- #
    country = serializers.CharField(read_only=True, source='country.country_name')
    occupationversion = serializers.CharField(read_only=True, source='occupationversion.occupation_version')
    occupationcategory = serializers.CharField(read_only=True, source='occupationcategory.occupationcategory')
    occupationlevel = serializers.CharField(read_only=True, source='occupationlevel.occupationlevel')
    occupationlevelcode = serializers.CharField(read_only=True, source='occupationlevelcode.occupationlevelcode')
    occupationcode = serializers.CharField(read_only=True, source='occupationcode.occupationcode')

    country_uuid= serializers.CharField(read_only=True, source='country.uuid')
    occupationversion_uuid = serializers.CharField(read_only=True, source='occupationversion.uuid')
    occupationcategory_uuid = serializers.CharField(read_only=True, source='occupationcategory.uuid')
    occupationlevel_uuid = serializers.CharField(read_only=True, source='occupationlevel.uuid')
    occupationlevelcode_uuid = serializers.CharField(read_only=True, source='occupationlevelcode.uuid')
    occupationcode_uuid = serializers.CharField(read_only=True, source='occupationcode.uuid')


    # -------------------- WRITE ONLY UUID FIELDS -------------------- #
    country_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all(),
        source='country',
        write_only=True,
        allow_null=True,
        required=False
    )
    occupationversion_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationVersion.objects.all(),
        source='occupationversion',
        write_only=True,
        allow_null=True,
        required=False
    )
    occupationcategory_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationCategory.objects.all(),
        source='occupationcategory',
        write_only=True,
        allow_null=True,
        required=False
    )
    occupationlevel_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationLevel.objects.all(),
        source='occupationlevel',
        write_only=True,
        allow_null=True,
        required=False
    )
    occupationlevelcode_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationLevelCode.objects.all(),
        source='occupationlevelcode',
        write_only=True,
        allow_null=True,
        required=False
    )
    occupationcode_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationCode.objects.all(),
        source='occupationcode',
        write_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = OccupationName
        fields = [
            'id', 'uuid','occupationlevelcode_uuid','occupationcode_uuid',

            # READ fields
            'country', 'occupationlevel_uuid','occupationversion', 'occupationcategory','country_uuid','occupationcategory_uuid',
            'occupationlevel', 'occupationlevelcode', 'occupationcode',

            # WRITE UUID fields
            'country_id', 'occupationversion_id', 'occupationcategory_id','occupationversion_uuid',
            'occupationlevel_id', 'occupationlevelcode_id', 'occupationcode_id',

            # Model fields
            'occupationname', 'description', 'Mainduties',
            'is_deleted', 'created_at', 'updated_at'
        ]

        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


        
class JobProspectSerializer(serializers.ModelSerializer):
    # ---------- Read-only display fields ---------- #
    country = serializers.CharField(read_only=True, source='country.country_name')
    occupationversion = serializers.CharField(read_only=True, source='occupationversion.occupation_version')
    occupationlevelcode = serializers.CharField(read_only=True, source='occupationlevelcode.occupationlevelcode')
    occupationtype = serializers.CharField(read_only=True, source='occupationtype.name')
    occupationcode = serializers.CharField(read_only=True, source='occupationcode.occupationcode')
    occupationprospect = serializers.CharField(read_only=True, source='occupationprospect.name')

    # ---------- Write-only UUID fields ---------- #
    country_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all(),
        source='country',
        write_only=True,
        allow_null=True,
        required=False
    )

    occupationversion_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationVersion.objects.all(),
        source='occupationversion',
        write_only=True,
        allow_null=True,
        required=False
    )

    occupationlevelcode_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationLevelCode.objects.all(),
        source='occupationlevelcode',
        write_only=True,
        allow_null=True,
        required=False
    )

    occupationtype_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationType.objects.all(),
        source='occupationtype',
        write_only=True,
        allow_null=True,
        required=False
    )

    occupationcode_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationCode.objects.all(),
        source='occupationcode',
        write_only=True,
        allow_null=True,
        required=False
    )

    occupationprospect_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationProspect.objects.all(),
        source='occupationprospect',
        write_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = JobProspect
        fields = [
            'id', 'uuid',

            # Readable foreign keys
            'country', 'occupationversion', 'occupationlevelcode',
            'occupationtype', 'occupationcode', 'occupationprospect',

            # Writable UUIDs
            'country_id', 'occupationversion_id', 'occupationlevelcode_id',
            'occupationtype_id', 'occupationcode_id', 'occupationprospect_id',

            'occupationname', 'salarycurrency', 'salaryamount', 'duration',
            'description', 'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']



class RepresentingCountrySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    largest_state_name = serializers.CharField(source='largest_state.name', read_only=True)
    largest_city_name = serializers.CharField(source='largest_city.name', read_only=True)

    class Meta:
        model = RepresentingCountry
        fields = [
            'uuid',
            'country',
            'country_name',
            'continent',
            'short_name',
            'full_name',
            'official_name',
            'capital_city',
            'dial_codes',
            'currency_full_name',
            'currency_short_name',
            'currency_code',
            'no_of_states',
            'no_of_territories',
            'total_states_and_territories',
            'land_area_sq_km',
            'water_area_sq_km',
            'total_area_sq_km',
            'population',
            'religions',
            'monthly_living_cost',
            'unemployment',
            'skilled_shortages',
            'independence_day',
            'government_type',
            'official_language',
            'largest_state',
            'largest_state_name',
            'largest_city',
            'largest_city_name',
            'major_cities',
            'national_animal',
            'national_bird',
            'national_flower',
            'border_countries_and_oceans',
            'national_flag',
            'country_map',
            'status',
            'is_active',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'created_at', 'updated_at',
            'country_name', 'largest_state_name', 'largest_city_name'
        ]

    def create(self, validated_data):
        country = validated_data.get('country')

        # Autofill fields from selected country
        validated_data['continent'] = country.continent
        validated_data['short_name'] = country.shortName
        validated_data['full_name'] = country.fullName
        validated_data['official_name'] = country.officialName
        validated_data['capital_city'] = country.capitalCity
        validated_data['dial_codes'] = country.dialCodes
        validated_data['currency_full_name'] = country.currencyfullname
        validated_data['currency_short_name'] = country.currencyshortname
        validated_data['currency_code'] = country.currencyCode

        return super().create(validated_data)
class VisaMainSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisaMain
        fields = [
            'id', 'uuid', 'name', 'description', 
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class VisaMajorSerializer(serializers.ModelSerializer):
    visamain_name = serializers.CharField(source='visamain.name', read_only=True)

    class Meta:
        model = VisaMajor
        fields = [
            'id', 'uuid', 'visamain', 'visamain_name', 
            'name', 'description', 'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'visamain_name']


# class VisaNameSerializer(serializers.ModelSerializer):
#     country_name = serializers.CharField(source='country.full_name', read_only=True)
#     visamain_name = serializers.CharField(source='visamain.name', read_only=True)
#     visamajor_name = serializers.CharField(source='visamajor.name', read_only=True)

#     class Meta:
#         model = VisaName
#         fields = [
#             'id', 'uuid', 'country', 'country_name',
#             'visamain', 'visamain_name',
#             'visamajor', 'visamajor_name',
#             'full_name', 'short_name', 'description',
#             'is_deleted', 'created_at', 'updated_at'
#         ]
#         read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'country_name', 'visamain_name', 'visamajor_name']


class VisaNameSerializer(serializers.ModelSerializer):
    country = serializers.UUIDField(write_only=True)
    visamain = serializers.UUIDField(write_only=True)
    visamajor = serializers.UUIDField(write_only=True)

    country_name = serializers.CharField(source='country.full_name', read_only=True)
    visamain_name = serializers.CharField(source='visamain.name', read_only=True)
    visamajor_name = serializers.CharField(source='visamajor.name', read_only=True)

    class Meta:
        model = VisaName
        fields = [
            'id', 'uuid',
            'country', 'country_name',
            'visamain', 'visamain_name',
            'visamajor', 'visamajor_name',
            'full_name', 'short_name', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at',
                            'country_name', 'visamain_name', 'visamajor_name']

    def create(self, validated_data):
        country_uuid = validated_data.pop("country")
        visamain_uuid = validated_data.pop("visamain")
        visamajor_uuid = validated_data.pop("visamajor")

        from master.models import RepresentingCountry, VisaMain, VisaMajor

        try:
            validated_data["country"] = RepresentingCountry.objects.get(uuid=country_uuid)
        except RepresentingCountry.DoesNotExist:
            raise serializers.ValidationError({"country": "Invalid country UUID"})

        try:
            validated_data["visamain"] = VisaMain.objects.get(uuid=visamain_uuid)
        except VisaMain.DoesNotExist:
            raise serializers.ValidationError({"visamain": "Invalid visamain UUID"})

        try:
            validated_data["visamajor"] = VisaMajor.objects.get(uuid=visamajor_uuid)
        except VisaMajor.DoesNotExist:
            raise serializers.ValidationError({"visamajor": "Invalid visamajor UUID"})

        return VisaName.objects.create(**validated_data)



class ApplicantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantType
        fields = [
            'id', 'uuid', 'name', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']



class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = [
            "id",
            "uuid",
            "name",
            "description",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = [
            "uuid",
            "name",
            "description",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]



class DocumentNameSerializer(serializers.ModelSerializer):
    document_category_name = serializers.CharField(
        source='document_category.name', read_only=True
    )

    
    document_category = serializers.UUIDField(write_only=True)

    class Meta:
        model = DocumentName
        fields = [
            "uuid",
            "document_category",
            "document_category_name",
            "document_name",
            "description",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]

    def validate_document_category(self, value):
        """
        Validate and convert UUID → actual DocumentCategory instance.
        """
        try:
            return DocumentCategory.objects.get(uuid=value)
        except DocumentCategory.DoesNotExist:
            raise serializers.ValidationError("Invalid document category UUID.")



class PurposeOfVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurposeOfVisit
        fields = [
            "id",
            "uuid",
            "name",
            "description",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]




class DocumentsForSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentsFor
        fields = [
            "uuid",
            "name",
            "description",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]


class RequiredDocumentSerializer(serializers.ModelSerializer):
    # Read-only human-readable fields
    country_name = serializers.CharField(source='country.name', read_only=True)
    visa_main_category_name = serializers.CharField(source='visa_main_category.name', read_only=True)
    visa_major_category_name = serializers.CharField(source='visa_major_category.name', read_only=True)
    visa_name_name = serializers.CharField(source='visa_name.name', read_only=True)
    document_category_name = serializers.CharField(source='document_category.name', read_only=True)
    document_name_name = serializers.CharField(source='document_name.document_name', read_only=True)

    # Accept UUIDs for foreign keys in write operations
    country = serializers.UUIDField(write_only=True)
    visa_main_category = serializers.UUIDField(write_only=True)
    visa_major_category = serializers.UUIDField(write_only=True)
    visa_name = serializers.UUIDField(write_only=True)
    document_category = serializers.UUIDField(write_only=True)
    document_name = serializers.UUIDField(write_only=True)

    class Meta:
        model = RequiredDocument
        fields = [
            "id",
            "uuid",
            "country",
            "country_name",
            "visa_main_category",
            "visa_main_category_name",
            "visa_major_category",
            "visa_major_category_name",
            "visa_name",
            "visa_name_name",
            "document_category",
            "document_category_name",
            "document_name",
            "document_name_name",
            "description",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]

    # Validate-and-convert helper: convert incoming UUID -> model instance
    def _get_instance_by_uuid(self, model_class, value, field_label):
        try:
            return model_class.objects.get(uuid=value, is_deleted=False)
        except model_class.DoesNotExist:
            raise serializers.ValidationError({field_label: f"Invalid {field_label} UUID."})

    def validate_country(self, value):
        return self._get_instance_by_uuid(Country, value, 'country')

    def validate_visa_main_category(self, value):
        return self._get_instance_by_uuid(VisaMain, value, 'visa_main_category')

    def validate_visa_major_category(self, value):
        return self._get_instance_by_uuid(VisaMajor, value, 'visa_major_category')

    def validate_visa_name(self, value):
        return self._get_instance_by_uuid(VisaName, value, 'visa_name')

    def validate_document_category(self, value):
        return self._get_instance_by_uuid(DocumentCategory, value, 'document_category')

    def validate_document_name(self, value):
        return self._get_instance_by_uuid(DocumentName, value, 'document_name')


class ProcessStatusSerializer(serializers.ModelSerializer):
    # Read-only names for related models
    country_name = serializers.CharField(source='country.name', read_only=True)
    visa_main_category_name = serializers.CharField(source='visa_main_category.name', read_only=True)

    # Accept UUIDs for foreign-key fields
    country = serializers.UUIDField(write_only=True)
    visa_main_category = serializers.UUIDField(write_only=True)

    # Now process_status_name is a TEXT field, so:
    process_status_name = serializers.CharField()

    class Meta:
        model = ProcessStatusName
        fields = [
            "id",
            "uuid",
            "country",
            "country_name",
            "visa_main_category",
            "visa_main_category_name",
            "process_status_name",
            # removed: process_status_name_value
            "description",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]

    def _get_instance(self, model_class, value, label):
        try:
            return model_class.objects.get(uuid=value, is_deleted=False)
        except model_class.DoesNotExist:
            raise serializers.ValidationError({label: f"Invalid {label} UUID."})

    def validate_country(self, value):
        return self._get_instance(Country, value, "country")

    def validate_visa_main_category(self, value):
        return self._get_instance(VisaMain, value, "visa_main_category")


class ProcessSubStatusSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    visa_main_category_name = serializers.CharField(source='visa_main_category.name', read_only=True)
    process_status_name_value = serializers.CharField(source='process_status_name.name', read_only=True)

    country = serializers.UUIDField(write_only=True)
    visa_main_category = serializers.UUIDField(write_only=True)
    process_status_name = serializers.UUIDField(write_only=True)

    class Meta:
        model = ProcessSubStatusName
        fields = [
            "id",
            "uuid",
            "country",
            "country_name",
            "visa_main_category",
            "visa_main_category_name",
            "process_status_name",
            "process_status_name_value",
            "process_sub_status_name",
            "description",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]

    def _get_instance(self, model_class, value, label):
        try:
            return model_class.objects.get(uuid=value, is_deleted=False)
        except model_class.DoesNotExist:
            raise serializers.ValidationError({label: f"Invalid {label} UUID."})

    def validate_country(self, value):
        return self._get_instance(Country, value, "country")

    def validate_visa_main_category(self, value):
        return self._get_instance(VisaMain, value, "visa_main_category")

    def validate_process_status_name(self, value):
        return self._get_instance(ProcessStatusName, value, "process_status_name")

    
class ProcessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessType
        fields = [
            "id",
            "uuid",
            "name",
            "description",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]


class PaymentToSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTo
        fields = [
            "id",
            "uuid",
            "name",
            "description",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]



class PaymentCategorySerializer(serializers.ModelSerializer):
    payment_to_name = serializers.CharField(source='payment_to.name', read_only=True)
    payment_to = serializers.UUIDField(write_only=True)

    class Meta:
        model = PaymentCategory
        fields = [
            "id",
            "uuid",
            "payment_to",
            "payment_to_name",
            "payment_category",
            "description",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]

    def validate_payment_to(self, value):
        try:
            return PaymentTo.objects.get(uuid=value, is_deleted=False)
        except PaymentTo.DoesNotExist:
            raise serializers.ValidationError("Invalid or deleted Payment To UUID.")



class CivilIdNameSerializer(serializers.ModelSerializer):
    # Show choice label for valid_type
    valid_type_detail = serializers.SerializerMethodField()

    # Show choice label for valid_duration_unit
    valid_duration_unit_detail = serializers.SerializerMethodField()

    class Meta:
        model = CivilIdName
        fields = [
            'uuid',
            'civil_id_name',
            'authority_full_name',
            'authority_short_name',

            'valid_type',
            'valid_type_detail',

            'valid_duration_value',
            'valid_duration_unit',
            'valid_duration_unit_detail',

            'description',
            'is_deleted',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at','is_deleted']

    def get_valid_type_detail(self, obj):
        return obj.get_valid_type_display() if obj.valid_type else None

    def get_valid_duration_unit_detail(self, obj):
        return obj.get_valid_duration_unit_display() if obj.valid_duration_unit else None
class VisaEligibilityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisaEligibilityType
        fields = [
            'id', 'uuid', 'name', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class VisaStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisaStatus
        fields = [
            'id', 'uuid', 'name', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class PossibilityLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PossibilityLevel
        fields = [
            'id', 'uuid', 'name', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']



#----------------------------occupation-----------------

class JobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = [
            'id',
            'uuid',
            'name',
            'description',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class ModeofSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ModeofSalary
        fields = [
            'id',
            'uuid',
            'name',
            'description',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class ITReturnStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ITReturnStatus
        fields = [
            'id',
            'uuid',
            'name',
            'description',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


#---------------------visa conditions master---------------------------

class WorkRightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkRights
        fields = '__all__'


class WorkRightsDuringStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkRightsDuringStudy
        fields = '__all__'


class WorkRightsDuringVacationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkRightsDuringVacation
        fields = '__all__'


class WorkRightsAfterStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkRightsAfterStudy
        fields = '__all__'


class PRPossibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PRPossibility
        fields = '__all__'


class SpouseCanApplywithCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpouseCanApplywithCandidate
        fields = '__all__'


class SpouseVisaCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpouseVisaCategory
        fields = '__all__'


class SpouseWorkRightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpouseWorkRights
        fields = '__all__'


class ChildrenCanApplywithCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildrenCanApplywithCandidate
        fields = '__all__'


class ChildrenVisaCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildrenVisaCategory
        fields = '__all__'


class ChildrenStudyWorkRightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildrenStudyWorkRights
        fields = '__all__'



#--------------------instituite  master -----------------------------

class InstituteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstituteType
        fields = '__all__'


class InstituteGroupNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstituteGroupName
        fields = '__all__'


class InstituteStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstituteStatus
        fields = '__all__'


class InstitutePrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutePriority
        fields = '__all__'


class InstituteDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstituteDepartment
        fields = '__all__'


class BankAccountForSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccountFor
        fields = '__all__'


class WhenCommissionIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhenCommissionIssue
        fields = '__all__ ,'


class CourseLevelCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseLevelCode
        fields = '__all__'


class CourseLevelSerializer(serializers.ModelSerializer):
    courselevelcode = serializers.CharField(read_only=True, source='courselevelcode.name') 
    courselevelcode_uuid = serializers.CharField(read_only=True, source='courselevelcode.uuid') 

    courselevelcode_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=CourseLevelCode.objects.all(),
        source='courselevelcode',
        write_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = CourseLevel
        fields = [
            'id', 'uuid',
            'courselevelcode', 'courselevelcode_id','courselevelcode_uuid',
            'name', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']

# ------------------- CourseDuration Serializer ------------------- #
class CourseDurationSerializer(serializers.ModelSerializer):
    courselevel = serializers.CharField(read_only=True, source='courselevel.name')
    courselevel_uuid = serializers.CharField(read_only=True, source='courselevel.uuid')

    courselevel_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=CourseLevel.objects.all(),
        source='courselevel',
        write_only=True,
        allow_null=False,
        required=True
    )

    class Meta:
        model = CourseDuration
        fields = [
            'id', 'uuid',
            'courselevel', 'courselevel_id', 'courselevel_uuid',
            'valid_duration_value', 'valid_duration_unit',
            'description', 'is_deleted',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class CourseDividedInSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDividedIn
        fields = '__all__'


class CourseStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStatus
        fields = '__all__'


class IntakeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntakeName
        fields = '__all__'


class CourseStatusIntakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStatusIntake
        fields = '__all__'


class ScholorshipBasedOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholorshipBasedOn
        fields = '__all__'


class RelatedOccupationSerializer(serializers.ModelSerializer):
    # -------------------- READ ONLY DISPLAY FIELDS -------------------- #
    country = serializers.CharField(read_only=True, source='country.country_name')
    occupationversion = serializers.CharField(read_only=True, source='occupationversion.occupation_version')
    occupationcode = serializers.CharField(read_only=True, source='occupationcode.occupationcode')
    occupationname = serializers.CharField(read_only=True, source='occupationname.occupationname')

    # -------------------- WRITE ONLY UUID FIELDS -------------------- #
    country_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all(),
        source='country',
        write_only=True,
        allow_null=True,
        required=False
    )
    occupationversion_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationVersion.objects.all(),
        source='occupationversion',
        write_only=True,
        allow_null=True,
        required=False
    )
    occupationcode_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationCode.objects.all(),
        source='occupationcode',
        write_only=True,
        allow_null=True,
        required=False
    )
    occupationname_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationName.objects.all(),
        source='occupationname',
        write_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = RelatedOccupation
        fields = [
            'id', 'uuid',
            'country', 'occupationversion', 'occupationcode', 'occupationname',
            'country_id', 'occupationversion_id', 'occupationcode_id', 'occupationname_id',
            'relatedoccupation', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']



class OccupationToOccupationSerializer(serializers.ModelSerializer):
    # -------------------- READ ONLY DISPLAY FIELDS -------------------- #
    country = serializers.CharField(read_only=True, source='country.country_name')
    occupationversion = serializers.CharField(read_only=True, source='occupationversion.occupation_version')
    occupationcode = serializers.CharField(read_only=True, source='occupationcode.occupationcode')
    occupationname = serializers.CharField(read_only=True, source='occupationname.occupationname')

    comparecountry = serializers.CharField(read_only=True, source='comparecountry.country_name')
    compareoccupationversion = serializers.CharField(read_only=True, source='compareoccupationversion.occupation_version')
    compareoccupationcode = serializers.CharField(read_only=True, source='compareoccupationcode.occupationcode')
    compareoccupationname = serializers.CharField(read_only=True, source='compareoccupationname.occupationname')

    # -------------------- WRITE ONLY UUID FIELDS -------------------- #
    country_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all(),
        source='country',
        write_only=True,
        allow_null=True,
        required=False
    )
    occupationversion_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationVersion.objects.all(),
        source='occupationversion',
        write_only=True,
        allow_null=True,
        required=False
    )
    occupationcode_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationCode.objects.all(),
        source='occupationcode',
        write_only=True,
        allow_null=True,
        required=False
    )
    occupationname_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationName.objects.all(),
        source='occupationname',
        write_only=True,
        allow_null=True,
        required=False
    )

    comparecountry_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Country.objects.all(),
        source='comparecountry',
        write_only=True,
        allow_null=True,
        required=False
    )
    compareoccupationversion_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationVersion.objects.all(),
        source='compareoccupationversion',
        write_only=True,
        allow_null=True,
        required=False
    )
    compareoccupationcode_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationCode.objects.all(),
        source='compareoccupationcode',
        write_only=True,
        allow_null=True,
        required=False
    )
    compareoccupationname_id = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=OccupationName.objects.all(),
        source='compareoccupationname',
        write_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = OccupationToOccupation
        fields = [
            'id', 'uuid',
            # READ fields
            'country', 'occupationversion', 'occupationcode', 'occupationname',
            'comparecountry', 'compareoccupationversion', 'compareoccupationcode', 'compareoccupationname',

            # WRITE UUID fields
            'country_id', 'occupationversion_id', 'occupationcode_id', 'occupationname_id',
            'comparecountry_id', 'compareoccupationversion_id', 'compareoccupationcode_id', 'compareoccupationname_id',

            # Model fields
            'description', 'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']

        
