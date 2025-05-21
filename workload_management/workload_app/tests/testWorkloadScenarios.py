from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *
from workload_app.models import Lecturer, Module, TeachingAssignment,WorkloadScenario,ModuleType,Department, EmploymentTrack, ServiceRole,Faculty,ProgrammeOffered, UniversityStaff


class TestWorkloadScenarios(TestCase):
    def setup_user(self):
        #The test client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
        self.user.is_superuser = True
        self.user.save()
        uni_user = UniversityStaff.objects.create(user = self.user, department=None,faculty=None)
        
    def test_empty_db(self):
        '''This test checks that all is OK with an empty database'''

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        self.assertEqual(WorkloadScenario.objects.all().count(),0)
        self.assertEqual(Module.objects.all().count(),0)
        self.assertEqual(Lecturer.objects.all().count(),0)
        self.assertEqual(Department.objects.all().count(),1) #One created by default

        new_scen = WorkloadScenario.objects.create(label='test_scen');
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        
        empty_wl_table = response.context['wl_table']
        self.assertEqual(len(empty_wl_table),0)
        
        empty_mod_table = response.context['mod_table']
        self.assertEqual(len(empty_mod_table),0)
        
        self.assertEqual(WorkloadScenario.objects.all().count(),1)
        
        empty_assign_list = TeachingAssignment.objects.all()
        self.assertEqual(empty_assign_list.count(),0)
        
        self.assertEqual(WorkloadScenario.objects.all().count(),1)
        self.assertEqual(Module.objects.all().count(),0)
        self.assertEqual(Lecturer.objects.all().count(),0)

    def test_add_remove_scenario_forms(self):

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        first_scen = 'test_scen'
        first_dept = Department.objects.create(department_name = "noname", department_acronym="ACRN")
        first_scenario = WorkloadScenario.objects.create(label=first_scen, dept = first_dept)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scenario.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertContains(response, "label")
        self.assertEqual(WorkloadScenario.objects.all().count(),1)
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department = first_dept)
        new_track = EmploymentTrack.objects.create(track_name='test_track', track_adjustment = 0.8)
        new_role = ServiceRole.objects.create(role_name='test_role', role_adjustment = 0.8)

        #Add alecturer and a module to the default scenario
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': first_scenario.id}),{'name':'bob','fraction_appointment' : '0.5',    'service_role' : new_role.id, 'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': first_scenario.id}), {'module_code': "unused_module_code", 'module_title' : 'testing_unused', 'total_hours' : '234', 'module_type' : mod_type_1.id , 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.assertEqual(Module.objects.all().count(),1)
        self.assertEqual(Lecturer.objects.all().count(),1)
        self.assertEqual(TeachingAssignment.objects.all().count(),0)
        self.assertEqual(Lecturer.objects.filter(workload_scenario__label = first_scen).count(),1)
        self.assertEqual(Module.objects.filter(scenario_ref__label = first_scen).count(),1)
        
        #Test the POST now by adding a scenario
        new_label = 'new_test_scen'
        self.client.post(reverse('workload_app:manage_scenario'),{'label':new_label, 'dept' : first_dept.id, 'fresh_record' : True, \
                                                                    'status': WorkloadScenario.OFFICIAL, 'academic_year' : 1})
        new_scenario = WorkloadScenario.objects.filter(label=new_label)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        
        self.assertEqual(WorkloadScenario.objects.all().count(),2)

        #click on the new scenario
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scenario.get().id}))
        self.assertEqual(response.status_code, 200) #No issues

        self.assertEqual(WorkloadScenario.objects.filter(label=new_label).exists(),True)     
        
        #Add the same lecturer and module to the new scenario
        mod_code = 'AA111'
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scenario.get().id}),{'name':'bob','fraction_appointment' : '0.5',    'service_role' : new_role.id, 'employment_track': new_track.id, 'is_external': False, 'fresh_record' : True})
        self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': new_scenario.get().id}), {'module_code': mod_code, 'module_title' : 'testing', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        normal_lecturer = Lecturer.objects.filter(name = 'bob').filter(workload_scenario__label = new_label).get()
        module_1 = Module.objects.filter(module_code = mod_code).filter(scenario_ref__label = new_label).get()
        
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': new_scenario.get().id}), data = {'select_lecturer': normal_lecturer.id, 'select_module': module_1.id, 'counted_towards_workload' : 'yes','manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'136'});
        self.assertEqual(Module.objects.all().count(),2)
        self.assertEqual(Module.objects.filter(scenario_ref__label = first_scen).count(),1)
        self.assertEqual(Module.objects.filter(scenario_ref__label = new_label).count(),1)
        
        self.assertEqual(TeachingAssignment.objects.all().count(),1)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = new_label).count(),1)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = first_scen).count(),0)
        
        self.assertEqual(Lecturer.objects.all().count(),2)
        self.assertEqual(Lecturer.objects.filter(workload_scenario__label = new_label).count(),1)
        self.assertEqual(Lecturer.objects.filter(workload_scenario__label = first_scen).count(),1)
                
        #Now remove the scenario with the assignment (new_label)
        self.client.post(reverse('workload_app:remove_scenario'), {'select_scenario_to_remove': WorkloadScenario.objects.filter(label=new_label).get().id})
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        
        #Scenario 1 (the only remaining) had no assignment. We removed the only scenario with the
        #an assignment and the remove routine is supposed to get rid of the assignment as well..
        
        self.assertEqual(WorkloadScenario.objects.all().count(),1)
        self.assertEqual(WorkloadScenario.objects.filter(label=new_label).exists(),False)
        self.assertEqual(WorkloadScenario.objects.filter(label=first_scen).exists(),True)
        
        #The module remained only in the old scenario
        self.assertEqual(Module.objects.all().count(),1)
        self.assertEqual(Module.objects.filter(scenario_ref__label = first_scen).count(),1)
        self.assertEqual(Module.objects.filter(scenario_ref__label = new_label).exists(),False)
        
        self.assertEqual(TeachingAssignment.objects.all().count(),0)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = first_scen).count(),0)
        #The lecturer remained only in the old scenario
        self.assertEqual(Lecturer.objects.all().count(),1)
        self.assertEqual(Lecturer.objects.filter(workload_scenario__label = first_scen).count(),1)
        self.assertEqual(Lecturer.objects.filter(workload_scenario__label = new_label).exists(),False)
        
        
    def test_manage_scenario(self):

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        
        first_fac = Faculty.objects.create(faculty_name = "first fac", faculty_acronym = "FRTE")
        #create a new workload
        first_scen_label = 'test_scen'
        first_dept = Department.objects.create(department_name = "noname", department_acronym="ACRN", faculty = first_fac)

        #Create a programme
        first_prog = ProgrammeOffered.objects.create(programme_name = "test_prog", primary_dept = first_dept)

        first_scenario = WorkloadScenario.objects.create(label=first_scen_label, dept=first_dept)
        #Click on it
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scenario.id}))
        
        self.assertEqual(response.status_code, 200) #No issues
        normal_lecturer = Lecturer.objects.create(name="normal_lecturer",fraction_appointment=0.7);
        educator_track = Lecturer.objects.create(name="educator_track",fraction_appointment=1.0)
        vice_dean = Lecturer.objects.create(name="vice_dean",fraction_appointment=0.5)
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department = first_dept)
        
        mod_code_1 = 'AS101'
        mod_code_2 = 'AS201'
        mod_code_3 = 'AS301' #This thrid one is associated with "test_prog"
        self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': first_scenario.id}), {'module_code': mod_code_1, 'module_title' : 'testing', 'total_hours' : '2340', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': first_scenario.id}), {'module_code': mod_code_2, 'module_title' : 'testing2', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': first_scenario.id}), {'module_code': mod_code_3, 'module_title' : 'testing3', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'primary_programme' : first_prog.id, 'fresh_record' : True})    
        self.assertEqual(Module.objects.all().count(),3)
        self.assertEqual(Module.objects.filter(primary_programme__isnull=True).count(),2)
        self.assertEqual(Module.objects.filter(primary_programme__isnull=False).count(),1)
        self.assertEqual(Module.objects.all().count(),3)
        self.assertEqual(TeachingAssignment.objects.all().count(),0)
        
        module_1 = Module.objects.filter(module_code = mod_code_1).filter(scenario_ref = first_scenario)
        #Add one assignment to this scenario
        self.client.post(reverse('workload_app:add_assignment',kwargs={'workloadscenario_id': first_scenario.id}), {'select_lecturer': normal_lecturer.id, \
            'select_module': module_1.get().id, 'counted_towards_workload' : 'yes','manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'16'})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scenario.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(Module.objects.all().count(),3)
        self.assertEqual(Lecturer.objects.all().count(),3)
        self.assertEqual(TeachingAssignment.objects.all().count(),1)
        
        teaching_assignments_for_first_scen = TeachingAssignment.objects.filter(workload_scenario__id=first_scenario.id)
        self.assertEqual(teaching_assignments_for_first_scen.count(),1)
        self.assertEqual(teaching_assignments_for_first_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(assigned_module__module_code='AS101').exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(assigned_lecturer__name='normal_lecturer').exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(counted_towards_workload = True).count(),1)
        
        #Add another assignment. This time not counted towards workload
        module_2 = Module.objects.filter(module_code = mod_code_2).filter(scenario_ref = first_scenario)
        self.client.post(reverse('workload_app:add_assignment',kwargs={'workloadscenario_id': first_scenario.id}), {'select_lecturer': educator_track.id, \
            'select_module': module_2.get().id, 'counted_towards_workload' : 'no','manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'582'})
        
        teaching_assignments_for_first_scen = TeachingAssignment.objects.filter(workload_scenario__id=first_scenario.id)
        self.assertEqual(teaching_assignments_for_first_scen.count(),2)
        self.assertEqual(teaching_assignments_for_first_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(assigned_module__module_code=mod_code_1).exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(assigned_lecturer__name='normal_lecturer').exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(number_of_hours='582').exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(assigned_module__module_code=mod_code_2).exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(assigned_lecturer__name='educator_track').exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(counted_towards_workload = True).count(),1)
        self.assertEqual(teaching_assignments_for_first_scen.filter(counted_towards_workload = False).count(),1)

        #Now create a new scenario, copying from the existing one
        new_label = "new_scenario"
        self.client.post(reverse('workload_app:manage_scenario'), {'label': new_label, 'dept' : first_dept.id, 'copy_from':first_scenario.id, \
                                                                    'status': WorkloadScenario.DRAFT, 'fresh_record' : True, 'academic_year' : 1});
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        
        self.assertEqual(WorkloadScenario.objects.all().count(),2)        
        self.assertEqual(Module.objects.all().count(),6)#The 3 created in the beginning, plus 3 copied over
        self.assertEqual(Lecturer.objects.all().count(),6)#The 3 created in the beginning, plus 3 copied over
        self.assertEqual(Module.objects.filter(primary_programme__isnull=True).count(),4)#The two before, plus 2 more
        self.assertEqual(Module.objects.filter(primary_programme__isnull=False).count(),2)
        self.assertEqual(Module.objects.filter(scenario_ref__label = first_scen_label).count(),3)#The 3 created in the beginning
        self.assertEqual(Module.objects.filter(scenario_ref__label = new_label).count(),3)#The 3 new ones
        self.assertEqual(Module.objects.filter(total_hours='2340').count(),2)#
        self.assertEqual(Module.objects.filter(total_hours='234').count(),4)#
        self.assertEqual(TeachingAssignment.objects.all().count(),4) #2 per scenario

        #Check assignments for both scenarios
        teaching_assignments_for_first_scen = TeachingAssignment.objects.filter(workload_scenario__id=first_scenario.id)
        self.assertEqual(teaching_assignments_for_first_scen.count(),2)
        self.assertEqual(teaching_assignments_for_first_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(assigned_module__module_code=mod_code_1).exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(assigned_lecturer__name='normal_lecturer').exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(number_of_hours='582').exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(assigned_module__module_code=mod_code_2).exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(assigned_lecturer__name='educator_track').exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(counted_towards_workload = True).count(),1)
        self.assertEqual(teaching_assignments_for_first_scen.filter(counted_towards_workload = False).count(),1)

        new_scenario = WorkloadScenario.objects.filter(label=new_label).get()
        teaching_assignments_for_new_scen = TeachingAssignment.objects.filter(workload_scenario__id=new_scenario.id)
        self.assertEqual(teaching_assignments_for_new_scen.count(),2)
        self.assertEqual(teaching_assignments_for_new_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_new_scen.filter(assigned_module__module_code=mod_code_1).exists(),True)
        self.assertEqual(teaching_assignments_for_new_scen.filter(assigned_lecturer__name='normal_lecturer').exists(),True)
        self.assertEqual(teaching_assignments_for_new_scen.filter(number_of_hours='582').exists(),True)
        self.assertEqual(teaching_assignments_for_new_scen.filter(assigned_module__module_code=mod_code_2).exists(),True)
        self.assertEqual(teaching_assignments_for_new_scen.filter(assigned_lecturer__name='educator_track').exists(),True)
        self.assertEqual(teaching_assignments_for_new_scen.filter(counted_towards_workload = True).count(),1)
        self.assertEqual(teaching_assignments_for_new_scen.filter(counted_towards_workload = False).count(),1)
        
        #Now create another scenario, but empty
        third_scen_label = "third_scenario"
        self.client.post(reverse('workload_app:manage_scenario'), {'label': third_scen_label, 'dept' : first_dept.id, 'copy_from':'', \
                                                                        'status': WorkloadScenario.DRAFT,'fresh_record' :  True,'academic_year' : 1});
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(WorkloadScenario.objects.all().count(),3)  #2 previously,plus one
        self.assertEqual(Module.objects.all().count(),6)#Still 6 mods

        #Now remove "new_scenario"
        self.client.post(reverse('workload_app:remove_scenario'), {'select_scenario_to_remove': new_scenario.id})
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(WorkloadScenario.objects.all().count(),2)  #the first one, plus the empty one
        self.assertEqual(Module.objects.all().count(),3)#Only 3 mods left
        self.assertEqual(Lecturer.objects.all().count(),3)#3 left
        self.assertEqual(TeachingAssignment.objects.all().count(),2)

        teaching_assignments_for_first_scen = TeachingAssignment.objects.filter(workload_scenario__id=first_scenario.id)
        self.assertEqual(teaching_assignments_for_first_scen.count(),2)
        self.assertEqual(teaching_assignments_for_first_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(assigned_module__module_code=mod_code_1).exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(assigned_lecturer__name='normal_lecturer').exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(number_of_hours='582').exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(assigned_module__module_code=mod_code_2).exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(assigned_lecturer__name='educator_track').exists(),True)
        self.assertEqual(teaching_assignments_for_first_scen.filter(counted_towards_workload = True).count(),1)
        self.assertEqual(teaching_assignments_for_first_scen.filter(counted_towards_workload = False).count(),1)

    def test_manage_scenario_same_name(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(WorkloadScenario.objects.all().count(),0) 
        first_scen_label = 'test_scen'
        first_dept = Department.objects.create(department_name = "noname", department_acronym="ACRN")
        first_scenario = WorkloadScenario.objects.create(label=first_scen_label);
        self.assertEqual(WorkloadScenario.objects.all().count(),1) 
        
        #create one with the same name
        self.client.post(reverse('workload_app:manage_scenario'), {'label': first_scen_label, 'dept' : first_dept.id,  'copy_from': '',\
                                                                    'status': WorkloadScenario.DRAFT,'fresh_record' : True});
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        
        self.assertEqual(WorkloadScenario.objects.all().count(),1)#Should not have been created 
        #Make sure the current_name is used only once, even after trying to add one with the same name
        #(the code should have added a suffix)
        self.assertEqual(WorkloadScenario.objects.filter(label=first_scen_label).count(),1)
    
    def test_edit_existing_scenario(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(WorkloadScenario.objects.all().count(),0) 
        first_scen_label = 'test_scen'
        first_dept = Department.objects.create(department_name = "noname", department_acronym="ACRN")
        first_scenario = WorkloadScenario.objects.create(label=first_scen_label);
        self.assertEqual(WorkloadScenario.objects.all().count(),1) 

        new_name = 'hello';
        self.client.post(reverse('workload_app:manage_scenario'), {'label': new_name, 'dept' : first_dept.id,\
             'fresh_record' : False, 'status': WorkloadScenario.DRAFT, 'scenario_id' : first_scenario.id, 'academic_year' : 1});
        self.assertEqual(WorkloadScenario.objects.filter(label=first_scen_label).count(),0)#Old name, not there
        self.assertEqual(WorkloadScenario.objects.filter(label=new_name).count(),1)#New name is there
        
    def test_edit_scenario_into_existing_name(self):
        '''Same as the test above, but we edit the scenario to have a name of an already existing one (should not be allowed)'''

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(WorkloadScenario.objects.all().count(),0) 
        first_scen_label = 'test_scen'
        first_dept = Department.objects.create(department_name = "noname", department_acronym="ACRN")
        first_scenario = WorkloadScenario.objects.create(label=first_scen_label);
        self.assertEqual(WorkloadScenario.objects.all().count(),1) 
        
        new_name = 'testing'
        #Create a new scenario with the new name
        self.client.post(reverse('workload_app:manage_scenario'), {'label': new_name, 'dept' : first_dept.id, 'copy_from': '', 
        'fresh_record' : True, 'status': WorkloadScenario.DRAFT, 'academic_year' : 1});

        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(WorkloadScenario.objects.all().count(),2)
        self.assertEqual(WorkloadScenario.objects.filter(label=first_scen_label).count(),1)#Old name
        self.assertEqual(WorkloadScenario.objects.filter(label=new_name).count(),1)#New name is there
        
        new_name_scenario = WorkloadScenario.objects.filter(label=new_name).get()
        #Now try edit the new one by giving it the name of hte first one we had
        self.client.post(reverse('workload_app:manage_scenario'), {'label': first_scen_label, 'dept' : first_dept.id,\
            'fresh_record' : False, 'status': WorkloadScenario.DRAFT, 'scenario_id' : new_name_scenario.id});
        #Both should still be there. Third one not created
        self.assertEqual(WorkloadScenario.objects.filter(label=first_scen_label).count(),1)#Old name
        self.assertEqual(WorkloadScenario.objects.filter(label=new_name).count(),1)#New name is there
        self.assertEqual(WorkloadScenario.objects.all().count(),2)
        
        
    def test_multiple_scenarios(self):
        '''Check multiple scenario functionalities, including add/remove teaching asignments and add/remove scenarios'''

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        first_fac = Faculty.objects.create(faculty_name = "first fac", faculty_acronym = "FRTE")
        first_dept = Department.objects.create(department_name = "noname", department_acronym="ACRN", faculty = first_fac)
        
        #create two scenarios
        scen_name_1 = 'scen_1'
        scenario_1 = WorkloadScenario.objects.create(label=scen_name_1);
        
        scen_name_2 = 'scen_2'
        scenario_2 = WorkloadScenario.objects.create(label=scen_name_2);
        
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(WorkloadScenario.objects.all().count(),2)

        new_role = ServiceRole.objects.create(role_name='test_role', role_adjustment = 0.8)
        new_track = EmploymentTrack.objects.create(track_name='test_track', track_adjustment = 0.8)
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_2.id}),{'name':'normal_lecturer','fraction_appointment' : '0.7',    'service_role' : new_role.id,'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_2.id}),{'name':'educator_track','fraction_appointment' : '1.0',    'service_role' : new_role.id,'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_2.id}),{'name':'vice_dean','fraction_appointment' : '0.5',    'service_role' : new_role.id,'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        
        educator_track = Lecturer.objects.filter(name = 'educator_track').get()
        normal_lecturer = Lecturer.objects.filter(name = 'normal_lecturer').get()
        vice_dean = Lecturer.objects.filter(name = 'vice_dean').get()
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE")
        
        mod_code_1 = 'AS101'
        mod_code_2 = 'AS201'
        mod_code_3 = 'AS301'
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_2.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_2.id}), {'module_code': mod_code_2, 'module_title' : 'module 2', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_2.id}), {'module_code': mod_code_3, 'module_title' : 'module 3', 'total_hours' : '234', 'module_type' : mod_type_1.id , 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.assertEqual(Module.objects.all().count(),3)
        
        module_1 = Module.objects.filter(module_code = mod_code_1).get()
        module_2 = Module.objects.filter(module_code = mod_code_2).get()
        module_3 = Module.objects.filter(module_code = mod_code_3).get()
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        wl_table = response.context['wl_table']
        self.assertEqual(len(wl_table),3)#3 profs
        
        self.assertEqual(Module.objects.all().count(),3)#3 mods in total
        
        #add first assignment to scenario 2
        self.client.post(reverse('workload_app:add_assignment', kwargs={'workloadscenario_id': scenario_2.id}), {'select_lecturer': normal_lecturer.id, 'select_module': module_1.id, 'counted_towards_workload' : 'yes','manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'36'});
        #Scenario 2 is active now
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        teaching_assignments =  TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),1)
        obtained_wl_table = response.context['wl_table']
        self.assertEqual(len(obtained_wl_table),3)#still 3 profs
        self.assertEqual(obtained_wl_table[0]["prof_name"],"educator_track")
        self.assertEqual(obtained_wl_table[0]["assignments"],"No teaching assignments")
        self.assertEqual(obtained_wl_table[1]["prof_name"],"normal_lecturer")
        self.assertEqual(obtained_wl_table[1]["assignments"],"AS101 (36)")
        
        obtained_mod_table = response.context['mod_table']
        self.assertEqual(len(obtained_mod_table),3)#3 modules
        self.assertEqual(obtained_mod_table[0]["module_code"],"AS101")
        
        #Now activate scenario 1  (simulate button click)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        scenario_1.refresh_from_db();
        scenario_2.refresh_from_db();
        
        #response = self.client.get(reverse('workload_app:index'))
        
        #No workload table as no active assignments in scenario 1
        obtained_wl_table = response.context['wl_table']
        self.assertEqual(len(obtained_wl_table),0)
        obtained_mod_table = response.context['mod_table']
        self.assertEqual(len(obtained_wl_table),0)
        
        #RE-add lecturers nd modules to the active scenario
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_1.id}),{'name':'normal_lecturer','fraction_appointment' : '0.7',    'service_role' : new_role.id, 'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_1.id}),{'name':'educator_track','fraction_appointment' : '1.0',    'service_role' : new_role.id, 'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_1.id}),{'name':'vice_dean','fraction_appointment' : '0.5',    'service_role' : new_role.id, 'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        
        educator_track_scen_1 = Lecturer.objects.filter(name = 'educator_track').filter(workload_scenario__id=scenario_1.id).get()
        normal_lecturer_scen_1 = Lecturer.objects.filter(name = 'normal_lecturer').filter(workload_scenario__id=scenario_1.id).get()
        vice_dean_scen_1 = Lecturer.objects.filter(name = 'vice_dean').filter(workload_scenario__id=scenario_1.id).get()
        
        mod_code_1 = 'AS101'
        mod_code_2 = 'AS201'
        mod_code_3 = 'AS301'
        self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_2, 'module_title' : 'module 2', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_3, 'module_title' : 'module 3', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        
        module_1_scen_1 = Module.objects.filter(module_code = mod_code_1).filter(scenario_ref__id=scenario_1.id).get()
        module_2_scen_1 = Module.objects.filter(module_code = mod_code_2).filter(scenario_ref__id=scenario_1.id).get()
        module_3_scen_1 = Module.objects.filter(module_code = mod_code_3).filter(scenario_ref__id=scenario_1.id).get()
        
        #Now add an asisgnment to scenario 1
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': educator_track_scen_1.id, 'select_module': module_2_scen_1.id, 'counted_towards_workload' : 'yes','manual_hours_yes_no': 'yes', 'enter_number_of_total_hours_assigned':'56'});
        teaching_assignments =  TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),2)#Two total assignments, but only one to scenario 1

        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        obtained_wl_table = response.context['wl_table']
        self.assertEqual(len(obtained_wl_table),3)#3 profs
        self.assertEqual(obtained_wl_table[0]["prof_name"],"educator_track")
        self.assertEqual(obtained_wl_table[0]["assignments"],"AS201 (56)")
        
        obtained_mod_table = response.context['mod_table']
        self.assertEqual(len(obtained_mod_table),3)
        self.assertEqual(obtained_mod_table[1]["module_code"],"AS201")
        self.assertEqual(obtained_mod_table[1]["module_title"],"module 2")
        self.assertEqual(obtained_mod_table[1]["module_lecturers"],"educator_track (56)")
        
        #Now go to scenario 2  (simulate button click)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        scenario_1.refresh_from_db();
        scenario_2.refresh_from_db();

        #Scenario 2 is active now
        #response = self.client.get(reverse('workload_app:index'))
        teaching_assignments =  TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),2)#Two still total....
        obtained_wl_table = response.context['wl_table']
        self.assertEqual(len(obtained_wl_table),3)
        self.assertEqual(obtained_wl_table[1]["prof_name"],"normal_lecturer")
        self.assertEqual(obtained_wl_table[1]["assignments"],"AS101 (36)")
        
        obtained_mod_table = response.context['mod_table']
        self.assertEqual(len(obtained_mod_table),3)
        self.assertEqual(obtained_mod_table[0]["module_code"],"AS101")
        teaching_assignments_for_active_scenario = TeachingAssignment.objects.filter(workload_scenario__id = scenario_2.id)
        #Remove the only teaching assignment from scenario 2
        self.client.post(reverse('workload_app:remove_assignment',  kwargs={'workloadscenario_id': scenario_2.id}), {'select_teaching_assignment_to_remove': teaching_assignments_for_active_scenario[0].id})
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments =  TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),1)#One in total....
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__id=scenario_2.id).count(),0)#Zero for active scenario
   
        
    def test_scenario_status(self):
        '''This test simply checks the scenario forms for creating and editing the status of a workload scenario'''
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        first_fac = Faculty.objects.create(faculty_name = "first fac", faculty_acronym = "FRTE")
        first_dept = Department.objects.create(department_name = "noname", department_acronym="ACRN", faculty = first_fac)
        
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        first_label = 'new_test_scen'
        #Create one in draft mode
        self.client.post(reverse('workload_app:manage_scenario'),{'label':first_label, 'dept' : first_dept.id, 'fresh_record' : True, \
                                                                    'status': WorkloadScenario.DRAFT, 'academic_year' : 1})
        
        self.assertEqual(WorkloadScenario.objects.all().count(),1)
        #Default one is in draft mode
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.DRAFT).count(),1)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.OFFICIAL).count(),0)

        #Crate another one in OFFICIAL mode
        second_label = first_label+'2'
        self.client.post(reverse('workload_app:manage_scenario'),{'label':second_label, 'dept' : first_dept.id, 'fresh_record' : True, \
                                                                    'status': WorkloadScenario.OFFICIAL, 'academic_year' : 1})

        self.assertEqual(WorkloadScenario.objects.all().count(),2)
        #Default one is in draft mode
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.DRAFT).count(),1)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.OFFICIAL).count(),1)

        #Edit the official into draft
        new_scen_obj = WorkloadScenario.objects.filter(label = second_label).get()
        self.client.post(reverse('workload_app:manage_scenario'),{'scenario_id' : new_scen_obj.id, 'label':second_label, 'dept' : first_dept.id, 'fresh_record' : False, \
                                                                    'status': WorkloadScenario.DRAFT, 'academic_year' : 1})
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.DRAFT).count(),2)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.OFFICIAL).count(),0)

        #Create a second department
        second_dept = Department.objects.create(department_name = "second_dept", department_acronym="SCDP", faculty = first_fac)
        #Create a new scenario for this second department. Official one
        third_label = first_label+"3"
        self.client.post(reverse('workload_app:manage_scenario'),{'label':third_label, 'dept' : second_dept.id, 'fresh_record' : True, \
                                                                    'status': WorkloadScenario.OFFICIAL, 'academic_year' : 1})
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.DRAFT).count(),2)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.OFFICIAL).count(),1)

        #Now, for the first dept, turn the first scenario to official
        first_scen_obj = WorkloadScenario.objects.filter(label = first_label).get()
        self.client.post(reverse('workload_app:manage_scenario'),{'scenario_id' : first_scen_obj.id, 'label':first_label, 'dept' : first_dept.id, 'fresh_record' : False, \
                                                                    'status': WorkloadScenario.OFFICIAL, 'academic_year' : 1})
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.DRAFT).count(),1)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.OFFICIAL).count(),2)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.OFFICIAL).filter(label=third_label).count(),1)#

        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.DRAFT).filter(label=second_label).count(),1)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.DRAFT).filter(label=first_label).count(),0)

        #Now we turn even the second scenario into official mode. It is the same dept, same academic year as the first one. 
        # We want only one official one for same dept, same academic year
        #The expected behaviour is that, being the latest, the second scenario remains offocial (latest modified)
        #while the first gets turned automatically back into draft
        self.client.post(reverse('workload_app:manage_scenario'),{'scenario_id' : new_scen_obj.id, 'label':second_label, 'dept' : first_dept.id, 'fresh_record' : False, \
                                                                    'status': WorkloadScenario.OFFICIAL, 'academic_year' : 1})

        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.DRAFT).count(),1)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.OFFICIAL).count(),2)
        
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.DRAFT).filter(label=second_label).count(),0)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.DRAFT).filter(label=first_label).count(),1)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.OFFICIAL).filter(label=second_label).count(),1)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.OFFICIAL).filter(label=first_label).count(),0)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.OFFICIAL).filter(label=third_label).count(),1)#Other dept, untouched.

        #Add a draft one to the fist dept, same academic year
        fourth_label = first_label+'4'
        self.client.post(reverse('workload_app:manage_scenario'),{'label':fourth_label, 'dept' : first_dept.id, 'fresh_record' : True, \
                                                                    'status': WorkloadScenario.DRAFT, 'academic_year' : 1})
        
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.DRAFT).filter(label=fourth_label).count(),1)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.OFFICIAL).filter(label=fourth_label).count(),0)
        #The rest untouched
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.DRAFT).filter(label=second_label).count(),0)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.DRAFT).filter(label=first_label).count(),1)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.OFFICIAL).filter(label=second_label).count(),1)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.OFFICIAL).filter(label=first_label).count(),0)
        self.assertEqual(WorkloadScenario.objects.filter(status=WorkloadScenario.OFFICIAL).filter(label=third_label).count(),1)#Other dept, untouched.