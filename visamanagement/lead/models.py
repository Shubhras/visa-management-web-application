import uuid
from django.db import models
from master.models import *



class Applicant(models.Model):
    LeadForChoices = (
        ("Visa", "Visa"),
        ("Coaching","Coaching"),
        ("Visa & Coaching", "Visa & Coaching"),
    )

    lead_datetime = models.DateTimeField(blank=True, null=True)             
    lead_id = models.CharField(max_length=50, unique=True,blank=True, null=True)
    lead_for = models.CharField(
        max_length=30,
        choices=LeadForChoices,
        blank=True, null=True
    )

    test_exam_name = models.ForeignKey(                 
        LanguageTest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    interested_visa_categories = models.ManyToManyField(  
        VisaMain,
        blank=True,
        related_name="interested_applicants"
    )

    interested_countries = models.ManyToManyField(        
        Country,
       blank=True,
        related_name="interest_country_leads"
    )
    
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=100,blank=True, null=True)
    last_name = models.CharField(max_length=100,blank=True, null=True)
    gender = models.ForeignKey(Gender,on_delete=models.SET_NULL,null=True,related_name="citizens")
    date_of_birth = models.DateField(blank=True, null=True)
    marital_status =models.ForeignKey(Maritalstatus,on_delete=models.SET_NULL,null=True,related_name="citizens")
    along_with = models.BooleanField(default=False)   
    country_of_citizenship = models.ForeignKey(Country,on_delete=models.SET_NULL,null=True,related_name="citizens")

    country_of_residency = models.ForeignKey(Country,on_delete=models.SET_NULL,null=True,related_name="residents")
    residency_status = models.ForeignKey(VisaName,on_delete=models.SET_NULL,null=True,related_name="residents")
    default_citizen = models.BooleanField(default=True)
    mobile_country_code = models.CharField(max_length=10,blank=True, null=True)
    mobile_number = models.CharField(max_length=20)

    whatsapp_country_code = models.CharField(max_length=10,null=True, blank=True)
    whatsapp_number = models.CharField(max_length=20)
    email = models.EmailField()
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True, null=True)
    landmark_area = models.CharField(max_length=200, null=True, blank=True)

    country = models.ForeignKey(Country,on_delete=models.SET_NULL,null=True,related_name="applicant_country")
    state = models.ForeignKey(State,on_delete=models.SET_NULL,null=True,related_name="applicant_state")
    district = models.ForeignKey(District,on_delete=models.SET_NULL,null=True,related_name="applicant_district")
    city = models.ForeignKey(City,on_delete=models.SET_NULL,null=True,related_name="applicant_city")
    village = models.CharField(max_length=150, null=True, blank=True)
    pin_zip = models.CharField(max_length=10,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return f"{self.first_name}"









class Education(models.Model):
    VALID_UNIT_CHOICES = (
        ("Yes", "Yes"),
        ("No","No"),
    )
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    applicant = models.ForeignKey(Applicant,on_delete=models.CASCADE,related_name="educations")

    consider = models.CharField(max_length=10,choices=VALID_UNIT_CHOICES, blank=True, null=True)

    education_level = models.ForeignKey(EducationLevel,on_delete=models.SET_NULL,null=True)

    education_duration = models.ForeignKey(EducationDuration,on_delete=models.SET_NULL,null=True)


    study_major_area = models.ForeignKey(Studymajorarea,on_delete=models.SET_NULL,null=True)

    study_main_area = models.ForeignKey(Studymainarea,on_delete=models.SET_NULL,null=True,blank=True)
    country = models.ForeignKey(Country,on_delete=models.SET_NULL,null=True)

    state = models.ForeignKey(State,on_delete=models.SET_NULL,null=True)
    start_date = models.DateField()
    end_date = models.DateField()

    backlogs = models.PositiveIntegerField(default=0)

    medium_of_education = models.ForeignKey(MediumofEducation,on_delete=models.SET_NULL,null=True)
    academic_result_type = models.ForeignKey(AcademicResultType,on_delete=models.SET_NULL,null=True,related_name="academic_result_type")
    academic_result_value = models.CharField(max_length=20)
    education_type = models.ForeignKey(EducationType,on_delete=models.SET_NULL,null=True)
    math_result_type = models.ForeignKey(AcademicResultType,on_delete=models.SET_NULL,null=True,related_name="math_result_type")
    math_result_value = models.CharField(max_length=20, null=True, blank=True)

    english_result_type = models.ForeignKey(AcademicResultType,on_delete=models.SET_NULL,null=True,related_name="english_result_type")
    english_result_value = models.CharField(max_length=20, null=True, blank=True)

    physics_result_type = models.ForeignKey(AcademicResultType,on_delete=models.SET_NULL,null=True,related_name="physics_result_type")
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
    applicant = models.ForeignKey(Applicant,on_delete=models.CASCADE,related_name="work_experiences")
    consider = models.CharField(max_length=10,choices=VALID_UNIT_CHOICES, blank=True, null=True)

    country = models.ForeignKey(Country,on_delete=models.SET_NULL,null=True,related_name="work_country")

    state = models.ForeignKey(State,on_delete=models.SET_NULL,null=True,related_name="work_state")

    employer_name = models.CharField(max_length=200)

    designation = models.ForeignKey(Designation,on_delete=models.SET_NULL,null=True)

    job_start_date = models.DateField()
    job_end_date = models.DateField(null=True, blank=True)  
    years = models.IntegerField(default=0)
    months = models.IntegerField(default=0)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)

    salary_mode = models.ForeignKey(ModeofSalary,on_delete=models.SET_NULL,null=True,default=None)
    itr_status = models.ForeignKey(ITReturnStatus,on_delete=models.SET_NULL,null=True)

    currency = models.ForeignKey(Country,on_delete=models.SET_NULL,null=True,related_name="work_currency")
    job_type = models.ForeignKey(JobType,on_delete=models.SET_NULL,null=True)
    salary_amount = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)

    days = models.IntegerField(null=True, blank=True)
    amount_numeric = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employer_name} – {self.designation}"




