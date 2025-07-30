from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *

from workload_app.models import Faculty,Lecturer, Module, TeachingAssignment,WorkloadScenario, ModuleType,\
      Department,EmploymentTrack,ServiceRole,Academicyear, UniversityStaff,TeachingAssignmentType


class TestLecturer(TestCase):
    def setup_user(self):
        #The test client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
        self.user.is_superuser = True
        self.user.save()
        uni_user = UniversityStaff.objects.create(user = self.user, department=None,faculty=None)
    def test_add_lecturer_method(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        #Test the GET
        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        new_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        def_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        new_track = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 0.8, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertContains(response, "Workload")

        new_scen = WorkloadScenario.objects.create(label='test_scen', academic_year=acad_year, dept = new_dept)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues

        #Test the POST now
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'bob','fraction_appointment' : '0.5',    \
                                                                'service_role' : def_role.id,'employment_track': new_track.id,'is_external': False, 'fresh_record' : True})
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues

        obtained_profs_list = Lecturer.objects.all()
        self.assertEqual(obtained_profs_list.count(),1)
        self.assertEqual(obtained_profs_list.filter(name='bob').exists(),True)
        
    def test_add_remove_professor_method(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        new_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        def_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        new_track = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 0.8, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertContains(response, "Workload")

        #Create a new scenario
        new_scen = WorkloadScenario.objects.create(label='test_scen', academic_year=acad_year, dept = new_dept)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        
        #Add a professor via the form in the modal        
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'bob','fraction_appointment' : '0.25',    \
                                                                'service_role' : def_role.id, 'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        
        all_profs = Lecturer.objects.all()
        self.assertEqual(all_profs.count(),1)#1
        self.assertEqual(all_profs[0].name,'bob')
        self.assertAlmostEqual(all_profs[0].fraction_appointment,Decimal(0.25))
        
        #Remove the professor we just added
        self.client.post(reverse('workload_app:remove_professor',  kwargs={'workloadscenario_id': new_scen.id}), {'select_professor_to_remove': all_profs[0].id, 'wipe_out_from_table' : True})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        
        all_profs = Lecturer.objects.all()
        self.assertEqual(all_profs.count(),0)

    def test_add_lecturer_same_name(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        def_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        new_track = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 0.8, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertContains(response, "Workload")

        #Create a new scenario
        new_scen = WorkloadScenario.objects.create(label='test_scen', dept = first_dept, academic_year = acad_year)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues

        #Test the POST now
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'bob','fraction_appointment' : '0.5', \
                                                                'service_role' : def_role.id,'employment_track': new_track.id, 'is_external': False,   'fresh_record' : True})
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues

        obtained_profs_list = Lecturer.objects.all()
        self.assertEqual(obtained_profs_list.count(),1)
        self.assertEqual(obtained_profs_list.filter(name='bob').exists(),True)
        
        #Now add Bob again
        response = self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'bob','fraction_appointment' : '0.5',    \
                                                                            'service_role' : def_role.id,'employment_track': new_track.id,'is_external': False,'fresh_record' : True})        
        self.assertEqual(response.status_code, 200) 
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        obtained_profs_list = Lecturer.objects.all()
        self.assertEqual(obtained_profs_list.count(),1)
        self.assertEqual(obtained_profs_list.filter(name='bob').exists(),True)
        
        #Now create another scenario
        scen_name_2 = 'scen_2'
        acad_year = Academicyear.objects.create(start_year=2200)
        self.client.post(reverse('workload_app:manage_scenario'), {'label': scen_name_2, 'dept' : first_dept.id, 'copy_from': '', 'status': WorkloadScenario.DRAFT, 'fresh_record' : True, 'academic_year' : acad_year.id});
        obtained_profs_list = Lecturer.objects.all()
        new_scen.refresh_from_db()
        
        self.assertEqual(obtained_profs_list.count(),1)
        self.assertEqual(obtained_profs_list.filter(name='bob').exists(),True)
        self.assertEqual(obtained_profs_list.filter(name='bob').filter(workload_scenario__label=scen_name_2).exists(),False)
        
        #Now try adding bob again in the new scenario
        #ADDITION SHOULD WORK

        #Go to new scenario (and activate it)
        scen_2 = WorkloadScenario.objects.filter(label=scen_name_2)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scen_2.get().id}))
        
        #add now
        response = self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scen_2.get().id}),{'name':'bob','fraction_appointment' : '0.5',   \
                                                                            'service_role' : def_role.id,'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})        
        
        #check after addition
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scen_2.get().id}))
        self.assertEqual(response.status_code, 200) #No issues
        obtained_profs_list = Lecturer.objects.all()
        self.assertEqual(obtained_profs_list.count(),2)#Now 2 because addition worked
        self.assertEqual(obtained_profs_list.filter(name='bob').exists(),True)
        self.assertEqual(obtained_profs_list.filter(name='bob').count(),2)
        self.assertEqual(obtained_profs_list.filter(name='bob').filter(workload_scenario__label=scen_name_2).exists(),True)
        self.assertEqual(obtained_profs_list.filter(name='bob').filter(workload_scenario__label=scen_name_2).count(),1)
        self.assertEqual(Lecturer.objects.filter(is_external = True).count(),0)

        #add a prof who ise xternal
        response = self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scen_2.get().id}),{'name':'bob_external','fraction_appointment' : '0.5',   \
                                                                            'service_role' : def_role.id,'employment_track': new_track.id, 'is_external': True, 'fresh_record' : True})        
        
        #check after addition
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scen_2.get().id}))
        self.assertEqual(response.status_code, 200) #No issues
        obtained_profs_list = Lecturer.objects.all()
        self.assertEqual(obtained_profs_list.count(),3)#Now 2 because addition worked + external
        self.assertEqual(obtained_profs_list.filter(name='bob').exists(),True)
        self.assertEqual(obtained_profs_list.filter(name='bob').count(),2)
        self.assertEqual(obtained_profs_list.filter(name='bob').filter(workload_scenario__label=scen_name_2).exists(),True)
        self.assertEqual(obtained_profs_list.filter(name='bob').filter(workload_scenario__label=scen_name_2).count(),1)
        self.assertEqual(Lecturer.objects.filter(is_external = True).count(),1)
        

    def test_edit_existing_lecturer(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        def_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        new_track = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 0.8, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertContains(response, "Workload")

        #Create a new scenario
        new_scen = WorkloadScenario.objects.create(label='test_scen', academic_year = acad_year, dept=first_dept)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues

        #Test the POST for two profs
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'bob','fraction_appointment' : '0.7',    \
                                                                'service_role' : def_role.id,'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'fred','fraction_appointment' : '0.5',    \
                                                                'service_role' : def_role.id,'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues

        obtained_profs_list = Lecturer.objects.all()
        self.assertEqual(obtained_profs_list.count(),2)
        self.assertEqual(obtained_profs_list.filter(name='bob').exists(),True)
        self.assertEqual(obtained_profs_list.filter(name='fred').exists(),True)
        
        #Give bob a mod to teach
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE",department=first_dept)
        mod_code_1 = 'AS101'
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    

        module_1 = Module.objects.filter(module_code = mod_code_1).get() 
        
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=new_fac)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': new_scen.id}), data = {'select_lecturer': obtained_profs_list.filter(name='bob').get().id, \
                 'select_module': module_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'36'})
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),1)
        
        #Now edit Bob - KEY CHANGE: appointment adjustment from 2 to 1
        response = self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'bob','fraction_appointment' : '0.7',    \
                                                                        'service_role' : def_role.id,'employment_track': new_track.id, 'is_external': False,'fresh_record' : False})        
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        obtained_profs_list = Lecturer.objects.all()
        self.assertEqual(obtained_profs_list.count(),2)
        self.assertEqual(obtained_profs_list.filter(name='bob').exists(),True)
        self.assertEqual(obtained_profs_list.filter(name='fred').exists(),True)
        
        #Check that everything else stays the same
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),1)
        
        #Edit again with out-of-range appointment (0.7 to 1.5)
        response = self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'bob','fraction_appointment' : '1.5',    \
                                                                            'service_role' : def_role.id,'employment_track': new_track.id,'is_external': False, 'fresh_record' : False})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        #The change should not take efefct because the fraction appointment is out of range
        self.assertEqual(obtained_profs_list.filter(fraction_appointment='0.7').exists(),True)
        self.assertEqual(obtained_profs_list.filter(fraction_appointment='1.5').exists(),False)
    
    def test_edit_existing_lecturer_different_scenarios(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
    
        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        def_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        new_track = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 0.8, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertContains(response, "Workload")

        #create two scenarios
        scen_name_1 = 'scen_1'
        scenario_1 = WorkloadScenario.objects.create(label=scen_name_1, dept = first_dept, academic_year=acad_year)

        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues

        #Test the POST
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_1.id}),{'name':'bob','fraction_appointment' : '0.7',    \
                                                                'service_role' : def_role.id,'employment_track': new_track.id,'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_1.id}),{'name':'fred','fraction_appointment' : '0.5',    \
                                                                'service_role' : def_role.id,'employment_track': new_track.id,'is_external': False,'fresh_record' : True})
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues

        obtained_profs_list = Lecturer.objects.all()
        self.assertEqual(obtained_profs_list.count(),2)
        self.assertEqual(obtained_profs_list.filter(name='bob').filter(workload_scenario__label = scen_name_1).exists(),True)
        self.assertEqual(obtained_profs_list.filter(name='fred').filter(workload_scenario__label = scen_name_1).exists(),True)
        self.assertEqual(obtained_profs_list.filter(name='bob').filter(workload_scenario__label = scen_name_1).count(),1)
        self.assertEqual(obtained_profs_list.filter(name='fred').filter(workload_scenario__label = scen_name_1).count(),1)
        
        scen_name_2 = 'scen_2'
        #Now create a new scenario, copying from the existing one
        acad_year = Academicyear.objects.create(start_year=2200)
        self.client.post(reverse('workload_app:manage_scenario'), {'label': scen_name_2, 'dept' : first_dept.id, 'copy_from': scenario_1.id, 'status': WorkloadScenario.DRAFT, 'fresh_record' : True, 'academic_year' : acad_year.id});
        scenario_2 = WorkloadScenario.objects.filter(label=scen_name_2).get()
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        scenario_1.refresh_from_db();
        scenario_2.refresh_from_db();

        self.assertEqual(WorkloadScenario.objects.filter(label=scen_name_2).exists(), True)
        self.assertEqual(WorkloadScenario.objects.filter(label=scen_name_2).count(), 1)
        
        obtained_profs_list = Lecturer.objects.all()
        self.assertEqual(obtained_profs_list.count(),4)
        self.assertEqual(obtained_profs_list.filter(name='bob').filter(workload_scenario__label = scen_name_2).exists(),True)
        self.assertEqual(obtained_profs_list.filter(name='fred').filter(workload_scenario__label = scen_name_2).exists(),True)
        self.assertEqual(obtained_profs_list.filter(name='bob').filter(workload_scenario__label = scen_name_2).count(),1)
        self.assertEqual(obtained_profs_list.filter(name='fred').filter(workload_scenario__label = scen_name_2).count(),1)
        
        #Now edit bob in scenario 2 (the active one) - KEY CHANNGE: appointment adjustment from 2 to 1
        response = self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_2.id}),{'name':'bob','fraction_appointment' : '0.7',    \
                                                                            'service_role' : def_role.id,'employment_track': new_track.id, 'is_external': False, 'fresh_record' : False})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        obtained_profs_list = Lecturer.objects.all()
        profs_in_scen_2 = Lecturer.objects.filter(workload_scenario__label = scen_name_2)
        self.assertEqual(profs_in_scen_2.filter(name='bob').exists(),True)
        self.assertEqual(profs_in_scen_2.filter(name='fred').exists(),True)
        
        profs_in_scen_1 = Lecturer.objects.filter(workload_scenario__label = scen_name_1)
        
        self.assertEqual(profs_in_scen_1.filter(name='bob').exists(),True)
        self.assertEqual(profs_in_scen_1.filter(name='fred').exists(),True)
        
    def test_remove_prof_with_assignments(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        def_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        new_track = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 0.8, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertContains(response, "Workload")

        acad_year_2 = Academicyear.objects.create(start_year=2345)        
        #create two scenarios
        scen_name_1 = 'scen_1'
        scenario_1 = WorkloadScenario.objects.create(label=scen_name_1, academic_year=acad_year, dept=first_dept)
        
        scen_name_2 = 'scen_2'
        scenario_2 = WorkloadScenario.objects.create(label=scen_name_2, academic_year=acad_year_2, dept=first_dept)
        
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_2.id}),{'name':'normal_lecturer','fraction_appointment' : '0.7',    'service_role' : def_role.id, 'employment_track': new_track.id,'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_2.id}),{'name':'educator_track','fraction_appointment' : '1.0',    'service_role' : def_role.id,'employment_track': new_track.id,'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_2.id}),{'name':'vice_dean','fraction_appointment' : '0.5',    'service_role' : def_role.id,'employment_track': new_track.id,'is_external': False,'fresh_record' : True})
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department=first_dept)
        
        mod_code_1 = 'AS101'
        mod_code_2 = 'AS201'
        mod_code_3 = 'AS301'
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_2.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_2.id}), {'module_code': mod_code_2, 'module_title' : 'module 2', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_2.id}), {'module_code': mod_code_3, 'module_title' : 'module 3', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.assertEqual(Module.objects.all().count(),3)
        
        module_1 = Module.objects.filter(module_code = mod_code_1).get()
        module_2 = Module.objects.filter(module_code = mod_code_2).get()
        module_3 = Module.objects.filter(module_code = mod_code_3).get()
        
        educator_track = Lecturer.objects.filter(name = 'educator_track').get()
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        all_profs = Lecturer.objects.all()
        self.assertEqual(all_profs.count(),3)
        self.assertEqual(all_profs.filter(workload_scenario__label = scen_name_2).count(),3)
        
        #Add an assignment
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=new_fac)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_2.id}), data = {'select_lecturer': educator_track.id, \
                 'select_module': module_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'56'})
                
        all_mods  = Module.objects.all();
        self.assertEqual(all_mods.count(),3)#3 mods in total (unchanged)
        
        #Now remove one that had modules assigned
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),1)#One left before removal of the professor
        #Now remove one that had modules assigned
        self.client.post(reverse('workload_app:remove_professor',  kwargs={'workloadscenario_id': scenario_2.id}), {'select_professor_to_remove': educator_track.id,'wipe_out_from_table' : False})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_profs = Lecturer.objects.all()
        self.assertEqual(all_profs.count(),3)#should still be 3 as prof is not wiped

        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),0)#Should be zero by now
        
        #Add an assignment again - This is in scenario 2
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_2.id}), data = {'select_lecturer': educator_track.id, \
                 'select_module': module_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'56'})
        
        #Switch to senario 1
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        scenario_1.refresh_from_db()
        scenario_2.refresh_from_db()
        
        #add the same guy to scenario 1
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_1.id}),{'name':'educator_track',\
                                'fraction_appointment' : '1.0',    'service_role' : def_role.id, 'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        educator_track_scen_1 = Lecturer.objects.filter(name = 'educator_track').filter(workload_scenario__label=scen_name_1).get()
        #and add two same modules to scen 1 as well
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_2, 'module_title' : 'module 2', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_3, 'module_title' : 'module 3', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.assertEqual(Module.objects.all().count(),6)
        self.assertEqual(Module.objects.filter(scenario_ref__label=scen_name_1).count(),3)
        
        module_1_scen_1 = Module.objects.filter(module_code = mod_code_1).filter(scenario_ref__label=scen_name_1).get()
        module_2_scen_1 = Module.objects.filter(module_code = mod_code_2).filter(scenario_ref__label=scen_name_1).get()
        module_3_scen_1 = Module.objects.filter(module_code = mod_code_3).filter(scenario_ref__label=scen_name_1).get()
        
        #Add 2 assignments to the same guy, but in scenario 1

        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), data = {'select_lecturer': educator_track_scen_1.id, \
                 'select_module': module_3_scen_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'96'})
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), data = {'select_lecturer': educator_track_scen_1.id, \
                 'select_module': module_1_scen_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'196'})
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),3)#Should be 3 by now
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(teaching_assignments_for_active_scen.count(),2)
        
        #Now, from scenario 1, we remove the guy's assignments 
        self.client.post(reverse('workload_app:remove_professor',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_professor_to_remove': educator_track.id,'wipe_out_from_table' : False})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),3)
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(teaching_assignments_for_active_scen.count(),2)
        

        #Switch to senario 2
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        scenario_1.refresh_from_db()
        scenario_2.refresh_from_db()
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),3)#Same as above
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_2.id)
        self.assertEqual(teaching_assignments_for_active_scen.count(),1)#One assignment in scenario 2

    