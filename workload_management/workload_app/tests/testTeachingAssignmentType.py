from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *

from workload_app.models import Lecturer, TeachingAssignment, TeachingAssignmentType, WorkloadScenario, Department, EmploymentTrack, ServiceRole, UniversityStaff, Faculty,Academicyear


class TestTeachingAssignmentType(TestCase):
    def setup_user(self):
        #The test client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
        self.user.is_superuser = True
        self.user.save()
        uni_user = UniversityStaff.objects.create(user = self.user, department=None,faculty=None)
        
    def test_add_remove_edit_type(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
        self.assertEqual(TeachingAssignmentType.objects.all().count(),0)
        #Test the POST now
        new_type_name = 'test_type'
        num_hrs = 12
        self.client.post(reverse('workload_app:school_page' ,  kwargs={'faculty_id': new_fac.id}),\
                         {'description':new_type_name,'quantum_number_of_hours' : str(num_hrs), 'fresh_record': True})
        
        self.assertEqual(TeachingAssignmentType.objects.all().count(),1) #One created
        self.assertEqual(TeachingAssignmentType.objects.filter(description = new_type_name).count(),1)
        self.assertEqual(TeachingAssignmentType.objects.filter(quantum_number_of_hours = num_hrs).count(),1)
        self.assertEqual(TeachingAssignmentType.objects.filter(workload_valid_from__isnull = True).count(),1)
        self.assertEqual(TeachingAssignmentType.objects.filter(workload_valid_until__isnull = True).count(),1)
        self.assertEqual(TeachingAssignmentType.objects.filter(faculty__isnull = True).count(),0) #the view will always assign its faculty
        ass_type_obj = TeachingAssignmentType.objects.filter(description = new_type_name).get()
        #Test the helper method inside the model class
        self.assertEqual(ass_type_obj.DisplayAssignmentTypeValidity(),"Applies to all workloads")
        #Now try an edit
        modified_type_name = 'modified'
        num_hrs_2 = 369
        acad_year_1 = Academicyear.objects.create(start_year=2018)
        acad_year_2 = Academicyear.objects.create(start_year=2022)
        self.client.post(reverse('workload_app:school_page' ,  kwargs={'faculty_id': new_fac.id}),\
                         {'description':modified_type_name,'quantum_number_of_hours' : str(num_hrs_2),\
                          'teaching_ass_id':ass_type_obj.id, 'workload_valid_from': acad_year_1.id, 'workload_valid_until':acad_year_2.id, 'fresh_record': False})
        
        self.assertEqual(TeachingAssignmentType.objects.all().count(),1) #One created
        self.assertEqual(TeachingAssignmentType.objects.filter(description = new_type_name).count(),0)#no more
        self.assertEqual(TeachingAssignmentType.objects.filter(description = modified_type_name).count(),1)
        self.assertEqual(TeachingAssignmentType.objects.filter(quantum_number_of_hours = num_hrs).count(),0)#no more
        self.assertEqual(TeachingAssignmentType.objects.filter(quantum_number_of_hours = num_hrs_2).count(),1)
        self.assertEqual(TeachingAssignmentType.objects.filter(workload_valid_from__isnull = True).count(),0)
        self.assertEqual(TeachingAssignmentType.objects.filter(workload_valid_until__isnull = True).count(),0)
        self.assertEqual(TeachingAssignmentType.objects.filter(workload_valid_from__start_year = 2018).count(),1)
        self.assertEqual(TeachingAssignmentType.objects.filter(workload_valid_until__start_year = 2022).count(),1)
        self.assertEqual(TeachingAssignmentType.objects.filter(faculty__isnull = True).count(),0) #the view will always assign its faculty
        
        ass_type_obj = TeachingAssignmentType.objects.filter(description = modified_type_name).get()
        self.assertEqual(ass_type_obj.DisplayAssignmentTypeValidity(),"Applies to workloads from 2018-2019 until 2022-2023")

        #Try adding another one with the same name - PREVENT DUPLICATE NAMES
        self.client.post(reverse('workload_app:school_page' ,  kwargs={'faculty_id': new_fac.id}),\
                         {'description':modified_type_name,'quantum_number_of_hours' : str(num_hrs), 'fresh_record': True})
        #This should have failed and situation is uncganged
        self.assertEqual(TeachingAssignmentType.objects.all().count(),1) #One created
        self.assertEqual(TeachingAssignmentType.objects.filter(description = new_type_name).count(),0)#no more
        self.assertEqual(TeachingAssignmentType.objects.filter(description = modified_type_name).count(),1)

        ass_type_obj = TeachingAssignmentType.objects.filter(description = modified_type_name).get()
        #Remove the assignment type we just added
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'select_assignment_type_to_remove':ass_type_obj.id})
        self.assertEqual(TeachingAssignmentType.objects.all().count(),0) #None left
    
    def test_assignment_trype_helper_method(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        assign_always_valid = TeachingAssignmentType.objects.create(description="always valid", quantum_number_of_hours=1,faculty=new_fac)
        self.assertEqual(assign_always_valid.IsValidForYear(1900), True)
        self.assertEqual(assign_always_valid.IsValidForYear(2008), True)
        self.assertEqual(assign_always_valid.IsValidForYear(2010), True)
        self.assertEqual(assign_always_valid.IsValidForYear(2020), True)

        acad_year_0 = Academicyear.objects.create(start_year=2019)
        assign_valid_until_2019 = TeachingAssignmentType.objects.create(description="always valid", quantum_number_of_hours=1,workload_valid_until=acad_year_0,faculty=new_fac)
        self.assertEqual(assign_valid_until_2019.IsValidForYear(1900), True)
        self.assertEqual(assign_valid_until_2019.IsValidForYear(2008), True)
        self.assertEqual(assign_valid_until_2019.IsValidForYear(2010), True)
        self.assertEqual(assign_valid_until_2019.IsValidForYear(2019), True)#equality is OK
        self.assertEqual(assign_valid_until_2019.IsValidForYear(2020), False)
        
        acad_year_1 = Academicyear.objects.create(start_year=2010)
        assign_valid_starting_2010 = TeachingAssignmentType.objects.create(description="always valid", quantum_number_of_hours=1,workload_valid_from=acad_year_1,faculty=new_fac)
        self.assertEqual(assign_valid_starting_2010.IsValidForYear(1900), False)
        self.assertEqual(assign_valid_starting_2010.IsValidForYear(2008), False)
        self.assertEqual(assign_valid_starting_2010.IsValidForYear(2010), True)#equality is OK
        self.assertEqual(assign_valid_starting_2010.IsValidForYear(2019), True)
        self.assertEqual(assign_valid_starting_2010.IsValidForYear(2020), True)

        assign_from2010_to_2019 = TeachingAssignmentType.objects.create(description="always valid", quantum_number_of_hours=1,workload_valid_from=acad_year_1,workload_valid_until=acad_year_0, faculty=new_fac)
        self.assertEqual(assign_from2010_to_2019.IsValidForYear(1900), False)
        self.assertEqual(assign_from2010_to_2019.IsValidForYear(2009), False)
        self.assertEqual(assign_from2010_to_2019.IsValidForYear(2010), True)#equality is OK
        self.assertEqual(assign_from2010_to_2019.IsValidForYear(2019), True)#equality is OK
        self.assertEqual(assign_from2010_to_2019.IsValidForYear(2020), False)

    def test_assignment_type_in_workload(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        first_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        def_role = ServiceRole.objects.create(role_name="test role", role_adjustment=1, faculty=new_fac)
        new_track = EmploymentTrack.objects.create(track_name = "track default", track_adjustment = 0.8, faculty=new_fac)

        #Here we create two workload scenarios of different academic years
        year_1 = 2020
        year_2 = 2025
        acad_year_1 = Academicyear.objects.create(start_year=year_1)
        acad_year_2 = Academicyear.objects.create(start_year=year_2) 
        #create two scenarios for different academic years
        scen_name_1 = 'scen_1'
        scenario_1 = WorkloadScenario.objects.create(label=scen_name_1, academic_year=acad_year_1, dept=first_dept)
        scen_name_2 = 'scen_2'
        scenario_2 = WorkloadScenario.objects.create(label=scen_name_2, academic_year=acad_year_2, dept=first_dept)

        #Now create on teaching assignment type
        always_valid_description = "always valid"
        assign_always_valid = TeachingAssignmentType.objects.create(description=always_valid_description, quantum_number_of_hours=1,faculty=new_fac)
        self.assertEqual(TeachingAssignmentType.objects.all().count(),1) #One created
        #Since it is always valid, it should appear in both scenarios. Note that it appears in the forms (in the modals) for adding new assignments, at least
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertContains(response,always_valid_description)#Note the Django's assertContains will decode and examine the response object for us

        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertContains(response,always_valid_description)#Note the Django's assertContains will decode and examine the response object for us

        #Now create another one with validity completely out of the range (stops in 2019)
        year_0 = 2019
        acad_year_0 = Academicyear.objects.create(start_year=year_0)
        until_2019_description = "until_2019"
        until_2019_assignment = TeachingAssignmentType.objects.create(description=until_2019_description, quantum_number_of_hours=1,workload_valid_until=acad_year_0, faculty=new_fac)
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(TeachingAssignmentType.objects.all().count(),2) #Now 2
        self.assertContains(response,always_valid_description)#
        self.assertNotContains(response,until_2019_description)#

        #Now create another one in the middle of the range
        year_1 = 2023
        acad_year_1 = Academicyear.objects.create(start_year=year_1)
        until_2023_description = "until_2023"
        until_2023_assignment = TeachingAssignmentType.objects.create(description=until_2023_description, quantum_number_of_hours=12,workload_valid_until=acad_year_1, faculty=new_fac)
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(TeachingAssignmentType.objects.all().count(),3) #Now 3
        self.assertContains(response,until_2023_description)#

        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertNotContains(response,until_2023_description)#Not in the 2025 one

        #Now create another one in the far future
        year_2 = 2030
        acad_year_2 = Academicyear.objects.create(start_year=year_2)
        from_2026_description = "from_2026"
        from_2026_assignment = TeachingAssignmentType.objects.create(description=from_2026_description, quantum_number_of_hours=122,workload_valid_from=acad_year_2, faculty=new_fac)
        
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_1.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(TeachingAssignmentType.objects.all().count(),4) #Now 4
        self.assertNotContains(response,from_2026_description)#

        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': scenario_2.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertNotContains(response,from_2026_description)#Not in the 2025 one