import datetime
import math
import os
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms import ValidationError
from django.conf import settings
from django.db.models import F
from django.core.files.storage import default_storage


from .models import Lecturer, Module, TeachingAssignment, WorkloadScenario, ModuleType, Department, EmploymentTrack,\
                    ServiceRole, Faculty,Academicyear,ProgrammeOffered,SubProgrammeOffered, StudentLearningOutcome,\
                    ProgrammeEducationalObjective,PEOSLOMapping, ModuleLearningOutcome, MLOSLOMapping,Survey,\
                    SurveyQuestionResponse,MLOPerformanceMeasure,CorrectiveAction,UniversityStaff
from .forms import ProfessorForm, RemoveProfessorForm, ModuleForm, RemoveModuleForm,AddTeachingAssignmentForm,\
                   RemoveTeachingAssignmentForm,ScenarioForm,RemoveScenarioForm,EditTeachingAssignmentForm,\
                   EditModuleAssignmentForm, RemoveModuleTypeForm, ModuleTypeForm, DepartmentForm, RemoveDepartmentForm,\
                   EmplymentTrackForm, RemoveEmploymentTrackForm,ServiceRoleForm, RemoveServiceRoleForm,\
                   FacultyForm, RemoveFacultyForm, SelectFacultyForReport,ProgrammeOfferedForm,\
                   RemoveProgrammeForm,SLOForm,RemoveSLOForm,SubProgrammeOfferedForm,RemoveSubProgrammeForm,\
                   SelectAcademicYearForm,PEOForm,RemovePEOForm,PEOSLOMappingForm,MLOForm,RemoveMLOForm,MLOSLOMappingForm,\
                   AddMLOSurveyForm,RemoveMLOSurveyForm,MLOPerformanceMeasureForm,RemoveMLOPerformanceMeasureForm,\
                   AddSLOSurveyForm,RemoveSLOSurveyForm, RemovePEOSurveyForm,AddPEOSurveyForm,SelectAccreditationReportForm,\
                   CorrectiveActionForm, RemoveCorrectiveActionForm, InputPEOSurveyDataForm, InputSLOSurveyDataForm, InputMLOSurveyForm,EditSurveySettingsForm

from .global_constants import DEFAULT_TRACK_NAME, DEFAULT_SERVICE_ROLE_NAME, DEFAULT_FACULTY_NAME,\
                              DEFAULT_FACULTY_ACRONYM,CalculateNumHoursBasedOnWeeklyInfo, DEFAULT_DEPARTMENT_NAME, DEFAULT_DEPT_ACRONYM,\
                              requested_table_type,COLOUR_SCHEMES, accreditation_outcome_type,ShortenString
from .helper_methods import CalculateDepartmentWorkloadTable, CalculateModuleWorkloadTable,CalculateSummaryData,\
                            CalculateTotalModuleHours,CalculateWorkloadsIndexTable,\
                            CalculateEmploymentTracksTable, CalculateServiceRolesTable, CalculateModuleTypeTable, CalculateDepartmentTable,\
                            CalculateFacultiesTable,CalculateModuleTypesTableForProgramme, CalculateModuleHourlyTableForProgramme,\
                            CalculateSingleModuleInformationTable, HandleScenarioForm
from .helper_methods_survey import CalculateSurveyDetails,DetermineSurveyLabelsForProgramme,DeteremineSurveyInitialValues
from .helper_methods_accreditation import DetermineIconBasedOnStrength,CalculateTableForOverallSLOMapping,\
                                          CalculateAllInforAboutOneSLO, DisplayOutcomeValidity, CalculateAttentionScoresSummaryTable

from .report_methods import GetLastNYears,CalculateProfessorIndividualWorkload, CalculateProfessorChartData, CalculateFacultyReportTable
from .helper_methods_users import DetermineUserHomePage, CanUserAdminThisDepartment, CanUserAdminThisModule, CanUserAdminThisFaculty,\
      CanUserAdminUniversity, CanUserAdminThisLecturer, DetermineUserMenu
from .helper_methods_demo import populate_database

def post_login_landing(request):
    myerror = "error"
    home_page  = DetermineUserHomePage(request.user.id,request.user.is_superuser,error_text = myerror)
    if (home_page == myerror):
        user_menu  = DetermineUserMenu(request.user.id,request.user.is_superuser)
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "Access forbidden. User has no access to this page",
                'user_menu' : user_menu,
                'user_homepage' : home_page
        }
        return HttpResponse(template.render(context, request))
    
    return HttpResponseRedirect('/workload_app'+home_page)

##This is the for the page of a single workload scenario
def scenario_view(request, workloadscenario_id):

    user_menu  = DetermineUserMenu(request.user.id,request.user.is_superuser)
    user_homepage = DetermineUserHomePage(request.user.id,request.user.is_superuser)

    dept_id = WorkloadScenario.objects.filter(id = workloadscenario_id).get().dept.id
    if request.user.is_authenticated == False or CanUserAdminThisDepartment(request.user.id,dept_id, is_super_user = request.user.is_superuser)==False:
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "Access forbidden. User has no access to this page",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))
    
    #Name of this scenario (this will be displayed)
    name_of_active_scenario = WorkloadScenario.objects.filter(id = workloadscenario_id).get().label
    department = WorkloadScenario.objects.filter(id = workloadscenario_id).get().dept
    acad_year = WorkloadScenario.objects.filter(id = workloadscenario_id).get().academic_year
    status = WorkloadScenario.objects.filter(id = workloadscenario_id).get().status
    edit_active_scenario_form = ScenarioForm(initial = {'fresh_record' : False, 'scenario_id' : workloadscenario_id,\
                                                        'label' : name_of_active_scenario,
                                                        'dept' : department,
                                                        'status' : status,
                                                        'academic_year' : acad_year}).as_p()

    workload_table  = CalculateDepartmentWorkloadTable(workloadscenario_id)
    modules_table = CalculateModuleWorkloadTable(workloadscenario_id)
    summary_data = CalculateSummaryData(workloadscenario_id)
    
    #Make sure the empty forms are avilable to the scenario page
    #NOTE: The edit assignments form is created within within wl_table
    
    #Lecturer forms (the edit forms are added in the helper methods in the table)
    prof_form = ProfessorForm(initial = {'fresh_record' : True})
    remove_prof_form = RemoveProfessorForm(workloadscenario_id = workloadscenario_id)
    #Module forms (the edit forms are added in the helper methods in the table)
    mod_form  = ModuleForm(dept_id = department.id,initial = {'fresh_record' : True})
    remove_mod_form = RemoveModuleForm(workloadscenario_id = workloadscenario_id)
    
    #Teaching Assignment forms
    add_teaching_assignment_form = AddTeachingAssignmentForm(auto_id=False, prof_id = -1, module_id= -1, workloadscenario_id = workloadscenario_id)
    remove_teaching_assignment_form = RemoveTeachingAssignmentForm(workloadscenario_id = workloadscenario_id)
    
    template = loader.get_template('workload_app/workload.html')
    context = {
        'workloadscenario_id' : workloadscenario_id,
        'name_of_active_scenario' : name_of_active_scenario,
        'edit_active_scenario_form' : edit_active_scenario_form,
        'wl_table': workload_table,
        'mod_table':modules_table,
        'summary_data' : summary_data,
        'prof_form':prof_form.as_p(),
        'remove_prof_form':remove_prof_form.as_p(),
        'mod_form':mod_form,
        'remove_mod_form':remove_mod_form.as_p(),
        'add_teaching_assignment_form':add_teaching_assignment_form,
        'remove_teaching_assignment_form':remove_teaching_assignment_form.as_p(),
        'department_id' : department.id,
        'user_menu' : user_menu,
        'user_homepage' : user_homepage
    }
    return HttpResponse(template.render(context, request))

def school_page(request,faculty_id):
    user_menu  = DetermineUserMenu(request.user.id,request.user.is_superuser)
    user_homepage = DetermineUserHomePage(request.user.id,request.user.is_superuser)
    fac_qs = Faculty.objects.filter(id = faculty_id)
    if (fac_qs.count() != 1):#This should never happen, but just in case user puts in some random number...
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "Requested faculty does not exist",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))
    
    
    fac_obj = fac_qs.get()
    if request.user.is_authenticated == False or CanUserAdminThisFaculty(request.user.id,faculty_id, is_super_user = request.user.is_superuser)==False:
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "Access forbidden. User has no access to this page",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))
    
    
    if request.method =='POST':

        form = EmplymentTrackForm(request.POST)
        if form.is_valid():  
            supplied_track_name = form.cleaned_data['track_name']
            supplied_track_adj = form.cleaned_data['track_adjustment']
            supplied_is_adjunct_flag = form.cleaned_data['is_adjunct']
            if (request.POST['fresh_record'] == 'False'):
                #This is an edit
                supplied_id = form.cleaned_data['employment_track_id']
                EmploymentTrack.objects.filter(id = int(supplied_id)).update(track_name = supplied_track_name,\
                    track_adjustment = float(supplied_track_adj), is_adjunct = supplied_is_adjunct_flag)
            else:
                #This is a new track
                new_track = EmploymentTrack.objects.create(track_name = supplied_track_name, \
                                                           track_adjustment = float(supplied_track_adj),is_adjunct = supplied_is_adjunct_flag,\
                                                           faculty =  fac_obj)
                new_track.save()
        
        form = ServiceRoleForm(request.POST)
        if form.is_valid():  
            supplied_role_name = form.cleaned_data['role_name']
            supplied_role_adj = form.cleaned_data['role_adjustment']
            
            if (request.POST['fresh_record'] == 'False'):
                supplied_id = form.cleaned_data['role_id']
                #This is an edit
                ServiceRole.objects.filter(id = int(supplied_id)).update(role_name = supplied_role_name, role_adjustment = float(supplied_role_adj))               
            else:
                #This is a new role
                new_role = ServiceRole.objects.create(role_name = supplied_role_name, role_adjustment = float(supplied_role_adj), faculty = fac_obj)
                new_role.save()
        
        form = RemoveServiceRoleForm(request.POST, faculty_id = faculty_id)
        if form.is_valid():  
            selected_role = form.cleaned_data['select_service_role_to_remove']
            if (selected_role.role_name != DEFAULT_SERVICE_ROLE_NAME):#If user wants to delete the default, we do nothing
                default_role = ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME)
                if (default_role.count() == 0): #If, for some reason, the default role is not there, create one (this should be impossible...)
                    ServiceRole.objects.create(role_name = DEFAULT_SERVICE_ROLE_NAME, role_adjustment = 1.0)
                    default_role = ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME)               
                #Turn all lecturers of the removed service role to the default one
                Lecturer.objects.filter(service_role__role_name=selected_role).update(service_role = default_role.get().id)
                ServiceRole.objects.filter(role_name=selected_role).delete()
        
        form = RemoveEmploymentTrackForm(request.POST, faculty_id=faculty_id)
        if form.is_valid():  
            selected_track = form.cleaned_data['select_track_to_remove']
            if (selected_track.track_name != DEFAULT_TRACK_NAME):#If user wants to delete the default, we do nothing
                default_track = EmploymentTrack.objects.filter(track_name = DEFAULT_TRACK_NAME)
                if (default_track.count() == 0): #If, for some reason, the default track is not there, create one (this should be impossible...)
                    EmploymentTrack.objects.create(track_name = DEFAULT_TRACK_NAME, track_adjustment = 1.0)
                    default_track = EmploymentTrack.objects.filter(track_name = DEFAULT_TRACK_NAME)

                #Turn all lecturers of that track to the default track
                Lecturer.objects.filter(employment_track__track_name=selected_track).update(employment_track = default_track.get().id)
                EmploymentTrack.objects.filter(track_name=selected_track).delete()
        
        #trigger a GET
        return HttpResponseRedirect(reverse('workload_app:school_page',  kwargs={'faculty_id': faculty_id}))
    else: #This is a get
        overall_table = CalculateWorkloadsIndexTable(faculty_id = faculty_id)

        scenario_form = ScenarioForm(initial = {'fresh_record' : True})
        remove_scenario_form = RemoveScenarioForm(dept_id=-1) #-1 indicates no dept restrictions
        
        #Dept forms
        dept_form = DepartmentForm(initial = {'fresh_record' : True})
        remove_dept_form = RemoveDepartmentForm()

        employment_track_form = EmplymentTrackForm(initial = {'fresh_record' : True})
        remove_employment_track_form = RemoveEmploymentTrackForm(faculty_id=faculty_id)

        service_role_form = ServiceRoleForm(initial = {'fresh_record' : True})
        remove_service_role_form = RemoveServiceRoleForm(faculty_id = faculty_id)

        tracks_table = CalculateEmploymentTracksTable(faculty_id = faculty_id)
        roles_table = CalculateServiceRolesTable(faculty_id = faculty_id)
    
        department_table = CalculateDepartmentTable(faculty_id=faculty_id)

        template = loader.get_template('workload_app/school_page.html')
        context = { 'faculty_id' : faculty_id,
                    'school_name' : fac_obj.faculty_name,
                    'overall_table' : overall_table,
                    'tracks_table' : tracks_table,
                    'roles_table' : roles_table,
                    'department_table' : department_table,
                    'dept_form': dept_form.as_p(),
                    'remove_dept_form':remove_dept_form.as_p(),
                    'employment_track_form': employment_track_form.as_p(),
                    'remove_employment_track_form' : remove_employment_track_form.as_p(),
                    'service_role_form' : service_role_form.as_p(),
                    'remove_service_role_form' : remove_service_role_form.as_p(),
                    'scenario_form':scenario_form.as_p(),
                    'remove_scenario_form':remove_scenario_form.as_p(),
                    'user_menu' : user_menu,
                    'user_homepage' : user_homepage
                    }
        return HttpResponse(template.render(context, request))

