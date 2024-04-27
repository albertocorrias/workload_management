import datetime
from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *
from workload_app.global_constants import DEFAULT_TRACK_NAME,DEFAULT_SERVICE_ROLE_NAME
from workload_app.models import StudentLearningOutcome, ProgrammeOffered, Faculty, Department, ModuleType, Module,WorkloadScenario, Academicyear,\
                                ModuleLearningOutcome,MLOSLOMapping,MLOPerformanceMeasure,Survey,SurveyQuestionResponse
from workload_app.helper_methods_accreditation import CalculateTableForSLOSurveys,CalculateTableForMLOSurveys, CalculateTableForMLODirectMeasures,\
                                                        CalculateTableForOverallSLOMapping,DetermineIconBasedOnStrength, CalculateMLOSLOMappingTable
from workload_app.helper_methods_survey import CalulatePositiveResponsesFractionForQuestion

class TestAccreditationReport(TestCase):
    def setup_user(self):
        #The tets client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
    
    
    def test_report(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        #create 4 academic years
        start_year = 2012
        acad_year_1 = Academicyear.objects.create(start_year=start_year)
        acad_year_2 = Academicyear.objects.create(start_year=start_year+1)
        acad_year_3 = Academicyear.objects.create(start_year=start_year+2)
        acad_year_4 = Academicyear.objects.create(start_year=start_year+3)
        #Create 4 worklaod scenarios
        scenario_1 = WorkloadScenario.objects.create(label='a workload 1', academic_year=acad_year_1)
        scenario_2 = WorkloadScenario.objects.create(label='a workload 2', academic_year=acad_year_2)
        scenario_3 = WorkloadScenario.objects.create(label='a workload 3', academic_year=acad_year_3)
        scenario_4 = WorkloadScenario.objects.create(label='a workload 4', academic_year=acad_year_4)

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        new_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        prog_to_accredit = ProgrammeOffered.objects.create(programme_name="test_prog", primary_dept = new_dept)

        slo_1 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_1', \
                                                      slo_short_description = 'slo_1', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'a',
                                                      programme = prog_to_accredit)

        slo_2 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_2', \
                                                      slo_short_description = 'slo_2', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'b',
                                                      programme = prog_to_accredit)
        slo_3 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_3', \
                                                      slo_short_description = 'slo_3', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'c',
                                                      programme = prog_to_accredit)
        
        mod_code_1 = 'AA101'
        mod_code_2 = 'AA201'
        mod_code_3 = 'AA301'
        mod_code_4 = 'AA401'
        #Module one present in 4 scenarios
        mod_1_1 = Module.objects.create(module_code = mod_code_1, module_title = mod_code_1+'-title', scenario_ref=scenario_1,primary_programme = prog_to_accredit)
        mod_1_2 = Module.objects.create(module_code = mod_code_1, module_title = mod_code_1+'-title', scenario_ref=scenario_2,primary_programme = prog_to_accredit)
        mod_1_3 = Module.objects.create(module_code = mod_code_1, module_title = mod_code_1+'-title', scenario_ref=scenario_3,primary_programme = prog_to_accredit)
        mod_1_4 = Module.objects.create(module_code = mod_code_1, module_title = mod_code_1+'-title', scenario_ref=scenario_4,primary_programme = prog_to_accredit)
        
        #Module two present in 4 scenarios
        mod_2_1 = Module.objects.create(module_code = mod_code_2, module_title = mod_code_2+'-title', scenario_ref=scenario_1,primary_programme = prog_to_accredit)
        mod_2_2 = Module.objects.create(module_code = mod_code_2, module_title = mod_code_2+'-title', scenario_ref=scenario_2,primary_programme = prog_to_accredit)
        mod_2_3 = Module.objects.create(module_code = mod_code_2, module_title = mod_code_2+'-title', scenario_ref=scenario_3,primary_programme = prog_to_accredit)
        mod_2_4 = Module.objects.create(module_code = mod_code_2, module_title = mod_code_2+'-title', scenario_ref=scenario_4,primary_programme = prog_to_accredit)

        #Module 3 present in 4 scenarios
        mod_3_1 = Module.objects.create(module_code = mod_code_3, module_title = mod_code_3+'-title', scenario_ref=scenario_1,primary_programme = prog_to_accredit)
        mod_3_2 = Module.objects.create(module_code = mod_code_3, module_title = mod_code_3+'-title', scenario_ref=scenario_2,primary_programme = prog_to_accredit)
        mod_3_3 = Module.objects.create(module_code = mod_code_3, module_title = mod_code_3+'-title', scenario_ref=scenario_3,primary_programme = prog_to_accredit)
        mod_3_4 = Module.objects.create(module_code = mod_code_3, module_title = mod_code_3+'-title', scenario_ref=scenario_4,primary_programme = prog_to_accredit)

        #Module 4 present in 4 scenarios
        mod_4_1 = Module.objects.create(module_code = mod_code_4, module_title = mod_code_4+'-title', scenario_ref=scenario_1,primary_programme = prog_to_accredit)
        mod_4_2 = Module.objects.create(module_code = mod_code_4, module_title = mod_code_4+'-title', scenario_ref=scenario_2,primary_programme = prog_to_accredit)
        mod_4_3 = Module.objects.create(module_code = mod_code_4, module_title = mod_code_4+'-title', scenario_ref=scenario_3,primary_programme = prog_to_accredit)
        mod_4_4 = Module.objects.create(module_code = mod_code_4, module_title = mod_code_4+'-title', scenario_ref=scenario_4,primary_programme = prog_to_accredit)

        self.assertEqual(Module.objects.all().count(),16)

        #Create MLOS
        #Module code 1 has 4 mlos
        mlo_1_1 = ModuleLearningOutcome.objects.create(mlo_description = "MLO_1-mod 1", mlo_short_description="short-MLO_1-mod 1", module_code = mod_code_1)
        mlo_1_2 = ModuleLearningOutcome.objects.create(mlo_description = "MLO_2-mod 1", mlo_short_description="short-MLO_2-mod 1", module_code = mod_code_1)
        mlo_1_3 = ModuleLearningOutcome.objects.create(mlo_description = "MLO_3-mod 1", mlo_short_description="short-MLO_3-mod 1", module_code = mod_code_1)
        mlo_1_4 = ModuleLearningOutcome.objects.create(mlo_description = "MLO_4-mod 1", mlo_short_description="short-MLO_4-mod 1", module_code = mod_code_1)
        #Module code 2 has 3 mlos
        mlo_2_1 = ModuleLearningOutcome.objects.create(mlo_description = "MLO_1-mod 2", mlo_short_description="short-MLO_1-mod 2", module_code = mod_code_2)
        mlo_2_2 = ModuleLearningOutcome.objects.create(mlo_description = "MLO_2-mod 2", mlo_short_description="short-MLO_2-mod 2", module_code = mod_code_2)
        mlo_2_3 = ModuleLearningOutcome.objects.create(mlo_description = "MLO_3-mod 2", mlo_short_description="short-MLO_3-mod 2", module_code = mod_code_2)
        #Module code 3 has 3 mlos
        mlo_3_1 = ModuleLearningOutcome.objects.create(mlo_description = "MLO_1-mod 3", mlo_short_description="short-MLO_1-mod 3", module_code = mod_code_3)
        mlo_3_2 = ModuleLearningOutcome.objects.create(mlo_description = "MLO_2-mod 3", mlo_short_description="short-MLO_2-mod 3", module_code = mod_code_3)
        mlo_3_3 = ModuleLearningOutcome.objects.create(mlo_description = "MLO_3-mod 3", mlo_short_description="short-MLO_3-mod 3", module_code = mod_code_3)
        #Module code 4 has only one MLO
        mlo_4_1 = ModuleLearningOutcome.objects.create(mlo_description = "MLO_1-mod 4", mlo_short_description="short-MLO_1-mod 4", module_code = mod_code_4)

        self.assertEqual(ModuleLearningOutcome.objects.all().count(),11)

        #Now create the mappings
        #It will look like this
        #                           SLO 1               SLO 2           SLO 3
        # MOD 1 - MLO 1                3                   3               1
        # MOD 1 - MLO 2                2
        # MOD 1 - MLO 3                1                                   2
        # MOD 1 - MLO 4                                    2
        #
        # MOD 2 - MLO 1                2                   3
        # MOD 2 - MLO 2                                                    1
        # MOD 2 - MLO 3                3
        #
        # MOD 3 - MLO 1                2                                   3
        # MOD 3 - MLO 2                                                    3
        # MOD 3 - MLO 3 (UNMAPPED)
        #
        # MOD 4 - MLO 1                                    1

        #MLO 1 of module 1 maps as follows
        map_mod_1_mlo_1_slo_1 = MLOSLOMapping.objects.create(mlo = mlo_1_1, slo=slo_1, strength = 3)
        map_mod_1_mlo_1_slo_2 = MLOSLOMapping.objects.create(mlo = mlo_1_1, slo=slo_2, strength = 3)
        map_mod_1_mlo_1_slo_3 = MLOSLOMapping.objects.create(mlo = mlo_1_1, slo=slo_3, strength = 1)
        #MLO 2 of module 1 maps as follows
        map_mod_1_mlo_2_slo_1 = MLOSLOMapping.objects.create(mlo = mlo_1_2, slo=slo_1, strength = 2)
        #MLO 3 of module 1 maps as follows
        map_mod_1_mlo_3_slo_1 = MLOSLOMapping.objects.create(mlo = mlo_1_3, slo=slo_1, strength = 1)
        map_mod_1_mlo_3_slo_3 = MLOSLOMapping.objects.create(mlo = mlo_1_3, slo=slo_3, strength = 2)
        #The MLO 4 of module 1  maps to SLO 2
        map_mod_1_mlo_4_slo_2 = MLOSLOMapping.objects.create(mlo = mlo_1_4, slo=slo_2, strength = 2)

        #MLO 1 of module 2 maps as follows
        map_mod_2_mlo_1_slo_1 = MLOSLOMapping.objects.create(mlo = mlo_2_1, slo=slo_1, strength = 2)
        map_mod_2_mlo_1_slo_2 = MLOSLOMapping.objects.create(mlo = mlo_2_1, slo=slo_2, strength = 3)
        #MLO 2 of module 2 maps as follows
        map_mod_2_mlo_2_slo_3 = MLOSLOMapping.objects.create(mlo = mlo_2_2, slo=slo_3, strength = 1)
        #MLO 3 of module 2 maps as follows
        map_mod_2_mlo_3_slo_1 = MLOSLOMapping.objects.create(mlo = mlo_2_3, slo=slo_1, strength = 3)

        #MLO 1 of module 3 maps as follows
        map_mod_3_mlo_1_slo_1 = MLOSLOMapping.objects.create(mlo = mlo_3_1, slo=slo_1, strength = 2)
        map_mod_3_mlo_1_slo_3 = MLOSLOMapping.objects.create(mlo = mlo_3_1, slo=slo_3, strength = 3)
        #MLO 2 of module 3 maps as follows
        map_mod_3_mlo_2_slo_3 = MLOSLOMapping.objects.create(mlo = mlo_3_2, slo=slo_3, strength = 3)
        #MLO 3 of module 3 is unmapped

        #MLO 1 of module 4 maps only to slo 2
        map_mod_4_mlo_1_slo_2 = MLOSLOMapping.objects.create(mlo = mlo_4_1, slo=slo_2, strength = 1)
        self.assertEqual(MLOSLOMapping.objects.all().count(),15)

        #Start testing the direct measures
        measure_1 = MLOPerformanceMeasure.objects.create(description = 'test 1', academic_year = acad_year_2, associated_mlo = mlo_1_1,percentage_score=75)
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),1)
        table_slo_1 = CalculateTableForMLODirectMeasures(slo_id = slo_1.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_1), 2)#one measure plus the totals row
        self.assertEqual(len(table_slo_1[0]), 5)
        self.assertEqual(len(table_slo_1[1]), 5)
        self.assertEqual(table_slo_1[0][0], mod_code_1)
        self.assertEqual(table_slo_1[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_1[0][2], 75)#75 measure in second academic year
        self.assertEqual(table_slo_1[0][3], '')#no measure in third academic year
        self.assertEqual(table_slo_1[0][4], '')#no measure in last academic year
        self.assertEqual(table_slo_1[1][0], 'Weighted average')
        self.assertEqual(table_slo_1[1][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_1[1][2], 75.0)#75 measure in second academic year, total is 75
        self.assertEqual(table_slo_1[1][3], 0)#no measure in third academic year -> totals row is zero
        self.assertEqual(table_slo_1[1][4], 0)#no measure in last academic year -> totals row is zero
        
        table_slo_2 = CalculateTableForMLODirectMeasures(slo_id = slo_2.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_2), 2)#one measure plus the totals row
        self.assertEqual(len(table_slo_2[0]), 5)
        self.assertEqual(len(table_slo_2[1]), 5)
        self.assertEqual(table_slo_2[0][0], mod_code_1)
        self.assertEqual(table_slo_2[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_2[0][2], 75)#75 measure in second academic year
        self.assertEqual(table_slo_2[0][3], '')#no measure in third academic year
        self.assertEqual(table_slo_2[0][4], '')#no measure in last academic year
        self.assertEqual(table_slo_2[1][0], 'Weighted average')
        self.assertEqual(table_slo_2[1][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_2[1][2], 75.0)#75 measure in second academic year, total is 75
        self.assertEqual(table_slo_2[1][3], 0)#no measure in third academic year -> totals row is zero
        self.assertEqual(table_slo_2[1][4], 0)#no measure in last academic year -> totals row is zero

        table_slo_3 = CalculateTableForMLODirectMeasures(slo_id = slo_3.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_3), 2)#one measure plus the totals row
        self.assertEqual(len(table_slo_3[0]), 5)
        self.assertEqual(len(table_slo_3[1]), 5)
        self.assertEqual(table_slo_3[0][0], mod_code_1)
        self.assertEqual(table_slo_3[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_3[0][2], 75)#75 measure in second academic year
        self.assertEqual(table_slo_3[0][3], '')#no measure in third academic year
        self.assertEqual(table_slo_3[0][4], '')#no measure in last academic year
        self.assertEqual(table_slo_3[1][0], 'Weighted average')
        self.assertEqual(table_slo_3[1][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_3[1][2], 75.0)#75 measure in second academic year, total is 75
        self.assertEqual(table_slo_3[1][3], 0)#no measure in third academic year -> totals row is zero
        self.assertEqual(table_slo_3[1][4], 0)#no measure in last academic year -> totals row is zero

        #Now add another measure for MLO 2, still module 1. This is mapped to SLO 1 (strength 2). So only the table for SLO1 should change - SAME academic year
        measure_2 = MLOPerformanceMeasure.objects.create(description = 'test 2', academic_year = acad_year_2, associated_mlo = mlo_1_2,percentage_score=45)
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),2)
        table_slo_1 = CalculateTableForMLODirectMeasures(slo_id = slo_1.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_1), 2)#one measure plus the totals row
        self.assertEqual(len(table_slo_1[0]), 5)
        self.assertEqual(len(table_slo_1[1]), 5)
        self.assertEqual(table_slo_1[0][0], mod_code_1)
        self.assertEqual(table_slo_1[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_1[0][2], (75*3+45*2)/5)#75 measure in second academic year, plus 45 measure ->Weighted average
        self.assertEqual(table_slo_1[0][3], '')#no measure in third academic year
        self.assertEqual(table_slo_1[0][4], '')#no measure in last academic year
        self.assertEqual(table_slo_1[1][0], 'Weighted average')
        self.assertEqual(table_slo_1[1][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_1[1][2], (75*3+45*2)/5)#75 measure in second academic year, plus 45 measure ->Weighted average
        self.assertEqual(table_slo_1[1][3], 0)#no measure in third academic year -> totals row is zero
        self.assertEqual(table_slo_1[1][4], 0)#no measure in last academic year -> totals row is zero
        
        table_slo_2 = CalculateTableForMLODirectMeasures(slo_id = slo_2.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_2), 2)#one measure plus the totals row
        self.assertEqual(len(table_slo_2[0]), 5)
        self.assertEqual(len(table_slo_2[1]), 5)
        self.assertEqual(table_slo_2[0][0], mod_code_1)
        self.assertEqual(table_slo_2[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_2[0][2], 75)#75 measure in second academic year
        self.assertEqual(table_slo_2[0][3], '')#no measure in third academic year
        self.assertEqual(table_slo_2[0][4], '')#no measure in last academic year
        self.assertEqual(table_slo_2[1][0], 'Weighted average')
        self.assertEqual(table_slo_2[1][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_2[1][2], 75.0)#75 measure in second academic year, total is 75
        self.assertEqual(table_slo_2[1][3], 0)#no measure in third academic year -> totals row is zero
        self.assertEqual(table_slo_2[1][4], 0)#no measure in last academic year -> totals row is zero

        table_slo_3 = CalculateTableForMLODirectMeasures(slo_id = slo_3.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_3), 2)#one measure plus the totals row
        self.assertEqual(len(table_slo_3[0]), 5)
        self.assertEqual(len(table_slo_3[1]), 5)
        self.assertEqual(table_slo_3[0][0], mod_code_1)
        self.assertEqual(table_slo_3[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_3[0][2], 75)#75 measure in second academic year
        self.assertEqual(table_slo_3[0][3], '')#no measure in third academic year
        self.assertEqual(table_slo_3[0][4], '')#no measure in last academic year
        self.assertEqual(table_slo_3[1][0], 'Weighted average')
        self.assertEqual(table_slo_3[1][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_3[1][2], 75.0)#75 measure in second academic year, total is 75
        self.assertEqual(table_slo_3[1][3], 0)#no measure in third academic year -> totals row is zero
        self.assertEqual(table_slo_3[1][4], 0)#no measure in last academic year -> totals row is zero

        #Now add another measure for MLO 1, for module 2. 
        # This is mapped to SLO 1 (strength 2) and SLO 2 (strength 3).Different academic academic year
        # Tables for SLO1 and SLO2 should change. Tbale for SLO3 should remain unaltered
        measure_3 = MLOPerformanceMeasure.objects.create(description = 'test 3', academic_year = acad_year_3, associated_mlo = mlo_2_1,percentage_score=65)
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),3)
        table_slo_1 = CalculateTableForMLODirectMeasures(slo_id = slo_1.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_1), 3)#measures for Module 1 and module 2 plus the totals row
        self.assertEqual(len(table_slo_1[0]), 5)
        self.assertEqual(len(table_slo_1[1]), 5)
        self.assertEqual(len(table_slo_1[2]), 5)
        self.assertEqual(table_slo_1[0][0], mod_code_1)
        self.assertEqual(table_slo_1[0][1], '')#no measure in first academic year for module 1
        self.assertAlmostEqual(table_slo_1[0][2], (75*3+45*2)/5)#75 measure in second academic year, plus 45 measure ->Weighted average
        self.assertEqual(table_slo_1[0][3], '')#no measure in third academic year
        self.assertEqual(table_slo_1[0][4], '')#no measure in last academic year
        self.assertEqual(table_slo_1[1][0], mod_code_2)
        self.assertEqual(table_slo_1[1][1], '')#no measure in first academic year for module 2
        self.assertEqual(table_slo_1[1][2], '')#no measure in second academic year for module 2
        self.assertAlmostEqual(table_slo_1[1][3], 65)#65 measure in 3rd academic year
        self.assertEqual(table_slo_1[1][4], '')#no measure in last academic year for module 2
        self.assertEqual(table_slo_1[2][0], 'Weighted average')
        self.assertEqual(table_slo_1[2][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_1[2][2], (75*3+45*2)/5)#75 measure in second academic year, plus 45 measure ->Weighted average
        self.assertAlmostEqual(table_slo_1[2][3], 65)#one measure in third academic year (module 2, MLO 1)
        self.assertEqual(table_slo_1[2][4], 0)#no measure in last academic year -> totals row is zero

        table_slo_2 = CalculateTableForMLODirectMeasures(slo_id = slo_2.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_2), 3)#MOD 1, MOS 2 plus the totals row
        self.assertEqual(len(table_slo_2[0]), 5)
        self.assertEqual(len(table_slo_2[1]), 5)
        self.assertEqual(len(table_slo_2[2]), 5)
        self.assertEqual(table_slo_2[0][0], mod_code_1)
        self.assertEqual(table_slo_2[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_2[0][2], 75)#75 measure in second academic year
        self.assertEqual(table_slo_2[0][3], '')#no measure in third academic year
        self.assertEqual(table_slo_2[0][4], '')#no measure in last academic year
        self.assertEqual(table_slo_2[1][0], mod_code_2)
        self.assertEqual(table_slo_2[1][1], '')#no measure in first academic year
        self.assertEqual(table_slo_2[1][2], '')#NO measure in second academic year
        self.assertEqual(table_slo_2[1][3], 65)#65 measure in third academic year for MOD 2
        self.assertEqual(table_slo_2[1][4], '')#no measure in last academic year
        self.assertEqual(table_slo_2[2][0], 'Weighted average')
        self.assertEqual(table_slo_2[2][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_2[2][2], 75.0)#75 measure in second academic year, total is 75
        self.assertAlmostEqual(table_slo_2[2][3], 65)#65 measure in third academic year, only one measure
        self.assertEqual(table_slo_2[2][4], 0)#no measure in last academic year -> totals row is zero

        table_slo_3 = CalculateTableForMLODirectMeasures(slo_id = slo_3.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_3), 2)#one measure plus the totals row
        self.assertEqual(len(table_slo_3[0]), 5)
        self.assertEqual(len(table_slo_3[1]), 5)
        self.assertEqual(table_slo_3[0][0], mod_code_1)
        self.assertEqual(table_slo_3[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_3[0][2], 75)#75 measure in second academic year
        self.assertEqual(table_slo_3[0][3], '')#no measure in third academic year
        self.assertEqual(table_slo_3[0][4], '')#no measure in last academic year
        self.assertEqual(table_slo_3[1][0], 'Weighted average')
        self.assertEqual(table_slo_3[1][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_3[1][2], 75.0)#75 measure in second academic year, total is 75
        self.assertEqual(table_slo_3[1][3], 0)#no measure in third academic year -> totals row is zero
        self.assertEqual(table_slo_3[1][4], 0)#no measure in last academic year -> totals row is zero

        #Now add another measure for MLO 1, for module 3. 
        # This is mapped to SLO 1 (strength 2) and SLO 3 (strength 1).We go for the second academic year (same as measure 1)
        # Tables for SLO1 and SLO3 should change. Table for SLO2 should remain unaltered
        measure_4 = MLOPerformanceMeasure.objects.create(description = 'test 3', academic_year = acad_year_2, associated_mlo = mlo_3_1,percentage_score=15)
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),4)
        table_slo_1 = CalculateTableForMLODirectMeasures(slo_id = slo_1.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_1), 4)#measures for Module 1, Module 2 and module 3 plus the totals row
        self.assertEqual(len(table_slo_1[0]), 5)
        self.assertEqual(len(table_slo_1[1]), 5)
        self.assertEqual(len(table_slo_1[2]), 5)
        self.assertEqual(len(table_slo_1[3]), 5)
        self.assertEqual(table_slo_1[0][0], mod_code_1)
        self.assertEqual(table_slo_1[0][1], '')#no measure in first academic year for module 1
        self.assertAlmostEqual(table_slo_1[0][2], (75*3+45*2)/5)#75 measure in second academic year, plus 45 measure ->Weighted average
        self.assertEqual(table_slo_1[0][3], '')#no measure in third academic year
        self.assertEqual(table_slo_1[0][4], '')#no measure in last academic year
        self.assertEqual(table_slo_1[1][0], mod_code_2)
        self.assertEqual(table_slo_1[1][1], '')#no measure in first academic year for module 2
        self.assertEqual(table_slo_1[1][2], '')#no measure in second academic year for module 2
        self.assertAlmostEqual(table_slo_1[1][3], 65)#65 measure in 3rd academic year
        self.assertEqual(table_slo_1[1][4], '')#no measure in last academic year for module 2
        self.assertEqual(table_slo_1[2][0], mod_code_3)
        self.assertEqual(table_slo_1[2][1], '')#no measure in first academic year for module 1
        self.assertAlmostEqual(table_slo_1[2][2], 15)#15 measure in second academic yea
        self.assertEqual(table_slo_1[2][3], '')#no measure in third academic year
        self.assertEqual(table_slo_1[2][4], '')#no measure in last academic year
        self.assertEqual(table_slo_1[3][0], 'Weighted average')
        self.assertEqual(table_slo_1[3][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_1[3][2], Decimal((75*3.0 + 45*2 + 15*2)/(3.0+2.0+2.0)))#75 measure in second academic year, plus 45 measure, plus 15 measure ->Weighted average
        self.assertAlmostEqual(table_slo_1[3][3], 65)#one measure in third academic year (module 2, MLO 1)
        self.assertEqual(table_slo_1[3][4], 0)#no measure in last academic year -> totals row is zero

        #unachanged
        table_slo_2 = CalculateTableForMLODirectMeasures(slo_id = slo_2.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_2), 3)#MOD 1, MOS 2 plus the totals row
        self.assertEqual(len(table_slo_2[0]), 5)
        self.assertEqual(len(table_slo_2[1]), 5)
        self.assertEqual(len(table_slo_2[2]), 5)
        self.assertEqual(table_slo_2[0][0], mod_code_1)
        self.assertEqual(table_slo_2[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_2[0][2], 75)#75 measure in second academic year
        self.assertEqual(table_slo_2[0][3], '')#no measure in third academic year
        self.assertEqual(table_slo_2[0][4], '')#no measure in last academic year
        self.assertEqual(table_slo_2[1][0], mod_code_2)
        self.assertEqual(table_slo_2[1][1], '')#no measure in first academic year
        self.assertEqual(table_slo_2[1][2], '')#NO measure in second academic year
        self.assertEqual(table_slo_2[1][3], 65)#65 measure in third academic year for MOD 2
        self.assertEqual(table_slo_2[1][4], '')#no measure in last academic year
        self.assertEqual(table_slo_2[2][0], 'Weighted average')
        self.assertEqual(table_slo_2[2][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_2[2][2], 75.0)#75 measure in second academic year, total is 75
        self.assertAlmostEqual(table_slo_2[2][3], 65)#65 measure in third academic year, only one measure
        self.assertEqual(table_slo_2[2][4], 0)#no measure in last academic year -> totals row is zero

        table_slo_3 = CalculateTableForMLODirectMeasures(slo_id = slo_3.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_3), 3)#two moduleswith measure plus the totals row
        self.assertEqual(len(table_slo_3[0]), 5)
        self.assertEqual(len(table_slo_3[1]), 5)
        self.assertEqual(len(table_slo_3[2]), 5)
        self.assertEqual(table_slo_3[0][0], mod_code_1)
        self.assertEqual(table_slo_3[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_3[0][2], 75)#75 measure in second academic year
        self.assertEqual(table_slo_3[0][3], '')#no measure in third academic year
        self.assertEqual(table_slo_3[0][4], '')#no measure in last academic year
        self.assertEqual(table_slo_3[1][0], mod_code_3)
        self.assertEqual(table_slo_3[1][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_3[1][2], 15)#15 measure in second academic year from mod 3
        self.assertEqual(table_slo_3[1][3], '')#no measure in third academic year
        self.assertEqual(table_slo_3[1][4], '')#no measure in last academic year
        self.assertEqual(table_slo_3[2][0], 'Weighted average')
        self.assertEqual(table_slo_3[2][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_3[2][2], (75.0*1 + 15*3)/(1.0 + 3.0))#75 measure in second academic year (strength 1), plus 15 from mod 3 (strength 3)
        self.assertEqual(table_slo_3[2][3], 0)#no measure in third academic year -> totals row is zero
        self.assertEqual(table_slo_3[2][4], 0)#no measure in last academic year -> totals row is zero

        #Now add another measure for MLO 1, for module 4
        # This is mapped to SLO 2 (strength 1).We go for the second academic year (same as measure 1)
        # Tables for SLO2 should change. Tables for SLO1 and SLO3 should remain unaltered
        measure_5 = MLOPerformanceMeasure.objects.create(description = 'test 4', academic_year = acad_year_2, associated_mlo = mlo_4_1,percentage_score=12.6)
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),5)
        #unachanged
        table_slo_1 = CalculateTableForMLODirectMeasures(slo_id = slo_1.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_1), 4)#measures for Module 1, Module 2 and module 3 plus the totals row
        self.assertEqual(len(table_slo_1[0]), 5)
        self.assertEqual(len(table_slo_1[1]), 5)
        self.assertEqual(len(table_slo_1[2]), 5)
        self.assertEqual(len(table_slo_1[3]), 5)
        self.assertEqual(table_slo_1[0][0], mod_code_1)
        self.assertEqual(table_slo_1[0][1], '')#no measure in first academic year for module 1
        self.assertAlmostEqual(table_slo_1[0][2], (75*3+45*2)/5)#75 measure in second academic year, plus 45 measure ->Weighted average
        self.assertEqual(table_slo_1[0][3], '')#no measure in third academic year
        self.assertEqual(table_slo_1[0][4], '')#no measure in last academic year
        self.assertEqual(table_slo_1[1][0], mod_code_2)
        self.assertEqual(table_slo_1[1][1], '')#no measure in first academic year for module 2
        self.assertEqual(table_slo_1[1][2], '')#no measure in second academic year for module 2
        self.assertAlmostEqual(table_slo_1[1][3], 65)#65 measure in 3rd academic year
        self.assertEqual(table_slo_1[1][4], '')#no measure in last academic year for module 2
        self.assertEqual(table_slo_1[2][0], mod_code_3)
        self.assertEqual(table_slo_1[2][1], '')#no measure in first academic year for module 1
        self.assertAlmostEqual(table_slo_1[2][2], 15)#15 measure in second academic yea
        self.assertEqual(table_slo_1[2][3], '')#no measure in third academic year
        self.assertEqual(table_slo_1[2][4], '')#no measure in last academic year
        self.assertEqual(table_slo_1[3][0], 'Weighted average')
        self.assertEqual(table_slo_1[3][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_1[3][2], Decimal((75*3.0 + 45*2 + 15*2)/(3.0+2.0+2.0)))#75 measure in second academic year, plus 45 measure, plus 15 measure ->Weighted average
        self.assertAlmostEqual(table_slo_1[3][3], 65)#one measure in third academic year (module 2, MLO 1)
        self.assertEqual(table_slo_1[3][4], 0)#no measure in last academic year -> totals row is zero

        
        table_slo_2 = CalculateTableForMLODirectMeasures(slo_id = slo_2.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_2), 4)#MOD 1, MOD 2, MOD 4, plus the totals row
        self.assertEqual(len(table_slo_2[0]), 5)
        self.assertEqual(len(table_slo_2[1]), 5)
        self.assertEqual(len(table_slo_2[2]), 5)
        self.assertEqual(len(table_slo_2[3]), 5)
        self.assertEqual(table_slo_2[0][0], mod_code_1)
        self.assertEqual(table_slo_2[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_2[0][2], 75)#75 measure in second academic year
        self.assertEqual(table_slo_2[0][3], '')#no measure in third academic year
        self.assertEqual(table_slo_2[0][4], '')#no measure in last academic year
        self.assertEqual(table_slo_2[1][0], mod_code_2)
        self.assertEqual(table_slo_2[1][1], '')#no measure in first academic year
        self.assertEqual(table_slo_2[1][2], '')#NO measure in second academic year
        self.assertEqual(table_slo_2[1][3], 65)#65 measure in third academic year for MOD 2
        self.assertEqual(table_slo_2[1][4], '')#no measure in last academic year
        self.assertEqual(table_slo_2[2][0], mod_code_4)
        self.assertEqual(table_slo_2[2][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_2[2][2], Decimal(12.6))#12.6 measure in third academic year for MOD 4
        self.assertEqual(table_slo_2[2][3], '')#No measure in third academic year
        self.assertEqual(table_slo_2[2][4], '')#no measure in last academic year
        self.assertEqual(table_slo_2[3][0], 'Weighted average')
        self.assertEqual(table_slo_2[3][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_2[3][2], Decimal((75.0*3+12.6*1)/(3.0+1.0)))#75 measure in second academic year (weight 3), plust 12.5 for module 4 (weight 1)
        self.assertAlmostEqual(table_slo_2[3][3], 65)#65 measure in third academic year, only one measure
        self.assertEqual(table_slo_2[3][4], 0)#no measure in last academic year -> totals row is zero

        #unachanged
        table_slo_3 = CalculateTableForMLODirectMeasures(slo_id = slo_3.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_3), 3)#two moduleswith measure plus the totals row
        self.assertEqual(len(table_slo_3[0]), 5)
        self.assertEqual(len(table_slo_3[1]), 5)
        self.assertEqual(len(table_slo_3[2]), 5)
        self.assertEqual(table_slo_3[0][0], mod_code_1)
        self.assertEqual(table_slo_3[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_3[0][2], 75)#75 measure in second academic year
        self.assertEqual(table_slo_3[0][3], '')#no measure in third academic year
        self.assertEqual(table_slo_3[0][4], '')#no measure in last academic year
        self.assertEqual(table_slo_3[1][0], mod_code_3)
        self.assertEqual(table_slo_3[1][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_3[1][2], 15)#15 measure in second academic year from mod 3
        self.assertEqual(table_slo_3[1][3], '')#no measure in third academic year
        self.assertEqual(table_slo_3[1][4], '')#no measure in last academic year
        self.assertEqual(table_slo_3[2][0], 'Weighted average')
        self.assertEqual(table_slo_3[2][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_3[2][2], (75.0*1 + 15*3)/(1.0 + 3.0))#75 measure in second academic year (strength 1), plus 15 from mod 3 (strength 3)
        self.assertEqual(table_slo_3[2][3], 0)#no measure in third academic year -> totals row is zero
        self.assertEqual(table_slo_3[2][4], 0)#no measure in last academic year -> totals row is zero

        #Now ad a measure with secondary and tertiary target        
        measure_6 = MLOPerformanceMeasure.objects.create(description = 'test 6', academic_year = acad_year_4, associated_mlo = mlo_1_2,\
                                                        secondary_associated_mlo = mlo_1_3,
                                                        tertiary_associated_mlo = mlo_1_4,
                                                        percentage_score=89.9)
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),6)
        table_slo_1 = CalculateTableForMLODirectMeasures(slo_id = slo_1.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_1), 4)#measures for Module 1, Module 2 and module 3 plus the totals row
        self.assertEqual(len(table_slo_1[0]), 5)
        self.assertEqual(len(table_slo_1[1]), 5)
        self.assertEqual(len(table_slo_1[2]), 5)
        self.assertEqual(len(table_slo_1[3]), 5)
        self.assertEqual(table_slo_1[0][0], mod_code_1)
        self.assertEqual(table_slo_1[0][1], '')#no measure in first academic year for module 1
        self.assertAlmostEqual(table_slo_1[0][2], (75*3+45*2)/5)#75 measure in second academic year, plus 45 measure ->Weighted average
        self.assertEqual(table_slo_1[0][3], '')#no measure in third academic year
        self.assertAlmostEqual(table_slo_1[0][4], Decimal(89.9))#this last measure 89.9
        self.assertEqual(table_slo_1[1][0], mod_code_2)
        self.assertEqual(table_slo_1[1][1], '')#no measure in first academic year for module 2
        self.assertEqual(table_slo_1[1][2], '')#no measure in second academic year for module 2
        self.assertAlmostEqual(table_slo_1[1][3], 65)#65 measure in 3rd academic year
        self.assertEqual(table_slo_1[1][4], '')#no measure in last academic year for module 2
        self.assertEqual(table_slo_1[2][0], mod_code_3)
        self.assertEqual(table_slo_1[2][1], '')#no measure in first academic year for module 1
        self.assertAlmostEqual(table_slo_1[2][2], 15)#15 measure in second academic yea
        self.assertEqual(table_slo_1[2][3], '')#no measure in third academic year
        self.assertEqual(table_slo_1[2][4], '')#no measure in last academic year
        self.assertEqual(table_slo_1[3][0], 'Weighted average')
        self.assertEqual(table_slo_1[3][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_1[3][2], Decimal((75*3.0 + 45*2 + 15*2)/(3.0+2.0+2.0)))#75 measure in second academic year, plus 45 measure, plus 15 measure ->Weighted average
        self.assertAlmostEqual(table_slo_1[3][3], 65)#one measure in third academic year (module 2, MLO 1)
        self.assertAlmostEqual(table_slo_1[3][4], Decimal(89.9))#This last measure alone

        
        table_slo_2 = CalculateTableForMLODirectMeasures(slo_id = slo_2.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_2), 4)#MOD 1, MOD 2, MOD 4, plus the totals row
        self.assertEqual(len(table_slo_2[0]), 5)
        self.assertEqual(len(table_slo_2[1]), 5)
        self.assertEqual(len(table_slo_2[2]), 5)
        self.assertEqual(len(table_slo_2[3]), 5)
        self.assertEqual(table_slo_2[0][0], mod_code_1)
        self.assertEqual(table_slo_2[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_2[0][2], 75)#75 measure in second academic year
        self.assertEqual(table_slo_2[0][3], '')#no measure in third academic year
        self.assertAlmostEqual(table_slo_2[0][4], Decimal(89.9))#this last measure 89.9
        self.assertEqual(table_slo_2[1][0], mod_code_2)
        self.assertEqual(table_slo_2[1][1], '')#no measure in first academic year
        self.assertEqual(table_slo_2[1][2], '')#NO measure in second academic year
        self.assertEqual(table_slo_2[1][3], 65)#65 measure in third academic year for MOD 2
        self.assertEqual(table_slo_2[1][4], '')#no measure in last academic year
        self.assertEqual(table_slo_2[2][0], mod_code_4)
        self.assertEqual(table_slo_2[2][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_2[2][2], Decimal(12.6))#12.6 measure in third academic year for MOD 4
        self.assertEqual(table_slo_2[2][3], '')#No measure in third academic year
        self.assertEqual(table_slo_2[2][4], '')#no measure in last academic year
        self.assertEqual(table_slo_2[3][0], 'Weighted average')
        self.assertEqual(table_slo_2[3][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_2[3][2], Decimal((75.0*3+12.6*1)/(3.0+1.0)))#75 measure in second academic year (weight 3), plust 12.5 for module 4 (weight 1)
        self.assertAlmostEqual(table_slo_2[3][3], 65)#65 measure in third academic year, only one measure
        self.assertAlmostEqual(table_slo_2[3][4], Decimal(89.9))#this last measure

        table_slo_3 = CalculateTableForMLODirectMeasures(slo_id = slo_3.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year)
        self.assertEqual(len(table_slo_3), 3)#two moduleswith measure plus the totals row
        self.assertEqual(len(table_slo_3[0]), 5)
        self.assertEqual(len(table_slo_3[1]), 5)
        self.assertEqual(len(table_slo_3[2]), 5)
        self.assertEqual(table_slo_3[0][0], mod_code_1)
        self.assertEqual(table_slo_3[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_3[0][2], 75)#75 measure in second academic year
        self.assertEqual(table_slo_3[0][3], '')#no measure in third academic year
        self.assertAlmostEqual(table_slo_3[0][4], Decimal(89.9))#this last measure 89.9
        self.assertEqual(table_slo_3[1][0], mod_code_3)
        self.assertEqual(table_slo_3[1][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_3[1][2], 15)#15 measure in second academic year from mod 3
        self.assertEqual(table_slo_3[1][3], '')#no measure in third academic year
        self.assertEqual(table_slo_3[1][4], '')#no measure in last academic year
        self.assertEqual(table_slo_3[2][0], 'Weighted average')
        self.assertEqual(table_slo_3[2][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_3[2][2], (75.0*1 + 15*3)/(1.0 + 3.0))#75 measure in second academic year (strength 1), plus 15 from mod 3 (strength 3)
        self.assertEqual(table_slo_3[2][3], 0)#no measure in third academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_3[2][4], Decimal(89.9))#this last measure

        #####################################################################
        # Test the MLO survey table
        #####################################################################
        mlo_survey_1 = Survey.objects.create(survey_title = "first mlo survey", opening_date = datetime.datetime(2020, 5, 17),\
                                                                                closing_date = datetime.datetime(2021, 5, 17),\
                                                                                max_respondents = 100)
        #Create the responses
        response_1 = SurveyQuestionResponse.objects.create(question_text = mlo_1_1.mlo_description,\
                                                           n_highest_score = 50,\
                                                           n_second_highest_score = 30,\
                                                           n_third_highest_score = 5,\
                                                           n_fourth_highest_score = 15,\
                                                           associated_mlo = mlo_1_1,\
                                                           parent_survey = mlo_survey_1 )
                                                                                
        #Generate the table for SLO 1
        mlo_table_slo_1 = CalculateTableForMLOSurveys(slo_id = slo_1.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(mlo_table_slo_1), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_1[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_1[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_1[0][0], mlo_1_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_1[0][1],100*CalulatePositiveResponsesFractionForQuestion(response_1.id))#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_1[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_1[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_1[1][1],100*CalulatePositiveResponsesFractionForQuestion(response_1.id))#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_1[1][2],0)#Nothing in 2021

        #Generate the table for SLO 2 - at this stage this is the same as the one for SLO 1, with just one measure
        mlo_table_slo_2 = CalculateTableForMLOSurveys(slo_id = slo_2.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(mlo_table_slo_2), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_2[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_2[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_2[0][0], mlo_1_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_2[0][1],100*CalulatePositiveResponsesFractionForQuestion(response_1.id))#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_2[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_2[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_2[1][1],100*CalulatePositiveResponsesFractionForQuestion(response_1.id))#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_2[1][2],0)#Nothing in 2021

        #Generate the table for SLO 3 - at this stage this is the same as the one for SLO 1, with just one measure
        mlo_table_slo_3 = CalculateTableForMLOSurveys(slo_id = slo_3.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(mlo_table_slo_3), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_3[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_3[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_3[0][0], mlo_1_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_3[0][1],100*CalulatePositiveResponsesFractionForQuestion(response_1.id))#MLO 1 of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_3[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_3[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_3[1][1],100*CalulatePositiveResponsesFractionForQuestion(response_1.id))#MLO 1 of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_3[1][2],0)#Nothing in 2021

        #Create another response in the same survey, for MLO 2 of module 1
        response_2 = SurveyQuestionResponse.objects.create(question_text = mlo_1_2.mlo_description,\
                                                           n_highest_score = 5,\
                                                           n_second_highest_score = 15,\
                                                           n_third_highest_score = 55,\
                                                           n_fourth_highest_score = 25,\
                                                           associated_mlo = mlo_1_2,\
                                                           parent_survey = mlo_survey_1 )
        #Generate the table for SLO 1 - CHANGED
        mlo_table_slo_1 = CalculateTableForMLOSurveys(slo_id = slo_1.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(mlo_table_slo_1), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_1[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_1[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_1[0][0], mlo_1_1.module_code)
        expected_weigthed_average = (3.0*CalulatePositiveResponsesFractionForQuestion(response_1.id) + \
                                     2.0*CalulatePositiveResponsesFractionForQuestion(response_2.id))/(3.0+2.0)
        self.assertAlmostEqual(mlo_table_slo_1[0][1],100*expected_weigthed_average)#MLO 1of module 1 mapped to slo 1, but also MLO 2 of module 1
        self.assertAlmostEqual(mlo_table_slo_1[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_1[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_1[1][1],100*expected_weigthed_average)#same as above
        self.assertAlmostEqual(mlo_table_slo_1[1][2],0)#Nothing in 2021

        #Generate the table for SLO 2 - UNCHANGED as MLO 2 of module 1 does not map to slo 3
        mlo_table_slo_2 = CalculateTableForMLOSurveys(slo_id = slo_2.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(mlo_table_slo_2), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_2[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_2[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_2[0][0], mlo_1_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_2[0][1],100*CalulatePositiveResponsesFractionForQuestion(response_1.id))#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_2[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_2[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_2[1][1],100*CalulatePositiveResponsesFractionForQuestion(response_1.id))#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_2[1][2],0)#Nothing in 2021

        #Generate the table for SLO 3 - UNCHANGED as MLO 2 of module 1 does not map to slo 3
        mlo_table_slo_3 = CalculateTableForMLOSurveys(slo_id = slo_3.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(mlo_table_slo_3), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_3[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_3[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_3[0][0], mlo_1_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_3[0][1],100*CalulatePositiveResponsesFractionForQuestion(response_1.id))#MLO 1 of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_3[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_3[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_3[1][1],100*CalulatePositiveResponsesFractionForQuestion(response_1.id))#MLO 1 of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_3[1][2],0)#Nothing in 2021

        mlo_survey_2 = Survey.objects.create(survey_title = "second mlo survey", opening_date = datetime.datetime(2020, 5, 17),\
                                                                                closing_date = datetime.datetime(2021, 5, 17),\
                                                                                max_respondents = 100)
        #Create another response for MLO 1 of module 2
        response_3 = SurveyQuestionResponse.objects.create(question_text = mlo_1_1.mlo_description,\
                                                           n_highest_score = 15,\
                                                           n_second_highest_score = 28,\
                                                           n_third_highest_score = 2,\
                                                           n_fourth_highest_score = 55,\
                                                           associated_mlo = mlo_2_1,\
                                                           parent_survey = mlo_survey_2 ) #mapped to slo 1 (2) and slo 2 (3)
        mlo_table_slo_1 = CalculateTableForMLOSurveys(slo_id = slo_1.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(mlo_table_slo_1), 3)#Two meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_1[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_1[1]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_1[2]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_1[0][0], mlo_1_1.module_code)
        expected_weigthed_average = (3.0*CalulatePositiveResponsesFractionForQuestion(response_1.id) + \
                                     2.0*CalulatePositiveResponsesFractionForQuestion(response_2.id))/(3.0+2.0)
        self.assertAlmostEqual(mlo_table_slo_1[0][1],100*expected_weigthed_average)#MLO 1of module 1 mapped to slo 1, but also MLO 2 of module 1
        self.assertAlmostEqual(mlo_table_slo_1[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_1[1][0], mlo_2_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_1[1][1],100*CalulatePositiveResponsesFractionForQuestion(response_3.id) )#MLO 1 of module 2 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_1[1][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_1[2][0], "Weighted average")
        expected_weigthed_average_2 = (3.0*CalulatePositiveResponsesFractionForQuestion(response_1.id) + \
                                      2.0*CalulatePositiveResponsesFractionForQuestion(response_2.id) + \
                                      2.0*CalulatePositiveResponsesFractionForQuestion(response_3.id))/(3.0+2.0+2.0)
        self.assertAlmostEqual(mlo_table_slo_1[2][1],100*expected_weigthed_average_2)#same as above
        self.assertAlmostEqual(mlo_table_slo_1[2][2],0)#Nothing in 2021

        #Generate the table for SLO 2 
        mlo_table_slo_2 = CalculateTableForMLOSurveys(slo_id = slo_2.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(mlo_table_slo_2), 3)#Three meausures, plus the totals
        self.assertEqual(len(mlo_table_slo_2[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_2[1]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_2[2]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_2[0][0], mlo_1_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_2[0][1],100*CalulatePositiveResponsesFractionForQuestion(response_1.id))#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_2[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_2[1][0], mlo_2_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_2[1][1],100*CalulatePositiveResponsesFractionForQuestion(response_3.id))#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_2[1][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_2[2][0], "Weighted average")
        expected_weighted_average_3 = (3.0* CalulatePositiveResponsesFractionForQuestion(response_1.id) +\
                                       3.0*CalulatePositiveResponsesFractionForQuestion(response_3.id))/(3.0+3.0)
        self.assertAlmostEqual(mlo_table_slo_2[2][1],100*expected_weighted_average_3)
        self.assertAlmostEqual(mlo_table_slo_2[2][2],0)#Nothing in 2021

        #Generate the table for SLO 3 - UNCHANGED as MLO 1 of module 2 does not map to slo 3
        mlo_table_slo_3 = CalculateTableForMLOSurveys(slo_id = slo_3.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(mlo_table_slo_3), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_3[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_3[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_3[0][0], mlo_1_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_3[0][1],100*CalulatePositiveResponsesFractionForQuestion(response_1.id))#MLO 1 of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_3[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_3[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_3[1][1],100*CalulatePositiveResponsesFractionForQuestion(response_1.id))#MLO 1 of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_3[1][2],0)#Nothing in 2021

        #Cover the empty table because of dates out of range
        empty_mlo_table_slo = CalculateTableForMLOSurveys(slo_id = slo_3.id,start_year = 2010, end_year = 2011)
        self.assertEqual(len(empty_mlo_table_slo), 1)#Only the totals

        #####################################################################
        # Test the SLO survey table
        #####################################################################

        slo_survey_1 = Survey.objects.create(survey_title = "first slo survey", opening_date = datetime.datetime(2020, 5, 17),\
                                                                                closing_date = datetime.datetime(2021, 5, 17),\
                                                                                max_respondents = 100)
        slo_response_1 = SurveyQuestionResponse.objects.create(question_text = slo_1.slo_description,\
                                                           n_highest_score = 15,\
                                                           n_second_highest_score = 28,\
                                                           n_third_highest_score = 2,\
                                                           n_fourth_highest_score = 55,\
                                                           associated_slo = slo_1,\
                                                           parent_survey = slo_survey_1)
        slo_response_2 = SurveyQuestionResponse.objects.create(question_text = slo_2.slo_description,\
                                                           n_highest_score = 55,\
                                                           n_second_highest_score = 28,\
                                                           n_third_highest_score = 2,\
                                                           n_fourth_highest_score = 15,\
                                                           associated_slo = slo_2,\
                                                           parent_survey = slo_survey_1)
        #Generate table for SLO 1
        slo_1_survey_table = CalculateTableForSLOSurveys(slo_id = slo_1.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(slo_1_survey_table),1)
        self.assertEqual(slo_1_survey_table[0]['question'],slo_1.slo_description)
        self.assertAlmostEqual(slo_1_survey_table[0]['percent_positive'],100*CalulatePositiveResponsesFractionForQuestion(slo_response_1.id))
        self.assertEqual(slo_1_survey_table[0]['n_questions'],1)

        #Generate table for SLO 2
        slo_2_survey_table = CalculateTableForSLOSurveys(slo_id = slo_2.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(slo_2_survey_table),1)
        self.assertEqual(slo_2_survey_table[0]['question'],slo_2.slo_description)
        self.assertAlmostEqual(slo_2_survey_table[0]['percent_positive'],100*CalulatePositiveResponsesFractionForQuestion(slo_response_2.id))
        self.assertEqual(slo_2_survey_table[0]['n_questions'],1)

        #Generate table for SLO 3 (this one is empty)
        slo_3_survey_table = CalculateTableForSLOSurveys(slo_id = slo_3.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(slo_3_survey_table),0)

        #Add another response linked to slo 1 in the same survey (test concatenation and averaging of two questions with same target)
        alternate_question = "blah blah"
        slo_response_1_alternate = SurveyQuestionResponse.objects.create(question_text = alternate_question,\
                                                           n_highest_score = 5,\
                                                           n_second_highest_score = 28,\
                                                           n_third_highest_score = 2,\
                                                           n_fourth_highest_score = 65,\
                                                           associated_slo = slo_1,\
                                                           parent_survey = slo_survey_1)
        #Generate table for SLO 1
        slo_1_survey_table = CalculateTableForSLOSurveys(slo_id = slo_1.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(slo_1_survey_table),1)
        self.assertEqual(slo_1_survey_table[0]['question'],slo_1.slo_description + ', ' + alternate_question)
        expected_fraction = 0.5*(CalulatePositiveResponsesFractionForQuestion(slo_response_1.id) + CalulatePositiveResponsesFractionForQuestion(slo_response_1_alternate.id))
        self.assertAlmostEqual(slo_1_survey_table[0]['percent_positive'],100*expected_fraction)
        self.assertEqual(slo_1_survey_table[0]['n_questions'],2)#2 questions now

        #Generate table for SLO 2 - UNCHANGED
        slo_2_survey_table = CalculateTableForSLOSurveys(slo_id = slo_2.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(slo_2_survey_table),1)
        self.assertEqual(slo_2_survey_table[0]['question'],slo_2.slo_description)
        self.assertAlmostEqual(slo_2_survey_table[0]['percent_positive'],100*CalulatePositiveResponsesFractionForQuestion(slo_response_2.id))
        self.assertEqual(slo_2_survey_table[0]['n_questions'],1)

        #Generate table for SLO 3 (this one is empty) - UNCHANGED
        slo_3_survey_table = CalculateTableForSLOSurveys(slo_id = slo_3.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(slo_3_survey_table),0)

        #Do another survey. Test ability to create new lines in the table
        slo_survey_2 = Survey.objects.create(survey_title = "second slo survey", opening_date = datetime.datetime(2020, 7, 17),\
                                                                                closing_date = datetime.datetime(2021, 9, 17),\
                                                                                max_respondents = 100)
        slo_response_2_srv2 = SurveyQuestionResponse.objects.create(question_text = slo_2.slo_description,\
                                                           n_highest_score = 15,\
                                                           n_second_highest_score = 28,\
                                                           n_third_highest_score = 2,\
                                                           n_fourth_highest_score = 55,\
                                                           associated_slo = slo_2,\
                                                           parent_survey = slo_survey_2)
        #Generate table for SLO 1 - UNCHANGED
        slo_1_survey_table = CalculateTableForSLOSurveys(slo_id = slo_1.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(slo_1_survey_table),1)
        self.assertEqual(slo_1_survey_table[0]['question'],slo_1.slo_description + ', ' + alternate_question)
        expected_fraction = 0.5*(CalulatePositiveResponsesFractionForQuestion(slo_response_1.id) + CalulatePositiveResponsesFractionForQuestion(slo_response_1_alternate.id))
        self.assertAlmostEqual(slo_1_survey_table[0]['percent_positive'],100*expected_fraction)
        self.assertEqual(slo_1_survey_table[0]['n_questions'],2)#2 questions now

        #Generate table for SLO 2 - new line added here
        slo_2_survey_table = CalculateTableForSLOSurveys(slo_id = slo_2.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(slo_2_survey_table),2)
        self.assertEqual(slo_2_survey_table[0]['question'],slo_2.slo_description)
        self.assertAlmostEqual(slo_2_survey_table[0]['percent_positive'],100*CalulatePositiveResponsesFractionForQuestion(slo_response_2.id))
        self.assertEqual(slo_2_survey_table[0]['n_questions'],1)
        self.assertEqual(slo_2_survey_table[1]['question'],slo_2.slo_description)
        self.assertAlmostEqual(slo_2_survey_table[1]['percent_positive'],100*CalulatePositiveResponsesFractionForQuestion(slo_response_2_srv2.id))
        self.assertEqual(slo_2_survey_table[1]['n_questions'],1)

        #Generate table for SLO 3 (this one is empty) - UNCHANGED
        slo_3_survey_table = CalculateTableForSLOSurveys(slo_id = slo_3.id,start_year = 2020, end_year = 2021)
        self.assertEqual(len(slo_3_survey_table),0)

        #Test the MLO-SLO mapping table for a single SLO
        slo_1_table = CalculateMLOSLOMappingTable(slo_1.id, 2012,2015)
        self.assertEqual(len(slo_1_table), 3) #3 mods mapped
        self.assertEqual(slo_1_table[0]["module_code"], mod_code_1)
        self.assertEqual(slo_1_table[1]["module_code"], mod_code_2)
        self.assertEqual(slo_1_table[2]["module_code"], mod_code_3)
        self.assertEqual(len(slo_1_table[0]["numerical_mappings"]), 4)
        self.assertEqual(slo_1_table[0]["numerical_mappings"][0], 3)#SLO 1 - MOD 1 - 2012
        self.assertEqual(slo_1_table[0]["numerical_mappings"][1], 3)#SLO 1 - MOD 1 - 2013
        self.assertEqual(slo_1_table[0]["numerical_mappings"][2], 3)#SLO 1 - MOD 1 - 2014
        self.assertEqual(slo_1_table[0]["numerical_mappings"][3], 3)#SLO 1 - MOD 1 - 2014

        self.assertEqual(slo_1_table[0]["n_mlo_mapped"][0], 3)#SLO 1 - MOD 1 - 2012
        self.assertEqual(slo_1_table[0]["n_mlo_mapped"][1], 3)#SLO 1 - MOD 1 - 2013
        self.assertEqual(slo_1_table[0]["n_mlo_mapped"][2], 3)#SLO 1 - MOD 1 - 2014
        self.assertEqual(slo_1_table[0]["n_mlo_mapped"][3], 3)#SLO 1 - MOD 1 - 2015

        self.assertEqual(slo_1_table[1]["numerical_mappings"][0], 3)#SLO 1 - MOD 2 - 2012
        self.assertEqual(slo_1_table[1]["numerical_mappings"][1], 3)#SLO 1 - MOD 2 - 2013
        self.assertEqual(slo_1_table[1]["numerical_mappings"][2], 3)#SLO 1 - MOD 2 - 2014
        self.assertEqual(slo_1_table[1]["numerical_mappings"][3], 3)#SLO 1 - MOD 2 - 2014

        self.assertEqual(slo_1_table[1]["n_mlo_mapped"][0], 2)#SLO 1 - MOD 2 - 2012
        self.assertEqual(slo_1_table[1]["n_mlo_mapped"][1], 2)#SLO 1 - MOD 2 - 2013
        self.assertEqual(slo_1_table[1]["n_mlo_mapped"][2], 2)#SLO 1 - MOD 2 - 2014
        self.assertEqual(slo_1_table[1]["n_mlo_mapped"][3], 2)#SLO 1 - MOD 2 - 2015

        self.assertEqual(slo_1_table[2]["numerical_mappings"][0], 2)#SLO 1 - MOD 3 - 2012
        self.assertEqual(slo_1_table[2]["numerical_mappings"][1], 2)#SLO 1 - MOD 3 - 2013
        self.assertEqual(slo_1_table[2]["numerical_mappings"][2], 2)#SLO 1 - MOD 3 - 2014
        self.assertEqual(slo_1_table[2]["numerical_mappings"][3], 2)#SLO 1 - MOD 3 - 2014

        self.assertEqual(slo_1_table[2]["n_mlo_mapped"][0], 1)#SLO 1 - MOD 3 - 2012
        self.assertEqual(slo_1_table[2]["n_mlo_mapped"][1], 1)#SLO 1 - MOD 3 - 2013
        self.assertEqual(slo_1_table[2]["n_mlo_mapped"][2], 1)#SLO 1 - MOD 3 - 2014
        self.assertEqual(slo_1_table[2]["n_mlo_mapped"][3], 1)#SLO 1 - MOD 3 - 2015


        slo_2_table = CalculateMLOSLOMappingTable(slo_2.id, 2012,2015)
        self.assertEqual(len(slo_2_table), 3) #3 mods mapped
        self.assertEqual(slo_2_table[0]["module_code"], mod_code_1)
        self.assertEqual(slo_2_table[1]["module_code"], mod_code_2)
        self.assertEqual(slo_2_table[2]["module_code"], mod_code_4)
        self.assertEqual(len(slo_2_table[0]["numerical_mappings"]), 4)
        self.assertEqual(slo_2_table[0]["numerical_mappings"][0], 3)#SLO 2 - MOD 1 - 2012
        self.assertEqual(slo_2_table[0]["numerical_mappings"][1], 3)#SLO 2 - MOD 1 - 2013
        self.assertEqual(slo_2_table[0]["numerical_mappings"][2], 3)#SLO 2 - MOD 1 - 2014
        self.assertEqual(slo_2_table[0]["numerical_mappings"][3], 3)#SLO 2 - MOD 1 - 2014

        self.assertEqual(slo_2_table[0]["n_mlo_mapped"][0], 2)#SLO 2 - MOD 1 - 2012
        self.assertEqual(slo_2_table[0]["n_mlo_mapped"][1], 2)#SLO 2 - MOD 1 - 2013
        self.assertEqual(slo_2_table[0]["n_mlo_mapped"][2], 2)#SLO 2 - MOD 1 - 2014
        self.assertEqual(slo_2_table[0]["n_mlo_mapped"][3], 2)#SLO 2 - MOD 1 - 2015

        self.assertEqual(slo_2_table[1]["numerical_mappings"][0], 3)#SLO 2 - MOD 2 - 2012
        self.assertEqual(slo_2_table[1]["numerical_mappings"][1], 3)#SLO 2 - MOD 2 - 2013
        self.assertEqual(slo_2_table[1]["numerical_mappings"][2], 3)#SLO 2 - MOD 2 - 2014
        self.assertEqual(slo_2_table[1]["numerical_mappings"][3], 3)#SLO 2 - MOD 2 - 2014

        self.assertEqual(slo_2_table[1]["n_mlo_mapped"][0], 1)#SLO 2 - MOD 2 - 2012
        self.assertEqual(slo_2_table[1]["n_mlo_mapped"][1], 1)#SLO 2 - MOD 2 - 2013
        self.assertEqual(slo_2_table[1]["n_mlo_mapped"][2], 1)#SLO 2 - MOD 2 - 2014
        self.assertEqual(slo_2_table[1]["n_mlo_mapped"][3], 1)#SLO 2 - MOD 2 - 2015

        self.assertEqual(slo_2_table[2]["numerical_mappings"][0], 1)#SLO 2 - MOD 4 - 2012
        self.assertEqual(slo_2_table[2]["numerical_mappings"][1], 1)#SLO 2 - MOD 4 - 2013
        self.assertEqual(slo_2_table[2]["numerical_mappings"][2], 1)#SLO 2 - MOD 4 - 2014
        self.assertEqual(slo_2_table[2]["numerical_mappings"][3], 1)#SLO 2 - MOD 4 - 2014

        self.assertEqual(slo_2_table[2]["n_mlo_mapped"][0], 1)#SLO 2 - MOD 4 - 2012
        self.assertEqual(slo_2_table[2]["n_mlo_mapped"][1], 1)#SLO 2 - MOD 4 - 2013
        self.assertEqual(slo_2_table[2]["n_mlo_mapped"][2], 1)#SLO 2 - MOD 4 - 2014
        self.assertEqual(slo_2_table[2]["n_mlo_mapped"][3], 1)#SLO 2 - MOD 4 - 2015

        slo_3_table = CalculateMLOSLOMappingTable(slo_3.id, 2012,2015)
        self.assertEqual(len(slo_3_table), 3) #3 mods mapped
        self.assertEqual(slo_3_table[0]["module_code"], mod_code_1)
        self.assertEqual(slo_3_table[1]["module_code"], mod_code_2)
        self.assertEqual(slo_3_table[2]["module_code"], mod_code_3)
        self.assertEqual(len(slo_3_table[0]["numerical_mappings"]), 4)
        self.assertEqual(slo_3_table[0]["numerical_mappings"][0], 2)#SLO 3 - MOD 1 - 2012
        self.assertEqual(slo_3_table[0]["numerical_mappings"][1], 2)#SLO 3 - MOD 1 - 2013
        self.assertEqual(slo_3_table[0]["numerical_mappings"][2], 2)#SLO 3 - MOD 1 - 2014
        self.assertEqual(slo_3_table[0]["numerical_mappings"][3], 2)#SLO 3 - MOD 1 - 2014

        self.assertEqual(slo_3_table[0]["n_mlo_mapped"][0], 2)#SLO 3 - MOD 1 - 2012
        self.assertEqual(slo_3_table[0]["n_mlo_mapped"][1], 2)#SLO 3 - MOD 1 - 2013
        self.assertEqual(slo_3_table[0]["n_mlo_mapped"][2], 2)#SLO 3 - MOD 1 - 2014
        self.assertEqual(slo_3_table[0]["n_mlo_mapped"][3], 2)#SLO 3 - MOD 1 - 2015

        self.assertEqual(slo_3_table[1]["numerical_mappings"][0], 1)#SLO 3 - MOD 2 - 2012
        self.assertEqual(slo_3_table[1]["numerical_mappings"][1], 1)#SLO 3 - MOD 2 - 2013
        self.assertEqual(slo_3_table[1]["numerical_mappings"][2], 1)#SLO 3 - MOD 2 - 2014
        self.assertEqual(slo_3_table[1]["numerical_mappings"][3], 1)#SLO 3 - MOD 2 - 2014

        self.assertEqual(slo_3_table[1]["n_mlo_mapped"][0], 1)#SLO 3 - MOD 2 - 2012
        self.assertEqual(slo_3_table[1]["n_mlo_mapped"][1], 1)#SLO 3 - MOD 2 - 2012
        self.assertEqual(slo_3_table[1]["n_mlo_mapped"][2], 1)#SLO 3 - MOD 2 - 2012
        self.assertEqual(slo_3_table[1]["n_mlo_mapped"][3], 1)#SLO 3 - MOD 2 - 2012

        self.assertEqual(slo_3_table[2]["numerical_mappings"][0], 3)#SLO 3 - MOD 4 - 2012
        self.assertEqual(slo_3_table[2]["numerical_mappings"][1], 3)#SLO 3 - MOD 4 - 2013
        self.assertEqual(slo_3_table[2]["numerical_mappings"][2], 3)#SLO 3 - MOD 4 - 2014
        self.assertEqual(slo_3_table[2]["numerical_mappings"][3], 3)#SLO 3 - MOD 4 - 2015

        self.assertEqual(slo_3_table[2]["n_mlo_mapped"][0], 2)#SLO 3 - MOD 3 - 2012
        self.assertEqual(slo_3_table[2]["n_mlo_mapped"][1], 2)#SLO 3 - MOD 3 - 2013
        self.assertEqual(slo_3_table[2]["n_mlo_mapped"][2], 2)#SLO 3 - MOD 3 - 2014
        self.assertEqual(slo_3_table[2]["n_mlo_mapped"][3], 2)#SLO 3 - MOD 3 - 2015

        #Test the big slo mlo table
        main_body_table = CalculateTableForOverallSLOMapping(prog_to_accredit.id, 2020,2021)['main_body_table']
        self.assertEqual(len(main_body_table), 0) #No workloads in the period
        big_table = CalculateTableForOverallSLOMapping(prog_to_accredit.id, 2010,2021)
        main_body_table = big_table['main_body_table']
        self.assertEqual(len(main_body_table), 4) 
        self.assertEqual(main_body_table[0]["module_code"], mod_code_1)
        self.assertEqual(len(main_body_table[0]["slo_identifiers"]), 3)
        self.assertEqual(len(main_body_table[0]["numerical_mappings"]), 3)
        self.assertEqual(main_body_table[0]["numerical_mappings"][0], 3)#SLO 1 - MOD 1
        self.assertEqual(main_body_table[0]["numerical_mappings"][1], 3)#SLO 2 - MOD 1
        self.assertEqual(main_body_table[0]["numerical_mappings"][2], 2)#SLO 3 - MOD 1
        self.assertEqual(len(main_body_table[1]["numerical_mappings"]), 3)
        self.assertEqual(main_body_table[1]["numerical_mappings"][0], 3)#SLO 1 - MOD 2
        self.assertEqual(main_body_table[1]["numerical_mappings"][1], 3)#SLO 2 - MOD 2
        self.assertEqual(main_body_table[1]["numerical_mappings"][2], 1)#SLO 3 - MOD 2
        self.assertEqual(len(main_body_table[2]["numerical_mappings"]), 3)
        self.assertEqual(main_body_table[2]["numerical_mappings"][0], 2)#SLO 1 - MOD 3 
        self.assertEqual(main_body_table[2]["numerical_mappings"][1], 0)#SLO 2 - MOD 3
        self.assertEqual(main_body_table[2]["numerical_mappings"][2], 3)#SLO 3 - MOD 3
        self.assertEqual(len(main_body_table[3]["numerical_mappings"]), 3)
        self.assertEqual(main_body_table[3]["numerical_mappings"][0], 0)#SLO 1 - MOD 4 
        self.assertEqual(main_body_table[3]["numerical_mappings"][1], 1)#SLO 2 - MOD 4
        self.assertEqual(main_body_table[3]["numerical_mappings"][2], 0)#SLO 3 - MOD 4

        self.assertEqual(len(main_body_table[0]["summation_strengths"]), 3)
        self.assertEqual(main_body_table[0]["summation_strengths"][0], 3+2+1)#SLO 1 - MOD 1
        self.assertEqual(main_body_table[0]["summation_strengths"][1], 3+2)#SLO 2 - MOD 1
        self.assertEqual(main_body_table[0]["summation_strengths"][2], 1+2)#SLO 3 - MOD 1
        self.assertEqual(len(main_body_table[1]["summation_strengths"]), 3)
        self.assertEqual(main_body_table[1]["summation_strengths"][0], 2+3)#SLO 1 - MOD 2
        self.assertEqual(main_body_table[1]["summation_strengths"][1], 3)#SLO 2 - MOD 2
        self.assertEqual(main_body_table[1]["summation_strengths"][2], 1)#SLO 3 - MOD 2
        self.assertEqual(len(main_body_table[2]["summation_strengths"]), 3)
        self.assertEqual(main_body_table[2]["summation_strengths"][0], 2)#SLO 1 - MOD 3 
        self.assertEqual(main_body_table[2]["summation_strengths"][1], 0)#SLO 2 - MOD 3
        self.assertEqual(main_body_table[2]["summation_strengths"][2], 3+3)#SLO 3 - MOD 3
        self.assertEqual(len(main_body_table[3]["summation_strengths"]), 3)
        self.assertEqual(main_body_table[3]["summation_strengths"][0], 0)#SLO 1 - MOD 4 
        self.assertEqual(main_body_table[3]["summation_strengths"][1], 1)#SLO 2 - MOD 4
        self.assertEqual(main_body_table[3]["summation_strengths"][2], 0)#SLO 3 - MOD 4

        self.assertEqual(len(main_body_table[0]["icons"]), 3)
        self.assertEqual(main_body_table[0]["icons"][0], DetermineIconBasedOnStrength(3))#SLO 1 - MOD 1
        self.assertEqual(main_body_table[0]["icons"][1], DetermineIconBasedOnStrength(3))#SLO 2 - MOD 1
        self.assertEqual(main_body_table[0]["icons"][2], DetermineIconBasedOnStrength(2))#SLO 3 - MOD 1
        self.assertEqual(len(main_body_table[1]["icons"]), 3)
        self.assertEqual(main_body_table[1]["icons"][0], DetermineIconBasedOnStrength(3))#SLO 1 - MOD 2
        self.assertEqual(main_body_table[1]["icons"][1], DetermineIconBasedOnStrength(3))#SLO 2 - MOD 2
        self.assertEqual(main_body_table[1]["icons"][2], DetermineIconBasedOnStrength(1))#SLO 3 - MOD 2
        self.assertEqual(len(main_body_table[2]["icons"]), 3)
        self.assertEqual(main_body_table[2]["icons"][0], DetermineIconBasedOnStrength(2))#SLO 1 - MOD 3 
        self.assertEqual(main_body_table[2]["icons"][1], DetermineIconBasedOnStrength(0))#SLO 2 - MOD 3
        self.assertEqual(main_body_table[2]["icons"][2], DetermineIconBasedOnStrength(3))#SLO 3 - MOD 3
        self.assertEqual(len(main_body_table[3]["icons"]), 3)
        self.assertEqual(main_body_table[3]["icons"][0], DetermineIconBasedOnStrength(0))#SLO 1 - MOD 4 
        self.assertEqual(main_body_table[3]["icons"][1], DetermineIconBasedOnStrength(1))#SLO 2 - MOD 4
        self.assertEqual(main_body_table[3]["icons"][2], DetermineIconBasedOnStrength(0))#SLO 3 - MOD 4

        self.assertEqual(len(main_body_table[0]["n_mlo_mapped"]), 3)
        self.assertEqual(main_body_table[0]["n_mlo_mapped"][0],3)#SLO 1 - MOD 1
        self.assertEqual(main_body_table[0]["n_mlo_mapped"][1], 2)#SLO 2 - MOD 1
        self.assertEqual(main_body_table[0]["n_mlo_mapped"][2], 2)#SLO 3 - MOD 1
        self.assertEqual(len(main_body_table[1]["n_mlo_mapped"]), 3)
        self.assertEqual(main_body_table[1]["n_mlo_mapped"][0], 2)#SLO 1 - MOD 2
        self.assertEqual(main_body_table[1]["n_mlo_mapped"][1], 1)#SLO 2 - MOD 2
        self.assertEqual(main_body_table[1]["n_mlo_mapped"][2], 1)#SLO 3 - MOD 2
        self.assertEqual(len(main_body_table[2]["n_mlo_mapped"]), 3)
        self.assertEqual(main_body_table[2]["n_mlo_mapped"][0], 1)#SLO 1 - MOD 3 
        self.assertEqual(main_body_table[2]["n_mlo_mapped"][1], 0)#SLO 2 - MOD 3
        self.assertEqual(main_body_table[2]["n_mlo_mapped"][2], 2)#SLO 3 - MOD 3
        self.assertEqual(len(main_body_table[3]["n_mlo_mapped"]), 3)
        self.assertEqual(main_body_table[3]["n_mlo_mapped"][0], 0)#SLO 1 - MOD 4 
        self.assertEqual(main_body_table[3]["n_mlo_mapped"][1], 1)#SLO 2 - MOD 4
        self.assertEqual(main_body_table[3]["n_mlo_mapped"][2], 0)#SLO 3 - MOD 4

        #Test the calculation of the rows containing the totals -> number of MLOs per SLO
        total_n_mods_row = big_table['totals_n_mlo_row']
        self.assertEqual(len(total_n_mods_row),3)#3 SLOS
        self.assertEqual(total_n_mods_row[0], 3+2+1)#MOD 1 (3 mlos), MOD 2 (2 mlos), MOD 3 (1 mlos) map to SLO 1
        self.assertEqual(total_n_mods_row[1], 2+1+1)#MOD 1 (2 mlos), MOD 2 (1 mlos), MOD 4 (1 mlos) map to SLO 2
        self.assertEqual(total_n_mods_row[2], 2+1+2)#MOD 1 (2 mlos), MOD 2 (1 mlos), MOD 3 (2 mlos) map to SLO 3
        
        #Test the calculation of the rows containing the totals -> total overall strength
        total_strength_row = big_table['totals_strengths_row']
        self.assertEqual(len(total_strength_row),3)#3 SLOS
        self.assertEqual(total_strength_row[0], 3+2+1+2+3+2)#MOD 1 (3+2+1), MOD 2 (2+3), MOD 3 (2) map to SLO 1
        self.assertEqual(total_strength_row[1], 3+2+3+1)#MOD 1 (3+2), MOD 2 (3), MOD 4 (1) map to SLO 2
        self.assertEqual(total_strength_row[2], 1+2+1+3+3)#MOD 1 (1+2), MOD 2 (1), MOD 3 (3+3) map to SLO 3

        #Now test the view (up to now testing only the helper methods)
        response = self.client.get(reverse('workload_app:accreditation_report',  kwargs={'programme_id': prog_to_accredit.id, 
                                                                                         'start_year' : 2020, 'end_year':2021}))
        self.assertEqual(response.status_code, 200) #No issues

        self.assertEqual(response.context['programme_id'], prog_to_accredit.id)
        self.assertEqual(response.context['programme_name'], prog_to_accredit.programme_name)
        self.assertEqual(response.context['start_year'], 2020)
        self.assertEqual(response.context['end_year'], 2021)
        self.assertEqual(len(response.context['slo_measures']),StudentLearningOutcome.objects.filter(programme__id = prog_to_accredit.id).count())
        main_body_table = CalculateTableForOverallSLOMapping(prog_to_accredit.id, 2020,2021)['main_body_table']
        self.assertEqual(len(main_body_table), 0) #No workloads in the period
        self.assertEqual(len(response.context['big_mlo_slo_table']),len(main_body_table))

        