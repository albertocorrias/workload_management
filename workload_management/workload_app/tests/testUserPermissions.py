from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User, Group
from decimal import *
import datetime

from workload_app.models import Faculty, Department, Module, ModuleType, WorkloadScenario,UniversityStaff, \
    Academicyear, Lecturer, EmploymentTrack, ServiceRole,TeachingAssignment,ProgrammeOffered,StudentLearningOutcome, Survey,ModuleLearningOutcome
from workload_app.helper_methods_users import DetermineUserHomePage, CanUserAdminThisDepartment, CanUserAdminThisModule, CanUserAdminThisFaculty, CanUserAdminUniversity, DetermineUserMenu
from workload_app.helper_methods_survey import DetermineSurveyLabelsForProgramme

class TestUserPermissions(TestCase):

    def testHelperMethodsForUser(self):
        
        sup_user = User.objects.create_user('new_super_user', 'test@user.com', 'test_super_user_password')
        sup_user.is_superuser = True
        sup_user.save()
        uni_super_user = UniversityStaff.objects.create(user = sup_user, department=None,faculty=None)
        self.assertEqual(DetermineUserHomePage(uni_super_user.id, is_super_user = True), '/workloads_index')
        self.assertEqual(CanUserAdminUniversity(uni_super_user.id, is_super_user = True), True)

        #Create fauclty, dept and module
        new_fac = Faculty.objects.create(faculty_name = 'test_fac', faculty_acronym = 'CDE')
        new_fac_2 = Faculty.objects.create(faculty_name = 'test_fac2', faculty_acronym = 'CDE2')

        new_dept = Department.objects.create(department_name = 'test_dept', department_acronym = 'BME', faculty = new_fac)
        new_prog = ProgrammeOffered.objects.create(programme_name = 'test_prog', primary_dept = new_dept)
        uni_super_user.departemnt = new_dept
        uni_super_user.faculty = new_fac
        #Check even after assigning faculty...
        self.assertEqual(DetermineUserHomePage(uni_super_user.id, is_super_user = True), '/workloads_index')
        self.assertEqual(CanUserAdminUniversity(uni_super_user.id, is_super_user = True), True)

        #Create a module
        mod_code = "BN2102"
        acad_year_1 = Academicyear.objects.create(start_year=2021)
        scenario_1 = WorkloadScenario.objects.create(label="scenario_1", academic_year = acad_year_1, dept = new_dept, status = WorkloadScenario.OFFICIAL)
        mod_type_1 = ModuleType.objects.create(type_name = "one type")
        track_1 = EmploymentTrack.objects.create(track_name = "track_1", track_adjustment = 2.0, is_adjunct = False)
        service_role_1 = ServiceRole.objects.create(role_name = "role_1", role_adjustment = 2.0)
        module_1 = Module.objects.create(module_code = mod_code, module_title="First module", scenario_ref=scenario_1, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1)
        module_2 = Module.objects.create(module_code = mod_code+"_2", module_title="second module", scenario_ref=scenario_1, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1)
        lecturer_1 = Lecturer.objects.create(name="lecturer_1", fraction_appointment = 0.7, employment_track=track_1, workload_scenario = scenario_1, service_role = service_role_1)
        lecturer_2 = Lecturer.objects.create(name="lecturer_2", fraction_appointment = 0.7, employment_track=track_1, workload_scenario = scenario_1, service_role = service_role_1)
        self.assertEqual(CanUserAdminThisDepartment(uni_super_user.id, new_dept.id+1258, is_super_user = True), False) #coverage of wrong dept number
        self.assertEqual(CanUserAdminThisModule(uni_super_user.id, module_code = mod_code+'hello', is_super_user = True), False) #coverage of wrong module code
        self.assertEqual(CanUserAdminThisDepartment(uni_super_user.id, new_dept.id, is_super_user = True), True)

        fac_admin = User.objects.create_user('new_fac_admin_user', 'test@fuser.com', 'test_fac_admin_user_password')
        fac_admin.is_superuser = False
        fac_admin.save()
        #create realistic group
        fac_admin_gr = Group.objects.create(name = 'FacultyAdminStaff')
        fac_admin.groups.add(fac_admin_gr) #add user to group
        #Simulate creation with None Dept and None Faculty (should return error text)
        uni_fac_admin = UniversityStaff.objects.create(user = fac_admin, department=None,faculty=None)
        custom_error_message = "my error message"
        self.assertEqual(DetermineUserHomePage(uni_fac_admin.id, error_text = custom_error_message), custom_error_message)
        self.assertEqual(CanUserAdminThisDepartment(uni_fac_admin.id, new_dept.id), False)#No faculty assigned yet....
        self.assertEqual(CanUserAdminThisModule(uni_fac_admin.id, mod_code), False)
        #Now assign the faculty
        uni_fac_admin.faculty = new_fac
        uni_fac_admin.save()
        self.assertEqual(DetermineUserHomePage(uni_fac_admin.id, error_text = custom_error_message), "/school_page/"+str(new_fac.id))
        self.assertEqual(CanUserAdminThisDepartment(uni_fac_admin.id, new_dept.id), True)#Now assigned proper faculty
        self.assertEqual(CanUserAdminThisFaculty(uni_fac_admin.id, new_fac.id), True)#can admin its own faculty...
        self.assertEqual(CanUserAdminThisFaculty(uni_fac_admin.id, new_fac_2.id), False)#but not the otehr one...

        dept_admin = User.objects.create_user('new_dept_admin_user', 'test@duser.com', 'test_dept_admin_user_password')
        dept_admin.is_superuser = False
        dept_admin.save()
        #Create dept admin group
        dept_admin_group = Group.objects.create(name = 'DepartmentAdminStaff')
        dept_admin.groups.add(dept_admin_group)
        #Create a uni dept admin user
        uni_dept_admin = UniversityStaff.objects.create(user = dept_admin, department=None,faculty=None)
        #NOW this dept admin has both faculty and dept as None. Should thrpw error
        self.assertEqual(DetermineUserHomePage(uni_dept_admin.id, error_text = custom_error_message), custom_error_message)
        self.assertEqual(CanUserAdminThisDepartment(uni_dept_admin.id, new_dept.id), False)#No dept assigned yet....
        self.assertEqual(CanUserAdminThisModule(uni_dept_admin.id, mod_code), False)
        #assign faculty and department
        uni_dept_admin.faculty = new_fac
        uni_dept_admin.save()
        uni_dept_admin.department = new_dept
        uni_dept_admin.save()
        self.assertEqual(DetermineUserHomePage(uni_dept_admin.id, error_text = custom_error_message), '/department/'+str(new_dept.id))
        self.assertEqual(CanUserAdminThisDepartment(uni_dept_admin.id, new_dept.id), True)#Now assigned proper dept

        self.assertEqual(CanUserAdminThisModule(uni_dept_admin.id, mod_code), True)
        self.assertEqual(CanUserAdminThisModule(uni_fac_admin.id, mod_code), True)
        self.assertEqual(CanUserAdminThisModule(uni_super_user.id, mod_code, is_super_user = True), True)
        self.assertEqual(CanUserAdminThisFaculty(uni_dept_admin.id, new_fac.id), False)#dept admin can't manage faculty
        self.assertEqual(CanUserAdminThisFaculty(uni_dept_admin.id, new_fac_2.id), False)#dept admin can't manage faculty

        #Create a lecturer user
        lec_user = User.objects.create_user('new_lecturer_user', 'test@luser.com', 'test_lec_user_password')
        lec_user.is_superuser = False
        lec_user.save()
        #Create dept admin group
        lec_user_group = Group.objects.create(name = 'LecturerStaff')
        lec_user.groups.add(lec_user_group)
        #Create a uni lecturer user
        uni_lec_user = UniversityStaff.objects.create(user = lec_user, department=None,faculty=None,lecturer=None)
        self.assertEqual(DetermineUserHomePage(uni_lec_user.id, error_text = custom_error_message), custom_error_message)#Still no lecturer assigned
        uni_lec_user.faculty = new_fac
        uni_lec_user.save()
        uni_lec_user.department = new_dept
        uni_lec_user.save()
        uni_lec_user.lecturer = lecturer_1
        uni_lec_user.save()
        self.assertEqual(DetermineUserHomePage(uni_lec_user.id, error_text = custom_error_message), "/lecturer/"+str(lecturer_1.id))
        #Now we make a teaching assignment for lecturer_1 (associated with the user) to module 1
        teach_ass_1 = TeachingAssignment.objects.create(assigned_module = module_1, assigned_lecturer = lecturer_1, number_of_hours=39, workload_scenario=scenario_1)
        self.assertEqual(TeachingAssignment.objects.all().count(),1)
        #Now lecturer 1 should be able to admin module 1 but not module 2...
        self.assertEqual(CanUserAdminThisModule(uni_lec_user.id, mod_code), True)
        self.assertEqual(CanUserAdminThisModule(uni_lec_user.id, mod_code+"_2"), False)
        #... while faculy and dept admin shuld be able to admin both
        self.assertEqual(CanUserAdminThisModule(uni_dept_admin.id, mod_code), True)
        self.assertEqual(CanUserAdminThisModule(uni_fac_admin.id, mod_code), True)
        self.assertEqual(CanUserAdminUniversity(uni_fac_admin.id), False)
        self.assertEqual(CanUserAdminThisModule(uni_super_user.id, mod_code, is_super_user = True), True)
        self.assertEqual(CanUserAdminUniversity(uni_super_user.id, is_super_user = True), True)
        
        self.assertEqual(CanUserAdminThisModule(uni_dept_admin.id, mod_code+"_2"), True)
        self.assertEqual(CanUserAdminThisModule(uni_fac_admin.id, mod_code+"_2"), True)
        self.assertEqual(CanUserAdminThisModule(uni_super_user.id, mod_code+"_2", is_super_user = True), True)
        self.assertEqual(CanUserAdminUniversity(uni_dept_admin.id), False)
        #Check that the lecturer can't manage departments or faculties
        self.assertEqual(CanUserAdminThisDepartment(uni_lec_user.id, new_dept.id), False)
        self.assertEqual(CanUserAdminThisFaculty(uni_lec_user.id, new_fac.id), False)#dept admin can't manage faculty
        self.assertEqual(CanUserAdminThisFaculty(uni_lec_user.id, new_fac_2.id), False)#dept admin can't manage faculty
        self.assertEqual(CanUserAdminUniversity(uni_lec_user.id), False)
        
        #test faculty and department mismatch
        #Create one more faculty and one more dpet      
        new_fac_2 = Faculty.objects.create(faculty_name = 'test_fac_2', faculty_acronym = 'CDE_2')
        new_dept_2 = Department.objects.create(department_name = 'test_dept_2', department_acronym = 'BME_2', faculty = new_fac_2)
        uni_dept_admin.faculty = new_fac_2
        uni_dept_admin.save()
        uni_dept_admin.department = new_dept_2
        uni_dept_admin.save()
        uni_fac_admin.faculty = new_fac_2
        uni_fac_admin.save()

        #Now both dept admin and faculty admin have mismatched faculty and department belonging
        self.assertEqual(CanUserAdminThisDepartment(uni_dept_admin.id, new_dept.id), False)#Can't manage old dept
        self.assertEqual(CanUserAdminThisDepartment(uni_dept_admin.id, new_dept_2.id), True)#Can  manage new dept_2

        self.assertEqual(CanUserAdminThisDepartment(uni_fac_admin.id, new_dept.id), False)#Can't manage old dept
        self.assertEqual(CanUserAdminThisDepartment(uni_fac_admin.id, new_dept_2.id), True)#Can  manage new dept_2
        #And th e lecturer can't acces the new dept 2
        self.assertEqual(CanUserAdminThisDepartment(uni_lec_user.id, new_dept_2.id), False)

        #tests for the user menu method
        super_user_menu = DetermineUserMenu(uni_super_user.id,is_super_user=True)
        self.assertEqual(len(super_user_menu["departments"]),2)
        self.assertEqual(len(super_user_menu["accreditations"]),1)
        self.assertEqual(len(super_user_menu["lecturers"]),2)
        self.assertEqual(len(super_user_menu["courses"]),2)
        self.assertEqual(super_user_menu["departments"][0]["label"],"test_dept")
        self.assertEqual(super_user_menu["departments"][0]["url"],"/department/"+str(new_dept.id))
        self.assertEqual(super_user_menu["departments"][1]["label"],"test_dept_2")
        self.assertEqual(super_user_menu["departments"][1]["url"],"/department/"+str(new_dept_2.id))
        self.assertEqual(super_user_menu["accreditations"][0]["label"],"test_prog")
        self.assertEqual(super_user_menu["accreditations"][0]["url"],"/accreditation/"+str(new_prog.id))
        self.assertEqual(super_user_menu["lecturers"][0]["label"],"lecturer_1")
        self.assertEqual(super_user_menu["lecturers"][0]["url"],"/lecturer_page/"+str(lecturer_1.id))
        self.assertEqual(super_user_menu["lecturers"][1]["label"],"lecturer_2")
        self.assertEqual(super_user_menu["lecturers"][1]["url"],"/lecturer_page/"+str(lecturer_2.id))
        self.assertEqual(super_user_menu["courses"][0]["label"],mod_code)
        self.assertEqual(super_user_menu["courses"][0]["url"],"/module/"+str(mod_code))
        self.assertEqual(super_user_menu["courses"][1]["label"],mod_code + "_2")
        self.assertEqual(super_user_menu["courses"][1]["url"],"/module/"+str(mod_code + "_2"))

        
        uni_dept_admin.faculty = new_fac
        uni_dept_admin.save()
        uni_dept_admin.department = new_dept
        uni_dept_admin.save()
        uni_fac_admin.faculty = new_fac
        uni_fac_admin.save()
        faculty_user_menu = DetermineUserMenu(uni_fac_admin.id,is_super_user=False)
        self.assertEqual(len(faculty_user_menu["departments"]),1)
        self.assertEqual(len(faculty_user_menu["accreditations"]),1)
        self.assertEqual(len(faculty_user_menu["lecturers"]),2)
        self.assertEqual(len(faculty_user_menu["courses"]),2)
        self.assertEqual(faculty_user_menu["departments"][0]["label"],"test_dept")
        self.assertEqual(faculty_user_menu["departments"][0]["url"],"/department/"+str(new_dept.id))
        self.assertEqual(faculty_user_menu["accreditations"][0]["label"],"test_prog")
        self.assertEqual(faculty_user_menu["accreditations"][0]["url"],"/accreditation/"+str(new_prog.id))
        self.assertEqual(faculty_user_menu["lecturers"][0]["label"],"lecturer_1")
        self.assertEqual(faculty_user_menu["lecturers"][0]["url"],"/lecturer_page/"+str(lecturer_1.id))
        self.assertEqual(faculty_user_menu["lecturers"][1]["label"],"lecturer_2")
        self.assertEqual(faculty_user_menu["lecturers"][1]["url"],"/lecturer_page/"+str(lecturer_2.id))
        self.assertEqual(faculty_user_menu["courses"][0]["label"],mod_code)
        self.assertEqual(faculty_user_menu["courses"][0]["url"],"/module/"+str(mod_code))
        self.assertEqual(faculty_user_menu["courses"][1]["label"],mod_code + "_2")
        self.assertEqual(faculty_user_menu["courses"][1]["url"],"/module/"+str(mod_code + "_2"))

        dept_user_menu = DetermineUserMenu(uni_dept_admin.id,is_super_user=False)
        self.assertEqual(len(dept_user_menu["departments"]),1)
        self.assertEqual(len(dept_user_menu["accreditations"]),1)
        self.assertEqual(len(dept_user_menu["lecturers"]),2)
        self.assertEqual(len(dept_user_menu["courses"]),2)
        self.assertEqual(dept_user_menu["departments"][0]["label"],"test_dept")
        self.assertEqual(dept_user_menu["departments"][0]["url"],"/department/"+str(new_dept.id))
        self.assertEqual(dept_user_menu["accreditations"][0]["label"],"test_prog")
        self.assertEqual(dept_user_menu["accreditations"][0]["url"],"/accreditation/"+str(new_prog.id))
        self.assertEqual(dept_user_menu["lecturers"][0]["label"],"lecturer_1")
        self.assertEqual(dept_user_menu["lecturers"][0]["url"],"/lecturer_page/"+str(lecturer_1.id))
        self.assertEqual(dept_user_menu["lecturers"][1]["label"],"lecturer_2")
        self.assertEqual(dept_user_menu["lecturers"][1]["url"],"/lecturer_page/"+str(lecturer_2.id))
        self.assertEqual(dept_user_menu["courses"][0]["label"],mod_code)
        self.assertEqual(dept_user_menu["courses"][0]["url"],"/module/"+str(mod_code))
        self.assertEqual(dept_user_menu["courses"][1]["label"],mod_code + "_2")
        self.assertEqual(dept_user_menu["courses"][1]["url"],"/module/"+str(mod_code + "_2"))

        #Assign module_1 (but not module_2) to lecturer_1
        teach_ass_1 = TeachingAssignment.objects.create(assigned_module = module_1, assigned_lecturer = lecturer_1, number_of_hours=39, workload_scenario=scenario_1)
        lect_user_menu = DetermineUserMenu(uni_lec_user.id,is_super_user=False)
        self.assertEqual(len(lect_user_menu["departments"]),0)
        self.assertEqual(len(lect_user_menu["accreditations"]),0)
        self.assertEqual(len(lect_user_menu["lecturers"]),1)
        self.assertEqual(len(lect_user_menu["courses"]),1)
        self.assertEqual(lect_user_menu["lecturers"][0]["label"],"lecturer_1")
        self.assertEqual(lect_user_menu["lecturers"][0]["url"],"/lecturer_page/"+str(lecturer_1.id))
        self.assertEqual(lect_user_menu["courses"][0]["label"],mod_code)
        self.assertEqual(lect_user_menu["courses"][0]["url"],"/module/"+str(mod_code))

    def testSuperUserPageAccess(self):
        #Create fauclty, dept, programmes and modules
        new_fac = Faculty.objects.create(faculty_name = 'test_fac', faculty_acronym = 'CDE')
        new_fac_2 = Faculty.objects.create(faculty_name = 'test_fac2', faculty_acronym = 'CDE2')
        new_dept = Department.objects.create(department_name = 'test_dept', department_acronym = 'BME', faculty = new_fac)
        new_dept_2 = Department.objects.create(department_name = 'test_dept2', department_acronym = 'BME2', faculty = new_fac_2)
        new_prog = ProgrammeOffered.objects.create(programme_name = "new_prog",primary_dept=new_dept)
        new_prog_2 = ProgrammeOffered.objects.create(programme_name = "new_prog2",primary_dept=new_dept_2)

        def_labels = DetermineSurveyLabelsForProgramme(new_prog.id)#This will set the labels by default in the programme object
        #Create modules
        mod_code = "BN2102"
        acad_year_1 = Academicyear.objects.create(start_year=2021)
        acad_year_2 = Academicyear.objects.create(start_year=2022)
        scenario_1 = WorkloadScenario.objects.create(label="scenario_1", academic_year = acad_year_1, dept = new_dept, status = WorkloadScenario.OFFICIAL)
        scenario_2 = WorkloadScenario.objects.create(label="scenario_1", academic_year = acad_year_1, dept = new_dept_2, status = WorkloadScenario.OFFICIAL)
        mod_type_1 = ModuleType.objects.create(type_name = "one type")
        track_1 = EmploymentTrack.objects.create(track_name = "track_1", track_adjustment = 2.0, is_adjunct = False,faculty=new_fac)
        track_2 = EmploymentTrack.objects.create(track_name = "track_2", track_adjustment = 2.0, is_adjunct = False,faculty=new_fac_2)
        service_role_1 = ServiceRole.objects.create(role_name = "role_1", role_adjustment = 2.0, faculty=new_fac)
        service_role_2 = ServiceRole.objects.create(role_name = "role_2", role_adjustment = 2.0, faculty=new_fac_2)
        module_1 = Module.objects.create(module_code = mod_code, module_title="First module", \
                                         scenario_ref=scenario_1, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1,\
                                         primary_programme = new_prog)
        module_2 = Module.objects.create(module_code = mod_code+"_2", module_title="second module", scenario_ref=scenario_2, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1)
        lecturer_1 = Lecturer.objects.create(name="lecturer_1", fraction_appointment = 0.7, employment_track=track_1, workload_scenario = scenario_1, service_role = service_role_1)
        lecturer_2 = Lecturer.objects.create(name="lecturer_2", fraction_appointment = 0.7, employment_track=track_2, workload_scenario = scenario_2, service_role = service_role_2)
        
        #Make a teaching assignment of lecturer 1 to module 1
        teach_ass_1 = TeachingAssignment.objects.create(assigned_module = module_1, assigned_lecturer = lecturer_1, number_of_hours=39, workload_scenario=scenario_1)
        #Now create an SLO and an SLO survey
        slo_1 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_1', \
                                                      slo_short_description = 'slo_1', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'a',
                                                      cohort_valid_from = acad_year_1,
                                                      cohort_valid_to = acad_year_2,
                                                      programme = new_prog)
        mlo_1 = ModuleLearningOutcome.objects.create(mlo_description = "hello1", mlo_short_description = 'h4', module_code = mod_code,\
            mlo_valid_from = acad_year_1, mlo_valid_to = acad_year_2)
        
        slo_survey_1 = Survey.objects.create(survey_title = "first slo survey", opening_date = datetime.datetime(2012, 5, 17),\
                                                                        closing_date = datetime.datetime(2013, 5, 17),\
                                                                        cohort_targeted = acad_year_1,\
                                                                        programme_associated = new_prog,\
                                                                        likert_labels = def_labels["slo_survey_labels_object"],\
                                                                        survey_type = Survey.SurveyType.SLO,\
                                                                        max_respondents = 100)
        
        mlo_survey_1 = Survey.objects.create(survey_title = "first mlo survey", opening_date = datetime.datetime(2012, 5, 17),\
                                                                        closing_date = datetime.datetime(2013, 5, 17),\
                                                                        cohort_targeted = acad_year_1,\
                                                                        programme_associated = new_prog,\
                                                                        likert_labels = def_labels["slo_survey_labels_object"],\
                                                                        survey_type = Survey.SurveyType.MLO,\
                                                                        max_respondents = 100)
        #These ones is for Prog_2 of Dept_2 of faculty_2
        slo_survey_2 = Survey.objects.create(survey_title = "first slo survey", opening_date = datetime.datetime(2012, 5, 17),\
                                                                        closing_date = datetime.datetime(2013, 5, 17),\
                                                                        cohort_targeted = acad_year_1,\
                                                                        programme_associated = new_prog_2,\
                                                                        likert_labels = def_labels["slo_survey_labels_object"],\
                                                                        survey_type = Survey.SurveyType.SLO,\
                                                                        max_respondents = 100)
        mlo_survey_2 = Survey.objects.create(survey_title = "second mlo survey", opening_date = datetime.datetime(2012, 5, 17),\
                                                                        closing_date = datetime.datetime(2013, 5, 17),\
                                                                        cohort_targeted = acad_year_1,\
                                                                        programme_associated = new_prog_2,\
                                                                        likert_labels = def_labels["slo_survey_labels_object"],\
                                                                        survey_type = Survey.SurveyType.MLO,\
                                                                        max_respondents = 100)
        

    
        ####################
        ##SUPER  USER ACCESS
        ####################  
        sup_user = User.objects.create_user('new_super_user', 'test@user.com', 'test_super_user_password')
        sup_user.is_superuser = True
        sup_user.save()
        uni_super_user = UniversityStaff.objects.create(user = sup_user, department=None,faculty=None)
        self.client.login(username='new_super_user', password='test_super_user_password')
        #Workloads index page access
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        #Workload sceanrio page access
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["name_of_active_scenario"],"scenario_1")
        #module pages  access
        response = self.client.get(reverse('workload_app:module',  kwargs={'module_code': mod_code}))
        self.assertEqual(response.status_code, 200) #no issues
        self.assertEqual(response.context["module_title"], "First module")
        self.assertEqual(response.context["module_code"], mod_code)
        response = self.client.get(reverse('workload_app:module',  kwargs={'module_code': mod_code+"_2"}))
        self.assertEqual(response.status_code, 200) #no issues
        self.assertEqual(response.context["module_title"], "second module")
        self.assertEqual(response.context["module_code"], mod_code+"_2")
        #Department page  access
        response = self.client.get(reverse('workload_app:department', kwargs={'department_id': new_dept.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["dept_name"], "test_dept")
        #Accreditation page  access
        response = self.client.get(reverse('workload_app:accreditation', kwargs={'programme_id': new_prog.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["programme_name"], "new_prog")
        #accreditation report page access
        response = self.client.get(reverse('workload_app:accreditation_report', kwargs={'programme_id': new_prog.id, 'start_year' : 2020, 'end_year':2021}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["programme_name"], "new_prog")
        #Lecturer page access 
        response = self.client.get(reverse('workload_app:lecturer_page', kwargs={'lecturer_id': lecturer_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["lec_name"], "lecturer_1")
        #Survey results page access
        response = self.client.get(reverse('workload_app:survey_results', kwargs={'survey_id': slo_survey_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('survey_details' in response.context), True)
        #Programme survey input page access
        response = self.client.get(reverse('workload_app:input_programme_survey_results', kwargs={'programme_id': new_prog.id, 'survey_id': slo_survey_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["programme_id"], new_prog.id)
        #Module survey input page access
        response = self.client.get(reverse('workload_app:input_module_survey_results', kwargs={'module_code': mod_code, 'survey_id': mlo_survey_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["module_code"], mod_code)

        self.client.logout()

        #Groups to be tested mirroring real db
        #superuser (done above)
        #DepartmentAdminStaff
	    #FacultyAdminStaff
	    #LecturerStaff

        fac_admins =  Group.objects.create(name="FacultyAdminStaff")
        dept_admins =  Group.objects.create(name="DepartmentAdminStaff")
        lecturers = Group.objects.create(name="LecturerStaff")

        #######################
        ####FACULTY ADMIN TESTS
        #######################
        fac_admin = User.objects.create_user('new_fac_admin', 'test@fac_user.com', 'fac_super_user_password')
        fac_admin.is_superuser = False
        fac_admin.groups.add(fac_admins)
        fac_admin.save()
        uni_fac_admin = UniversityStaff.objects.create(user = fac_admin, department=new_dept,faculty=new_fac)
        self.client.login(username='new_fac_admin', password='fac_super_user_password')
        
        #Workloads index page access - NO ACCESS - send user to error page
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #
        self.assertEqual(('error_message' in response.context), True) #
        #Faculty  page access
        response = self.client.get(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["school_name"],new_fac.faculty_name)
        #Try with another faculty - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac_2.id}))
        self.assertEqual(('error_message' in response.context), True)

        #Workload scenario page access
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["name_of_active_scenario"],"scenario_1")
        #Try with another workload scenario of another department of ANOTHER FACULTY. SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(('error_message' in response.context), True)

        #module pages  access
        response = self.client.get(reverse('workload_app:module',  kwargs={'module_code': mod_code}))
        self.assertEqual(response.status_code, 200) #no issues
        self.assertEqual(response.context["module_title"], "First module")
        self.assertEqual(response.context["module_code"], mod_code)
        #Try with the module of another dept of another faculty - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:module',  kwargs={'module_code': mod_code+"_2"}))
        self.assertEqual(response.status_code, 200) #no issues
        self.assertEqual(('error_message' in response.context), True)

        #Department page  access
        response = self.client.get(reverse('workload_app:department', kwargs={'department_id': new_dept.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["dept_name"], "test_dept")
        #Try with another department of ANOTHER FACULTY. SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:department', kwargs={'department_id': new_dept_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)

        #Accreditation page  access
        response = self.client.get(reverse('workload_app:accreditation', kwargs={'programme_id': new_prog.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["programme_name"], "new_prog")
        #Accreditation of programme of ANOTHE dept of ANOTHER faculty - NO access
        response = self.client.get(reverse('workload_app:accreditation', kwargs={'programme_id': new_prog_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)       

        #accreditation report page access
        response = self.client.get(reverse('workload_app:accreditation_report', kwargs={'programme_id': new_prog.id, 'start_year' : 2020, 'end_year':2021}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["programme_name"], "new_prog")
        #Accreditation report of programme of ANOTHE dept of ANOTHER faculty - NO access
        response = self.client.get(reverse('workload_app:accreditation_report', kwargs={'programme_id': new_prog_2.id, 'start_year' : 2020, 'end_year':2021}))
        self.assertEqual(('error_message' in response.context), True)   
        
        #Lecturer page access 
        response = self.client.get(reverse('workload_app:lecturer_page', kwargs={'lecturer_id': lecturer_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["lec_name"], "lecturer_1")
        #Lecturer page of another lecturer from another department of another faculty - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:lecturer_page', kwargs={'lecturer_id': lecturer_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)

        #Survey results page access
        response = self.client.get(reverse('workload_app:survey_results', kwargs={'survey_id': slo_survey_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), False)
        #Now another survey of anothe programe of another faculty - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:survey_results', kwargs={'survey_id': slo_survey_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)

        #Programme survey input page access
        response = self.client.get(reverse('workload_app:input_programme_survey_results', kwargs={'programme_id': new_prog.id, 'survey_id': slo_survey_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["programme_id"], new_prog.id)
        #Programme survey input of ANOTHER programme of ANOTHER FACULTY - NO ACCESS
        response = self.client.get(reverse('workload_app:input_programme_survey_results', kwargs={'programme_id': new_prog_2.id, 'survey_id': slo_survey_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)
        
        #Module survey input page access
        response = self.client.get(reverse('workload_app:input_module_survey_results', kwargs={'module_code': mod_code, 'survey_id': mlo_survey_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["module_code"], mod_code)
        #Now input into a survey of a module of ANOTHER faculty - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:input_module_survey_results', kwargs={'module_code': mod_code+"_2", 'survey_id': mlo_survey_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)

        self.client.logout()

        #######################
        ####DEPT ADMIN TESTS
        #######################
        dept_admin = User.objects.create_user('new_dept_admin', 'test@dept_user.com', 'dept_super_user_password')
        dept_admin.is_superuser = False
        dept_admin.groups.add(dept_admins)
        dept_admin.save()
        uni_dept_admin = UniversityStaff.objects.create(user = dept_admin, department=new_dept,faculty=new_fac)
        self.client.login(username='new_dept_admin', password='dept_super_user_password')
        
        #Workloads index page access - NO ACCESS - send user to error page
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #
        self.assertEqual(('error_message' in response.context), True) #
        #Faculty  page access - NO ACCESS - This is a dept admin
        response = self.client.get(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)
        #Try with another faculty - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)

        #Workload scenario page access
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["name_of_active_scenario"],"scenario_1")
        #Try with another workload scenario of another department of ANOTHER FACULTY. SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(('error_message' in response.context), True)

        #module pages  access
        response = self.client.get(reverse('workload_app:module',  kwargs={'module_code': mod_code}))
        self.assertEqual(response.status_code, 200) #no issues
        self.assertEqual(response.context["module_title"], "First module")
        self.assertEqual(response.context["module_code"], mod_code)
        #Try with the module of another dept of another faculty - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:module',  kwargs={'module_code': mod_code+"_2"}))
        self.assertEqual(response.status_code, 200) #no issues
        self.assertEqual(('error_message' in response.context), True)

        #Department page  access
        response = self.client.get(reverse('workload_app:department', kwargs={'department_id': new_dept.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["dept_name"], "test_dept")
        #Try with another department of ANOTHER FACULTY. SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:department', kwargs={'department_id': new_dept_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)

        #Accreditation page  access
        response = self.client.get(reverse('workload_app:accreditation', kwargs={'programme_id': new_prog.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["programme_name"], "new_prog")
        #Accreditation of programme of ANOTHE dept of ANOTHER faculty - NO access
        response = self.client.get(reverse('workload_app:accreditation', kwargs={'programme_id': new_prog_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)       

        #accreditation report page access
        response = self.client.get(reverse('workload_app:accreditation_report', kwargs={'programme_id': new_prog.id, 'start_year' : 2020, 'end_year':2021}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["programme_name"], "new_prog")
        #Accreditation report of programme of ANOTHE dept of ANOTHER faculty - NO access
        response = self.client.get(reverse('workload_app:accreditation_report', kwargs={'programme_id': new_prog_2.id, 'start_year' : 2020, 'end_year':2021}))
        self.assertEqual(('error_message' in response.context), True)   
        
        #Lecturer page access 
        response = self.client.get(reverse('workload_app:lecturer_page', kwargs={'lecturer_id': lecturer_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["lec_name"], "lecturer_1")
        #Lecturer page of another lecturer from another department of another faculty - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:lecturer_page', kwargs={'lecturer_id': lecturer_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)

        #Survey results page access
        response = self.client.get(reverse('workload_app:survey_results', kwargs={'survey_id': slo_survey_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), False)
        #Now another survey of anothe programe of another faculty - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:survey_results', kwargs={'survey_id': slo_survey_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)

        #Programme survey input page access
        response = self.client.get(reverse('workload_app:input_programme_survey_results', kwargs={'programme_id': new_prog.id, 'survey_id': slo_survey_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["programme_id"], new_prog.id)
        #Programme survey input of ANOTHER programme of ANOTHER FACULTY - NO ACCESS
        response = self.client.get(reverse('workload_app:input_programme_survey_results', kwargs={'programme_id': new_prog_2.id, 'survey_id': slo_survey_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)
        
        #Module survey input page access
        response = self.client.get(reverse('workload_app:input_module_survey_results', kwargs={'module_code': mod_code, 'survey_id': mlo_survey_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["module_code"], mod_code)
        #Now input into a survey of a module of ANOTHER faculty - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:input_module_survey_results', kwargs={'module_code': mod_code+"_2", 'survey_id': mlo_survey_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)

        self.client.logout()

        #######################
        ####Lecturer TESTS
        #######################
        lect = User.objects.create_user('new_lecturer', 'test@lec_user.com', 'lec_user_password')
        lect.is_superuser = False
        lect.groups.add(lecturers)
        lect.save()
        uni_lec = UniversityStaff.objects.create(user = lect, department=new_dept,faculty=new_fac,lecturer=lecturer_1)
        self.client.login(username='new_lecturer', password='lec_user_password')
        
        #Workloads index page access - NO ACCESS - send user to error page
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #
        self.assertEqual(('error_message' in response.context), True) #
        #Faculty  page access - NO ACCESS - This is a dept admin
        response = self.client.get(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)
        #Try with another faculty - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)

        #Workload scenario page access - Should be no access
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)
        #Try with another workload scenario of another department of ANOTHER FACULTY. SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)

        #module pages  access
        response = self.client.get(reverse('workload_app:module',  kwargs={'module_code': mod_code}))
        self.assertEqual(response.status_code, 200) #no issues
        self.assertEqual(response.context["module_title"], "First module")
        self.assertEqual(response.context["module_code"], mod_code)
        #Try with the module of another dept of another faculty - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:module',  kwargs={'module_code': mod_code+"_2"}))
        self.assertEqual(response.status_code, 200) #no issues
        self.assertEqual(('error_message' in response.context), True)

        #Department page  access - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:department', kwargs={'department_id': new_dept.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)
        #Try with another department of ANOTHER FACULTY. SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:department', kwargs={'department_id': new_dept_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)

        #Accreditation page  access - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:accreditation', kwargs={'programme_id': new_prog.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True) 
        #Accreditation of programme of ANOTHE dept of ANOTHER faculty - NO access
        response = self.client.get(reverse('workload_app:accreditation', kwargs={'programme_id': new_prog_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)       

        #accreditation report page access - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:accreditation_report', kwargs={'programme_id': new_prog.id, 'start_year' : 2020, 'end_year':2021}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)
        #Accreditation report of programme of ANOTHE dept of ANOTHER faculty - NO access
        response = self.client.get(reverse('workload_app:accreditation_report', kwargs={'programme_id': new_prog_2.id, 'start_year' : 2020, 'end_year':2021}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)   
        
        #Lecturer page access 
        response = self.client.get(reverse('workload_app:lecturer_page', kwargs={'lecturer_id': lecturer_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["lec_name"], "lecturer_1")
        #Lecturer page of another lecturer from another department of another faculty - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:lecturer_page', kwargs={'lecturer_id': lecturer_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)

        #Survey results page access - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:survey_results', kwargs={'survey_id': slo_survey_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)
        #Now another survey of anothe programe of another faculty - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:survey_results', kwargs={'survey_id': slo_survey_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)

        #Survey results page access for MLO of his/her own mod -> OK access
        response = self.client.get(reverse('workload_app:survey_results', kwargs={'survey_id': mlo_survey_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), False)

        #Programme survey input page access -S SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:input_programme_survey_results', kwargs={'programme_id': new_prog.id, 'survey_id': slo_survey_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)
        #Programme survey input of ANOTHER programme of ANOTHER FACULTY - NO ACCESS
        response = self.client.get(reverse('workload_app:input_programme_survey_results', kwargs={'programme_id': new_prog_2.id, 'survey_id': slo_survey_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)
      
        #Module survey input page access
        response = self.client.get(reverse('workload_app:input_module_survey_results', kwargs={'module_code': mod_code, 'survey_id': mlo_survey_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["module_code"], mod_code)
        #Now input into a survey of a module of ANOTHER faculty - SHOULD BE NO ACCESS
        response = self.client.get(reverse('workload_app:input_module_survey_results', kwargs={'module_code': mod_code+"_2", 'survey_id': mlo_survey_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(('error_message' in response.context), True)

        self.client.logout()