def workloads_index(request):
    user_menu  = DetermineUserMenu(request.user.id,request.user.is_superuser)
    user_homepage = DetermineUserHomePage(request.user.id,request.user.is_superuser)
    #populate_database()#-Used to generate DB for demo leave commented out
    if request.user.is_authenticated == False or CanUserAdminUniversity(request.user.id, is_super_user = request.user.is_superuser)==False:
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "Access forbidden. User has no access to this page",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))
    
    #If no Faculty, create a default one
    if (Faculty.objects.all().count() == 0):
        Faculty.objects.create(faculty_name = DEFAULT_FACULTY_NAME, faculty_acronym = DEFAULT_FACULTY_ACRONYM)
    
    #If no Department, create a default one
    if (Department.objects.all().count() == 0):
        Department.objects.create(department_name = DEFAULT_DEPARTMENT_NAME, department_acronym = DEFAULT_DEPT_ACRONYM)

    #If no track adjustment, create a default one
    if (EmploymentTrack.objects.all().count() == 0):
        EmploymentTrack.objects.create(track_name = DEFAULT_TRACK_NAME, is_adjunct = False, track_adjustment = 1.0)

    #If no role, create a default one
    if (ServiceRole.objects.all().count() == 0):
        ServiceRole.objects.create(role_name = DEFAULT_SERVICE_ROLE_NAME, role_adjustment = 1.0)

    #If no academic year, create a few ones
    if (Academicyear.objects.all().count() == 0):
        for year in range(2000, 2050):
            Academicyear.objects.create(start_year = year)

    overall_table = CalculateWorkloadsIndexTable()

    #Scenario forms
    scenario_form = ScenarioForm(initial = {'fresh_record' : True})
    remove_scenario_form = RemoveScenarioForm(dept_id=-1) #-1 indicates no dept restrictions
    
    #Dept forms
    dept_form = DepartmentForm(initial = {'fresh_record' : True})
    remove_dept_form = RemoveDepartmentForm()

    #Faculty forms
    fac_form = FacultyForm()
    remove_fac_form = RemoveFacultyForm()
 
    department_table = CalculateDepartmentTable()
    faculty_table = CalculateFacultiesTable()

    template = loader.get_template('workload_app/workloads_index.html')
    context = {'overall_table' : overall_table,
                'department_table' : department_table,
                'faculty_table' : faculty_table,
                'dept_form': dept_form.as_p(),
                'fac_form' : fac_form.as_p(),
                'remove_fac_form' : remove_fac_form.as_p(),
                'remove_dept_form':remove_dept_form.as_p(),
               'scenario_form':scenario_form.as_p(),
               'remove_scenario_form':remove_scenario_form.as_p(),
               'user_menu' : user_menu,
                'user_homepage' : user_homepage
                }
    return HttpResponse(template.render(context, request))

def lecturer_page(request,lecturer_id):
    user_menu  = DetermineUserMenu(request.user.id,request.user.is_superuser)
    user_homepage = DetermineUserHomePage(request.user.id,request.user.is_superuser)
    lecturer_qs = Lecturer.objects.filter(id = lecturer_id)
    if (lecturer_qs.count() != 1):#this should never happen, but just in case the user enters some random number
        #This should really never happen, but just in case the user enters some random number...
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "No such lecturer exists",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))
    
    if request.user.is_authenticated == False or CanUserAdminThisLecturer(request.user.id,lecturer_id  = lecturer_id, is_super_user = request.user.is_superuser)==False:
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "Access forbidden. User has no access to this page",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))
    
    lec_name = lecturer_qs.get().name
    summary_wl_table = CalculateProfessorIndividualWorkload(lec_name)
    chart_data = CalculateProfessorChartData(lec_name)

    template = loader.get_template('workload_app/lecturer_page.html')
    context = {
        'return_page' : 'scenario_view/'+'1',
        'lec_name' : lec_name,
        'summary_wl_table_individual' : summary_wl_table,
        'chart_data' : chart_data,
        'user_menu' : user_menu,
        'user_homepage' : user_homepage
    }
    return HttpResponse(template.render(context, request))       

def faculty_report(request):
    user_menu  = DetermineUserMenu(request.user.id,request.user.is_superuser)
    user_homepage = DetermineUserHomePage(request.user.id,request.user.is_superuser)
    time_info  = GetLastNYears(5)
    labels = time_info["labels"]
    years = time_info["years"]
    table_header = " "
    data_for_table = []
    if request.method =='POST':
        faculty_form = SelectFacultyForReport(request.POST)
        if (faculty_form.is_valid()):
            table_header = faculty_form.cleaned_data["select_report_type"]
            faculty_name = faculty_form.cleaned_data["select_faculty"]
            data_for_table = CalculateFacultyReportTable(faculty = faculty_name, report_type = table_header)
        
    else:#GET
        faculty_form = SelectFacultyForReport()
    
    template = loader.get_template('workload_app/faculty_report.html')
    context = {
        'faculty_form'  : faculty_form,
        'table_header' : table_header,
        'labels_faculty' : labels,
        'data_for_faculty_table' : data_for_table,
        'user_menu' : user_menu,
        'user_homepage' : user_homepage
    }
    return HttpResponse(template.render(context, request))

