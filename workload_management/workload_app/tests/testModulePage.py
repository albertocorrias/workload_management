from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *
from workload_app.global_constants import DEFAULT_TRACK_NAME,DEFAULT_SERVICE_ROLE_NAME
from workload_app.models import StudentLearningOutcome, ProgrammeOffered, Faculty, Department, Academicyear,WorkloadScenario,EmploymentTrack,ServiceRole,\
    ModuleType, SubProgrammeOffered, Lecturer, Module, TeachingAssignment,ModuleLearningOutcome,MLOSLOMapping,MLOPerformanceMeasure


class TestModulePage(TestCase):
    def setup_user(self):
        #The tets client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
    
    def test_module_page(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        acad_year_1 = Academicyear.objects.create(start_year=2021)
        acad_year_2 = Academicyear.objects.create(start_year=2022)
        dept_name = 'test_dept'
        first_fac = Faculty.objects.create(faculty_name = "first fac", faculty_acronym = "FRTE")
        test_dept = Department.objects.create(department_name = dept_name, department_acronym = "ACR", faculty = first_fac)
        scenario_1 = WorkloadScenario.objects.create(label="scenario_1", academic_year = acad_year_1, dept = test_dept, status = WorkloadScenario.OFFICIAL)
        track_1 = EmploymentTrack.objects.create(track_name = "track_1", track_adjustment = 2.0, is_adjunct = False)
        service_role_1 = ServiceRole.objects.create(role_name = "role_1", role_adjustment = 2.0)
        mod_type_1 = ModuleType.objects.create(type_name = "one type")
        programme_1 = ProgrammeOffered.objects.create(programme_name = "B. Eng", primary_dept = test_dept)
        programme_2 = ProgrammeOffered.objects.create(programme_name = "M. Sc", primary_dept = test_dept)
        sub_programme_1 = SubProgrammeOffered.objects.create(sub_programme_name = "specialization", main_programme = programme_1)

        #CREATE THREE LECTURERS
        lecturer_1 = Lecturer.objects.create(name="lecturer_1", fraction_appointment = 0.7, employment_track=track_1, workload_scenario = scenario_1, service_role = service_role_1)
        lecturer_2 = Lecturer.objects.create(name="lecturer_2", fraction_appointment = 1.0, employment_track=track_1, workload_scenario = scenario_1, service_role = service_role_1)
        lecturer_3 = Lecturer.objects.create(name="lecturer_3", fraction_appointment = 0.5, employment_track=track_1, workload_scenario = scenario_1, service_role = service_role_1)
        #Create three modules. Module two has associated programme. Module 3 has two programmes and also one sub-programme
        module_1 = Module.objects.create(module_code = "BN101", module_title="First module", scenario_ref=scenario_1, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1)
        module_2 = Module.objects.create(module_code = "BN201", module_title="Second module", scenario_ref=scenario_1, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1,\
                                        primary_programme = programme_2)
        module_3 = Module.objects.create(module_code = "BN301", module_title="Third module", scenario_ref=scenario_1, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1,\
                                        primary_programme = programme_1, secondary_programme = programme_2, sub_programme = sub_programme_1)
        #Do some assignments
        #2 lecturers for module 1
        TeachingAssignment.objects.create(assigned_module = module_1, assigned_lecturer = lecturer_1, number_of_hours = 25, workload_scenario=scenario_1)
        TeachingAssignment.objects.create(assigned_module = module_1, assigned_lecturer = lecturer_2, number_of_hours = 55, workload_scenario=scenario_1)
        #One for module 2
        TeachingAssignment.objects.create(assigned_module = module_2, assigned_lecturer = lecturer_3, number_of_hours = 100, workload_scenario=scenario_1)
        #Two for module 3
        TeachingAssignment.objects.create(assigned_module = module_3, assigned_lecturer = lecturer_1, number_of_hours = 35, workload_scenario=scenario_1)
        TeachingAssignment.objects.create(assigned_module = module_3, assigned_lecturer = lecturer_3, number_of_hours = 45, workload_scenario=scenario_1)
        #Now call module page
        response = self.client.get(reverse('workload_app:module',  kwargs={'module_code': "BN301"}))
        self.assertEqual(response.status_code, 200) #no issues
        self.assertEqual(response.context["module_title"], "Third module")
        self.assertEqual(response.context["module_code"], "BN301")
        self.assertEqual(len(response.context["module_table"]),1)#Content of the table is tested in the helper method!
        self.assertEqual(len(response.context["mlo_list"]), 0) #No MLO yet (see test below)
        #Cover the case of non-existent module code
        response = self.client.get(reverse('workload_app:module',  kwargs={'module_code': "BN301TT"}))
        self.assertEqual(response.status_code, 200) #no issues, simply the error page is shown
        self.assertContains(response,"There are no modules")

    def test_add_remove_mlo(self):
        
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        acad_year_1 = Academicyear.objects.create(start_year=2021)
        dept_name = 'test_dept'
        mod_type_1 = ModuleType.objects.create(type_name = "one type")
        first_fac = Faculty.objects.create(faculty_name = "first fac", faculty_acronym = "FRTE")
        test_dept = Department.objects.create(department_name = dept_name, department_acronym = "ACR", faculty = first_fac)
        scenario_1 = WorkloadScenario.objects.create(label="scenario_1", academic_year = acad_year_1, dept = test_dept, status = WorkloadScenario.OFFICIAL)
        mod_code = "BN101"
        module_1 = Module.objects.create(module_code = mod_code, module_title="First module", scenario_ref=scenario_1, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1)

        #Test the get without any MLO
        response = self.client.get(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(len(response.context["mlo_list"]), 0) #
        self.assertEqual(len(response.context["slo_list"]), 0) #
        
        #Create a MLO
        self.assertEqual(ModuleLearningOutcome.objects.all().count(),0)
        descr = "MLO fulld escription"
        short_desc = "MLo short"
        response = self.client.post(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}), \
            {"mlo_description" : descr,\
            "mlo_short_description" : short_desc, "fresh_record" : True, "mod_code" : module_1.module_code})
        self.assertEqual(response.status_code, 302) #re-direct triggered
        self.assertEqual(ModuleLearningOutcome.objects.all().count(),1)
        self.assertEqual(ModuleLearningOutcome.objects.filter(mlo_description = descr).count(),1)
        self.assertEqual(ModuleLearningOutcome.objects.filter(mlo_short_description = short_desc).count(),1)

        #Try editing it
        mlo_obj = ModuleLearningOutcome.objects.filter(mlo_description = descr).get()
        new_description = "NEW description"
        response = self.client.post(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}), \
            {"mlo_description" : new_description,\
            "mlo_short_description" : short_desc, "fresh_record" : False, "mod_code" : module_1.module_code, "mlo_id" : mlo_obj.id})
        
        self.assertEqual(response.status_code, 302) #re-direct triggered
        self.assertEqual(ModuleLearningOutcome.objects.all().count(),1)
        self.assertEqual(ModuleLearningOutcome.objects.filter(mlo_description = descr).count(),0)#Not there any more
        self.assertEqual(ModuleLearningOutcome.objects.filter(mlo_description = new_description).count(),1)#New description
        self.assertEqual(ModuleLearningOutcome.objects.filter(mlo_short_description = short_desc).count(),1)

        #Test the get directly, with one MLO
        response = self.client.get(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(len(response.context["mlo_list"]), 1) #
        self.assertEqual(response.context["mlo_list"][0]["mlo_desc"], new_description)
        self.assertEqual(response.context["mlo_list"][0]["mlo_short_desc"], short_desc)
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping_form"], None)
        self.assertEqual(len(response.context["mlo_list"][0]["slo_mapping"]), 0) #
        self.assertEqual(len(response.context["slo_list"]), 0) #
        
        #Create one programme
        new_prog = ProgrammeOffered.objects.create(programme_name="new_prog", primary_dept=test_dept)
        #create two SLOs for this programme
        slo_1 = StudentLearningOutcome.objects.create(slo_description="slo_1", slo_short_description="short_1", programme = new_prog)
        slo_2 = StudentLearningOutcome.objects.create(slo_description="slo_2", slo_short_description="short_2", programme = new_prog)
        self.assertEqual(StudentLearningOutcome.objects.all().count(),2)
        self.assertEqual(ProgrammeOffered.objects.all().count(),1)
        #Now make sure the module 1 is associated with the new programme
        module_1.primary_programme=new_prog
        module_1.save()
        #Call the get again
        response = self.client.get(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(MLOSLOMapping.objects.all().count(),2)#one MLO mapped to 2 SLO created by the view
        self.assertEqual(len(response.context["mlo_list"]), 1) #
        self.assertEqual(response.context["mlo_list"][0]["mlo_desc"], new_description)
        self.assertEqual(response.context["mlo_list"][0]["mlo_short_desc"], short_desc)
        self.assertNotEqual(response.context["mlo_list"][0]["slo_mapping_form"], None)
        self.assertEqual(len(response.context["mlo_list"][0]["slo_mapping"]), 2) #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][0]["slo_description"], "slo_1") #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][1]["slo_description"], "slo_2") #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][0]["slo_short_description"], "short_1") #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][1]["slo_short_description"], "short_2") #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][0]["mapping_strength"], 0) #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][1]["mapping_strength"], 0) #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][0]["mapping_icon"], "circle.svg") #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][1]["mapping_icon"], "circle.svg") #
        self.assertEqual(len(response.context["slo_list"]), 2) #
        self.assertEqual(response.context["slo_list"][0]["slo_description"], "slo_1") #
        self.assertEqual(response.context["slo_list"][1]["slo_description"], "slo_2") #
        
        #Try to edit the strength of one MLO-SLO mapping
        response = self.client.post(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}), \
            {"prog_id" : new_prog.id, "mlo_slo_mapping_strength"+str(slo_1.id) : 3, "mlo_id" : mlo_obj.id, "slo_id" : slo_1.id, \
                                      "mlo_slo_mapping_strength"+str(slo_2.id) : 0, "mlo_id" : mlo_obj.id, "slo_id" : slo_2.id,})
        self.assertEqual(response.status_code, 302) #No issues, re-direct

        #Call the get again
        response = self.client.get(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][0]["mapping_strength"], 3) #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][1]["mapping_strength"], 0) #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][0]["mapping_icon"], "circle-fill.svg") #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][1]["mapping_icon"], "circle.svg") #

        #Add another MLO
        new_MLO_descr = "NEW MLO fulld escription"
        new_MLO_short_desc = "NEW MLo short"
        response = self.client.post(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}), \
            {"mlo_description" : new_MLO_descr,\
            "mlo_short_description" : new_MLO_short_desc, "fresh_record" : True, "mod_code" : module_1.module_code})
        self.assertEqual(response.status_code, 302) #re-direct triggered
        self.assertEqual(ModuleLearningOutcome.objects.all().count(),2)
        self.assertEqual(ModuleLearningOutcome.objects.filter(mlo_description = new_description).count(),1)
        self.assertEqual(ModuleLearningOutcome.objects.filter(mlo_short_description = short_desc).count(),1)
        self.assertEqual(ModuleLearningOutcome.objects.filter(mlo_description = new_MLO_descr).count(),1)
        self.assertEqual(ModuleLearningOutcome.objects.filter(mlo_short_description = new_MLO_short_desc).count(),1)
        new_mlo_obj = ModuleLearningOutcome.objects.filter(mlo_description = new_MLO_descr).get()
        #Get again
        response = self.client.get(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(len(response.context["mlo_list"]), 2) #
        self.assertEqual(MLOSLOMapping.objects.all().count(),4)#2 mlo mapped to two SLO
        #CHECK FIRST MLO
        self.assertEqual(response.context["mlo_list"][0]["mlo_desc"], new_MLO_descr)
        self.assertEqual(response.context["mlo_list"][0]["mlo_short_desc"], new_MLO_short_desc)
        self.assertNotEqual(response.context["mlo_list"][0]["slo_mapping_form"], None)
        self.assertEqual(len(response.context["mlo_list"][0]["slo_mapping"]), 2) #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][0]["slo_description"], "slo_1") #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][1]["slo_description"], "slo_2") #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][0]["slo_short_description"], "short_1") #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][1]["slo_short_description"], "short_2") #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][0]["mapping_strength"], 0) #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][1]["mapping_strength"], 0) #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][0]["mapping_icon"], "circle.svg") #
        self.assertEqual(response.context["mlo_list"][0]["slo_mapping"][1]["mapping_icon"], "circle.svg") #
        self.assertEqual(len(response.context["slo_list"]), 2) #
        self.assertEqual(response.context["slo_list"][0]["slo_description"], "slo_1") #
        self.assertEqual(response.context["slo_list"][1]["slo_description"], "slo_2") #
        #CHECK SECOND MLO (USED TO BE FIRST)
        self.assertEqual(response.context["mlo_list"][1]["mlo_desc"], new_description)
        self.assertEqual(response.context["mlo_list"][1]["mlo_short_desc"], short_desc)
        self.assertNotEqual(response.context["mlo_list"][1]["slo_mapping_form"], None)
        self.assertEqual(len(response.context["mlo_list"][1]["slo_mapping"]), 2) #
        self.assertEqual(response.context["mlo_list"][1]["slo_mapping"][0]["slo_description"], "slo_1") #
        self.assertEqual(response.context["mlo_list"][1]["slo_mapping"][1]["slo_description"], "slo_2") #
        self.assertEqual(response.context["mlo_list"][1]["slo_mapping"][0]["slo_short_description"], "short_1") #
        self.assertEqual(response.context["mlo_list"][1]["slo_mapping"][1]["slo_short_description"], "short_2") #
        self.assertEqual(response.context["mlo_list"][1]["slo_mapping"][0]["mapping_strength"], 3) #
        self.assertEqual(response.context["mlo_list"][1]["slo_mapping"][1]["mapping_strength"], 0) #
        self.assertEqual(response.context["mlo_list"][1]["slo_mapping"][0]["mapping_icon"], "circle-fill.svg") #
        self.assertEqual(response.context["mlo_list"][1]["slo_mapping"][1]["mapping_icon"], "circle.svg") #
        self.assertEqual(len(response.context["slo_list"]), 2) #
        self.assertEqual(response.context["slo_list"][0]["slo_description"], "slo_1") #
        self.assertEqual(response.context["slo_list"][1]["slo_description"], "slo_2") #

        #Now remove both MLOs
        response = self.client.post(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}), \
            {"select_mlo_to_remove" : mlo_obj.id})
        self.assertEqual(response.status_code, 302) #re-direct triggered
        self.assertEqual(ModuleLearningOutcome.objects.all().count(),1)
        #Delete the other one as well
        response = self.client.post(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}), \
            {"select_mlo_to_remove" : new_mlo_obj.id})
        self.assertEqual(response.status_code, 302) #re-direct triggered
        self.assertEqual(ModuleLearningOutcome.objects.all().count(),0)

        #Get again
        response = self.client.get(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(len(response.context["mlo_list"]), 0) #
        self.assertEqual(MLOSLOMapping.objects.all().count(),0)#The "cascade" delete policy should do the job

    def test_mlo_measures(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        acad_year_1 = Academicyear.objects.create(start_year=2021)
        dept_name = 'test_dept'
        mod_type_1 = ModuleType.objects.create(type_name = "one type")
        first_fac = Faculty.objects.create(faculty_name = "first fac", faculty_acronym = "FRTE")
        test_dept = Department.objects.create(department_name = dept_name, department_acronym = "ACR", faculty = first_fac)
        scenario_1 = WorkloadScenario.objects.create(label="scenario_1", academic_year = acad_year_1, dept = test_dept, status = WorkloadScenario.OFFICIAL)
        mod_code = "BN101"
        module_1 = Module.objects.create(module_code = mod_code, module_title="First module", scenario_ref=scenario_1, total_hours=100, module_type = mod_type_1, semester_offered = Module.SEM_1)
        #Create two MLOs
        self.assertEqual(ModuleLearningOutcome.objects.all().count(),0)
        descr = "MLO 1 full description"
        short_desc = "MLO 1 short"
        response = self.client.post(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}), \
            {"mlo_description" : descr,\
            "mlo_short_description" : short_desc, "fresh_record" : True, "mod_code" : module_1.module_code})
        self.assertEqual(response.status_code, 302) #re-direct triggered
        self.assertEqual(ModuleLearningOutcome.objects.all().count(),1)
        self.assertEqual(ModuleLearningOutcome.objects.filter(mlo_description = descr).count(),1)
        self.assertEqual(ModuleLearningOutcome.objects.filter(mlo_short_description = short_desc).count(),1)

        descr_2 = "MLO 2 full description"
        short_desc_2 = "MLO 2 short"
        response = self.client.post(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}), \
            {"mlo_description" : descr_2,\
            "mlo_short_description" : short_desc_2, "fresh_record" : True, "mod_code" : module_1.module_code})
        self.assertEqual(response.status_code, 302) #re-direct triggered
        
        response = self.client.get(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(ModuleLearningOutcome.objects.all().count(),2)
        self.assertEqual(ModuleLearningOutcome.objects.filter(mlo_description = descr).count(),1)
        self.assertEqual(ModuleLearningOutcome.objects.filter(mlo_short_description = short_desc).count(),1)
        self.assertEqual(ModuleLearningOutcome.objects.filter(mlo_description = descr_2).count(),1)
        self.assertEqual(ModuleLearningOutcome.objects.filter(mlo_short_description = short_desc_2).count(),1)

        mlo_1_obj = ModuleLearningOutcome.objects.filter(mlo_description = descr).get()
        mlo_2_obj = ModuleLearningOutcome.objects.filter(mlo_description = descr_2).get()
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),0)
        table = response.context["mlo_measure_table"]
        self.assertEqual(len(table),0)
        #add one MLO direct measure
        measure_desc = "hello this is a test"
        response = self.client.post(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}), \
            {"academic_year" : acad_year_1.id,
            "measure_description" : measure_desc,
            "percentage_score" : 78,
            "mlo_mapped_1" : mlo_1_obj.id})
        self.assertEqual(response.status_code, 302) #No issues, re-direct

        #Call the get again
        response = self.client.get(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(description = measure_desc).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(percentage_score = 78).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(associated_mlo = mlo_1_obj).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(associated_mlo = mlo_2_obj).count(),0)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(secondary_associated_mlo__isnull = True).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(tertiary_associated_mlo__isnull = True).count(),1)
        #Test the table passed to the template
        table = response.context["mlo_measure_table"]
        self.assertEqual(len(table),1)
        self.assertEqual(table[0]["description"],measure_desc)
        self.assertEqual(table[0]["mlos_mapped"],short_desc)
        self.assertEqual(table[0]["score"],78)

        measure_desc_2 = "hello this is another test"
        response = self.client.post(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}), \
            {"academic_year" : acad_year_1.id,
            "measure_description" : measure_desc_2,
            "percentage_score" : 8,
            "mlo_mapped_1" : mlo_2_obj.id,
            "mlo_mapped_2" : mlo_1_obj.id})
        self.assertEqual(response.status_code, 302) #No issues, re-direct
        #Call the get again
        response = self.client.get(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),2)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(description = measure_desc).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(description = measure_desc_2).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(percentage_score = 78).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(percentage_score = 8).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(associated_mlo = mlo_1_obj).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(associated_mlo = mlo_2_obj).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(secondary_associated_mlo = mlo_1_obj).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(secondary_associated_mlo = mlo_2_obj).count(),0)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(secondary_associated_mlo__isnull = True).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(tertiary_associated_mlo__isnull = True).count(),2)

        #Test the table passed to the template
        table = response.context["mlo_measure_table"]
        self.assertEqual(len(table),2)
        self.assertEqual(table[0]["description"],measure_desc)
        self.assertEqual(table[0]["mlos_mapped"],short_desc)
        self.assertEqual(table[0]["score"],78)
        self.assertEqual(table[1]["description"],measure_desc_2)
        self.assertEqual(table[1]["mlos_mapped"],short_desc_2 + ", " + short_desc)
        self.assertEqual(table[1]["score"],8)

        #Remove the second measure
        meas = MLOPerformanceMeasure.objects.filter(description = measure_desc_2).get()
        response = self.client.post(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}), \
            {"Select_MLO_measure_to_remove" : meas.id})
        self.assertEqual(response.status_code, 302) #No issues, re-direct
        #Call the get again
        response = self.client.get(reverse('workload_app:module', kwargs={'module_code': module_1.module_code}))
        self.assertEqual(response.status_code, 200) #No issues

        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(description = measure_desc).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(percentage_score = 78).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(associated_mlo = mlo_1_obj).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(associated_mlo = mlo_2_obj).count(),0)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(secondary_associated_mlo__isnull = True).count(),1)
        self.assertEqual(MLOPerformanceMeasure.objects.filter(tertiary_associated_mlo__isnull = True).count(),1)
        #Test the table passed to the template
        table = response.context["mlo_measure_table"]
        self.assertEqual(len(table),1)
        self.assertEqual(table[0]["description"],measure_desc)
        self.assertEqual(table[0]["mlos_mapped"],short_desc)
        self.assertEqual(table[0]["score"],78)