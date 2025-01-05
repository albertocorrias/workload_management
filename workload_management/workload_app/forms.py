from ast import mod
from django import forms
from django.forms import ModelForm, ValidationError, SelectDateWidget
from django.core.validators import EMPTY_VALUES
from django.utils.translation import gettext_lazy as _
import datetime
from .models import Lecturer, Module, TeachingAssignment, WorkloadScenario, ModuleType, \
                    Department, EmploymentTrack,ServiceRole,Faculty, ProgrammeOffered, \
                    StudentLearningOutcome,SubProgrammeOffered,Academicyear,ProgrammeEducationalObjective,\
                    ModuleLearningOutcome, Survey,SurveyQuestionResponse, MLOPerformanceMeasure
from .global_constants import NUS_SLO_SURVEY_LABELS

class ProfessorForm(ModelForm):
    """
    Form to add new lecturer (professor). Modelled after the Lecturer model.
    
    Attributes
    ----------
    
    fresh_record : boolean
        a flag that differentiates when the form is for adding a 
        fresh record or when it is for editing an existing one
    
    """
    
    fresh_record = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Lecturer
        fields = ['name', 'fraction_appointment', 'employment_track', 'service_role']
        labels = {'name' : _('Name'),
                  'fraction_appointment' : _('Fractional appointment'),
                  'employment_track' : _('Select employment track'),
                  'service_role' : _('Select service role')}
        widgets = {'employment_track' : forms.Select(choices=EmploymentTrack.objects.all()),
                   'service_role' : forms.Select(choices=ServiceRole.objects.all())}
        
    def __init__(self, *args, **kwargs):
        super(ProfessorForm, self).__init__(*args, **kwargs)
        #No editing of names of existing profs
        if 'fresh_record' in self.initial: #Must check, otherwise a KeyError occurs (I suspect this is run a couple of times upon post)
            if (self.initial["fresh_record"] == False):
                self.fields['name'].widget = forms.HiddenInput()#Hides the name alltogether
     
class RemoveProfessorForm(forms.Form):
    """
    Form to remove a lecturer (professor).
    
    Attributes
    ----------
    
    select_professor_to_remove : ModelChoiceField
        the professor to remove
    wipe_out_from_table : boolean
        whether or not to remove the prof from the table completely. If false, only the teaching assignments will be removed
    """
    def __init__(self, *args, **kwargs):
        workload_scenario_id = kwargs.pop('workloadscenario_id')
        super(RemoveProfessorForm, self).__init__(*args, **kwargs)
        self.fields['select_professor_to_remove'] = forms.ModelChoiceField(label = 'Select professor for whom you want to remove all assignments of this workload', \
                                                        queryset=Lecturer.objects.filter(workload_scenario__id = workload_scenario_id))
        self.fields['wipe_out_from_table'] = forms.BooleanField(label = 'Remove professor entirely from the database?', required=False,\
                                                     help_text='If this option is ticked, the name of the professor will be eliminated from the table')
        
#Form to add new module. Modelled after the Module model.
class ModuleForm(ModelForm):
    """
    Form to add new module. Modelled after the Module model.
    
    Attributes
    ----------
    
    manual_hours_checked : boolean
        whether or not the number of assigne dhours will be manually enetered or not.
    fresh_record : boolean
        This is a flag that differentiate when the form is for adding a 
        fresh record or when it is for editing an existing one
    """    
    manual_hours_checked = forms.BooleanField(initial=False, required=False, label="Specify custom number of hours? (if left unticked, number of hours will be assigned automatically based on module type and number of tutorial groups)")    

    fresh_record = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Module
        fields = ['module_code', 'module_title', 'module_type', 'semester_offered', 'primary_programme',
                  'compulsory_in_primary_programme','students_year_of_study','secondary_programme','sub_programme', 'secondary_sub_programme','number_of_tutorial_groups', 'total_hours', ]
        labels = {'module_code' : _('Module Code'),
                  'module_title' : _('Module title'),
                  'module_type' : _('Type of module'),
                  'semester_offered' : _('Semester offered'),
                  'primary_programme' : _('Primary  programme the module is part of'),
                  'compulsory_in_primary_programme': _('Compulsory in primary programme?'),
                  'students_year_of_study': _('Year of study of students taking this module'),
                  'secondary_programme' : _('Another programme the module is part of'),
                  'sub_programme' : _('Sub-programme this module is part of'),
                  'secondary_sub_programme' : _('Another sub-programme this module is also part of'),
                  'number_of_tutorial_groups' : _('Number of tutorial groups'),
                  'total_hours' : _('Total hours')
                  }

        widgets = {'module_type' : forms.Select(choices=ModuleType.objects.all()),
                   'semester_offered' : forms.Select(choices=Module.SEMESTER_OFFERED),
                   'compulsory_in_primary_programme' : forms.Select(choices=Module.YES_NO_MODULE)}
        
    def __init__(self, *args, **kwargs):        
        super(ModuleForm, self).__init__(*args, **kwargs)
        self.fields['total_hours'].required = False
        self.fields['primary_programme'].required = False
        self.fields['compulsory_in_primary_programme'].required=False
        self.fields['students_year_of_study'].required=False
        self.fields['secondary_programme'].required = False
        self.fields['sub_programme'].required = False
        self.fields['secondary_sub_programme'].required = False
        #No editing of module codes of existing modules
        if 'fresh_record' in self.initial: #Must check, otherwise a KeyError occurs (I suspect this is run a couple of times upon post)
            if (self.initial["fresh_record"] == False):
                self.fields['module_code'].widget = forms.HiddenInput()#Hides the module code alltogether
                self.fields['manual_hours_checked'].widget = forms.HiddenInput()#Hides the checkbox
            
    class Media:
        """ 
        Media subclaas to associate the relevant JS. The JS hides/shwos the total hours field
        according to the tickbox status
        """
        
        js = ('workload_app/module_form.js',)           
                