def department(request,department_id):
    user_menu  = DetermineUserMenu(request.user.id,request.user.is_superuser)
    user_homepage = DetermineUserHomePage(request.user.id,request.user.is_superuser)
    
    if request.user.is_authenticated == False or CanUserAdminThisDepartment(request.user.id,department_id, is_super_user = request.user.is_superuser)==False:
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "Access forbidden. User has no access to this page",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))

    if (Department.objects.filter(id = department_id).count() == 0):
        #This should really never happen, but just in case the user enters some random number...
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "No such department exists",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))

    if request.method =='POST':
        new_wl_form = ScenarioForm(request.POST)
        if(new_wl_form.is_valid()):
            HandleScenarioForm(new_wl_form,department_id)

        remove_wl_form =  RemoveScenarioForm(request.POST, dept_id=department_id)
        if remove_wl_form.is_valid():
            selected_scenario_label = remove_wl_form.cleaned_data['select_scenario_to_remove']
            how_many_scenarios = WorkloadScenario.objects.all().count()
            if (how_many_scenarios>1):
                #Remove relevant teaching assignment
                TeachingAssignment.objects.filter(workload_scenario__label = selected_scenario_label).delete()
                #Remove the selected scenario.
                WorkloadScenario.objects.filter(label=selected_scenario_label).delete()

        acad_year_form = SelectAcademicYearForm(request.POST)
        if (acad_year_form.is_valid()):
            academic_year_requested = acad_year_form.cleaned_data["select_academic_year"]
            #Store info in the session
            request.session['acad_year_requested'] =  academic_year_requested.start_year

        #Trigger a GET
        return HttpResponseRedirect(reverse('workload_app:department',  kwargs={'department_id': department_id}))

    else: #GET request
        
        start_year=0 #It simply won't find anything with this year
        if ('acad_year_requested' in request.session.keys()): 
            start_year = request.session['acad_year_requested']
        
        #The table with all the programmes offered by the Department
        dept_obj = Department.objects.filter(id = department_id).get()
        dept_name = dept_obj.department_name
        prog_form = ProgrammeOfferedForm(initial={'fresh_record': True})
        sub_prog_form = SubProgrammeOfferedForm(department_id = dept_obj.id,initial={'fresh_record': True})
        prog_offered = []
        for prg in ProgrammeOffered.objects.filter(primary_dept=department_id):
            item = {
                "programme_name" : prg.programme_name,
                "programme_id" : prg.id,
                "programme_edit_form" : ProgrammeOfferedForm(initial = {'fresh_record' : False, \
                                                                        'prog_id' : prg.id, 
                                                                        'dept_id' : department_id,\
                                                                        'programme_name' : prg.programme_name,
                                                                        'primary_dept' : department_id}),
                "sub_programmes" : [],
                "n_subprogrammes_rowspan" : 0,#used for rowspan
                "n_subprogrammes" : 0
            }
            
            for sub_prg in SubProgrammeOffered.objects.filter(main_programme=prg):
                item["sub_programmes"].append(sub_prg.sub_programme_name)
            
            item["n_subprogrammes_rowspan"] = max(1,len(item["sub_programmes"])) #IF no subprogrammes, we have one here (used as colspan)
            item["n_subprogrammes"] = len(item["sub_programmes"])
            prog_offered.append(item)
        
        wl_form = ScenarioForm(initial = {'dept' : department_id, 'fresh_record' : True})
        #Here we are in the Dept page, so we assume the new workload will be created for this dept only and we hide the choice
        wl_form.fields['dept'].widget = forms.HiddenInput()

        remove_prog_form = RemoveProgrammeForm(department_id = department_id)
        remove_sub_prog_form = RemoveSubProgrammeForm(department_id = department_id)
        remove_wl_scenario_form = RemoveScenarioForm(dept_id=department_id)
        #Table with all the workloads for this Department
        dept_wls = []
        this_year = datetime.datetime.now().year
        for start_year_dept in range(this_year-6,this_year+5):
            item = {
                "academic_year" : str(start_year_dept)+'/'+str(start_year_dept+1),
                "official_wl_ids" : [],
                "draft_wl_ids" : [],
            }
            for wl in WorkloadScenario.objects.filter(dept = department_id).filter(academic_year__start_year = start_year_dept):
                if (wl.status==WorkloadScenario.OFFICIAL):
                    item["official_wl_ids"].append(wl.id)
                else:
                    item["draft_wl_ids"].append(wl.id)
            dept_wls.append(item)

        mod_type_form = ModuleTypeForm()
        remove_mod_type_form = RemoveModuleTypeForm(department_id=department_id)
        module_type_table = CalculateModuleTypeTable(department_id)  

        #Generate the report for the year
        if (start_year == 0 ):
            acad_year_form = SelectAcademicYearForm()
        else:
            acad_year_form = SelectAcademicYearForm(initial={'select_academic_year' : Academicyear.objects.filter(start_year = start_year).get().id})

        scen_qs = WorkloadScenario.objects.filter(dept = department_id).filter(status=WorkloadScenario.OFFICIAL).filter(academic_year__start_year = start_year)
        scenario_id = ''
        academic_year = ''
        tables_for_year=[]
        workload_there=False
        no_show_message = "" #This is the message to be displayed if there are no tables to be shown for one reason or another.
        if (scen_qs.count()==1):         
            workload_there=True
            scen  = scen_qs.get()
            scenario_id = scen.id
            academic_year = scen.academic_year.__str__()
            something_to_show = False
            index = 0
            for prg in ProgrammeOffered.objects.filter(primary_dept=department_id):
                hourly_table = CalculateModuleHourlyTableForProgramme(scen.id, prg.id, requested_table_type.PROGRAMME)
                if(hourly_table["mods_present"] > 0):
                    tables_for_prog = {
                        "prog_id" : prg.id,
                        "table_with_hours" : '',
                        "table_with_mod_types" : '',
                        "hourly_tables_with_subprogrammes" : [],
                        "colour_scheme" : COLOUR_SCHEMES[index%len(COLOUR_SCHEMES)]
                    }
                    index = index + 1
                    tables_for_prog["table_with_hours"] = hourly_table
                    tables_for_prog["table_with_mod_types"] = CalculateModuleTypesTableForProgramme(scen.id,prg.id)
                    
                    for sub_prg in SubProgrammeOffered.objects.filter(main_programme = prg):
                        sub_prg_table = CalculateModuleHourlyTableForProgramme(scen.id, sub_prg.id, requested_table_type.SUB_PROGRAMME)
                        tables_for_prog["hourly_tables_with_subprogrammes"].append(sub_prg_table)

                    tables_for_year.append(tables_for_prog)
                    something_to_show = True
            if (something_to_show == False): no_show_message = "Note: the modules in the workload requested are not associated with any programme"

        if (workload_there == False): no_show_message = "No official workload is in the system database for the requested year"
        if start_year == 0 : no_show_message = ""#Reset if there is requested year in the session (e.g., first landing) 

        template = loader.get_template('workload_app/department.html')
        context = {
            'workload_there' : workload_there, #whetehre or not an official workload was even found for the requested year
            'workload_id' : scenario_id,
            'acad_year' : academic_year,
            'dept_id' : department_id,
            'dept_name' : dept_name,
            'acad_year_form' : acad_year_form,
            'prog_offered' : prog_offered, #This is a list of dictionary items
            'dept_wls' : dept_wls,#This is the table with workloads from recent years
            'module_type_table' : module_type_table,
            'mod_type_form': mod_type_form,
            'remove_mod_type_form':remove_mod_type_form.as_p(),
            'wl_form' : wl_form,
            'remove_wl_scenario_form' : remove_wl_scenario_form,
            'prog_form' : prog_form,
            'sub_prog_form' : sub_prog_form,
            'remove_prog_form' : remove_prog_form,
            'remove_sub_prog_form' : remove_sub_prog_form,
            'tables_for_year' : tables_for_year,
            'no_show_message' : no_show_message,
            'user_menu' : user_menu,
            'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))

def module(request, module_code):
    user_menu  = DetermineUserMenu(request.user.id,request.user.is_superuser)
    user_homepage = DetermineUserHomePage(request.user.id,request.user.is_superuser)
    if request.user.is_authenticated == False or CanUserAdminThisModule(request.user.id,module_code  = module_code, is_super_user = request.user.is_superuser)==False:
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "Access forbidden. User has no access to this page",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))
    
    #Figure out the programme(s) this module may belong to
    all_prog_ids = [None,None,None]#3 because we support up to 3 proghrammes for now
    all_prog_names = [None,None,None]
    for mod in Module.objects.filter(module_code=module_code):
        if (mod.primary_programme is not None):
            all_prog_ids[0] = mod.primary_programme.id
            all_prog_names[0] = mod.primary_programme.programme_name
        if (mod.secondary_programme is not None):
            all_prog_ids[1] = mod.secondary_programme.id
            all_prog_names[1] = mod.secondary_programme.programme_name
        if (mod.tertiary_programme is not None):
            all_prog_ids[2] = mod.tertiary_programme.id
            all_prog_names = mod.tertiary_programme.programme_name
    #Determine primary programme ID or- if None - the highest level programme ID
    for i in range(0,len(all_prog_ids)):
        if (all_prog_ids[i] is not None):
            primary_prog  = ProgrammeOffered.objects.filter(id = all_prog_ids[i]).get()
            primary_programme_id = all_prog_ids[i]
            break #exit at the first. Note we put primary, secondary and tertiary in order at loop above

    if request.method =='POST':
        mlo_form = MLOForm(request.POST)
        if (mlo_form.is_valid()):
            mlo_text = mlo_form.cleaned_data["mlo_description"]
            mlo_short_text = mlo_form.cleaned_data["mlo_short_description"]
            mlo_valid_from = mlo_form.cleaned_data["mlo_valid_from"]
            mlo_valid_to = mlo_form.cleaned_data["mlo_valid_to"]
            if (mlo_form.cleaned_data['fresh_record'] == True):
                new_mlo = ModuleLearningOutcome.objects.create(mlo_description = mlo_text,mlo_short_description= mlo_short_text,module_code = module_code,\
                                mlo_valid_from=mlo_valid_from, mlo_valid_to=mlo_valid_to)
                new_mlo.save()
            else: #This is an edit
                mlo_id = mlo_form.cleaned_data['mlo_id']
                ModuleLearningOutcome.objects.filter(id = int(mlo_id)).update(mlo_description = mlo_text,\
                            mlo_short_description = mlo_short_text,\
                            mlo_valid_from=mlo_valid_from, mlo_valid_to=mlo_valid_to)
        
        remove_mlo_form = RemoveMLOForm(request.POST, module_code = module_code)
        if (remove_mlo_form.is_valid() == True):
            ModuleLearningOutcome.objects.filter(id=request.POST.get('select_mlo_to_remove')).delete()

        mlo_survey_form = AddMLOSurveyForm(request.POST, request.FILES, module_code = module_code)
        if (mlo_survey_form.is_valid()):
            survey_name = mlo_survey_form.cleaned_data['survey_title']
            start_date = mlo_survey_form.cleaned_data['start_date']
            end_date = mlo_survey_form.cleaned_data['end_date']
            n_invited = mlo_survey_form.cleaned_data['totoal_N_recipients']
            supplied_cohort_targeted = mlo_survey_form.cleaned_data['cohort_targeted']
            comments = mlo_survey_form.cleaned_data['comments']
                        
            #Point of creation of MLO survey. We look at the programme's policy to determine the survey labels
            #Such policy will follow the primary programme
            #Note: the line below will take care of creating defaults, if needed
            likert_scale = DetermineSurveyLabelsForProgramme(primary_programme_id)["mlo_survey_labels_object"]
            #first we create a survey object
            new_survey = Survey.objects.create(survey_title = survey_name, opening_date = start_date, closing_date = end_date,\
                                               cohort_targeted = supplied_cohort_targeted,\
                                               likert_labels = likert_scale,\
                                               max_respondents = n_invited, comments = comments,\
                                               survey_type = Survey.SurveyType.MLO,\
                                               programme_associated = primary_prog)
            new_survey.save()

        
        remove_mlo_survey_form = RemoveMLOSurveyForm(request.POST, module_code = module_code)
        if (remove_mlo_survey_form.is_valid()):
            #Note the "cascade" policy will delete the responses as well.
            Survey.objects.filter(id=request.POST.get('select_MLO_survey_to_remove')).delete()

        mlo_performance_form = MLOPerformanceMeasureForm(request.POST, request.FILES, module_code = module_code)
        if (mlo_performance_form.is_valid()):
            supplied_desc = mlo_performance_form.cleaned_data["measure_description"]
            supplied_acad_year = mlo_performance_form.cleaned_data['academic_year']
            supplied_mlo = mlo_performance_form.cleaned_data['mlo_mapped_1']
            supplied_secondary_mlo = mlo_performance_form.cleaned_data['mlo_mapped_2']
            supplied_tertiary_mlo = mlo_performance_form.cleaned_data['mlo_mapped_3']
            supplied_score = mlo_performance_form.cleaned_data['percentage_score']
            file_obj = None
            if ("original_file" in request.FILES):#original_raw_file is the field in the form!
                file_obj = request.FILES["original_file"]
                
            new_measure = MLOPerformanceMeasure.objects.create(description = supplied_desc,\
                                                               academic_year = supplied_acad_year,\
                                                                associated_mlo = supplied_mlo,\
                                                                secondary_associated_mlo = supplied_secondary_mlo,\
                                                                tertiary_associated_mlo = supplied_tertiary_mlo,\
                                                                percentage_score = supplied_score,
                                                                original_file = file_obj)
            new_measure.save()

        remove_mlo_measure_form = RemoveMLOPerformanceMeasureForm(request.POST, module_code = module_code)
        if (remove_mlo_measure_form.is_valid()):
            MLOPerformanceMeasure.objects.filter(id=request.POST.get('Select_MLO_measure_to_remove')).delete()


        for prog_id in all_prog_ids:
            if (prog_id is not None):
                    mlo_slo_mapping_form = MLOSLOMappingForm(request.POST, prog_id=prog_id)
                    if mlo_slo_mapping_form.is_valid():
                        supplied_slo_id = mlo_slo_mapping_form.cleaned_data["slo_id"]
                        if StudentLearningOutcome.objects.filter(programme__id = prog_id).filter(id=supplied_slo_id).count()>0:
                            for slo in StudentLearningOutcome.objects.filter(programme__id = prog_id):
                                supplied_strength = mlo_slo_mapping_form.cleaned_data ["mlo_slo_mapping_strength"+str(slo.id)]
                                supplied_mlo_id = mlo_slo_mapping_form.cleaned_data["mlo_id_for_slo_mapping"]
                                MLOSLOMapping.objects.filter(slo__id=slo.id).filter(mlo__id=supplied_mlo_id).update(strength = supplied_strength)

        corr_action_form = CorrectiveActionForm(request.POST, module_code=module_code)
        if(corr_action_form.is_valid()):
            supplied_corr_desc = corr_action_form.cleaned_data['description']
            supplied_implementation_acad_year = corr_action_form.cleaned_data['implementation_acad_year']
            supplied_observed_results = corr_action_form.cleaned_data['observed_results']
            if (corr_action_form.cleaned_data['fresh_record'] == True):
                new_act = CorrectiveAction.objects.create(description = supplied_corr_desc,implementation_acad_year= supplied_implementation_acad_year,module_code = module_code,\
                                observed_results=supplied_observed_results)
                new_act.save()
            else: #This is an edit
                act_id = corr_action_form.cleaned_data['action_id']
                CorrectiveAction.objects.filter(id = act_id).update(description = supplied_corr_desc,implementation_acad_year= supplied_implementation_acad_year,module_code = module_code,\
                                observed_results=supplied_observed_results)
        
        remove_corective_action_form = RemoveCorrectiveActionForm(request.POST, module_code = module_code)
        if (remove_corective_action_form.is_valid()):
            CorrectiveAction.objects.filter(id=request.POST.get('select_action_to_remove')).delete()

        return HttpResponseRedirect(reverse('workload_app:module', kwargs={'module_code' : module_code}));#Trigger a get
    else:#This is a get
        module_name_qs = Module.objects.filter(module_code = module_code)
        if (module_name_qs.count() < 1):
            #This should really never happen, but just in case the user enters some random number...
            template = loader.get_template('workload_app/errors_page.html')
            context = {
                'error_message': "There are no modules with the " + module_code + " code in the database.",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
            }
            return HttpResponse(template.render(context, request))
        
        module_name = module_name_qs.first().module_title
        module_table = CalculateSingleModuleInformationTable(module_name_qs.first().module_code)
        new_mlo_form = MLOForm(initial = {'mod_code' : module_code, 'fresh_record' : True})
        remove_mlo_form = RemoveMLOForm(module_code = module_code)
        all_mlo_slo_tables = []#One item per programme
        for prog_id in all_prog_ids:
            if (prog_id is not None):
                table_item = {
                    "slo_list" : None,
                    "mlo_list" : None
                }
                mlo_list = []#List of dictionaries
                for mlo in ModuleLearningOutcome.objects.filter(module_code=module_code):
                    mlo_edit_form = MLOForm(initial = {'fresh_rescord' : False, 'mlo_id' : mlo.id,\
                                                        'mlo_description' : mlo.mlo_description,\
                                                        'mlo_short_description' : mlo.mlo_short_description,\
                                                        'mlo_valid_from': mlo.mlo_valid_from,\
                                                        'mlo_valid_to'  :mlo.mlo_valid_to})
                    mlo_item = {
                        'mlo_desc' : mlo.mlo_description,
                        'mlo_short_desc' : mlo.mlo_short_description,
                        'mlo_edit_form' : mlo_edit_form,
                        'mlo_validity' : DisplayOutcomeValidity(mlo.id, accreditation_outcome_type.MLO),
                        'mlo_id' : mlo.id,
                        'slo_mapping' : [],
                        'slo_mapping_form' : None
                    }

                    mlo_item["slo_mapping_form"] = MLOSLOMappingForm(prog_id = prog_id, initial = {"mlo_id_for_slo_mapping" : mlo.id} )
                    for slo in StudentLearningOutcome.objects.filter(programme__id = prog_id):
                        strength = 0
                        mapping_qs = MLOSLOMapping.objects.filter(slo__id=slo.id).filter(mlo__id=mlo.id)
                        if (mapping_qs.count()==1):# if it is there...
                            strength = mapping_qs.get().strength
                        if (mapping_qs.count()==0):#Not there, we create
                            MLOSLOMapping.objects.create(slo=slo,mlo=mlo,strength=strength)
            
                        icon = DetermineIconBasedOnStrength(strength)
                        slo_mapping_item = {
                            'slo_description' : slo.slo_description,
                            'slo_short_description' : slo.slo_short_description,
                            'slo_letter' : slo.letter_associated,
                            'mapping_strength' : strength,
                            'mapping_icon' : icon
                        }
                        mlo_item["slo_mapping"].append(slo_mapping_item)
                        mlo_item["slo_mapping_form"]["mlo_slo_mapping_strength"+str(slo.id)].initial = strength
                    mlo_list.append(mlo_item)
                #Since the slo list is contained in all MLO items, we extract one, if any, for easy display in the table
                slo_list = []
                for item in mlo_list:
                    slo_list = item["slo_mapping"]
                    break #Only once needed to extract the list, if any
                table_item["slo_list"] = slo_list
                table_item["mlo_list"] = mlo_list
                table_item["programme_name"] = ProgrammeOffered.objects.filter(id = prog_id).get().programme_name
                table_item["programme_id"] = prog_id
                all_mlo_slo_tables.append(table_item)
        
        ####
        # MLO survey forms
        mlo_survey_form = AddMLOSurveyForm(module_code = module_code)
        #The one for removing
        remove_mlo_survey_form = RemoveMLOSurveyForm(module_code = module_code)
        ############

        #########################
        #MLOs survey list
        #########################
        #Find all surveys
        surveys_ids = []
        for mlo in ModuleLearningOutcome.objects.filter(module_code = module_code):
            for response in SurveyQuestionResponse.objects.filter(associated_mlo=mlo):     
                surveys_ids.append(response.parent_survey.id)
                
        #Remove duplicates
        surveys_ids = list(dict.fromkeys(surveys_ids))
        
        #Prepare table structure
        survey_table = []
        for survey_id in surveys_ids:
            srv_details = CalculateSurveyDetails(survey_id)
            table_row_item = {
                'survey_name' : srv_details["title"],
                'survey_comments' : srv_details["comments"],
                'survey_start_date' : srv_details["start_date"],
                'survey_end_date' :srv_details["end_date"],
                'original_file_url' : srv_details["file"],
                'n_respondents' : srv_details["recipients"],
                'average_response_rate' : srv_details["average_response_rate"],
                'survey_id' : survey_id
            }
            survey_table.append(table_row_item)
        #########################

        #########################
        #MLOs direct measures
        #########################
        mlo_performance_measure_form = MLOPerformanceMeasureForm(module_code=module_code)
        remove_mlo_perfroamnce_measure_form  = RemoveMLOPerformanceMeasureForm(module_code = module_code)

        mlo_measure_table = []
        for measure in MLOPerformanceMeasure.objects.filter(associated_mlo__module_code = module_code):
            mlo_measure_table_row = {
                'year' : measure.academic_year,
                'description' : measure.description,
                'download_url' : '',
                'mlos_mapped' : measure.associated_mlo.mlo_short_description + ", ",#Will be culled at the end
                'score' : measure.percentage_score
            }
            for secondary_map in MLOPerformanceMeasure.objects.filter(description = measure.description).filter(secondary_associated_mlo__module_code = module_code):
                mlo_measure_table_row["mlos_mapped"] += secondary_map.secondary_associated_mlo.mlo_short_description + ", "
            for tertiary_map in MLOPerformanceMeasure.objects.filter(description = measure.description).filter(tertiary_associated_mlo__module_code = module_code):
                mlo_measure_table_row["mlos_mapped"] += tertiary_map.tertiary_associated_mlo.mlo_short_description + ", "
            
            #remove the the last two chracters(", " or just "  ")
            mlo_measure_table_row["mlos_mapped"] = mlo_measure_table_row["mlos_mapped"][:-2]
            mlo_measure_table.append(mlo_measure_table_row)
            if (len(measure.original_file.name) > 0):
                mlo_measure_table_row["download_url"] = measure.original_file.url
        
        #############################
        # Corrective actions
        ################################
        new_corrective_action_form = CorrectiveActionForm(module_code=module_code, initial = {'module_code' : module_code,'fresh_record' : True})
        remove_correctiove_action_form = RemoveCorrectiveActionForm(module_code=module_code)
        corrective_action_table = []
        for action in CorrectiveAction.objects.filter(module_code=module_code):
            corr_action_table_row = {
                'description' : action.description,
                'year' : action.implementation_acad_year,
                'results' : action.observed_results,
                'action_id' : action.id,
                'corr_act_edit_form' : CorrectiveActionForm(module_code=module_code, initial = {'fresh_rescord' : False,\
                                                'description' : action.description,\
                                                'implementation_acad_year' : action.implementation_acad_year,\
                                                'observed_results': action.observed_results,\
                                                'action_id'  :action.id})}
            corrective_action_table.append(corr_action_table_row)

        #Determine the primary department this module is on. We take as the dept of the first workload this module appears in
        dept_id = ''
        dept_name = ''
        for mod in Module.objects.filter(module_code = module_code):
            dept_id  = mod.scenario_ref.dept.id
            dept_name  = mod.scenario_ref.dept.department_acronym
            break
        
        #Store info module code the session
        request.session['module_code'] =  module_code

        template = loader.get_template('workload_app/module.html')
        context = {
                    'module_title' : module_name,
                    'module_code' : module_code,
                    'module_table' : module_table,
                    'new_mlo_form' : new_mlo_form,
                    'remove_mlo_form' : remove_mlo_form,
                    'all_mlo_slo_tables' : all_mlo_slo_tables,
                    #'mlo_list' : mlo_list,
                    #'slo_list' : slo_list,
                    'mlo_survey_table' : survey_table,
                    'mlo_survey_form' : mlo_survey_form,
                    'remove_mlo_survey_form' : remove_mlo_survey_form,
                    'mlo_performance_measure_form' : mlo_performance_measure_form,
                    'remove_mlo_perfroamnce_measure_form' : remove_mlo_perfroamnce_measure_form,
                    'mlo_measure_table' : mlo_measure_table,
                    'corrective_action_table' : corrective_action_table,
                    'corrective_action_form' : new_corrective_action_form,
                    'remove_corrective_action_form' : remove_correctiove_action_form,
                    'department_id' : dept_id,
                    'department_name' : dept_name,
                    'user_menu' : user_menu,
                    'user_homepage' : user_homepage
                    }
        return HttpResponse(template.render(context, request))

def accreditation(request,programme_id):
    
    user_menu  = DetermineUserMenu(request.user.id,request.user.is_superuser)
    user_homepage = DetermineUserHomePage(request.user.id,request.user.is_superuser)
    if (ProgrammeOffered.objects.filter(id = programme_id).count() <1):
        #This should really never happen, but just in case the user enters some random number...
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "No such programme exists in the database",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))


    programme = ProgrammeOffered.objects.filter(id = programme_id).get()
    department_id = programme.primary_dept.id
    if request.user.is_authenticated == False or CanUserAdminThisDepartment(request.user.id,department_id, is_super_user = request.user.is_superuser)==False:
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "Access forbidden. User has no access to this page",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))
    
    if request.method =='POST':
        slo_form = SLOForm(request.POST)
        if (slo_form.is_valid()):
            slo_text = slo_form.cleaned_data["slo_description"]
            slo_short_text = slo_form.cleaned_data["slo_short_description"]
            default_or_not = slo_form.cleaned_data["is_default_by_accreditor"]
            letter = slo_form.cleaned_data["letter_associated"]
            academic_year_start = slo_form.cleaned_data['cohort_valid_from']
            academic_year_end = slo_form.cleaned_data['cohort_valid_to']
            if (slo_form.cleaned_data['fresh_record'] == True):
                new_slo = StudentLearningOutcome.objects.create(slo_description = slo_text,\
                                                                slo_short_description = slo_short_text,\
                                                                is_default_by_accreditor = default_or_not,
                                                                letter_associated = letter,
                                                                cohort_valid_from = academic_year_start,
                                                                cohort_valid_to = academic_year_end,
                                                                programme = programme)
                new_slo.save()
            else: #edit
                slo_id = slo_form.cleaned_data['slo_id']
                StudentLearningOutcome.objects.filter(id = int(slo_id)).update(slo_description = slo_text,\
                           slo_short_description = slo_short_text,\
                           is_default_by_accreditor = default_or_not,
                           letter_associated = letter,
                           cohort_valid_from = academic_year_start,
                           cohort_valid_to = academic_year_end,
                           programme = programme)
                

        remove_slo_form = RemoveSLOForm(request.POST, programme_id = programme_id)
        if (remove_slo_form.is_valid()):
            StudentLearningOutcome.objects.filter(id=request.POST.get('select_slo_to_remove')).delete()
        
        slo_survey_form = AddSLOSurveyForm(request.POST,request.FILES)
        peo_survey_form = AddPEOSurveyForm(request.POST,request.FILES)

        is_slo_survey = False
        is_peo_survey=False
        if (slo_survey_form.is_valid()): is_slo_survey = True
        if (peo_survey_form.is_valid()): is_peo_survey = True
        if (is_slo_survey or is_peo_survey):
            
            supplied_opening_date = slo_survey_form.cleaned_data["start_date"]
            supplied_closing_date = slo_survey_form.cleaned_data["end_date"]
            supplied_targeted_cohort = slo_survey_form.cleaned_data["cohort_targeted"]
            supplied_max_respondents = slo_survey_form.cleaned_data["totoal_N_recipients"]
            supplied_comments = slo_survey_form.cleaned_data["comments"]
            
            survey_type = Survey.SurveyType.UNDEFINED
            #We will set this according the policy stored in the programme because this is point of creation of survey object
            #The line below also takes care of creating default ones if not present
            likert_labels_struct = DetermineSurveyLabelsForProgramme(programme_id) 
            if (is_slo_survey): 
                supplied_survey_title = slo_survey_form.cleaned_data["slo_survey_title"]
                survey_type = Survey.SurveyType.SLO
                likert_labels = likert_labels_struct["slo_survey_labels_object"]
            if (is_peo_survey): 
                supplied_survey_title = peo_survey_form.cleaned_data["peo_survey_title"]
                survey_type = Survey.SurveyType.PEO
                likert_labels = likert_labels_struct["peo_survey_labels_object"]
            
            #Crate the survey object
            new_survey = Survey.objects.create(survey_title = supplied_survey_title,\
                                               opening_date = supplied_opening_date, closing_date = supplied_closing_date,\
                                               cohort_targeted = supplied_targeted_cohort,\
                                               likert_labels = likert_labels,\
                                               survey_type = survey_type,\
                                               max_respondents =  supplied_max_respondents, comments = supplied_comments,\
                                               programme_associated = programme)
            new_survey.save()

            
        remove_SLO_survey_form = RemoveSLOSurveyForm(request.POST,  programme_id = programme_id)
        if (remove_SLO_survey_form.is_valid()):
            #Note the "cascade" policy will delete the responses as well.
            Survey.objects.filter(id=request.POST.get('select_SLO_survey_to_remove')).delete()

        remove_PEO_survey_form = RemovePEOSurveyForm(request.POST,  programme_id = programme_id)
        if (remove_PEO_survey_form.is_valid()):
            #Note the "cascade" policy will delete the responses as well.
            Survey.objects.filter(id=request.POST.get('select_PEO_survey_to_remove')).delete()

        peo_form = PEOForm(request.POST)
        if peo_form.is_valid():
            peo_text = peo_form.cleaned_data["peo_description"]
            peo_short_text = peo_form.cleaned_data["peo_short_description"]
            letter = peo_form.cleaned_data["letter_associated"]
            supplied_acad_year_start = peo_form.cleaned_data['peo_cohort_valid_from']
            supplied_acad_year_to = peo_form.cleaned_data['peo_cohort_valid_to']
            if (peo_form.cleaned_data['fresh_record'] == True):
                new_peo = ProgrammeEducationalObjective.objects.create(peo_description = peo_text,\
                                                                peo_short_description = peo_short_text,\
                                                                letter_associated = letter,
                                                                peo_cohort_valid_from = supplied_acad_year_start,
                                                                peo_cohort_valid_to = supplied_acad_year_to,
                                                                programme = programme)
                new_peo.save()
            else: #edit
                peo_id = peo_form.cleaned_data['peo_id']
                ProgrammeEducationalObjective.objects.filter(id = int(peo_id)).update(peo_description = peo_text,\
                           peo_short_description = peo_short_text,\
                           letter_associated = letter,\
                           peo_cohort_valid_from = supplied_acad_year_start,\
                           peo_cohort_valid_to = supplied_acad_year_to,\
                           programme = programme)
        
        remove_peo_form = RemovePEOForm(request.POST, programme_id = programme_id)
        if (remove_peo_form.is_valid()):
            ProgrammeEducationalObjective.objects.filter(id=request.POST.get('select_peo_to_remove')).delete()
            
        peo_slo_mapping_form = PEOSLOMappingForm(request.POST, prog_id=programme_id)
        if peo_slo_mapping_form.is_valid():
            for peo in ProgrammeEducationalObjective.objects.filter(programme__id = programme_id):
                supplied_strength = peo_slo_mapping_form.cleaned_data ["mapping_strength"+str(peo.id)]
                supplied_slo_id = peo_slo_mapping_form.cleaned_data["slo_id"]
                PEOSLOMapping.objects.filter(slo__id=supplied_slo_id).filter(peo__id=peo.id).update(strength = supplied_strength)
        
        select_report_years_form  =SelectAccreditationReportForm(request.POST)
        if select_report_years_form.is_valid():
            start  = select_report_years_form.cleaned_data["academic_year_start"].start_year
            end  = select_report_years_form.cleaned_data["academic_year_end"].start_year
            compulsory_only = select_report_years_form.cleaned_data["only_core"]
            return HttpResponseRedirect(reverse('workload_app:accreditation_report', 
            kwargs={'programme_id' : programme_id, 'start_year' : start, 'end_year': end,'compulsory_only': compulsory_only}));#Trigger a re-direct to full report page


        edit_survey_label_form = EditSurveySettingsForm(request.POST)
        if (edit_survey_label_form.is_valid()):
            type_of_label = edit_survey_label_form.cleaned_data['type']
            high_1_label = edit_survey_label_form.cleaned_data["highest_score_label"]
            high_2_label = edit_survey_label_form.cleaned_data["second_highest_score_label"]
            high_3_label = edit_survey_label_form.cleaned_data["third_highest_score_label"]
            high_4_label = edit_survey_label_form.cleaned_data["fourth_highest_score_label"]
            high_5_label = edit_survey_label_form.cleaned_data["fifth_highest_score_label"]
            high_6_label = edit_survey_label_form.cleaned_data["sixth_highest_score_label"]
            high_7_label = edit_survey_label_form.cleaned_data["seventh_highest_score_label"]
            high_8_label = edit_survey_label_form.cleaned_data["eighth_highest_score_label"]
            high_9_label = edit_survey_label_form.cleaned_data["ninth_highest_score_label"]
            high_10_label = edit_survey_label_form.cleaned_data["tenth_score_label"]
            prog = ProgrammeOffered.objects.filter(id=programme_id).get()
            if (type_of_label == Survey.SurveyType.SLO):
                prog.slo_survey_labels.highest_score_label = high_1_label
                prog.slo_survey_labels.second_highest_score_label = high_2_label
                prog.slo_survey_labels.third_highest_score_label = high_3_label
                prog.slo_survey_labels.fourth_highest_score_label = high_4_label
                prog.slo_survey_labels.fifth_highest_score_label = high_5_label
                prog.slo_survey_labels.sixth_highest_score_label = high_6_label
                prog.slo_survey_labels.seventh_highest_score_label = high_7_label
                prog.slo_survey_labels.eighth_highest_score_label = high_8_label
                prog.slo_survey_labels.ninth_highest_score_label = high_9_label
                prog.slo_survey_labels.tenth_score_label = high_10_label
                prog.slo_survey_labels.save()
            if (type_of_label == Survey.SurveyType.PEO):
                prog.peo_survey_labels.highest_score_label = high_1_label
                prog.peo_survey_labels.second_highest_score_label = high_2_label
                prog.peo_survey_labels.third_highest_score_label = high_3_label
                prog.peo_survey_labels.fourth_highest_score_label = high_4_label
                prog.peo_survey_labels.fifth_highest_score_label = high_5_label
                prog.peo_survey_labels.sixth_highest_score_label = high_6_label
                prog.peo_survey_labels.seventh_highest_score_label = high_7_label
                prog.peo_survey_labels.eighth_highest_score_label = high_8_label
                prog.peo_survey_labels.ninth_highest_score_label = high_9_label
                prog.peo_survey_labels.tenth_score_label = high_10_label
                prog.peo_survey_labels.save()               
            if (type_of_label == Survey.SurveyType.MLO):
                prog.mlo_survey_labels.highest_score_label = high_1_label
                prog.mlo_survey_labels.second_highest_score_label = high_2_label
                prog.mlo_survey_labels.third_highest_score_label = high_3_label
                prog.mlo_survey_labels.fourth_highest_score_label = high_4_label
                prog.mlo_survey_labels.fifth_highest_score_label = high_5_label
                prog.mlo_survey_labels.sixth_highest_score_label = high_6_label
                prog.mlo_survey_labels.seventh_highest_score_label = high_7_label
                prog.mlo_survey_labels.eighth_highest_score_label = high_8_label
                prog.mlo_survey_labels.ninth_highest_score_label = high_9_label
                prog.mlo_survey_labels.tenth_score_label = high_10_label
                prog.mlo_survey_labels.save()                  
        return HttpResponseRedirect(reverse('workload_app:accreditation', kwargs={'programme_id' : programme_id}));#Trigger a get
        
    else:#GET
        
        new_slo_form = SLOForm(initial = {'fresh_record' : True})
        new_peo_form = PEOForm(initial = {'fresh_record' : True})
        
        remove_slo_form = RemoveSLOForm(programme_id = programme_id)
        remove_peo_form = RemovePEOForm(programme_id = programme_id)
        
        new_slo_survey_form = AddSLOSurveyForm()
        new_peo_survey_form = AddPEOSurveyForm()

        remove_slo_survey_form  = RemoveSLOSurveyForm(programme_id = programme_id)
        remove_peo_survey_form  = RemovePEOSurveyForm(programme_id = programme_id)

        select_report_years_form  =SelectAccreditationReportForm()

        peo_list = []#List of dictionaries - table of peos
        for peo in ProgrammeEducationalObjective.objects.filter(programme__id = programme_id):
            peo_edit_form = PEOForm(initial = {'fresh_rescord' : False, 'peo_id' : peo.id,\
                                                'peo_description' : peo.peo_description,\
                                                'peo_short_description' : peo.peo_short_description,\
                                                'letter_associated' : peo.letter_associated,\
                                                'peo_cohort_valid_from' : peo.peo_cohort_valid_from,\
                                                'peo_cohort_valid_to': peo.peo_cohort_valid_to })
            peo_item = {
                'peo_desc' : peo.peo_description,
                'peo_short_desc' : peo.peo_short_description,
                'peo_letter' : peo.letter_associated,
                'peo_validity' : DisplayOutcomeValidity(peo.id,accreditation_outcome_type.PEO),
                'peo_edit_form' : peo_edit_form,
                'peo_id' : peo.id
            }
            peo_list.append(peo_item)

        slo_list = [] #list of dictionaries -  table of slos and mappings
        for slo in StudentLearningOutcome.objects.filter(programme__id = programme_id):
            edit_form = SLOForm(initial = {'fresh_record' : False, 'slo_id': slo.id, \
                                            'slo_description' : slo.slo_description,\
                                            'slo_short_description' : slo.slo_short_description,\
                                            'is_default_by_accreditor' : slo.is_default_by_accreditor,\
                                            'letter_associated' : slo.letter_associated,\
                                            'cohort_valid_from' : slo.cohort_valid_from,\
                                            'cohort_valid_to': slo.cohort_valid_to})
            slo_item = {
                'slo_desc' : slo.slo_description,
                'slo_short_desc' : slo.slo_short_description,
                'slo_letter' : slo.letter_associated,
                'slo_edit_form' : edit_form,
                'slo_validity' : DisplayOutcomeValidity(slo.id,accreditation_outcome_type.SLO),
                'slo_id' : slo.id,
                'slo_mapping_form' : PEOSLOMappingForm(prog_id=programme_id),
                'peo_mapping' : []
            }
            #Set the SLO in the form
            slo_item["slo_mapping_form"]["slo_id"].initial = slo.id
            for peo in ProgrammeEducationalObjective.objects.filter(programme__id = programme_id):
                strength = 0
                mapping_qs = PEOSLOMapping.objects.filter(slo__id=slo.id).filter(peo__id=peo.id)
                if (mapping_qs.count()==1):# if it is there...
                    strength = mapping_qs.get().strength
                else:#otherwise create it the object
                    PEOSLOMapping.objects.create(slo=slo, peo=peo,strength=strength)
                
                icon = 'circle.svg'
                if (strength == 1 or strength ==2) : icon = 'circle-half.svg'
                if (strength ==3) : icon = 'circle-fill.svg'
                peo_mapping_item = {
                    'peo_id' : peo.id,
                    'strength' : strength,
                    'mapping_icon' : icon
                }
                peo_mapping_item["strength"] = strength
                slo_item["peo_mapping"].append(peo_mapping_item)
                slo_item["slo_mapping_form"]["mapping_strength"+str(peo.id)].initial = strength
            
            slo_list.append(slo_item)

        #Table of slo and peo surveys
        slo_peo_survey_table = []
        for srv in Survey.objects.filter(programme_associated__id = programme_id).filter(survey_type = Survey.SurveyType.SLO) | \
                   Survey.objects.filter(programme_associated__id = programme_id).filter(survey_type = Survey.SurveyType.PEO):
            slo_peo_survey_table.append(CalculateSurveyDetails(srv.id))
        
        #Table for current programme settings
        survey_settings = DetermineSurveyLabelsForProgramme(programme_id)
        max_labels = max(len(survey_settings["slo_survey_labels"]), len(survey_settings["mlo_survey_labels"]),len(survey_settings["peo_survey_labels"]))
        peo_row = ['PEO survey labels']
        slo_row = ['SLO survey labels']
        mlo_row = ['MLO survey labels']
        for i in range(0,max_labels):
            peo_row.append(survey_settings["peo_survey_labels_object"].GetFullListOfLabels()[i])
            slo_row.append(survey_settings["slo_survey_labels_object"].GetFullListOfLabels()[i])
            mlo_row.append(survey_settings["mlo_survey_labels_object"].GetFullListOfLabels()[i])
        survey_settings_table = [peo_row,slo_row,mlo_row]

        exisitng_labels = DetermineSurveyLabelsForProgramme(programme_id)
        existing_peo_labels = exisitng_labels['peo_survey_labels_object'].GetFullListOfLabels() 
        edit_peo_settings_form = EditSurveySettingsForm(initial = {
                'type' : Survey.SurveyType.PEO,
                'highest_score_label' : existing_peo_labels[0],
                'second_highest_score_label' : existing_peo_labels[1],
                'third_highest_score_label' : existing_peo_labels[2],
                'fourth_highest_score_label' : existing_peo_labels[3],
                'fifth_highest_score_label' : existing_peo_labels[4],
                'sixth_highest_score_label' : existing_peo_labels[5],
                'seventh_highest_score_label' : existing_peo_labels[6],
                'eighth_highest_score_label' : existing_peo_labels[7],
                'ninth_highest_score_label' : existing_peo_labels[8],
                'tenth_score_label' : existing_peo_labels[9]
        })

        existing_slo_labels = exisitng_labels['slo_survey_labels_object'].GetFullListOfLabels() 
        edit_slo_settings_form = EditSurveySettingsForm(initial = {
                'type' : Survey.SurveyType.SLO,
                'highest_score_label' : existing_slo_labels[0],
                'second_highest_score_label' : existing_slo_labels[1],
                'third_highest_score_label' : existing_slo_labels[2],
                'fourth_highest_score_label' : existing_slo_labels[3],
                'fifth_highest_score_label' : existing_slo_labels[4],
                'sixth_highest_score_label' : existing_slo_labels[5],
                'seventh_highest_score_label' : existing_slo_labels[6],
                'eighth_highest_score_label' : existing_slo_labels[7],
                'ninth_highest_score_label' : existing_slo_labels[8],
                'tenth_score_label' : existing_slo_labels[9]
        })

        existing_mlo_labels = exisitng_labels['mlo_survey_labels_object'].GetFullListOfLabels() 
        edit_mlo_settings_form = EditSurveySettingsForm(initial = {
                'type' : Survey.SurveyType.MLO,
                'highest_score_label' : existing_mlo_labels[0],
                'second_highest_score_label' : existing_mlo_labels[1],
                'third_highest_score_label' : existing_mlo_labels[2],
                'fourth_highest_score_label' : existing_mlo_labels[3],
                'fifth_highest_score_label' : existing_mlo_labels[4],
                'sixth_highest_score_label' : existing_mlo_labels[5],
                'seventh_highest_score_label' : existing_mlo_labels[6],
                'eighth_highest_score_label' : existing_mlo_labels[7],
                'ninth_highest_score_label' : existing_mlo_labels[8],
                'tenth_score_label' : existing_mlo_labels[9]
        })
        
        template = loader.get_template('workload_app/accreditation.html')
        context = {
                'programme_id' : programme_id,
                'programme_name' : programme.programme_name,
                'department_id' : department_id,
                'slo_list' : slo_list,
                'new_slo_form' : new_slo_form,
                'remove_slo_form' : remove_slo_form,
                'new_slo_survey_form' : new_slo_survey_form,
                'new_peo_survey_form' : new_peo_survey_form, 
                'remove_slo_survey_form' : remove_slo_survey_form,
                'remove_peo_survey_form' : remove_peo_survey_form,
                'peo_list' : peo_list,
                'new_peo_form' : new_peo_form,
                'remove_peo_form' : remove_peo_form,
                'slo_survey_table' : slo_peo_survey_table,
                'select_report_years_form' : select_report_years_form,
                'survey_settings_table' : survey_settings_table,
                'colspan_for_survey_settings' : max_labels,
                'edit_peo_settings_form' : edit_peo_settings_form,
                'edit_slo_settings_form' : edit_slo_settings_form,
                'edit_mlo_settings_form' : edit_mlo_settings_form,
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))

