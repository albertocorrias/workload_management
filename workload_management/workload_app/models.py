
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime


class Faculty(models.Model):
    """
    Model that describes a faculty.
    It stores the name of the faculty and an acronym
    """
    faculty_name = models.CharField(max_length=300) #the full name of the faculty/school
    faculty_acronym = models.CharField(max_length=4) #the acronym, e.g., CDE for College of Design and Engineering
    
    def __str__(self):
        return self.faculty_name
            
    class Meta:
        ordering = ['faculty_acronym']   

class Academicyear(models.Model):
    """
    A simple model to deal with academic years
    It only stores the start year. The __str__ method wil give the full string e.g., for 2018, it will be 2018-2019
    """
    start_year = models.PositiveIntegerField(unique = True, validators=[MaxValueValidator(2200),MinValueValidator(1900)])

    def __str__(self):
        return str(self.start_year) + '-' + str(self.start_year+1)

    class Meta:
        ordering = ['start_year']

class Department(models.Model):
    """
    Model that describes a department.
    It stores the name of the department, an acronym to be used andthe faculty the dept belongs to
    """
    department_name = models.CharField(max_length=300) #the full name of the deparment
    department_acronym = models.CharField(max_length=4) #the acronym, e.g., ME for Mechanical Engineering
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, default=1) #The faculty/school this department is in
    
    def __str__(self):
        return self.department_name
            
    class Meta:
        ordering = ['department_acronym']

class EmploymentTrack(models.Model):
    """
    Model that describes the employment track for a lecturer (e.g., tenure track, etc)
    It stores the name of the track and the multiplier to be applied to the teaching expectations
    """
    #This is the name of the track
    track_name = models.CharField(max_length=300)
    
    #This is the adjustment that will be applied to the teaching expectations
    #e.g. if track_adjustment = 2, the expectations are double than one with track_adjustment =1
    # If you set to 0, there are no teaching expectations for people in this track
    track_adjustment = models.DecimalField(max_digits=3, decimal_places=2, validators=[
            MaxValueValidator(99),
            MinValueValidator(0)
        ])

    #Whether this is the default employment track with the default adjustment
    is_default = models.BooleanField(default=True, null=True)

    # Whether or not this is employed as external person (adjunct).
    is_adjunct = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.track_name
    
    class Meta:
        ordering = ['track_name']

class ServiceRole(models.Model):
    """
    Model that describes a possible service role for a lecturer (e.g., head of department, etc)
    It stores the name of the role and the multiplier to be applied to the teaching expectations
    """
    #This is the name of the service role (e.g., Head of department)
    role_name = models.CharField(max_length=300)
    
    #This is the adjustment that will be applied to the teaching expectations
    #e.g. if role_adjustment = 2, the expectations are double than one with role_adjustment =1
    # If you set to 0, there are no teaching expectations for people in this role
    role_adjustment = models.DecimalField(max_digits=3, decimal_places=2, validators=[
            MaxValueValidator(99),
            MinValueValidator(0)
        ])

    #Whether this is the default service role with the default adjustment
    is_default = models.BooleanField(default=True, null=True)

    def __str__(self):
        return self.role_name
    
    class Meta:
        ordering = ['role_name']

class WorkloadScenario(models.Model):
    """
    Model that describes a workload scenario for a given department, in a given academic year.
    It is the key container model. Lecturer, modules, etc will be referred to this.
    """

    DRAFT = 'Draft'
    OFFICIAL = 'Official'
    
    WORKLOAD_STATUS = [
        (DRAFT, 'Draft'),
        (OFFICIAL, 'Official'),
    ]

    label = models.CharField(max_length=300) #the name of the scenario. E.g., dept / academic year
    date_created = models.DateField(auto_now=False, auto_now_add=False,default=datetime.date.today)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE, default=1) #The dept this workload is relevant to
    academic_year = models.ForeignKey(Academicyear, on_delete=models.CASCADE, default=1) #The academic year this workload refers to
    status = models.CharField(max_length = 50, choices = WORKLOAD_STATUS, default=DRAFT)

    def __str__(self):
        return self.label
            
    class Meta:
        ordering = ['date_created']



