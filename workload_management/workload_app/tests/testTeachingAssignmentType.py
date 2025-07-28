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
    


   