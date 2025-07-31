import datetime
from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *
from workload_app.models import WorkloadScenario,Department, Faculty, ProgrammeOffered, Academicyear, Lecturer, \
    ServiceRole, EmploymentTrack, Module, ModuleType,TeachingAssignment, UniversityStaff

class TestDepartments(TestCase):
    def setup_user(self):
        #The test client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
        self.user.is_superuser = True
        self.user.save()
        uni_user = UniversityStaff.objects.create(user = self.user, department=None,faculty=None)
        
    def test_add_remove(self):

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(Department.objects.all().count(),0) #0 to start with
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(Department.objects.all().count(),0) #
        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        new_dept_name = 'new name'
        new_dept_code = 'NN'
        #add  one
        self.client.post(reverse('workload_app:manage_department'),{'department_name':new_dept_name, 'department_acronym' : new_dept_code,\
                        'faculty' : new_fac.id, 'fresh_record' :  True})
        self.assertEqual(Department.objects.all().count(),1) #1 created 
        self.assertEqual(Department.objects.filter(department_name = new_dept_name).count(), 1)
        self.assertEqual(Department.objects.filter(department_acronym = new_dept_code).count(), 1)


        new_dept_object = Department.objects.filter(department_name = new_dept_name)
        #Remove department
        self.client.post(reverse('workload_app:remove_department'),{'select_department_to_remove':new_dept_object.get().id})
        self.assertEqual(Department.objects.all().count(),0) #
        self.assertEqual(Department.objects.filter(department_name = new_dept_name).count(), 0)
        self.assertEqual(Department.objects.filter(department_acronym = new_dept_code).count(), 0)

    def test_add_same_name(self):

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(Department.objects.all().count(),0) #0 to start with
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(Department.objects.all().count(),0) #

        new_dept_name = 'new name'
        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        new_dept = Department.objects.create(department_name=new_dept_name, department_acronym="TTDD", faculty=new_fac)

        new_dept_code = 'NN'
        #add another one, same name. It should fail to add
        self.client.post(reverse('workload_app:manage_department'),{'department_name':new_dept_name, 'department_acronym' : new_dept_code,\
                        'faculty' : new_fac.id, 'fresh_record' :  True})
        self.assertEqual(Department.objects.all().count(),1) #1, add should fail
        self.assertEqual(Department.objects.filter(department_name = new_dept_name).count(), 1)
        self.assertEqual(Department.objects.filter(department_acronym = new_dept_code).count(), 0)


    def test_add_remove_with_workloads(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(Department.objects.all().count(),0) #0 to start with
        self.assertEqual(Department.objects.all().count(),0) #
        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        acad_year = Academicyear.objects.create(start_year=2025)
        #Add a new dept
        new_dept_name = 'new name'
        new_dept_code = 'NN'
        self.client.post(reverse('workload_app:manage_department'),{'department_name':new_dept_name, 'department_acronym' : new_dept_code,\
                        'faculty' : new_fac.id, 'fresh_record' :  True})
        self.assertEqual(Department.objects.all().count(),1) 

        new_dept_object = Department.objects.filter(department_name = new_dept_name)
        #Add a new workload associated with the new department
        self.client.post(reverse('workload_app:manage_scenario'), {'label': 'test_scen', 'dept' : new_dept_object.get().id, 'status': WorkloadScenario.DRAFT, 'copy_from':'','fresh_record' : True, 'academic_year' : acad_year.id});
        
        self.assertEqual(WorkloadScenario.objects.all().count(), 1)
        self.assertEqual(WorkloadScenario.objects.filter(dept__department_name=new_dept_name).count(), 1)

        #Now remove the new department. Expected behaviour: the workload will disappear
        self.client.post(reverse('workload_app:remove_department'),{'select_department_to_remove':new_dept_object.get().id})        
        self.assertEqual(WorkloadScenario.objects.all().count(), 0)
        self.assertEqual(WorkloadScenario.objects.filter(dept__department_name=new_dept_name).count(), 0)
        self.assertEqual(Department.objects.all().count(),0)

    def test_edit_department(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(Department.objects.all().count(),0) #0 to start with
        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        acad_year = Academicyear.objects.create(start_year=2025)
        #Add a new dept
        dept_name = 'my_dept'
        dept_code = 'NN'
        self.client.post(reverse('workload_app:manage_department'),{'department_name':dept_name, 'department_acronym' : dept_code,\
                        'faculty' : new_fac.id, 'fresh_record' :  True})
        self.assertEqual(Department.objects.all().count(),1) 
        self.assertEqual(Department.objects.filter(department_name = dept_name).count(), 1)
        self.assertEqual(Department.objects.filter(department_acronym = dept_code).count(), 1)

        #Now edit the name of the new dept
        dept_id = Department.objects.filter(department_name = dept_name).get().id
        new_name = "new name"
        self.client.post(reverse('workload_app:manage_department'),{'department_name':new_name, 'department_acronym' : dept_code,\
                        'faculty' : new_fac.id, 'fresh_record' :  False,
                        'dept_id' : dept_id})
        self.assertEqual(Department.objects.all().count(),1) #still 1
        self.assertEqual(Department.objects.filter(department_name = dept_name).count(), 0) #should be gone
        self.assertEqual(Department.objects.filter(department_name = new_name).count(), 1) #should be there, it is the new name
        self.assertEqual(Department.objects.filter(department_acronym = dept_code).count(), 1) #no change
        
        new_acronym = "NCRW"
        #Now edit the acronym
        self.client.post(reverse('workload_app:manage_department'),{'department_name':new_name, 'department_acronym' : new_acronym,\
                        'faculty' : new_fac.id, 'fresh_record' :  False,
                        'dept_id' : dept_id})
        self.assertEqual(Department.objects.all().count(),1) #still 1
        self.assertEqual(Department.objects.filter(department_name = dept_name).count(), 0) #should be gone
        self.assertEqual(Department.objects.filter(department_name = new_name).count(), 1) #should be there, it is the new name
        self.assertEqual(Department.objects.filter(department_acronym = dept_code).count(), 0) #should be gone
        self.assertEqual(Department.objects.filter(department_acronym = new_acronym).count(), 1) #should be there, the new one

        #Create a new faculty
        new_fac_name = 'new name'
        new_fac_code = 'NN'
        #add another one
        self.client.post(reverse('workload_app:manage_faculty'),{'faculty_name':new_fac_name, 'faculty_acronym' : new_fac_code, 'fresh_record' :  True})

        #Edit the department to belong to this new faculty
        self.client.post(reverse('workload_app:manage_department'),{'department_name':new_name, 'department_acronym' : new_acronym,\
                        'faculty' : Faculty.objects.filter(faculty_name = new_fac_name).get().id, 'fresh_record' :  False,
                        'dept_id' : dept_id})
        
        self.assertEqual(Department.objects.all().count(),1) #still 2
        self.assertEqual(Department.objects.filter(department_name = dept_name).count(), 0) #should be gone
        self.assertEqual(Department.objects.filter(department_name = new_name).count(), 1) #should be there, it is the new name
        self.assertEqual(Department.objects.filter(department_acronym = dept_code).count(), 0) #should be gone
        self.assertEqual(Department.objects.filter(department_acronym = new_acronym).count(), 1) #should be there, the new one
        self.assertEqual(Department.objects.filter(faculty = Faculty.objects.filter(faculty_name = new_fac_name).get().id).count(), 1) #new one

    def test_edit_department_into_same_name(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(Department.objects.all().count(),0) #0 to start with
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(Department.objects.all().count(),0) #

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        #Create two separate departments
        dept_name_1= 'dept_1'
        dept_code_1 = 'NN1'
        self.client.post(reverse('workload_app:manage_department'),{'department_name':dept_name_1, 'department_acronym' : dept_code_1,\
                    'faculty' : new_fac.id, 'fresh_record' :  True})

        dept_name_2= 'dept_2'
        dept_code_2 = 'NN2'
        self.client.post(reverse('workload_app:manage_department'),{'department_name':dept_name_2, 'department_acronym' : dept_code_2,\
                    'faculty' : new_fac.id, 'fresh_record' :  True})
        
        self.assertEqual(Department.objects.all().count(),2) #2
        self.assertEqual(Department.objects.filter(department_name = dept_name_1).count(), 1) #
        self.assertEqual(Department.objects.filter(department_name = dept_name_2).count(), 1) #
        
        #Now try to edit dept 1 to have the same name as dept 2
        dept_id = Department.objects.filter(department_name = dept_name_1).get().id
        self.client.post(reverse('workload_app:manage_department'),{'department_name':dept_name_2, 'department_acronym' : dept_code_1,\
                    'faculty' : new_fac.id, 'fresh_record' :  False,
                    'dept_id' : dept_id})
        
        #Edit should have failed
        self.assertEqual(Department.objects.all().count(),2) #2
        self.assertEqual(Department.objects.filter(department_name = dept_name_1).count(), 1) #
        self.assertEqual(Department.objects.filter(department_name = dept_name_2).count(), 1) #


    def testDepartmentSummaryViewAndAddNewScenario(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        
        this_year = datetime.datetime.now().year
        #Create a Dept affiliated to a faculty
        dept_name = 'test_dept'
        first_fac = Faculty.objects.create(faculty_name = "first fac", faculty_acronym = "FRTE")
        test_dept = Department.objects.create(department_name = dept_name, department_acronym = "ACR", faculty = first_fac)
        self.assertEqual(Department.objects.all().count(), 1)
        #Create two programmes
        ug_prog_name ='UG'
        ug_prog = ProgrammeOffered.objects.create(programme_name = ug_prog_name, primary_dept = test_dept)
        self.assertEqual(ProgrammeOffered.objects.all().count(), 1)
        pg_prog_name ='PG'
        pg_prog = ProgrammeOffered.objects.create(programme_name = pg_prog_name, primary_dept = test_dept)
        self.assertEqual(ProgrammeOffered.objects.all().count(), 2)

        #Create an academic year
        test_acad_year = Academicyear.objects.create(start_year = this_year)
        #Create a Workload scenario
        test_scenario_name = "test_scen"
        wl_scen = WorkloadScenario.objects.create(label = test_scenario_name, dept = test_dept, academic_year = test_acad_year,\
                                                   status = WorkloadScenario.OFFICIAL)
        #Create some lecturers
        def_track = EmploymentTrack.objects.create(track_name = "track_def", track_adjustment = 1.0, is_adjunct = False, faculty=first_fac)
        track_1 = EmploymentTrack.objects.create(track_name = "track_1", track_adjustment = 2.0, is_adjunct = False, faculty=first_fac)
        test_svc_role = ServiceRole.objects.create(role_name = "test", role_adjustment = 2.0, faculty=first_fac)
        normal_lecturer = Lecturer.objects.create(name="normal_lecturer", fraction_appointment = 0.7, employment_track = def_track, service_role = test_svc_role, workload_scenario = wl_scen)
        educator_track = Lecturer.objects.create(name="educator_track", fraction_appointment = 1.0, service_role = test_svc_role, employment_track=track_1,workload_scenario = wl_scen)
        vice_dean = Lecturer.objects.create(name="vice_dean", fraction_appointment = 0.5, employment_track = def_track, service_role = test_svc_role, workload_scenario = wl_scen)
        #and some modules with two types
        core_mod = ModuleType.objects.create(type_name = "core", department=test_dept)
        elective_mod = ModuleType.objects.create(type_name = "elective", department=test_dept)
        mod_1_ug_sem_1 = Module.objects.create(module_code = "M1-UG-SEM1", module_title = "module 1 ug sem 1", scenario_ref = wl_scen,\
                                               total_hours = 200, module_type = core_mod, semester_offered= Module.SEM_1, \
                                               primary_programme=ug_prog)
        mod_2_ug_sem_1 = Module.objects.create(module_code = "M2-UG-SEM1", module_title = "module 2 ug sem 1", scenario_ref = wl_scen,\
                                               total_hours = 150, module_type = core_mod, semester_offered= Module.SEM_1, \
                                               primary_programme=ug_prog)
        mod_3_ug_sem_2 = Module.objects.create(module_code = "M3-UG-SEM2", module_title = "module 3 ug sem 2", scenario_ref = wl_scen,\
                                               total_hours = 150, module_type = core_mod, semester_offered= Module.SEM_2, \
                                               primary_programme=ug_prog)
        mod_4_pg_sem_1 = Module.objects.create(module_code = "M4-PG-SEM1", module_title = "module 4 pg sem 1", scenario_ref = wl_scen,\
                                               total_hours = 150, module_type = core_mod, semester_offered= Module.SEM_1, \
                                               primary_programme=pg_prog)
        mod_5_pg_sem_2 = Module.objects.create(module_code = "M5-PG-SEM2", module_title = "module 5 pg sem 2", scenario_ref = wl_scen,\
                                               total_hours = 150, module_type = elective_mod, semester_offered= Module.SEM_2, \
                                               primary_programme=pg_prog)
        #Assign modules to lecturers
        TeachingAssignment.objects.create(assigned_module = mod_1_ug_sem_1, assigned_lecturer = normal_lecturer, number_of_hours = 25, workload_scenario=wl_scen)
        TeachingAssignment.objects.create(assigned_module = mod_2_ug_sem_1, assigned_lecturer = normal_lecturer, number_of_hours = 55, workload_scenario=wl_scen)
        TeachingAssignment.objects.create(assigned_module = mod_3_ug_sem_2, assigned_lecturer = normal_lecturer, number_of_hours = 25, workload_scenario=wl_scen)
        TeachingAssignment.objects.create(assigned_module = mod_4_pg_sem_1, assigned_lecturer = normal_lecturer, number_of_hours = 25, workload_scenario=wl_scen)
        TeachingAssignment.objects.create(assigned_module = mod_5_pg_sem_2, assigned_lecturer = normal_lecturer, number_of_hours = 95, workload_scenario=wl_scen)
        TeachingAssignment.objects.create(assigned_module = mod_1_ug_sem_1, assigned_lecturer = educator_track, number_of_hours = 25, workload_scenario=wl_scen)
        TeachingAssignment.objects.create(assigned_module = mod_1_ug_sem_1, assigned_lecturer = vice_dean, number_of_hours = 125, workload_scenario=wl_scen)
        
        response = self.client.get(reverse('workload_app:department', kwargs={'department_id': test_dept.id}))
        
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["workload_there"], False)#no academic year in the session. should not find any workload
        self.assertEqual(response.context["no_show_message"], "")#First landing, no error message

        response = self.client.post(reverse('workload_app:department', kwargs={'department_id': test_dept.id}), {"select_academic_year" : test_acad_year.id})
        self.assertEqual(response.status_code, 302) #Re-direct
        #Now the Get
        response = self.client.get(reverse('workload_app:department', kwargs={'department_id': test_dept.id}))
        #Programmes offered
        self.assertEqual(response.context["workload_there"], True)
        self.assertEqual(len(response.context["prog_offered"]), 2)
        self.assertEqual(response.context["prog_offered"][0]["programme_id"], ug_prog.id)
        self.assertEqual(response.context["prog_offered"][1]["programme_id"], pg_prog.id)
        self.assertEqual(len(response.context["tables_for_year"]), 2)#Note: content of the table is tested under helper methods
        self.assertEqual(response.context["no_show_message"], "")
        #Department workloads
        self.assertEqual(len(response.context["dept_wls"]), 11)
        first_year = this_year - 6
        self.assertEqual(response.context["dept_wls"][0]["academic_year"], str(first_year)+'/'+str(first_year+1))
        self.assertEqual(response.context["dept_wls"][6]["academic_year"], str(this_year)+'/'+str(this_year+1))
        self.assertEqual(len(response.context["dept_wls"][6]["official_wl_ids"]),1)#One official wl in this year
        self.assertEqual(len(response.context["dept_wls"][6]["draft_wl_ids"]),0)#no unofficial ones
        self.assertEqual(response.context["dept_wls"][6]["official_wl_ids"][0],wl_scen.id)#

        #No wl the year after
        self.assertEqual(len(response.context["dept_wls"][7]["official_wl_ids"]),0)#No official wls
        self.assertEqual(len(response.context["dept_wls"][7]["draft_wl_ids"]),0)#no unofficial ones
        
        #check one is there first
        self.assertEqual(WorkloadScenario.objects.all().count(),1)
        self.assertEqual(Lecturer.objects.all().count(),3)
        self.assertEqual(Module.objects.all().count(),5)
        #Now try adding a new scenario from the department page
        new_label = 'new_scenario'
        self.client.post(reverse('workload_app:department', kwargs={'department_id': test_dept.id}),{\
                        'label':new_label, \
                        'dept' : test_dept.id,\
                        'academic_year' : test_acad_year.id,\
                        'status' : WorkloadScenario.OFFICIAL,\
                        'copy_from' : wl_scen.id,
                        'fresh_record' :  True})
        self.assertEqual(WorkloadScenario.objects.all().count(),2)
        self.assertEqual(Lecturer.objects.all().count(),6)
        self.assertEqual(Module.objects.all().count(),10)

        #Remove the scenario we just created
        new_scen = WorkloadScenario.objects.filter(label = new_label).get()
        self.client.post(reverse('workload_app:department', kwargs={'department_id': test_dept.id}), {'select_scenario_to_remove': new_scen.id})
        #Back to previous situation
        self.assertEqual(WorkloadScenario.objects.all().count(),1)
        self.assertEqual(Lecturer.objects.all().count(),3)
        self.assertEqual(Module.objects.all().count(),5)


        