class Lecturer(models.Model):
    """
    Model the describes a lecturer. It stores the name, the fractional appointment,
    the workload scenario this person is active in, emplyment track and service role.
    """
    name = models.CharField(max_length=300)

    #This is 1 for 100% with the department, 0.5 for 50% appointees, etc
    fraction_appointment = models.DecimalField(max_digits=3, decimal_places=2, validators=[
            MaxValueValidator(1),
            MinValueValidator(0)
        ])

    #The workload scenario this lecturer appears in
    workload_scenario = models.ForeignKey(WorkloadScenario, on_delete=models.CASCADE, default=1)

    #The employment track of this lecturer
    employment_track = models.ForeignKey(EmploymentTrack, on_delete=models.CASCADE, default=1)

    #The service role of this lecturer (e.g. head of department, director, etc)
    service_role = models.ForeignKey(ServiceRole, on_delete=models.CASCADE, default=1)
    
    def __str__(self):
        return self.name

class ProgrammeOffered(models.Model):
    #The name of the programme
    programme_name = models.CharField(max_length=300)
    #The primary Department offering the programme
    primary_dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.programme_name

class SubProgrammeOffered(models.Model):
    #The name of the sub-programme
    sub_programme_name = models.CharField(max_length=300)
    #The main programme this subprogramme belongs to
    main_programme = models.ForeignKey(ProgrammeOffered, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.sub_programme_name

class StudentLearningOutcome(models.Model):
    #The text of the SLO
    slo_description = models.CharField(max_length=3000)
    #A short description 
    slo_short_description = models.CharField(max_length=500, default='')
    #Whether or not this is a default SLO by the accreditation board
    is_default_by_accreditor = models.BooleanField(default=False)
    #Letter associated to slo
    letter_associated = models.CharField(max_length=2, default='')
    #The programme this SLO belongs to
    programme = models.ForeignKey(ProgrammeOffered, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.letter_associated + ') ' + self.slo_short_description

    class Meta:
        ordering = ['letter_associated']

class ModuleLearningOutcome(models.Model):
    #The text of the MLO
    mlo_description = models.CharField(max_length=3000)
    #A short description 
    mlo_short_description = models.CharField(max_length=500, default='')
    #Moduel code associated. #NOTE: as module objects are dependent on the workload scenario, we associate with module code only
    module_code = models.CharField(max_length=300)

    def __str__(self):
        return self.mlo_description

    class Meta:
        ordering = ['mlo_description']

#A model to capture the mapping between MLO and SLO
class MLOSLOMapping(models.Model):
    mlo = models.ForeignKey(ModuleLearningOutcome, on_delete=models.CASCADE)
    slo = models.ForeignKey(StudentLearningOutcome, on_delete=models.CASCADE)
    strength = models.PositiveIntegerField(validators=[MaxValueValidator(3),MinValueValidator(0)])

    def __str__(self):
        return self.mlo.mlo_short_description + " is mapped to " + self.slo.slo_description + " with strength " + str(self.strength)

    class Meta:
        ordering = ["mlo"]

class ProgrammeEducationalObjective(models.Model):
    #The text of the PEO
    peo_description = models.CharField(max_length=3000)
    #A short description 
    peo_short_description = models.CharField(max_length=500, default='')
    #The programme this PEO belongs to
    programme = models.ForeignKey(ProgrammeOffered, on_delete=models.SET_NULL, null=True)
    #Letter associated to the peo
    letter_associated = models.CharField(max_length=2, default='')
    
    def __str__(self):
        return self.letter_associated + ') ' + self.peo_short_description

    class Meta:
        ordering = ['letter_associated']

#A model to capture the mapping between a PEO and an SLO. 
class PEOSLOMapping(models.Model):
    peo = models.ForeignKey(ProgrammeEducationalObjective, on_delete=models.CASCADE)
    slo = models.ForeignKey(StudentLearningOutcome, on_delete=models.CASCADE)
    strength = models.PositiveIntegerField(validators=[MaxValueValidator(3),MinValueValidator(0)])

    def __str__(self):
        return self.peo + " is mapped to " + self.slo + " with strength " + self.strength

    class Meta:
        ordering = ["peo"]

class ModuleType(models.Model):
    """
    A simple model to describe the module type
    """
    type_name = models.CharField(max_length=300)
    
    def __str__(self):
        return self.type_name
    
    class Meta:
        ordering = ['type_name']
        
class Module(models.Model):
    """
    Model the describes a module (or class or course). It stores the code, the name, the semester offered,
    the workload scenario this module is relevant to, the module type and others.
    """
    UNASSIGNED = 'Not assigned'
    SEM_1 = 'Semester 1'
    SEM_2 = 'Semester 2'
    BOTH_SEMESTERS = 'Sem 1 and sem 2'
    SPECIAL_TERM_1 = 'Special term 1'
    SPECIAL_TERM_2 = 'Special term 2'
      
    SEMESTER_OFFERED = [
            (UNASSIGNED, 'No semester assigned yet'),
            (SEM_1, 'Semester 1'),
            (SEM_2, 'Semester 2'),
            (BOTH_SEMESTERS, 'Sem 1 and sem 2'),
            (SPECIAL_TERM_1, 'Special term 1'),
            (SPECIAL_TERM_2, 'Special term 2')
            ]
    
    #The module code
    module_code = models.CharField(max_length=300)
    #The module title
    module_title = models.CharField(max_length=300)
    #The workload scenario in which it appears
    scenario_ref = models.ForeignKey(WorkloadScenario, on_delete=models.CASCADE, default=1)
    #Total expected hours to be taught
    total_hours = models.PositiveIntegerField(null=True);
    #The type of module
    module_type = models.ForeignKey(ModuleType, on_delete=models.PROTECT, null=True)
    #Whether it is compulsory in primary programme
    compulsory_in_primary_programme = models.BooleanField(default=False)
    #year of study of students
    students_year_of_study = models.PositiveIntegerField(default=0)

    #The semester in which it is offered
    semester_offered = models.CharField(max_length=300, choices=SEMESTER_OFFERED,default=UNASSIGNED)
    #The number of student groups
    number_of_tutorial_groups = models.PositiveIntegerField(default=1);
    
    #The primary programme this module belongs to
    primary_programme = models.ForeignKey(ProgrammeOffered, on_delete=models.SET_NULL, null=True, related_name="primary_programme")
    #Another programme this module may be offered as part of
    secondary_programme = models.ForeignKey(ProgrammeOffered, on_delete=models.SET_NULL, null=True, related_name="secondary_programme")
    #The sub-programme this module is part of
    sub_programme = models.ForeignKey(SubProgrammeOffered, on_delete=models.SET_NULL, null=True, related_name="sub_programme")
    #Another sub-programme this module may be part of
    secondary_sub_programme = models.ForeignKey(SubProgrammeOffered, on_delete=models.SET_NULL, null=True, related_name="secondary_sub_programme")

    def __str__(self):
        return "%s - %s" % (self.module_code, self.module_title)
    
    class Meta:
        ordering = ['module_code']

class TeachingAssignment(models.Model):
    """
    This is the key model the workload calculations are based upon. It essentially
    captures when one lecturer is assigned to teach one module in a given workload scenario.
    """
    assigned_module = models.ForeignKey(Module, on_delete=models.CASCADE)
    assigned_lecturer = models.ForeignKey(Lecturer,on_delete=models.CASCADE)
    number_of_weekly_lecture_hours = models.PositiveIntegerField(default=0)
    number_of_weekly_tutorial_hours = models.PositiveIntegerField(default=0)
    number_of_tutorial_groups = models.PositiveIntegerField(default=0)
    number_of_weeks_assigned = models.PositiveIntegerField(default=13)
    number_of_hours = models.PositiveIntegerField()
    assigned_manually = models.BooleanField(default=True) #Whether or not the hours were assigned manually, or following weekly hours and policies
    counted_towards_workload = models.BooleanField(default=True) #Whether or not this assignment will be counted towards workload. E.g. if it is remunerated separately, you can set it to False
    #The workload scenario this assignment belongs to
    workload_scenario = models.ForeignKey(WorkloadScenario, on_delete=models.CASCADE)    
    
    def __str__(self):
        return "Module %s assigned to %s for %s hours in workload %s" % (\
               self.assigned_module.module_code, \
               self.assigned_lecturer.name,\
               str(self.number_of_hours),\
               self.workload_scenario.label)
        
    class Meta:
        ordering = ['number_of_hours']

class Survey(models.Model):
    """
    A model to cpature a whole survey
    """
    #The title of the survey
    survey_title = models.CharField(max_length=3000)
    #To store the original survey file. Note: file will be uploaded to MEDIA_ROOT/surveys/
    original_file = models.FileField(upload_to="surveys")
    #The opening date when the survey was distributed
    opening_date = models.DateField()
    #The closing date when the survey stopped accepting answers
    closing_date = models.DateField()
    #Maximum number of respondents (used to calculate response rate). Defaults to -1 if unknown.
    max_respondents = models.IntegerField(default=-1)
    #A storage for some comments about the survey
    comments = models.CharField(max_length=50000, default="")

    
    def __str__(self):
        return self.survey_title

class SurveyQuestionResponse(models.Model):
    """
    A model to capture the results of a survey question.
    It caters to Likert scale responses (up to 6-scale) as well as open-ended.
    """
    #The text of the question
    question_text = models.CharField(max_length=3000)
    #The label of the response considered most favourable (e.g., "strongly agree")
    label_highest_score = models.CharField(max_length=350, default = "Strongly agree")
    #The number of responses with the highest score (e.g., "strongly agree")
    n_highest_score = models.IntegerField(default=-1)
    #The label of the response considered second most favourable (e.g., "agree")
    label_second_highest_score = models.CharField(max_length=350, default = "Agree")
    #The number of responses with the second highest score (e.g., "agree")
    n_second_highest_score = models.IntegerField(default=-1)
    #The label of the response considered third most favourable (e.g., "Neutral")
    label_third_highest_score = models.CharField(max_length=350, default = "Neutral")
    #The number of responses with the third highest score (e.g., "neutral")
    n_third_highest_score = models.IntegerField(default=-1)
    #The label of the response considered fourth most favourable (e.g., "Disagree")
    label_fourth_highest_score = models.CharField(max_length=350, default = "Disagree")
    #The number of responses with the fourth highest score (e.g., "disagree")
    n_fourth_highest_score = models.IntegerField(default=-1)
    #The label of the response considered fifth most favourable (e.g., "Strongly disagree")
    label_fifth_highest_score = models.CharField(max_length=350, default = "Strongly disagree")
    #The number of responses with the fifth highest score (e.g., "strongly disagree")
    n_fifth_highest_score = models.IntegerField(default=-1)
    #The label of the response considered sixth most favourable 
    label_sixth_highest_score = models.CharField(max_length=350, default = "")
    #The number of responses with the sixth highest score (used only for rare 6-point scales)
    n_sixth_highest_score = models.IntegerField(default=-1)
    #Text response - Used for open-ended survey questions
    text_response = models.CharField(max_length=60000, default="")
    #The survey object this question belongs to
    parent_survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    #The MLO (if any) this question is targeted at
    associated_mlo = models.ForeignKey(ModuleLearningOutcome, null=True, on_delete=models.SET_NULL)
    #The SLO (if any) this question is targeted at
    associated_slo = models.ForeignKey(StudentLearningOutcome, null=True, on_delete=models.SET_NULL)
    #The PEO (if any) this question is targeted at
    associated_peo = models.ForeignKey(ProgrammeEducationalObjective, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.question_text
        
    class Meta:
        ordering = ['question_text']
        
class MLOPerformanceMeasure(models.Model):
    #The descrpition, e.g. Question 5 of final exam, etc
    description = models.CharField(max_length=100000)
    #Academic year
    academic_year = models.ForeignKey(Academicyear, null=True, on_delete=models.SET_NULL)
    #The MLO this measure is referred to
    associated_mlo = models.ForeignKey(ModuleLearningOutcome, on_delete=models.CASCADE)
    #Another MLO this measure might be referred to, if any
    secondary_associated_mlo = models.ForeignKey(ModuleLearningOutcome, null=True,on_delete=models.SET_NULL,related_name="secondary_mlo")
    #Another MLO this measure might be referred to, if any
    tertiary_associated_mlo = models.ForeignKey(ModuleLearningOutcome, null=True,on_delete=models.SET_NULL, related_name = "tertiary_mlo")
    #The score, in %
    percentage_score = models.DecimalField(max_digits=5, decimal_places=2, validators=[MaxValueValidator(100),MinValueValidator(0)])
    #To store the original file (e.g., the exam paper). Note: file will be uploaded to MEDIA_ROOT/mlo_performance_measures/
    original_file = models.FileField(upload_to="mlo_performance_measures")

    def __str__(self):
        return self.academic_year.__str__() + " - " + self.description
