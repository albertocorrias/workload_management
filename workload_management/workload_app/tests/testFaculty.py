from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *
from workload_app.models import Department, Faculty, UniversityStaff

class TestFaculty(TestCase):
    def setup_user(self):
        #The test client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
        self.user.is_superuser = True
        self.user.save()
        uni_user = UniversityStaff.objects.create(user = self.user, department=None,faculty=None)
    def test_add_remove_faculty(self):

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(Faculty.objects.all().count(),0) #0 to start with
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(Faculty.objects.all().count(),0) #

        new_fac_name = 'new name'
        new_fac_code = 'NN'
        #add another one
        self.client.post(reverse('workload_app:manage_faculty'),{'faculty_name':new_fac_name, 'faculty_acronym' : new_fac_code, 'fresh_record' : True})
        self.assertEqual(Faculty.objects.all().count(),1) #
        self.assertEqual(Faculty.objects.filter(faculty_name = new_fac_name).count(), 1)
        self.assertEqual(Faculty.objects.filter(faculty_acronym = new_fac_code).count(), 1)


        new_fac_object = Faculty.objects.filter(faculty_name = new_fac_name)
        #Remove faculty
        self.client.post(reverse('workload_app:remove_faculty'),{'select_faculty_to_remove':new_fac_object.get().id})
        self.assertEqual(Faculty.objects.all().count(),0) #removed
        self.assertEqual(Faculty.objects.filter(faculty_name = new_fac_name).count(), 0)
        self.assertEqual(Faculty.objects.filter(faculty_acronym = new_fac_code).count(), 0)


    def test_add_remove_with_departments(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(Faculty.objects.all().count(),0) #0 to start with
        self.assertEqual(Department.objects.all().count(), 0)

        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(Faculty.objects.all().count(),0) #1 created by default when there is none
        self.assertEqual(Department.objects.all().count(), 0) #1 created by default
        new_fac_name = 'new name'
        new_fac_code = 'NN'
        #add another one
        self.client.post(reverse('workload_app:manage_faculty'),{'faculty_name':new_fac_name, 'faculty_acronym' : new_fac_code, 'fresh_record' : True})
        self.assertEqual(Faculty.objects.all().count(),1) 
        self.assertEqual(Faculty.objects.filter(faculty_name = new_fac_name).count(), 1)

        new_fac_object = Faculty.objects.filter(faculty_name = new_fac_name)
        #Add a new department in the new faculty
        self.client.post(reverse('workload_app:manage_department'), {'department_name': 'test_dept', 'department_acronym' : 'TD3', \
                                                                    'faculty' : new_fac_object.get().id, 'fresh_record' :  True});
        
        self.assertEqual(Department.objects.all().count(), 1)
        self.assertEqual(Department.objects.filter(faculty__faculty_name=new_fac_name).count(), 1)


        # #Now remove the new faculty. Expected behaviour: the department will point to NULL faculty
        self.client.post(reverse('workload_app:remove_faculty'),{'select_faculty_to_remove':new_fac_object.get().id})        
        self.assertEqual(Faculty.objects.all().count(), 0)
        self.assertEqual(Faculty.objects.filter(faculty_name=new_fac_name).count(), 0)
        self.assertEqual(Department.objects.all().count(),1)
        #self.assertEqual(Department.objects.filter(faculty__faculty_name=new_fac_name).count(), 0)#NO more in the removed faculty

    
    def test_edit_existing_faculty(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(Faculty.objects.all().count(),0) #
        self.assertEqual(Department.objects.all().count(), 0) #
        fac_name_1 = 'new name'
        fac_code_1 = 'NN'
        #add  one
        self.client.post(reverse('workload_app:manage_faculty'),{'faculty_name':fac_name_1, 'faculty_acronym' : fac_code_1, 'fresh_record' : True})
        self.assertEqual(Faculty.objects.all().count(),1) 
        self.assertEqual(Faculty.objects.filter(faculty_name = fac_name_1).count(), 1)
        self.assertEqual(Faculty.objects.filter(faculty_acronym = fac_code_1).count(), 1)

        #Edit the name
        new_name = "anotherone"
        fac_id = Faculty.objects.filter(faculty_name = fac_name_1).get().id
        self.client.post(reverse('workload_app:manage_faculty'),{'faculty_name':new_name, 'faculty_acronym' : fac_code_1, \
                                                              'fresh_record' : False,
                                                              "fac_id" : fac_id})
        self.assertEqual(Faculty.objects.all().count(),1) 
        self.assertEqual(Faculty.objects.filter(faculty_name = fac_name_1).count(), 0)#Old name is gone
        self.assertEqual(Faculty.objects.filter(faculty_name = new_name).count(), 1)#New one is there
        self.assertEqual(Faculty.objects.filter(faculty_acronym = fac_code_1).count(), 1)
        
        #Edit the acronym
        new_acronym = "TT"
        self.client.post(reverse('workload_app:manage_faculty'),{'faculty_name':new_name, 'faculty_acronym' : new_acronym, \
                                                              'fresh_record' : False,
                                                              "fac_id" : fac_id})
        self.assertEqual(Faculty.objects.all().count(),1) 
        self.assertEqual(Faculty.objects.filter(faculty_name = fac_name_1).count(), 0)#Old name is gone
        self.assertEqual(Faculty.objects.filter(faculty_name = new_name).count(), 1)#New one is there
        self.assertEqual(Faculty.objects.filter(faculty_acronym = fac_code_1).count(), 0)#Old acronym gone
        self.assertEqual(Faculty.objects.filter(faculty_acronym = new_acronym).count(), 1)#New acronym there

    def test_faculty_same_name(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        fac_name_1 = 'new name'
        fac_code_1 = 'NN'
        #add one
        self.client.post(reverse('workload_app:manage_faculty'),{'faculty_name':fac_name_1, 'faculty_acronym' : fac_code_1, 'fresh_record' : True})
        self.assertEqual(Faculty.objects.all().count(),1) 
        self.assertEqual(Faculty.objects.filter(faculty_name = fac_name_1).count(), 1)
        self.assertEqual(Faculty.objects.filter(faculty_acronym = fac_code_1).count(), 1)

        #Try adding another one with the same name
        self.client.post(reverse('workload_app:manage_faculty'),{'faculty_name':fac_name_1, 'faculty_acronym' : fac_code_1, 'fresh_record' : True})
        #Check everything unchanged, addition should have failed
        self.assertEqual(Faculty.objects.all().count(),1) 
        self.assertEqual(Faculty.objects.filter(faculty_name = fac_name_1).count(), 1)
        self.assertEqual(Faculty.objects.filter(faculty_acronym = fac_code_1).count(), 1)
    
    def test_edit_faculty_into_same_name(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        fac_name_1 = 'new name'
        fac_code_1 = 'NN'
        #add another one
        self.client.post(reverse('workload_app:manage_faculty'),{'faculty_name':fac_name_1, 'faculty_acronym' : fac_code_1, 'fresh_record' : True})
        self.assertEqual(Faculty.objects.all().count(),1) 
        self.assertEqual(Faculty.objects.filter(faculty_name = fac_name_1).count(), 1)
        self.assertEqual(Faculty.objects.filter(faculty_acronym = fac_code_1).count(), 1)

        #Try adding another one with the another name
        fac_name_2 = 'anotherone'
        fac_code_2 = 'RR'
        self.client.post(reverse('workload_app:manage_faculty'),{'faculty_name':fac_name_2, 'faculty_acronym' : fac_code_2, 'fresh_record' : True})
        #Check we added
        self.assertEqual(Faculty.objects.all().count(),2) 
        self.assertEqual(Faculty.objects.filter(faculty_name = fac_name_2).count(), 1)
        self.assertEqual(Faculty.objects.filter(faculty_acronym = fac_code_2).count(), 1)
        self.assertEqual(Faculty.objects.filter(faculty_name = fac_name_1).count(), 1)
        self.assertEqual(Faculty.objects.filter(faculty_acronym = fac_code_1).count(), 1)

        #Try editing fac_name_2 into the first name
        fac_id = Faculty.objects.filter(faculty_name = fac_name_2).get().id #beinge dited
        self.client.post(reverse('workload_app:manage_faculty'),{'faculty_name':fac_name_1, 'faculty_acronym' : fac_code_2, \
                                                              'fresh_record' : False,
                                                              "fac_id" : fac_id})

        #This edit should have failed and everything should have stayed the same
        self.assertEqual(Faculty.objects.all().count(),2) 
        self.assertEqual(Faculty.objects.filter(faculty_name = fac_name_2).count(), 1)
        self.assertEqual(Faculty.objects.filter(faculty_acronym = fac_code_2).count(), 1)
        self.assertEqual(Faculty.objects.filter(faculty_name = fac_name_1).count(), 1)
        self.assertEqual(Faculty.objects.filter(faculty_acronym = fac_code_1).count(), 1)