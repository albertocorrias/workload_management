from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User, Group
from decimal import *

from workload_app.models import Faculty, Department, Module, ModuleType, WorkloadScenario,UniversityStaff, Academicyear, Lecturer, EmploymentTrack, ServiceRole
from workload_app.helper_methods_users import DetermineUserHomePage, CanUserAdminThisDepartment, CanUserAdminThisModule

class TestUserPermissions(TestCase):

    def testHelperMethodsForUser(self):
        
        sup_user = User.objects.create_user('new_super_user', 'test@user.com', 'test_super_user_password')
        sup_user.is_superuser = True
        sup_user.save()
        uni_super_user = UniversityStaff.objects.create(user = sup_user, department=None,faculty=None)
        self.assertEqual(DetermineUserHomePage(uni_super_user.id), 'workloads_index/')

        #Create fauclty, dept and module
        new_fac = Faculty.objects.create(faculty_name = 'test_fac', faculty_acronym = 'CDE')
        new_dept = Department.objects.create(department_name = 'test_dept', department_acronym = 'BME', faculty = new_fac)
        #Create a module
        mod_code = "BN2102"
        acad_year_1 = Academicyear.objects.create(start_year=2021)
        scenario_1 = WorkloadScenario.objects.create(label="scenario_1", academic_year = acad_year_1, dept = new_dept, status = WorkloadScenario.OFFICIAL)
        mod_type_1 = ModuleType.objects.create(type_name = "one type")
        track_1 = EmploymentTrack.objects.create(track_name = "track_1", track_adjustment = 2.0, is_adjunct = False)
        service_role_1 = ServiceRole.objects.create(role_name = "role_1", role_adjustment = 2.0)
        module_1 = Module.objects.create(module_code = mod_code, module_title="First module", scenario_ref=scenario_1, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1)
        lecturer_1 = Lecturer.objects.create(name="lecturer_1", fraction_appointment = 0.7, employment_track=track_1, workload_scenario = scenario_1, service_role = service_role_1)
        self.assertEqual(CanUserAdminThisDepartment(uni_super_user.id, new_dept.id+1258), False) #coverage of wrong dept number
        self.assertEqual(CanUserAdminThisModule(uni_super_user.id, module_code = mod_code+'hello'), False) #coverage of wrong module code
        self.assertEqual(CanUserAdminThisDepartment(uni_super_user.id, new_dept.id), True)

        fac_admin = User.objects.create_user('new_fac_admin_user', 'test@fuser.com', 'test_fac_admin_user_password')
        fac_admin.is_superuser = False
        fac_admin.save()
        #create realistic group
        fac_admin_gr = Group.objects.create(name = 'FacultyAdminStaff')
        fac_admin.groups.add(fac_admin_gr) #add user to group
        #Simulate creation with None Dept and None Faculty (should return error text)
        uni_fac_admin = UniversityStaff.objects.create(user = fac_admin, department=None,faculty=None)
        custom_error_message = "my error message"
        self.assertEqual(DetermineUserHomePage(uni_fac_admin.id, error_text = custom_error_message), custom_error_message)
        self.assertEqual(CanUserAdminThisDepartment(uni_fac_admin.id, new_dept.id), False)#No faculty assigned yet....
        self.assertEqual(CanUserAdminThisModule(uni_fac_admin.id, mod_code), False)
        #Now assign the faculty
        uni_fac_admin.faculty = new_fac
        uni_fac_admin.save()
        self.assertEqual(DetermineUserHomePage(uni_fac_admin.id, error_text = custom_error_message), "workloads_index/")
        self.assertEqual(CanUserAdminThisDepartment(uni_fac_admin.id, new_dept.id), True)#Now assigned proper faculty

        dept_admin = User.objects.create_user('new_dept_admin_user', 'test@duser.com', 'test_dept_admin_user_password')
        dept_admin.is_superuser = False
        dept_admin.save()
        #Create dept admin group
        dept_admin_group = Group.objects.create(name = 'DepartmentAdminStaff')
        dept_admin.groups.add(dept_admin_group)
        #Create a uni dept admin user
        uni_dept_admin = UniversityStaff.objects.create(user = dept_admin, department=None,faculty=None)
        #NOW this dept admin has both faculty and dept as None. Should thrpw error
        self.assertEqual(DetermineUserHomePage(uni_dept_admin.id, error_text = custom_error_message), custom_error_message)
        self.assertEqual(CanUserAdminThisDepartment(uni_dept_admin.id, new_dept.id), False)#No dept assigned yet....
        self.assertEqual(CanUserAdminThisModule(uni_dept_admin.id, mod_code), False)
        #assign faculty and department
        uni_dept_admin.faculty = new_fac
        uni_dept_admin.save()
        uni_dept_admin.department = new_dept
        uni_dept_admin.save()
        self.assertEqual(DetermineUserHomePage(uni_dept_admin.id, error_text = custom_error_message), 'department/'+str(new_dept.id))
        self.assertEqual(CanUserAdminThisDepartment(uni_dept_admin.id, new_dept.id), True)#Now assigned proper dept

        self.assertEqual(CanUserAdminThisModule(uni_dept_admin.id, mod_code), True)
        self.assertEqual(CanUserAdminThisModule(uni_fac_admin.id, mod_code), True)
        self.assertEqual(CanUserAdminThisModule(uni_super_user.id, mod_code), True)

        #Create a lecturer user
        lec_user = User.objects.create_user('new_lecturer_user', 'test@luser.com', 'test_lec_user_password')
        lec_user.is_superuser = False
        lec_user.save()
        #Create dept admin group
        lec_user_group = Group.objects.create(name = 'LecturerStaff')
        lec_user.groups.add(lec_user_group)
        #Create a uni dept admin user
        uni_lec_user = UniversityStaff.objects.create(user = lec_user, department=None,faculty=None,lecturer=None)
        self.assertEqual(DetermineUserHomePage(uni_lec_user.id, error_text = custom_error_message), custom_error_message)#Still no lecturer assigned
        uni_lec_user.faculty = new_fac
        uni_lec_user.save()
        uni_lec_user.department = new_dept
        uni_lec_user.save()
        uni_lec_user.lecturer = lecturer_1
        uni_lec_user.save()
        #####################
        ##TBC here
        ####################

        #test faculty and department mismatch
        #Create one mor efacultya nd one more dpet      
        new_fac_2 = Faculty.objects.create(faculty_name = 'test_fac_2', faculty_acronym = 'CDE_2')
        new_dept_2 = Department.objects.create(department_name = 'test_dept_2', department_acronym = 'BME_2', faculty = new_fac_2)
        uni_dept_admin.faculty = new_fac_2
        uni_dept_admin.save()
        uni_dept_admin.department = new_dept_2
        uni_dept_admin.save()
        uni_fac_admin.faculty = new_fac_2
        uni_fac_admin.save()

        #Now both dept admin and faculty admin have mismatched faculty and department belonging
        self.assertEqual(CanUserAdminThisDepartment(uni_dept_admin.id, new_dept.id), False)#Can't manage old dept
        self.assertEqual(CanUserAdminThisDepartment(uni_dept_admin.id, new_dept_2.id), True)#Can  manage new dept_2

        self.assertEqual(CanUserAdminThisDepartment(uni_fac_admin.id, new_dept.id), False)#Can't manage old dept
        self.assertEqual(CanUserAdminThisDepartment(uni_fac_admin.id, new_dept_2.id), True)#Can  manage new dept_2