def accreditation_report(request,programme_id, start_year,end_year,compulsory_only):
    user_menu  = DetermineUserMenu(request.user.id,request.user.is_superuser)
    user_homepage = DetermineUserHomePage(request.user.id,request.user.is_superuser)
    programme = ProgrammeOffered.objects.filter(id = programme_id).get()
    department_id = programme.primary_dept.id
    if request.user.is_authenticated == False or CanUserAdminThisDepartment(request.user.id,department_id, is_super_user = request.user.is_superuser)==False:
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "Access forbidden. User has no access to this page",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))
    
    if request.method == 'GET':
        #The overall MLO-SLO mapping (big table with full and half moons, one for the whole period)
        big_mlo_slo_table = CalculateTableForOverallSLOMapping(programme_id, start_year=start_year, end_year=end_year,compulsory_only=compulsory_only)
        attention_scores_table = CalculateAttentionScoresSummaryTable(programme_id,start_year=start_year, end_year=end_year,compulsory_only=compulsory_only)

        slo_measures = [] #A list with all SLO measures. As long as there are SLO in the programme
        slo_identifiers = []
        all_slo_data_for_plot = []
        all_slo_ids = []
        for slo in StudentLearningOutcome.objects.filter(programme__id = programme_id).order_by("letter_associated"):
            all_slo_info = CalculateAllInforAboutOneSLO(slo.id,start_year,end_year,compulsory_only=compulsory_only) 
            slo_survey_measures = all_slo_info["slo_surveys"] #A list of all the slo survey measures. This one is ready for HTML
            mlo_slo_survey_table_rows = all_slo_info["mlo_surveys_for_slo"]#A list of measurements for this SLO obtained via MLO survey
            mlo_direct_measures_table_rows = all_slo_info["mlo_direct_measures_for_slo"]
            mlo_slo_mapping_table_rows = all_slo_info["mlo_mapping_for_slo"] 
            
            slo_measures_data_plot = all_slo_info["slo_measures_plot_data"]
            years_for_tables = []
            for year in range(start_year, end_year+1):
                years_for_tables.append(year)
            slo_info = {
                'slo_id' : slo.id,
                'slo_desc' : slo.slo_short_description,
                'slo_full_description' : slo.slo_description,
                'slo_letter' : slo.letter_associated,
                'mlo_mappings' : mlo_slo_mapping_table_rows,
                'slo_surveys' : slo_survey_measures,
                'mlo_direct_measures' : mlo_direct_measures_table_rows,
                'colspan_param' : end_year - start_year + 2,
                'years_for_tables' : years_for_tables,
                'mlo_slo_survey_table_rows' : mlo_slo_survey_table_rows,
                'slo_measures_plot_data' : slo_measures_data_plot #unused here?
            }
            slo_measures.append(slo_info)
            slo_identifiers.append(slo.slo_short_description)
            all_slo_data_for_plot.append(slo_measures_data_plot)
            all_slo_ids.append(slo.id)
        

        #all_direct_data
        for row in attention_scores_table:
            row['zipped_direct'] = zip(row['attention_scores_direct'], row['colours_direct'])
            row['zipped_mlo_surveys'] = zip(row['attention_scores_mlo_surveys'], row['colours_mlo_surveys'])
            row['zipped_slo_surveys'] = zip(row['attention_scores_slo_surveys'], row['colours_slo_surveys'])
                                    
        years_to_display = range(start_year,end_year+1)
        template = loader.get_template('workload_app/accreditation_report.html')
        context = {
            'programme_id' : programme_id,
            'programme_name' : ProgrammeOffered.objects.filter(id = programme_id).get().programme_name,
            'start_year' : str(start_year)+'/'+str(start_year+1),
            'end_year' : str(end_year)+'/'+str(end_year+1),
            'slo_measures' : slo_measures, 
            'years_to_display' : years_to_display,
            'num_years_colspan' : len(years_to_display),
            'overall_colpsan' : len(years_to_display)+2,
            'big_mlo_slo_table' : big_mlo_slo_table['main_body_table'],
            'attention_scores_table' : attention_scores_table,
            'big_mlo_slo_table_totals_strengths' : big_mlo_slo_table['totals_strengths_row'],
            'big_mlo_slo_table_totals_n_mlo' : big_mlo_slo_table['totals_n_mlo_row'],
            'number_of_slo_plus_one' : len(slo_measures)+1,
            'number_of_slo' : len(slo_measures),
            'slo_identifiers' : slo_identifiers,
            'all_slo_data_for_plot' : all_slo_data_for_plot,
            'all_slo_ids' : all_slo_ids,
            'user_menu' : user_menu,
            'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))

def input_module_survey_results(request,module_code,survey_id):
    user_menu  = DetermineUserMenu(request.user.id,request.user.is_superuser)
    user_homepage = DetermineUserHomePage(request.user.id,request.user.is_superuser)
    survey_qs  =Survey.objects.filter(id = survey_id)
    if (survey_qs.count() != 1):
        #This should really never happen, but just in case the user enters some random number...
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "No such survey exists in the database",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))
    
    if request.user.is_authenticated == False or CanUserAdminThisModule(request.user.id,module_code=module_code, is_super_user = request.user.is_superuser)==False:
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "Access forbidden. User has no access to this page",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))
    
    survey_obj = survey_qs.get()#Should be safe after the if above
    labels = survey_obj.likert_labels.GetListOfLabels()#USe the labels stored in the survey upon creation (not the programme ones which may have changed)
    full_labels = survey_obj.likert_labels.GetFullListOfLabels()
    survey_scores = [-1]*len(full_labels) #max allowed number of options, see model of label set
    if request.method =='POST':
        if survey_obj.survey_type == Survey.SurveyType.MLO:
            mlo_survey_form = InputMLOSurveyForm(request.POST, module_code=module_code, survey_id = survey_id)
            if mlo_survey_form.is_valid():
                #If there are alreday responses, we delete them first (i.e., editing)
                existing_response = SurveyQuestionResponse.objects.filter(parent_survey = survey_obj).delete()

                #If there are alreday responses, we delete them first (i.e., editing)
                SurveyQuestionResponse.objects.filter(parent_survey = survey_obj).delete()

                relevant_lo_queryset = ModuleLearningOutcome.objects.filter(module_code=module_code)
                how_many_questions = relevant_lo_queryset.count() + 5 #5 extra questions

                for question_index in range(0,how_many_questions):
                    question_text = mlo_survey_form.cleaned_data['survey_' + str(survey_id) + '_question_'+ str(question_index)]
                    associated_lo = mlo_survey_form.cleaned_data['survey_' + str(survey_id) + '_associated_lo_of_question_'+ str(question_index)]
                    if(len(question_text) > 0):
                        survey_scores = [-1]*len(full_labels) # max allowed number of options, see model of SurveyLabelSet
                        for opt_idx in range(0,len(labels)):
                            #Note concatenation 
                            supplied_score = mlo_survey_form.cleaned_data['survey_' + str(survey_id) + '_question_' +  str(question_index) + 'response_' + str(opt_idx)]
                            if (supplied_score is not None):
                                survey_scores[opt_idx] = int(supplied_score)
                            else:
                                survey_scores[opt_idx] = 0
                        new_response = SurveyQuestionResponse.objects.create(question_text = question_text,\
                        label_highest_score = full_labels[0],\
                        n_highest_score = survey_scores[0],
                        label_second_highest_score = full_labels[1],\
                        n_second_highest_score = survey_scores[1],
                        label_third_highest_score = full_labels[2],\
                        n_third_highest_score = survey_scores[2],
                        label_fourth_highest_score = full_labels[3],\
                        n_fourth_highest_score = survey_scores[3],\
                        label_fifth_highest_score = full_labels[4],\
                        n_fifth_highest_score = survey_scores[4],\
                        label_sixth_highest_score = full_labels[5],\
                        n_sixth_highest_score = survey_scores[5],\
                        label_seventh_highest_score = full_labels[6],\
                        n_seventh_highest_score = survey_scores[6],\
                        label_eighth_highest_score = full_labels[7],\
                        n_eighth_highest_score = survey_scores[7],\
                        label_ninth_highest_score = full_labels[8],\
                        n_ninth_highest_score = survey_scores[8],\
                        label_tenth_highest_score = full_labels[9],\
                        n_tenth_highest_score = survey_scores[9],\
                        associated_mlo = associated_lo, parent_survey = survey_obj)
                        new_response.save()

                file_obj = None
                if ("raw_file" in request.FILES):#raw_file is the field in the form!
                    file_obj = request.FILES["raw_file"]
                    #Store file in the survey object
                    survey = Survey.objects.filter(id = survey_id).get()                        
                    survey.original_file = file_obj
                    survey.save(update_fields = ["original_file"]) 

    else: #This is a get

        form_to_show = InputMLOSurveyForm(module_code=module_code,survey_id = survey_id, initial = DeteremineSurveyInitialValues(survey_obj.id,module_code))
        template = loader.get_template('workload_app/module_survey_input.html')
        
        all_survey_details = CalculateSurveyDetails(survey_id)
        parent_survey = all_survey_details["title"]
        file_url = all_survey_details["file"] #empty string or something, template may check
        pre_file_upload_message = ''
        if len(file_url) > 0:#there is already a file
            pre_file_upload_message = 'An existing file for this survey is uploaded: '
            form_to_show.fields["raw_file"].label = "If you wish to change the uploaded survey file, upload another one and click \"Submit changes\" below"

        context = {
            'form_to_show' : form_to_show,
            'survey_id' :survey_id,
            'module_code' : module_code,
            'pre_file_upload_message' : pre_file_upload_message,
            'parent_survey' : parent_survey,
            'user_menu' : user_menu,
            'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))

    #Re-load module page (trigger a get there)
    return HttpResponseRedirect(reverse('workload_app:module',  kwargs={'module_code': module_code}))

def input_programme_survey_results(request,programme_id,survey_id):
    user_menu  = DetermineUserMenu(request.user.id,request.user.is_superuser)
    user_homepage = DetermineUserHomePage(request.user.id,request.user.is_superuser)
    
    survey_qs  =Survey.objects.filter(id = survey_id)
    if (survey_qs.count() != 1):
        #This should really never happen, but just in case the user enters some random number...
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "No such survey exissts in the database",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))
    survey_obj = survey_qs.get()#Should be safe after the if above
    
    #USe the labels stored in the Survey object (the programme ones may have changed in the meanwhile, but behaviour is that existing surveys don't change)
    labels = survey_obj.likert_labels.GetListOfLabels()
    full_labels = survey_obj.likert_labels.GetFullListOfLabels()#this one includes "empty" unused ones

    programme = ProgrammeOffered.objects.filter(id = programme_id).get()
    department_id = programme.primary_dept.id
    if request.user.is_authenticated == False or CanUserAdminThisDepartment(request.user.id,department_id, is_super_user = request.user.is_superuser)==False:
        template = loader.get_template('workload_app/errors_page.html')
        context = {
                'error_message': "Access forbidden. User has no access to this page",
                'user_menu' : user_menu,
                'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))
    
    if request.method =='POST':
        if survey_obj.survey_type == Survey.SurveyType.SLO:
            slo_survey_form = InputSLOSurveyDataForm(request.POST, request.FILES, programme_id = programme_id,survey_id = survey_id)
            if slo_survey_form.is_valid():
                #If there are alreday responses, we delete them first (i.e., editing)
                SurveyQuestionResponse.objects.filter(parent_survey = survey_obj).delete()

                relevant_lo_queryset = StudentLearningOutcome.objects.filter(programme__id = programme_id)
                how_many_questions = relevant_lo_queryset.count() + 5 #5 extra questions

                for question_index in range(0,how_many_questions):
                    question_text = slo_survey_form.cleaned_data['survey_' + str(survey_id) + '_question_'+ str(question_index)]
                    associated_lo = slo_survey_form.cleaned_data['survey_' + str(survey_id) + '_associated_lo_of_question_'+ str(question_index)]
                    if(len(question_text) > 0):
                        survey_scores = [-1]*len(full_labels) # max allowed number of options, see model of SurveyLabelSet
                        for opt_idx in range(0,len(labels)):
                            #Note concatenation 
                            supplied_score = slo_survey_form.cleaned_data['survey_' + str(survey_id) + '_question_' +  str(question_index) + 'response_' + str(opt_idx)]
                            if (supplied_score is not None):
                                survey_scores[opt_idx] = int(supplied_score)
                            else:
                                survey_scores[opt_idx] = 0
                        new_response = SurveyQuestionResponse.objects.create(question_text = question_text,\
                        label_highest_score = full_labels[0],\
                        n_highest_score = survey_scores[0],
                        label_second_highest_score = full_labels[1],\
                        n_second_highest_score = survey_scores[1],
                        label_third_highest_score = full_labels[2],\
                        n_third_highest_score = survey_scores[2],
                        label_fourth_highest_score = full_labels[3],\
                        n_fourth_highest_score = survey_scores[3],\
                        label_fifth_highest_score = full_labels[4],\
                        n_fifth_highest_score = survey_scores[4],\
                        label_sixth_highest_score = full_labels[5],\
                        n_sixth_highest_score = survey_scores[5],\
                        label_seventh_highest_score = full_labels[6],\
                        n_seventh_highest_score = survey_scores[6],\
                        label_eighth_highest_score = full_labels[7],\
                        n_eighth_highest_score = survey_scores[7],\
                        label_ninth_highest_score = full_labels[8],\
                        n_ninth_highest_score = survey_scores[8],\
                        label_tenth_highest_score = full_labels[9],\
                        n_tenth_highest_score = survey_scores[9],\
                        associated_slo = associated_lo, parent_survey = survey_obj)
                        new_response.save()
                        #Process file for SLO surveys
                        file_obj = None
                        if ("raw_file" in request.FILES):#raw_file is the field in the form!
                            file_obj = request.FILES["raw_file"]
                            #Store file in the survey object
                            survey = Survey.objects.filter(id = survey_id).get()
                            survey.original_file = file_obj
                            survey.save(update_fields = ["original_file"])


        if survey_obj.survey_type == Survey.SurveyType.PEO:
            peo_survey_form = InputPEOSurveyDataForm(request.POST, request.FILES, programme_id = programme_id,survey_id = survey_id)
            if peo_survey_form.is_valid():
                #If there are alreday responses, we delete them first (i.e., editing)
                SurveyQuestionResponse.objects.filter(parent_survey = survey_obj).delete()
                
                relevant_lo_queryset = ProgrammeEducationalObjective.objects.filter(programme__id = programme_id)
                how_many_questions = relevant_lo_queryset.count() + 5 #5 extra questions

                for question_index in range(0,how_many_questions):
                    question_text = peo_survey_form.cleaned_data['survey_' + str(survey_id) + '_question_'+ str(question_index)]
                    associated_lo = peo_survey_form.cleaned_data['survey_' + str(survey_id) + '_associated_lo_of_question_'+ str(question_index)]
                    if(len(question_text) > 0):
                        survey_scores = [-1]*len(full_labels) # max allowed number of options, see model of SurveyLabelSet
                        for opt_idx in range(0,len(labels)):
                            #Note concatenation 
                            supplied_score = peo_survey_form.cleaned_data['survey_' + str(survey_id) + '_question_' +  str(question_index) + 'response_' + str(opt_idx)]
                            if (supplied_score is not None):
                                survey_scores[opt_idx] = int(supplied_score)
                            else:
                                survey_scores[opt_idx] = 0
                        new_response = SurveyQuestionResponse.objects.create(question_text = question_text,\
                        label_highest_score = full_labels[0],\
                        n_highest_score = survey_scores[0],
                        label_second_highest_score = full_labels[1],\
                        n_second_highest_score = survey_scores[1],
                        label_third_highest_score = full_labels[2],\
                        n_third_highest_score = survey_scores[2],
                        label_fourth_highest_score = full_labels[3],\
                        n_fourth_highest_score = survey_scores[3],\
                        label_fifth_highest_score = full_labels[4],\
                        n_fifth_highest_score = survey_scores[4],\
                        label_sixth_highest_score = full_labels[5],\
                        n_sixth_highest_score = survey_scores[5],\
                        label_seventh_highest_score = full_labels[6],\
                        n_seventh_highest_score = survey_scores[6],\
                        label_eighth_highest_score = full_labels[7],\
                        n_eighth_highest_score = survey_scores[7],\
                        label_ninth_highest_score = full_labels[8],\
                        n_ninth_highest_score = survey_scores[8],\
                        label_tenth_highest_score = full_labels[9],\
                        n_tenth_highest_score = survey_scores[9],\
                        associated_peo = associated_lo, parent_survey = survey_obj)
                        new_response.save()
                        #Process file for PEO surveys
                        file_obj = None
                        if ("raw_file" in request.FILES):#raw_file is the field in the form!
                            file_obj = request.FILES["raw_file"]
                            #Store file in the survey object
                            survey = Survey.objects.filter(id = survey_id).get()
                            survey.original_file = file_obj
                            survey.save(update_fields = ["original_file"])
        
        #Re-load accreditation (trigger a get there)
        return HttpResponseRedirect(reverse('workload_app:accreditation',  kwargs={'programme_id': programme_id}))

    else:#this is a GET
        
        form_to_show = InputSLOSurveyDataForm(programme_id = programme_id,survey_id = survey_id, initial = DeteremineSurveyInitialValues(survey_obj.id,'N/A'))
        if survey_obj.survey_type == Survey.SurveyType.PEO:
            form_to_show = InputPEOSurveyDataForm(programme_id = programme_id,survey_id = survey_id, initial = DeteremineSurveyInitialValues(survey_obj.id, 'N/A'))

        all_survey_details = CalculateSurveyDetails(survey_id)
        parent_survey = all_survey_details["title"]
        file_url = all_survey_details["file"] #empty string or something, template may check
        pre_file_upload_message = ''
        if len(file_url) > 0:#there is already a file
            pre_file_upload_message = 'An existing file for this survey is uploaded: '
            form_to_show.fields["raw_file"].label = "If you wish to change the uploaded survey file, upload another one and click \"Submit changes\" below"

        template = loader.get_template('workload_app/survey_input.html')
        context = {
            'form_to_show' : form_to_show,
            'programme_id' : programme_id,
            'survey_id' :survey_id,
            'parent_survey': parent_survey,
            'pre_file_upload_message' : pre_file_upload_message,
            'file_url' : file_url,
            'user_menu' : user_menu,
            'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))

def survey_results(request,survey_id):
    user_menu  = DetermineUserMenu(request.user.id,request.user.is_superuser)
    user_homepage = DetermineUserHomePage(request.user.id,request.user.is_superuser)
    
    survey_obj = Survey.objects.filter(id=survey_id).get()
    programme_id = survey_obj.programme_associated.id
    department_id = ProgrammeOffered.objects.filter(id = programme_id).get().primary_dept.id
    if (survey_obj.survey_type != Survey.SurveyType.MLO):#WE block only survey that programme-level. We allow all to see MLO survey results (but there won't be links...)
        if request.user.is_authenticated == False or CanUserAdminThisDepartment(request.user.id,department_id, is_super_user = request.user.is_superuser)==False:
            template = loader.get_template('workload_app/errors_page.html')
            context = {
                    'error_message': "Access forbidden. User has no access to this page",
                    'user_menu' : user_menu,
                    'user_homepage' : user_homepage
            }
            return HttpResponse(template.render(context, request))
    
    if request.method=="GET":
        survey_labels = []
        survey_obj = Survey.objects.filter(id = survey_id).get()
        #WE are visualizaing here. The labels are taken from the survey object
        survey_labels = survey_obj.likert_labels.GetListOfLabels()

        question_texts = []
        shorter_question_texts = []
        srv_results = []
        percentages = []
        cumulative_percenatges = []
        total_responses_per_question = []
        questions_nps = []
        questions_nps_messages = []
        questions_perc_positive = []
        questions_perc_non_negative = []
        for response in SurveyQuestionResponse.objects.filter(parent_survey__id = survey_id):
            question_texts.append(response.question_text)
            shorter_question_texts.append(ShortenString(response.question_text,25))

            resp_feat = response.CalculateRepsonsesProprties()
            srv_results.append(resp_feat["responses"])
            percentages.append(resp_feat["percentages"])
            cumulative_percenatges.append(resp_feat["cumulative_percentages"])
            total_responses_per_question.append(resp_feat["all_respondents"])
            questions_nps.append(resp_feat["nps"])
            questions_nps_messages.append(resp_feat["nps_message"])
            questions_perc_positive.append(resp_feat["percentage_positive"])
            questions_perc_non_negative.append(resp_feat["percentage_non_negative"])
        all_survey_details = CalculateSurveyDetails(survey_id)
        template = loader.get_template('workload_app/survey_results.html')

        #transpose percentages for the overall stacked chart data
        overall_plot_data = list(map(list, zip(*percentages)))

        context = {
            'survey_details' : all_survey_details,
            'average_response_rate' : all_survey_details["average_response_rate"],
            'question_texts' : question_texts,
            'shorter_question_texts' : shorter_question_texts,
            'labels' : survey_labels,
            'bar_chart_data' : srv_results,
            'percentages' : percentages,
            'overall_plot_data' : overall_plot_data,
            'cumulative_percentages' : cumulative_percenatges,
            'total_responses_per_question' : total_responses_per_question,
            'questions_nps' : questions_nps,
            'questions_nps_messages' : questions_nps_messages,
            'questions_perc_positive' : questions_perc_positive,
            'questions_perc_non_negative' : questions_perc_non_negative,
            'user_menu' : user_menu,
            'user_homepage' : user_homepage
        }
        return HttpResponse(template.render(context, request))
    

###################
# BElow here only handler methods that handle some of the POST requests
###################

def add_assignment(request,workloadscenario_id):
    if request.method =='POST':
        id_of_prof_involved = request.POST['select_lecturer']
        id_of_mod_involved = request.POST['select_module']
        manual_radio_button_status = request.POST['manual_hours_yes_no']
        counted_or_not_radio_button_status = request.POST['counted_towards_workload']
        selected_scen = WorkloadScenario.objects.filter(id = workloadscenario_id).get()
        form = AddTeachingAssignmentForm(request.POST, prof_id = id_of_prof_involved, module_id = id_of_mod_involved,workloadscenario_id = selected_scen.id)
        if form.is_valid():
            selected_prof_name = form.cleaned_data['select_lecturer']
            selected_module = form.cleaned_data['select_module']

            selected_module = Module.objects.filter(id = id_of_mod_involved).filter(scenario_ref__id = workloadscenario_id).get()
            selected_prof =  Lecturer.objects.filter(name = selected_prof_name).filter(workload_scenario__id = workloadscenario_id).get()
            count_in_wl = True
            if (counted_or_not_radio_button_status == 'no'): count_in_wl = False
            #Check if an assignment for the same module and same prof alreday exists (if so, we just add the hours)
            possible_existing_objects = TeachingAssignment.objects.filter(assigned_module = selected_module)\
                                                                  .filter(assigned_lecturer = selected_prof)\
                                                                  .filter(workload_scenario__id=workloadscenario_id)\
                                                                  .filter(counted_towards_workload = count_in_wl)
            if (possible_existing_objects.count() > 0):
                num_hrs = form.cleaned_data['enter_number_of_total_hours_assigned'];#TODO This is bad here, must chack if manual hours were given or not
                existing_hrs = possible_existing_objects.values().get()
                total_number_of_hours = num_hrs + existing_hrs['number_of_hours'] #Just add the hours
                possible_existing_objects.update(number_of_hours=int(total_number_of_hours))
            else:#Here the count is zero: an assignment to the same prof, same mod does not exist, finally create the assignment object
                
                if manual_radio_button_status == 'no' :
                    supplied_weekly_lecture_hours = form.cleaned_data["enter_number_of_weekly_lecture_hours"]
                    supplied_weekly_tutorial_hours = form.cleaned_data["enter_number_of_weekly_tutorial_hours"]
                    supplied_num_tutorial_groups = form.cleaned_data["enter_number_of_tutorial_groups"]
                    supplied_weeks_assigned = form.cleaned_data["enter_number_of_weeks_assigned"]
                    #Calculation of hours based on weekly info
                    num_hrs = CalculateNumHoursBasedOnWeeklyInfo(int(supplied_weekly_lecture_hours), int(supplied_weekly_tutorial_hours),
                                                                         int(supplied_weeks_assigned), int(supplied_num_tutorial_groups))
                    TeachingAssignment.objects.create(assigned_module=selected_module,\
                                                      assigned_lecturer=selected_prof,\
                                                      number_of_hours=int(num_hrs),\
                                                      number_of_weekly_lecture_hours = int(supplied_weekly_lecture_hours),\
                                                      number_of_weekly_tutorial_hours = int(supplied_weekly_tutorial_hours),\
                                                      number_of_tutorial_groups = int(supplied_num_tutorial_groups),\
                                                      number_of_weeks_assigned = int(supplied_weeks_assigned),\
                                                      assigned_manually = False,\
                                                      counted_towards_workload = count_in_wl,\
                                                      workload_scenario= selected_scen)
                else:
                    num_hrs = form.cleaned_data['enter_number_of_total_hours_assigned'];
                    TeachingAssignment.objects.create(assigned_module=selected_module,\
                                                      assigned_lecturer=selected_prof,\
                                                      number_of_hours=int(num_hrs),\
                                                      assigned_manually = True,\
                                                      counted_towards_workload = count_in_wl,\
                                                      workload_scenario= selected_scen)
        else:
            template = loader.get_template('workload_app/errors_page.html')
            context = {
                    'error_message': form.errors
            }
            return HttpResponse(template.render(context, request))    

    #Re-load workload scenario page (trigger a get)
    return HttpResponseRedirect(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': workloadscenario_id}))


def remove_assignment(request, workloadscenario_id):
    if request.method =='POST':
        form = RemoveTeachingAssignmentForm(request.POST, workloadscenario_id = workloadscenario_id)
        if (form.is_valid()):
            TeachingAssignment.objects.filter(id=request.POST.get('select_teaching_assignment_to_remove')).delete()
    #Otherwise do nothing
    return HttpResponseRedirect(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': workloadscenario_id}))


def edit_lecturer_assignments(request, prof_id):
    prof_involved = Lecturer.objects.filter(id = prof_id).get()
    scenario_id = prof_involved.workload_scenario.id

    if request.method =='POST':    
        form = EditTeachingAssignmentForm(request.POST,prof_id = prof_id)
        if form.is_valid():
            for mod in Module.objects.filter(scenario_ref__id = scenario_id):
                mod_code = mod.module_code
                if mod_code in form.cleaned_data.keys():
                    if Module.objects.filter(module_code = mod_code).exists():
                        assign = TeachingAssignment.objects.filter(assigned_module__module_code=mod_code)\
                                            .filter(assigned_lecturer__id=prof_id)
                        supplied_flag_for_counting_in_wl = form.cleaned_data['counted_in_workload'+mod_code]
                        counted_in_wl = True
                        if (supplied_flag_for_counting_in_wl == 'no') : counted_in_wl = False

                        if (assign.get().assigned_manually == True):#Manually assigned, we only care about toal hours
                            supplied_number_of_hours = form.cleaned_data['total_hours'+mod_code]
                            if supplied_number_of_hours is None: #If field is empty, we put to zero otherwise the following cast to integer will crash
                                supplied_number_of_hours = 0;
                            if (int(supplied_number_of_hours) > 0):
                                assign.update(number_of_hours=int(supplied_number_of_hours),\
                                               counted_towards_workload = counted_in_wl)
                            else:#If zero or negative, remove the assignment
                                assign.delete();
                        else:#Assigned by week. We need to do the calculation
                            supplied_weekly_lecture_hours = form.cleaned_data["weekly_lecture_hrs"+mod_code]
                            if supplied_weekly_lecture_hours is None: supplied_weekly_lecture_hours = 0
                            supplied_weekly_tutorial_hours = form.cleaned_data["weekly_tutorial_hrs"+mod_code]
                            if supplied_weekly_tutorial_hours is None: supplied_weekly_tutorial_hours = 0
                            supplied_num_tutorial_groups = form.cleaned_data["num_tut"+mod_code]
                            if supplied_num_tutorial_groups is None: supplied_num_tutorial_groups = 0
                            supplied_weeks_assigned = form.cleaned_data["num_weeks"+mod_code]
                            if supplied_weeks_assigned is None: supplied_weeks_assigned = 0
                            
                            #Calculation of hours based on weekly info
                            num_hrs = CalculateNumHoursBasedOnWeeklyInfo(int(supplied_weekly_lecture_hours), int(supplied_weekly_tutorial_hours),
                                                                         int(supplied_weeks_assigned), int(supplied_num_tutorial_groups))
                                
                            if num_hrs > 0:
                                assign.update( number_of_hours=int(num_hrs),\
                                               number_of_weekly_lecture_hours = int(supplied_weekly_lecture_hours),\
                                               number_of_weekly_tutorial_hours = int(supplied_weekly_tutorial_hours),\
                                               number_of_tutorial_groups = int(supplied_num_tutorial_groups),\
                                               number_of_weeks_assigned = int(supplied_weeks_assigned),\
                                               counted_towards_workload = counted_in_wl)
                            else:
                                assign.delete()
    #Otherwise do nothing
    return HttpResponseRedirect(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_id}))

def edit_module_assignments(request, module_id):
    module_involved = Module.objects.filter(id=module_id).get()
    scenario_id = module_involved.scenario_ref.id
    if request.method =='POST':
        
        form = EditModuleAssignmentForm(request.POST,module_id = module_id)
        if form.is_valid():
            for prof in Lecturer.objects.filter(workload_scenario__id = scenario_id):
                prof_name = prof.name
                if prof_name in form.cleaned_data.keys():
                    
                    if Lecturer.objects.filter(name = prof_name).exists():
                        supplied_flag_for_counting_in_wl = form.cleaned_data['counted_in_workload'+prof_name]
                        counted_in_wl = True
                        if (supplied_flag_for_counting_in_wl == 'no') : counted_in_wl = False

                        assign = TeachingAssignment.objects.filter(assigned_module__id=module_id)\
                                                .filter(assigned_lecturer__name=prof_name)\
                                                .filter(workload_scenario__id=scenario_id)
                        if (assign.get().assigned_manually == True):#Manually assigned, we only care about toal hours
                            supplied_number_of_hours = form.cleaned_data['total_hours'+prof_name]
                            if supplied_number_of_hours is None: #If field is empty, we put to zero otherwise the following cast to integer will crash
                                supplied_number_of_hours = 0;
                            if (int(supplied_number_of_hours) > 0):
                                assign.update(number_of_hours=int(supplied_number_of_hours),\
                                               counted_towards_workload = counted_in_wl)
                            else:
                                assign.delete();
                        else:#Assigned by week. We need to do the calculation
                            
                            supplied_weekly_lecture_hours = form.cleaned_data["weekly_lecture_hrs"+prof_name]
                            if supplied_weekly_lecture_hours is None: supplied_weekly_lecture_hours = 0
                            supplied_weekly_tutorial_hours = form.cleaned_data["weekly_tutorial_hrs"+prof_name]
                            if supplied_weekly_tutorial_hours is None: supplied_weekly_tutorial_hours = 0
                            supplied_num_tutorial_groups = form.cleaned_data["num_tut"+prof_name]
                            if supplied_num_tutorial_groups is None: supplied_num_tutorial_groups = 0
                            supplied_weeks_assigned = form.cleaned_data["num_weeks"+prof_name]
                            if supplied_weeks_assigned is None: supplied_weeks_assigned = 0
                            #Calculation of hours based on weekly info
                            num_hrs = CalculateNumHoursBasedOnWeeklyInfo(int(supplied_weekly_lecture_hours), int(supplied_weekly_tutorial_hours),
                                                                            int(supplied_weeks_assigned), int(supplied_num_tutorial_groups))
                                
                            if num_hrs > 0:
                                assign.update( number_of_hours=int(num_hrs),\
                                                number_of_weekly_lecture_hours = int(supplied_weekly_lecture_hours),\
                                                number_of_weekly_tutorial_hours = int(supplied_weekly_tutorial_hours),\
                                                number_of_tutorial_groups = int(supplied_num_tutorial_groups),\
                                                number_of_weeks_assigned = int(supplied_weeks_assigned),\
                                                counted_towards_workload = counted_in_wl)
                            else:#0 hours, delete the assignment
                                assign.delete()         
    #Otherwise do nothing
    return HttpResponseRedirect(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_id}))