class RemoveModuleForm(forms.Form):
    """
    Form to remove a module.
    
    Attributes
    ----------
    
    select_module_to_remove : ModelChoiceField
        the module to remove
    wipe_from_table : boolean
        whether or not to remove from all secnarios
    """
    REMOVE_COMPLETELY = 'Remove'
    RETIRE_ONLY = 'Retire'
    REMOVE_CHOICES = [(RETIRE_ONLY , 'No, remove only the assignments for this module'), (REMOVE_COMPLETELY, 'Yes, remove it from the list of modules')]

    def __init__(self, *args, **kwargs):
        workload_scenario_id = kwargs.pop('workloadscenario_id')
        super(RemoveModuleForm, self).__init__(*args, **kwargs)
        self.fields['select_module_to_remove'] = forms.ModelChoiceField(label = 'Select the module to remove or retire',\
                                                    queryset=Module.objects.filter(scenario_ref__id = workload_scenario_id));
        self.fields['wipe_from_table'] = forms.ChoiceField(label = 'Remove module entirely from the list of modules?', required=False,\
                                                      choices=self.REMOVE_CHOICES)
    
class ModuleTypeForm(forms.ModelForm):
    class Meta:
        model = ModuleType;
        fields = ['type_name']

class RemoveModuleTypeForm(forms.Form):
    select_module_type_to_remove = forms.ModelChoiceField(label = 'Select the module type to remove', queryset=ModuleType.objects.all())

class DepartmentForm(forms.ModelForm):
    #A flag to establish whether it's a new record or editing an existing one
    fresh_record = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    # The ID of the dpeartment being edited (for editing purposes only)
    dept_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Department;
        fields = ['department_name', 'department_acronym', 'faculty']
        labels = {'department_name' : _('Department name'),
                  'department_acronym' : _('Acronym to be used (max 4 letters)'),
                  'faculty' : _('Select the faculty this department belongs to ')}
    def clean(self):
        cleaned_data = super().clean();
        dept_name  = cleaned_data.get("department_name")
        #if it is a fesh record, we must make sure no duplicate names 
        if (cleaned_data.get("fresh_record") == True):
            if (Department.objects.filter(department_name = dept_name).exists()):
                raise ValidationError(_('Invalid department name: it alreday exists'), code='invalid')
        else: #This is an edit, we prevent editing into an existing name
            current_id = cleaned_data.get("dept_id")
            if (Department.objects.filter(department_name = dept_name).exclude(id = current_id).exists()):
                raise ValidationError(_('Invalid department name: it alreday exists'), code='invalid')

class RemoveDepartmentForm(forms.Form):
    select_department_to_remove = forms.ModelChoiceField(label = 'Select the department to remove', queryset=Department.objects.all())

class FacultyForm(forms.ModelForm):
    #A flag to establish whether it's a new record or editing an existing one
    fresh_record = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    # The ID of the faculty being edited (for editing purposes only)
    fac_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Faculty;
        fields = ['faculty_name', 'faculty_acronym']
        labels = {'faculty_name' : _('Faculty name'),
                  'faculty_acronym' : _('Acronym to be used (max 4 letters)')}
    def clean(self):
        cleaned_data = super().clean();
        fac_name  = cleaned_data.get("faculty_name")
        #if it is a fesh record, we must make sure no duplicate names 
        if (cleaned_data.get("fresh_record") == True):
            if (Faculty.objects.filter(faculty_name = fac_name).exists()):
                raise ValidationError(_('Invalid faculty name: it alreday exists'), code='invalid')
        else: #This is an edit, we prevent editing into an existing name
            current_id = cleaned_data.get("fac_id")
            if (Faculty.objects.filter(faculty_name = fac_name).exclude(id = current_id).exists()):
                raise ValidationError(_('Invalid faculty name: it alreday exists'), code='invalid')

class RemoveFacultyForm(forms.Form):
    select_faculty_to_remove = forms.ModelChoiceField(label = 'Select the faculty to remove', queryset=Faculty.objects.all())

class ServiceRoleForm(forms.ModelForm):
    
    fresh_record = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    role_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = ServiceRole;
        fields = ['role_name', 'role_adjustment']
        labels = {'role_name' : _('Title of the service role (e.g., Head of department)'),
                  'role_adjustment' : _('Multiplier for teaching expectations (e.g., 0 for no expectations, 2 for double, etc)')}
    
    def clean(self):
        cleaned_data = super().clean();
        role_name  = cleaned_data.get("role_name")
        #if it is a fesh record, we must make sure no duplicate names 
        if (cleaned_data.get("fresh_record") == True):
            if (ServiceRole.objects.filter(role_name = role_name).exists()):
                raise ValidationError(_('Invalid service role name: it alreday exists'), code='invalid')
        else: #This is an edit, we prevent editing into an existing name
            current_id = cleaned_data.get("role_id")
            if (ServiceRole.objects.filter(role_name = role_name).exclude(id = current_id).exists()):
                raise ValidationError(_('Invalid service role name: it alreday exists'), code='invalid')

class RemoveServiceRoleForm(forms.Form):
    select_service_role_to_remove = forms.ModelChoiceField(label = 'Select the service role to remove', queryset=ServiceRole.objects.all())

