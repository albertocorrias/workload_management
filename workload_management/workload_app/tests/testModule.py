from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *
from workload_app.models import Lecturer, Module, TeachingAssignment,WorkloadScenario, ModuleType, \
    Department,EmploymentTrack,ServiceRole, Faculty, Academicyear, ProgrammeOffered, UniversityStaff, TeachingAssignmentType
from workload_app.forms import RemoveModuleForm
from workload_app.global_constants import DEFAULT_WORKLOAD_NAME,DEFAULT_MODULE_TYPE_NAME

class TestModule(TestCase):
    def setup_user(self):
        #The test client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
        self.user.is_superuser = True
        self.user.save()
        uni_user = UniversityStaff.objects.create(user = self.user, department=None,faculty=None)

    def test_add_remove_module_method(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        #Create a new scenario
        new_scen = WorkloadScenario.objects.create(label='test_scen',dept=first_dept, academic_year=acad_year)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues

        mod_table = response.context['mod_table']
        self.assertEqual(len(mod_table),0)
        self.assertEqual(Module.objects.all().count(),0)#0 mods to start with
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department=first_dept)
        #Add a new module
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': 'XXXX1', 'module_title' : 'testing', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods  = Module.objects.all();
        self.assertEqual(all_mods.count(),1)# mods now after this addition
        self.assertEqual(all_mods.filter(module_code='XXXX1').exists(),True)
        self.assertEqual(all_mods.filter(module_title='testing').exists(),True)
        self.assertEqual(all_mods.filter(compulsory_in_primary_programme=True).count(),0)
        self.assertEqual(all_mods.filter(compulsory_in_primary_programme=False).count(),1)#Covers defaut value
        self.assertEqual(all_mods.filter(compulsory_in_secondary_programme=True).count(),0)
        self.assertEqual(all_mods.filter(compulsory_in_secondary_programme=False).count(),1)#Covers defaut value
        self.assertEqual(all_mods.filter(compulsory_in_tertiary_programme=True).count(),0)
        self.assertEqual(all_mods.filter(compulsory_in_tertiary_programme=False).count(),1)#Covers defaut value
        self.assertEqual(all_mods.filter(students_year_of_study__isnull=True).count(),1)#
        self.assertEqual(all_mods.filter(primary_programme__isnull=True).count(),1)
        self.assertEqual(all_mods.filter(secondary_programme__isnull=True).count(),1)
        self.assertEqual(all_mods.filter(sub_programme__isnull=True).count(),1)
        self.assertEqual(all_mods.filter(secondary_sub_programme__isnull=True).count(),1)
        #Remove the module we just added
        self.client.post(reverse('workload_app:remove_module',  kwargs={'workloadscenario_id': new_scen.id}), {'select_module_to_remove': all_mods[0].id,'wipe_from_table' : RemoveModuleForm.REMOVE_COMPLETELY})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(Module.objects.all().count(),0)
    
    def test_add_remove_module_type(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(ModuleType.objects.all().count(),0)#
        
        #Create a new scenario
        new_scen = WorkloadScenario.objects.create(label='test_scen', dept=first_dept, academic_year=acad_year)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues    
        
        #Add a new module type
        self.client.post(reverse('workload_app:manage_module_type', kwargs={'department_id': first_dept.id}), {'type_name': 'TEST'})
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        all_types = ModuleType.objects.all()
        self.assertEqual(all_types.count(),1)#1
        self.assertEqual(all_types.filter(type_name='TEST').exists(),True)
        self.assertEqual(all_types.filter(type_name='TEST').count(),1)
    
        #Remove the module type we just added
        self.client.post(reverse('workload_app:remove_module_type',kwargs={'department_id': first_dept.id}), {'select_module_type_to_remove': all_types[0].id})
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(ModuleType.objects.all().count(),0)

    def test_add_remove_module_method_wipeout(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        #Create a new scenario
        new_scen = WorkloadScenario.objects.create(label='test_scen', dept = first_dept, academic_year=acad_year)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues

        mod_table = response.context['mod_table']
        self.assertEqual(len(mod_table),0)
        self.assertEqual(Module.objects.all().count(),0)#0 mods to start with
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department=first_dept)
        
        #Add a new module
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': 'XXXX1', 'module_title' : 'testing', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})
        normal_lecturer = Lecturer.objects.create(name="normal_lecturer",fraction_appointment=0.7, employment_track=track_def,service_role=srvc_role, workload_scenario=new_scen)
        
        all_mods  = Module.objects.all()
        #make an assignment
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=new_fac)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': new_scen.id}), data = {'select_lecturer': normal_lecturer.id, \
                 'select_module': all_mods.get().id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'36'})
                
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods  = Module.objects.all();
        all_assignments = TeachingAssignment.objects.all();
        self.assertEqual(all_mods.count(),1)# mods now after this addition
        self.assertEqual(all_assignments.count(),1)# one assignment
        
        self.assertEqual(all_mods.filter(module_code='XXXX1').exists(),True)
        self.assertEqual(all_mods.filter(module_title='testing').exists(),True)
        self.assertEqual(Module.objects.filter(total_hours='234').exists(),True)
    
        #Remove the module we just added, wiping out everything
        self.client.post(reverse('workload_app:remove_module',  kwargs={'workloadscenario_id': new_scen.id}), {'select_module_to_remove': all_mods[0].id,'wipe_from_table' : RemoveModuleForm.REMOVE_COMPLETELY})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods  = Module.objects.all();
        all_assignments = TeachingAssignment.objects.all();
        self.assertEqual(all_mods.count(),0)
        self.assertEqual(all_assignments.count(),0)
        
        #Make sure lecturer is still there
        self.assertEqual(Lecturer.objects.all().count(),1)
        
    def test_add_retire_module_method(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        #Create a new scenario
        new_scen = WorkloadScenario.objects.create(label='test_scen',dept=first_dept, academic_year=acad_year)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues

        mod_table = response.context['mod_table']
        self.assertEqual(len(mod_table),0)
        self.assertEqual(Module.objects.all().count(),0)#0 mods to start with
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE",department=first_dept)
        
        #Add a new module
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': 'XXXX1', 'module_title' : 'testing', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods  = Module.objects.all();
        self.assertEqual(all_mods.count(),1)# mods now after this addition
        self.assertEqual(all_mods.filter(module_code='XXXX1').exists(),True)
        self.assertEqual(all_mods.filter(module_title='testing').exists(),True)
        self.assertEqual(Module.objects.filter(total_hours='234').exists(),True)
        
        #Retire the module we just added
        self.client.post(reverse('workload_app:remove_module',  kwargs={'workloadscenario_id': new_scen.id}), {'select_module_to_remove': all_mods[0].id,'wipe_from_table' : RemoveModuleForm.RETIRE_ONLY})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(Module.objects.all().count(),1)#Still there
        
    def test_add_module_same_code(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        
        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        #Create a new scenario
        new_scen = WorkloadScenario.objects.create(label='test_scen', dept = first_dept, academic_year=acad_year)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues

        mod_table = response.context['mod_table']
        self.assertEqual(len(mod_table),0)
        self.assertEqual(Module.objects.all().count(),0)#0 mods to start with
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department=first_dept)
        
        mod_code = 'XXX1'
        #Add a new module
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code, 'module_title' : 'testing', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods  = Module.objects.all();
        self.assertEqual(all_mods.count(),1)# mods now after this addition
        self.assertEqual(all_mods.filter(module_code=mod_code).exists(),True)
        self.assertEqual(all_mods.filter(module_title='testing').exists(),True)
        self.assertEqual(Module.objects.filter(total_hours='234').exists(),True)
    
        #Now trying adding another one with the same code (different title)
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code, 'module_title' : 'different', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})    
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(Module.objects.all().count(),1)# addition failed... this should be 1
        #One only with this code
        self.assertEqual(Module.objects.filter(module_code=mod_code).count(),1)
        
        #Now create another scenario
        scen_name_2 = 'scen_2'
        acad_year = Academicyear.objects.create(start_year=2200)
        self.client.post(reverse('workload_app:manage_scenario'), {'label': scen_name_2, 'dept' : first_dept.id, 'copy_from': '', 'status': WorkloadScenario.DRAFT, 'fresh_record' : True, 'academic_year' : acad_year.id});
        scenario_2 = WorkloadScenario.objects.filter(label=scen_name_2)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.get().id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods  = Module.objects.all();
        self.assertEqual(all_mods.count(),1)# mods now after this addition
        self.assertEqual(all_mods.filter(module_code=mod_code).exists(),True)
        self.assertEqual(all_mods.filter(module_title='testing').exists(),True)
        self.assertEqual(Module.objects.filter(total_hours='234').exists(),True)
        
        self.assertEqual(all_mods.filter(scenario_ref__label = scen_name_2).count(),0)#
        self.assertEqual(all_mods.filter(module_code=mod_code).filter(scenario_ref__label = scen_name_2).exists(),False)
        self.assertEqual(all_mods.filter(module_title='testing').filter(scenario_ref__label = scen_name_2).exists(),False)
        self.assertEqual(Module.objects.filter(total_hours='234').filter(scenario_ref__label = scen_name_2).exists(),False)
        #Now trying adding another one with the same code (different title)
        #THIS TIME THE ADDITION SHOULD WORK AS WE ARE IN ANOTHER SCENARIO
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_2.get().id}), {'module_code': mod_code, 'module_title' : 'different', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})    
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.get().id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(Module.objects.all().count(),2)# addition succeded... this should be 2
        all_mods  = Module.objects.all();
        self.assertEqual(all_mods.filter(scenario_ref__label = scen_name_2).count(),1)#
        self.assertEqual(all_mods.filter(module_code=mod_code).filter(scenario_ref__label = scen_name_2).exists(),True)
        self.assertEqual(all_mods.filter(module_title='different').filter(scenario_ref__label = scen_name_2).exists(),True)
        self.assertEqual(Module.objects.filter(total_hours='234').filter(scenario_ref__label = scen_name_2).exists(),True)
        
    def test_add_module_with_no_hours(self):
        ''' this test simulates the case where the user allows
            the default number of hours to be specified based on module type and 
            number of tutorial groups '''
        
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        
        #Create a new scenario
        new_scen = WorkloadScenario.objects.create(label='test_scen',dept=first_dept, academic_year=acad_year)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department=first_dept)
        
        mod_code = 'XXX1'
        #Add a new module - but do not submit the optional value "total_hours"
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code, 'module_title' : 'testing', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods  = Module.objects.all()
    #     self.assertEqual(all_mods.count(),1)# mods now after this addition
    #     self.assertEqual(all_mods.filter(module_code=mod_code).exists(),True)
    #     self.assertEqual(all_mods.filter(module_title='testing').exists(),True)
    #     self.assertEqual(Module.objects.filter(total_hours='39').exists(),True)
        
    def test_edit_existing_module(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        #Create a programme
        prog_1 = ProgrammeOffered.objects.create(programme_name = "new_prog", primary_dept = first_dept)

        #Create a new scenario
        new_scen = WorkloadScenario.objects.create(label='test_scen', dept = first_dept, academic_year=acad_year)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues

        mod_table = response.context['mod_table']
        self.assertEqual(len(mod_table),0)
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.count(),0)#0 mods to start with
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department=first_dept)        
        mod_code = 'XXX1'
        #Add a new module
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {
            'module_code': mod_code, 'module_title' : 'testing', 'total_hours' : '234', 
            'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(Module.objects.all().count(),1)# mods now after this addition
        self.assertEqual(all_mods.filter(module_code=mod_code).exists(),True)
        self.assertEqual(all_mods.filter(module_title='testing').exists(),True)
        self.assertEqual(Module.objects.filter(total_hours='234').exists(),True)
        self.assertEqual(all_mods.filter(primary_programme__isnull=True).count(),1)
        self.assertEqual(all_mods.filter(secondary_programme__isnull=True).count(),1)
    
        #Now edit the existing module. KEY CHANGE: tutorial groups from 1 to 2
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code, 'module_title' : 'testing', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : False})    
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues        
        self.assertEqual(Module.objects.all().count(),1)#Still 1
        #One only with this code
        self.assertEqual(Module.objects.filter(module_code=mod_code).count(),1)
        
        #Now edit the existing module. KEY CHANGHE: total hours from 234 to 10
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code, 'module_title' : 'testing', 'total_hours' : '10', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : False})    
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.count(),1)#Still 1
        self.assertEqual(Module.objects.filter(total_hours='234').exists(),False)
        self.assertEqual(Module.objects.filter(total_hours='10').exists(),True)
        self.assertEqual(Module.objects.filter(compulsory_in_primary_programme=True).exists(),False)

        #Now edit the existing module. KEY CHANGHES: make it compulsory and add year of study
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code, \
        'module_title' : 'testing', 'total_hours' : '10', 'module_type' : mod_type_1.id, 'compulsory_in_primary_programme' : Module.YES,\
        'students_year_of_study' : 2,\
        'semester_offered' : Module.UNASSIGNED,   'fresh_record' : False})    
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.count(),1)#Still 1
        self.assertEqual(Module.objects.filter(compulsory_in_primary_programme=True).exists(),True)
        self.assertEqual(Module.objects.filter(students_year_of_study=2).exists(),True)
        self.assertEqual(Module.objects.filter(students_year_of_study=0).exists(),False)
        self.assertEqual(all_mods.get().scenario_ref.id,WorkloadScenario.objects.all().get().id)#Still 1, as we are editing the only one present
        #One only with this code
        self.assertEqual(Module.objects.filter(module_code=mod_code).count(),1)
        
        #Now edit the existing module. KEY CHANGHE: module title from testing to hello
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code, 'module_title' : 'hello', 'total_hours' : '10', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : False})    
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.count(),1)#Still 1
        #One only with this code
        self.assertEqual(Module.objects.filter(module_code=mod_code).count(),1)
        self.assertEqual(all_mods.filter(module_title='hello').exists(),True)
        self.assertEqual(all_mods.filter(module_title='testing').exists(),False)

        #Now edit. Assign prog_1 as primary programme
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code,\
        'module_title' : 'hello', 'total_hours' : '10', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 
         'primary_programme' : prog_1.id, 'fresh_record' : False})    
        self.assertEqual(all_mods.filter(primary_programme__isnull=True).count(),0)
        self.assertEqual(all_mods.filter(primary_programme__programme_name="new_prog").count(),1)
        self.assertEqual(all_mods.filter(secondary_programme__isnull=True).count(),1)

        #Create another programme
        prog_2 = ProgrammeOffered.objects.create(programme_name = "new_prog2", primary_dept = first_dept)
        #Now edit. Assign prog_2 as secondary programme
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code, 'module_title' : 'hello', 'total_hours' : '10', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,  'primary_programme' : prog_1.id, 'secondary_programme' : prog_2.id,'fresh_record' : False})    
        self.assertEqual(all_mods.filter(primary_programme__isnull=True).count(),0)
        self.assertEqual(all_mods.filter(primary_programme__programme_name="new_prog").count(),1)
        self.assertEqual(all_mods.filter(secondary_programme__isnull=True).count(),0)
        self.assertEqual(all_mods.filter(secondary_programme__programme_name="new_prog2").count(),1)

        #Create another programme
        prog_3 = ProgrammeOffered.objects.create(programme_name = "new_prog3", primary_dept = first_dept)
        #Now edit. Assign prog_3 as tertiary programme
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code, \
        'module_title' : 'hello', 'total_hours' : '10', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,\
        'primary_programme' : prog_1.id, 'secondary_programme' : prog_2.id, 'tertiary_programme' : prog_3.id, 'fresh_record' : False})    
        self.assertEqual(all_mods.filter(primary_programme__isnull=True).count(),0)
        self.assertEqual(all_mods.filter(primary_programme__programme_name="new_prog").count(),1)
        self.assertEqual(all_mods.filter(secondary_programme__isnull=True).count(),0)
        self.assertEqual(all_mods.filter(secondary_programme__programme_name="new_prog2").count(),1)
        self.assertEqual(all_mods.filter(tertiary_programme__isnull=True).count(),0)
        self.assertEqual(all_mods.filter(tertiary_programme__programme_name="new_prog3").count(),1)

        self.assertEqual(all_mods.filter(compulsory_in_secondary_programme=True).count(),0)
        self.assertEqual(all_mods.filter(compulsory_in_tertiary_programme=True).count(),0)
        #Now edit.MAke it compulsory in boths econdary and tertiary programmes
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code, \
        'module_title' : 'hello', 'total_hours' : '10', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,\
        'primary_programme' : prog_1.id, 'secondary_programme' : prog_2.id, 'tertiary_programme' : prog_3.id, \
        'compulsory_in_secondary_programme':True,'compulsory_in_tertiary_programme':True, 'fresh_record' : False})    
        self.assertEqual(all_mods.filter(primary_programme__isnull=True).count(),0)
        self.assertEqual(all_mods.filter(primary_programme__programme_name="new_prog").count(),1)
        self.assertEqual(all_mods.filter(secondary_programme__isnull=True).count(),0)
        self.assertEqual(all_mods.filter(secondary_programme__programme_name="new_prog2").count(),1)
        self.assertEqual(all_mods.filter(tertiary_programme__isnull=True).count(),0)
        self.assertEqual(all_mods.filter(tertiary_programme__programme_name="new_prog3").count(),1)
        self.assertEqual(all_mods.filter(compulsory_in_secondary_programme=True).count(),1)
        self.assertEqual(all_mods.filter(compulsory_in_tertiary_programme=True).count(),1)

    def test_edit_existing_module_with_multiple_scenarios(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        
        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        
        #Create a new scenario
        first_label = 'test_scen'
        first_scen = WorkloadScenario.objects.create(label=first_label, dept = first_dept, academic_year=acad_year)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues

        mod_table = response.context['mod_table']
        self.assertEqual(len(mod_table),0)
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.count(),0)#0 mods to start with

        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department=first_dept)
        
        mod_code = 'XXX1'
        #Add a new module
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': first_scen.id}), {'module_code': mod_code,\
         'module_title' : 'testing', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, \
         'compulsory_in_primary_programme' : False,'students_year_of_study' : '1',
          'fresh_record' : True})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
        all_mods = Module.objects.all()
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(Module.objects.all().count(),1)# mods now after this addition
        self.assertEqual(all_mods.filter(module_code=mod_code).exists(),True)
        self.assertEqual(all_mods.filter(module_title='testing').exists(),True)
        self.assertEqual(Module.objects.filter(total_hours='234').exists(),True)
        self.assertEqual(Module.objects.filter(compulsory_in_primary_programme=True).exists(),False)
        self.assertEqual(Module.objects.filter(students_year_of_study=1).exists(),True)
        
        #CREATE ANOTHER SCENARIO - COPYING FROM EXISTING
        default_scen_id = first_scen.id
        #Now create a new scenario, copying from the existing one
        new_label = 'new_scen'
        acad_year = Academicyear.objects.create(start_year=2200)
        self.client.post(reverse('workload_app:manage_scenario'), {'label': new_label, 'dept' : first_dept.id, 'copy_from':default_scen_id, 'status': WorkloadScenario.DRAFT, 'fresh_record' : True, 'academic_year' :  acad_year.id});
        new_scenario = WorkloadScenario.objects.filter(label=new_label)
        #Activate second scenario
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scenario.get().id}))
        self.assertEqual(Module.objects.all().count(),2)# mods now after this addition
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.filter(module_code=mod_code).count(),2)
        self.assertEqual(all_mods.filter(module_title='testing').count(),2)
        self.assertEqual(Module.objects.filter(total_hours='234').count(),2)
        self.assertEqual(Module.objects.filter(compulsory_in_primary_programme=True).exists(),False)
        self.assertEqual(Module.objects.filter(students_year_of_study=1).exists(),True)
        
        #Now edit the one in this scenario
        #Now edit the existing module. KEY CHANGHE: total hours from 234 to 10
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scenario.get().id}), {'module_code': mod_code, 'module_title' : 'testing', 'total_hours' : '10', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : False})    
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scenario.get().id}))
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.filter(module_code=mod_code).count(),2)
        self.assertEqual(all_mods.filter(module_title='testing').count(),2)
        self.assertEqual(Module.objects.filter(total_hours='234').count(),1)
        self.assertEqual(Module.objects.filter(total_hours='10').count(),1)
        self.assertEqual(Module.objects.filter(total_hours='234').filter(scenario_ref__label = new_label).count(),0)
        self.assertEqual(Module.objects.filter(total_hours='10').filter(scenario_ref__label = new_label).count(),1)
        self.assertEqual(Module.objects.filter(total_hours='234').filter(scenario_ref__label = first_label).count(),1)
        self.assertEqual(Module.objects.filter(total_hours='10').filter(scenario_ref__label = first_label).count(),0)
        
    def test_remove_module_with_assignments_multiple_scens(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        first_fac = Faculty.objects.create(faculty_name = "first fac", faculty_acronym = "FRTE")
        first_dept = Department.objects.create(department_name = "noname", department_acronym="ACRN", faculty= first_fac)
        acad_year = Academicyear.objects.create(start_year=2200)
        #create two scenarios, scen 2 is active
        scen_name_1 = 'scen_1'
        scenario_1 = WorkloadScenario.objects.create(label=scen_name_1, dept = first_dept, academic_year = acad_year)
        
        scen_name_2 = 'scen_2'
        acad_year_2 = Academicyear.objects.create(start_year=2205)
        scenario_2 = WorkloadScenario.objects.create(label=scen_name_2, dept = first_dept, academic_year=acad_year_2)
        
        new_track = EmploymentTrack.objects.create(track_name='test_track', track_adjustment = 0.8, faculty=first_fac)
        new_role = ServiceRole.objects.create(role_name='test_role', role_adjustment = 0.8, faculty=first_fac)
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_2.id}),{'name':'normal_lecturer','fraction_appointment' : '0.7',    'service_role' : new_role.id, 'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_2.id}),{'name':'educator_track','fraction_appointment' : '1.0',     'service_role' : new_role.id,  'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_2.id}),{'name':'vice_dean','fraction_appointment' : '0.5',     'service_role' : new_role.id, 'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        self.assertEqual(Lecturer.objects.all().count(),3)
        educator_track = Lecturer.objects.filter(name = 'educator_track').get()
        normal_lecturer = Lecturer.objects.filter(name = 'normal_lecturer').get()
        vice_dean = Lecturer.objects.filter(name = 'vice_dean').get()
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department=first_dept)
        
        mod_code_1 = 'AS101'
        mod_code_2 = 'AS201'
        mod_code_3 = 'AS301'
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_2.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_2.id}), {'module_code': mod_code_2, 'module_title' : 'module 2', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_2.id}), {'module_code': mod_code_3, 'module_title' : 'module 3', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})    
        self.assertEqual(Module.objects.all().count(),3)
        
        module_1 = Module.objects.filter(module_code = mod_code_1).get()
        module_2 = Module.objects.filter(module_code = mod_code_2).get()
        module_3 = Module.objects.filter(module_code = mod_code_3).get()
        
        #Add an assignment (scenario 2)
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=first_fac)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_2.id}), data = {'select_lecturer': educator_track.id, \
                 'select_module': module_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'56'})
                
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),1)
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_2.id)
        self.assertEqual(teaching_assignments_for_active_scen.count(),1)
        
        #Try removing the module
        #Check before
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.count(),3)
    
        #Now remove AS201 without wiping
        self.client.post(reverse('workload_app:remove_module',  kwargs={'workloadscenario_id': scenario_2.id}), {'select_module_to_remove': module_2.id, 'wipe_from_table' : RemoveModuleForm.RETIRE_ONLY})
        #Check after
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.count(),3)#Still 3 as it didn't wipe
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),0)
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_2.id)
        self.assertEqual(teaching_assignments_for_active_scen.count(),0)       
        #Re-add an assignment for module 2 (still scenario 2)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_2.id}), data = {'select_lecturer': normal_lecturer.id, \
                 'select_module': module_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'56'})
        
        #Check after re-adding
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.count(),3)#Still 3
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),1)
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_2.id)
        self.assertEqual(teaching_assignments_for_active_scen.count(),1)  
        
        #Now switch scenario and go to scenario 1
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))

        #Re-add smae people, same modules to scenario 1
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_1.id}),{'name':'normal_lecturer','fraction_appointment' : '0.7',     'service_role' : new_role.id, 'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_1.id}),{'name':'educator_track','fraction_appointment' : '1.0',     'service_role' : new_role.id, 'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_1.id}),{'name':'vice_dean','fraction_appointment' : '0.5',     'service_role' : new_role.id, 'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        self.assertEqual(Lecturer.objects.all().count(),6)#3 in scen 2 and now 3 in scen 1
        educator_track_scen_1 = Lecturer.objects.filter(name = 'educator_track').filter(workload_scenario__label = scen_name_1).get()
        normal_lecturer_scen_1 = Lecturer.objects.filter(name = 'normal_lecturer').filter(workload_scenario__label = scen_name_1).get()
        vice_dean_scen_1 = Lecturer.objects.filter(name = 'vice_dean').filter(workload_scenario__label = scen_name_1).get()
        
        #Add 3 modules to this scenario 1 as well
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': 'MOD2SCEN1', 'module_title' : 'module 2 scenario 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_3, 'module_title' : 'module 3', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})    
        self.assertEqual(Module.objects.all().count(),6)#3+3
        
        module_1_scen_1 = Module.objects.filter(module_code = mod_code_1).filter(scenario_ref__label = scen_name_1).get()
        module_2_scen_1 = Module.objects.filter(module_code = 'MOD2SCEN1').filter(scenario_ref__label = scen_name_1).get()
        module_3_scen_1 = Module.objects.filter(module_code = mod_code_3).filter(scenario_ref__label = scen_name_1).get()
        
        #add two assignments to scenario 1 for module 2
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), data = {'select_lecturer': normal_lecturer_scen_1.id, \
                 'select_module': module_2_scen_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'1586'})
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), data = {'select_lecturer': vice_dean_scen_1.id, \
                 'select_module': module_2_scen_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'1369'})
        
        #Check after adding these 2
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.count(),6)#3+3 still
        mods_in_active_scen = Module.objects.filter(scenario_ref__id = scenario_1.id)
        self.assertEqual(mods_in_active_scen.count(),3)#3 mods in active scenario
        
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),3)#1+2
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(teaching_assignments_for_active_scen.count(),2) 
        
        #Now remove module 2 from scenario 1 (the two latest assignments should go) - No wiping
        self.client.post(reverse('workload_app:remove_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_module_to_remove': module_2_scen_1.id, 'wipe_from_table' : RemoveModuleForm.RETIRE_ONLY})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.count(),6)#Still 6 as we didn't wipe anything
        #Check that the assignment involving the module is gone as well
        teaching_assignments = TeachingAssignment.objects.all()
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(teaching_assignments_for_active_scen.count(),0) #Scenario 1 should have no assignments
        self.assertEqual(teaching_assignments.count(),1)#Should be 1, from scenario 2 (inactive)
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(teaching_assignments_for_active_scen.count(),0) 
        
        #Now switch back to scenario 2
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.count(),6)#Still 6 as we didn't wipe anything
        #Check that the assignment involving the module is gone as well
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),1)#Should be 1, from scenario 2 
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_2.id)
        self.assertEqual(teaching_assignments_for_active_scen.count(),1) #One in active scenario 2
        
        #Now wipe module 2
        self.client.post(reverse('workload_app:remove_module',  kwargs={'workloadscenario_id': scenario_2.id}), {'select_module_to_remove': module_2.id, 'wipe_from_table' : RemoveModuleForm.REMOVE_COMPLETELY})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.count(),5)#5 after wiping 1
        #Check that the assignment involving the module is gone as well
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),0)#No more
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_2.id)
        self.assertEqual(teaching_assignments_for_active_scen.count(),0)        

    def test_remove_module_type_with_modules_and_assignments(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        
        #Call page once. This should create one scenario and one module type
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        
        self.assertEqual(WorkloadScenario.objects.all().count(), 0)
        self.assertEqual(ModuleType.objects.all().count(), 0)
        
        first_fac = Faculty.objects.create(faculty_name = "first fac", faculty_acronym = "FRTE")
        first_dept = Department.objects.create(department_name = "noname", department_acronym="ACRN", faculty= first_fac)
        acad_year_1 = Academicyear.objects.create(start_year=2345)
        acad_year_2 = Academicyear.objects.create(start_year=2222)
        #create two scenarios, scen 2 is active
        scen_name_1 = 'scen_1'
        scenario_1 = WorkloadScenario.objects.create(label=scen_name_1,dept=first_dept, academic_year=acad_year_1)
        
        scen_name_2 = 'scen_2'
        scenario_2 = WorkloadScenario.objects.create(label=scen_name_2, dept=first_dept, academic_year=acad_year_2)
        self.assertEqual(WorkloadScenario.objects.all().count(), 2)
        
        new_role = ServiceRole.objects.create(role_name='test_role', role_adjustment = 0.8, faculty=first_fac)
        new_track = EmploymentTrack.objects.create(track_name='test_track', track_adjustment = 0.8, faculty=first_fac)

        #Now switch scenario and go to scenario 2
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        
        #add 3 lecturers
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_2.id}),{'name':'normal_lecturer','fraction_appointment' : '0.7',     'service_role' : new_role.id, 'employment_track': new_track.id, 'is_external': False, 'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_2.id}),{'name':'educator_track','fraction_appointment' : '1.0',     'service_role' : new_role.id, 'employment_track': new_track.id,'is_external': False, 'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_2.id}),{'name':'vice_dean','fraction_appointment' : '0.5',     'service_role' : new_role.id, 'employment_track': new_track.id,'is_external': False, 'fresh_record' : True})
        self.assertEqual(Lecturer.objects.all().count(),3)
        educator_track = Lecturer.objects.filter(name = 'educator_track').get()
        normal_lecturer = Lecturer.objects.filter(name = 'normal_lecturer').get()
        vice_dean = Lecturer.objects.filter(name = 'vice_dean').get()
        
        #Create two module types
        name_type_1 = "MOD_TYPE_1"
        name_type_2 = "MOD_TYPE_2"
        mod_type_1 = ModuleType.objects.create(type_name=name_type_1, department=first_dept)
        mod_type_2 = ModuleType.objects.create(type_name=name_type_2, department=first_dept)
        self.assertEqual(ModuleType.objects.all().count(), 2)
        
        #Create 3 mods
        mod_code_1 = 'AS101'
        mod_code_2 = 'AS201'#This is type 2
        mod_code_3 = 'AS301'
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_2.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_2.id}), {'module_code': mod_code_2, 'module_title' : 'module 2', 'total_hours' : '234', 'module_type' : mod_type_2.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_2.id}), {'module_code': mod_code_3, 'module_title' : 'module 3', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})    
        self.assertEqual(Module.objects.all().count(),3)
        
        module_1 = Module.objects.filter(module_code = mod_code_1).get()
        module_2 = Module.objects.filter(module_code = mod_code_2).get()
        module_3 = Module.objects.filter(module_code = mod_code_3).get()
        
        #Add two assignments (scenario 2). First for module 2 (type 2) and one for module 3 (type 1)
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=first_fac)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_2.id}), data = {'select_lecturer': educator_track.id, \
                 'select_module': module_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'56'})
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_2.id}), data = {'select_lecturer': normal_lecturer.id, \
                 'select_module': module_3.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'56'})       
         
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),2)
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_2.id)
        self.assertEqual(teaching_assignments_for_active_scen.count(),2)
          
        #Now switch scenario and go to scenario 1
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))

        #Re-add smae people, same modules to scenario 1
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_1.id}),{'name':'normal_lecturer','fraction_appointment' : '0.7',   'service_role' : new_role.id, 'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_1.id}),{'name':'educator_track','fraction_appointment' : '1.0',    'service_role' : new_role.id, 'employment_track': new_track.id, 'is_external': False, 'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_1.id}),{'name':'vice_dean','fraction_appointment' : '0.5',    'service_role' : new_role.id, 'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        self.assertEqual(Lecturer.objects.all().count(),6)#3 in scen 2 and now 3 in scen 1
        educator_track_scen_1 = Lecturer.objects.filter(name = 'educator_track').filter(workload_scenario__label = scen_name_1).get()
        normal_lecturer_scen_1 = Lecturer.objects.filter(name = 'normal_lecturer').filter(workload_scenario__label = scen_name_1).get()
        vice_dean_scen_1 = Lecturer.objects.filter(name = 'vice_dean').filter(workload_scenario__label = scen_name_1).get()
        
        #Add 3 modules to this scenario 1 as well. smae as before, module 2 is type 2, others are type 1
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_2, 'module_title' : 'module 2 scenario 1', 'total_hours' : '234', 'module_type' : mod_type_2.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_3, 'module_title' : 'module 3', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED,   'fresh_record' : True})    
        self.assertEqual(Module.objects.all().count(),6)#3+3
        
        module_1_scen_1 = Module.objects.filter(module_code = mod_code_1).filter(scenario_ref__label = scen_name_1).get()
        module_2_scen_1 = Module.objects.filter(module_code = mod_code_2).filter(scenario_ref__label = scen_name_1).get()
        module_3_scen_1 = Module.objects.filter(module_code = mod_code_3).filter(scenario_ref__label = scen_name_1).get()
        
        #add two assignments to scenario 1 for module 2 (type 2)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), data = {'select_lecturer': normal_lecturer_scen_1.id, \
                 'select_module': module_2_scen_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'1568'})
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), data = {'select_lecturer': vice_dean_scen_1.id, \
                 'select_module': module_2_scen_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'1369'})     
        
        #Check after adding these 2
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.count(),6)#3+3 still
        mods_in_active_scen = Module.objects.filter(scenario_ref__id = scenario_1.id)
        self.assertEqual(mods_in_active_scen.count(),3)#3 mods in active scenario
        
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),4)#2+2
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(teaching_assignments_for_active_scen.count(),2)#2 in this scenario
        
        #Current situation
        #Scenario 1 (ACTIVE):3 modules, 3 lecturers, 2 assignments (both for mod 2 (type 2)
        #Scenario 2 (INACTIVE):3 modules, 3 lecturers, 2 assignments (1 for mod 2 (type 2) and one for mod 3 (type 1))
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_1).count(),2)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_1).filter(assigned_module__module_type__type_name = DEFAULT_MODULE_TYPE_NAME).count(),0)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_1).filter(assigned_module__module_type__type_name = name_type_1).count(),0)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_1).filter(assigned_module__module_type__type_name = name_type_2).count(),2)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_1).count(),2)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_2).filter(assigned_module__module_type__type_name = DEFAULT_MODULE_TYPE_NAME).count(),0)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_2).filter(assigned_module__module_type__type_name = name_type_1).count(),1)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_2).filter(assigned_module__module_type__type_name = name_type_2).count(),1)
        
        #Now we remove module type 2
        self.client.post(reverse('workload_app:remove_module_type', kwargs={'department_id': first_dept.id}), {'select_module_type_to_remove': mod_type_2.id})
        self.assertEqual(ModuleType.objects.all().count(), 1)#module type 1 only left
        #Expected result:
        #Scenario 1 (ACTIVE):3 modules, 3 lecturers, 2 assignments (both for mod 2 - WHICH TURNED TO UNAASIGNED NOW)
        #Scenario 2 (INACTIVE):3 modules, 3 lecturers, 2 assignments (1 for mod 2 (WHICH TURNED TO UNAASIGNED NOW) and one for mod 3 (type 1))
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        all_mods = Module.objects.all()
        self.assertEqual(all_mods.count(),6)#3+3 still
        mods_in_active_scen = Module.objects.filter(scenario_ref__id = scenario_1.id)
        self.assertEqual(mods_in_active_scen.count(),3)#3 mods in active scenario
        
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),4)#2+2
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(teaching_assignments_for_active_scen.count(),2)#2 in this scenario
        
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_1).count(),2)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_1).filter(assigned_module__module_type__type_name = name_type_1).count(),0)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_1).filter(assigned_module__module_type__type_name = name_type_2).count(),0)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_1).count(),2)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_2).filter(assigned_module__module_type__type_name = name_type_1).count(),1)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_2).filter(assigned_module__module_type__type_name = name_type_2).count(),0)
         