
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from .global_constants import ShortenString
import datetime
import math

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

class SurveyLabelSet(models.Model):
    """
    A model to allow programmes to store sets of labels for the surveys
    """
    highest_score_label = models.CharField(max_length=150,default = '')
    second_highest_score_label = models.CharField(max_length=150,default = '')
    third_highest_score_label = models.CharField(max_length=150,default = '')
    fourth_highest_score_label = models.CharField(max_length=150,default = '')
    fifth_highest_score_label = models.CharField(max_length=150,default = '')
    sixth_highest_score_label = models.CharField(max_length=150,default = '')
    seventh_highest_score_label = models.CharField(max_length=150,default = '')
    eighth_highest_score_label = models.CharField(max_length=150,default = '')
    ninth_highest_score_label = models.CharField(max_length=150,default = '')
    tenth_score_label = models.CharField(max_length=150,default = '')

    def GetListOfLabels(self):
        """
        Convenience method to return a list of non-empty labels
        """
        ret = []
        
        if (len(self.highest_score_label)>0):
            ret.append(self.highest_score_label)
        if (len(self.second_highest_score_label)>0):
            ret.append(self.second_highest_score_label)
        if (len(self.third_highest_score_label)>0):
            ret.append(self.third_highest_score_label)
        if (len(self.fourth_highest_score_label)>0):
            ret.append(self.fourth_highest_score_label)
        if (len(self.fifth_highest_score_label)>0):
            ret.append(self.fifth_highest_score_label)
        if (len(self.sixth_highest_score_label)>0):
            ret.append(self.sixth_highest_score_label)
        if (len(self.seventh_highest_score_label)>0):
            ret.append(self.seventh_highest_score_label)
        if (len(self.eighth_highest_score_label)>0):
            ret.append(self.eighth_highest_score_label)
        if (len(self.ninth_highest_score_label)>0):
            ret.append(self.ninth_highest_score_label)
        if (len(self.tenth_score_label)>0):
            ret.append(self.tenth_score_label)
        return ret
    
    def GetFullListOfLabels(self):
        """
        Little convenience method to return all the labels in a list
        (including empty ones)
        """
        ret = []
        ret.append(self.highest_score_label)
        ret.append(self.second_highest_score_label)
        ret.append(self.third_highest_score_label)
        ret.append(self.fourth_highest_score_label)
        ret.append(self.fifth_highest_score_label)
        ret.append(self.sixth_highest_score_label)
        ret.append(self.seventh_highest_score_label)
        ret.append(self.eighth_highest_score_label)
        ret.append(self.ninth_highest_score_label)
        ret.append(self.tenth_score_label)
        return ret

class ProgrammeOffered(models.Model):
    #The name of the programme
    programme_name = models.CharField(max_length=300)
    #The primary Department offering the programme
    primary_dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    #Accreditation setting: label set for SLO survey
    slo_survey_labels = models.ForeignKey(SurveyLabelSet, on_delete=models.SET_NULL, null=True,related_name="slo_survey_labels")
    #Accreditation setting: label set for PEO survey
    peo_survey_labels = models.ForeignKey(SurveyLabelSet, on_delete=models.SET_NULL, null=True,related_name="peo_survey_labels")
    #Accreditation setting: label set for MLO survey
    mlo_survey_labels = models.ForeignKey(SurveyLabelSet, on_delete=models.SET_NULL, null=True,related_name="mlo_survey_labels")

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
    #Cohort validity from
    cohort_valid_from = models.ForeignKey(Academicyear,on_delete=models.SET_NULL, null=True, related_name="cohort_valid_from")
    #Cohort validity to
    cohort_valid_to = models.ForeignKey(Academicyear,on_delete=models.SET_NULL, null=True, related_name = "cohort_valid_to")

    def __str__(self):
        return self.letter_associated + ') ' + self.slo_short_description

    class Meta:
        ordering = ['letter_associated']