class LanguageAbility(models.Model):
    VALID_UNIT_CHOICES = (
        ("Yes", "Yes"),
        ("No", "No"),

    )

    TEST_LEVEL_CHOICES = (
        ("First", "First"),
        ("Second", "Second"),
    )

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name="language_abilities")

    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    consider = models.CharField(max_length=10, choices=VALID_UNIT_CHOICES, blank=True, null=True)

    test_name = models.CharField(max_length=100, blank=True, null=True)
    test_short_name = models.CharField(max_length=50, blank=True, null=True)
    test_level = models.CharField(max_length=20, choices=TEST_LEVEL_CHOICES, blank=True, null=True)

    listening_score = models.ForeignKey(LanguagetestmoduleName, on_delete=models.CASCADE, related_name="language_test_listen")
    speaking_score = models.ForeignKey(LanguagetestmoduleName, on_delete=models.CASCADE, related_name="language_test_spoken")
    reading_score = models.ForeignKey(LanguagetestmoduleName, on_delete=models.CASCADE, related_name="language_test_reading")
    writing_score = models.ForeignKey(LanguagetestmoduleName, on_delete=models.CASCADE, related_name="language_test_write")
    overall_score = models.ForeignKey(LanguagetestmoduleName, on_delete=models.CASCADE, related_name="language_test_overall")
    test_date = models.DateField(blank=True, null=True)
    first_or_second_language = models.CharField(max_length=10, choices=(("First", "First"), ("Second", "Second")), default="First")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.language} – {self.applicant.first_name}"