def manage_scenario(request):
    if request.method =='POST':
        form = ScenarioForm(request.POST)
        if form.is_valid():
            #This is from the workloads index page. We capture the required dept
            supplied_dept_name = form.cleaned_data['dept']
            supplied_dept = Department.objects.filter(department_name = supplied_dept_name)
            #Call the helper to create what's needed
            HandleScenarioForm(form,supplied_dept.get().id)
        else:#Invalid data, send to error page
            template = loader.get_template('workload_app/errors_page.html')
            context = {
                    'error_message': form.errors
            }
            return HttpResponse(template.render(context, request))   

    return HttpResponseRedirect(reverse('workload_app:workloads_index'))

def remove_scenario(request):
    if request.method =='POST':
        form = RemoveScenarioForm(request.POST, dept_id=-1)
        if form.is_valid():
            selected_scenario_label = form.cleaned_data['select_scenario_to_remove'];
            how_many_scenarios = WorkloadScenario.objects.all().count()
            
            if (how_many_scenarios>1):
                #Remove relevant teaching assignment
                TeachingAssignment.objects.filter(workload_scenario__label = selected_scenario_label).delete()
                #Remove the selected scenario.
                WorkloadScenario.objects.filter(label=selected_scenario_label).delete()
                    
    return HttpResponseRedirect(reverse('workload_app:workloads_index'))
    