class ProgrammeOfferedForm(forms.ModelForm):
    
    fresh_record = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    prog_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    dept_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = ProgrammeOffered;
        fields = ['programme_name', 'primary_dept']
        labels = {'programme_name' : _('Name of the programme (e.g., Bachelor of...)'),
                  'primary_dept' : _('Primary Department offering the programme')}
    
    def clean(self):
        cleaned_data = super().clean();
        programme_name  = cleaned_data.get("programme_name")
        dept_offering  = cleaned_data.get("primary_dept")
        #if it is a fesh record, we must make sure no duplicate names 
        if (cleaned_data.get("fresh_record") == True):
            if (ProgrammeOffered.objects.filter(programme_name = programme_name).filter(primary_dept=dept_offering).exists()):
                raise ValidationError(_('Invalid programme name: it alreday exists'), code='invalid')
        else: #This is an edit, we prevent editing into an existing name
            if (ProgrammeOffered.objects.filter(programme_name = programme_name).filter(primary_dept=dept_offering).exists()):
                raise ValidationError(_('Invalid programme name: it alreday exists'), code='invalid')


class RemoveProgrammeForm(forms.Form):

    def __init__(self, *args, **kwargs):
        dept_id = kwargs.pop('department_id')
        super(RemoveProgrammeForm, self).__init__(*args, **kwargs)
        #Make user select programmes only offered by this department
        self.fields['select_programme_to_remove'] = forms.ModelChoiceField(label = 'Select the programe to remove', queryset=ProgrammeOffered.objects.filter(primary_dept__id = dept_id))

class SubProgrammeOfferedForm(forms.ModelForm):

    fresh_record = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    sub_prog_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    dept_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = SubProgrammeOffered;
        fields = ['sub_programme_name', 'main_programme']
        labels = {'sub_programme_name' : _('Name of the sub programme (e.g., Specialization in...)'),
                  'main_programme' : _('Main programme this subprogramme belongs to ')}
    
    def clean(self):
        cleaned_data = super().clean();
        sub_programme_name  = cleaned_data.get("sub_programme_name")
        main_programme  = cleaned_data.get("main_programme")
        #if it is a fesh record, we must make sure no duplicate names 
        if (cleaned_data.get("fresh_record") == True):
            if (SubProgrammeOffered.objects.filter(sub_programme_name = sub_programme_name).filter(main_programme=main_programme).exists()):
                raise ValidationError(_('Invalid subprogramme name: it alreday exists'), code='invalid')
        else: #This is an edit, we prevent editing into an existing name
            if (SubProgrammeOffered.objects.filter(sub_programme_name = sub_programme_name).filter(main_programme=main_programme).exists()):
                raise ValidationError(_('Invalid subprogramme name: it alreday exists'), code='invalid')

class RemoveSubProgrammeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        dept_id = kwargs.pop('department_id')
        super(RemoveSubProgrammeForm, self).__init__(*args, **kwargs)
        #Make user select programmes only offered by this department
        self.fields['select_subprogramme_to_remove'] = forms.ModelChoiceField(label = 'Select the sub-programe to remove', queryset=SubProgrammeOffered.objects.filter(main_programme__primary_dept__id = dept_id))

class EmplymentTrackForm(forms.ModelForm):

    fresh_record = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    employment_track_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = EmploymentTrack;
        fields = ['track_name', 'track_adjustment', 'is_adjunct']
        labels = {'track_name' : _('Name of the track (e.g., tenure track)'),
                  'track_adjustment' : _('Multiplier for teaching expectations (e.g., 0 for no expectations, 2 for double, etc)'),
                  'is_adjunct' : _('Whether or not this position refers to adjunct (not employed by the University) staff')}
    
    def clean(self):
        cleaned_data = super().clean();
        track_name  = cleaned_data.get("track_name")
        #if it is a fesh record, we must make sure no duplicate names 
        if (cleaned_data.get("fresh_record") == True):
            if (EmploymentTrack.objects.filter(track_name = track_name).exists()):
                raise ValidationError(_('Invalid employment track name: it alreday exists'), code='invalid')
        else: #This is an edit, we prevent editing into an existing name
            current_id = cleaned_data.get("employment_track_id")
            if (EmploymentTrack.objects.filter(track_name = track_name).exclude(id = current_id).exists()):
                raise ValidationError(_('Invalid employment track name: it alreday exists'), code='invalid')

class RemoveEmploymentTrackForm(forms.Form):
    select_track_to_remove = forms.ModelChoiceField(label = 'Select the track to remove', queryset=EmploymentTrack.objects.all())

class SLOForm(forms.ModelForm):

    fresh_record = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    slo_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    def __init__(self, *args, **kwargs):
        super(SLOForm, self).__init__(*args, **kwargs)
        self.fields['cohort_valid_from'].required = False
        self.fields['cohort_valid_to'].required = False

    class Meta:

        model = StudentLearningOutcome;
        fields = ['slo_description', 'slo_short_description', 'is_default_by_accreditor', 'letter_associated', 'cohort_valid_from', 'cohort_valid_to']
        labels = {'slo_description' : _('Description of the SLO'),
                  'slo_short_description' : _('A shorter description of the SLO'),
                  'is_default_by_accreditor' : _('Is this SLO a default one established by the accreditor? (If it is programme-sepcific, leave unticked)'),
                  'letter_associated' : _('The alphabetical letter this SLO is usually associated with'),
                  'cohort_valid_from' : _('This SLO applies to cohorts starting from  '),
                  'cohort_valid_to' : _('This SLO applies to cohorts until  ')}
        widgets = {'slo_description' : forms.Textarea}

