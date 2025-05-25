from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *
from workload_app.global_constants import DEFAULT_SERVICE_ROLE_NAME,DEFAULT_TRACK_NAME
from workload_app.models import Lecturer, ServiceRole,WorkloadScenario, EmploymentTrack, UniversityStaff,Faculty


class TestServiceRole(TestCase):
    def setup_user(self):
        #The test client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
        self.user.is_superuser = True
        self.user.save()
        uni_user = UniversityStaff.objects.create(user = self.user, department=None,faculty=None)
    def test_add_remove_role(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(ServiceRole.objects.all().count(),0)
        #Test the GET
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        self.assertEqual(ServiceRole.objects.all().count(),1) #Test the default creation of default service role
        self.assertEqual(ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME).count(),1)
        new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
        #Test the POST now
        new_role_name = 'test_role'
        role_adj = 0.5
        self.client.post(reverse('workload_app:school_page' ,  kwargs={'faculty_id': new_fac.id}),{'role_name':new_role_name,'role_adjustment' : str(role_adj), 'fresh_record': True})
        
        self.assertEqual(ServiceRole.objects.all().count(),2) #The default plus the new one
        self.assertEqual(ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_name = new_role_name).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_adjustment = role_adj).count(),1)

        #Remove the role we just added
        new_role = ServiceRole.objects.filter(role_name = new_role_name)
        self.client.post(reverse('workload_app:school_page', kwargs={'faculty_id': new_fac.id}),{'select_service_role_to_remove':new_role.get().id})
        self.assertEqual(ServiceRole.objects.all().count(),1) #Only the default one should be there
        self.assertEqual(ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_name = new_role_name).count(),0)
        self.assertEqual(ServiceRole.objects.filter(role_adjustment = role_adj).count(),0)

        #Try deleting the default role (should not be possible)
        def_role = ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME)
        self.client.post(reverse('workload_app:school_page', kwargs={'faculty_id': new_fac.id}),{'select_service_role_to_remove':def_role.get().id})
        self.assertEqual(ServiceRole.objects.all().count(),1) #default track should still be there
        self.assertEqual(ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME).count(),1) #default role should still be there

    def test_edit_existing_role(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(ServiceRole.objects.all().count(),0)
        #Test the GET
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
        self.assertEqual(ServiceRole.objects.all().count(),1) #Test the default creation of default service role
        self.assertEqual(ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME).count(),1)

        #Test the POST now
        new_role_name = 'test_role'
        role_adj = 0.5
        self.client.post(reverse('workload_app:school_page', kwargs={'faculty_id': new_fac.id}),{'role_name':new_role_name,'role_adjustment' : str(role_adj), 'fresh_record': True})
        
        self.assertEqual(ServiceRole.objects.all().count(),2) #The default plus the new one
        self.assertEqual(ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_name = new_role_name).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_adjustment = role_adj).count(),1)

        #Edit the existing one, change role adjustment
        new_role_id = ServiceRole.objects.filter(role_name = new_role_name).get().id
        new_role_adj = 0.8
        self.client.post(reverse('workload_app:school_page', kwargs={'faculty_id': new_fac.id}),{'role_name':new_role_name,'role_adjustment' : str(new_role_adj),\
                                                                   'fresh_record': False, 'role_id' : new_role_id})
        self.assertEqual(ServiceRole.objects.all().count(),2) #The default plus the new one
        self.assertEqual(ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_name = new_role_name).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_adjustment = role_adj).count(),0)#old one is gone
        self.assertEqual(ServiceRole.objects.filter(role_adjustment = new_role_adj).count(),1)#edited value is recorded
    
    def test_same_role_name(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(ServiceRole.objects.all().count(),0)
        #Test the GET
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        
        new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
        self.assertEqual(ServiceRole.objects.all().count(),1) #Test the default creation of default service role
        self.assertEqual(ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME).count(),1)

        #Test the POST now
        new_role_name = 'test_role'
        role_adj = 0.5
        self.client.post(reverse('workload_app:school_page', kwargs={'faculty_id': new_fac.id}),{'role_name':new_role_name,'role_adjustment' : str(role_adj), 'fresh_record': True})
        
        self.assertEqual(ServiceRole.objects.all().count(),2) #The default plus the new one
        self.assertEqual(ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_name = new_role_name).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_adjustment = role_adj).count(),1)

        #Try adding another one with the same name
        new_role_adj = 0.8
        self.client.post(reverse('workload_app:school_page', kwargs={'faculty_id': new_fac.id}),{'role_name':new_role_name,'role_adjustment' : str(new_role_adj), 'fresh_record': True})
        self.assertEqual(ServiceRole.objects.all().count(),2) #The default plus the new one
        self.assertEqual(ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_name = new_role_name).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_adjustment = role_adj).count(),1)#old one still there
        self.assertEqual(ServiceRole.objects.filter(role_adjustment = new_role_adj).count(),0)#New one not added

        #Now add another one, valid addition
        valid_name = 'new_valid_addition'
        new_adj = 0.8
        self.client.post(reverse('workload_app:school_page', kwargs={'faculty_id': new_fac.id}),{'role_name':valid_name,'role_adjustment' : str(new_adj), 'fresh_record': True})
        self.assertEqual(ServiceRole.objects.all().count(),3) #The default plus two new ones
        self.assertEqual(ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_name = new_role_name).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_adjustment = role_adj).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_name = valid_name).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_adjustment = new_adj).count(),1)

        #Now edit the one just added (valid_name), trying to give it the same name as "new_role_name"
        id_of_valid = ServiceRole.objects.filter(role_name = valid_name).get().id
        self.client.post(reverse('workload_app:school_page', kwargs={'faculty_id': new_fac.id}),{'role_name':new_role_name,'role_adjustment' : str(new_adj), \
                                 'fresh_record': False,
                                 'role_id' : str(id_of_valid)})
        #Nothing should have changed
        self.assertEqual(ServiceRole.objects.all().count(),3) #The default plus two new ones
        self.assertEqual(ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_name = new_role_name).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_adjustment = role_adj).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_name = valid_name).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_adjustment = new_adj).count(),1)

    def test_add_remove_service_role_with_lecturer(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        
        new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
        new_scen = WorkloadScenario.objects.create(label='test_scen')
        def_track = EmploymentTrack.objects.filter(track_name = DEFAULT_TRACK_NAME)
        #Add one service role
        new_role_name = 'test_role'
        role_adj = 0.5
        self.client.post(reverse('workload_app:school_page', kwargs={'faculty_id': new_fac.id} ),{'role_name':new_role_name,'role_adjustment' : str(role_adj), 'fresh_record': True})
        new_role = ServiceRole.objects.filter(role_name = new_role_name)

        self.assertEqual(Lecturer.objects.all().count(),0)
        #Add a lecturer on this service role
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'bob','fraction_appointment' : '0.5',   \
                                                                 'employment_track': def_track.get().id, 'service_role' : new_role.get().id, 'is_external': False,'fresh_record' : True})
        self.assertEqual(Lecturer.objects.all().count(),1)
        self.assertEqual(Lecturer.objects.all().filter(name='bob').count(),1)
        self.assertEqual(Lecturer.objects.all().filter(service_role__role_name=new_role_name).count(),1)

        #Now remove the new role (in which the lecturer is in)
        self.client.post(reverse('workload_app:school_page', kwargs={'faculty_id': new_fac.id}),{'select_service_role_to_remove':new_role.get().id})
        #Expected behaviour: lecturer still there, switched to default role
        self.assertEqual(Lecturer.objects.all().count(),1)
        self.assertEqual(Lecturer.objects.all().filter(name='bob').count(),1)
        self.assertEqual(Lecturer.objects.all().filter(service_role__role_name=DEFAULT_SERVICE_ROLE_NAME).count(),1)
        self.assertEqual(ServiceRole.objects.all().count(),1) #Only the default one should be there
        self.assertEqual(ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_name = new_role_name).count(),0)
        self.assertEqual(ServiceRole.objects.filter(role_adjustment = role_adj).count(),0)

    def test_edit_lecturer_change_role(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        
        new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
        new_scen = WorkloadScenario.objects.create(label='test_scen')
        def_track = EmploymentTrack.objects.filter(track_name = DEFAULT_TRACK_NAME)
        
        #Add one track
        #Add one service role
        new_role_name = 'test_role'
        role_adj = 0.5
        self.client.post(reverse('workload_app:school_page', kwargs={'faculty_id': new_fac.id}),{'role_name':new_role_name,'role_adjustment' : str(role_adj), 'fresh_record': True})
        new_role = ServiceRole.objects.filter(role_name = new_role_name)
        self.assertEqual(ServiceRole.objects.all().count(),2)
        
        #Add another
        new_role_name_2 = 'test_role_2'
        role_adj_2 = 9
        self.client.post(reverse('workload_app:school_page', kwargs={'faculty_id': new_fac.id}),{'role_name':new_role_name_2,'role_adjustment' : str(role_adj_2), 'fresh_record': True})
        new_role_2 = ServiceRole.objects.filter(role_name = new_role_name_2)
        self.assertEqual(ServiceRole.objects.all().count(),3)
        self.assertEqual(ServiceRole.objects.filter(role_name=new_role_name_2).count(),1)

        self.assertEqual(Lecturer.objects.all().count(),0)
        #Add a lecturer on this service role
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'bob','fraction_appointment' : '0.5',  'employment_track': def_track.get().id, 'service_role' : new_role.get().id,\
                                                                 'is_external': False,'fresh_record' : True})
        self.assertEqual(Lecturer.objects.all().count(),1)
        self.assertEqual(Lecturer.objects.all().filter(name='bob').count(),1)
        self.assertEqual(Lecturer.objects.all().filter(service_role__role_name=new_role_name).count(),1)

        #Now edit the lecturer by changing his role
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'bob','fraction_appointment' : '0.5',   \
                                                                 'employment_track': def_track.get().id, 'service_role' : new_role_2.get().id,\
                                                                 'is_external': False, 'fresh_record' : False})
        self.assertEqual(Lecturer.objects.all().filter(name='bob').filter(service_role__role_name=new_role_name).count(),0)
        self.assertEqual(Lecturer.objects.all().filter(name='bob').filter(service_role__role_name=new_role_name_2).count(),1)

    def test_add_remove_role_with_lecturer_multiple_scen(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
        def_track = EmploymentTrack.objects.filter(track_name = DEFAULT_TRACK_NAME)

        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        
        new_scen_label = 'test_scen'
        new_scen_label_2 = 'test_scen_2'
        new_scen = WorkloadScenario.objects.create(label=new_scen_label)
        new_scen_2 = WorkloadScenario.objects.create(label=new_scen_label_2)
        #Add two roles
        new_role_name = 'test_role'
        new_role_name_2 = 'test_role_2'
        role_adj = 0.5
        self.client.post(reverse('workload_app:school_page', kwargs={'faculty_id': new_fac.id}),{'role_name':new_role_name,'role_adjustment' : str(role_adj), 'fresh_record': True})
        self.client.post(reverse('workload_app:school_page', kwargs={'faculty_id': new_fac.id} ),{'role_name':new_role_name_2,'role_adjustment' : str(role_adj), 'fresh_record': True})
        new_role = ServiceRole.objects.filter(role_name = new_role_name)
        new_role_2 = ServiceRole.objects.filter(role_name = new_role_name_2)

        self.assertEqual(Lecturer.objects.all().count(),0)
        #Add lecturers on one track on one scenario...
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'bob','fraction_appointment' : '0.5',    \
                                                                'workload_scenario': new_scen.id, 'service_role' : new_role.get().id, \
                                                                'employment_track': def_track.get().id, 'is_external': False, 'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'ted','fraction_appointment' : '0.5',    \
                                                                'workload_scenario': new_scen.id, 'service_role' : new_role.get().id, \
                                                                'employment_track': def_track.get().id, 'is_external': False, 'fresh_record' : True})
        #Focus on scenario 2
        #and the same lecturers to another scenario (one changed role)
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen_2.id}),{'name':'bob','fraction_appointment' : '0.5',    \
                                                                'workload_scenario': new_scen_2.id, 'service_role' : new_role.get().id, \
                                                                'employment_track': def_track.get().id, 'is_external': False,'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen_2.id}),{'name':'ted','fraction_appointment' : '0.5',    \
                                                                'workload_scenario': new_scen_2.id, 'service_role' : new_role_2.get().id, \
                                                                'employment_track': def_track.get().id, 'is_external': False, 'fresh_record' : True})
        #Back to scenario 1
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        
        self.assertEqual(Lecturer.objects.all().count(),4)
        self.assertEqual(Lecturer.objects.all().filter(name='bob').count(),2)
        self.assertEqual(Lecturer.objects.all().filter(service_role__role_name=new_role_name).count(),3)

        #Now remove the new track (in which 3 lecturers, in 2 scenarios are in)
        self.client.post(reverse('workload_app:school_page', kwargs={'faculty_id': new_fac.id}),{'select_service_role_to_remove':new_role.get().id})
        #Expected behaviour: all lecturers still there, but switched to default service role
        self.assertEqual(Lecturer.objects.all().count(),4)
        self.assertEqual(Lecturer.objects.all().filter(name='bob').count(),2)
        self.assertEqual(Lecturer.objects.all().filter(service_role__role_name=DEFAULT_SERVICE_ROLE_NAME).count(),3)#3 turned to default
        self.assertEqual(ServiceRole.objects.all().count(),2) #default plus role_2
        self.assertEqual(ServiceRole.objects.filter(role_name = DEFAULT_SERVICE_ROLE_NAME).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_name = new_role_name).count(),0)
        self.assertEqual(ServiceRole.objects.filter(role_name = new_role_name_2).count(),1)
        self.assertEqual(ServiceRole.objects.filter(role_adjustment = role_adj).count(),1)