class EntranceTestAbility(models.Model):
    YES_NO_CHOICES = (
        ("Yes", "Yes"),
        ("No", "No"),
    )

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name="entrance_test_abilities")

    appeared_test = models.CharField(max_length=10, choices=YES_NO_CHOICES, default="No")
    entrance_test_name = models.CharField(max_length=100, blank=True, null=True)
    entrance_test_short_name = models.CharField(max_length=50, blank=True, null=True)

    module_01_score = models.ForeignKey(EntranceTestModuleName, on_delete=models.CASCADE, related_name="entrance_test_m1")
    module_02_score = models.ForeignKey(EntranceTestModuleName, on_delete=models.CASCADE, related_name="entrance_test_m2")
    module_03_score = models.ForeignKey(EntranceTestModuleName, on_delete=models.CASCADE, related_name="entrance_test_m3")
    total_score = models.ForeignKey(EntranceTestModuleName, on_delete=models.CASCADE, related_name="entrance_test_m4")

    test_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.entrance_test_name} – {self.applicant.first_name}"



class Relative(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    applicant = models.ForeignKey(Applicant,on_delete=models.CASCADE,related_name="relatives")

    applicant_type = models.ForeignKey(ApplicantType,on_delete=models.SET_NULL,null=True)

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)

    relation = models.ForeignKey(Relation,on_delete=models.SET_NULL,null=True)

    visa_category = models.ForeignKey(VisaMain,on_delete=models.SET_NULL,null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.applicant}"





class VisitHistory(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    applicant = models.ForeignKey(Applicant,on_delete=models.CASCADE,related_name="visit_history")

    applicant_type = models.ForeignKey(ApplicantType, on_delete=models.SET_NULL, null=True)

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)

    visa_category = models.ForeignKey(VisaMain, on_delete=models.SET_NULL, null=True)

    issue_date = models.DateField()
    travel_from = models.DateField()
    travel_to = models.DateField()

    purpose_of_visit = models.ForeignKey(PurposeOfVisit,on_delete=models.SET_NULL,null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.applicant}"



class RefusalHistory(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    applicant = models.ForeignKey(Applicant,on_delete=models.CASCADE,related_name="refusal_history")

    applicant_type = models.ForeignKey(ApplicantType, on_delete=models.SET_NULL, null=True,related_name="refusal_history")

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    visa_category = models.ForeignKey(VisaMain, on_delete=models.SET_NULL, null=True)

    refusal_date = models.DateField()
    refusal_reason = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.applicant}"




class BusinessExperience(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    applicant = models.ForeignKey(Applicant,on_delete=models.CASCADE,related_name="business_experience")

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    company_name = models.CharField(max_length=255)

    company_type = models.ForeignKey(CompanyType, on_delete=models.SET_NULL, null=True)

    share_percent = models.DecimalField(max_digits=5, decimal_places=2)   # Example: 25.50%

    start_date = models.DateField()
    end_date = models.DateField()

    turnover = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.applicant}"



class Networth(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False, unique=True)

    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name="networth"
    )

    applicant_type = models.ForeignKey(ApplicantType, on_delete=models.SET_NULL, null=True, related_name="networth")

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name="networths_as_country")
    currency = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name="networths_as_currency")

    immovable_property = models.DecimalField(max_digits=12, decimal_places=2)
    movable_property = models.DecimalField(max_digits=12, decimal_places=2)
    liquid_amount = models.DecimalField(max_digits=12, decimal_places=2)

    total_networth = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.applicant}"


class EligibilityFlags(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False, unique=True)
    applicant = models.OneToOneField(
        Applicant,
        on_delete=models.CASCADE,
        related_name="eligibility_flags"
    )

    trade_certificate = models.BooleanField(default=False)
    educational_credential_assessment = models.BooleanField(default=False)
    ita_province = models.BooleanField(default=False)
    tech_startup_founder = models.BooleanField(default=False)
    reside_outside_greater_city = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.applicant}"
 