class MLOForm(forms.ModelForm):

    fresh_record = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    mlo_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    mod_code = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = ModuleLearningOutcome;
        fields = ['mlo_description', 'mlo_short_description',]
        labels = {'mlo_description' : _('Description of the MLO'),
                  'mlo_short_description' : _('A shorter description of the MLO')}
        widgets = {'mlo_description' : forms.Textarea}

class RemoveMLOForm(forms.Form):
    def __init__(self, *args, **kwargs):
        module_code = kwargs.pop('module_code')
        super(RemoveMLOForm, self).__init__(*args, **kwargs)
        #Make user select only MLO of this module
        self.fields['select_mlo_to_remove'] = forms.ModelChoiceField(label = 'Select the MLO to remove', queryset=ModuleLearningOutcome.objects.filter(module_code = module_code))

class RemoveSLOForm(forms.Form):
    def __init__(self, *args, **kwargs):
        prog_id = kwargs.pop('programme_id')
        super(RemoveSLOForm, self).__init__(*args, **kwargs)
        #Make user select only SLO of this programme
        self.fields['select_slo_to_remove'] = forms.ModelChoiceField(label = 'Select the SLO to remove', queryset=StudentLearningOutcome.objects.filter(programme__id = prog_id))

class AddSLOSurveyForm(forms.Form):

    def __init__(self, *args, **kwargs):
        years_to_show = []
        year_now = datetime.datetime.now().year
        for gap in range(-6,3):
            years_to_show.append(year_now + gap)
        programme_id = kwargs.pop('programme_id')
        super(AddSLOSurveyForm, self).__init__(*args, **kwargs)
        self.fields['slo_survey_title'] = forms.CharField(label="Survey title (e.g., graduiate exit survey)")
        self.fields['start_date'] = forms.DateField(label="Start date of the survey distribution",widget=SelectDateWidget(empty_label="Nothing", years=years_to_show))
        self.fields['end_date'] = forms.DateField(label="End date of the survey distribution",widget=SelectDateWidget(empty_label="Nothing", years = years_to_show))
        self.fields['cohort_targeted'] = forms.ModelChoiceField(label='Cohort targeted', required=False,\
                                                      queryset=Academicyear.objects.filter(start_year__gte = year_now-5).filter(start_year__lte=year_now+1))
        self.fields['totoal_N_recipients'] = forms.IntegerField(label="Total number of recipients")
        self.fields['comments'] = forms.CharField(label="Notes", widget=forms.Textarea, required=False)
        self.fields['raw_file'] = forms.FileField(label="Upload raw survey results file", required=False)

        for slo in StudentLearningOutcome.objects.filter(programme__id = programme_id):
            slo_id = str(slo.id)
            self.fields['slo_descr'+slo_id] = forms.CharField(label="SLO: " + slo.slo_description, required=False, widget=forms.HiddenInput)
            self.fields['n_highest_score'+slo_id] = forms.IntegerField(label = NUS_SLO_SURVEY_LABELS[0])
            self.fields['n_second_highest_score'+slo_id] = forms.IntegerField(label = NUS_SLO_SURVEY_LABELS[1])
            self.fields['n_third_highest_score'+slo_id] = forms.IntegerField(label = NUS_SLO_SURVEY_LABELS[2])
            self.fields['n_fourth_highest_score'+slo_id] = forms.IntegerField(label = NUS_SLO_SURVEY_LABELS[3])
            self.fields['n_fifth_highest_score'+slo_id] = forms.IntegerField(label = NUS_SLO_SURVEY_LABELS[4])

class AddPEOSurveyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        years_to_show = []
        for gap in range(-6,3):
            years_to_show.append(datetime.datetime.now().year + gap)
        programme_id = kwargs.pop('programme_id')
        super(AddPEOSurveyForm, self).__init__(*args, **kwargs)
        self.fields['peo_survey_title'] = forms.CharField(label="Survey title (e.g., alumni survey)")
        self.fields['start_date'] = forms.DateField(label="Start date of the survey distribution",widget=SelectDateWidget(empty_label="Nothing", years=years_to_show))
        self.fields['end_date'] = forms.DateField(label="End date of the survey distribution",widget=SelectDateWidget(empty_label="Nothing", years = years_to_show))
        self.fields['totoal_N_recipients'] = forms.IntegerField(label="Total number of recipients")
        self.fields['comments'] = forms.CharField(label="Notes", widget=forms.Textarea, required=False)
        self.fields['raw_file'] = forms.FileField(label="Upload raw survey results file", required=False)

        for peo in ProgrammeEducationalObjective.objects.filter(programme__id = programme_id):
            peo_id = str(peo.id)
            self.fields['peo_descr'+peo_id] = forms.CharField(label="PEO: " + peo.peo_description, required=False, widget=forms.HiddenInput)
            self.fields['n_highest_score'+peo_id] = forms.IntegerField(label = NUS_SLO_SURVEY_LABELS[0])
            self.fields['n_second_highest_score'+peo_id] = forms.IntegerField(label = NUS_SLO_SURVEY_LABELS[1])
            self.fields['n_third_highest_score'+peo_id] = forms.IntegerField(label = NUS_SLO_SURVEY_LABELS[2])
            self.fields['n_fourth_highest_score'+peo_id] = forms.IntegerField(label = NUS_SLO_SURVEY_LABELS[3])
            self.fields['n_fifth_highest_score'+peo_id] = forms.IntegerField(label = NUS_SLO_SURVEY_LABELS[4])
              
class RemoveSLOSurveyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        programme_id = kwargs.pop('programme_id')
        super(RemoveSLOSurveyForm, self).__init__(*args, **kwargs)
        #Figure out the surveys associated with this module code
        my_ids = []
        for srv_resp in SurveyQuestionResponse.objects.filter(associated_slo__programme__id = programme_id):
            my_ids.append(srv_resp.parent_survey.id)
        #Remove duplicates
        my_ids = list(dict.fromkeys(my_ids))

        #Make user select surveys for this module only
        self.fields['select_SLO_survey_to_remove'] = forms.ModelChoiceField(queryset=Survey.objects.filter(pk__in=my_ids))

class RemovePEOSurveyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        programme_id = kwargs.pop('programme_id')
        super(RemovePEOSurveyForm, self).__init__(*args, **kwargs)
        #Figure out the surveys associated with this module code
        my_ids = []
        for srv_resp in SurveyQuestionResponse.objects.filter(associated_peo__programme__id = programme_id):
            my_ids.append(srv_resp.parent_survey.id)
        #Remove duplicates
        my_ids = list(dict.fromkeys(my_ids))

        #Make user select surveys for this module only
        self.fields['select_PEO_survey_to_remove'] = forms.ModelChoiceField(queryset=Survey.objects.filter(pk__in=my_ids))
        
class PEOForm(forms.ModelForm):
    fresh_record = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    peo_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    def __init__(self, *args, **kwargs):
        super(PEOForm, self).__init__(*args, **kwargs)
        self.fields['peo_cohort_valid_from'].required = False
        self.fields['peo_cohort_valid_to'].required = False
    class Meta:
        model = ProgrammeEducationalObjective;
        fields = ['peo_description', 'peo_short_description', 'letter_associated', 'peo_cohort_valid_from', 'peo_cohort_valid_to']
        labels = {'peo_description' : _('Description of the PEO'),
                  'peo_short_description' : _('A shorter description of the PEO'),
                  'letter_associated' : _('The alphabetical letter this PEO is usually associated with'),
                  'peo_cohort_valid_from': _('Cohort where this PEO started being valid'),
                  'peo_cohort_valid_to': _('Cohort where this PEO stopped being valid'),}
        widgets = {'peo_description' : forms.Textarea}

class RemovePEOForm(forms.Form):
    def __init__(self, *args, **kwargs):
        prog_id = kwargs.pop('programme_id')
        super(RemovePEOForm, self).__init__(*args, **kwargs)
        #Make user select only PEO of this programme
        self.fields['select_peo_to_remove'] = forms.ModelChoiceField(label = 'Select the PEOs to remove', queryset=ProgrammeEducationalObjective.objects.filter(programme__id = prog_id))

class PEOSLOMappingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        prog_id = kwargs.pop('prog_id')
        super(PEOSLOMappingForm, self).__init__(*args, **kwargs)
        self.fields['slo_id'] = forms.IntegerField(required=False, widget=forms.HiddenInput())
        for peo in ProgrammeEducationalObjective.objects.filter(programme__id = prog_id):
            self.fields['mapping_strength'+str(peo.id)] = forms.IntegerField(min_value=0, max_value=3, label='Enter mapping strength for PEO ' + peo.peo_description)
            self.fields['peo_id'] = forms.IntegerField(initial=peo.id, required=False, widget=forms.HiddenInput())
        
class MLOSLOMappingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        prog_id = kwargs.pop('prog_id')
        super(MLOSLOMappingForm, self).__init__(*args, **kwargs)
        self.fields['mlo_id'] = forms.IntegerField(required=False, widget=forms.HiddenInput())
        
        for slo in StudentLearningOutcome.objects.filter(programme__id = prog_id):
            self.fields['mlo_slo_mapping_strength'+str(slo.id)] = forms.IntegerField(min_value=0, max_value=3, label='Enter mapping strength for SLO: ' + slo.slo_description)
            self.fields['slo_id'] = forms.IntegerField(initial=slo.id, required=False, widget=forms.HiddenInput())

class AddMLOSurveyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        years_to_show = []
        for gap in range(-6,3):
            years_to_show.append(datetime.datetime.now().year + gap)
        module_code = kwargs.pop('module_code')
        super(AddMLOSurveyForm, self).__init__(*args, **kwargs)
        self.fields['start_date'] = forms.DateField(label="Start date of the survey distribution",widget=SelectDateWidget(empty_label="Nothing", years=years_to_show))
        self.fields['end_date'] = forms.DateField(label="End date of the survey distribution",widget=SelectDateWidget(empty_label="Nothing", years = years_to_show))
        self.fields['totoal_N_recipients'] = forms.IntegerField(label="Total number of recipients")
        self.fields['comments'] = forms.CharField(label="Notes", widget=forms.Textarea, required=False)
        self.fields['raw_file'] = forms.FileField(label="Upload raw results file", required=False)
        
        for mlo in ModuleLearningOutcome.objects.filter(module_code = module_code):
            mlo_id = str(mlo.id)
            self.fields['mlo_descr'+mlo_id] = forms.CharField(label="MLO: " + mlo.mlo_description, required=False, widget=forms.HiddenInput)
            self.fields['n_highest_score'+mlo_id] = forms.IntegerField()
            self.fields['n_second_highest_score'+mlo_id] = forms.IntegerField()
            self.fields['n_third_highest_score'+mlo_id] = forms.IntegerField()
            self.fields['n_fourth_highest_score'+mlo_id] = forms.IntegerField()

class RemoveMLOSurveyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        module_code = kwargs.pop('module_code')
        super(RemoveMLOSurveyForm, self).__init__(*args, **kwargs)
        #Figure out the surveys associated with this module code
        my_ids = []
        for srv_resp in SurveyQuestionResponse.objects.filter(associated_mlo__module_code = module_code):
            my_ids.append(srv_resp.parent_survey.id)
        #Remove duplicates
        my_ids = list(dict.fromkeys(my_ids))

        #Make user select surveys for this module only
        self.fields['select_MLO_survey_to_remove'] = forms.ModelChoiceField(queryset=Survey.objects.filter(pk__in=my_ids))

class MLOPerformanceMeasureForm(forms.Form):
    def __init__(self, *args, **kwargs):
        module_code = kwargs.pop('module_code')
        super(MLOPerformanceMeasureForm, self).__init__(*args, **kwargs)
        self.fields['academic_year'] = forms.ModelChoiceField(queryset=Academicyear.objects.filter(start_year__gte =  datetime.datetime.now().year - 5).filter(start_year__lte =  datetime.datetime.now().year + 5))
        self.fields['measure_description'] = forms.CharField(widget=forms.Textarea, label='Description (e.g., Final exam question 3, or Group presentation)')
        self.fields['percentage_score'] = forms.DecimalField(min_value=0, max_value=100, label="Percentage score (0 to 100)")
        self.fields['mlo_mapped_1']  = forms.ModelChoiceField(queryset=ModuleLearningOutcome.objects.filter(module_code = module_code), label="Associated MLO")
        self.fields['mlo_mapped_2']  = forms.ModelChoiceField(queryset=ModuleLearningOutcome.objects.filter(module_code = module_code), label="Other assocuated MLO (if any)", required=False)
        self.fields['mlo_mapped_3']  = forms.ModelChoiceField(queryset=ModuleLearningOutcome.objects.filter(module_code = module_code), label="Other assocuated MLO (if any)", required=False)
        self.fields['original_file'] = forms.FileField(label="Upload original file (e.g., the exam questions)", required=False)

class RemoveMLOPerformanceMeasureForm(forms.Form):
    def __init__(self, *args, **kwargs):
        module_code = kwargs.pop('module_code')
        super(RemoveMLOPerformanceMeasureForm, self).__init__(*args, **kwargs)
        #Make user select surveys for this module only
        self.fields['Select_MLO_measure_to_remove'] = forms.ModelChoiceField(queryset=MLOPerformanceMeasure.objects.filter(associated_mlo__module_code=module_code))

class AddTeachingAssignmentForm(forms.Form):

    YES_NO_CHOICES = [('no', 'No'), ('yes', 'Yes')] #Used by the radio button

    manual_hours_yes_no = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'teaching_assignment_radio_buttons_style'}), \
                                            choices=YES_NO_CHOICES, \
                                            label = "Enter total hours manually?",
                                            initial='no')
    enter_number_of_weekly_lecture_hours = forms.IntegerField(min_value=0, max_value=1000, \
                                           widget = forms.NumberInput(attrs={'class' : 'teaching_assignment_weekly_hours'}), required=False)
    enter_number_of_weekly_tutorial_hours = forms.IntegerField(min_value=0, max_value=1000,\
                                           widget = forms.NumberInput(attrs={'class' : 'teaching_assignment_weekly_hours'}), required=False)
    enter_number_of_tutorial_groups = forms.IntegerField(min_value=0, max_value=1000,\
                                           widget = forms.NumberInput(attrs={'class' : 'teaching_assignment_weekly_hours'}), required=False)
    enter_number_of_weeks_assigned = forms.IntegerField(min_value=0, max_value=1000, \
                                           widget = forms.NumberInput(attrs={'class' : 'teaching_assignment_weekly_hours'}), required=False)
    
    enter_number_of_total_hours_assigned = forms.IntegerField(min_value=0, max_value=100000, \
                                            widget = forms.NumberInput(attrs={'class' : 'teaching_assignment_manual_hours'}), required=False)
    
    counted_towards_workload = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'teaching_assignment_counted_style'}), \
                                            choices=YES_NO_CHOICES, \
                                            label = "Counted towards workload?",
                                            initial='yes')

    def __init__(self, *args, **kwargs):
        id_of_prof_involved = kwargs.pop('prof_id')
        id_of_mod_involved = kwargs.pop('module_id')
        workload_scenario_id = kwargs.pop('workloadscenario_id')
        super(AddTeachingAssignmentForm, self).__init__(*args, **kwargs)
        self.fields['select_lecturer'] = forms.ModelChoiceField(queryset=Lecturer.objects.filter(workload_scenario__id = int(workload_scenario_id)).order_by('name'));
        self.fields['select_module'] = forms.ModelChoiceField(queryset=Module.objects.filter(scenario_ref__id = int(workload_scenario_id)));

        if str(id_of_prof_involved) != str(-1): # a bit dodgy, but comparing against -1 works to check if name is found
            self.fields['select_lecturer'].widget = forms.HiddenInput()#Hides the name alltogether
            self.fields['select_lecturer'].initial = Lecturer.objects.get(id = id_of_prof_involved)
        if str(id_of_mod_involved) != str(-1): #see above
            self.fields['select_module'].widget = forms.HiddenInput()#Hides the module alltogether
            self.fields['select_module'].initial = Module.objects.get(id = id_of_mod_involved)

        field_order = [
            'select_lecturer',
            'select_module',
            'counted_towards_workload',
            'manual_hours_yes_no',
            'enter_number_of_weekly_lecture_hours',
            'enter_number_of_weekly_tutorial_hours',
            'enter_number_of_tutorial_groups',
            'enter_number_of_weeks_assigned',
            'enter_number_of_total_hours_assigned']
        self.order_fields(field_order=field_order)

    #Override validation depending on radio button
    def clean(self):
        cleaned_data = super().clean()
        manual_hours_wanted = cleaned_data.get("manual_hours_yes_no")
        if (manual_hours_wanted == 'yes'):
            num_tot_hrs = cleaned_data.get("enter_number_of_total_hours_assigned")
            if  num_tot_hrs in EMPTY_VALUES:
                raise ValidationError(_('Must supply number of hours'), code='missing_total_hrs')
        if (manual_hours_wanted == 'no'):
            num_lect_hrs = cleaned_data.get("enter_number_of_weekly_lecture_hours")
            num_tut_hrs = cleaned_data.get("enter_number_of_weekly_tutorial_hours")
            num_tut_grps = cleaned_data.get("enter_number_of_tutorial_groups")
            num_weeks = cleaned_data.get("enter_number_of_weeks_assigned")
            
            if  num_lect_hrs in EMPTY_VALUES:
                raise ValidationError(_('Must supply number of lecture hours'), code='missing_lect_hrs') 
            if  num_tut_hrs in EMPTY_VALUES:
                raise ValidationError(_('Must supply number of tutroial hours'), code='missing_tut_hrs')
            if  num_tut_grps in EMPTY_VALUES:
                raise ValidationError(_('Must supply number of tutorial groups'), code='missing_num_groups')
            if  num_weeks in EMPTY_VALUES:
                raise ValidationError(_('Must supply number of weeks'), code='missing_num_weeks')
    
    class Media:
        """ 
        Media subclaas to associate the relevant JS. The JS hides/shwos the rlevant hours input field
        according to the radiobox status
        """
        js = ('workload_app/teaching_assignment_form.js',)   
            
class RemoveTeachingAssignmentForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        workload_scenario_id = kwargs.pop('workloadscenario_id')
        super(RemoveTeachingAssignmentForm, self).__init__(*args, **kwargs)
        #Make user select teaching assignmemnts only in the current scenario
        self.fields['select_teaching_assignment_to_remove'] = forms.ModelChoiceField(queryset=TeachingAssignment.objects.filter(workload_scenario__id = workload_scenario_id))

class EditTeachingAssignmentForm(forms.Form):
    """
    This form is the one that changes a teaching assignment for a specific prof.
    The fields are all the assignments for that particular prof.
    """
    def __init__(self, *args, **kwargs):
        YES_NO_CHOICES = [('no', 'No'), ('yes', 'Yes')] #Used by the radio button
        prof_id = kwargs.pop('prof_id')
        super(EditTeachingAssignmentForm, self).__init__(*args, **kwargs)
        all_assignments_for_prof = TeachingAssignment.objects.filter(assigned_lecturer__id = prof_id)
        
        for assign in all_assignments_for_prof:
            module_assigned = assign.assigned_module.module_code
            module_label = ' (' + module_assigned + ')'
            full_label = "Assignments for " + module_assigned
            self.fields[module_assigned] = forms.CharField(initial=module_assigned,widget=forms.HiddenInput(), label = full_label, required=False)
            if (assign.assigned_manually == True):
                num_hrs = assign.number_of_hours
                self.fields['total_hours'+module_assigned] = forms.IntegerField(label='Total hours ' + module_label,initial=num_hrs, min_value=0, max_value=100000,\
                                                                help_text=' hours', required=False)
            else:#this assignment had been done through weekly assignments               
                weekly_lect = assign.number_of_weekly_lecture_hours
                weekly_tut = assign.number_of_weekly_tutorial_hours
                num_tut = assign.number_of_tutorial_groups
                num_weeks = assign.number_of_weeks_assigned
                
                self.fields['weekly_lecture_hrs'+module_assigned] = forms.IntegerField(label = 'Weekly lecture hrs' + module_label,min_value=0, max_value=1000, \
                                                                      initial = weekly_lect, required=False)
                self.fields['weekly_tutorial_hrs'+module_assigned] = forms.IntegerField(label = 'Weekly tutorial hrs' + module_label,min_value=0, max_value=1000, \
                                                                      initial = weekly_tut, required=False)
                self.fields['num_tut'+module_assigned] = forms.IntegerField(label = 'Number of tutorial grps' + module_label,min_value=0, max_value=1000, \
                                                                      initial = num_tut, required=False)
                self.fields['num_weeks'+module_assigned] = forms.IntegerField(label = 'Number of weeks' + module_label,min_value=0, max_value=1000, \
                                                                      initial = num_weeks, required=False)
            counted_flag = 'yes'
            if (assign.counted_towards_workload == False): counted_flag = 'no'                                       
            self.fields['counted_in_workload'+module_assigned] = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'teaching_assignment_counted_style'}), \
                                            choices=YES_NO_CHOICES, \
                                            label = "Counted towards workload?",
                                            initial=counted_flag)

