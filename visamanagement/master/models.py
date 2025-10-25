
import uuid
from django.db import models

class Gender(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.text
  
class Maritalstatus(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text


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
    relation=models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.relation

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
    short_name = models.CharField(max_length=255, unique=True)
    issuing_authority = models.CharField(max_length=255)
    valid_upto = models.CharField(max_length=255)
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

class EducationLevelCode(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    level_code = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.level_code


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
        return self.level_code.level_code if self.level_code else "No Level Code"
    

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
    Mainarea=models.TextField(max_length=255,null=True,blank=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Mainarea



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
        return self.Majorarea

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
    Academicresulttype=models.TextField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Academicresulttype


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