class SpouseEducationlead(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False, unique=True)
    applicant = models.ForeignKey(Applicant,on_delete=models.CASCADE,related_name='spio')
    education_level = models.ForeignKey(EducationLevel,on_delete=models.SET_NULL, null=True, related_name='education_level')
    duration = models.ForeignKey(EducationDuration,on_delete=models.SET_NULL,null=True,related_name='duration')
    study_main_area = models.ForeignKey(Studymainarea,on_delete=models.SET_NULL,null=True,related_name='study_main_area')
    edu_type = models.ForeignKey(EducationType,on_delete=models.SET_NULL,null=True,related_name='education_type')

    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    result = models.CharField(max_length=50,null=True,blank=True)
    
    def __str__(self):
        return f"{self.applicant}"

class LeadDocument(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    documentcategory = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE)
    documentname = models.ForeignKey(DocumentName, on_delete=models.CASCADE)

    attachments = models.JSONField(default=list)  # <-- multiple file URLs in list

    created_at = models.DateTimeField(auto_now_add=True)


class QuickAssessment(models.Model):
 
    # Top section
    visa_main_category = models.ForeignKey( VisaMain, on_delete=models.SET_NULL, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    visa_major_category = models.ManyToManyField(VisaMajor, blank=True)
    visa_name = models.CharField(max_length=255, blank=True, null=True)
 
    # If Student Visa → Show below fields
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
 
    course_level = models.ForeignKey(CourseLevel, on_delete=models.SET_NULL, null=True, blank=True)
    course_duration = models.ForeignKey(CourseDuration, on_delete=models.SET_NULL, null=True, blank=True)
 
 
    study_main_areas = models.ManyToManyField(Studymainarea, blank=True)
    study_major_areas = models.ManyToManyField(Studymajorarea, blank=True)
 
    intake_name = models.ForeignKey(IntakeName, on_delete=models.SET_NULL, null=True, blank=True)
    intake_year = models.CharField(max_length=255, blank=True, null=True)
 
    max_application_fee_currency = models.CharField(max_length=20, null=True, blank=True)
    max_application_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
 
    course_fee_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    course_fee_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
 
    scholarships_available = models.BooleanField(default=False)
    scholarship_min_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
 
    with_moi = models.BooleanField(default=False)
    with_esl = models.BooleanField(default=False)
    with_pre_course = models.BooleanField(default=False)
 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
 
 
    def __str__(self):
        return f"Assessment #{self.id}"
    


class QuickAssessmentNew(models.Model):
 
    # Top section
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False, unique=True)

    visa_main_category = models.ForeignKey( VisaMain, on_delete=models.SET_NULL, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    visa_major_category = models.ManyToManyField(VisaMajor, blank=True)
    visa_name = models.CharField(max_length=255, blank=True, null=True)
 
    # If Student Visa → Show below fields
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
 
    course_level = models.ForeignKey(CourseLevel, on_delete=models.SET_NULL, null=True, blank=True)
    course_duration = models.ForeignKey(CourseDuration, on_delete=models.SET_NULL, null=True, blank=True)
 
 
    study_main_areas = models.ManyToManyField(Studymainarea, blank=True)
    study_major_areas = models.ManyToManyField(Studymajorarea, blank=True)
 
    intake_name = models.ForeignKey(IntakeName, on_delete=models.SET_NULL, null=True, blank=True)
    intake_year = models.CharField(max_length=255, blank=True, null=True)
 
    max_application_fee_currency = models.CharField(max_length=20, null=True, blank=True)
    max_application_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
 
    course_fee_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    course_fee_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
 
    scholarships_available = models.BooleanField(default=False)
    scholarship_min_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
 
    with_moi = models.BooleanField(default=False)
    with_esl = models.BooleanField(default=False)
    with_pre_course = models.BooleanField(default=False)
 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
 
 
    def __str__(self):
        return f"Assessment #{self.uuid}"
    

    

