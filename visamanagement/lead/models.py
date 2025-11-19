import uuid
from django.db import models



class Applicant(models.Model):
    LeadForChoices = (
        ("Visa", "Visa"),
        ("Coaching","Coaching"),
        ("Visa & Coaching", "Visa & Coaching"),
    )

    lead_datetime = models.DateTimeField()             
    lead_id = models.CharField(max_length=50, unique=True)
    lead_for = models.CharField(
        max_length=30,
        choices=LeadForChoices.choices
    )

    test_exam_name = models.ForeignKey(                 
        "LanguageTest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    interested_visa_categories = models.ManyToManyField(  
        "VisaMainCategory",
        blank=True,
        related_name="interested_applicants"
    )

    interested_countries = models.ManyToManyField(        
        "Country",
        blank=True,
        related_name="interest_country_leads"
    )
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.ForeignKey("Gender",on_delete=models.SET_NULL,null=True,related_name="citizens")
    date_of_birth = models.DateField()
    marital_status =models.ForeignKey("Maritalstatus",on_delete=models.SET_NULL,null=True,related_name="citizens")
    along_with = models.BooleanField(default=False)   
    country_of_citizenship = models.ForeignKey("Country",on_delete=models.SET_NULL,null=True,related_name="citizens")

    country_of_residency = models.ForeignKey("Country",on_delete=models.SET_NULL,null=True,related_name="residents")
    residency_status = models.ForeignKey("VisaName",on_delete=models.SET_NULL,null=True,related_name="residents")
    default_citizen = models.BooleanField(default=True)
    mobile_country_code = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=20)

    whatsapp_country_code = models.CharField(max_length=10)
    whatsapp_number = models.CharField(max_length=20)
    email = models.EmailField()
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True, null=True)
    landmark_area = models.CharField(max_length=200, null=True, blank=True)

    country = models.ForeignKey("Country",on_delete=models.SET_NULL,null=True,related_name="applicant_country")
    state = models.ForeignKey("State",on_delete=models.SET_NULL,null=True,related_name="applicant_state")
    district = models.ForeignKey("District",on_delete=models.SET_NULL,null=True,related_name="applicant_district")
    city = models.ForeignKey("City",on_delete=models.SET_NULL,null=True,related_name="applicant_city")
    village = models.CharField(max_length=150, null=True, blank=True)
    pin_zip = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)











class Education(models.Model):
    VALID_UNIT_CHOICES = (
        ("Yes", "Yes"),
        ("No","No"),
    )
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    applicant = models.ForeignKey("Applicant",on_delete=models.CASCADE,related_name="educations")

    consider = models.CharField(max_length=10,choices=VALID_UNIT_CHOICES, blank=True, null=True)

    education_level = models.ForeignKey("EducationLevel",on_delete=models.SET_NULL,null=True)

    education_duration = models.ForeignKey("EducationDuration",on_delete=models.SET_NULL,null=True)


    study_major_area = models.ForeignKey("StudyMajorArea",on_delete=models.SET_NULL,null=True)

    study_main_area = models.ForeignKey("StudyMainArea",on_delete=models.SET_NULL,null=True,blank=True)
    country = models.ForeignKey("Country",on_delete=models.SET_NULL,null=True)

    state = models.ForeignKey("State",on_delete=models.SET_NULL,null=True)
    start_date = models.DateField()
    end_date = models.DateField()

    backlogs = models.PositiveIntegerField(default=0)

    medium_of_education = models.ForeignKey("MediumOfEducation",on_delete=models.SET_NULL,null=True)
    academic_result_type = models.ForeignKey("ResultType",on_delete=models.SET_NULL,null=True,related_name="academic_result_type")
    academic_result_value = models.CharField(max_length=20)
    education_type = models.ForeignKey("EducationType",on_delete=models.SET_NULL,null=True)
    math_result_type = models.ForeignKey("ResultType",on_delete=models.SET_NULL,null=True,related_name="math_result_type")
    math_result_value = models.CharField(max_length=20, null=True, blank=True)

    english_result_type = models.ForeignKey("ResultType",on_delete=models.SET_NULL,null=True,related_name="english_result_type")
    english_result_value = models.CharField(max_length=20, null=True, blank=True)

    physics_result_type = models.ForeignKey("ResultType",on_delete=models.SET_NULL,null=True,related_name="physics_result_type")
    physics_result_value = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.education_level} – {self.applicant.first_name}"



class WorkExperience(models.Model):
    VALID_UNIT_CHOICES = (
        ("Yes", "Yes"),
        ("No","No"),
    )
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    applicant = models.ForeignKey("Applicant",on_delete=models.CASCADE,related_name="work_experiences")
    consider = models.CharField(max_length=10,choices=VALID_UNIT_CHOICES, blank=True, null=True)

    country = models.ForeignKey("Country",on_delete=models.SET_NULL,null=True,related_name="work_country")

    state = models.ForeignKey("State",on_delete=models.SET_NULL,null=True,related_name="work_state")

    employer_name = models.CharField(max_length=200)

    designation = models.ForeignKey("Designation",on_delete=models.SET_NULL,null=True)

    job_duration = models.ForeignKey("JobDuration",on_delete=models.SET_NULL,null=True)

    experience_duration = models.ForeignKey("ExperienceDuration",on_delete=models.SET_NULL,null=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  
    years = models.IntegerField(default=0)
    months = models.IntegerField(default=0)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)

    salary_mode = models.ForeignKey("SalaryMode",on_delete=models.SET_NULL,null=True,default=None)
    itr_status = models.ForeignKey("ITRStatus",on_delete=models.SET_NULL,null=True)

    currency = models.ForeignKey("Currency",on_delete=models.SET_NULL,null=True,related_name="work_currency")
    job_type = models.ForeignKey("JobType",on_delete=models.SET_NULL,null=True)
    salary_amount = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)

    days = models.IntegerField(null=True, blank=True)
    amount_numeric = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employer_name} – {self.designation}"