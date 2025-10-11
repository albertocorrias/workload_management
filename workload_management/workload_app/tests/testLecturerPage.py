from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *
from workload_app.global_constants import DEFAULT_TRACK_NAME,DEFAULT_SERVICE_ROLE_NAME
from workload_app.models import StudentLearningOutcome, ProgrammeOffered, Faculty, Department, Academicyear,WorkloadScenario,EmploymentTrack,ServiceRole,TeachingAssignmentType,\
    ModuleType, SubProgrammeOffered, Lecturer, Module, TeachingAssignment,ModuleLearningOutcome,MLOSLOMapping,MLOPerformanceMeasure, CorrectiveAction, UniversityStaff

from workload_app.report_methods import GetLastNYears,CalculateProfessorIndividualWorkload,CalculateProfessorChartData
from workload_app.helper_methods_users import DetermineUserMenu
class TestLecturerPage(TestCase):
    def setup_user(self):
        #The test client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
        self.user.is_superuser = True
        self.user.save()
        uni_user = UniversityStaff.objects.create(user = self.user, department=None,faculty=None)

    def test_lecturer_page(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        years = GetLastNYears(5)
        self.assertEqual(len(years["labels"]),5)
        self.assertEqual(len(years["years"]),5)

        #Cover the case of a random lecturer_id that does not exist
        response = self.client.get(reverse('workload_app:lecturer_page',  kwargs={'lecturer_id': 345}))
        self.assertEqual(response.status_code, 200) #no issue
        self.assertEqual(response.context["error_message"], "No such lecturer exists")
        
        acad_year_1 = Academicyear.objects.create(start_year=years["years"][0])
        acad_year_2 = Academicyear.objects.create(start_year=years["years"][1])
        acad_year_3 = Academicyear.objects.create(start_year=years["years"][2])
        acad_year_4 = Academicyear.objects.create(start_year=years["years"][3])
        acad_year_5 = Academicyear.objects.create(start_year=years["years"][4])
        dept_name = 'test_dept'
        first_fac = Faculty.objects.create(faculty_name = "first fac", faculty_acronym = "FRTE")
        test_dept = Department.objects.create(department_name = dept_name, department_acronym = "ACR", faculty = first_fac)
        
        scenario_1 = WorkloadScenario.objects.create(label="scenario_1", academic_year = acad_year_1, dept = test_dept, status = WorkloadScenario.OFFICIAL)
        scenario_2 = WorkloadScenario.objects.create(label="scenario_2", academic_year = acad_year_2, dept = test_dept, status = WorkloadScenario.OFFICIAL)
        scenario_3 = WorkloadScenario.objects.create(label="scenario_3", academic_year = acad_year_3, dept = test_dept, status = WorkloadScenario.OFFICIAL)
        scenario_4 = WorkloadScenario.objects.create(label="scenario_4", academic_year = acad_year_4, dept = test_dept, status = WorkloadScenario.OFFICIAL)
        scenario_5 = WorkloadScenario.objects.create(label="scenario_5", academic_year = acad_year_5, dept = test_dept, status = WorkloadScenario.OFFICIAL)

        track_adjust = 2.0
        service_role_adjust = 3.0
        track_1 = EmploymentTrack.objects.create(track_name = "track_1", track_adjustment = track_adjust, is_adjunct = False, faculty=first_fac)
        service_role_1 = ServiceRole.objects.create(role_name = "role_1", role_adjustment = service_role_adjust, faculty=first_fac)
        service_role_2 = ServiceRole.objects.create(role_name = "role_2", role_adjustment = service_role_adjust+0.5, faculty=first_fac)
        mod_type_1 = ModuleType.objects.create(type_name = "one type", department=test_dept)
        programme_1 = ProgrammeOffered.objects.create(programme_name = "B. Eng", primary_dept = test_dept)
        programme_2 = ProgrammeOffered.objects.create(programme_name = "M. Sc", primary_dept = test_dept)
        sub_programme_1 = SubProgrammeOffered.objects.create(sub_programme_name = "specialization", main_programme = programme_1)

        #CREATE ONE LECTURER - for the first 4 of the 5 academic years (same name)
        lecturer_1 = Lecturer.objects.create(name="lecturer_1", fraction_appointment = 1.0, employment_track=track_1, workload_scenario = scenario_1, service_role = service_role_1)
        lecturer_2 = Lecturer.objects.create(name="lecturer_1", fraction_appointment = 1.0, employment_track=track_1, workload_scenario = scenario_2, service_role = service_role_1)
        lecturer_3 = Lecturer.objects.create(name="lecturer_1", fraction_appointment = 0.5, employment_track=track_1, workload_scenario = scenario_3, service_role = service_role_1)
        lecturer_4 = Lecturer.objects.create(name="lecturer_1", fraction_appointment = 0.5, employment_track=track_1, workload_scenario = scenario_4, service_role = service_role_2)
        #For the last acad year, there is another lecturer
        anot_lect = Lecturer.objects.create(name="another_lect", fraction_appointment = 0.5, employment_track=track_1, workload_scenario = scenario_5, service_role = service_role_1)
        
        #Create 5 modules, same code same title
        mod_code = "BN101"
        mod_title = "new mod"
        module_1 = Module.objects.create(module_code = mod_code, module_title=mod_title, scenario_ref=scenario_1, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1)
        module_2 = Module.objects.create(module_code = mod_code, module_title=mod_title, scenario_ref=scenario_2, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1)
        module_3 = Module.objects.create(module_code = mod_code, module_title=mod_title, scenario_ref=scenario_3, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1)
        module_4 = Module.objects.create(module_code = mod_code, module_title=mod_title, scenario_ref=scenario_4, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1)
        module_5 = Module.objects.create(module_code = mod_code, module_title=mod_title, scenario_ref=scenario_5, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1)

        mode_code_2 = "BN201"
        mod_title_2 = "new mod 2"
        module_6 = Module.objects.create(module_code = mode_code_2, module_title=mod_title_2, scenario_ref=scenario_5, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1)

        #Do some assignmentsto "lecturer_1" for the first four years, to another_elct for the last year
        assignment_type = TeachingAssignmentType.objects.create(description="hours", quantum_number_of_hours=1,faculty=first_fac)
        TeachingAssignment.objects.create(assigned_module = module_1, assigned_lecturer = lecturer_1, assignnment_type=assignment_type, number_of_hours = 25, workload_scenario=scenario_1)
        TeachingAssignment.objects.create(assigned_module = module_2, assigned_lecturer = lecturer_2, assignnment_type=assignment_type, number_of_hours = 35, workload_scenario=scenario_2)
        TeachingAssignment.objects.create(assigned_module = module_3, assigned_lecturer = lecturer_3, assignnment_type=assignment_type, number_of_hours = 45, workload_scenario=scenario_3)
        TeachingAssignment.objects.create(assigned_module = module_4, assigned_lecturer = lecturer_4, assignnment_type=assignment_type, number_of_hours = 95, workload_scenario=scenario_4)
        TeachingAssignment.objects.create(assigned_module = module_5, assigned_lecturer = anot_lect, assignnment_type=assignment_type, number_of_hours = 25, workload_scenario=scenario_5)
        
        user_oobj = UniversityStaff.objects.filter(user__username='test_user').get()
        menu = DetermineUserMenu(user_oobj, is_super_user=True,force_population=True)

        #Now call lecturer page
        response = self.client.get(reverse('workload_app:lecturer_page',  kwargs={'lecturer_id': lecturer_1.id}))
        self.assertEqual(response.status_code, 200) #no issues
        self.assertEqual(response.context["lec_name"], "lecturer_1")
        summary_wl_table = response.context["summary_wl_table_individual"]
        self.assertEqual(len(summary_wl_table), 3)#one assigment plus 2 extra lines
        self.assertEqual(len(summary_wl_table[0]), 7)#mod code, mod title, plus 5 years
        self.assertEqual(len(summary_wl_table[1]), 7)#mod code, mod title, plus 5 years
        self.assertEqual(len(summary_wl_table[2]), 7)#mod code, mod title, plus 5 years
        
        self.assertEqual(summary_wl_table[0][0],mod_code)#
        self.assertEqual(summary_wl_table[0][1],mod_title)#
        self.assertEqual(summary_wl_table[0][2],25)#
        self.assertEqual(summary_wl_table[0][3],35)#
        self.assertEqual(summary_wl_table[0][4],45)#
        self.assertEqual(summary_wl_table[0][5],95)#
        self.assertEqual(summary_wl_table[0][6],0)# No assigments in last year

        self.assertEqual(summary_wl_table[1][0],"Total")#
        self.assertEqual(summary_wl_table[1][1],"")#
        self.assertEqual(summary_wl_table[1][2],25)#
        self.assertEqual(summary_wl_table[1][3],35)#
        self.assertEqual(summary_wl_table[1][4],45)#
        self.assertEqual(summary_wl_table[1][5],95)#
        self.assertEqual(summary_wl_table[1][6],0)# No assigments in last year

        self.assertEqual(summary_wl_table[2][0],"tFTE")#
        self.assertEqual(summary_wl_table[2][1],"")#
        self.assertAlmostEqual(summary_wl_table[2][2],track_adjust*service_role_adjust*1.0)#
        self.assertAlmostEqual(summary_wl_table[2][3],track_adjust*service_role_adjust*1.0)#
        self.assertAlmostEqual(summary_wl_table[2][4],track_adjust*service_role_adjust*0.5)#
        self.assertAlmostEqual(summary_wl_table[2][5],track_adjust*(service_role_adjust+0.5)*0.5)#fourth year, new service role with +0.5
        self.assertEqual(summary_wl_table[2][6],0)# No assigments in last year - lecturer is not in the workload. We put zero there

        #If we call for lecturer 2,we should get the same stuff as it is the same guy actually
        response = self.client.get(reverse('workload_app:lecturer_page',  kwargs={'lecturer_id': lecturer_2.id}))
        self.assertEqual(response.status_code, 200) #no issues
        self.assertEqual(response.context["lec_name"], "lecturer_1")
        summary_wl_table = response.context["summary_wl_table_individual"]
        self.assertEqual(len(summary_wl_table), 3)#one assigment plus 2 extra lines
        self.assertEqual(len(summary_wl_table[0]), 7)#mod code, mod title, plus 5 years
        self.assertEqual(len(summary_wl_table[1]), 7)#mod code, mod title, plus 5 years
        self.assertEqual(len(summary_wl_table[2]), 7)#mod code, mod title, plus 5 years
        
        self.assertEqual(summary_wl_table[0][0],mod_code)#
        self.assertEqual(summary_wl_table[0][1],mod_title)#
        self.assertEqual(summary_wl_table[0][2],25)#
        self.assertEqual(summary_wl_table[0][3],35)#
        self.assertEqual(summary_wl_table[0][4],45)#
        self.assertEqual(summary_wl_table[0][5],95)#
        self.assertEqual(summary_wl_table[0][6],0)# No assigments in last year

        #Now we call for "another lecturer"
        response = self.client.get(reverse('workload_app:lecturer_page',  kwargs={'lecturer_id': anot_lect.id}))
        self.assertEqual(response.status_code, 200) #no issues
        self.assertEqual(response.context["lec_name"], "another_lect")
        summary_wl_table = response.context["summary_wl_table_individual"]
        self.assertEqual(len(summary_wl_table), 3)#one assigment plus 2 extra lines
        self.assertEqual(len(summary_wl_table[0]), 7)#mod code, mod title, plus 5 years
        self.assertEqual(len(summary_wl_table[1]), 7)#mod code, mod title, plus 5 years
        self.assertEqual(len(summary_wl_table[2]), 7)#mod code, mod title, plus 5 years
        
        self.assertEqual(summary_wl_table[0][0],mod_code)#
        self.assertEqual(summary_wl_table[0][1],mod_title)#
        self.assertEqual(summary_wl_table[0][2],0)#
        self.assertEqual(summary_wl_table[0][3],0)#
        self.assertEqual(summary_wl_table[0][4],0)#
        self.assertEqual(summary_wl_table[0][5],0)#
        self.assertEqual(summary_wl_table[0][6],25)# Only assigned in last year      

        self.assertEqual(summary_wl_table[1][0],"Total")#
        self.assertEqual(summary_wl_table[1][1],"")#
        self.assertEqual(summary_wl_table[1][2],0)#
        self.assertEqual(summary_wl_table[1][3],0)#
        self.assertEqual(summary_wl_table[1][4],0)#
        self.assertEqual(summary_wl_table[1][5],0)#
        self.assertEqual(summary_wl_table[1][6],25)# Only assigned in last year     

        self.assertEqual(summary_wl_table[2][0],"tFTE")#
        self.assertEqual(summary_wl_table[2][1],"")#
        self.assertAlmostEqual(summary_wl_table[2][2],0)# No assigments in this year - lecturer is not in the workload. We put zero there
        self.assertAlmostEqual(summary_wl_table[2][3],0)# No assigments in this year - lecturer is not in the workload. We put zero there
        self.assertAlmostEqual(summary_wl_table[2][4],0)# No assigments in this year - lecturer is not in the workload. We put zero there
        self.assertAlmostEqual(summary_wl_table[2][5],0)# No assigments in this year - lecturer is not in the workload. We put zero there
        self.assertEqual(summary_wl_table[2][6],track_adjust*service_role_adjust*0.5)# No assigments in this year - lecturer is not in the workload. We put zero there

        #we test the ability of making summations here. DO another assignment to "anotehr lect"
        TeachingAssignment.objects.create(assigned_module = module_6, assigned_lecturer = anot_lect, number_of_hours = 75, workload_scenario=scenario_5)
        response = self.client.get(reverse('workload_app:lecturer_page',  kwargs={'lecturer_id': anot_lect.id}))
        self.assertEqual(response.status_code, 200) #no issues
        self.assertEqual(response.context["lec_name"], "another_lect")
        summary_wl_table = response.context["summary_wl_table_individual"]
        self.assertEqual(len(summary_wl_table), 4)#two assigments plus 2 extra lines
        self.assertEqual(len(summary_wl_table[0]), 7)#mod code, mod title, plus 5 years
        self.assertEqual(len(summary_wl_table[1]), 7)#mod code, mod title, plus 5 years
        self.assertEqual(len(summary_wl_table[2]), 7)#mod code, mod title, plus 5 years
        self.assertEqual(len(summary_wl_table[3]), 7)#mod code, mod title, plus 5 years

        self.assertEqual(summary_wl_table[0][0],mod_code)#
        self.assertEqual(summary_wl_table[0][1],mod_title)#
        self.assertEqual(summary_wl_table[0][2],0)#
        self.assertEqual(summary_wl_table[0][3],0)#
        self.assertEqual(summary_wl_table[0][4],0)#
        self.assertEqual(summary_wl_table[0][5],0)#
        self.assertEqual(summary_wl_table[0][6],25)# Only assigned in last year    

        self.assertEqual(summary_wl_table[1][0],mode_code_2)#
        self.assertEqual(summary_wl_table[1][1],mod_title_2)#
        self.assertEqual(summary_wl_table[1][2],0)#
        self.assertEqual(summary_wl_table[1][3],0)#
        self.assertEqual(summary_wl_table[1][4],0)#
        self.assertEqual(summary_wl_table[1][5],0)#
        self.assertEqual(summary_wl_table[1][6],75)# Only assigned in last year, 75 hrs    

        self.assertEqual(summary_wl_table[2][0],"Total")#
        self.assertEqual(summary_wl_table[2][1],"")#
        self.assertEqual(summary_wl_table[2][2],0)#
        self.assertEqual(summary_wl_table[2][3],0)#
        self.assertEqual(summary_wl_table[2][4],0)#
        self.assertEqual(summary_wl_table[2][5],0)#
        self.assertEqual(summary_wl_table[2][6],75+25)# Summation here

        #unchanged
        self.assertEqual(summary_wl_table[3][0],"tFTE")#
        self.assertEqual(summary_wl_table[3][1],"")#
        self.assertAlmostEqual(summary_wl_table[3][2],0)# No assigments in this year - lecturer is not in the workload. We put zero there
        self.assertAlmostEqual(summary_wl_table[3][3],0)# No assigments in this year - lecturer is not in the workload. We put zero there
        self.assertAlmostEqual(summary_wl_table[3][4],0)# No assigments in this year - lecturer is not in the workload. We put zero there
        self.assertAlmostEqual(summary_wl_table[3][5],0)# No assigments in this year - lecturer is not in the workload. We put zero there
        self.assertEqual(summary_wl_table[3][6],track_adjust*service_role_adjust*0.5)# No assigments in this year - lecturer is not in the workload. We put zero there

        #Now test the nethod to generate the chart data for lecturer 1
        response = self.client.get(reverse('workload_app:lecturer_page',  kwargs={'lecturer_id': lecturer_1.id}))
        self.assertEqual(response.status_code, 200) #no issues
        chart_data = response.context["chart_data"]
        self.assertEqual(len(chart_data["labels_temp_individual"]),5)
        self.assertEqual(len(chart_data["hrs_temp_individual_expected"]),5)
        self.assertEqual(len(chart_data["hrs_temp_individual_delivered"]),5)
        self.assertEqual(len(chart_data["hrs_expected_upper_boundary"]),5)
        self.assertEqual(len(chart_data["hrs_expected_lower_boundary"]),5)

        self.assertAlmostEqual(chart_data["hrs_temp_individual_expected"][0],25,0)#
        self.assertAlmostEqual(chart_data["hrs_temp_individual_expected"][1],35,0)#
        self.assertAlmostEqual(chart_data["hrs_temp_individual_expected"][2],45,0)#
        self.assertAlmostEqual(chart_data["hrs_temp_individual_expected"][3],95,0)#
        self.assertAlmostEqual(chart_data["hrs_temp_individual_expected"][4],0)# No assigments in last year

        self.assertAlmostEqual(chart_data["hrs_temp_individual_delivered"][0],25,0)#
        self.assertAlmostEqual(chart_data["hrs_temp_individual_delivered"][1],35,0)#
        self.assertAlmostEqual(chart_data["hrs_temp_individual_delivered"][2],45,0)#
        self.assertAlmostEqual(chart_data["hrs_temp_individual_delivered"][3],95,0)#
        self.assertAlmostEqual(chart_data["hrs_temp_individual_delivered"][4],0)# No assigments in last year

        self.assertAlmostEqual(chart_data["hrs_expected_upper_boundary"][0],25+15,0)#
        self.assertAlmostEqual(chart_data["hrs_expected_upper_boundary"][1],35+15,0)#
        self.assertAlmostEqual(chart_data["hrs_expected_upper_boundary"][2],45+15,0)#
        self.assertAlmostEqual(chart_data["hrs_expected_upper_boundary"][3],95+15,0)#
        self.assertAlmostEqual(chart_data["hrs_expected_upper_boundary"][4],0+15,0)# No assigments in last year

        self.assertAlmostEqual(chart_data["hrs_expected_lower_boundary"][0],25-15,0)#
        self.assertAlmostEqual(chart_data["hrs_expected_lower_boundary"][1],35-15,0)#
        self.assertAlmostEqual(chart_data["hrs_expected_lower_boundary"][2],45-15,0)#
        self.assertAlmostEqual(chart_data["hrs_expected_lower_boundary"][3],95-15,0)#
        self.assertAlmostEqual(chart_data["hrs_expected_lower_boundary"][4],0-15,0)# No assigments in last year    