class EditModuleAssignmentForm(forms.Form):
    """
    This form is the one that chnages a teaching assignment for a specific module
    The fields are all the assignments for that particular module.
    """
    def __init__(self, *args, **kwargs):
        YES_NO_CHOICES = [('no', 'No'), ('yes', 'Yes')] #Used by the radio button
        module_id = kwargs.pop('module_id')
        super(EditModuleAssignmentForm, self).__init__(*args, **kwargs)
        all_assignments_for_module = TeachingAssignment.objects.filter(assigned_module__id = module_id)

        for assign in all_assignments_for_module: 
            prof_assigned = assign.assigned_lecturer.name
            prof_label = ' (' + prof_assigned + ')'
            full_label = "Assignments for " + prof_assigned
            self.fields[prof_assigned] = forms.CharField(initial=prof_assigned,widget=forms.HiddenInput(), label = full_label, required=False);

            if (assign.assigned_manually == True):           
                num_hrs = assign.number_of_hours
                self.fields['total_hours'+prof_assigned] = forms.IntegerField(label='Total hours ' + prof_label,initial=num_hrs, min_value=0, max_value=100000,\
                        help_text=' hours', required=False)
            else:
                weekly_lect = assign.number_of_weekly_lecture_hours
                weekly_tut = assign.number_of_weekly_tutorial_hours
                num_tut = assign.number_of_tutorial_groups
                num_weeks = assign.number_of_weeks_assigned
                self.fields['weekly_lecture_hrs'+prof_assigned] = forms.IntegerField(label = 'Weekly lecture hrs' + prof_label,min_value=0, max_value=1000, \
                                                                      initial = weekly_lect, required=False)
                self.fields['weekly_tutorial_hrs'+prof_assigned] = forms.IntegerField(label = 'Weekly tutorial hrs' + prof_label,min_value=0, max_value=1000, \
                                                                      initial = weekly_tut, required=False)
                self.fields['num_tut'+prof_assigned] = forms.IntegerField(label = 'Number of tutorial grps' + prof_label,min_value=0, max_value=1000, \
                                                                      initial = num_tut, required=False)
                self.fields['num_weeks'+prof_assigned] = forms.IntegerField(label = 'Number of weeks' + prof_label,min_value=0, max_value=1000, \
                                                                      initial = num_weeks, required=False)
            counted_flag = 'yes'
            if (assign.counted_towards_workload == False): counted_flag = 'no' 
            self.fields['counted_in_workload'+prof_assigned] = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'teaching_assignment_counted_style'}), \
                                            choices=YES_NO_CHOICES, \
                                            label = "Counted towards workload?",
                                            initial=counted_flag)


        
    
class ScenarioForm(ModelForm):
    #A flag to establish whether it's a new record or editing an existing one
    fresh_record = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    #The ID of the workload being edited (only used when editing)
    scenario_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    #This is another flag to signal whether the assignments need to be copied 
    #from another workload
    copy_from = forms.ModelChoiceField(required=False,label="Select an existing workload scenario to copy from",\
                                        empty_label="No, thanks. Create an empty one",queryset=WorkloadScenario.objects.all())
    
    class Meta:
        model = WorkloadScenario
        fields = ['label','dept', 'academic_year','status']
        labels = {'label' : _('Name of the workload scenario'), 'dept' : _('Department'), 'Academic Year' : _('academic_year'),'status' : _('Status')}

    def __init__(self, *args, **kwargs):
        super(ScenarioForm, self).__init__(*args, **kwargs)
        if 'fresh_record' in self.initial: #Must check, otherwise a KeyError occurs (I suspect this is run a couple of times upon post)
            if (self.initial["fresh_record"] == False):
                #First, we hide the copy-from. ///\TODO re-activate this and allow copy upon editing (may require substantial work in the view)
                self.fields['copy_from'].widget = forms.HiddenInput()#Hides the widget alltogether

    def clean(self):
        cleaned_data = super().clean();
        scen_name  = cleaned_data.get("label")
        #if it is a fesh record, we must make sure no duplicate names 
        if (cleaned_data.get("fresh_record") == True):
            if (WorkloadScenario.objects.filter(label = scen_name).exists()):
                raise ValidationError(_('Invalid workload name: it alreday exists'), code='invalid')
        else: #This is an edit, we prevent editing into an existing name
            current_id = cleaned_data.get("scenario_id")
            if (WorkloadScenario.objects.filter(label = scen_name).exclude(id = current_id).exists()):
                raise ValidationError(_('Invalid workload name: it alreday exists'), code='invalid')
              
class RemoveScenarioForm(forms.Form):
    select_scenario_to_remove = forms.ModelChoiceField(queryset=WorkloadScenario.objects.all())

class SelectLecturerForReport(forms.Form):
    select_lecturer = forms.CharField(label = 'Lecturer\'s name ')

class SelectFacultyForReport(forms.Form):
    EXPECTATION_PER_tFTE= 'Expected hours per tFTE'
    TOTAL_TFTE = 'Total tFTE'
    
    FACULTY_REPORT_TYPES = [
        (EXPECTATION_PER_tFTE, 'Expected hours per tFTE'),
        (TOTAL_TFTE, 'Total tFTE'),
    ]

    select_faculty = forms.ModelChoiceField(queryset=Faculty.objects.all(), label="Select the faculty for the report")
    select_report_type = forms.ChoiceField(choices=FACULTY_REPORT_TYPES, label='Select the type of report')

class SelectAcademicYearForm(forms.Form):
    this_year = datetime.datetime.now().year
    select_academic_year = forms.ModelChoiceField(queryset=Academicyear.objects.filter(start_year__gt=(this_year-7)).filter(start_year__lt=(this_year+5)))

class SelectAccreditationReportForm(forms.Form):
    this_year = datetime.datetime.now().year
    academic_year_start = forms.ModelChoiceField(queryset=Academicyear.objects.filter(start_year__gt=(this_year-7)).filter(start_year__lt=(this_year+5)))
    academic_year_end = forms.ModelChoiceField(queryset=Academicyear.objects.filter(start_year__gt=(this_year-7)).filter(start_year__lt=(this_year+5)))
