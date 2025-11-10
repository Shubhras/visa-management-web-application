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
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class AcademicResultTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicResultType
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



class AcademicResultSerializer(serializers.ModelSerializer):
    # Show type details as separate keys
    AcademicResulttype_uuid = serializers.SerializerMethodField()
    AcademicResulttype_name = serializers.SerializerMethodField()

    # Accept UUID to set the relation
    AcademicResulttype_id = serializers.SlugRelatedField(
        queryset=AcademicResultType.objects.all(),
        source='AcademicResulttype',
        slug_field='uuid',
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
            'updated_at'
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
    entrancetest_id = serializers.PrimaryKeyRelatedField(
        queryset=EntranceTestName.objects.all(), source='entrancetest', write_only=True
    )

    class Meta:
        model = EntranceTestModuleName
        fields = ['id', 'uuid', 'entrancetest', 'entrancetest_id', 'moduleName', 'description', 
                  'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']



class EntranceTestResultSerializer(serializers.ModelSerializer):
    entrancetest = EntranceTestNameSerializer(read_only=True)
    entrancetest_id = serializers.PrimaryKeyRelatedField(
        queryset=EntranceTestName.objects.all(), source='entrancetest', write_only=True
    )
    
    moduleName = EntranceTestModuleNameSerializer(read_only=True)
    moduleName_id = serializers.PrimaryKeyRelatedField(
        queryset=EntranceTestModuleName.objects.all(), source='moduleName', write_only=True
    )

    class Meta:
        model = EntranceTestResult
        fields = ['id', 'uuid', 
                  'entrancetest', 'entrancetest_id', 
                  'moduleName', 'moduleName_id', 
                  'testresult', 'description',
                  'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class OccupationVersionSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        source='country',
        write_only=True
    )

    class Meta:
        model = OccupationVersion
        fields = [
            'id',
            'uuid',
            'country',
            'country_id',
            'occupation_version',
            'effect_from',
            'valid_upto',
            'description',
            'is_deleted',
            'created_at',
            'updated_at'
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
        read_only_fields = ['created_at', 'updated_at', 'country_name', 'largest_state_name', 'largest_city_name']


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


class VisaNameSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.full_name', read_only=True)
    visamain_name = serializers.CharField(source='visamain.name', read_only=True)
    visamajor_name = serializers.CharField(source='visamajor.name', read_only=True)

    class Meta:
        model = VisaName
        fields = [
            'id', 'uuid', 'country', 'country_name',
            'visamain', 'visamain_name',
            'visamajor', 'visamajor_name',
            'full_name', 'short_name', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'country_name', 'visamain_name', 'visamajor_name']


class ApplicantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantType
        fields = [
            'id', 'uuid', 'name', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']