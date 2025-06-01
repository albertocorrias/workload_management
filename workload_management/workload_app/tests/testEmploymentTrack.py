from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *

from workload_app.models import Lecturer, WorkloadScenario, Department, EmploymentTrack, ServiceRole, UniversityStaff, Faculty,Academicyear


class TestEmploymentTrack(TestCase):
    def setup_user(self):
        #The test client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
        self.user.is_superuser = True
        self.user.save()
        uni_user = UniversityStaff.objects.create(user = self.user, department=None,faculty=None)
        
    def test_add_remove_track(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(EmploymentTrack.objects.all().count(),0)
        #Test the GET
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
        #Test the POST now
        new_track_name = 'test_track'
        track_adj = 0.5
        self.client.post(reverse('workload_app:school_page' ,  kwargs={'faculty_id': new_fac.id}),{'track_name':new_track_name,'track_adjustment' : str(track_adj), 'fresh_record': True})
        
        self.assertEqual(EmploymentTrack.objects.all().count(),1) #One created
        self.assertEqual(EmploymentTrack.objects.filter(track_name = new_track_name).count(),1)
        self.assertEqual(EmploymentTrack.objects.filter(track_adjustment = track_adj).count(),1)
        self.assertEqual(EmploymentTrack.objects.filter(is_adjunct = False).count(),1)#Default is false for the adjunct flag

        #Remove the track we just added
        new_track = EmploymentTrack.objects.filter(track_name = new_track_name)
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'select_track_to_remove':new_track.get().id})
        self.assertEqual(EmploymentTrack.objects.all().count(),0) #None left
    
    def test_edit_existing_track(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
        self.assertEqual(EmploymentTrack.objects.all().count(),0)
        #Test the GET
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        self.assertEqual(EmploymentTrack.objects.all().count(),0) #T
        self.assertEqual(EmploymentTrack.objects.filter(is_adjunct = False).count(),0)

        #Test the POST now
        track_name = 'test_track'
        track_adj = 0.5
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'track_name':track_name,'track_adjustment' : str(track_adj), 'is_adjunct' : False,'fresh_record': True})
        self.assertEqual(EmploymentTrack.objects.all().count(),1) #One
        self.assertEqual(EmploymentTrack.objects.filter(track_name = track_name).count(),1)
        self.assertEqual(EmploymentTrack.objects.filter(is_adjunct = False).count(),1)#Default is false for the adjunct flag, plus the default track

        track_id = EmploymentTrack.objects.filter(track_name = track_name).get().id
        #Now edit the adjustment
        track_adj_after_change = 0.8
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'track_name':track_name,\
                                                                        'track_adjustment' : str(track_adj_after_change), \
                                                                         'fresh_record': False,
                                                                         'is_adjunct' : False,
                                                                         'employment_track_id': str(track_id)})

        self.assertEqual(EmploymentTrack.objects.all().count(),1) #One
        self.assertEqual(EmploymentTrack.objects.filter(track_name = track_name).count(),1)
        self.assertEqual(EmploymentTrack.objects.filter(track_adjustment = track_adj).count(),0)
        self.assertEqual(EmploymentTrack.objects.filter(track_adjustment = track_adj_after_change).count(),1)
        self.assertEqual(EmploymentTrack.objects.filter(is_adjunct = False).count(),1)

        #Now edit the name
        new_name = "hello"
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'track_name':new_name,\
                                                                        'track_adjustment' : str(track_adj_after_change), \
                                                                         'fresh_record': False,
                                                                         'is_adjunct' : False,
                                                                         'employment_track_id': str(track_id)})

        self.assertEqual(EmploymentTrack.objects.all().count(),1) #one
        self.assertEqual(EmploymentTrack.objects.filter(track_name = track_name).count(),0)#No more
        self.assertEqual(EmploymentTrack.objects.filter(track_name = new_name).count(),1)#new one is there
        self.assertEqual(EmploymentTrack.objects.filter(track_adjustment = track_adj).count(),0)
        self.assertEqual(EmploymentTrack.objects.filter(track_adjustment = track_adj_after_change).count(),1)
        self.assertEqual(EmploymentTrack.objects.filter(is_adjunct = False).count(),1)

        #Now edit the is_adjunct flag
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'track_name':new_name,\
                                                                        'track_adjustment' : str(track_adj_after_change), \
                                                                         'fresh_record': False,
                                                                         'is_adjunct': True,
                                                                         'employment_track_id': str(track_id)})

        self.assertEqual(EmploymentTrack.objects.all().count(),1)#one
        self.assertEqual(EmploymentTrack.objects.filter(track_name = track_name).count(),0)#No more
        self.assertEqual(EmploymentTrack.objects.filter(track_name = new_name).count(),1)#new one is there
        self.assertEqual(EmploymentTrack.objects.filter(track_adjustment = track_adj).count(),0)
        self.assertEqual(EmploymentTrack.objects.filter(track_adjustment = track_adj_after_change).count(),1)
        self.assertEqual(EmploymentTrack.objects.filter(is_adjunct = False).count(),0)
        self.assertEqual(EmploymentTrack.objects.filter(is_adjunct = True).count(),1)#This one has become adjunct

        #Coverage. Create new employment track from scratch, as adjunct
        another_new_name = 'this one is adjunct'
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'track_name':another_new_name,\
                                                                        'track_adjustment' : str(track_adj_after_change), \
                                                                         'fresh_record': True,
                                                                         'is_adjunct': True,
                                                                         'employment_track_id': str(track_id)})
        self.assertEqual(EmploymentTrack.objects.all().count(),2) #one plus one
        self.assertEqual(EmploymentTrack.objects.filter(track_name = track_name).count(),0)#No more
        self.assertEqual(EmploymentTrack.objects.filter(track_name = new_name).count(),1)#new one is still there
        self.assertEqual(EmploymentTrack.objects.filter(track_name = another_new_name).count(),1)#the newest new one is there
        self.assertEqual(EmploymentTrack.objects.filter(track_adjustment = track_adj).count(),0)
        self.assertEqual(EmploymentTrack.objects.filter(track_adjustment = track_adj_after_change).count(),2)
        self.assertEqual(EmploymentTrack.objects.filter(is_adjunct = False).count(),0)
        self.assertEqual(EmploymentTrack.objects.filter(is_adjunct = True).count(),2)#One with adjunct now
        self.assertEqual(EmploymentTrack.objects.filter(is_adjunct = True).filter(track_name = another_new_name).count(),1)#just to be sure...

    
    def test_no_duplicate_names(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
        self.assertEqual(EmploymentTrack.objects.all().count(),0)
        #Test the GET
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        self.assertEqual(EmploymentTrack.objects.all().count(),0)

        #Test the POST now
        track_name = 'test_track'
        track_adj = 0.5
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'track_name':track_name,'track_adjustment' : str(track_adj), 'fresh_record': True})
        self.assertEqual(EmploymentTrack.objects.all().count(),1)
        self.assertEqual(EmploymentTrack.objects.filter(track_name = track_name).count(),1)

        #Try adding another one with the same name
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'track_name':track_name,'track_adjustment' : str(0.3), 'fresh_record': True})
        self.assertEqual(EmploymentTrack.objects.all().count(),1)
        self.assertEqual(EmploymentTrack.objects.filter(track_name = track_name).count(),1)

        #Now we ligitinamtely add another one
        new_name = "hello"
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'track_name':new_name,'track_adjustment' : str(0.75), 'fresh_record': True})
        self.assertEqual(EmploymentTrack.objects.all().count(),2)
        self.assertEqual(EmploymentTrack.objects.filter(track_name = new_name).count(),1)

        #Now try editing the new one and give it the name of the existing one
        new_track_id = EmploymentTrack.objects.filter(track_name = new_name).get().id
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'track_name':track_name,\
                                                                        'track_adjustment' : str(0.75), \
                                                                         'fresh_record': False,
                                                                         'employment_track_id': str(new_track_id)})
        
        #The edit should fail. everything should remian as it is
        self.assertEqual(EmploymentTrack.objects.all().count(),2)
        self.assertEqual(EmploymentTrack.objects.filter(track_name = track_name).count(),1)
        self.assertEqual(EmploymentTrack.objects.filter(track_name = new_name).count(),1)#Still there, edit failed

    def test_add_remove_track_with_lecturer(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
        new_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        new_scen = WorkloadScenario.objects.create(label='test_scen', dept=new_dept, academic_year=acad_year)
        #Add one track
        new_track_name = 'test_track'
        track_adj = 0.5
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'track_name':new_track_name,'track_adjustment' : str(track_adj), 'fresh_record': True})
        new_track = EmploymentTrack.objects.filter(track_name = new_track_name)

        def_role = ServiceRole.objects.create(role_name = "bew role", role_adjustment=1.0, faculty=new_fac)
        self.assertEqual(Lecturer.objects.all().count(),0)
        #Add a lecturer on that track
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'bob','fraction_appointment' : '0.5',    \
                                                                'service_role' : def_role.id, 'employment_track' : new_track.get().id, 'is_external': False, 'fresh_record' : True})
        self.assertEqual(Lecturer.objects.all().count(),1)
        self.assertEqual(Lecturer.objects.all().filter(name='bob').count(),1)
        self.assertEqual(Lecturer.objects.all().filter(employment_track__track_name=new_track_name).count(),1)

        #Now remove the new track (in which the lecturer is in)
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'select_track_to_remove':new_track.get().id})
        #Expected behaviour: lecturer deleted
        self.assertEqual(Lecturer.objects.all().count(),0)
        self.assertEqual(EmploymentTrack.objects.all().count(),0) #No more

    def test_edit_lecturer_change_track(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
        new_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        new_scen = WorkloadScenario.objects.create(label='test_scen', dept=new_dept, academic_year=acad_year)
        def_role = ServiceRole.objects.create(role_name = "bew role", role_adjustment=1.0, faculty=new_fac)
        #Add one track
        new_track_name = 'test_track'
        track_adj = 0.5
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'track_name':new_track_name,'track_adjustment' : str(track_adj), 'fresh_record': True})
        new_track = EmploymentTrack.objects.filter(track_name = new_track_name)
        self.assertEqual(EmploymentTrack.objects.all().count(),1)
        
        #Add another
        new_track_name_2 = 'test_track_2'
        track_adj_2 = 9
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'track_name':new_track_name_2,'track_adjustment' : str(track_adj_2), 'fresh_record': True})
        new_track_2 = EmploymentTrack.objects.filter(track_name = new_track_name_2)
        self.assertEqual(EmploymentTrack.objects.all().count(),2)
        self.assertEqual(EmploymentTrack.objects.filter(track_name=new_track_name_2).count(),1)

        self.assertEqual(Lecturer.objects.all().count(),0)
        #Add a lecturer on that track
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'bob','fraction_appointment' : '0.5',    \
                                                                'service_role' : def_role.id, 'employment_track' : new_track.get().id, 'is_external': False,'fresh_record' : True})
        self.assertEqual(Lecturer.objects.all().count(),1)
        self.assertEqual(Lecturer.objects.all().filter(name='bob').count(),1)
        self.assertEqual(Lecturer.objects.all().filter(name='bob').filter(employment_track__track_name=new_track_name).count(),1)
        self.assertEqual(Lecturer.objects.all().filter(name='bob').filter(employment_track__track_name=new_track_name_2).count(),0)

        #Now edit the lecturer by changing his track
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'bob','fraction_appointment' : '0.5',    \
                                                                 'service_role' : def_role.id, 'employment_track' : new_track_2.get().id, 'is_external': False,'fresh_record' : False})
        self.assertEqual(Lecturer.objects.all().filter(name='bob').filter(employment_track__track_name=new_track_name).count(),0)
        self.assertEqual(Lecturer.objects.all().filter(name='bob').filter(employment_track__track_name=new_track_name_2).count(),1)

    def test_add_remove_track_with_lecturer_multiple_scen(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        new_fac = Faculty.objects.create(faculty_name ="test fac",faculty_acronym="TSFC")
        new_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        acad_year = Academicyear.objects.create(start_year=2025)
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        def_role = ServiceRole.objects.create(role_name = "bew role", role_adjustment=1.0, faculty=new_fac)

        new_scen_label = 'test_scen'
        new_scen_label_2 = 'test_scen_2'
        acad_year_2 = Academicyear.objects.create(start_year=2015)
        
        new_scen = WorkloadScenario.objects.create(label=new_scen_label,dept=new_dept, academic_year=acad_year)
        new_scen_2 = WorkloadScenario.objects.create(label=new_scen_label_2,dept=new_dept, academic_year=acad_year_2)
        #Add two tracks
        new_track_name = 'test_track'
        new_track_name_2 = 'test_track_2'
        track_adj = 0.5
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'track_name':new_track_name,'track_adjustment' : str(track_adj),'fresh_record': True})
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'track_name':new_track_name_2,'track_adjustment' : str(track_adj), 'fresh_record': True})
        new_track = EmploymentTrack.objects.filter(track_name = new_track_name)
        new_track_2 = EmploymentTrack.objects.filter(track_name = new_track_name_2)

        self.assertEqual(Lecturer.objects.all().count(),0)
        #Add lecturers on one track on one scenario...
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'bob','fraction_appointment' : '0.5',    \
                                                                'workload_scenario': new_scen.id, 'employment_track' : new_track.get().id, \
                                                                'service_role' : def_role.id, 'is_external': False, 'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen.id}),{'name':'ted','fraction_appointment' : '0.5',    \
                                                                'workload_scenario': new_scen.id, 'employment_track' : new_track.get().id, \
                                                                'service_role' : def_role.id, 'is_external': False,'fresh_record' : True})
        
        #and the same lecturers to another scenario (one changed track)
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen_2.id}),{'name':'bob','fraction_appointment' : '0.5',    \
                                                                'workload_scenario': new_scen_2.id, 'employment_track' : new_track.get().id, \
                                                                'service_role' : def_role.id,'is_external': False, 'fresh_record' : True})
        self.client.post(reverse('workload_app:add_professor',  kwargs={'workloadscenario_id': new_scen_2.id}),{'name':'ted','fraction_appointment' : '0.5',    \
                                                                'workload_scenario': new_scen_2.id, 'employment_track' : new_track_2.get().id, \
                                                                'service_role' : def_role.id, 'is_external': False,'fresh_record' : True})
        #Focus on scenario 1 now
        response = self.client.get(reverse('workload_app:scenario_view',  kwargs={'workloadscenario_id': new_scen.id}))
        self.assertEqual(response.status_code, 200) #No issues
        
        self.assertEqual(Lecturer.objects.all().count(),4)
        self.assertEqual(Lecturer.objects.all().filter(name='bob').count(),2)
        self.assertEqual(Lecturer.objects.all().filter(employment_track__track_name=new_track_name).count(),3)

        #Now remove the new track (in which 3 lecturers, in 2 scenarios are in)
        self.client.post(reverse('workload_app:school_page',  kwargs={'faculty_id': new_fac.id}),{'select_track_to_remove':new_track.get().id})
        #Expected behaviour: lecturer still there, switched to default track
        self.assertEqual(Lecturer.objects.all().count(),1)
        self.assertEqual(Lecturer.objects.all().filter(name='ted').count(),1)
        self.assertEqual(EmploymentTrack.objects.all().count(),1) #one
        self.assertEqual(EmploymentTrack.objects.filter(track_name = new_track_name).count(),0)
        self.assertEqual(EmploymentTrack.objects.filter(track_name = new_track_name_2).count(),1)
        self.assertEqual(EmploymentTrack.objects.filter(track_adjustment = track_adj).count(),1)