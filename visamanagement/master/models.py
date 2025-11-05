
import uuid
from django.db import models
from django.utils import timezone

class Gender(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
  
class Maritalstatus(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class Continents(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name= models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class Country(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    continent=models.ForeignKey(Continents,on_delete=models.SET_NULL,related_name="countries", blank=True, null=True)
    shortName = models.CharField(max_length=50, blank=True, null=True)
    fullName = models.CharField(max_length=50, blank=True, null=True)
    officialName = models.CharField(max_length=50, blank=True, null=True)
    capitalCity = models.CharField(max_length=50, blank=True, null=True)
    dialCodes = models.JSONField(blank=True, null=True)  
    currencyfullname=models.CharField(max_length=50, blank=True, null=True)
    currencyshortname=models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=255)
    currencyCode = models.CharField(max_length=50, blank=True, default="")  
    status = models.BooleanField(default=True)  
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
   

    def __str__(self):
        return self.name



class State(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    countryName=models.ForeignKey(Country,on_delete=models.SET_NULL,related_name="states", blank=True, null=True)
    stateName=models.CharField(max_length=255, unique=True)
    stateshortName=models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.stateName


class District(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    countryName=models.ForeignKey(Country,on_delete=models.SET_NULL,related_name="districts_by_country", blank=True, null=True)
    stateName=models.ForeignKey(State,on_delete=models.SET_NULL,related_name="districts", blank=True, null=True)
    districtName=models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)  
    is_deleted = models.BooleanField(default=False,null=True, blank=True)  
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.districtName


class City(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    countryName=models.ForeignKey(Country,on_delete=models.SET_NULL,  related_name="cities_in_country",  blank=True, null=True)
    stateName=models.ForeignKey(State,on_delete=models.SET_NULL,related_name="cities_in_state", blank=True, null=True)
    districtName=models.ForeignKey(District,on_delete=models.SET_NULL,related_name="cities_in_district", blank=True, null=True)
    cityName=models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False,null=True, blank=True)  
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.cityName


class Relation(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name=models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.name

class Timezone(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    countryName=models.ForeignKey(Country,on_delete=models.SET_NULL,related_name="timezone", blank=True, null=True)
    stateName=models.ForeignKey(State,on_delete=models.SET_NULL,related_name="timezone", blank=True, null=True)
    Timezone =models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.Timezone


class Department(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="Department Name", help_text="Name of the department")
    description = models.TextField(max_length=255, blank=True, verbose_name="Description", help_text="Optional description of the department")
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'is_deleted')

    def __str__(self):
        return self.name

class EmployeeType(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name="Employee Type", help_text="Type of employee")
    description = models.TextField(max_length=255, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CompanyType(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name="Company Type")
    description = models.TextField(max_length=255, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OwnershipType(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_type = models.ForeignKey(CompanyType, on_delete=models.SET_NULL, related_name="ownership_types", blank=True, null=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class StakeholderCategory(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name


class StakeholderType(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(StakeholderCategory, on_delete=models.SET_NULL, related_name="types", blank=True, null=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AccreditationCategory(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AccreditationName(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.ForeignKey("Country", on_delete=models.SET_NULL, related_name="accreditation_names", blank=True, null=True)
    category = models.ForeignKey(AccreditationCategory, on_delete=models.SET_NULL, related_name="accreditation_names", blank=True, null=True)
    full_name = models.CharField(max_length=255, unique=True)
    short_name = models.CharField(max_length=255, null=True,blank=True)
    issuing_authority = models.CharField(max_length=255)
    valid_upto = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(max_length=255, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name





class BankAccountType(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class LicenseName(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  
    country = models.ForeignKey("Country", on_delete=models.SET_NULL, related_name="license_name", blank=True, null=True)
    full_name = models.CharField(max_length=255,blank=True,unique=True)
    short_name = models.CharField(max_length=255,blank=True)
    issuing_authority= models.CharField(max_length=255,blank=True)
    description = models.TextField(max_length=255,blank=True)
    valid_upto = models.CharField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name




class LeadSource(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class InterestLevel(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Priority(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Tags(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ActivityType(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class LostReason(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class LostReasonB2B(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class EducationLevelCode(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    
class EducationLevel(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    level_code = models.ForeignKey(
        EducationLevelCode,
        on_delete=models.SET_NULL,
        related_name="education_levels",
        blank=True,
        null=True
    )
    educationlevel= models.TextField(max_length=255,blank=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.level_code.name if self.level_code else "No Level Code"
    

class  EducationDuration(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    educationlevel = models.ForeignKey(
        EducationLevel,
        on_delete=models.SET_NULL,
        related_name="Education_duration",
        blank=True,
        null=True
    )
    durations=models.IntegerField(null=True,blank=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.durations 
    



class Studymainarea(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name=models.TextField(max_length=255,null=True,blank=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class Studymajorarea(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    mainarea=models.ForeignKey(Studymainarea, on_delete=models.SET_NULL,
        related_name="Studymajor_area",
        blank=True,
        null=True)
    majorarea=models.TextField(null=True,blank=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.majorarea
    

class StudySpecialisation(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    mainarea=models.ForeignKey(Studymainarea, on_delete=models.SET_NULL,
        related_name="Study_Specialisation",
        blank=True,
        null=True)
    majorarea=models.ForeignKey(Studymajorarea, on_delete=models.SET_NULL,
        related_name="StudySpecialisation",
        blank=True,
        null=True)
    studyspecialisation=models.TextField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.studyspecialisation


class AcademicResultType(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name=models.TextField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AcademicResult(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    AcademicResulttype=models.ForeignKey(AcademicResultType, on_delete=models.SET_NULL,
        related_name="Academic_result",
        blank=True,
        null=True)
    Academicresult=models.TextField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Academicresult


class EducationType(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    educationType= models.TextField(max_length=255,blank=True,null=True)
    Perticulars = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.educationType

class MediumofEducation(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name= models.TextField(max_length=255,blank=True,null=True)
    Perticulars = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name




class  Language(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name= models.TextField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class  LanguageTest(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    language=models.ForeignKey(Language, on_delete=models.SET_NULL, related_name="language_test", blank=True, null=True)
    name=models.TextField(max_length=255,blank=True,null=True)
    fullname= models.TextField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class LanguagetestmoduleName(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name=models.TextField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class CLBLevel(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name=models.TextField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class LanguageTestResult(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    language = models.ForeignKey('Language',on_delete=models.SET_NULL,null=True,blank=True,related_name='test_results')
    language_test = models.ForeignKey('LanguageTest',on_delete=models.SET_NULL,null=True,blank=True,related_name='results')
    module_name = models.ForeignKey('LanguagetestmoduleName',  on_delete=models.SET_NULL,null=True,blank=True,related_name='test_results')
    clb_level = models.ForeignKey('CLBLevel', on_delete=models.SET_NULL,null=True,blank=True,related_name='language_test_results'    )

    numeric_score = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.language_test} - {self.language} - {self.module_name}"


class StudyLanguageBanchmark(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name=models.TextField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class EntranceTestName(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    fullname=models.TextField(max_length=255,blank=True,null=True)
    shortname=models.TextField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fullname


class EntranceTestModuleName(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    entrancetest=models.ForeignKey('EntranceTestName',on_delete=models.SET_NULL,null=True,blank=True,related_name='entrance_test')
    moduleName=models.TextField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.moduleName


class EntranceTestResult(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    entrancetest=models.ForeignKey('EntranceTestName',on_delete=models.SET_NULL,null=True,blank=True,related_name='entrance_result')
    moduleName=models.ForeignKey('EntranceTestModuleName',on_delete=models.SET_NULL,null=True,blank=True,related_name='entrance_result')
    testresult=models.TextField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.testresult


class OccupationVersion(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('Country',on_delete=models.SET_NULL,null=True,blank=True,related_name='occupation_versions')
    occupation_version = models.CharField(max_length=255, unique=True)  # duplicate not allowed
    effect_from = models.DateField(null=True, blank=True)
    valid_upto = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.occupation_version
    


class RepresentingCountry(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='representations')
    continent=models.CharField(max_length=50, blank=True, null=True)
    short_name = models.CharField(max_length=50, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    official_name = models.CharField(max_length=255, blank=True, null=True)
    capital_city = models.CharField(max_length=255, blank=True, null=True)
    
    dial_codes = models.JSONField(blank=True, null=True) 
    currency_full_name = models.CharField(max_length=255, blank=True, null=True)
    currency_short_name = models.CharField(max_length=50, blank=True, null=True)
    currency_code = models.CharField(max_length=50, blank=True, default="")
    
    no_of_states = models.IntegerField(default=0)
    no_of_territories = models.IntegerField(default=0)
    total_states_and_territories = models.IntegerField(default=0)
    land_area_sq_km = models.FloatField(blank=True, null=True)
    water_area_sq_km = models.FloatField(blank=True, null=True)
    total_area_sq_km = models.FloatField(blank=True, null=True)
    
    population = models.BigIntegerField(blank=True, null=True)
    religions = models.TextField(blank=True, null=True)
    monthly_living_cost = models.FloatField(blank=True, null=True)
    unemployment = models.FloatField(blank=True, null=True)
    skilled_shortages = models.TextField(blank=True, null=True)
    
    independence_day = models.DateField(blank=True, null=True)
    government_type = models.CharField(max_length=255, blank=True, null=True)
    official_language = models.CharField(max_length=255, blank=True, null=True)
    
    
    largest_state = models.ForeignKey('State', on_delete=models.CASCADE, related_name='representations')
    largest_city = models.ForeignKey('City', on_delete=models.CASCADE, related_name='representations')
    major_cities = models.TextField(blank=True, null=True)
    
    national_animal = models.CharField(max_length=255, blank=True, null=True)
    national_bird = models.CharField(max_length=255, blank=True, null=True)
    national_flower = models.CharField(max_length=255, blank=True, null=True)
    

    border_countries_and_oceans = models.TextField(blank=True, null=True)
    national_flag = models.FileField(upload_to='flags/', blank=True, null=True)
    country_map = models.FileField(upload_to='maps/', blank=True, null=True)
    

    status = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name
    

class VisaMain(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class VisaMajor(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    visamain=models.ForeignKey('VisaMain', on_delete=models.CASCADE, related_name='visamajor')
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class VisaName(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    country=models.ForeignKey('RepresentingCountry', on_delete=models.CASCADE, related_name='visaname')
    visamain=models.ForeignKey('VisaMain', on_delete=models.CASCADE, related_name='visaname')
    visamajor=models.ForeignKey('VisaMajor', on_delete=models.CASCADE, related_name='visaname')
    full_name = models.CharField(max_length=255,unique=True)
    short_name=models.CharField(max_length=255,blank=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name



class ApplicantType(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DocumentCategory(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class DocumentName(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    document_category = models.ForeignKey(DocumentCategory,on_delete=models.CASCADE,related_name='document_names')
    document_name = models.CharField(max_length=255)
    description = models.CharField(max_length=500, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.document_name

class DocumentType(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name    
    

class PurposeOfVisit(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name    
    

class RequiredDocument(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='required_documents')
    visa_main_category = models.ForeignKey('master.VisaMain', on_delete=models.CASCADE, related_name='required_documents')
    visa_major_category = models.ForeignKey('master.VisaMajor', on_delete=models.CASCADE, related_name='required_documents')
    visa_name = models.ForeignKey('VisaName', on_delete=models.CASCADE, related_name='required_documents')
    document_category = models.ForeignKey('DocumentCategory', on_delete=models.CASCADE, related_name='required_documents')
    document_name = models.ForeignKey('DocumentName', on_delete=models.CASCADE, related_name='required_documents')
    description = models.CharField(max_length=500, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.country} - {self.visa_name} - {self.document_name}"



class ProcessStatus(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='process_statuses')
    visa_main_category = models.ForeignKey('master.VisaMain', on_delete=models.CASCADE, related_name='process_statuses')
    process_status_name = models.ForeignKey('ProcessStatusName', on_delete=models.CASCADE, related_name='process_statuses')
    description = models.CharField(max_length=500, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.country} - {self.visa_main_category} - {self.process_status_name}"



class ProcessSubStatus(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='process_sub_statuses')
    visa_main_category = models.ForeignKey('master.VisaMain', on_delete=models.CASCADE, related_name='process_sub_statuses')
    process_status_name = models.ForeignKey('ProcessStatusName', on_delete=models.CASCADE, related_name='process_sub_statuses')
    process_sub_status_name = models.CharField(max_length=255)
    description = models.CharField(max_length=500, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.country} - {self.visa_main_category} - {self.process_status_name} - {self.process_sub_status_name}"


class ProcessType(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PaymentTo(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class PaymentCategory(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    payment_to = models.ForeignKey(PaymentTo, on_delete=models.CASCADE, related_name="payment_categories")
    payment_category = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.payment_category} ({self.payment_to.name})"


