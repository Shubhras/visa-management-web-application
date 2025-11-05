from django.contrib.auth import authenticate,get_user_model
from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
# from .process import*

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
    description = serializers.CharField(required=False, allow_blank=True)  # optional

    class Meta:
        model = Gender
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at', 'is_active', 'is_deleted']
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'is_deleted']


class MaritalstatusSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False, allow_blank=True)  # optional

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
        write_only=True
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
    countryName = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        source='countryName',
        write_only=True
    )

    class Meta:
        model = State
        fields = [
            'uuid', 'countryName', 'country_id',
            'stateName', 'stateshortName', 'description',
            'is_active', 'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class DistrictSerializer(serializers.ModelSerializer):
    countryName = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        source='countryName',
        write_only=True
    )
    stateName = StateSerializer(read_only=True)
    state_id = serializers.PrimaryKeyRelatedField(
        queryset=State.objects.all(),
        source='stateName',
        write_only=True
    )

    class Meta:
        model = District
        fields = [
            'uuid', 'countryName', 'country_id',
            'stateName', 'state_id',
            'districtName', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class CitySerializer(serializers.ModelSerializer):
    countryName = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        source='countryName',
        write_only=True
    )
    stateName = StateSerializer(read_only=True)
    state_id = serializers.PrimaryKeyRelatedField(
        queryset=State.objects.all(),
        source='stateName',
        write_only=True
    )
    districtName = DistrictSerializer(read_only=True)
    district_id = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(),
        source='districtName',
        write_only=True
    )

    class Meta:
        model = City
        fields = [
            'uuid', 'countryName', 'country_id',
            'stateName', 'state_id',
            'districtName', 'district_id',
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
    countryName = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        source='countryName',
        write_only=True
    )
    stateName = StateSerializer(read_only=True)
    state_id = serializers.PrimaryKeyRelatedField(
        queryset=State.objects.all(),
        source='stateName',
        write_only=True
    )

    class Meta:
        model = Timezone
        fields = [
            'uuid', 'countryName', 'country_id',
            'stateName', 'state_id',
            'Timezone', 'description',
            'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']


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
    mainarea = StudymainareaSerializer(read_only=True)
    mainarea_id = serializers.PrimaryKeyRelatedField(
        queryset=Studymainarea.objects.all(),
        source='mainarea',
        write_only=True,
        required=False,
        allow_null=True
    )

    Majorarea = StudyMajorAreaSerializer(read_only=True)
    Majorarea_id = serializers.PrimaryKeyRelatedField(
        queryset=Studymajorarea.objects.all(),
        source='majorarea',
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
            'majorarea',
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

# Main Result serializer
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
    process_status_name_value = serializers.CharField(source='process_status_name.name', read_only=True)

    # Accept UUIDs for foreign keys
    country = serializers.UUIDField(write_only=True)
    visa_main_category = serializers.UUIDField(write_only=True)
    process_status_name = serializers.UUIDField(write_only=True)

    class Meta:
        model = ProcessStatus
        fields = [
            "id",
            "uuid",
            "country",
            "country_name",
            "visa_main_category",
            "visa_main_category_name",
            "process_status_name",
            "process_status_name_value",
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
        return self._get_instance(ProcessStatus, value, "process_status_name")



class ProcessSubStatusSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    visa_main_category_name = serializers.CharField(source='visa_main_category.name', read_only=True)
    process_status_name_value = serializers.CharField(source='process_status_name.name', read_only=True)

    country = serializers.UUIDField(write_only=True)
    visa_main_category = serializers.UUIDField(write_only=True)
    process_status_name = serializers.UUIDField(write_only=True)

    class Meta:
        model = ProcessSubStatus
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
        return self._get_instance(ProcessStatus, value, "process_status_name")



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
