import uuid
from django.db import models 
from django.utils import timezone 

class Gender(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
  
class Maritalstatus(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class Continents(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name= models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class Country(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    continent=models.ForeignKey(Continents,on_delete=models.PROTECT,related_name="countries", blank=True, null=True)
    shortName = models.CharField(max_length=250, blank=True, null=True)
    fullName = models.CharField(max_length=250, blank=True, null=True)
    officialName = models.CharField(max_length=2250, blank=True, null=True)
    capitalCity = models.CharField(max_length=250, blank=True, null=True)
    dialCodes = models.JSONField(blank=True, null=True)  
    currencyfullname=models.CharField(max_length=250, blank=True, null=True)
    currencyshortname=models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(max_length=255,null=True, blank=True)
    currencyCode = models.CharField(max_length=250, blank=True, default="")  
    status = models.BooleanField(default=True)  
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('continent', 'name')
   

    def __str__(self):
        return self.name



class State(models.Model):
    STATE_CHOICES = (
        ("STATE", "State"),
        ("TERRITORY","Territory"),
    )
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    countryName=models.ForeignKey(Country,on_delete=models.PROTECT,related_name="states", blank=True, null=True)
    stateName=models.CharField(max_length=255)
    state = models.CharField(max_length=20, choices=STATE_CHOICES)
    stateshortName=models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(max_length=255,blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        unique_together = ('countryName', 'stateName')



    def __str__(self):
        return self.stateName if self.stateName else "Unnamed stateName"


class District(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    countryName = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True)
    stateName = models.ForeignKey(State, on_delete=models.PROTECT, blank=True, null=True)
    districtName = models.CharField(max_length=255)
    description = models.TextField(max_length=255,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  
    is_deleted = models.BooleanField(default=False,null=True, blank=True)  
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        unique_together = ('districtName', 'stateName', 'countryName')

    def __str__(self):
        return self.districtName


class City(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    countryName=models.ForeignKey(Country,on_delete=models.PROTECT,  related_name="cities_in_country",  blank=True, null=True)
    stateName=models.ForeignKey(State,on_delete=models.PROTECT,related_name="cities_in_state", blank=True, null=True)
    districtName=models.ForeignKey(District,on_delete=models.PROTECT,related_name="cities_in_district", blank=True, null=True)
    cityName=models.CharField(max_length=255)
    description = models.TextField(max_length=255,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False,null=True, blank=True)  
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        unique_together = ('districtName', 'stateName', 'countryName','cityName')

    def __str__(self):
        return self.cityName


class Relation(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name=models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.name


class CivilIdName(models.Model):
    VALID_TYPE_CHOICES = (
        ("Permanent", "Permanent"),
        ("Valid Upto", "Valid Upto"),
        ("Date","Date")
    )
 
    VALID_UNIT_CHOICES = (
        ("Months", "Months"),
        ("Weeks","Weeks"),
        ("Years", "Years"),
    )
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
 
    civil_id_name = models.CharField(max_length=255)
    authority_full_name = models.CharField(max_length=255,blank=True, null=True)
    authority_short_name = models.CharField(max_length=255, blank=True, null=True)
 
    valid_type = models.CharField(max_length=20, choices=VALID_TYPE_CHOICES, blank=True, null=True)
    valid_duration_value = models.IntegerField(blank=True, null=True)
    valid_date=models.DateField(blank=True, null=True)
    valid_duration_unit = models.CharField(max_length=20, choices=VALID_UNIT_CHOICES, blank=True, null=True)
    description = models.CharField(max_length=2500, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return self.civil_id_name
    
    

class Timezone(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    countryName=models.ForeignKey(Country,on_delete=models.PROTECT,related_name="timezone", blank=True, null=True)
    stateName=models.ForeignKey(State,on_delete=models.PROTECT,related_name="timezone", blank=True, null=True)
    Timezone =models.CharField(max_length=255)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        unique_together = ('Timezone', 'countryName')

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
    company_type = models.ForeignKey(CompanyType, on_delete=models.PROTECT, related_name="ownership_types", blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'company_type')

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
    category = models.ForeignKey(StakeholderCategory, on_delete=models.PROTECT, related_name="types", blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'category')
    

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
    VALID_TYPE_CHOICES = (
        ("Permanent", "Permanent"),
        ("Valid Upto", "Valid Upto"),
        ("Date","Date")
    )
 
    VALID_UNIT_CHOICES = (
        ("Months", "Months"),
        ("Weeks","Weeks"),
        ("Years", "Years"),
    )
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(AccreditationCategory, on_delete=models.PROTECT, related_name="accreditation_names", blank=True, null=True)
    full_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255, null=True,blank=True)
    issuing_authority = models.CharField(max_length=255,blank=True, null=True)
    valid_type = models.CharField(max_length=20, choices=VALID_TYPE_CHOICES,null=True,blank=True)
    valid_duration_value = models.IntegerField(blank=True, null=True)
    valid_date=models.DateField(blank=True, null=True)
    valid_duration_unit = models.CharField(max_length=20, choices=VALID_UNIT_CHOICES, blank=True, null=True)
    description = models.TextField(max_length=255, null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['full_name', 'category'], name='unique_fullname_per_country_category')
        ]

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

    VALID_TYPE_CHOICES = (
        ("Permanent", "Permanent"),
        ("Valid Upto", "Valid Upto"),
        ("Date","Date")
    )
 
    VALID_UNIT_CHOICES = (
        ("Months", "Months"),
        ("Weeks","Weeks"),
        ("Years", "Years"),
    )
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  
    country = models.ForeignKey("Country", on_delete=models.PROTECT, related_name="license_name", blank=True, null=True)
    full_name = models.CharField(max_length=255,blank=True)
    short_name = models.CharField(max_length=255,blank=True, null=True,unique=False)
    issuing_authority= models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    valid_type = models.CharField(max_length=20, choices=VALID_TYPE_CHOICES,null=True,blank=True)
    valid_duration_value = models.IntegerField(blank=True, null=True)
    valid_date=models.DateField(blank=True, null=True)
    valid_duration_unit = models.CharField(max_length=20, choices=VALID_UNIT_CHOICES, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['full_name', 'country'], name='unique_fullname_per_country')
        ]

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
    name = models.IntegerField(unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.name)

    
class EducationLevel(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    level_code = models.ForeignKey(
        EducationLevelCode,
        on_delete=models.PROTECT,
        related_name="education_levels",
        blank=True,
        null=True
    )
    educationlevel= models.CharField(max_length=255,blank=True)
    durations=models.IntegerField(null=True,blank=True,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        pass


    def __str__(self):
        return self.educationlevel
    

class  EducationDuration(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    educationlevel = models.ForeignKey(
        EducationLevel,
        on_delete=models.PROTECT,
        related_name="Education_duration",
        blank=True,
        null=True
    )
    durations=models.IntegerField(null=True,blank=True,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('durations', 'educationlevel')

    def __str__(self):
        return self.durations 
    
class Studymainarea(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name=models.CharField(max_length=255)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Studymajorarea(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    mainarea=models.ForeignKey(Studymainarea, on_delete=models.PROTECT,
        related_name="Studymajor_area",
        blank=True,
        null=True)
    majorarea=models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('mainarea', 'majorarea')

    def __str__(self):
        return self.majorarea
    

class StudySpecialisation(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    mainarea=models.ForeignKey(Studymainarea, on_delete=models.PROTECT,
        related_name="Study_Specialisation",
        blank=True,
        null=True)
    majorarea=models.ForeignKey(Studymajorarea, on_delete=models.PROTECT,
        related_name="StudySpecialisation",
        blank=True,
        null=True)
    studyspecialisation=models.CharField(max_length=255)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('mainarea', 'majorarea','studyspecialisation')

    def __str__(self):
        return self.studyspecialisation


class AcademicResultType(models.Model):
    VALID_TYPE_CHOICES = (
        ("Numeric", "Numeric"),
        ("Text", "Text")
    )
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name=models.CharField(max_length=255,blank=True,null=True)
    datatype=models.CharField(max_length=250,choices=VALID_TYPE_CHOICES,blank=True, null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AcademicResult(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    AcademicResulttype=models.ForeignKey(AcademicResultType, on_delete=models.PROTECT,
        related_name="Academic_result",
        blank=True,
        null=True)
    Academicresult=models.CharField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('AcademicResulttype','Academicresult')

    def __str__(self):
        return self.Academicresult


class EducationType(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    educationType= models.CharField(max_length=255,blank=True,null=True)
    Perticulars = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.educationType

class MediumofEducation(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name= models.CharField(max_length=255,unique=True)
    perticulars = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class ECAFor(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name= models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class ECAAwardingBody(models.Model):
    VALID_UNIT_CHOICES = (
        ("Months", "Months"),
        ("Weeks","Weeks"),
        ("Years", "Years"),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey("Country", on_delete=models.PROTECT, related_name="Country_ECAAwarding_body", blank=True, null=True)
    ecafor=models.ForeignKey("ECAFor", to_field="uuid", db_column="ecafor_id", on_delete=models.PROTECT, related_name="ECAFor_ECAAwarding_body", blank=True, null=True)
    valid_duration_value = models.IntegerField(blank=True, null=True)
    eca_body_full_name = models.CharField(max_length=255,blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    eca_body_short_name = models.CharField(max_length=100,blank=True, null=True)
    eca_valid_period = models.CharField(max_length=250,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('country','ecafor','eca_body_full_name')


    
    def __str__(self):
        return f"{self.eca_body_full_name} ({self.eca_body_short_name}) - {self.country}"


class AcademicResultComparison(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    original_result_type = models.ForeignKey(AcademicResultType, on_delete=models.PROTECT, related_name='original_comparisons')
    original_result = models.ForeignKey(AcademicResult, on_delete=models.PROTECT, related_name='original_comparisons')
    compare_result_type = models.ForeignKey(AcademicResultType, on_delete=models.PROTECT, related_name='compare_comparisons')
    compare_result = models.ForeignKey(AcademicResult, on_delete=models.PROTECT, related_name='compare_comparisons')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('original_result_type','compare_result_type','compare_result')

    def __str__(self):
        return f"{self.original_result} vs {self.compare_result}"

class DegreeAwardedBy(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)    
    country = models.ForeignKey("Country", on_delete=models.PROTECT, blank=True, null=True, related_name="degree_awarded_by_country")
    education_level = models.ForeignKey("EducationLevel", on_delete=models.PROTECT, blank=True, null=True, related_name="degree_awarded_by_education_level")
    degree_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('country','education_level')

    

    def __str__(self):
        return f"{self.degree_name}"


class DegreeAwardedInstitute(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey("Country", on_delete=models.PROTECT, blank=True, null=True, related_name="degree_by_instuite")
    state = models.ForeignKey("State", on_delete=models.PROTECT, blank=True, null=True, related_name="degree_by_state_instituite")
    education_level = models.ForeignKey("EducationLevel", on_delete=models.PROTECT, blank=True, null=True, related_name="degree_by_education_level")
    degree_awarded_by = models.ForeignKey(DegreeAwardedBy, on_delete=models.PROTECT, related_name='institutes')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('degree_awarded_by', 'education_level','country')

    def __str__(self):
        return f"{self.name}"

class DocumentCategory(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('name', 'is_deleted')


    def __str__(self):
        return self.name
    
    
class DocumentName(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    document_category = models.ForeignKey(DocumentCategory,on_delete=models.PROTECT,related_name='document_names')
    document_name = models.CharField(max_length=255)
    description = models.CharField(max_length=500, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('document_category', 'document_name')


    def __str__(self):
        return self.document_name


class DocumentType(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name    
    

class PurposeOfVisit(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


    

    def __str__(self):
        return self.name    
    

class DocumentsFor(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name="Documents For")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




    def __str__(self):
        return self.name



class RequiredDocument(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('Country', on_delete=models.PROTECT, related_name='required_documents')
    visa_main_category = models.ForeignKey('master.VisaMain', on_delete=models.PROTECT, related_name='required_documents')
    visa_major_category = models.ForeignKey('master.VisaMajor', on_delete=models.PROTECT, related_name='required_documents')
    visa_name = models.ForeignKey('VisaName', on_delete=models.PROTECT, related_name='required_documents')
    document_category = models.ForeignKey('DocumentCategory', on_delete=models.PROTECT, related_name='required_documents')
    document_name = models.ForeignKey('DocumentName', on_delete=models.PROTECT, related_name='required_documents')
    description = models.CharField(max_length=500, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('country','visa_main_category','visa_major_category','visa_name','document_category','document_name')
    

    def __str__(self):
        return f"{self.country} - {self.visa_name} - {self.document_name}"



class ProcessStatusName(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('Country', on_delete=models.PROTECT, related_name='process_statuses')
    visa_main_category = models.ForeignKey('master.VisaMain', on_delete=models.PROTECT, related_name='process_statuses')
    process_status_name = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('country','process_status_name','visa_main_category')

    def __str__(self):
        return f"{self.country} - {self.visa_main_category} - {self.process_status_name}"



class ProcessSubStatusName(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('Country', on_delete=models.PROTECT, related_name='process_sub_statuses')
    visa_main_category = models.ForeignKey('master.VisaMain', on_delete=models.PROTECT, related_name='process_sub_statuses')
    process_status_name = models.ForeignKey('ProcessStatusName', on_delete=models.PROTECT, related_name='process_sub_statuses')
    process_sub_status_name = models.CharField(max_length=255)
    description = models.CharField(max_length=500, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together =('country','visa_main_category','process_status_name','process_sub_status_name')

    def __str__(self):
        return f"{self.country} - {self.visa_main_category} - {self.process_status_name} - {self.process_sub_status_name}"


class ProcessType(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


  

    def __str__(self):
        return self.name



class PaymentTo(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
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
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together =('payment_to','payment_category')

    def __str__(self):
        return f"{self.payment_category} ({self.payment_to.name})"



    
class  Language(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name= models.CharField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class  LanguageTest(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    language=models.ForeignKey(Language, on_delete=models.PROTECT, related_name="language_test", blank=True, null=True)
    name=models.CharField(max_length=255,blank=True,null=True)
    fullname= models.TextField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('language', 'name')




    def __str__(self):
        return self.name



class LanguagetestmoduleName(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name=models.CharField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class CLBLevel(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name=models.CharField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class LanguageTestResult(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    language = models.ForeignKey(Language,on_delete=models.PROTECT,null=True,blank=True,related_name='test_results')
    language_test = models.ForeignKey('LanguageTest',on_delete=models.PROTECT,null=True,blank=True,related_name='results')
    module_name = models.ForeignKey('LanguagetestmoduleName',  on_delete=models.PROTECT,null=True,blank=True,related_name='test_results')
    lb_level = models.ForeignKey('StudyLanguageBanchmark', on_delete=models.PROTECT,null=True,blank=True,related_name='language_test_results')

    numeric_score = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    description =  models.TextField(max_length=255,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('language', 'language_test','module_name','lb_level','numeric_score')

    def __str__(self):
        return f"{self.language_test} - {self.language} - {self.module_name}"



class StudyLanguageBanchmark(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name=models.CharField(max_length=255,blank=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class EntranceTestName(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    fullname=models.CharField(max_length=255,blank=True,null=True,unique=True)
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
    entrancetest=models.ForeignKey('EntranceTestName',on_delete=models.PROTECT,null=True,blank=True,related_name='entrance_test')
    moduleName=models.CharField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('entrancetest', 'moduleName')

    def __str__(self):
        return self.moduleName


class EntranceTestResult(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    entrancetest=models.ForeignKey('EntranceTestName',on_delete=models.PROTECT,null=True,blank=True,related_name='entrance_result')
    moduleName=models.ForeignKey('EntranceTestModuleName',on_delete=models.PROTECT,null=True,blank=True,related_name='entrance_result')
    testresult=models.CharField(max_length=255,blank=True,null=True)
    description = models.TextField(max_length=255,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('entrancetest', 'moduleName','testresult')

    def __str__(self):
        return self.testresult




class JobType(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ModeofSalary(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ITReturnStatus(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OccupationVersion(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('RepresentingCountry',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_version')
    occupation_version = models.CharField(max_length=255)  
    effect_from = models.DateField(null=True, blank=True)
    valid_upto = models.DateField(null=True, blank=True)
    description =  models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('occupation_version', 'country')

    def __str__(self):
        return self.occupation_version



class OccupationCategory(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('RepresentingCountry',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_category')
    occupationversion =models.ForeignKey('OccupationVersion',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_category')
    occupationcategory =  models.CharField(max_length=255,blank=True)
    occupationcategorycode =  models.CharField(max_length=255,blank=True)
    description =  models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('occupationversion', 'country','occupationcategory')
    def __str__(self):
        return self.occupationcategory
    


class OccupationLevelCode(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('RepresentingCountry',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_level_code')
    occupationversion =models.ForeignKey('OccupationVersion',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_level_code')
    occupationlevelcode =  models.CharField(max_length=255,blank=True)
    description =  models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('occupationversion', 'country','occupationlevelcode')
    def __str__(self):
        return self.occupationlevelcode
    
class OccupationLevel(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('RepresentingCountry',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_level')
    occupationversion =models.ForeignKey('OccupationVersion',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_level')
    occupationcategory =models.ForeignKey('OccupationCategory',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_level')
    occupationlevelcode =models.ForeignKey('OccupationLevelCode',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_level')
    occupationlevel =  models.CharField(max_length=255,blank=True)
    description =  models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('occupationcategory', 'country','occupationversion','occupationlevelcode','occupationlevel')
    def __str__(self):
        return self.occupationlevel


class OccupationCode(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('RepresentingCountry',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_code')
    occupationversion =models.ForeignKey('OccupationVersion',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_code')
    occupationcode =  models.CharField(max_length=255,blank=True)
    description =  models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('occupationcode', 'country','occupationversion')
    def __str__(self):
        return self.occupationcode
    


class OccupationName(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('RepresentingCountry',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_name')
    occupationversion =models.ForeignKey('OccupationVersion',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_name')
    occupationcategory =models.ForeignKey('OccupationCategory',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_name')
    occupationlevel =models.ForeignKey('OccupationLevel',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_name')
    occupationlevelcode =models.ForeignKey('OccupationLevelCode',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_name')
    occupationcode =models.ForeignKey('OccupationCode',on_delete=models.PROTECT,null=True,blank=True,related_name='occupation_name')
    occupationname =  models.CharField(max_length=255,blank=True)
    description =  models.TextField(max_length=255,blank=True)
    Mainduties=models.TextField(max_length=500,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('occupationcategory', 'country','occupationversion','occupationlevelcode','occupationlevel','occupationcode')
    
    def __str__(self):
        return self.occupationname



class OccupationType(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class OccupationProspect(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Designation(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('RepresentingCountry',on_delete=models.SET_NULL,null=True,blank=True,related_name='designation')
    occupationversion =models.ForeignKey('OccupationVersion',on_delete=models.SET_NULL,null=True,blank=True,related_name='designation')
    occupationname =models.ForeignKey('OccupationName',on_delete=models.SET_NULL,null=True,blank=True,related_name='designation')
    occupationcode =models.ForeignKey('OccupationCode',on_delete=models.SET_NULL,null=True,blank=True,related_name='designation')
    designation=models.CharField(max_length=250,blank=True, null=True)
    description =  models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('occupationname', 'country','occupationversion','occupationcode','designation')
    def __str__(self):
        return self.designation



    

class JobProspect(models.Model):
    VALID_UNIT_CHOICES = (
        ("Hour", "Hour"),
        ("Month","Month"),
        ("Year", "Year"),
    )

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('RepresentingCountry',on_delete=models.SET_NULL,null=True,blank=True,related_name='job_prospect')
    occupationversion =models.ForeignKey('OccupationVersion',on_delete=models.SET_NULL,null=True,blank=True,related_name='job_prospect')
    occupationlevelcode =models.ForeignKey('OccupationLevelCode',on_delete=models.SET_NULL,null=True,blank=True,related_name='job_prospect')
    occupationtype =models.ForeignKey('OccupationType',on_delete=models.SET_NULL,null=True,blank=True,related_name='job_prospect')
    occupationcode =models.ForeignKey('OccupationCode',on_delete=models.SET_NULL,null=True,blank=True,related_name='job_prospect')
    occupationprospect =models.ForeignKey('OccupationProspect',on_delete=models.SET_NULL,null=True,blank=True,related_name='job_prospect')
    occupationname =  models.CharField(max_length=255,blank=True)
    salarycurrency=models.TextField(max_length=255,blank=True,null=True)
    salaryamount=models.IntegerField(null=True,blank=True)
    duration=models.CharField(max_length=250,choices=VALID_UNIT_CHOICES,blank=True, null=True)
    description =  models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('occupationtype', 'country','occupationversion','occupationlevelcode')
    def __str__(self):
        return self.occupationname




class RelatedOccupation(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('Country',on_delete=models.SET_NULL,null=True,blank=True,related_name='related_name')
    occupationversion =models.ForeignKey('OccupationVersion',on_delete=models.SET_NULL,null=True,blank=True,related_name='related_name')
    occupationcode =models.ForeignKey('OccupationCode',on_delete=models.SET_NULL,null=True,blank=True,related_name='related_name')
    occupationname =models.ForeignKey('OccupationName',on_delete=models.SET_NULL,null=True,blank=True,related_name='related_name')
    relatedoccupation =  models.CharField(max_length=255,blank=True)
    description =  models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('occupationcode', 'country','occupationversion')
    def __str__(self):
        return self.relatedoccupation

    

class OccupationToOccupation(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('Country',on_delete=models.SET_NULL,null=True,blank=True,related_name='Occupation_Occupation')
    occupationversion =models.ForeignKey('OccupationVersion',on_delete=models.SET_NULL,null=True,blank=True,related_name='Occupation_Occupation')
    occupationcode =models.ForeignKey('OccupationCode',on_delete=models.SET_NULL,null=True,blank=True,related_name='Occupation_Occupation')
    occupationname =models.ForeignKey('OccupationName',on_delete=models.SET_NULL,null=True,blank=True,related_name='Occupation_Occupation')
    comparecountry = models.ForeignKey('Country',on_delete=models.SET_NULL,null=True,blank=True,related_name='Occupation_To_Occupation')
    compareoccupationversion =models.ForeignKey('OccupationVersion',on_delete=models.SET_NULL,null=True,blank=True,related_name='Occupation_To_Occupation')
    compareoccupationcode =models.ForeignKey('OccupationCode',on_delete=models.SET_NULL,null=True,blank=True,related_name='Occupation_To_Occupation')
    compareoccupationname =models.ForeignKey('OccupationName',on_delete=models.SET_NULL,null=True,blank=True,related_name='Occupation_To_Occupation')
    description =  models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('occupationcode', 'country','occupationversion')
    def __str__(self):
        return self.country




class RepresentingCountry(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='representations')
    continent=models.CharField(max_length=250, blank=True, null=True)
    short_name = models.CharField(max_length=250, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    official_name = models.CharField(max_length=255, blank=True, null=True)
    capital_city = models.CharField(max_length=255, blank=True, null=True)
    dial_codes = models.JSONField(blank=True, null=True) 
    currency_full_name = models.CharField(max_length=255, blank=True, null=True)
    currency_short_name = models.CharField(max_length=250, blank=True, null=True)
    currency_code = models.CharField(max_length=250, blank=True, default="")
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
    largest_state = models.ForeignKey('State', on_delete=models.PROTECT, related_name='representations',blank=True, null=True)
    smallest_state = models.ForeignKey('State', on_delete=models.PROTECT, related_name='representations_small_state',blank=True, null=True)
    # largest_city = models.ForeignKey('City', on_delete=models.PROTECT, related_name='representations',blank=True, null=True)
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
        return self.full_name if self.full_name else "Unnamed Country"
    

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
    country=models.ForeignKey('RepresentingCountry', on_delete=models.CASCADE, related_name='visamajor',null=True,blank=True)
    visamain=models.ForeignKey('VisaMain', on_delete=models.CASCADE, related_name='visamajor')
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('country','visamain','name')

    def __str__(self):
        return self.name

class VisaName(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    country=models.ForeignKey('RepresentingCountry', on_delete=models.CASCADE, related_name='visaname')
    visamain=models.ForeignKey('VisaMain', on_delete=models.CASCADE, related_name='visaname')
    visamajor=models.ForeignKey('VisaMajor', on_delete=models.CASCADE, related_name='visaname')
    full_name = models.CharField(max_length=255)
    short_name=models.CharField(max_length=255,blank=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('visamain','visamajor','full_name','country')

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


    
    
class VisaEligibilityType(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class VisaStatus(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    


class PossibilityLevel(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class WorkRights(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class WorkRightsDuringStudy(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class WorkRightsDuringVacation(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class WorkRightsAfterStudy(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class PRPossibility(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    



class SpouseCanApplywithCandidate(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class CivilIdName(models.Model):
    VALID_TYPE_CHOICES = (
        ("Permanent", "Permanent"),
        ("Valid Upto", "Valid Upto"),
        ("Date","Date")
    )
 
    VALID_UNIT_CHOICES = (
        ("Months", "Months"),
        ("Weeks","Weeks"),
        ("Years", "Years"),
    )

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    civil_id_name = models.CharField(max_length=255)
    authority_full_name = models.CharField(max_length=255, blank=True, null=True)
    authority_short_name = models.CharField(max_length=255, blank=True, null=True)

    valid_type = models.CharField(max_length=20, choices=VALID_TYPE_CHOICES,blank=True, null=True)
    valid_duration_value = models.IntegerField(blank=True, null=True)
    valid_duration_unit = models.CharField(max_length=20, choices=VALID_UNIT_CHOICES, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.civil_id_name

class SpouseVisaCategory(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    visamain=models.ForeignKey('VisaMain', on_delete=models.CASCADE, related_name='spousevisa')
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.visamain

class SpouseWorkRights(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ChildrenCanApplywithCandidate(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ChildrenVisaCategory(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    visamain=models.ForeignKey('VisaMain', on_delete=models.CASCADE, related_name='childrenvisa')
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.visamain


class ChildrenStudyWorkRights(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class InstituteType(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class InstituteGroupName(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class InstituteStatus(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class InstitutePriority(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class InstituteDepartment(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class BankAccountFor(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class WhenCommissionIssue(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CourseLevelCode(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class CourseLevel(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    courselevelcode=models.ForeignKey(CourseLevelCode,on_delete=models.SET_NULL,related_name="course_level", blank=True, null=True)
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('courselevelcode', 'name')

    def __str__(self):
        return self.name


class CourseDuration(models.Model):
    VALID_UNIT_CHOICES = (
        ("Months", "Months"),
        ("Weeks","Weeks"),
        ("Years", "Years"),
    )
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    courselevel=models.ForeignKey(CourseLevel,on_delete=models.SET_NULL,related_name="course_duration", blank=True, null=True)
    valid_duration_value = models.IntegerField(blank=True, null=True)
    valid_duration_unit = models.CharField(max_length=20, choices=VALID_UNIT_CHOICES, blank=True, null=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('courselevel', 'valid_duration_value')

    def __str__(self):
        return self.valid_duration_value


class CourseDividedIn(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class CourseStatus(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class IntakeName(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CourseStatusIntake(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ScholorshipBasedOn(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class FactorFor(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    


class AgeGroup(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AcademicResultGroup(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class BacklogsGroup(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    


class GAPGroup(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class LanguageAbilityGroup(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class EntranceTestAbilityGroup(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class StudyFactorAge(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    factor_for = models.ForeignKey(FactorFor, on_delete=models.CASCADE, related_name="ages")
    study_age_group = models.ForeignKey(AgeGroup, on_delete=models.CASCADE, related_name="ages")
    minimum_age_months = models.PositiveIntegerField()
    maximum_age_months = models.PositiveIntegerField()
    country = models.ManyToManyField(Country, related_name="age_countries")
    course_level = models.ManyToManyField(CourseLevel, related_name="age_course_levels")
    description = models.TextField(max_length=255,null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.study_age_group.name} Age"
    
    
    
    
    
class StudyFactorAcademicResult(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    factor_for = models.ForeignKey(FactorFor, on_delete=models.CASCADE, related_name="academic_results",to_field='uuid',db_column='factor_for_uuid')
    academic_result_group = models.ForeignKey(AcademicResultGroup, on_delete=models.CASCADE, related_name="academic_results", to_field='uuid',db_column='academic_result_group_uuid')
    minimum_academic_result_required = models.ForeignKey(AcademicResultType, on_delete=models.CASCADE, related_name="academic_result_types", to_field='uuid',db_column='minimum_academic_result_required_uuid')
    description = models.TextField(max_length=255,null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.academic_result_group.name} - Academic Result"
    








class StudyFactorBacklogs(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    factor_for = models.ForeignKey("master.FactorFor", on_delete=models.CASCADE, related_name="study_backlogs")
    backlog_group = models.ForeignKey("master.BacklogsGroup", on_delete=models.CASCADE, related_name="study_backlogs")

    backlog_accepted = models.BooleanField(default=False)
    max_backlogs = models.PositiveIntegerField(default=0)

    description = models.TextField(blank=True, null=True)

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return f"{self.factor_for.name} - {self.backlog_group.name}"
    
    
    

class StudyFactorGAP(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    factor_for = models.ForeignKey("FactorFor", on_delete=models.CASCADE)
    study_gap_group = models.ForeignKey("GAPGroup", on_delete=models.CASCADE)

    maximum_gap_accepted = models.PositiveIntegerField(default=0)

    country_for_admission = models.ManyToManyField('RepresentingCountry',related_name="study_factor_gaps")  
    institute_type = models.ManyToManyField("InstituteType",related_name="study_factor_gaps")   # Multiple
    course_level = models.ManyToManyField("CourseLevel",related_name="study_factor_gaps")       # Multiple

    description = models.TextField(blank=True, null=True)

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.factor_for} - GAP Rule"
    
    



class StudyFactorLanguageAbility(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    factor_for = models.ForeignKey(FactorFor, on_delete=models.CASCADE)
    language_ability_group = models.ForeignKey(LanguageAbilityGroup, on_delete=models.CASCADE)
    language_test_name = models.ForeignKey('LanguageTest', on_delete=models.CASCADE)
    module_name = models.ForeignKey('LanguagetestmoduleName', on_delete=models.CASCADE)

    minimum_overall_score = models.ForeignKey(LanguageTestResult, on_delete=models.CASCADE, related_name='overall_scores')
    not_less_than = models.ForeignKey(LanguageTestResult, on_delete=models.CASCADE, related_name='not_less_than_scores')

    in_no_of_modules = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.factor_for.name} - {self.language_test_name.name}"
    
    
    
    
class StudyFactorEntranceTestAbility(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    factor_for = models.ForeignKey(FactorFor, on_delete=models.CASCADE)
    entrance_test_ability_group = models.ForeignKey('EntranceTestAbilityGroup', on_delete=models.CASCADE)
    entrance_test_name = models.ForeignKey('EntranceTestName', on_delete=models.CASCADE)

    minimum_score_required = models.ForeignKey('EntranceTestResult', on_delete=models.CASCADE)

    description = models.TextField(blank=True, null=True)

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.factor_for.name} - {self.entrance_test_name.name}"
    
   