class ModuleLearningOutcome(models.Model):
    #The text of the MLO
    mlo_description = models.CharField(max_length=3000)
    #A short description 
    mlo_short_description = models.CharField(max_length=500, default='')
    #Module code associated. #NOTE: as module objects are dependent on the workload scenario, we associate with module code only
    module_code = models.CharField(max_length=300)
    #Valid from
    mlo_valid_from = models.ForeignKey(Academicyear,on_delete=models.SET_NULL, null=True, related_name="mlo_valid_from")
    #Valid until
    mlo_valid_to = models.ForeignKey(Academicyear,on_delete=models.SET_NULL, null=True, related_name="mlo_valid_to")

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
    
    #Cohort validity from
    peo_cohort_valid_from = models.ForeignKey(Academicyear,on_delete=models.SET_NULL, null=True, related_name="peo_cohort_valid_from")
    #Cohort validity to
    peo_cohort_valid_to = models.ForeignKey(Academicyear,on_delete=models.SET_NULL, null=True, related_name = "peo_cohort_valid_to")
    
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
    department = models.ForeignKey(Department, on_delete=models.CASCADE,default=1)

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
    YES = True
    NO = False
    
    SEMESTER_OFFERED = [
            (UNASSIGNED, 'No semester assigned yet'),
            (SEM_1, 'Semester 1'),
            (SEM_2, 'Semester 2'),
            (BOTH_SEMESTERS, 'Sem 1 and sem 2'),
            (SPECIAL_TERM_1, 'Special term 1'),
            (SPECIAL_TERM_2, 'Special term 2')
            ]
    
    YES_NO_MODULE = [(YES, 'Yes'),(NO, 'No')]

    #The module code
    module_code = models.CharField(max_length=300)
    #The module title
    module_title = models.CharField(max_length=300)
    #The workload scenario in which it appears
    scenario_ref = models.ForeignKey(WorkloadScenario, on_delete=models.CASCADE, default=1)
    #Total expected hours to be taught
    total_hours = models.PositiveIntegerField(null=True);
    #The type of module
    module_type = models.ForeignKey(ModuleType, on_delete=models.SET_NULL, null=True)
    #Whether it is compulsory in primary programme
    compulsory_in_primary_programme = models.BooleanField(default=False)
    #year of study of students, this is intended as the "typical stduent" accoridng to recommended schedule
    students_year_of_study = models.PositiveIntegerField(default=0,null=True)

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
    class SurveyType(models.TextChoices):
        PEO = "PEO", _('PEO Survey')
        SLO = "SLO", _('SLO Survey')
        MLO = "MLO", _('MLO Survey')
        UNDEFINED = "Undefined", _('Other')

    #The title of the survey
    survey_title = models.CharField(max_length=3000)
    #To store the original survey file. Note: file will be uploaded to MEDIA_ROOT/surveys/
    original_file = models.FileField(upload_to="surveys")
    #The opening date when the survey was distributed
    opening_date = models.DateField()
    #The closing date when the survey stopped accepting answers
    closing_date = models.DateField()
    #cohort targeted, NULL if not available. Note that this might mean different things for MLO and SLO and PEO
    cohort_targeted = models.ForeignKey(Academicyear,on_delete=models.SET_NULL,null=True)
    #Maximum number of respondents (used to calculate response rate). Defaults to -1 if unknown.
    max_respondents = models.IntegerField(default=-1)
    #A storage for some comments about the survey
    comments = models.CharField(max_length=50000, default="")
    #Likert scale labels that were used for this survey
    likert_labels = models.ForeignKey(SurveyLabelSet, on_delete=models.SET_NULL, null=True)
    #The type of survey
    survey_type = models.CharField(max_length = 10, choices = SurveyType, default = SurveyType.UNDEFINED)
    #Prgramme associated
    programme_associated = models.ForeignKey(ProgrammeOffered, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.survey_title

class SurveyQuestionResponse(models.Model):
    """
    A model to capture the results of a survey question.
    It caters to Likert scale responses (up to 10-scale) as well as open-ended.
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
    #The number of responses with the sixth highest score
    n_sixth_highest_score = models.IntegerField(default=-1)
    #The label of the response considered seventth most favourable 
    label_seventh_highest_score = models.CharField(max_length=350, default = "")
    #The number of responses with the seventh highest score 
    n_seventh_highest_score = models.IntegerField(default=-1)
    #The label of the response considered eighth most favourable 
    label_eighth_highest_score = models.CharField(max_length=350, default = "")
    #The number of responses with the eighth highest score 
    n_eighth_highest_score = models.IntegerField(default=-1)
    #The label of the response considered ninth most favourable 
    label_ninth_highest_score = models.CharField(max_length=350, default = "")
    #The number of responses with the ninth highest score 
    n_ninth_highest_score = models.IntegerField(default=-1)
    #The label of the response considered tenth most favourable 
    label_tenth_highest_score = models.CharField(max_length=350, default = "")
    #The number of responses with the tenth highest score 
    n_tenth_highest_score = models.IntegerField(default=-1)

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
    
    def CalculateRepsonsesProprties(self):
        """
        A convenience method that calculates some properties of this object
        """
        all_scores = [self.n_highest_score,\
                      self.n_second_highest_score, \
                      self.n_third_highest_score,\
                      self.n_fourth_highest_score,\
                      self.n_fifth_highest_score,\
                      self.n_sixth_highest_score,\
                      self.n_seventh_highest_score,\
                      self.n_eighth_highest_score,\
                      self.n_ninth_highest_score,\
                      self.n_tenth_highest_score]
        num_responses = 0
        for i in range(0,len(all_scores)):
            if all_scores[i] > -1:
                num_responses += all_scores[i]
        point_scale_index = all_scores.index(-1)#the first "-1"indicates the end of the scale
        positives = 0
        non_negatives = 0
        if (point_scale_index %2 == 0 ):#This is an even point scale 
            for i in range(0,int(point_scale_index/2)):
                positives += all_scores[i]
                non_negatives += all_scores[i]
        else: #Odd point scale
            mid_point  = math.floor(point_scale_index/2)#index of mid-point e.g., 2 in a 5-poont scale (index of "neutral")
            for i in range(0,mid_point):
                positives += all_scores[i]
            non_negatives = positives + all_scores[mid_point]

        percentage_positive = 0
        percentage_non_negative = 0
        if (num_responses > 0):
            percentage_positive = 100*positives/num_responses
            percentage_non_negative = 100*non_negatives/num_responses
        
        responses = []
        percentages = []
        cumulative_percentages = []
        cumulat = 0
        for i in range(0,len(all_scores)):
            if (all_scores[i] > -1):
                responses.append(all_scores[i])
                percentages.append(100*all_scores[i]/num_responses)
                cumulat += 100*all_scores[i]/num_responses
                cumulative_percentages.append(cumulat)

        nps = 'N/A'
        nps_message = "NPS is not calculates for scales with less than 4 points"
        if (point_scale_index == 4):#Promoter is first, detractors are bottom 2
            nps = self.n_highest_score/num_responses - (self.n_third_highest_score + self.n_fourth_highest_score)/num_responses
            nps_message = "NPS for a 4-point scale is calculated as % of respondents with highest score minus % of respondents with the bottom two scores."
        if (point_scale_index == 5):#promoter is first, detractors are bottom 3
            nps = self.n_highest_score/num_responses - (self.n_third_highest_score + self.n_fourth_highest_score + self.n_fifth_highest_score)/num_responses
            nps_message = "NPS for a 5-point scale is calculated as % of respondents with highest score minus % of respondents with the bottom three scores."
        if (point_scale_index == 6):#promoter is first, detractors are bottom 3
            nps = self.n_highest_score/num_responses - (self.n_fourth_highest_score + self.n_fifth_highest_score + self.n_sixth_highest_score)/num_responses
            nps_message = "NPS for a 6-point scale is calculated as % of respondents with highest score minus % of respondents with the bottom three scores."
        if (point_scale_index == 7):#promoter is first, detractors are bottom 4
            nps = self.n_highest_score/num_responses - (self.n_fourth_highest_score + self.n_fifth_highest_score + self.n_sixth_highest_score + self.n_seventh_highest_score)/num_responses
            nps_message = "NPS for a 7-point scale is calculated as % of respondents with highest score minus % of respondents with the bottom four scores."
        if (point_scale_index == 8):#promoter is first, detractors are bottom 4
            nps = self.n_highest_score/num_responses - (self.n_fifth_highest_score + self.n_sixth_highest_score + self.n_seventh_highest_score+self.n_eighth_highest_score)/num_responses
            nps_message = "NPS for a 8-point scale is calculated as % of respondents with highest score minus % of respondents with the bottom four scores."
        if (point_scale_index == 9):#Promoter are top 2, detractors are bottom 6
            nps = (self.n_highest_score+self.n_second_highest_score)/num_responses - (self.n_fourth_highest_score + self.n_fifth_highest_score + self.n_sixth_highest_score + \
                                                            self.n_seventh_highest_score + self.n_eighth_highest_score + self.n_eighth_highest_score )/num_responses
            nps_message = "NPS for a 9-point scale is calculated as sum of the % of respondents with highest two scores,  minus % of respondents with the bottom six scores."
        if (point_scale_index == 10):#Promoter are top 2, detractors are bottom 6
            nps = (self.n_highest_score+self.n_second_highest_score)/num_responses - (self.n_fifth_highest_score + self.n_sixth_highest_score + \
                                                            self.n_seventh_highest_score + self.n_eighth_highest_score + self.n_eighth_highest_score + \
                                                            self.n_tenth_highest_score)/num_responses
            nps_message = "NPS for a 9-point scale is calculated as sum of the % of respondents with highest two scores,  minus % of respondents with the bottom six scores."

        ret = {
            'all_respondents' : num_responses,
            'responses' : responses,
            'point_scales' : point_scale_index,
            'positives' : positives,
            'non_negatives' : non_negatives,
            'percentage_positive' : percentage_positive,
            'percentage_non_negative' : percentage_non_negative,
            'percentages' : percentages,
            'cumulative_percentages' : cumulative_percentages,
            'nps' : nps,
            'nps_message' : nps_message
        }
        return ret


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
    
class CorrectiveAction(models.Model):
    #module code - the module code for which this action is relevant
    module_code = models.CharField(max_length=10)
    #The description of the corrective action
    description = models.CharField(max_length=1000000)
    #The academic year where it will be implemented
    implementation_acad_year = models.ForeignKey(Academicyear, null=True, on_delete=models.SET_NULL)
    #Observed results
    observed_results =  models.CharField(max_length=1000000)
    
    def __str__(self):
        return ShortenString(self.description) + ' (' + self.implementation_acad_year.__str__() + ')'

class UniversityStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL)