from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *
from workload_app.models import Faculty,Lecturer, Module, TeachingAssignment,WorkloadScenario,\
    ModuleType,Department,EmploymentTrack,ServiceRole,Academicyear, UniversityStaff,TeachingAssignmentType
from workload_app.global_constants import DEFAULT_WORKLOAD_NAME,CalculateNumHoursBasedOnWeeklyInfo

class TestTeachingAssignments(TestCase):
    def setup_user(self):
        #The test client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
        self.user.is_superuser = True
        self.user.save()
        uni_user = UniversityStaff.objects.create(user = self.user, department=None,faculty=None)
        
    def test_add_delete_teaching_assignment(self):
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
        new_scen = WorkloadScenario.objects.create(label='test_scen',dept  =first_dept, academic_year=acad_year)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        
        normal_lecturer = Lecturer.objects.create(name="normal_lecturer",fraction_appointment=0.7, employment_track=track_def,service_role=srvc_role, workload_scenario=new_scen)
        educator_track = Lecturer.objects.create(name="educator_track",fraction_appointment=1.0, employment_track=track_def,service_role=srvc_role, workload_scenario=new_scen)
        vice_dean = Lecturer.objects.create(name="vice_dean",fraction_appointment=0.5, employment_track=track_def,service_role=srvc_role, workload_scenario=new_scen)
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE",department=first_dept)
        
        mod_code_1 = 'AS101'
        mod_code_2 = 'AS201'
        mod_code_3 = 'AS301'
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code_2, 'module_title' : 'module 2', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code_3, 'module_title' : 'module 3', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        
        self.assertEqual(Module.objects.all().count(),3)
        
        module_1 = Module.objects.filter(module_code = mod_code_1).get()
        module_2 = Module.objects.filter(module_code = mod_code_2).get()
        module_3 = Module.objects.filter(module_code = mod_code_3).get()
        
        empty_assign_list = TeachingAssignment.objects.all()
        self.assertEqual(empty_assign_list.count(),0)
        self.assertEqual(WorkloadScenario.objects.all().count(),1)#one is created abovet
        
        #add first assignment using the form
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=new_fac)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': new_scen.id}), data = {'select_lecturer': normal_lecturer.id, \
                 'select_module': module_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'36'})
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        wl_table = response.context['wl_table']
        self.assertEqual(len(wl_table),3)# 3 profs
        
        self.assertEqual(Lecturer.objects.all().count(),3)#3 profs in total
        
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),1)
        
        #Add another one. Same prof. Different module
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': new_scen.id}), data = {'select_lecturer': normal_lecturer.id, \
                 'select_module': module_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'65'})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        
        #The list of assignments must have grown to 2
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),2)

        ta = TeachingAssignment.objects.all().first()
        #Remove the first one we added
        self.client.post(reverse('workload_app:remove_assignment',  kwargs={'workloadscenario_id': new_scen.id}), {'select_teaching_assignment_to_remove': ta.id})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        #The list of assignments must have gone down to 1
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),1)

    def test_add_teaching_assignment_same_prof_same_mod(self):
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
        new_scen = WorkloadScenario.objects.create(label='test_scen', dept=first_dept, academic_year=acad_year)

        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department=first_dept)
        
        normal_lecturer = normal_lecturer = Lecturer.objects.create(name="normal_lecturer",fraction_appointment=0.7, employment_track=track_def,service_role=srvc_role, workload_scenario=new_scen);        
        mod_code_1 = 'AS101'
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': new_scen.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    

        module_1 = Module.objects.filter(module_code = mod_code_1).get() 
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        empty_assign_list = TeachingAssignment.objects.all()
        self.assertEqual(len(empty_assign_list),0)
        self.assertEqual(WorkloadScenario.objects.all().count(),1)#one is created above
        
        #Now add an assignment
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=new_fac)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': new_scen.id}), data = {'select_lecturer': normal_lecturer.id, \
                 'select_module': module_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'36'})
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        assign_list = TeachingAssignment.objects.all()
        self.assertEqual(len(assign_list),1)
        
        #Now add another one, same lecturer, same module, different hours
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': new_scen.id}), data = {'select_lecturer': normal_lecturer.id, \
                 'select_module': module_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'56'})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        assign_list = TeachingAssignment.objects.all()
        self.assertEqual(len(assign_list),1)#MUST still be one
        self.assertEqual(TeachingAssignment.objects.filter(assigned_module=module_1).count(),1)
        self.assertEqual(TeachingAssignment.objects.filter(assigned_lecturer=normal_lecturer).count(),1)
        
        obtained_wl_table = response.context['wl_table']
        self.assertEqual(len(obtained_wl_table),1)
        self.assertEqual(obtained_wl_table[0]['prof_name'],"normal_lecturer")
        self.assertEqual(obtained_wl_table[0]['assignments'],"AS101 (92)")
        self.assertAlmostEqual(obtained_wl_table[0]['prof_expected_hours'],56+36)#Number of hours is the sum of the existing plus the new one
        

    def test_edit_lecturer_assignments(self):
        ''' This test simulates the triggering of the edit assignemnt form. '''

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        #create two scenarios
        scen_name_1 = 'scen_1'
        scenario_1 = WorkloadScenario.objects.create(label=scen_name_1, dept = first_dept, academic_year=acad_year)
        
        scen_name_2 = 'scen_2'
        acad_year_2=Academicyear.objects.create(start_year=1233)
        scenario_2 = WorkloadScenario.objects.create(label=scen_name_2, dept = first_dept, academic_year=acad_year_2)
        
        normal_lecturer = Lecturer.objects.create(name="normal_lecturer",fraction_appointment=0.7, employment_track=track_def,service_role=srvc_role,   workload_scenario=scenario_1)
        educator_track = Lecturer.objects.create(name="educator_track",fraction_appointment=1.0, employment_track=track_def,service_role=srvc_role,    workload_scenario=scenario_1)
        vice_dean = Lecturer.objects.create(name="vice_dean",fraction_appointment=0.5, employment_track=track_def,service_role=srvc_role,    workload_scenario=scenario_1)

        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department=first_dept)
        
        mod_code_1 = 'AS101'
        mod_code_2 = 'AS201'
        mod_code_3 = 'AS301'
        
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_2, 'module_title' : 'module 2', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_3, 'module_title' : 'module 3', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.assertEqual(Module.objects.all().count(),3)
        
        module_1 = Module.objects.filter(module_code = mod_code_1).get()
        module_2 = Module.objects.filter(module_code = mod_code_2).get()
        module_3 = Module.objects.filter(module_code = mod_code_3).get()
        
        #Add 4 assignments (scenario 1)
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=new_fac)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': normal_lecturer.id, 'select_module': module_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'16'});
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': educator_track.id, 'select_module': module_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'26'});
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': vice_dean.id, 'select_module': module_3.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'36'});        
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': vice_dean.id, 'select_module': module_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'no','how_many_units':'46'});        
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),4)
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(len(teaching_assignments_for_active_scen),4)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='26').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='36').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='46').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(counted_towards_workload=True).count(),3)
        self.assertEqual(teaching_assignments_for_active_scen.filter(counted_towards_workload=False).count(),1)
        
        prof_id = vice_dean.id
        #NOW edit the assignment. Key change simulated: 145 hours for vice_dean teaching AS301 (editing from 36)
        mod_id_as201 = module_2.id #(AS201)
        mod_id_as301 = module_3.id #(AS301)
        self.client.post(reverse('workload_app:edit_lecturer_assignments', kwargs={'prof_id':prof_id}),\
                          {'teaching_assignment_type'+str(mod_id_as201):str(assignment_type.id),'teaching_assignment_type'+str(mod_id_as301):str(assignment_type.id),\
                           'how_many_units'+str(mod_id_as301) : '145', 'how_many_units'+str(mod_id_as201) : '46','counted_in_workload'+str(mod_id_as201) : 'yes', 'counted_in_workload'+str(mod_id_as301) : 'yes'})
        #Check the new status
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),4)
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(len(teaching_assignments_for_active_scen),4)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='26').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='36').exists(),False)#Note that 145 replaced 36
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='46').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='145').exists(),True)
        
        workload_table = response.context['wl_table']
        self.assertEqual(len(workload_table),3)
        self.assertEqual(workload_table[1]['prof_name'],'normal_lecturer')
        self.assertEqual(workload_table[0]['prof_name'],'educator_track') #starts with e, should go first
        self.assertEqual(workload_table[2]['prof_name'],'vice_dean')
        #We examine the vice dean that should have the assignment changed
        self.assertEqual(workload_table[2]['assignments'],'AS201 (46), AS301 (145)')
        self.assertEqual(workload_table[2]['total_hours_for_prof'],46+145)        
        #Check that the module table also changed
        module_table = response.context['mod_table']
        self.assertEqual(len(module_table),3)
        self.assertEqual(module_table[0]["module_code"],'AS101')
        self.assertEqual(module_table[1]["module_code"],'AS201')
        self.assertEqual(module_table[2]["module_code"],'AS301')
        self.assertEqual(module_table[2]["module_lecturers"],'vice_dean (145)')
        self.assertEqual(module_table[2]["module_assigned_hours"],145)
        
        
    def test_edit_assignment_with_zero_hours(self):
        ''' This test simulates the triggering of the edit assignemnt form, same as above,
            but covers the behaviour of setting the hours to zero to remove the assignment'''  

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        #create two scenarios
        scen_name_1 = 'scen_1'
        scenario_1 = WorkloadScenario.objects.create(label=scen_name_1, dept = first_dept, academic_year=acad_year)
        
        normal_lecturer = Lecturer.objects.create(name="normal_lecturer",fraction_appointment=0.7, employment_track=track_def,service_role=srvc_role,    workload_scenario=scenario_1)
        educator_track = Lecturer.objects.create(name="educator_track",fraction_appointment=1.0, employment_track=track_def,service_role=srvc_role,    workload_scenario=scenario_1)
        vice_dean = Lecturer.objects.create(name="vice_dean",fraction_appointment=0.5,  employment_track=track_def,service_role=srvc_role,   workload_scenario=scenario_1)
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department=first_dept)
        
        mod_code_1 = 'AS101'
        mod_code_2 = 'AS201'
        mod_code_3 = 'AS301'
        
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_2, 'module_title' : 'module 2', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_3, 'module_title' : 'module 3', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.assertEqual(Module.objects.all().count(),3)
        
        module_1 = Module.objects.filter(module_code = mod_code_1).get()
        module_2 = Module.objects.filter(module_code = mod_code_2).get()
        module_3 = Module.objects.filter(module_code = mod_code_3).get()
        
        #Add 5 assignments (scenario 1)
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=new_fac)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': normal_lecturer.id, 'select_module': module_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'16'});
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': educator_track.id, 'select_module': module_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'26'});
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': educator_track.id, 'select_module': module_3.id,'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'126'});        
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': vice_dean.id, 'select_module': module_3.id,'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'36'});        
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': vice_dean.id, 'select_module': module_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'46'});        
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),5)
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(len(teaching_assignments_for_active_scen),5)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='26').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='126').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='36').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='46').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(counted_towards_workload=True).count(),5)
        
        prof_id = vice_dean.id
        #NOW edit the assignment. Key change simulated: 0 hours for vice_dean teaching AS301 (editing from 36)
        mod_id_as201 = module_2.id #(AS201)
        mod_id_as301 = module_3.id #(AS301)
        self.client.post(reverse('workload_app:edit_lecturer_assignments', kwargs={'prof_id':prof_id}), \
        {'teaching_assignment_type'+str(mod_id_as201):str(assignment_type.id),'teaching_assignment_type'+str(mod_id_as301):str(assignment_type.id),\
                           'how_many_units'+str(mod_id_as301) : '0', 'how_many_units'+str(mod_id_as201) : '46','counted_in_workload'+str(mod_id_as201) : 'yes', 'counted_in_workload'+str(mod_id_as301) : 'yes'})
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),4)#Down from 5, the one with 0 hours is gone...
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(len(teaching_assignments_for_active_scen),4)#Same as above
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='26').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='126').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='36').exists(),False)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='46').exists(),True)      
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='0').exists(),False)
        self.assertEqual(teaching_assignments_for_active_scen.filter(counted_towards_workload=True).count(),4)
        #Now switch the "counted" flag to false
        self.client.post(reverse('workload_app:edit_lecturer_assignments', kwargs={'prof_id':prof_id}), \
                {'teaching_assignment_type'+str(mod_id_as201):str(assignment_type.id),'how_many_units'+str(mod_id_as201) : '46','counted_in_workload'+str(mod_id_as201) : 'no'})

        
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),4)#Down from 5, the one with 0 hours is gone...
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(len(teaching_assignments_for_active_scen),4)#Same as above
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='26').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='126').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='36').exists(),False)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='46').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(counted_towards_workload=True).count(),3)
        self.assertEqual(teaching_assignments_for_active_scen.filter(counted_towards_workload=False).count(),1)


    def test_edit_assignment_with_zero_hours_multiple_scenarios(self):
        ''' This test simulates the triggering of the edit assignemnt form,
            covers the behaviour of setting the hours to zero to remove the assignment, same as above,
            but with multiple scenarios. This test uncovers a bug that was found and fixed'''  

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        #create two scenarios
        scen_name_1 = 'scen_1'
        scenario_1 = WorkloadScenario.objects.create(label=scen_name_1, dept = first_dept, academic_year=acad_year)
        
        scen_name_2 = 'scen_2'
        acad_year_2=Academicyear.objects.create(start_year=2343)
        scenario_2 = WorkloadScenario.objects.create(label=scen_name_2, dept = first_dept, academic_year=acad_year_2)
        
        #create 3 lecturers in scenario 1
        normal_lecturer = Lecturer.objects.create(name="normal_lecturer",fraction_appointment=0.7, employment_track=track_def,service_role=srvc_role,  workload_scenario=scenario_1)
        educator_track = Lecturer.objects.create(name="educator_track",fraction_appointment=1.0,  employment_track=track_def,service_role=srvc_role, workload_scenario=scenario_1)
        vice_dean = Lecturer.objects.create(name="vice_dean",fraction_appointment=0.5, employment_track=track_def,service_role=srvc_role,  workload_scenario=scenario_1)
        
        #create 3 lecturers in scenario 2
        normal_lecturer_2 = Lecturer.objects.create(name="normal_lecturer",fraction_appointment=0.7, employment_track=track_def,service_role=srvc_role,  workload_scenario=scenario_2)
        educator_track_2 = Lecturer.objects.create(name="educator_track",fraction_appointment=1.0, employment_track=track_def,service_role=srvc_role,  workload_scenario=scenario_2)
        vice_dean_2 = Lecturer.objects.create(name="vice_dean",fraction_appointment=0.5, employment_track=track_def,service_role=srvc_role,  workload_scenario=scenario_2)

        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department = first_dept)
        
        mod_code_1 = 'AS101'
        mod_code_2 = 'AS201'
        mod_code_3 = 'AS301'
        #create 3 modules in scenario 1
        module_1 = Module.objects.create(module_code = mod_code_1, module_title = 'module 1', total_hours = 234, module_type = mod_type_1, semester_offered = Module.UNASSIGNED, number_of_tutorial_groups = 2, scenario_ref = scenario_1)
        module_2 = Module.objects.create(module_code = mod_code_2, module_title = 'module 1', total_hours = 234, module_type = mod_type_1, semester_offered = Module.UNASSIGNED, number_of_tutorial_groups = 2, scenario_ref = scenario_1)
        module_3 = Module.objects.create(module_code = mod_code_3, module_title = 'module 1', total_hours = 234, module_type = mod_type_1, semester_offered = Module.UNASSIGNED, number_of_tutorial_groups = 2, scenario_ref = scenario_1)
        self.assertEqual(Module.objects.all().count(),3)
        
        #Create 3 modules in scenario 2 - THIS IS IMPORTANT. The bug was discovered because there modules iwth the same codes in inactive scenarios
        module_1_scen_2 = Module.objects.create(module_code = mod_code_1, module_title = 'module 1', total_hours = 234, module_type = mod_type_1, semester_offered = Module.UNASSIGNED, number_of_tutorial_groups = 2, scenario_ref = scenario_2)
        module_2_scen_2 = Module.objects.create(module_code = mod_code_2, module_title = 'module 1', total_hours = 234, module_type = mod_type_1, semester_offered = Module.UNASSIGNED, number_of_tutorial_groups = 2, scenario_ref = scenario_2)
        module_3_scen_2 = Module.objects.create(module_code = mod_code_3, module_title = 'module 1', total_hours = 234, module_type = mod_type_1, semester_offered = Module.UNASSIGNED, number_of_tutorial_groups = 2, scenario_ref = scenario_2) 
        self.assertEqual(Module.objects.all().count(),6)
        
        #Add 5 assignments (scenario 1)
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=new_fac)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': normal_lecturer.id, 'select_module': module_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'16'});
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': educator_track.id, 'select_module': module_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'26'});
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': educator_track.id, 'select_module': module_3.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'126'});        
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': vice_dean.id, 'select_module': module_3.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'36'});        
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': vice_dean.id, 'select_module': module_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'46'});        
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),5)
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(len(teaching_assignments_for_active_scen),5)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='26').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='126').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='36').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='46').exists(),True)        
        
        prof_id = vice_dean.id
        #NOW edit the assignment. Key change simulated: 0 hours for vice_dean teaching AS301 (editing from 36)
        mod_id_as201 = module_2.id #(AS201)
        mod_id_as301 = module_3.id #(AS301)
        self.client.post(reverse('workload_app:edit_lecturer_assignments', kwargs={'prof_id':prof_id}), \
                {'teaching_assignment_type'+str(mod_id_as201):str(assignment_type.id),'teaching_assignment_type'+str(mod_id_as301):str(assignment_type.id),\
                           'how_many_units'+str(mod_id_as301) : '0', 'how_many_units'+str(mod_id_as201) : '46','counted_in_workload'+str(mod_id_as201) : 'yes', 'counted_in_workload'+str(mod_id_as301) : 'yes'})

        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),4)#Down from 5, the one with 0 hours is gone...
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(len(teaching_assignments_for_active_scen),4)#Same as above
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='26').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='126').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='36').exists(),False)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='46').exists(),True)      
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='0').exists(),False)

    def test_edit_module_assignments(self):
        ''' This test is similar to the one above, but tests the edit_module_assignment method instead '''

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        
        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        
        first_dept = Department.objects.create(department_name = "noname", department_acronym="ACRN", faculty=new_fac)

        #create two scenarios
        scen_name_1 = 'scen_1'
        scenario_1 = WorkloadScenario.objects.create(label=scen_name_1, dept = first_dept, academic_year=acad_year)
        
        normal_lecturer = Lecturer.objects.create(name="normal_lecturer",fraction_appointment=0.7, employment_track=track_def,service_role=srvc_role,  workload_scenario=scenario_1);
        educator_track = Lecturer.objects.create(name="educator_track",fraction_appointment=1.0,  employment_track=track_def,service_role=srvc_role, workload_scenario=scenario_1);
        vice_dean = Lecturer.objects.create(name="vice_dean",fraction_appointment=0.5, employment_track=track_def,service_role=srvc_role,  workload_scenario=scenario_1);
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department = first_dept)
        
        mod_code_1 = 'AS101'
        mod_code_2 = 'AS201'
        mod_code_3 = 'AS301'
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_2, 'module_title' : 'module 2', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_3, 'module_title' : 'module 3', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.assertEqual(Module.objects.all().count(),3)
        
        module_1 = Module.objects.filter(module_code = mod_code_1).get()
        module_2 = Module.objects.filter(module_code = mod_code_2).get()
        module_3 = Module.objects.filter(module_code = mod_code_3).get()
        
        #Add 4 assignments (scenario 1)
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=new_fac)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': normal_lecturer.id, 'select_module': module_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'16'});
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': educator_track.id, 'select_module': module_3.id,'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'26'});        
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': vice_dean.id, 'select_module': module_3.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'36'});        
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': vice_dean.id, 'select_module': module_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'46'});        
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),4)
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(len(teaching_assignments_for_active_scen),4)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='26').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='36').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='46').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(counted_towards_workload=True).count(), 4)
        
        module_object = Module.objects.filter(module_code=mod_code_3).filter(scenario_ref__label = scen_name_1).get()
        module_id = module_object.id

        #NOW edit the assignment. Key change simulated: 145 hours for vice_dean teaching AS301 (editing from 36)
        self.client.post(reverse('workload_app:edit_module_assignments',kwargs={'module_id':module_id}), \
            {'teaching_assignment_type'+str(educator_track.id):str(assignment_type.id),'teaching_assignment_type'+str(vice_dean.id):str(assignment_type.id),\
              'how_many_units'+str(vice_dean.id) : '145', 'how_many_units'+str(educator_track.id) : '26','counted_in_workload'+str(educator_track.id) : 'yes', 'counted_in_workload'+str(vice_dean.id) : 'yes'})

        #Check the new status
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),4)
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(len(teaching_assignments_for_active_scen),4)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='26').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='36').exists(),False)#Not there any more 145 is there now
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='46').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='145').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='145').filter(assigned_lecturer=vice_dean.id).exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='145').filter(assigned_module=module_3.id).exists(),True)
        
        workload_table = response.context['wl_table']
        self.assertEqual(len(workload_table),3)
        self.assertEqual(workload_table[0]['prof_name'],'educator_track')#starts with e. Will go first
        self.assertEqual(workload_table[1]['prof_name'],'normal_lecturer')
        self.assertEqual(workload_table[2]['prof_name'],'vice_dean')
        #We examine the vice dean that should have the assignment changed        
        self.assertEqual(workload_table[2]['assignments'],'AS201 (46), AS301 (145)')
        self.assertEqual(workload_table[2]['total_hours_for_prof'],46+145)
        
        #Check that the module table changed
        module_table = response.context['mod_table']
        self.assertEqual(len(module_table),3)
        self.assertEqual(module_table[0]["module_code"],'AS101')
        self.assertEqual(module_table[1]["module_code"],'AS201')
        self.assertEqual(module_table[2]["module_code"],'AS301')
        self.assertEqual(module_table[2]["module_assigned_hours"],145+26)#AS301 has 2 profs assigned
        self.assertEqual(module_table[2]["module_lecturers"],'educator_track (26), vice_dean (145)')

        #NOW edit the assignment. Key change simulated:switch the flag for "counted in workload" to false for one assignment
        self.client.post(reverse('workload_app:edit_module_assignments',kwargs={'module_id':module_id}),\
                    {'teaching_assignment_type'+str(educator_track.id):str(assignment_type.id),'teaching_assignment_type'+str(vice_dean.id):str(assignment_type.id),\
              'how_many_units'+str(vice_dean.id) : '145', 'how_many_units'+str(educator_track.id) : '26','counted_in_workload'+str(educator_track.id) : 'yes', 'counted_in_workload'+str(vice_dean.id) : 'no'})

        self.assertEqual(teaching_assignments_for_active_scen.filter(counted_towards_workload=True).count(), 3)
        self.assertEqual(teaching_assignments_for_active_scen.filter(counted_towards_workload=False).count(), 1)

    def test_edit_module_assignments_zero_hours(self):
        ''' This test is similar to the one above, but tests the edit_module_assignment method instead 
             and tests the case where the use inputs zero hours (the expected behaviour 
             is that the assignment should be removed '''

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
      
        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        first_dept = Department.objects.create(department_name = "noname", department_acronym="ACRN", faculty=new_fac)
        #create two scenarios
        scen_name_1 = 'scen_1'
        scenario_1 = WorkloadScenario.objects.create(label=scen_name_1, dept = first_dept, academic_year=acad_year)
        
        scen_name_2 = 'scen_2'
        acad_year_2 = Academicyear.objects.create(start_year=1234)
        scenario_2 = WorkloadScenario.objects.create(label=scen_name_2, dept = first_dept, academic_year=acad_year_2)
        
        normal_lecturer = Lecturer.objects.create(name="normal_lecturer",fraction_appointment=0.7, employment_track=track_def,service_role=srvc_role,  workload_scenario=scenario_1)
        educator_track = Lecturer.objects.create(name="educator_track",fraction_appointment=1.0, employment_track=track_def,service_role=srvc_role,  workload_scenario=scenario_1)
        vice_dean = Lecturer.objects.create(name="vice_dean",fraction_appointment=0.5,  employment_track=track_def,service_role=srvc_role, workload_scenario=scenario_1)
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department=first_dept)
        
        mod_code_1 = 'AS101'
        mod_code_2 = 'AS201'
        mod_code_3 = 'AS301'
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_1, 'module_title' : 'module 1', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_2, 'module_title' : 'module 2', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code_3, 'module_title' : 'module 3', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : True})    
        self.assertEqual(Module.objects.all().count(),3)
        
        module_1 = Module.objects.filter(module_code = mod_code_1).get()
        module_2 = Module.objects.filter(module_code = mod_code_2).get()
        module_3 = Module.objects.filter(module_code = mod_code_3).get()
        

        #Add 4 assignments (scenario 1)
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=new_fac)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': normal_lecturer.id, 'select_module': module_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'16'});
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': educator_track.id, 'select_module': module_3.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'26'});        
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': vice_dean.id, 'select_module': module_3.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'36'});        
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': vice_dean.id, 'select_module': module_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'46'});        
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),4)
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(len(teaching_assignments_for_active_scen),4)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='26').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='36').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='46').exists(),True)
        
        module_object = Module.objects.filter(module_code=mod_code_3).filter(scenario_ref__label = scen_name_1).get()
        module_id = module_object.id
        
        #NOW edit the assignment. Key change simulated: 0 hours for vice_dean teaching AS301 (editing from 36)
        #Expected behaviour: the whole assignment should be removed
        self.client.post(reverse('workload_app:edit_module_assignments', kwargs={'module_id':module_id}),\
            {'teaching_assignment_type'+str(educator_track.id):str(assignment_type.id),'teaching_assignment_type'+str(vice_dean.id):str(assignment_type.id),\
              'how_many_units'+str(vice_dean.id) : '0', 'how_many_units'+str(educator_track.id) : '26','counted_in_workload'+str(educator_track.id) : 'yes', 'counted_in_workload'+str(vice_dean.id) : 'yes'})
        
        #Check the new status
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),3)#Down from 4
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_1.id)
        self.assertEqual(len(teaching_assignments_for_active_scen),3)#Down from 4
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='26').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='36').exists(),False)#No more 36
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='46').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='0').exists(),False)#Zero should never be there...
        
    def test_edit_module_assignments_zero_hours_multiple_scenarios(self):
        ''' This test is similar to the one above, it also tests the edit_module_assignment method
             and tests the case where the use inputs zero hours (the expected behaviour 
             is that the assignment should be removed). However it does so in the presence of other 
             lecturers in inactive scenario. This test was added after discovering a bug in these circumastances  '''

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        first_dept = Department.objects.create(department_name = "noname", department_acronym="ACRN", faculty=new_fac)
        #create two scenarios
        scen_name_1 = 'scen_1'
        scenario_1 = WorkloadScenario.objects.create(label=scen_name_1, dept = first_dept, academic_year=acad_year)
        
        scen_name_2 = 'scen_2'
        acad_year_2 = Academicyear.objects.create(start_year=1233)
        scenario_2 = WorkloadScenario.objects.create(label=scen_name_2, dept = first_dept, academic_year=acad_year_2)
        
        #create 3 lecturers in scenario 1
        normal_lecturer = Lecturer.objects.create(name="normal_lecturer",fraction_appointment=0.7, employment_track=track_def,service_role=srvc_role,  workload_scenario=scenario_1)
        educator_track = Lecturer.objects.create(name="educator_track",fraction_appointment=1.0,  employment_track=track_def,service_role=srvc_role,  workload_scenario=scenario_1)
        vice_dean = Lecturer.objects.create(name="vice_dean",fraction_appointment=0.5, employment_track=track_def,service_role=srvc_role,   workload_scenario=scenario_1)
        
        #create 3 lecturers in scenario 2 - THIS IS IMPORTANT. The bug was discovered because there were lecturers with the same names in inactive scenarios
        normal_lecturer_2 = Lecturer.objects.create(name="normal_lecturer",fraction_appointment=0.7, employment_track=track_def,service_role=srvc_role,  workload_scenario=scenario_2)
        educator_track_2 = Lecturer.objects.create(name="educator_track",fraction_appointment=1.0, employment_track=track_def,service_role=srvc_role,  workload_scenario=scenario_2)
        vice_dean_2 = Lecturer.objects.create(name="vice_dean",fraction_appointment=0.5,  employment_track=track_def,service_role=srvc_role, workload_scenario=scenario_2)
        
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department = first_dept)
        
        mod_code_1 = 'AS101'
        mod_code_2 = 'AS201'
        mod_code_3 = 'AS301'
        #create 3 modules in scenario 1
        module_1 = Module.objects.create(module_code = mod_code_1, module_title = 'module 1', total_hours = 234, module_type = mod_type_1, semester_offered = Module.UNASSIGNED, number_of_tutorial_groups = 2, scenario_ref = scenario_1)
        module_2 = Module.objects.create(module_code = mod_code_2, module_title = 'module 1', total_hours = 234, module_type = mod_type_1, semester_offered = Module.UNASSIGNED, number_of_tutorial_groups = 2, scenario_ref = scenario_1)
        module_3 = Module.objects.create(module_code = mod_code_3, module_title = 'module 1', total_hours = 234, module_type = mod_type_1, semester_offered = Module.UNASSIGNED, number_of_tutorial_groups = 2, scenario_ref = scenario_1)
        self.assertEqual(Module.objects.all().count(),3)
        
        #Create 3 modules in scenario 2 - 
        module_1_scen_2 = Module.objects.create(module_code = mod_code_1, module_title = 'module 1', total_hours = 234, module_type = mod_type_1, semester_offered = Module.UNASSIGNED, number_of_tutorial_groups = 2, scenario_ref = scenario_2)
        module_2_scen_2 = Module.objects.create(module_code = mod_code_2, module_title = 'module 1', total_hours = 234, module_type = mod_type_1, semester_offered = Module.UNASSIGNED, number_of_tutorial_groups = 2, scenario_ref = scenario_2)
        module_3_scen_2 = Module.objects.create(module_code = mod_code_3, module_title = 'module 1', total_hours = 234, module_type = mod_type_1, semester_offered = Module.UNASSIGNED, number_of_tutorial_groups = 2, scenario_ref = scenario_2) 
        self.assertEqual(Module.objects.all().count(),6)
        
        #Add 4 assignments (scenario 2)
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=new_fac)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_2.id}), {'select_lecturer': normal_lecturer_2.id, 'select_module': module_1_scen_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'16'});
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_2.id}), {'select_lecturer': educator_track_2.id, 'select_module': module_3_scen_2.id,'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'26'});        
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_2.id}), {'select_lecturer': vice_dean_2.id, 'select_module': module_3_scen_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'36'});        
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_2.id}), {'select_lecturer': vice_dean_2.id, 'select_module': module_2_scen_2.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'46'});        
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),4)
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_2.id)
        self.assertEqual(len(teaching_assignments_for_active_scen),4)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='26').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='36').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='46').exists(),True)
        
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),4)#

        #NOW edit the assignment. Key change simulated: 0 hours for vice_dean teaching AS301 (editing from 36)
        #Expected behaviour: the whole assignment should be removed
        module_object = Module.objects.filter(module_code=mod_code_3).filter(scenario_ref__id = scenario_2.id).get()
        module_id = module_object.id
        self.client.post(reverse('workload_app:edit_module_assignments', kwargs={'module_id':module_id}),\
        {'teaching_assignment_type'+str(educator_track_2.id):str(assignment_type.id),'teaching_assignment_type'+str(vice_dean_2.id):str(assignment_type.id),\
              'how_many_units'+str(vice_dean_2.id) : '0', 'how_many_units'+str(educator_track_2.id) : '26','counted_in_workload'+str(educator_track_2.id) : 'yes', 'counted_in_workload'+str(vice_dean_2.id) : 'yes'})

        #Check the new status
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        teaching_assignments = TeachingAssignment.objects.all()
        self.assertEqual(teaching_assignments.count(),3)#Down from 4
        teaching_assignments_for_active_scen = TeachingAssignment.objects.filter(workload_scenario__id = scenario_2.id)
        self.assertEqual(len(teaching_assignments_for_active_scen),3)#Down from 4
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='16').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='26').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='36').exists(),False)#No more 36
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='46').exists(),True)
        self.assertEqual(teaching_assignments_for_active_scen.filter(number_of_hours='0').exists(),False)#Zero should never be there...

    def test_teaching_assignments_copied_over(self):
        ''' This test checks that when we copy over modules, lecturers and teaching assignments
        from one scenario to a new one, we do proper duplicatons'''

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        #create one scenario
        scen_name_1 = 'scen_1'
        scenario_1 = WorkloadScenario.objects.create(label=scen_name_1, dept = first_dept, academic_year=acad_year)
        
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(WorkloadScenario.objects.all().count(), 1)

        new_role = ServiceRole.objects.create(role_name='test_role', role_adjustment = 0.8)
        new_track = EmploymentTrack.objects.create(track_name='test_track', track_adjustment = 0.8)

        #Add bob as professor
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_1.id}),{'name':'bob','fraction_appointment' : '0.7',    'service_role' : new_role.id, 'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        #Add a new module
        mod_code = 'XXX1'
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department = first_dept)
        
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_1.id}), {'module_code': mod_code, 'module_title' : 'testing', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '1',  'fresh_record' : True})
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues

        obtained_profs_list = Lecturer.objects.all()
        self.assertEqual(obtained_profs_list.count(),1)
        self.assertEqual(obtained_profs_list.filter(name='bob').filter(workload_scenario__label = scen_name_1).exists(),True)
        self.assertEqual(obtained_profs_list.filter(name='bob').filter(workload_scenario__label = scen_name_1).count(),1)
        
        obtained_mod_list = Module.objects.all()
        self.assertEqual(obtained_mod_list.count(),1)
        self.assertEqual(obtained_mod_list.filter(module_code=mod_code).filter(scenario_ref__label = scen_name_1).exists(),True)
        self.assertEqual(obtained_mod_list.filter(module_code=mod_code).filter(scenario_ref__label = scen_name_1).count(),1)

        bob_lecturer = Lecturer.objects.filter(name='bob').filter(workload_scenario__label = scen_name_1).get()
        module_1 = Module.objects.filter(module_code=mod_code).filter(scenario_ref__label = scen_name_1).get()
        #Assign module to Bob
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=new_fac)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': scenario_1.id}), {'select_lecturer': bob_lecturer.id, 'select_module': module_1.id, 'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'16'})
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))    
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(TeachingAssignment.objects.all().count(), 1)
        
        #NOW CREATE ANOTHER SCENARIO copying from the existing one
        scen_name_2 = 'scen_2'
        acad_year = Academicyear.objects.create(start_year=2200)
        self.client.post(reverse('workload_app:manage_scenario'), {'label': scen_name_2, 'dept' : first_dept.id, 'status': WorkloadScenario.DRAFT, 'copy_from': scenario_1.id,'fresh_record' : True, 'academic_year' : acad_year.id})
        scenario_2 = WorkloadScenario.objects.filter(label=scen_name_2)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.get().id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(WorkloadScenario.objects.all().count(), 2)
        self.assertEqual(Lecturer.objects.all().count(),2)
        self.assertEqual(Module.objects.all().count(),2)
        
        #Now edit bob in scenario 2 (the active one) - KEY CHANNGE: appointment adjustment from 2 to 1
        response = self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': scenario_2.get().id}),{'name':'bob','fraction_appointment' : '0.7',    'service_role' : new_role.id, 'employment_track': new_track.id,'is_external': False, 'fresh_record' : False})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.get().id}))
        self.assertEqual(response.status_code, 200) #No issues
        #NOw we check that bob in scenario 2 (which was edited) 
        #is the one linked to the teaching assignment  in scenario 2
        self.assertEqual(TeachingAssignment.objects.filter(assigned_lecturer__name = 'bob').count(), 2)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_2).count(), 1)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_1).count(), 1)
        
        bob_in_scen_2  = Lecturer.objects.filter(name='bob').filter(workload_scenario__label = scen_name_2).get()
        prof_id = bob_in_scen_2.id

        mod_id = Module.objects.filter(module_code = mod_code).filter(scenario_ref = scenario_2.get()).get().id
        #Now edit the teaching assignment for bob in scenario 2 (still the active one)
        #Key edit from 16 hours to 145 hours
        self.client.post(reverse('workload_app:edit_lecturer_assignments' , kwargs={'prof_id':prof_id}),\
                          {'teaching_assignment_type'+str(mod_id) : str(assignment_type.id), 'how_many_units'+str(mod_id) : '145', 'counted_in_workload'+str(mod_id) : 'yes'})
    
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.get().id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(TeachingAssignment.objects.filter(assigned_lecturer__name = 'bob').count(), 2)
        self.assertEqual(TeachingAssignment.objects.filter(number_of_hours = '145').count(), 1)
        self.assertEqual(TeachingAssignment.objects.filter(number_of_hours = '145').filter(workload_scenario__label = scen_name_1).count(), 0)
        self.assertEqual(TeachingAssignment.objects.filter(number_of_hours = '145').filter(workload_scenario__label = scen_name_2).count(), 1)
        #Check that the assignment in scenario 1 is untouched
        self.assertEqual(TeachingAssignment.objects.filter(number_of_hours = '16').count(), 1)
        self.assertEqual(TeachingAssignment.objects.filter(number_of_hours = '16').filter(workload_scenario__label = scen_name_1).count(), 1)
        self.assertEqual(TeachingAssignment.objects.filter(number_of_hours = '16').filter(workload_scenario__label = scen_name_2).count(), 0)
        
        #Now edit the module in scenario 2 (the active one) - KEY CHANGE num tutorial groups is now 2
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': scenario_2.get().id}), {'module_code': mod_code, 'module_title' : 'testing', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '2',  'fresh_record' : False})
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.get().id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(TeachingAssignment.objects.filter(assigned_module__module_code = mod_code).count(), 2)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_2).count(), 1)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_1).count(), 1)
        self.assertEqual(TeachingAssignment.objects.filter(assigned_module__number_of_tutorial_groups = '2').count(), 1)
        self.assertEqual(TeachingAssignment.objects.filter(assigned_module__number_of_tutorial_groups = '2').filter(workload_scenario__label = scen_name_2).count(), 1)
        self.assertEqual(TeachingAssignment.objects.filter(assigned_module__number_of_tutorial_groups = '2').filter(workload_scenario__label = scen_name_1).count(), 0)
        self.assertEqual(TeachingAssignment.objects.filter(assigned_module__number_of_tutorial_groups = '1').count(), 1)
        self.assertEqual(TeachingAssignment.objects.filter(assigned_module__number_of_tutorial_groups = '1').filter(workload_scenario__label = scen_name_2).count(), 0)
        self.assertEqual(TeachingAssignment.objects.filter(assigned_module__number_of_tutorial_groups = '1').filter(workload_scenario__label = scen_name_1).count(), 1)
        
        module_object = Module.objects.filter(module_code=mod_code).filter(scenario_ref__label = scen_name_2).get()
        module_id = module_object.id
        #Now edit the teaching assignment for the module in scenario 2 (still the active one)
        #Key edit from 145 to 389
        bob_2_id = bob_in_scen_2.id
        self.client.post(reverse('workload_app:edit_module_assignments', \
                                 kwargs={'module_id':module_id}), {'how_many_units'+str(bob_2_id) : '389', 'counted_in_workload'+str(bob_2_id): 'yes','teaching_assignment_type'+str(bob_2_id):str(assignment_type.id) })

        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.get().id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(TeachingAssignment.objects.filter(assigned_lecturer__name = 'bob').count(), 2)
        self.assertEqual(TeachingAssignment.objects.filter(assigned_module__module_code = mod_code).count(), 2)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_2).count(), 1)
        self.assertEqual(TeachingAssignment.objects.filter(workload_scenario__label = scen_name_1).count(), 1)
        
        self.assertEqual(TeachingAssignment.objects.filter(number_of_hours = '389').count(), 1)
        self.assertEqual(TeachingAssignment.objects.filter(number_of_hours = '389').filter(workload_scenario__label = scen_name_1).count(), 0)
        self.assertEqual(TeachingAssignment.objects.filter(number_of_hours = '389').filter(workload_scenario__label = scen_name_2).count(), 1)
        
        self.assertEqual(TeachingAssignment.objects.filter(number_of_hours = '145').count(), 0)
        self.assertEqual(TeachingAssignment.objects.filter(number_of_hours = '145').filter(workload_scenario__label = scen_name_1).count(), 0)
        self.assertEqual(TeachingAssignment.objects.filter(number_of_hours = '145').filter(workload_scenario__label = scen_name_2).count(), 0)
        #Check that the assignment in scenario 1 is untouched
        self.assertEqual(TeachingAssignment.objects.filter(number_of_hours = '16').count(), 1)
        self.assertEqual(TeachingAssignment.objects.filter(number_of_hours = '16').filter(workload_scenario__label = scen_name_1).count(), 1)
        self.assertEqual(TeachingAssignment.objects.filter(number_of_hours = '16').filter(workload_scenario__label = scen_name_2).count(), 0)

    
    def test_add_assignment_special_service_role(self):
        '''
        This test is introduced after finding out a bug whereby, in one scenario, if the first lecturer 
        has 0 tFTE, you can't assign anything to him first
        '''
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
       
        #check all good at the start        
        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        srvc_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        track_def = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 1.0, faculty=new_fac)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        #Create a new scenario
        first_label = 'test_scen'
        first_scen = WorkloadScenario.objects.create(label=first_label, dept=first_dept, academic_year=acad_year)
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues

        new_role = ServiceRole.objects.create(role_name='test_role', role_adjustment = 0.0, faculty=new_fac)#Note the 0 there
        new_role_2 = ServiceRole.objects.create(role_name='test_role_2', role_adjustment = 0.5, faculty=new_fac)#Note not zero here
        new_track = EmploymentTrack.objects.create(track_name='test_track', track_adjustment = 0.8, faculty=new_fac)

        self.assertEqual(WorkloadScenario.objects.all().count(), 1)
        
        #Add bob (role 1) and ted (role 2) as professors
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': first_scen.id}),{'name':'bob','fraction_appointment' : '0.7',    'service_role' : new_role.id,'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': first_scen.id}),{'name':'ted','fraction_appointment' : '0.5',    'service_role' : new_role_2.id,'employment_track': new_track.id, 'is_external': False,'fresh_record' : True})
        #Add a new module
        mod_code = 'XXX1'
        #Create a module type
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE", department=first_dept)
        
        self.client.post(reverse('workload_app:add_module',  kwargs={'workloadscenario_id': first_scen.id}), {'module_code': mod_code, 'module_title' : 'testing', 'total_hours' : '234', 'module_type' : mod_type_1.id, 'semester_offered' : Module.UNASSIGNED, 'number_of_tutorial_groups' : '1',  'fresh_record' : True})
        
        #Check still all good
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues

        module_object = Module.objects.filter(module_code=mod_code).filter(scenario_ref__label = first_label).get()
        module_id = module_object.id

        bob_lecturer = Lecturer.objects.filter(name='bob').filter(workload_scenario__label = first_label).get()
        ted_lecturer = Lecturer.objects.filter(name='ted').filter(workload_scenario__label = first_label).get()
        module_1 = Module.objects.filter(module_code=mod_code).filter(scenario_ref__label = first_label).get()
        #Assign module to Bob, using weekly assignments
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=new_fac)
        self.client.post(reverse('workload_app:add_assignment',  kwargs={'workloadscenario_id': first_scen.id}), {'select_lecturer': bob_lecturer.id,
                                                                   'select_module': module_1.id,
                                                                   'teaching_assignment_type' : assignment_type.id, 'counted_towards_workload' : 'yes','how_many_units':'25'});
        #Check still all good - this used to crash before the bug was fixed
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': first_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues