from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *
from eduload.models import WorkloadScenario,Department, Faculty, ProgrammeOffered, Academicyear, Lecturer, \
    ServiceRole, EmploymentTrack, Module, ModuleType,TeachingAssignment, UniversityStaff
from eduload.helper_methods_demo import populate_database

class TestHelperMethodsDemo(TenantTestCase):
    def setup_user(self):
        #The test client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = TenantClient(self.tenant, HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
        self.user.is_superuser = True
        self.user.save()
        uni_user = UniversityStaff.objects.create(user = self.user, department=None,faculty=None)
        
    def test_demo(self):

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        #Default schema name of TenantClient is 'test' according to documentation
        #https://django-tenants.readthedocs.io/en/latest/test.html?highlight=tenantclient
        x = populate_database(schema='test') 
        self.assertEqual(Lecturer.objects.all().count(),6*(40+43+20))


        