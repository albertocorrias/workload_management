import os
from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *
from workload_app.models import Lecturer, Module, TeachingAssignment,WorkloadScenario,\
                                ModuleType,Department, EmploymentTrack, ServiceRole, Faculty,Academicyear, \
                                ProgrammeOffered, SubProgrammeOffered, UniversityStaff, Faculty
from workload_app.global_constants import MAX_NUMBER_OF_CHARACTERS_IN_TABLE_CELL, DEFAULT_TRACK_NAME, ShortenString,\
    CalculateNumHoursBasedOnWeeklyInfo,csv_file_type, DEFAULT_DEPARTMENT_NAME,requested_table_type
from workload_app.helper_methods import CalculateTotalModuleHours, RegularizeName,CalculateEmploymentTracksTable,CalculateServiceRolesTable,\
                                         CalculateDepartmentTable, CalculateModuleTypesTableForProgramme, CalculateModuleHourlyTableForProgramme,\
                                         CalculateSingleModuleInformationTable, ReadInCsvFile

# Helper method for tests
def create_lecturer(lec_name, appt,adj):
    return Lecturer.objects.create(name=lec_name,fraction_appointment=appt);


class testHelperMethods(TestCase):
    def setup_user(self):
        #The test client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
        self.user.is_superuser = True
        self.user.save()
        uni_user = UniversityStaff.objects.create(user = self.user, department=None,faculty=None)

    def test_workload_tables(self):
        '''This test creates 3 profs and assign them to 3 modules. 
           It checks the generation of the tables by the helper methods
           and other variables passed to the HTML page'''
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        new_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
         
        #Create a new scenario
        first_label = 'test_scen'
        first_scen = WorkloadScenario.objects.create(label=first_label, dept=new_dept)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues

        #create two tracks
        track_1 = EmploymentTrack.objects.create(track_name = "track_1", track_adjustment = 2.0, faculty=new_fac)
        track_2 = EmploymentTrack.objects.create(track_name = "track_2", track_adjustment = 0.0, faculty=new_fac)

        normal_lecturer = Lecturer.objects.create(name="normal_lecturer", fraction_appointment = 0.7 )
        educator_track = Lecturer.objects.create(name="educator_track", fraction_appointment = 1.0, employment_track=track_1)
        vice_dean = Lecturer.objects.create(name="vice dean", fraction_appointment = 0.5  , employment_track=track_2)

        #Create a module type
        mod_type_name = "TEST_MOD_TYPE"
        mod_type_1 = ModuleType.objects.create(type_name=mod_type_name, department =new_dept )

        #create a Programme
        prog_name = "test prog"
        prog = ProgrammeOffered.objects.create(programme_name = prog_name, primary_dept = new_dept)

        mod_code_1 = 'AS101'
        mod_code_2 = 'AS201'
        mod_code_3 = 'AS301'
        
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': first_scen.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '52', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '1',  'primary_programme' : prog.id, 'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': first_scen.id}), {'module_code': mod_code_2, 'module_title' : 'module 2', 'total_hours' : '52', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '1',  'primary_programme' : prog.id, 'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': first_scen.id}), {'module_code': mod_code_3, 'module_title' : 'module 3', 'total_hours' : '52', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '1',  'primary_programme' : prog.id, 'fresh_record' : True})    
         
        self.assertEqual(Module.objects.all().count(),3)
        
        module_1 = Module.objects.filter(module_code = mod_code_1).get()
        module_2 = Module.objects.filter(module_code = mod_code_2).get()
        module_3 = Module.objects.filter(module_code = mod_code_3).get()
        
        #List of assignemnt and scenarios will still be zero
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
        empty_assign_list = TeachingAssignment.objects.all()
        self.assertEqual(empty_assign_list.count(),0)
        
        #Before making any teaching assignment, we test the default strings of the two table-generating helper methods
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        obtained_wl_table = response.context['wl_table']
        obtained_module_table = response.context['mod_table']
        self.assertEqual(len(obtained_wl_table),3)
        self.assertEqual(len(obtained_module_table),3)
        
        self.assertEqual(obtained_wl_table[0]["assignments"],"No teaching assignments")
        self.assertEqual(obtained_module_table[0]["module_lecturers"],"No lecturer assigned")
        self.assertEqual(obtained_wl_table[1]["assignments"],"No teaching assignments")
        self.assertEqual(obtained_module_table[1]["module_lecturers"],"No lecturer assigned")
        self.assertEqual(obtained_wl_table[2]["assignments"],"No teaching assignments")
        self.assertEqual(obtained_module_table[2]["module_lecturers"],"No lecturer assigned")
        ########################
        
        #Module one is assigned to 3 lecturers
        TeachingAssignment.objects.create(assigned_module=module_1,assigned_lecturer=normal_lecturer,number_of_hours=30, counted_towards_workload = True, workload_scenario=first_scen)
        TeachingAssignment.objects.create(assigned_module=module_1,assigned_lecturer=educator_track,number_of_hours=10, counted_towards_workload = True, workload_scenario=first_scen)
        TeachingAssignment.objects.create(assigned_module=module_1,assigned_lecturer=vice_dean,number_of_hours=12, workload_scenario=first_scen) #Counted towards workload is not mentioned to cover the default "true" value
        
        #Module two is assigned to one only
        TeachingAssignment.objects.create(assigned_module=module_2,assigned_lecturer=educator_track,number_of_hours=52, counted_towards_workload = True, workload_scenario=first_scen)
        
        #Module 3 is assigned to the vice dean, partially
        TeachingAssignment.objects.create(assigned_module=module_3,assigned_lecturer=vice_dean,number_of_hours=20, counted_towards_workload = True, workload_scenario=first_scen)
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        
        ###################################################
        # Check some context variable passed to the HTML
        ###################################################
        obtained_profs_list = Lecturer.objects.all()
        self.assertEqual(obtained_profs_list.count(),3)
        self.assertEqual(obtained_profs_list.filter(name='normal_lecturer').exists(),True)
        self.assertEqual(obtained_profs_list.filter(name='educator_track').exists(),True)
        self.assertEqual(obtained_profs_list.filter(name='vice dean').exists(),True)
        
        ###################################################
        # Check the workload table generated by the helper method
        ###################################################
        obtained_wl_table = response.context['wl_table']
        self.assertEqual(len(obtained_wl_table),3)
        #Check lecturer name
        self.assertEqual(obtained_wl_table[0]["prof_name"],"educator_track")
        self.assertEqual(obtained_wl_table[1]["prof_name"],"normal_lecturer")
        self.assertEqual(obtained_wl_table[2]["prof_name"],"vice dean")
        
        #Check first lecturer (educator track), all fields
        self.assertEqual(obtained_wl_table[0]["assignments"],"AS101 (10), AS201 (52)")
        self.assertEqual(obtained_wl_table[0]["total_hours_for_prof"],62)
        self.assertAlmostEqual(obtained_wl_table[0]["prof_tfte"],Decimal(2.0))
        self.assertAlmostEqual(obtained_wl_table[0]["prof_expected_hours"],Decimal(((30+10+12+52+20)/2.7)*2.0))
        self.assertAlmostEqual(obtained_wl_table[0]["prof_balance"], float(obtained_wl_table[0]["total_hours_for_prof"]) - float(obtained_wl_table[0]["prof_expected_hours"]))
        
        #Check second lecturer (normal lecturer), all fields
        self.assertEqual(obtained_wl_table[1]["assignments"],"AS101 (30)")
        self.assertEqual(obtained_wl_table[1]["total_hours_for_prof"],30)
        self.assertAlmostEqual(obtained_wl_table[1]["prof_tfte"],Decimal(0.7))
        self.assertAlmostEqual(obtained_wl_table[1]["prof_expected_hours"],Decimal(((30+10+12+52+20)/2.7)*0.7))
        self.assertAlmostEqual(obtained_wl_table[1]["prof_balance"], float(obtained_wl_table[1]["total_hours_for_prof"]) - float(obtained_wl_table[1]["prof_expected_hours"]))

        #Check third lecturer, all fields
        self.assertEqual(obtained_wl_table[2]["assignments"],"AS101 (12), AS301 (20)")
        self.assertEqual(obtained_wl_table[2]["total_hours_for_prof"],32)
        self.assertAlmostEqual(obtained_wl_table[2]["prof_tfte"],Decimal(0.0))
        self.assertAlmostEqual(obtained_wl_table[2]["prof_expected_hours"],Decimal(((30+10+12+52+20)/2.7)*0.0))
        self.assertAlmostEqual(obtained_wl_table[2]["prof_balance"], float(obtained_wl_table[2]["total_hours_for_prof"]) - float(obtained_wl_table[2]["prof_expected_hours"]))

        ######################################################################
        #Now add another assignment, not to be counted in the workload hours
        ######################################################################
        TeachingAssignment.objects.create(assigned_module=module_2,assigned_lecturer=normal_lecturer,number_of_hours=752, counted_towards_workload = False, workload_scenario=first_scen)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
        #RE-check everything
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(TeachingAssignment.objects.all().count(), 6) #
        obtained_wl_table = response.context['wl_table']
        self.assertEqual(len(obtained_wl_table),3)
        #Check lecturer name
        self.assertEqual(obtained_wl_table[0]["prof_name"],"educator_track")
        self.assertEqual(obtained_wl_table[1]["prof_name"],"normal_lecturer")
        self.assertEqual(obtained_wl_table[2]["prof_name"],"vice dean")
        
        #Check first lecturer (educator track), all fields
        self.assertEqual(obtained_wl_table[0]["assignments"],"AS101 (10), AS201 (52)")
        self.assertEqual(obtained_wl_table[0]["not_counted_assignments"],"")
        self.assertEqual(obtained_wl_table[0]["not_counted_total_hours"],0)
        self.assertEqual(obtained_wl_table[0]["total_hours_for_prof"],62)#No change!!!!
        self.assertAlmostEqual(obtained_wl_table[0]["prof_tfte"],Decimal(2.0))
        self.assertAlmostEqual(obtained_wl_table[0]["prof_expected_hours"],Decimal(((30+10+12+52+20)/2.7)*2.0))#No change!!!!
        self.assertAlmostEqual(obtained_wl_table[0]["prof_balance"], float(obtained_wl_table[0]["total_hours_for_prof"]) - float(obtained_wl_table[0]["prof_expected_hours"]))
        
        #Check second lecturer (normal lecturer), all fields
        self.assertEqual(obtained_wl_table[1]["assignments"],"AS101 (30)")
        self.assertEqual(obtained_wl_table[1]["not_counted_assignments"],"AS201 (752)")
        self.assertEqual(obtained_wl_table[1]["not_counted_total_hours"],752)
        self.assertEqual(obtained_wl_table[1]["total_hours_for_prof"],30)#No change!!!!
        self.assertAlmostEqual(obtained_wl_table[1]["prof_tfte"],Decimal(0.7))
        self.assertAlmostEqual(obtained_wl_table[1]["prof_expected_hours"],Decimal(((30+10+12+52+20)/2.7)*0.7))#No change!!!!
        self.assertAlmostEqual(obtained_wl_table[1]["prof_balance"], float(obtained_wl_table[1]["total_hours_for_prof"]) - float(obtained_wl_table[1]["prof_expected_hours"]))

        #Check third lecturer, all fields
        self.assertEqual(obtained_wl_table[2]["assignments"],"AS101 (12), AS301 (20)")
        self.assertEqual(obtained_wl_table[2]["not_counted_assignments"],"")
        self.assertEqual(obtained_wl_table[2]["not_counted_total_hours"],0)
        self.assertEqual(obtained_wl_table[2]["total_hours_for_prof"],32)#No change!!!!
        self.assertAlmostEqual(obtained_wl_table[2]["prof_tfte"],Decimal(0.0))
        self.assertAlmostEqual(obtained_wl_table[2]["prof_expected_hours"],Decimal(((30+10+12+52+20)/2.7)*0.0))#No change!!!!
        self.assertAlmostEqual(obtained_wl_table[2]["prof_balance"], float(obtained_wl_table[2]["total_hours_for_prof"]) - float(obtained_wl_table[2]["prof_expected_hours"]))


        #########################################################
        #Check the module table generated by the helper method
        #########################################################
        obtained_module_table = response.context['mod_table']
        self.assertEqual(len(obtained_module_table),3)
        #Chcek positions 0 and 1
        self.assertEqual(obtained_module_table[0]["module_code"],"AS101")
        self.assertEqual(obtained_module_table[1]["module_code"],"AS201")
        self.assertEqual(obtained_module_table[2]["module_code"],"AS301")
        self.assertEqual(obtained_module_table[0]["module_title"],"module 1")
        self.assertEqual(obtained_module_table[1]["module_title"],"module 2")
        self.assertEqual(obtained_module_table[2]["module_title"],"module 3")
        
        #First mod
        self.assertEqual(obtained_module_table[0]["module_lecturers"],"educator_track (10), vice dean (12), normal_lecturer (30)")
        self.assertEqual(obtained_module_table[0]["module_assigned_hours"],10+12+30)
        self.assertEqual(obtained_module_table[0]["module_lecturers_not_counted"],"")
        self.assertEqual(obtained_module_table[0]["module_assigned_hours_not_counted"],0)
        
        self.assertEqual(obtained_module_table[0]["module_hours_needed"],52)
        self.assertEqual(obtained_module_table[0]["module_type"],mod_type_name)
        self.assertEqual(obtained_module_table[0]["num_tut_groups"],1)
        
        #second mod
        self.assertEqual(obtained_module_table[1]["module_lecturers"],"educator_track (52)")
        self.assertEqual(obtained_module_table[1]["module_assigned_hours"],52)
        self.assertEqual(obtained_module_table[1]["module_lecturers_not_counted"],"normal_lecturer (752)")
        self.assertEqual(obtained_module_table[1]["module_assigned_hours_not_counted"],752)
        
        self.assertEqual(obtained_module_table[1]["module_hours_needed"],52)
        self.assertEqual(obtained_module_table[1]["module_type"],mod_type_name)
        self.assertEqual(obtained_module_table[1]["num_tut_groups"],1)
        
        #third mod
        self.assertEqual(obtained_module_table[2]["module_lecturers"],"vice dean (20)")
        self.assertEqual(obtained_module_table[2]["module_assigned_hours"],20)
        self.assertEqual(obtained_module_table[2]["module_hours_needed"],52)
        self.assertEqual(obtained_module_table[2]["module_lecturers_not_counted"],"")
        self.assertEqual(obtained_module_table[2]["module_assigned_hours_not_counted"],0)
        self.assertEqual(obtained_module_table[2]["module_type"],mod_type_name)
        self.assertEqual(obtained_module_table[2]["num_tut_groups"],1)
     
        #########################################################
        #Check the list of lecturers table generated by the helper method (redundant, but we leave it here)
        #########################################################
        obtained_profs_list_table = response.context['wl_table']
        self.assertEqual(len(obtained_profs_list_table),3)#3 mods
        self.assertEqual(obtained_profs_list_table[1]["prof_name"],"normal_lecturer")
        self.assertEqual(obtained_profs_list_table[0]["prof_name"],"educator_track")
        self.assertEqual(obtained_profs_list_table[2]["prof_name"],"vice dean")
        self.assertEqual(obtained_profs_list_table[1]["no_space_name"],"normal_lecturer")
        self.assertEqual(obtained_profs_list_table[0]["no_space_name"],"educator_track")
        self.assertEqual(obtained_profs_list_table[2]["no_space_name"],"vicedean")
        self.assertEqual(obtained_profs_list_table[1]["num_assigns_for_prof"],2)#One is not counted
        self.assertEqual(obtained_profs_list_table[0]["num_assigns_for_prof"],2)
        self.assertEqual(obtained_profs_list_table[2]["num_assigns_for_prof"],2)
        
        #########################################################
        #Check the list of modules table generated by the helper method (redundnat, but we leave it here)
        #########################################################
        obtained_module_list_table = response.context['mod_table']
        self.assertEqual(len(obtained_module_list_table),3)#3 mods
        self.assertEqual(obtained_module_list_table[0]["module_code"],mod_code_1)
        self.assertEqual(obtained_module_list_table[1]["module_code"],mod_code_2)
        self.assertEqual(obtained_module_list_table[2]["module_code"],mod_code_3)
        self.assertEqual(obtained_module_list_table[0]["module_title"],'module 1')
        self.assertEqual(obtained_module_list_table[1]["module_title"],'module 2')
        self.assertEqual(obtained_module_list_table[2]["module_title"],'module 3')
        self.assertEqual(obtained_module_list_table[0]["num_assigns_for_module"],3)
        self.assertEqual(obtained_module_list_table[1]["num_assigns_for_module"],2)#One counted, one not counted
        self.assertEqual(obtained_module_list_table[2]["num_assigns_for_module"],1)
        
    def test_shorten_string(self):

        self.assertEqual(ShortenString("hello"),"hello")
        self.assertEqual(ShortenString(""),"")
        self.assertEqual(ShortenString(" ")," ")
        
        test_str_1 = "Hello, my name is Alberto"
        self.assertEqual(ShortenString(test_str_1),"Hello, my nam...erto")
        
        test_exactly_the_maximum = '*' * MAX_NUMBER_OF_CHARACTERS_IN_TABLE_CELL
        self.assertEqual(ShortenString(test_exactly_the_maximum),test_exactly_the_maximum)
        
        test_exactly_the_maximum_plus_one = '*' * (MAX_NUMBER_OF_CHARACTERS_IN_TABLE_CELL+1)
        self.assertEqual(ShortenString(test_exactly_the_maximum_plus_one),"*************...****")

    def test_regularize_name(self):
        self.assertEqual(RegularizeName("hello"),"hello")
        self.assertEqual(RegularizeName(""),"")
        self.assertEqual(RegularizeName(" "),"")
        self.assertEqual(RegularizeName("         "),"")
        
        test_str_1 = "Hello, my name is Alberto"
        self.assertEqual(RegularizeName(test_str_1),"HellomynameisAlberto")
        
        test_str_2 = "Bob builder"
        self.assertEqual(RegularizeName(test_str_2),"Bobbuilder")
        
        test_str_3 = "Bob builder        ";
        self.assertEqual(RegularizeName(test_str_3),"Bobbuilder")
        
        test_str_4 = "      Bob builder        ";
        self.assertEqual(RegularizeName(test_str_4),"Bobbuilder")
        
        test_str_5 = " B";
        self.assertEqual(RegularizeName(test_str_5),"B")
        
        test_str_6 = "B1 and C4";
        self.assertEqual(RegularizeName(test_str_6),"B1andC4")
        
        test_str_7 = "B1, and C4";
        self.assertEqual(RegularizeName(test_str_7),"B1andC4")
        
        test_str_8 = ",";
        self.assertEqual(RegularizeName(test_str_8),"")
        
        test_str_9 = "hello,hello,";
        self.assertEqual(RegularizeName(test_str_9),"hellohello")

        test_str_10 = "hello/hello";
        self.assertEqual(RegularizeName(test_str_10),"hellohello")
        
    def test_module_table_with_long_module_name(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        
        #response = self.client.get(reverse('workload_app:workloads_index'))
        #self.assertEqual(response.status_code, 200) #No issues
        #new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        #new_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        #Create a new scenario
        # first_label = 'test_scen'
        # first_scen = WorkloadScenario.objects.create(label=first_label,dept=new_dept)
        # response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
        # self.assertEqual(response.status_code, 200) #No issues
        
        # normal_lecturer = create_lecturer("normal_lecturer",0.7,1.0)
        # long_string = "This module has a very long title I"
        
        # mod_type_1 = ModuleType.objects.create(type_name="Core",departmant= new_dept)
        # mod_code_1 = 'AS101'
        # self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': first_scen.id}), {'module_code': mod_code_1, 'module_title' : long_string, 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    

        # long_module_1 = Module.objects.filter(module_code = mod_code_1).get() 

        # #List of assignemnt and scenarios will still be zero
        # self.assertEqual(TeachingAssignment.objects.all().count(),0)
        
        # #Module one is assigned to 3 lecturers
        # TeachingAssignment.objects.create(assigned_module=long_module_1,assigned_lecturer=normal_lecturer,number_of_hours=30, workload_scenario=first_scen)
        
        # response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
        # self.assertEqual(response.status_code, 200) #No issues
        # obtained_module_table = response.context['mod_table']
        # self.assertEqual(len(obtained_module_table),1)
        # self.assertEqual(obtained_module_table[0]["module_code"],"AS101")
        # self.assertEqual(obtained_module_table[0]["module_title"],ShortenString(long_string))
        
    # def test_workload_summary_method(self):
    #     self.setup_user()
    #     self.client.login(username='test_user', password='test_user_password')
    #     response = self.client.get(reverse('workload_app:workloads_index'))
    #     self.assertEqual(response.status_code, 200) #No issues
    #     first_fac = Faculty.objects.create(faculty_name = "first fac", faculty_acronym = "FRTE")
    #     first_dept = Department.objects.create(department_name = "noname", department_acronym="ACRN",faculty = first_fac)
    #     prog_1 = ProgrammeOffered.objects.create(programme_name = 'P1', primary_dept = first_dept)
    #     prog_2 = ProgrammeOffered.objects.create(programme_name = 'P2', primary_dept = first_dept)

    #     #Create a new scenario
    #     first_label = 'test_scen'
    #     first_scen = WorkloadScenario.objects.create(label=first_label, dept = first_dept)
    #     response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
    #     self.assertEqual(response.status_code, 200) #No issues

    #     empty_assign_list = TeachingAssignment.objects.all()
    #     self.assertEqual(empty_assign_list.count(),0)
        
    #     #First test the method with an empty database
    #     obtained_summary_data = response.context['summary_data']
    #     self.assertEqual(len(obtained_summary_data["module_type_labels"]),0)
    #     self.assertEqual(len(obtained_summary_data["hours_by_type"]),0)
    #     self.assertEqual(len(obtained_summary_data["labels_prog"]),0)
    #     self.assertEqual(len(obtained_summary_data["hours_prog"]),0)

    #     self.assertAlmostEqual(obtained_summary_data["total_tFTE_for_workload"],Decimal(0))#
    #     self.assertAlmostEqual(obtained_summary_data["total_department_tFTE"],Decimal(0))#
    #     self.assertAlmostEqual(obtained_summary_data["total_module_hours_for_dept"],Decimal(0))#
    #     self.assertAlmostEqual(obtained_summary_data["total_hours_for_workload"],Decimal(0))
    #     self.assertAlmostEqual(obtained_summary_data["expected_hours_per_tFTE"],Decimal(0))

    #     new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
    #     #Now create a realistic database
    #     #create two tracks
    #     track_1 = EmploymentTrack.objects.create(track_name = "track_1", track_adjustment = 2.0, is_adjunct = False, faculty=new_fac)
    #     track_2 = EmploymentTrack.objects.create(track_name = "track_2", track_adjustment = 3.0, is_adjunct = True, faculty=new_fac)

    #     normal_lecturer = Lecturer.objects.create(name="normal_lecturer", fraction_appointment = 0.7  )
    #     educator_track = Lecturer.objects.create(name="educator_track", fraction_appointment = 1.0, employment_track=track_1)
    #     vice_dean = Lecturer.objects.create(name="vice_dean", fraction_appointment = 0.5) #should use default employment track (adjustment 1, is_adjunct false)
    #     #...and we check, to make sure
    #     self.assertEqual(vice_dean.employment_track.track_adjustment,1)
    #     self.assertEqual(vice_dean.employment_track.is_adjunct,False)
    #     self.assertEqual(vice_dean.employment_track.track_name,DEFAULT_TRACK_NAME)

    #     adjunct_lecturer = Lecturer.objects.create(name="adjunct_lecturer", fraction_appointment = 0.5, employment_track=track_2)
    #     external_lecturer = Lecturer.objects.create(name="external", fraction_appointment = 0.8, employment_track = track_1, is_external = True)

    #     #Create module types
    #     mod_type_core = ModuleType.objects.create(type_name="Core", department = first_dept)
    #     mod_type_elective = ModuleType.objects.create(type_name="Elective", department = first_dept)
    #     mod_type_faculty = ModuleType.objects.create(type_name="Faculty based", department = first_dept)
        
    #     mod_code_1 = 'AS101'
    #     mod_code_2 = 'AS201'
    #     mod_code_3 = 'AS301'
    #     mod_code_4 = 'AS401'
    #     unsued_mod_code = 'UNUSED'#UNUSED
    #     self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': first_scen.id}), \
    #                      {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '152', 'primary_programme' : prog_1.id, \
    #                       'module_type' : mod_type_core.id, 'semester_offered' : Module.SEM_1, 'number_of_tutorial_groups' : '1',  'fresh_record' : True})    
    #     self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': first_scen.id}), \
    #                      {'module_code': mod_code_2, 'module_title' : 'module 2', 'total_hours' : '252', 'primary_programme' : prog_2.id,\
    #                        'module_type' : mod_type_elective.id, 'semester_offered' : Module.SEM_1, 'number_of_tutorial_groups' : '1',  'fresh_record' : True})    
    #     self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': first_scen.id}),\
    #                       {'module_code': mod_code_3, 'module_title' : 'module 3', 'total_hours' : '352',\
    #                         'module_type' : mod_type_faculty.id, 'semester_offered' : Module.SEM_2, 'number_of_tutorial_groups' : '1',  'fresh_record' : True})    
    #     self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': first_scen.id}),\
    #                       {'module_code': mod_code_4,  'module_title' : 'module 4', 'total_hours' : '352',\
    #                         'module_type' : mod_type_faculty.id, 'semester_offered' : Module.SEM_2, 'number_of_tutorial_groups' : '1',  'fresh_record' : True})        
    #     self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': first_scen.id}),\
    #                       {'module_code': unsued_mod_code,  'module_title' : 'unused_mod', 'total_hours' : '1252', 'module_type' : mod_type_faculty.id, 'semester_offered' : Module.SEM_2, 'number_of_tutorial_groups' : '3',  'fresh_record' : True})        
        
    #     self.assertEqual(Module.objects.all().count(),5)
        
    #     module_1 = Module.objects.filter(module_code = mod_code_1).get()
    #     module_2 = Module.objects.filter(module_code = mod_code_2).get()
    #     module_3 = Module.objects.filter(module_code = mod_code_3).get()
    #     module_4 = Module.objects.filter(module_code = mod_code_4).get()
        
    #     #List of assignemnt and scenarios will still be zero
    #     response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
    #     self.assertEqual(response.status_code, 200) #No issues
        
    #     #Do some assignment
    #     self.client.post(reverse('workload_app:add_assignment', kwargs={'workloadscenario_id': first_scen.id}), {'select_lecturer': normal_lecturer.id, 'select_module': module_1.id,'counted_towards_workload' : 'yes', 'manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'36'});
    #     self.client.post(reverse('workload_app:add_assignment', kwargs={'workloadscenario_id': first_scen.id}), {'select_lecturer': vice_dean.id, 'select_module': module_1.id, 'counted_towards_workload' : 'yes','manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'6'});
    #     self.client.post(reverse('workload_app:add_assignment', kwargs={'workloadscenario_id': first_scen.id}), {'select_lecturer': normal_lecturer.id, 'select_module': module_2.id, 'counted_towards_workload' : 'yes','manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'56'});
    #     self.client.post(reverse('workload_app:add_assignment', kwargs={'workloadscenario_id': first_scen.id}), {'select_lecturer': educator_track.id, 'select_module': module_3.id, 'counted_towards_workload' : 'yes','manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'156'});
    #     self.client.post(reverse('workload_app:add_assignment', kwargs={'workloadscenario_id': first_scen.id}), {'select_lecturer': vice_dean.id, 'select_module': module_4.id, 'counted_towards_workload' : 'yes','manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'356'});
        
    #     #Refresh and call the method to be tested
    #     response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
    #     self.assertEqual(response.status_code, 200) #No issues
    #     obtained_summary_data = response.context['summary_data']
    #     self.assertEqual(len(obtained_summary_data["module_type_labels"]),3)
    #     self.assertEqual(len(obtained_summary_data["hours_by_type"]),3)
    #     self.assertEqual(obtained_summary_data["hours_by_type"][0],36+6)#36+6 hours to core mods from 2 assignments
    #     self.assertEqual(obtained_summary_data["hours_by_type"][1],56)#56 hours to elective mods from 1 assignment
    #     self.assertEqual(obtained_summary_data["hours_by_type"][2],156+356)#156+356 hours to faculty mods from 2 assignments
        
    #     self.assertEqual(len(obtained_summary_data["labels_prog"]),3)
    #     self.assertEqual(len(obtained_summary_data["hours_prog"]),3)
    #     self.assertEqual(obtained_summary_data['labels_prog'][0], prog_1.programme_name)
    #     self.assertEqual(obtained_summary_data['labels_prog'][1], prog_2.programme_name)
    #     self.assertEqual(obtained_summary_data['labels_prog'][2], 'No programme')
    #     self.assertEqual(obtained_summary_data["hours_prog"][0],36+6)#36+6 hours to core mods from 2 assignments of mod 1
    #     self.assertEqual(obtained_summary_data["hours_prog"][1],56)#56 from mod 2
    #     self.assertEqual(obtained_summary_data["hours_prog"][2],356+156)#From mod 3 and mod 4

    #     self.assertAlmostEqual(obtained_summary_data["total_tFTE_for_workload"],Decimal(0.7*1.0+1.0*2.0+0.5*1.0))#From 3 profs above
    #     self.assertAlmostEqual(obtained_summary_data["total_department_tFTE"],Decimal(0.7*1.0+1.0*2.0+0.5*1.0+0.5*3))#From 4 profs above
    #     self.assertAlmostEqual(obtained_summary_data["total_hours_for_workload"],Decimal(36+6+56+156+356))#From 4 assignments above
    #     self.assertAlmostEqual(obtained_summary_data["expected_hours_per_tFTE"],Decimal(36+6+56+156+356)/Decimal(0.7*1.0+1.0*2.0+0.5*1.0+0.5*3))#From 4 assignments above and 4 profs
    #     self.assertAlmostEqual(obtained_summary_data["total_module_hours_for_dept"],Decimal(152+252+352+352+1252))#
    #     self.assertAlmostEqual(obtained_summary_data["total_adjunct_tFTE"],Decimal(3*0.5))#adjunct lecturer is 0.5 appointed on the adjunct track (*3)
    #     self.assertAlmostEqual(obtained_summary_data["total_number_of_adjuncts"],Decimal(1))#one adjunct lecturer
    #     self.assertAlmostEqual(obtained_summary_data["total_number_of_external"], Decimal(1))#one external person
        
    #     #Add more modules and more assignments
    #     mod_code_5 = 'AS501'
    #     mod_code_6 = 'AS601'
    #     mod_code_7 = 'AS701'
    #     mod_code_8 = 'AS801'
    #     mod_code_9 = 'AS901'
    #     self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': first_scen.id}), {'module_code': mod_code_5, 'module_title' : 'module 5', 'total_hours' : '10', 'module_type' : mod_type_core.id, 'semester_offered' : Module.SPECIAL_TERM_1, 'number_of_tutorial_groups' : '1',  'fresh_record' : True})    
    #     self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': first_scen.id}), {'module_code': mod_code_6, 'module_title' : 'module 6', 'total_hours' : '20', 'module_type' : mod_type_elective.id, 'semester_offered' : Module.SPECIAL_TERM_1, 'number_of_tutorial_groups' : '1',  'fresh_record' : True})    
    #     self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': first_scen.id}), {'module_code': mod_code_7, 'module_title' : 'module 7', 'total_hours' : '30', 'module_type' : mod_type_faculty.id, 'semester_offered' : Module.SPECIAL_TERM_2, 'number_of_tutorial_groups' : '1',  'fresh_record' : True})    
    #     self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': first_scen.id}), {'module_code': mod_code_8,  'module_title' : 'module 8', 'total_hours' : '40', 'module_type' : mod_type_faculty.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '1',  'fresh_record' : True})        
    #     self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': first_scen.id}), {'module_code': mod_code_9,  'module_title' : 'module 9', 'total_hours' : '50', 'module_type' : mod_type_faculty.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '1',  'fresh_record' : True})        
    #     self.assertEqual(Module.objects.all().count(),10)

    #     #Note 6 and 9 have no assignments...        
    #     module_5 = Module.objects.filter(module_code = mod_code_5).get()
    #     module_7 = Module.objects.filter(module_code = mod_code_7).get()
    #     module_8 = Module.objects.filter(module_code = mod_code_8).get()
    #     self.client.post(reverse('workload_app:add_assignment', kwargs={'workloadscenario_id': first_scen.id}), {'select_lecturer': normal_lecturer.id, 'select_module': module_5.id, 'counted_towards_workload' : 'yes','manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'36'});
    #     self.client.post(reverse('workload_app:add_assignment', kwargs={'workloadscenario_id': first_scen.id}), {'select_lecturer': vice_dean.id, 'select_module': module_5.id, 'counted_towards_workload' : 'yes','manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'6'});
    #     self.client.post(reverse('workload_app:add_assignment', kwargs={'workloadscenario_id': first_scen.id}), {'select_lecturer': normal_lecturer.id, 'select_module': module_7.id, 'counted_towards_workload' : 'yes','manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'56'});
    #     self.client.post(reverse('workload_app:add_assignment', kwargs={'workloadscenario_id': first_scen.id}), {'select_lecturer': educator_track.id, 'select_module': module_8.id,'counted_towards_workload' : 'yes', 'manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'10'});
    #     self.client.post(reverse('workload_app:add_assignment', kwargs={'workloadscenario_id': first_scen.id}), {'select_lecturer': vice_dean.id, 'select_module': module_8.id, 'counted_towards_workload' : 'yes','manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'20'});
        
    #     response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
    #     self.assertEqual(response.status_code, 200) #No issues
    #     obtained_summary_data = response.context['summary_data']
    #     self.assertAlmostEqual(obtained_summary_data["hours_sem_1"],Decimal(36+6+56))#From 3 assignments of module 1 and 2
    #     self.assertAlmostEqual(obtained_summary_data["hours_sem_2"],Decimal(156+356))#From 2 assignments modules 3 and 4 
    #     self.assertAlmostEqual(obtained_summary_data["hours_other_sems"],Decimal(36+6+56+10+20))#From 5 assignments modules 5,7, and 8
    #     self.assertAlmostEqual(obtained_summary_data["total_hours_for_workload"],Decimal(36+6+56+156+356+36+6+56+10+20))#From all assignments
    #     self.assertAlmostEqual(obtained_summary_data["total_hours_not_counted"],Decimal(0))#From no assignment

    #     #Add an assignment NOT counted towards the workload
    #     self.client.post(reverse('workload_app:add_assignment', kwargs={'workloadscenario_id': first_scen.id}), {'select_lecturer': vice_dean.id, \
    #                                                   'select_module': module_7.id, 'counted_towards_workload' : 'no',\
    #                                                   'manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'1320'})
    #     #Check everything UNCHANGED
    #     response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
    #     self.assertEqual(response.status_code, 200) #No issues
    #     obtained_summary_data = response.context['summary_data']
    #     self.assertAlmostEqual(obtained_summary_data["hours_sem_1"],Decimal(36+6+56))#From 3 assignments of module 1 and 2
    #     self.assertAlmostEqual(obtained_summary_data["hours_sem_2"],Decimal(156+356))#From 2 assignments modules 3 and 4 
    #     self.assertAlmostEqual(obtained_summary_data["hours_other_sems"],Decimal(36+6+56+10+20))#From 5 assignments modules 5,7, and 8
    #     self.assertAlmostEqual(obtained_summary_data["total_hours_for_workload"],Decimal(36+6+56+156+356+36+6+56+10+20))#From all assignments
    #     #But the not counted hours are there...
    #     self.assertAlmostEqual(obtained_summary_data["total_hours_not_counted"],Decimal(1320))#From one assignment

    #     #Make an assignment to the external person
    #     self.client.post(reverse('workload_app:add_assignment', kwargs={'workloadscenario_id': first_scen.id}), {'select_lecturer': external_lecturer.id, \
    #                                                   'select_module': module_7.id, 'counted_towards_workload' : 'no',\
    #                                                   'manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'2340'})

    #     #Check everything UNCHANGED
    #     response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
    #     self.assertEqual(response.status_code, 200) #No issues
    #     obtained_summary_data = response.context['summary_data']
    #     self.assertAlmostEqual(obtained_summary_data["hours_sem_1"],Decimal(36+6+56))#From 3 assignments of module 1 and 2
    #     self.assertAlmostEqual(obtained_summary_data["hours_sem_2"],Decimal(156+356))#From 2 assignments modules 3 and 4 
    #     self.assertAlmostEqual(obtained_summary_data["hours_other_sems"],Decimal(36+6+56+10+20))#From 5 assignments modules 5,7, and 8
    #     self.assertAlmostEqual(obtained_summary_data["total_hours_for_workload"],Decimal(36+6+56+156+356+36+6+56+10+20))#From all assignments
    #     #But the not counted hours have changed beacuse of the assignment to the external staff
    #     self.assertAlmostEqual(obtained_summary_data["total_hours_not_counted"],Decimal(1320+2340))#From one assignment not counted, plus one to external staff

    #     #Create another scenario
    #     new_label = "new_scenario"
    #     acad_year = Academicyear.objects.create(start_year=2200)
    #     self.client.post(reverse('workload_app:manage_scenario'),{'label':new_label, 'dept' : first_dept.id, 'status': WorkloadScenario.DRAFT, 'fresh_record' : True, 'academic_year': acad_year.id})
    #     new_scenario = WorkloadScenario.objects.filter(label=new_label)
    #     response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scenario.get().id}))
    #     self.assertEqual(response.status_code, 200) #No issues
    #     obtained_summary_data = response.context['summary_data']
    #     self.assertEqual(len(obtained_summary_data["module_type_labels"]),0)#No teaching assignments in the new scenario, so no labels and no counts
    #     self.assertEqual(len(obtained_summary_data["hours_by_type"]),0)#No teaching assignments in the new scenario, so no labels and no counts
    #     self.assertEqual(len(obtained_summary_data["labels_prog"]),0)#No teaching assignments in the new scenario, so no labels and no counts
    #     self.assertEqual(len(obtained_summary_data["hours_prog"]),0)#No teaching assignments in the new scenario, so no labels and no counts
        
    #     self.assertAlmostEqual(obtained_summary_data["total_tFTE_for_workload"],Decimal(0))#
    #     self.assertAlmostEqual(obtained_summary_data["total_department_tFTE"],Decimal(0))#
    #     self.assertAlmostEqual(obtained_summary_data["total_module_hours_for_dept"],Decimal(0))#
    #     self.assertAlmostEqual(obtained_summary_data["total_hours_for_workload"],Decimal(0));
    #     self.assertAlmostEqual(obtained_summary_data["expected_hours_per_tFTE"],Decimal(0));
        
    #     #Add a module in new scenario
    #     self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': new_scenario.get().id}), {'module_code': 'in_new_scenario',  'module_title' : 'new_scen_mod', 'total_hours' : '8252', 'module_type' : mod_type_faculty.id, 'semester_offered' : Module.SEM_2, 'number_of_tutorial_groups' : '3',  'fresh_record' : True})        
        
    #     self.assertEqual(Module.objects.all().count(),11)
        
    #     response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scenario.get().id}))
    #     self.assertEqual(response.status_code, 200) #No issues
    #     obtained_summary_data = response.context['summary_data']
    #     self.assertAlmostEqual(obtained_summary_data["total_module_hours_for_dept"],Decimal(8252))#
    
    # def testCalculateDepartmentHourlyTablesForCoverage(self):
    #     #Call the method with invalid IDs
    #     table_struct = CalculateModuleHourlyTableForProgramme(12578,23698)
    #     self.assertEqual(table_struct["scenario_name"], "")
    #     self.assertEqual(table_struct["programme_name"], "")
    #     self.assertEqual(len(table_struct["table_rows_with_mods_and_hours"]), 0) #Nothing to display
    #     self.assertEqual(table_struct["total_hours_sem_1"], 0)
    #     self.assertEqual(table_struct["total_hours_sem_1"], 0)

    # def testCalculateModuleTableOverYears(self):
    #     calc = CalculateSingleModuleInformationTable("BN301")
    #     self.assertEqual(len(calc),0)

    #     acad_year_1 = Academicyear.objects.create(start_year=2021)
    #     acad_year_2 = Academicyear.objects.create(start_year=2022)
    #     dept_name = 'test_dept'
    #     first_fac = Faculty.objects.create(faculty_name = "first fac", faculty_acronym = "FRTE")
    #     test_dept = Department.objects.create(department_name = dept_name, department_acronym = "ACR", faculty = first_fac)
    #     scenario_1 = WorkloadScenario.objects.create(label="scenario_1", academic_year = acad_year_1, dept = test_dept, status = WorkloadScenario.OFFICIAL)
    #     track_1 = EmploymentTrack.objects.create(track_name = "track_1", track_adjustment = 2.0, is_adjunct = False, faculty=first_fac)
    #     service_role_1 = ServiceRole.objects.create(role_name = "role_1", role_adjustment = 2.0, faculty=first_fac)
    #     mod_type_1 = ModuleType.objects.create(type_name = "one type",departmant= test_dept)
    #     programme_1 = ProgrammeOffered.objects.create(programme_name = "B. Eng", primary_dept = test_dept)
    #     programme_2 = ProgrammeOffered.objects.create(programme_name = "M. Sc", primary_dept = test_dept)
    #     sub_programme_1 = SubProgrammeOffered.objects.create(sub_programme_name = "specialization", main_programme = programme_1)

    #     #CREATE THREE LECTURERS
    #     lecturer_1 = Lecturer.objects.create(name="lecturer_1", fraction_appointment = 0.7, employment_track=track_1, workload_scenario = scenario_1, service_role = service_role_1)
    #     lecturer_2 = Lecturer.objects.create(name="lecturer_2", fraction_appointment = 1.0, employment_track=track_1, workload_scenario = scenario_1, service_role = service_role_1)
    #     lecturer_3 = Lecturer.objects.create(name="lecturer_3", fraction_appointment = 0.5, employment_track=track_1, workload_scenario = scenario_1, service_role = service_role_1)
    #     #Create three modules. Module two has associated programme. Module 3 has two programmes and also one sub-programme
    #     module_1 = Module.objects.create(module_code = "BN101", module_title="First module", scenario_ref=scenario_1, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1)
    #     module_2 = Module.objects.create(module_code = "BN201", module_title="Second module", scenario_ref=scenario_1, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1,\
    #                                     primary_programme = programme_2)
    #     module_3 = Module.objects.create(module_code = "BN301", module_title="Third module", scenario_ref=scenario_1, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1,\
    #                                     students_year_of_study = 1, compulsory_in_primary_programme = True, primary_programme = programme_1, secondary_programme = programme_2, sub_programme = sub_programme_1)
    #     #Do some assignments
    #     #2 lecturers for module 1
    #     TeachingAssignment.objects.create(assigned_module = module_1, assigned_lecturer = lecturer_1, number_of_hours = 25, workload_scenario=scenario_1)
    #     TeachingAssignment.objects.create(assigned_module = module_1, assigned_lecturer = lecturer_2, number_of_hours = 55, workload_scenario=scenario_1)
    #     #One for module 2
    #     TeachingAssignment.objects.create(assigned_module = module_2, assigned_lecturer = lecturer_3, number_of_hours = 100, workload_scenario=scenario_1)
    #     #Two for module 3
    #     TeachingAssignment.objects.create(assigned_module = module_3, assigned_lecturer = lecturer_1, number_of_hours = 35, workload_scenario=scenario_1)
    #     TeachingAssignment.objects.create(assigned_module = module_3, assigned_lecturer = lecturer_3, number_of_hours = 45, workload_scenario=scenario_1)

    #     #Now call the helper method
    #     calc = CalculateSingleModuleInformationTable("BN101")
    #     self.assertEqual(len(calc),1)
    #     self.assertEqual(calc[0]["academic_year"],"2021-2022")
    #     self.assertEqual(calc[0]["module_type"],"one type")
    #     self.assertEqual(calc[0]["semester_offered"],"Semester 1")
    #     self.assertEqual(calc[0]["programmes"],"None")
    #     self.assertEqual(calc[0]["subprogrammes"],"None")
    #     self.assertEqual(calc[0]["year_of_study"],'0')
    #     self.assertEqual(calc[0]["total_hours_delivered"],25+55)
    #     self.assertEqual(calc[0]["lecturers_involved"],"lecturer_1 (25), lecturer_2 (55)")
        
    #     calc = CalculateSingleModuleInformationTable("BN201")
    #     self.assertEqual(len(calc),1)
    #     self.assertEqual(calc[0]["academic_year"],"2021-2022")
    #     self.assertEqual(calc[0]["module_type"],"one type")
    #     self.assertEqual(calc[0]["semester_offered"],"Semester 1")
    #     self.assertEqual(calc[0]["programmes"],programme_2.programme_name + ' (elective)')
    #     self.assertEqual(calc[0]["subprogrammes"],"None")
    #     self.assertEqual(calc[0]["year_of_study"],'0')
    #     self.assertEqual(calc[0]["total_hours_delivered"],100)
    #     self.assertEqual(calc[0]["lecturers_involved"],"lecturer_3 (100)")

    #     calc = CalculateSingleModuleInformationTable("BN301")
    #     self.assertEqual(len(calc),1)
    #     self.assertEqual(calc[0]["academic_year"],"2021-2022")
    #     self.assertEqual(calc[0]["module_type"],"one type")
    #     self.assertEqual(calc[0]["semester_offered"],"Semester 1")
    #     self.assertEqual(calc[0]["programmes"],programme_1.programme_name +  ' (compulsory), ' + programme_2.programme_name + ' (elective)')
    #     self.assertEqual(calc[0]["subprogrammes"],sub_programme_1.sub_programme_name)
    #     self.assertEqual(calc[0]["year_of_study"],'1')
    #     self.assertEqual(calc[0]["total_hours_delivered"],35+45)
    #     self.assertEqual(calc[0]["lecturers_involved"],"lecturer_1 (35), lecturer_3 (45)")

    #     self.assertEqual(TeachingAssignment.objects.all().count(),5)
    #     self.assertEqual(Lecturer.objects.all().count(),3)
    #     self.assertEqual(Module.objects.all().count(),3)
    #     #Create another one. Copying from the existing one
    #     new_label = "new_scenario"
    #     self.client.post(reverse('workload_app:manage_scenario'), {'label': new_label, 'dept' : test_dept.id, 'copy_from':scenario_1.id, \
    #                                                                 'status': WorkloadScenario.OFFICIAL, 'fresh_record' : True, 'academic_year' : acad_year_2.id});
    #     scenario_2 = WorkloadScenario.objects.filter(label=new_label).get()
    #     self.assertEqual(WorkloadScenario.objects.all().count(),2)
    #     self.assertEqual(TeachingAssignment.objects.all().count(),10)
    #     self.assertEqual(Lecturer.objects.all().count(),6)
    #     self.assertEqual(Module.objects.all().count(),6)
    #     self.assertEqual(Module.objects.filter(scenario_ref=scenario_1).count(),3)
    #     self.assertEqual(Module.objects.filter(scenario_ref=scenario_2).count(),3)
    #     self.assertEqual(Lecturer.objects.filter(workload_scenario=scenario_1).count(),3)
    #     self.assertEqual(Lecturer.objects.filter(workload_scenario=scenario_2).count(),3)
    #     self.assertEqual(TeachingAssignment.objects.filter(workload_scenario = scenario_1).count(),5)
    #     self.assertEqual(TeachingAssignment.objects.filter(workload_scenario = scenario_2).count(),5)

    #     calc = CalculateSingleModuleInformationTable("BN301")
    #     self.assertEqual(len(calc),2)
    #     self.assertEqual(calc[0]["academic_year"],"2021-2022")
    #     self.assertEqual(calc[0]["module_type"],"one type")
    #     self.assertEqual(calc[0]["semester_offered"],"Semester 1")
    #     self.assertEqual(calc[0]["programmes"],programme_1.programme_name + ' (compulsory), ' + programme_2.programme_name + ' (elective)')
    #     self.assertEqual(calc[0]["subprogrammes"],sub_programme_1.sub_programme_name)
    #     self.assertEqual(calc[0]["total_hours_delivered"],35+45)
    #     self.assertEqual(calc[0]["lecturers_involved"],"lecturer_1 (35), lecturer_3 (45)")
    #     self.assertEqual(calc[1]["academic_year"],"2022-2023")#new academic year
    #     self.assertEqual(calc[1]["module_type"],"one type")
    #     self.assertEqual(calc[1]["semester_offered"],"Semester 1")
    #     self.assertEqual(calc[1]["programmes"],programme_1.programme_name + ' (compulsory), ' + programme_2.programme_name + ' (elective)')
    #     self.assertEqual(calc[1]["subprogrammes"],sub_programme_1.sub_programme_name)
    #     self.assertEqual(calc[1]["total_hours_delivered"],35+45)
    #     self.assertEqual(calc[1]["lecturers_involved"],"lecturer_1 (35), lecturer_3 (45)")
        
    #     #make another assignment, only in the second scenario
    #     assign_new = TeachingAssignment.objects.create(assigned_module = module_3, assigned_lecturer = lecturer_2, number_of_hours = 65, workload_scenario=scenario_2)
    #     assign_new.save()
    #     self.assertEqual(TeachingAssignment.objects.filter(workload_scenario = scenario_2).count(),6)
    #     self.assertEqual(TeachingAssignment.objects.filter(number_of_hours=65).filter(assigned_module__module_code = "BN301").filter(workload_scenario = scenario_2).count(),1)

    #     calc = CalculateSingleModuleInformationTable("BN301")
    #     self.assertEqual(len(calc),2)
    #     self.assertEqual(calc[0]["academic_year"],"2021-2022")
    #     self.assertEqual(calc[0]["module_type"],"one type")
    #     self.assertEqual(calc[0]["semester_offered"],"Semester 1")
    #     self.assertEqual(calc[0]["programmes"],programme_1.programme_name + ' (compulsory), ' + programme_2.programme_name + ' (elective)')
    #     self.assertEqual(calc[0]["subprogrammes"],sub_programme_1.sub_programme_name)
    #     self.assertEqual(calc[0]["total_hours_delivered"],35+45)
    #     self.assertEqual(calc[0]["lecturers_involved"],"lecturer_1 (35), lecturer_3 (45)")
    #     self.assertEqual(calc[1]["academic_year"],"2022-2023")#new academic year
    #     self.assertEqual(calc[1]["module_type"],"one type")
    #     self.assertEqual(calc[1]["semester_offered"],"Semester 1")
    #     self.assertEqual(calc[1]["programmes"],programme_1.programme_name + ' (compulsory), ' + programme_2.programme_name + ' (elective)')
    #     self.assertEqual(calc[1]["subprogrammes"],sub_programme_1.sub_programme_name)
    #     self.assertEqual(calc[1]["total_hours_delivered"],35+45+65)#note teh 65 added 
    #     self.assertEqual(calc[1]["lecturers_involved"],"lecturer_1 (35), lecturer_3 (45), lecturer_2 (65)")#note lecturer 2 added

    # def testCalculateDepartmentProgrammeTables(self):
    #     #Create a Dept affiliated to a faculty
    #     dept_name = 'test_dept'
    #     first_fac = Faculty.objects.create(faculty_name = "first fac", faculty_acronym = "FRTE")
    #     test_dept = Department.objects.create(department_name = dept_name, department_acronym = "ACR", faculty = first_fac)
    #     self.assertEqual(Department.objects.all().count(), 1)
    #     #Create two programmes
    #     ug_prog_name ='UG'
    #     ug_prog = ProgrammeOffered.objects.create(programme_name = ug_prog_name, primary_dept = test_dept)
    #     self.assertEqual(ProgrammeOffered.objects.all().count(), 1)
    #     pg_prog_name ='PG'
    #     pg_prog = ProgrammeOffered.objects.create(programme_name = pg_prog_name, primary_dept = test_dept)
    #     self.assertEqual(ProgrammeOffered.objects.all().count(), 2)
    #     new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
    #     #Create an academic year
    #     test_acad_year = Academicyear.objects.create(start_year = 2023)
    #     #Create a Workload scenario
    #     test_scenario_name = "test_scen"
    #     wl_scen = WorkloadScenario.objects.create(label = test_scenario_name, dept = test_dept, academic_year = test_acad_year,\
    #                                                status = WorkloadScenario.OFFICIAL)
    #     #Create some lecturers
    #     track_1 = EmploymentTrack.objects.create(track_name = "track_1", track_adjustment = 2.0, is_adjunct = False, faculty=new_fac)
    #     test_svc_role = ServiceRole.objects.create(role_name = "test", role_adjustment = 2.0, faculty=new_fac)
    #     normal_lecturer = Lecturer.objects.create(name="normal_lecturer", fraction_appointment = 0.7, service_role = test_svc_role, workload_scenario = wl_scen)
    #     educator_track = Lecturer.objects.create(name="educator_track", fraction_appointment = 1.0, service_role = test_svc_role, employment_track=track_1,workload_scenario = wl_scen)
    #     vice_dean = Lecturer.objects.create(name="vice_dean", fraction_appointment = 0.5, service_role = test_svc_role, workload_scenario = wl_scen)
    #     #and some modules with two types
    #     core_mod = ModuleType.objects.create(type_name = "core",departmant= test_dept)
    #     elective_mod = ModuleType.objects.create(type_name = "elective",departmant= test_dept)
    #     mod_1_ug_sem_1 = Module.objects.create(module_code = "M1-UG-SEM1", module_title = "module 1 ug sem 1", scenario_ref = wl_scen,\
    #                                            total_hours = 200, module_type = core_mod, semester_offered= Module.SEM_1, number_of_tutorial_groups=1,\
    #                                            primary_programme=ug_prog)
    #     mod_2_ug_sem_1 = Module.objects.create(module_code = "M2-UG-SEM1", module_title = "module 2 ug sem 1", scenario_ref = wl_scen,\
    #                                            total_hours = 150, module_type = core_mod, semester_offered= Module.SEM_1, number_of_tutorial_groups=1,\
    #                                            primary_programme=ug_prog)
    #     mod_3_ug_sem_2 = Module.objects.create(module_code = "M3-UG-SEM2", module_title = "module 3 ug sem 2", scenario_ref = wl_scen,\
    #                                            total_hours = 150, module_type = core_mod, semester_offered= Module.SEM_2, number_of_tutorial_groups=1,\
    #                                            primary_programme=ug_prog)
    #     mod_4_pg_sem_1 = Module.objects.create(module_code = "M4-PG-SEM1", module_title = "module 4 pg sem 1", scenario_ref = wl_scen,\
    #                                            total_hours = 150, module_type = core_mod, semester_offered= Module.SEM_1, number_of_tutorial_groups=1,\
    #                                            primary_programme=pg_prog)
    #     mod_5_pg_sem_2 = Module.objects.create(module_code = "M5-PG-SEM2", module_title = "module 5 pg sem 2", scenario_ref = wl_scen,\
    #                                            total_hours = 150, module_type = elective_mod, semester_offered= Module.SEM_2, number_of_tutorial_groups=1,\
    #                                            primary_programme=pg_prog)
    #     #Must be here to check the table will not count it (simulates a module not offered that year)
    #     unassigned_pg_mod = Module.objects.create(module_code = "UNASSIGNED_PG", module_title = "unassigned pg sem 2", scenario_ref = wl_scen,\
    #                                            total_hours = 350, module_type = elective_mod, semester_offered= Module.SEM_2, number_of_tutorial_groups=1,\
    #                                            primary_programme=pg_prog)
        
    #     #Coverage. Call the method before making any assignment
    #     table_struct = CalculateModuleHourlyTableForProgramme(wl_scen.id,ug_prog.id)
    #     self.assertEqual(table_struct["scenario_name"], test_scenario_name)
    #     self.assertEqual(table_struct["programme_name"], ug_prog_name)
    #     self.assertEqual(len(table_struct["table_rows_with_mods_and_hours"]), 0) #Nothing to display
    #     self.assertEqual(table_struct["total_hours_sem_1"], 0)
    #     self.assertEqual(table_struct["total_hours_sem_1"], 0)
        
    #     #Assign modules to lecturers
    #     TeachingAssignment.objects.create(assigned_module = mod_1_ug_sem_1, assigned_lecturer = normal_lecturer, number_of_hours = 25, workload_scenario=wl_scen)
    #     TeachingAssignment.objects.create(assigned_module = mod_2_ug_sem_1, assigned_lecturer = normal_lecturer, number_of_hours = 55, workload_scenario=wl_scen)
    #     TeachingAssignment.objects.create(assigned_module = mod_3_ug_sem_2, assigned_lecturer = normal_lecturer, number_of_hours = 25, workload_scenario=wl_scen)
    #     TeachingAssignment.objects.create(assigned_module = mod_4_pg_sem_1, assigned_lecturer = normal_lecturer, number_of_hours = 25, workload_scenario=wl_scen)
    #     TeachingAssignment.objects.create(assigned_module = mod_5_pg_sem_2, assigned_lecturer = normal_lecturer, number_of_hours = 95, workload_scenario=wl_scen)
    #     TeachingAssignment.objects.create(assigned_module = mod_1_ug_sem_1, assigned_lecturer = educator_track, number_of_hours = 25, workload_scenario=wl_scen)
    #     TeachingAssignment.objects.create(assigned_module = mod_1_ug_sem_1, assigned_lecturer = vice_dean, number_of_hours = 125, workload_scenario=wl_scen)

    #     #Call the method now, analysing the UG programme, 2 mods in sem 1, 1 mod in sem 2
    #     table_struct = CalculateModuleHourlyTableForProgramme(wl_scen.id,ug_prog.id)
    #     self.assertEqual(table_struct["scenario_name"], test_scenario_name)
    #     self.assertEqual(table_struct["programme_name"], ug_prog_name)
    #     self.assertEqual(len(table_struct["table_rows_with_mods_and_hours"]), 2)
    #     self.assertEqual(table_struct["table_rows_with_mods_and_hours"][0]["mod_code_sem_1"], "M1-UG-SEM1")
    #     self.assertEqual(table_struct["table_rows_with_mods_and_hours"][0]["mod_title_sem_1"], "module 1 ug sem 1")
    #     self.assertEqual(table_struct["table_rows_with_mods_and_hours"][0]["hours_mod_sem_1"], 25+25+125)
    #     self.assertEqual(table_struct["table_rows_with_mods_and_hours"][0]["mod_code_sem_2"], "M3-UG-SEM2")
    #     self.assertEqual(table_struct["table_rows_with_mods_and_hours"][0]["mod_title_sem_2"], "module 3 ug sem 2")
    #     self.assertEqual(table_struct["table_rows_with_mods_and_hours"][0]["hours_mod_sem_2"], 25)
    #     self.assertEqual(table_struct["table_rows_with_mods_and_hours"][1]["mod_code_sem_1"], "M2-UG-SEM1")
    #     self.assertEqual(table_struct["table_rows_with_mods_and_hours"][1]["mod_title_sem_1"], "module 2 ug sem 1")
    #     self.assertEqual(table_struct["table_rows_with_mods_and_hours"][1]["hours_mod_sem_1"], 55)
    #     self.assertEqual(table_struct["table_rows_with_mods_and_hours"][1]["mod_code_sem_2"], "")
    #     self.assertEqual(table_struct["table_rows_with_mods_and_hours"][1]["hours_mod_sem_2"], "")
    #     self.assertEqual(table_struct["mods_present"], 3)
    #     self.assertEqual(table_struct["total_hours_sem_1"], 25+55+25+125)
    #     self.assertEqual(table_struct["total_hours_sem_2"], 25)
    #     self.assertEqual(table_struct["total_num_mods_sem_1"], 2)
    #     self.assertEqual(table_struct["total_num_mods_sem_2"], 1)
    #     self.assertEqual(len(table_struct["unused_modules"]), 0)

    #     #now check the table by module types for UG programme
    #     table_mod_types = CalculateModuleTypesTableForProgramme(wl_scen.id,ug_prog.id)
    #     self.assertEqual(table_mod_types["scenario_name"], test_scenario_name)
    #     self.assertEqual(table_mod_types["programme_name"], ug_prog_name)
    #     self.assertEqual(len(table_mod_types["table_rows_with_types_and_numbers"]), 1)#Core only 
    #     self.assertEqual(table_mod_types["table_rows_with_types_and_numbers"][0]["mod_type"], "core")
    #     self.assertEqual(table_mod_types["table_rows_with_types_and_numbers"][0]["no_mods_sem_1"], 2)
    #     self.assertEqual(table_mod_types["table_rows_with_types_and_numbers"][0]["no_mods_sem_2"], 1)
    #     self.assertEqual(table_mod_types["table_rows_with_types_and_numbers"][0]["hours_assigned_sem_1"], 25+25+55+125)
    #     self.assertEqual(table_mod_types["table_rows_with_types_and_numbers"][0]["hours_assigned_sem_2"], 25)
    #     self.assertEqual(table_mod_types["total_hours_assigned_sem_1"], 25+25+55+125)
    #     self.assertEqual(table_mod_types["total_hours_assigned_sem_2"], 25)

    #     #Call the method now, analysing the PG programme, 1 mod in sem 1, 1 mod in sem 2. Note the unassigned module should not be in the table
    #     table_struct_pg = CalculateModuleHourlyTableForProgramme(wl_scen.id,pg_prog.id)
    #     self.assertEqual(table_struct_pg["scenario_name"], test_scenario_name)
    #     self.assertEqual(table_struct_pg["programme_name"], pg_prog_name)
    #     self.assertEqual(len(table_struct_pg["table_rows_with_mods_and_hours"]), 1)
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][0]["mod_code_sem_1"], "M4-PG-SEM1")
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][0]["hours_mod_sem_1"], 25)
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][0]["mod_code_sem_2"], "M5-PG-SEM2")
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][0]["hours_mod_sem_2"], 95)
    #     self.assertEqual(table_struct_pg["total_num_mods_sem_1"], 1)
    #     self.assertEqual(table_struct_pg["total_num_mods_sem_2"], 1)
    #     self.assertEqual(len(table_struct_pg["unused_modules"]), 1)
    #     self.assertEqual(table_struct_pg["unused_modules"][0]["unused_mod_code_sem_1"], "")
    #     self.assertEqual(table_struct_pg["unused_modules"][0]["unused_mod_code_sem_2"], "UNASSIGNED_PG")

    #     # #now check the table by module types for PG programme
    #     table_mod_types_pg = CalculateModuleTypesTableForProgramme(wl_scen.id,pg_prog.id)
    #     self.assertEqual(table_mod_types_pg["scenario_name"], test_scenario_name)
    #     self.assertEqual(table_mod_types_pg["programme_name"], pg_prog_name)
    #     self.assertEqual(len(table_mod_types_pg["table_rows_with_types_and_numbers"]), 2)#Core and elective (see above)
    #     self.assertEqual(table_mod_types_pg["table_rows_with_types_and_numbers"][0]["mod_type"], "core")
    #     self.assertEqual(table_mod_types_pg["table_rows_with_types_and_numbers"][0]["no_mods_sem_1"], 1)
    #     self.assertEqual(table_mod_types_pg["table_rows_with_types_and_numbers"][0]["no_mods_sem_2"], 0)
    #     self.assertEqual(table_mod_types_pg["table_rows_with_types_and_numbers"][0]["hours_assigned_sem_1"], 25)
    #     self.assertEqual(table_mod_types_pg["table_rows_with_types_and_numbers"][0]["hours_assigned_sem_2"], 0)
    #     self.assertEqual(table_mod_types_pg["table_rows_with_types_and_numbers"][1]["mod_type"], "elective") 
    #     self.assertEqual(table_mod_types_pg["table_rows_with_types_and_numbers"][1]["no_mods_sem_1"], 0)
    #     self.assertEqual(table_mod_types_pg["table_rows_with_types_and_numbers"][1]["no_mods_sem_2"], 1)#Must exclude the one not offered (not assigne any hour)
    #     self.assertEqual(table_mod_types_pg["table_rows_with_types_and_numbers"][1]["hours_assigned_sem_1"], 0)
    #     self.assertEqual(table_mod_types_pg["table_rows_with_types_and_numbers"][1]["hours_assigned_sem_2"], 95)
    #     self.assertEqual(table_mod_types_pg["total_num_mods_sem_1"], 1)
    #     self.assertEqual(table_mod_types_pg["total_num_mods_sem_2"], 1)
    #     self.assertEqual(table_mod_types_pg["total_hours_assigned_sem_1"], 25)
    #     self.assertEqual(table_mod_types_pg["total_hours_assigned_sem_2"], 95)
    #     #Check consistency
    #     self.assertEqual(table_mod_types_pg["total_hours_assigned_sem_1"], table_struct_pg["total_hours_sem_1"])
    #     self.assertEqual(table_mod_types_pg["total_hours_assigned_sem_2"], table_struct_pg["total_hours_sem_2"])
    #     self.assertEqual(table_mod_types["total_hours_assigned_sem_1"], table_struct["total_hours_sem_1"])
    #     self.assertEqual(table_mod_types["total_hours_assigned_sem_2"], table_struct["total_hours_sem_2"])

    #     #Now add one module in the PG programme, offered in both sem 1 and sem 2
    #     mod_6_pg_both_sems = Module.objects.create(module_code = "M6-PG-BOTHSEMS", module_title = "module 6 pg both sems", scenario_ref = wl_scen,\
    #                                            total_hours = 150, module_type = elective_mod, semester_offered= Module.BOTH_SEMESTERS , number_of_tutorial_groups=1,\
    #                                            primary_programme=pg_prog)
        
    #     #Assign 150 hours. Supposedly assumed 50% each semester
    #     TeachingAssignment.objects.create(assigned_module = mod_6_pg_both_sems, assigned_lecturer = vice_dean, number_of_hours = 150, workload_scenario=wl_scen)
    #     #Call the method again
    #     table_struct_pg = CalculateModuleHourlyTableForProgramme(wl_scen.id,pg_prog.id)        
    #     self.assertEqual(len(table_struct_pg["table_rows_with_mods_and_hours"]), 2)
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][0]["mod_code_sem_1"], "M4-PG-SEM1")
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][0]["hours_mod_sem_1"], 25)
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][0]["mod_code_sem_2"], "M5-PG-SEM2")
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][0]["hours_mod_sem_2"], 95)
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][1]["mod_code_sem_1"], "M6-PG-BOTHSEMS")
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][1]["hours_mod_sem_1"], 75)#150/2
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][1]["mod_code_sem_2"], "M6-PG-BOTHSEMS")
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][1]["hours_mod_sem_2"], 75)#150/2
    #     self.assertEqual(table_struct_pg["total_num_mods_sem_1"], 2)
    #     self.assertEqual(table_struct_pg["total_num_mods_sem_2"], 2)
    #     self.assertEqual(len(table_struct_pg["unused_modules"]), 1)
    #     self.assertEqual(table_struct_pg["unused_modules"][0]["unused_mod_code_sem_1"], "")
    #     self.assertEqual(table_struct_pg["unused_modules"][0]["unused_mod_code_sem_2"], "UNASSIGNED_PG")
    #     #And call the module type method again
    #     table_mod_types_pg = CalculateModuleTypesTableForProgramme(wl_scen.id,pg_prog.id)
    #     self.assertEqual(len(table_mod_types_pg["table_rows_with_types_and_numbers"]), 2)#Core and elective (see above)
    #     self.assertEqual(table_mod_types_pg["table_rows_with_types_and_numbers"][0]["mod_type"], "core")
    #     self.assertEqual(table_mod_types_pg["table_rows_with_types_and_numbers"][1]["mod_type"], "elective") 
    #     self.assertEqual(table_mod_types_pg["total_hours_assigned_sem_1"], 25+75)#75 added by the newmmodule (150/2)
    #     self.assertEqual(table_mod_types_pg["total_hours_assigned_sem_2"], 95+75)#75 added by the newmmodule (150/2)
    #     #Re-check consistency
    #     self.assertEqual(table_mod_types_pg["total_hours_assigned_sem_1"], table_struct_pg["total_hours_sem_1"])
    #     self.assertEqual(table_mod_types_pg["total_hours_assigned_sem_2"], table_struct_pg["total_hours_sem_2"])
    #     self.assertEqual(table_mod_types["total_hours_assigned_sem_1"], table_struct["total_hours_sem_1"])
    #     self.assertEqual(table_mod_types["total_hours_assigned_sem_2"], table_struct["total_hours_sem_2"])

    #     #Now add one module in the PG programme as primary programme and UG as secondary programme
    #     mod_7_pg_and_ug = Module.objects.create(module_code = "M7-PG-AND-UG", module_title = "module 7 pg and ug", scenario_ref = wl_scen,\
    #                                            total_hours = 187, module_type = elective_mod, semester_offered= Module.SEM_1 , number_of_tutorial_groups=1,\
    #                                            primary_programme=pg_prog, secondary_programme=ug_prog)
    #     #assign to this module
    #     TeachingAssignment.objects.create(assigned_module = mod_7_pg_and_ug, assigned_lecturer = vice_dean, number_of_hours = 187, workload_scenario=wl_scen)
    #     #Now check. It should appear in both PG an d UG
    #     table_struct_pg = CalculateModuleHourlyTableForProgramme(wl_scen.id,pg_prog.id)
    #     table_struct_ug = CalculateModuleHourlyTableForProgramme(wl_scen.id,ug_prog.id)
    #     self.assertEqual(len(table_struct_pg["table_rows_with_mods_and_hours"]), 3)
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][0]["mod_code_sem_1"], "M4-PG-SEM1")
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][0]["hours_mod_sem_1"], 25)
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][0]["mod_code_sem_2"], "M5-PG-SEM2")
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][0]["hours_mod_sem_2"], 95)
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][1]["mod_code_sem_1"], "M6-PG-BOTHSEMS")
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][1]["hours_mod_sem_1"], 75)#150/2
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][1]["mod_code_sem_2"], "M6-PG-BOTHSEMS")
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][1]["hours_mod_sem_2"], 75)#150/2
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][2]["mod_code_sem_1"], "M7-PG-AND-UG")#The new module in PG!
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][2]["hours_mod_sem_1"], 187)#
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][2]["mod_code_sem_2"], "")
    #     self.assertEqual(table_struct_pg["table_rows_with_mods_and_hours"][2]["hours_mod_sem_2"], "")
    #     self.assertEqual(table_struct_pg["total_num_mods_sem_1"], 3)
    #     self.assertEqual(table_struct_pg["total_num_mods_sem_2"], 2)

    #     self.assertEqual(len(table_struct_ug["table_rows_with_mods_and_hours"]), 3)
    #     self.assertEqual(table_struct_ug["table_rows_with_mods_and_hours"][0]["mod_code_sem_1"], "M1-UG-SEM1")
    #     self.assertEqual(table_struct_ug["table_rows_with_mods_and_hours"][0]["hours_mod_sem_1"], 25+25+125)
    #     self.assertEqual(table_struct_ug["table_rows_with_mods_and_hours"][0]["mod_code_sem_2"], "M3-UG-SEM2")
    #     self.assertEqual(table_struct_ug["table_rows_with_mods_and_hours"][0]["hours_mod_sem_2"], 25)
    #     self.assertEqual(table_struct_ug["table_rows_with_mods_and_hours"][1]["mod_code_sem_1"], "M2-UG-SEM1")
    #     self.assertEqual(table_struct_ug["table_rows_with_mods_and_hours"][1]["hours_mod_sem_1"], 55)
    #     self.assertEqual(table_struct_ug["table_rows_with_mods_and_hours"][1]["mod_code_sem_2"], "")
    #     self.assertEqual(table_struct_ug["table_rows_with_mods_and_hours"][1]["hours_mod_sem_2"], "")
    #     self.assertEqual(table_struct_ug["table_rows_with_mods_and_hours"][2]["mod_code_sem_1"], "M7-PG-AND-UG")#The new module in UG as well!
    #     self.assertEqual(table_struct_ug["table_rows_with_mods_and_hours"][2]["hours_mod_sem_1"], 187)

    #     #And call the module type method again for both programmes
    #     table_mod_types_pg = CalculateModuleTypesTableForProgramme(wl_scen.id,pg_prog.id)
    #     table_mod_types_ug = CalculateModuleTypesTableForProgramme(wl_scen.id,ug_prog.id)
    #     self.assertEqual(len(table_mod_types_pg["table_rows_with_types_and_numbers"]), 2)#Core and elective (see above)
    #     self.assertEqual(table_mod_types_pg["table_rows_with_types_and_numbers"][0]["mod_type"], "core")
    #     self.assertEqual(table_mod_types_pg["table_rows_with_types_and_numbers"][1]["mod_type"], "elective") 
    #     self.assertEqual(table_mod_types_pg["total_hours_assigned_sem_1"], 25+75+187)#187 added by the new module
    #     self.assertEqual(table_mod_types_pg["total_hours_assigned_sem_2"], 95+75)#
    #     #Re-check consistency
    #     self.assertEqual(table_mod_types_pg["total_hours_assigned_sem_1"], table_struct_pg["total_hours_sem_1"])
    #     self.assertEqual(table_mod_types_pg["total_hours_assigned_sem_2"], table_struct_pg["total_hours_sem_2"])
    #     self.assertEqual(table_mod_types_ug["total_hours_assigned_sem_1"], table_struct_ug["total_hours_sem_1"])
    #     self.assertEqual(table_mod_types_ug["total_hours_assigned_sem_2"], table_struct_ug["total_hours_sem_2"])

    #     #We have no sub-programmes yet
    #     table_mod_types_ug_subprg = CalculateModuleHourlyTableForProgramme(wl_scen.id,ug_prog.id, requested_table_type.SUB_PROGRAMME)
    #     self.assertEqual(len(table_mod_types_ug_subprg["table_rows_with_mods_and_hours"]), 0)
    #     #Creat a sub-programme
    #     sub_prog_name ='SUB_PROG'
    #     sub_prog = SubProgrammeOffered.objects.create(sub_programme_name = sub_prog_name, main_programme = ug_prog)
    #     self.assertEqual(ProgrammeOffered.objects.all().count(), 2)
    #     self.assertEqual(SubProgrammeOffered.objects.all().count(), 1)
    #     self.assertEqual(Module.objects.filter(sub_programme=sub_prog).count(), 0)#No modules assigned yet
    #     #Edit 3 modules to be in the sub programme
    #     Module.objects.filter(id = mod_1_ug_sem_1.id).update( sub_programme = sub_prog)
    #     Module.objects.filter(id = mod_2_ug_sem_1.id).update( sub_programme = sub_prog)
    #     Module.objects.filter(id = mod_3_ug_sem_2.id).update( sub_programme = sub_prog)
    #     #Check the update worked
    #     self.assertEqual(Module.objects.filter(sub_programme=sub_prog).count(), 3)
    #     #Now generate the table for the sub-programme
    #     table_mod_hourly_ug_subprg = CalculateModuleHourlyTableForProgramme(wl_scen.id,sub_prog.id, requested_table_type.SUB_PROGRAMME)
    #     self.assertEqual(table_mod_hourly_ug_subprg["programme_name"], sub_prog_name)
    #     #it's 2 mods in sem 1 and one in sem 2. Table has two rows
    #     self.assertEqual(len(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"]),2)
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][0]["mod_code_sem_1"], "M1-UG-SEM1")
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][0]["hours_mod_sem_1"], 25+25+125)
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][0]["mod_code_sem_2"], "M3-UG-SEM2")
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][0]["hours_mod_sem_2"], 25)
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][1]["mod_code_sem_1"], "M2-UG-SEM1")
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][1]["hours_mod_sem_1"], 55)
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][1]["mod_code_sem_2"], "")
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][1]["hours_mod_sem_2"], "")
    #     self.assertEqual(table_mod_hourly_ug_subprg["total_hours_sem_1"], 25+25+125+55)
    #     self.assertEqual(table_mod_hourly_ug_subprg["total_hours_sem_2"], 25)

    #     #Create another sub-programme
    #     second_sub_prog_name ='SEC_SUB_PROG'
    #     second_sub_prog = SubProgrammeOffered.objects.create(sub_programme_name = second_sub_prog_name, main_programme = ug_prog)
    #     self.assertEqual(ProgrammeOffered.objects.all().count(), 2)
    #     self.assertEqual(SubProgrammeOffered.objects.all().count(), 2)
    #     self.assertEqual(Module.objects.filter(sub_programme=second_sub_prog).count(), 0)#No modules assigned yet
    #     #Edit 2 modules to be ALSO in this second sub_programme
    #     Module.objects.filter(id = mod_2_ug_sem_1.id).update( secondary_sub_programme = second_sub_prog)
    #     Module.objects.filter(id = mod_3_ug_sem_2.id).update( secondary_sub_programme = second_sub_prog)
    #     #Generate the table for the second sub_prog
    #     table_mod_hourly_ug_second_subprg = CalculateModuleHourlyTableForProgramme(wl_scen.id,second_sub_prog.id, requested_table_type.SUB_PROGRAMME)
    #     #it's 1 mod in sem 1 and one in sem 2. Table has one row
    #     self.assertEqual(len(table_mod_hourly_ug_second_subprg["table_rows_with_mods_and_hours"]),1)
    #     self.assertEqual(table_mod_hourly_ug_second_subprg["table_rows_with_mods_and_hours"][0]["mod_code_sem_1"], "M2-UG-SEM1")
    #     self.assertEqual(table_mod_hourly_ug_second_subprg["table_rows_with_mods_and_hours"][0]["hours_mod_sem_1"], 55)
    #     self.assertEqual(table_mod_hourly_ug_second_subprg["table_rows_with_mods_and_hours"][0]["mod_code_sem_2"], "M3-UG-SEM2")
    #     self.assertEqual(table_mod_hourly_ug_second_subprg["table_rows_with_mods_and_hours"][0]["hours_mod_sem_2"], 25)
    #     self.assertEqual(table_mod_hourly_ug_second_subprg["total_hours_sem_1"], 55)
    #     self.assertEqual(table_mod_hourly_ug_second_subprg["total_hours_sem_2"], 25)
        
    #     #also check that the main sub-propgramme is unchanged
    #     table_mod_hourly_ug_subprg = CalculateModuleHourlyTableForProgramme(wl_scen.id,sub_prog.id, requested_table_type.SUB_PROGRAMME)
    #     self.assertEqual(table_mod_hourly_ug_subprg["programme_name"], sub_prog_name)
    #     #it's 2 mods in sem 1 and one in sem 2. Table has two rows
    #     self.assertEqual(len(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"]),2)
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][0]["mod_code_sem_1"], "M1-UG-SEM1")
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][0]["hours_mod_sem_1"], 25+25+125)
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][0]["mod_code_sem_2"], "M3-UG-SEM2")
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][0]["hours_mod_sem_2"], 25)
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][1]["mod_code_sem_1"], "M2-UG-SEM1")
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][1]["hours_mod_sem_1"], 55)
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][1]["mod_code_sem_2"], "")
    #     self.assertEqual(table_mod_hourly_ug_subprg["table_rows_with_mods_and_hours"][1]["hours_mod_sem_2"], "")
    #     self.assertEqual(table_mod_hourly_ug_subprg["total_hours_sem_1"], 25+25+125+55)
    #     self.assertEqual(table_mod_hourly_ug_subprg["total_hours_sem_2"], 25)

    # def testCalculateEmploymentTracksTable(self):
    #     self.assertEqual(EmploymentTrack.objects.all().count(), 0)
    #     tbl = CalculateEmploymentTracksTable()
    #     self.assertEqual(len(tbl),0)
    #     new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
    #     EmploymentTrack.objects.create(track_name = "track_1", track_adjustment = 2,faculty=new_fac)
    #     self.assertEqual(EmploymentTrack.objects.all().count(), 1)
    #     tbl = CalculateEmploymentTracksTable()
    #     self.assertEqual(len(tbl),1)
    #     self.assertEqual(tbl[0]['track_name'],'track_1')
    #     self.assertEqual(tbl[0]['track_adjustment'],2)
    
    # def testCalculateServiceRolesTable(self):
    #     new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
    #     self.assertEqual(ServiceRole.objects.all().count(), 0)
    #     tbl = CalculateServiceRolesTable()
    #     self.assertEqual(len(tbl),0)
    #     ServiceRole.objects.create(role_name = "role_1", role_adjustment = 2, faculty=new_fac)
    #     self.assertEqual(ServiceRole.objects.all().count(), 1)
    #     tbl = CalculateServiceRolesTable()
    #     self.assertEqual(len(tbl),1)
    #     self.assertEqual(tbl[0]['role_name'],'role_1')
    #     self.assertEqual(tbl[0]['role_adjustment'],2)

    # def testCalculateAllDepartmentsTable(self):
    #     self.assertEqual(Department.objects.all().count(), 0)
    #     tbl = CalculateDepartmentTable()
    #     self.assertEqual(len(tbl),0)
    #     first_fac = Faculty.objects.create(faculty_name = "first fac", faculty_acronym = "FRTE")
    #     Department.objects.create(department_name = "test_dept", department_acronym = "ACR", faculty = first_fac)
    #     self.assertEqual(Department.objects.all().count(), 1)
    #     tbl = CalculateDepartmentTable()
    #     self.assertEqual(len(tbl),1)
    #     self.assertEqual(tbl[0]['department_name'],'test_dept')
    #     self.assertEqual(tbl[0]['department_acronym'],'ACR')
    #     self.assertEqual(tbl[0]['faculty'],'FRTE')

    # def test_assigned_hours_calculation_method(self):
    #     self.assertEqual(CalculateNumHoursBasedOnWeeklyInfo(0,0,1,2),0)
    #     self.assertEqual(CalculateNumHoursBasedOnWeeklyInfo(0,0,0,2),0)
    #     self.assertEqual(CalculateNumHoursBasedOnWeeklyInfo(1,1,0,2),0)
    #     self.assertEqual(CalculateNumHoursBasedOnWeeklyInfo(1,0,0,2),0)
    #     self.assertEqual(CalculateNumHoursBasedOnWeeklyInfo(2,1,1,2),int(4))
    #     self.assertEqual(CalculateNumHoursBasedOnWeeklyInfo(2,1,2,2),int(8))
        
    # def testReadInCsvFileForProfessors(self):
    #     #Regular file. Two columns, no header
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/profs/regular_no_header.csv'), file_type = csv_file_type.PROFESSOR_FILE)
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 3)
    #     self.assertEqual(len(data_read[1]), 3)
    #     self.assertEqual(data_read[0][0], 'John')
    #     self.assertEqual(data_read[0][1], 'Paul')
    #     self.assertEqual(data_read[0][2], 'Chris')
    #     self.assertEqual(data_read[1][0], '0.5')
    #     self.assertEqual(data_read[1][1], '1')
    #     self.assertEqual(data_read[1][2], '0.8')

    #     #Regular file. Two columns, no header, one extra new line at the end of the file
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/profs/regular_no_header_newline_at_end.csv'))
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 3)
    #     self.assertEqual(len(data_read[1]), 3)
    #     self.assertEqual(data_read[0][0], 'John')
    #     self.assertEqual(data_read[0][1], 'Paul')
    #     self.assertEqual(data_read[0][2], 'Chris')
    #     self.assertEqual(data_read[1][0], '0.5')
    #     self.assertEqual(data_read[1][1], '1')
    #     self.assertEqual(data_read[1][2], '0.8')

    #     #Regular file. Two columns, no header, missing one line in the middle
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/profs/regular_no_header_missing_line_in_the_middle.csv'))
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 2)
    #     self.assertEqual(len(data_read[1]), 2)
    #     self.assertEqual(data_read[0][0], 'John')
    #     self.assertEqual(data_read[0][1], 'Chris')
    #     self.assertEqual(data_read[1][0], '0.5')
    #     self.assertEqual(data_read[1][1], '0.8')

    #     #Irregular file. Two columns, no header, missing one name (but appt is there)
    #     #Expected behaviour is to ignore the line, even if appt is there
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/profs/missing_one_name_no_header.csv'))
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 2)
    #     self.assertEqual(len(data_read[1]), 2)
    #     self.assertEqual(data_read[0][0], 'Paul')
    #     self.assertEqual(data_read[0][1], 'Chris')
    #     self.assertEqual(data_read[1][0], '1')
    #     self.assertEqual(data_read[1][1], '0.8')

    #      #Irregular file. Two columns, no header, missing one name (but appt is there). Instead of the name, a bunch of white spaces are there
    #     #Expected behaviour is to ignore the line, even if appt is there and the name is just white spaces
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/profs/missing_one_name_spaces_instead_no_header.csv'))
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 2)
    #     self.assertEqual(len(data_read[1]), 2)
    #     self.assertEqual(data_read[0][0], 'Paul')
    #     self.assertEqual(data_read[0][1], 'Chris')
    #     self.assertEqual(data_read[1][0], '1')
    #     self.assertEqual(data_read[1][1], '0.8')       

    #     #Non existing file. Error flag true and data key not even in dictionary
    #     invalid = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/profs/hellohello.csv'))
    #     self.assertEqual(invalid["errors"], True)
    #     self.assertEqual("data" in invalid.keys(), False)

    #     #Empty file. No errors, but data is empty
    #     empty = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/profs/empty_file.csv'))
    #     self.assertEqual(empty["errors"], False)
    #     data_read = empty["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 0)
    #     self.assertEqual(len(data_read[1]), 0)

    #     #File with only white spaces in it. No errors, but data is empty
    #     empty = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/profs/empty_file_whitespaces.csv'))
    #     self.assertEqual(empty["errors"], False)
    #     data_read = empty["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 0)
    #     self.assertEqual(len(data_read[1]), 0)

    #     #Regular file. Two columns, one line header
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/profs/regular_one_line_header.csv'), skip_header=1)
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 3)
    #     self.assertEqual(len(data_read[1]), 3)
    #     self.assertEqual(data_read[0][0], 'John')
    #     self.assertEqual(data_read[0][1], 'Paul')
    #     self.assertEqual(data_read[0][2], 'Chris')
    #     self.assertEqual(data_read[1][0], '0.5')
    #     self.assertEqual(data_read[1][1], '1')
    #     self.assertEqual(data_read[1][2], '0.8')

    #     #Regular file. Two columns, two lines header
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/profs/regular_two_lines_header.csv'), skip_header=2)
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 3)
    #     self.assertEqual(len(data_read[1]), 3)
    #     self.assertEqual(data_read[0][0], 'John')
    #     self.assertEqual(data_read[0][1], 'Paul')
    #     self.assertEqual(data_read[0][2], 'Chris')
    #     self.assertEqual(data_read[1][0], '0.5')
    #     self.assertEqual(data_read[1][1], '1')
    #     self.assertEqual(data_read[1][2], '0.8')

    #     #irregular file. No header. One guy has appt > 1
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/profs/appt_greater_than_one.csv'))
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 3)
    #     self.assertEqual(len(data_read[1]), 3)
    #     self.assertEqual(data_read[0][0], 'John')
    #     self.assertEqual(data_read[0][1], 'Paul')
    #     self.assertEqual(data_read[0][2], 'Chris')
    #     self.assertEqual(data_read[1][0], '1')
    #     self.assertEqual(data_read[1][1], '1')#Turned to 1 from 3.5 in the file
    #     self.assertEqual(data_read[1][2], '0.2')

    #     #Irregular file. This file (one line header) has two columns, but the second (appointment) column has some missing values
    #     #The expected behaviour is to turn missing values into "1"
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/profs/missing_some_appts.csv'), skip_header=1)
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 3)
    #     self.assertEqual(len(data_read[1]), 3)
    #     self.assertEqual(data_read[0][0], 'John')
    #     self.assertEqual(data_read[0][1], 'Paul')
    #     self.assertEqual(data_read[0][2], 'Chris')
    #     self.assertEqual(data_read[1][0], '0.5')
    #     self.assertEqual(data_read[1][1], '1')#Missing turned to 1
    #     self.assertEqual(data_read[1][2], '1')#Missing turned to 1

    #     #Irregular file. This file (one line header) has two columns, but the second (appointment) column has some missing values
    #     #Instead of missing values, a series of white spaces are inserted
    #     #The expected behaviour is to turn missing values into "1"
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/profs/missing_some_appts_white_spaces.csv'), skip_header=1)
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 3)
    #     self.assertEqual(len(data_read[1]), 3)
    #     self.assertEqual(data_read[0][0], 'John')
    #     self.assertEqual(data_read[0][1], 'Paul')
    #     self.assertEqual(data_read[0][2], 'Chris')
    #     self.assertEqual(data_read[1][0], '0.5')
    #     self.assertEqual(data_read[1][1], '1')#Missing turned to 1
    #     self.assertEqual(data_read[1][2], '1')#Missing turned to 1

    #     #Irregular file. This file (one line header) has two columns, but the second (appointment) column has all missing values
    #     #The expected behaviour is to turn missing values into "1"
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/profs/missing_all_appts.csv'), skip_header=1)
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 3)
    #     self.assertEqual(len(data_read[1]), 3)
    #     self.assertEqual(data_read[0][0], 'John')
    #     self.assertEqual(data_read[0][1], 'Paul')
    #     self.assertEqual(data_read[0][2], 'Chris')
    #     self.assertEqual(data_read[1][0], '1')#Missing turned to 1
    #     self.assertEqual(data_read[1][1], '1')#Missing turned to 1
    #     self.assertEqual(data_read[1][2], '1')#Missing turned to 1

    #     #Irregular file. This file is just one column of names, no appointments and no headers
    #     #The expected behaviour is to turn missing values into "1"
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/profs/one_column_of_names.csv'),file_type = csv_file_type.PROFESSOR_FILE )
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 3)
    #     self.assertEqual(len(data_read[1]), 3)
    #     self.assertEqual(data_read[0][0], 'John')
    #     self.assertEqual(data_read[0][1], 'Paul')
    #     self.assertEqual(data_read[0][2], 'Chris')
    #     self.assertEqual(data_read[1][0], '1')#Missing turned to 1
    #     self.assertEqual(data_read[1][1], '1')#Missing turned to 1
    #     self.assertEqual(data_read[1][2], '1')#Missing turned to 1

    # def testReadInCsvFileForModules(self):
    #     #Regular file. Two columns, no header
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/mods/regular_file_no_headers.csv'), file_type = csv_file_type.MODULE_FILE)
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 3)
    #     self.assertEqual(len(data_read[1]), 3)
    #     self.assertEqual(data_read[0][0], 'BN1111')
    #     self.assertEqual(data_read[0][1], 'BN2102')
    #     self.assertEqual(data_read[0][2], 'BN2201')
    #     self.assertEqual(data_read[1][0], 'Module 1')
    #     self.assertEqual(data_read[1][1], 'Module 2')
    #     self.assertEqual(data_read[1][2], 'Module 3')

    #     #File with one line missing in the middle
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/mods/missing_one_line_no_headers.csv'), file_type = csv_file_type.MODULE_FILE)
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 2)
    #     self.assertEqual(len(data_read[1]), 2)
    #     self.assertEqual(data_read[0][0], 'BN1111')        
    #     self.assertEqual(data_read[0][1], 'BN2201')
    #     self.assertEqual(data_read[1][0], 'Module 1')
    #     self.assertEqual(data_read[1][1], 'Module 3')

    #     #File with one module title missing
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/mods/missing_one_module_title_no_headers.csv'), file_type = csv_file_type.MODULE_FILE)
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 3)
    #     self.assertEqual(len(data_read[1]), 3)
    #     self.assertEqual(data_read[0][0], 'BN1111')
    #     self.assertEqual(data_read[0][1], 'BN2102')
    #     self.assertEqual(data_read[0][2], 'BN2201')
    #     self.assertEqual(data_read[1][0], 'Module 1')
    #     self.assertEqual(data_read[1][1], 'No title') #Turned to a default because absent in file
    #     self.assertEqual(data_read[1][2], 'Module 3')
        
    #     #File with one column of codes, all  titles missing
    #     all_results = ReadInCsvFile(os.path.join(os.path.dirname(__file__), 'data/mods/one_column_of_codes.csv'), file_type = csv_file_type.MODULE_FILE)
    #     self.assertEqual(all_results["errors"], False)
    #     data_read = all_results["data"]
    #     self.assertEqual(len(data_read), 2)
    #     self.assertEqual(len(data_read[0]), 3)
    #     self.assertEqual(len(data_read[1]), 3)
    #     self.assertEqual(data_read[0][0], 'BN1111')
    #     self.assertEqual(data_read[0][1], 'BN2102')
    #     self.assertEqual(data_read[0][2], 'BN2201')
    #     self.assertEqual(data_read[1][0], 'No title') #Turned to a default because absent in file
    #     self.assertEqual(data_read[1][1], 'No title') #Turned to a default because absent in file
    #     self.assertEqual(data_read[1][2], 'No title') #Turned to a default because absent in file

    # #def test_module_hours_calculation_method(self):
        
    #     #self.assertAlmostEqual(CalculateTotalModuleHours(1,"not yet"),Decimal(39))

        
        
        
        