def add_professor(request, workloadscenario_id):
    if request.method =='POST':
        form = ProfessorForm(request.POST)
        if (form.is_valid()):
            supplied_prof_name = request.POST['name']
            supplied_prof_appointment = request.POST['fraction_appointment']
            supplied_employment_track_id = request.POST['employment_track']
            supplied_service_role_id = request.POST['service_role']
            supplied_external = request.POST['is_external']
            
            active_scen = WorkloadScenario.objects.filter(id=workloadscenario_id).get()
            empl_track = EmploymentTrack.objects.filter(id = supplied_employment_track_id).get()
            serv_role = ServiceRole.objects.filter(id = supplied_service_role_id).get()
            if (request.POST['fresh_record'] == 'False'):
                Lecturer.objects.filter(name=supplied_prof_name).filter(workload_scenario=active_scen).update(name=supplied_prof_name,\
                                                                                                fraction_appointment=float(supplied_prof_appointment), \
                                                                                                employment_track = empl_track,
                                                                                                service_role = serv_role,
                                                                                                is_external = supplied_external)
            else :
                if (Lecturer.objects.filter(name = supplied_prof_name).filter(workload_scenario__id = active_scen.id).exists()):
                    template = loader.get_template('workload_app/errors_page.html')
                    context = {
                        'error_message': 'Invalid lecturer name. It already exists in the ' + active_scen.label + ' workload',
                    }
                    return HttpResponse(template.render(context, request))           
                else:#we can safely add, no duplicates within the same workload
                    Lecturer.objects.create(name=supplied_prof_name,fraction_appointment=float(supplied_prof_appointment), \
                                                                                        workload_scenario = active_scen,\
                                                                                        employment_track = empl_track,
                                                                                        service_role = serv_role,
                                                                                        is_external = supplied_external)
        else:
            template = loader.get_template('workload_app/errors_page.html')
            context = {
                    'error_message': form.errors
            }
            return HttpResponse(template.render(context, request))   
    
    #Otherwise just go back to workload view
    selected_scen = WorkloadScenario.objects.filter(id = workloadscenario_id).get();
    return HttpResponseRedirect(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': selected_scen.id}))

def remove_professor(request,workloadscenario_id):
    if request.method =='POST':
        form = RemoveProfessorForm(request.POST, workloadscenario_id = workloadscenario_id)
        if (form.is_valid()):
            selected_prof_name = form.cleaned_data['select_professor_to_remove']
            wipe_out = form.cleaned_data['wipe_out_from_table']
            TeachingAssignment.objects.filter(assigned_lecturer__name = selected_prof_name, workload_scenario__id = workloadscenario_id).delete()
            if (wipe_out==True):                
                #Remove the prof from the list
                Lecturer.objects.filter(name=selected_prof_name, workload_scenario__id = workloadscenario_id).delete()
            #else, nothing, the lecturer remains on the list
                
        
        else:#invalid form
            template = loader.get_template('workload_app/errors_page.html')
            context = {
                    'error_message': form.errors
            }
            return HttpResponse(template.render(context, request))   
    
    
    #Otherwise just go back to workload view
    return HttpResponseRedirect(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': workloadscenario_id}))

def add_module(request,workloadscenario_id):
    department = WorkloadScenario.objects.filter(id = workloadscenario_id).get().dept
    
    if request.method =='POST':
        form = ModuleForm(request.POST, dept_id = department.id)      
        if form.is_valid():
            supplied_module_code = form.cleaned_data['module_code']
            supplied_module_title = form.cleaned_data['module_title']
            supplied_type = form.cleaned_data['module_type']
            supplied_sem_offered = form.cleaned_data['semester_offered']
            supplied_n_tutorial_groups = form.cleaned_data['number_of_tutorial_groups']
            supplied_programme_belongs_to = form.cleaned_data['primary_programme']
            supplied_compulsory_in_primary_programme = form.cleaned_data['compulsory_in_primary_programme']
            supplied_students_year_of_study = form.cleaned_data['students_year_of_study']
            supplied_secondary_programme_belongs_to = form.cleaned_data['secondary_programme']
            supplied_tertirary_programme_belongs_to = form.cleaned_data['tertiary_programme']
            supplied_compulsory_in_secondary_programme = form.cleaned_data['compulsory_in_secondary_programme']
            supplied_compulsory_in_tertiary_programme = form.cleaned_data['compulsory_in_tertiary_programme']
            supplied_sub_programme_belongs_to = form.cleaned_data['sub_programme']
            supplied_secondary_sub_programme_belongs_to = form.cleaned_data['secondary_sub_programme']

            supplied_hours = 0;
            if (form.cleaned_data['total_hours']):
                supplied_hours = form.cleaned_data['total_hours']
            else:
                supplied_hours = CalculateTotalModuleHours(supplied_n_tutorial_groups, supplied_type)
            
            if (request.POST['fresh_record'] == 'False'):
                #This is an update
                Module.objects.filter(module_code=supplied_module_code).filter(scenario_ref__id=workloadscenario_id).update(module_code=supplied_module_code, \
                                         module_title=supplied_module_title, \
                                         total_hours=supplied_hours, \
                                         module_type =  supplied_type,\
                                         semester_offered = supplied_sem_offered,\
                                         number_of_tutorial_groups = supplied_n_tutorial_groups,\
                                         primary_programme = supplied_programme_belongs_to,\
                                         compulsory_in_primary_programme = supplied_compulsory_in_primary_programme,\
                                         students_year_of_study = supplied_students_year_of_study,\
                                         secondary_programme = supplied_secondary_programme_belongs_to,\
                                         tertiary_programme = supplied_tertirary_programme_belongs_to,\
                                         compulsory_in_secondary_programme = supplied_compulsory_in_secondary_programme,\
                                         compulsory_in_tertiary_programme = supplied_compulsory_in_tertiary_programme,\
                                         sub_programme = supplied_sub_programme_belongs_to,\
                                         secondary_sub_programme = supplied_secondary_sub_programme_belongs_to);                  
                                
            else:
                #Create a new module
                active_scen = WorkloadScenario.objects.filter(id=workloadscenario_id).get()
                #if it is a fesh record, we must make sure no duplicate names in this scenario
                if (Module.objects.filter(module_code = supplied_module_code).filter(scenario_ref__id = workloadscenario_id).exists()):
                    template = loader.get_template('workload_app/errors_page.html')
                    context = {
                        'error_message': 'Invalid module code. It already exists in the ' + active_scen.label + ' workload',
                    }
                    return HttpResponse(template.render(context, request))   
                else: #We can safely add, no duplicate in this workload scenario   
                    new_mod = Module.objects.create(module_code=supplied_module_code, \
                                                module_title=supplied_module_title, \
                                                scenario_ref = active_scen,\
                                                total_hours = supplied_hours,\
                                                module_type = supplied_type,\
                                                semester_offered = supplied_sem_offered,\
                                                number_of_tutorial_groups = supplied_n_tutorial_groups,\
                                                primary_programme = supplied_programme_belongs_to,\
                                                compulsory_in_primary_programme = supplied_compulsory_in_primary_programme,\
                                                students_year_of_study = supplied_students_year_of_study,\
                                                secondary_programme = supplied_secondary_programme_belongs_to,\
                                                tertiary_programme = supplied_tertirary_programme_belongs_to,\
                                                compulsory_in_secondary_programme = supplied_compulsory_in_secondary_programme,\
                                                compulsory_in_tertiary_programme = supplied_compulsory_in_tertiary_programme,\
                                                sub_programme = supplied_sub_programme_belongs_to,\
                                                secondary_sub_programme = supplied_secondary_sub_programme_belongs_to)
                    new_mod.save()
        else:
            template = loader.get_template('workload_app/errors_page.html')
            context = {
                    'error_message': form.errors
            }
            return HttpResponse(template.render(context, request))   
        
    #Otherwise just go back to workload view or department view, depending where we come from
    if ("department" in request.META["HTTP_REFERER"]):#The edit module form appears in two pages, the workload page and the "department" page
        dept_id = WorkloadScenario.objects.filter(id=workloadscenario_id).get().dept.id
        return HttpResponseRedirect(reverse('workload_app:department',  kwargs={'department_id': dept_id}))
    else:
        return HttpResponseRedirect(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': workloadscenario_id}))

def remove_module(request,workloadscenario_id):
    if request.method =='POST':
        form = RemoveModuleForm(request.POST,workloadscenario_id = workloadscenario_id)
        if form.is_valid():  
            selected_module = form.cleaned_data['select_module_to_remove'];
            wipe_out = form.cleaned_data['wipe_from_table']
            #Extract module code
            selected_module_code = selected_module.__str__().split()[0];#see __str__ method of Module model, code is at the first position
            
            #Remove only the teaching assignments in this scenario
            TeachingAssignment.objects.filter(assigned_module__module_code = selected_module_code, workload_scenario__id = workloadscenario_id).delete();
            if (wipe_out==form.REMOVE_COMPLETELY):
                #Remove the module from the list
                Module.objects.filter(module_code=selected_module_code, scenario_ref__id = workloadscenario_id).delete()             
            #Else, module stays there because wipe is false
            
    #Otherwise just go back to workload view
    return HttpResponseRedirect(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': workloadscenario_id}))

def manage_module_type(request, department_id):
    if request.method =='POST':
        form = ModuleTypeForm(request.POST)
        if form.is_valid():  
            supplied_type_name = form.cleaned_data['type_name']
            new_type = ModuleType.objects.create(type_name = supplied_type_name, department=Department.objects.filter(id=department_id).get())
            new_type.save()
        else:
            template = loader.get_template('workload_app/errors_page.html')
            context = {
                    'error_message': form.errors
            }
            return HttpResponse(template.render(context, request))   
    #Otherwise do nothing
    return HttpResponseRedirect(reverse('workload_app:department',  kwargs={'department_id': department_id}))

def remove_module_type(request, department_id):
    if request.method =='POST':
        form = RemoveModuleTypeForm(request.POST,department_id=department_id)
        if form.is_valid():  
            ModuleType.objects.filter(id=request.POST.get('select_module_type_to_remove')).delete()
            
    #Otherwise do nothing
    return HttpResponseRedirect(reverse('workload_app:department',  kwargs={'department_id': department_id}))


def manage_department(request):
    if request.method =='POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():  
            supplied_dept_name = form.cleaned_data['department_name']
            supplied_dept_acr = form.cleaned_data['department_acronym']
            supplied_faculty = form.cleaned_data['faculty']
            fac_obj = Faculty.objects.filter(faculty_name=supplied_faculty).get()
            if (request.POST['fresh_record'] == 'False'):
                #This is an edit
                supplied_id = form.cleaned_data['dept_id']
                if (supplied_id != Department.objects.filter(department_name = DEFAULT_DEPARTMENT_NAME).get().id):#No messing with default dept
                    Department.objects.filter(id = int(supplied_id)).update(department_name = supplied_dept_name, \
                                                                        department_acronym = supplied_dept_acr, \
                                                                        faculty = fac_obj)
            else:#New dept
                new_dept = Department.objects.create(department_name = supplied_dept_name, department_acronym = supplied_dept_acr, faculty = fac_obj)
                new_dept.save()
        else:
            template = loader.get_template('workload_app/errors_page.html')
            context = {
                    'error_message': form.errors
            }
            return HttpResponse(template.render(context, request))   
    #Otherwise do nothing
    return HttpResponseRedirect(reverse('workload_app:workloads_index'))


def remove_department(request):
    if request.method =='POST':
        form = RemoveDepartmentForm(request.POST);
        if form.is_valid():  
            selected_department = form.cleaned_data['select_department_to_remove']
            if (selected_department.department_name != DEFAULT_DEPARTMENT_NAME):#If user wants to delete the default, we do nothing
                default_dept = Department.objects.filter(department_name = DEFAULT_DEPARTMENT_NAME)
                if (default_dept.count() == 0): #If, for some reason, the default dept is not there, create one (this should be impossible...)
                    Department.objects.create(department_name = DEFAULT_DEPARTMENT_NAME, department_acronym = DEFAULT_DEPT_ACRONYM)
                    default_dept = Department.objects.filter(department_name = DEFAULT_DEPARTMENT_NAME)

                #Turn all workload scenarios of that department to the default department    
                WorkloadScenario.objects.filter(dept__department_name=selected_department).update(dept = default_dept.get().id)
                Department.objects.filter(department_name=selected_department).delete()
            
    #Otherwise do nothing
    return HttpResponseRedirect(reverse('workload_app:workloads_index'));   

def manage_faculty(request):
    if request.method =='POST':
        form = FacultyForm(request.POST);
        if form.is_valid():  
            supplied_fac_name = form.cleaned_data['faculty_name']
            supplied_fac_acr = form.cleaned_data['faculty_acronym']

            if (request.POST['fresh_record'] == 'False'):
                #This is an edit
                supplied_id = form.cleaned_data['fac_id']
                if (supplied_id != Faculty.objects.filter(faculty_name = DEFAULT_FACULTY_NAME).get().id):#No messing with default faculty
                    Faculty.objects.filter(id = int(supplied_id)).update(faculty_name = supplied_fac_name, \
                                                                         faculty_acronym = supplied_fac_acr)
            else:#New faculty
                new_fac = Faculty.objects.create(faculty_name = supplied_fac_name, faculty_acronym = supplied_fac_acr)
                new_fac.save()
        else:#Invalid data
            template = loader.get_template('workload_app/errors_page.html')
            context = {
                    'error_message': form.errors
            }
            return HttpResponse(template.render(context, request))   

    #Otherwise do nothing
    return HttpResponseRedirect(reverse('workload_app:workloads_index'))

def remove_faculty(request):
    if request.method =='POST':
        form = RemoveFacultyForm(request.POST)
        if form.is_valid():  
            selected_faculty = form.cleaned_data['select_faculty_to_remove']
            if (selected_faculty.faculty_name != DEFAULT_FACULTY_NAME):#If user wants to delete the default, we do nothing
                default_fac = Faculty.objects.filter(faculty_name = DEFAULT_FACULTY_NAME)
                if (default_fac.count() == 0): #If, for some reason, the default faculty is not there, create one (this should be impossible...)
                    Faculty.objects.create(faculty_name = DEFAULT_FACULTY_NAME, faculty_acronym = DEFAULT_FACULTY_ACRONYM)
                    default_fac = Department.objects.filter(faculty_name = DEFAULT_FACULTY_NAME)

                #Turn all department of that faculy to the default faculty
                Department.objects.filter(faculty__faculty_name=selected_faculty).update(faculty = default_fac.get().id)
                #Then delete the faculty
                Faculty.objects.filter(faculty_name=selected_faculty).delete()

    #Otherwise do nothing
    return HttpResponseRedirect(reverse('workload_app:workloads_index'))


def manage_programme_offered(request, dept_id):
    if request.method =='POST':
        form = ProgrammeOfferedForm(request.POST);
        if form.is_valid():  
            supplied_prog_name = form.cleaned_data['programme_name']
            supplied_dept = form.cleaned_data['primary_dept']
            dept_obj = Department.objects.filter(department_name=supplied_dept).get()
            if (request.POST['fresh_record'] == 'False'):
                supplied_id = form.cleaned_data['prog_id']
                #This is an edit
                ProgrammeOffered.objects.filter(id = int(supplied_id)).update(programme_name = supplied_prog_name, primary_dept = dept_obj)
                
            else:
                #This is a new programme
                new_prog = ProgrammeOffered.objects.create(programme_name = supplied_prog_name, primary_dept = dept_obj)
                new_prog.save()
                
        else:
            template = loader.get_template('workload_app/errors_page.html')
            context = {
                    'error_message': form.errors
            }
            return HttpResponse(template.render(context, request))   
    #Otherwise do nothing
    return HttpResponseRedirect(reverse('workload_app:department',  kwargs={'department_id': dept_id}));

def manage_subprogramme_offered(request, dept_id):
    if request.method =='POST':
        form = SubProgrammeOfferedForm(request.POST, department_id = dept_id)
        if form.is_valid():
            supplied_sub_prog_name = form.cleaned_data['sub_programme_name']
            supplied_main_programme = form.cleaned_data['main_programme']
            main_prog_obj = ProgrammeOffered.objects.filter(programme_name=supplied_main_programme).get()
            if (request.POST['fresh_record'] == 'False'):
                supplied_id = form.cleaned_data['sub_prog_id']
                #This is an edit
                SubProgrammeOffered.objects.filter(id = int(supplied_id)).update(sub_programme_name = supplied_sub_prog_name, main_programme = main_prog_obj)
            else:
                #This is a new subprogramme
                new_prog = SubProgrammeOffered.objects.create(sub_programme_name = supplied_sub_prog_name, main_programme = main_prog_obj)
                new_prog.save()
        else:
            template = loader.get_template('workload_app/errors_page.html')
            context = {
                    'error_message': form.errors
            }
            return HttpResponse(template.render(context, request))   
    #Otherwise do nothing
    return HttpResponseRedirect(reverse('workload_app:department',  kwargs={'department_id': dept_id}))

def remove_programme_offered(request, dept_id):
    if request.method =='POST':
        form = RemoveProgrammeForm(request.POST, department_id = dept_id)
        if form.is_valid():
            supplied_prog_name = form.cleaned_data['select_programme_to_remove']
            ProgrammeOffered.objects.filter(primary_dept__id=dept_id).filter(programme_name=supplied_prog_name).delete()

    #Otherwise do nothing
    return HttpResponseRedirect(reverse('workload_app:department',  kwargs={'department_id': dept_id}))

def remove_subprogramme_offered(request, dept_id):
    if request.method =='POST':
        form = RemoveSubProgrammeForm(request.POST, department_id = dept_id)
        if form.is_valid():
            supplied_subprog_name = form.cleaned_data['select_subprogramme_to_remove']
            #Note we delete only subprogrammes from the same departemnt as the programmes they are linked to
            SubProgrammeOffered.objects.filter(main_programme__primary_dept__id=dept_id).filter(sub_programme_name=supplied_subprog_name.sub_programme_name).delete()

    #Otherwise do nothing
    return HttpResponseRedirect(reverse('workload_app:department',  kwargs={'department_id': dept_id}))


