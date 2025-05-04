import datetime
from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *
from workload_app.global_constants import DEFAULT_TRACK_NAME,DEFAULT_SERVICE_ROLE_NAME, accreditation_outcome_type
from workload_app.models import StudentLearningOutcome, ProgrammeOffered, Faculty, Department, ModuleType, Module,WorkloadScenario, Academicyear,\
                                ModuleLearningOutcome,MLOSLOMapping,MLOPerformanceMeasure,Survey,SurveyQuestionResponse,\
                                ProgrammeEducationalObjective, EmploymentTrack, ServiceRole, Lecturer, TeachingAssignment, UniversityStaff
from workload_app.helper_methods_accreditation import CalculateTableForSLOSurveys,CalculateTableForMLOSurveys, CalculateTableForMLODirectMeasures,\
                                                        CalculateTableForOverallSLOMapping,DetermineIconBasedOnStrength, CalculateMLOSLOMappingTable,\
                                                        CalculateAllInforAboutOneSLO, DisplayOutcomeValidity,IsOutcomeValidForYear, CalculateAttentionScoresSummaryTable


class TestAccreditationReport(TestCase):
    def setup_user(self):
        #The test client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
        self.user.is_superuser = True
        self.user.save()
        uni_user = UniversityStaff.objects.create(user = self.user, department=None,faculty=None)

    def test_outcome_validity(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        #create 4 academic years
        start_year = 2012
        acad_year_1 = Academicyear.objects.create(start_year=start_year)
        acad_year_4 = Academicyear.objects.create(start_year=start_year+3)

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        new_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        prog_to_accredit = ProgrammeOffered.objects.create(programme_name="test_prog", primary_dept = new_dept)

        #Valid from 2012 to 2015
        slo_1 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_1', \
                                                      slo_short_description = 'slo_1', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'a',
                                                      cohort_valid_from = acad_year_1,
                                                      cohort_valid_to = acad_year_4,
                                                      programme = prog_to_accredit)
        #Valid from 2012 onwards
        slo_2 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_2', \
                                                      slo_short_description = 'slo_2', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'b',
                                                      cohort_valid_from = acad_year_1,
                                                      programme = prog_to_accredit)
        #Valid until 2015
        slo_3 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_3', \
                                                      slo_short_description = 'slo_3', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'c',
                                                      cohort_valid_to = acad_year_4,
                                                      programme = prog_to_accredit)
        #Always valid (default NULL years)
        slo_4 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_4', \
                                                      slo_short_description = 'slo_4', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'd',
                                                      programme = prog_to_accredit)
        #Test the display strings
        display_string_1 = DisplayOutcomeValidity(slo_1.id, accreditation_outcome_type.SLO)
        display_string_2 = DisplayOutcomeValidity(slo_2.id, accreditation_outcome_type.SLO)
        display_string_3 = DisplayOutcomeValidity(slo_3.id, accreditation_outcome_type.SLO)
        display_string_4 = DisplayOutcomeValidity(slo_4.id, accreditation_outcome_type.SLO)
        self.assertEqual(display_string_1, "Valid from 2012-2013 until 2015-2016")
        self.assertEqual(display_string_2, "Valid since 2012-2013")
        self.assertEqual(display_string_3, "Valid until 2015-2016")
        self.assertEqual(display_string_4, "Always")
        #Test the true/false method
        self.assertEqual(IsOutcomeValidForYear(slo_1.id,accreditation_outcome_type.SLO,2011), False)#Starts in 2012
        self.assertEqual(IsOutcomeValidForYear(slo_1.id,accreditation_outcome_type.SLO,2012), True)
        self.assertEqual(IsOutcomeValidForYear(slo_1.id,accreditation_outcome_type.SLO,2013), True)
        self.assertEqual(IsOutcomeValidForYear(slo_1.id,accreditation_outcome_type.SLO,2014), True)
        self.assertEqual(IsOutcomeValidForYear(slo_1.id,accreditation_outcome_type.SLO,2015), True)
        self.assertEqual(IsOutcomeValidForYear(slo_1.id,accreditation_outcome_type.SLO,2016), False)

        self.assertEqual(IsOutcomeValidForYear(slo_2.id,accreditation_outcome_type.SLO,2011), False)#Starts in 2012
        self.assertEqual(IsOutcomeValidForYear(slo_2.id,accreditation_outcome_type.SLO,2012), True)
        self.assertEqual(IsOutcomeValidForYear(slo_2.id,accreditation_outcome_type.SLO,2013), True)
        self.assertEqual(IsOutcomeValidForYear(slo_2.id,accreditation_outcome_type.SLO,2014), True)
        self.assertEqual(IsOutcomeValidForYear(slo_2.id,accreditation_outcome_type.SLO,2015), True)
        self.assertEqual(IsOutcomeValidForYear(slo_2.id,accreditation_outcome_type.SLO,2016), True)#Noe nd dat for this one

        self.assertEqual(IsOutcomeValidForYear(slo_3.id,accreditation_outcome_type.SLO,2011), True)#No start date for this one
        self.assertEqual(IsOutcomeValidForYear(slo_3.id,accreditation_outcome_type.SLO,2012), True)
        self.assertEqual(IsOutcomeValidForYear(slo_3.id,accreditation_outcome_type.SLO,2013), True)
        self.assertEqual(IsOutcomeValidForYear(slo_3.id,accreditation_outcome_type.SLO,2014), True)
        self.assertEqual(IsOutcomeValidForYear(slo_3.id,accreditation_outcome_type.SLO,2015), True)
        self.assertEqual(IsOutcomeValidForYear(slo_3.id,accreditation_outcome_type.SLO,2016), False)

        self.assertEqual(IsOutcomeValidForYear(slo_4.id,accreditation_outcome_type.SLO,2011), True)#No start date for this one
        self.assertEqual(IsOutcomeValidForYear(slo_4.id,accreditation_outcome_type.SLO,2012), True)
        self.assertEqual(IsOutcomeValidForYear(slo_4.id,accreditation_outcome_type.SLO,2013), True)
        self.assertEqual(IsOutcomeValidForYear(slo_4.id,accreditation_outcome_type.SLO,2014), True)
        self.assertEqual(IsOutcomeValidForYear(slo_4.id,accreditation_outcome_type.SLO,2015), True)
        self.assertEqual(IsOutcomeValidForYear(slo_4.id,accreditation_outcome_type.SLO,2016), True)#No end date

        #Valid from 2012 to 2015
        peo_1 = ProgrammeEducationalObjective.objects.create(peo_description = 'This is peo_1', \
                                                      peo_short_description = 'peo_1', \
                                                      letter_associated  = 'a',
                                                      peo_cohort_valid_from = acad_year_1,
                                                      peo_cohort_valid_to = acad_year_4,
                                                      programme = prog_to_accredit)
        #Valid from 2012 onwards
        peo_2 = ProgrammeEducationalObjective.objects.create(peo_description = 'This is peo_2', \
                                                      peo_short_description = 'peo_2', \
                                                      letter_associated  = 'b',
                                                      peo_cohort_valid_from = acad_year_1,
                                                      programme = prog_to_accredit)
        #Valid until 2015
        peo_3 = ProgrammeEducationalObjective.objects.create(peo_description = 'This is peo_3', \
                                                      peo_short_description = 'peo_3', \
                                                      letter_associated  = 'c',
                                                      peo_cohort_valid_to = acad_year_4,
                                                      programme = prog_to_accredit)
        #Always valid (default NULL years)
        peo_4 = ProgrammeEducationalObjective.objects.create(peo_description = 'This is peo_4', \
                                                      peo_short_description = 'peo_4', \
                                                      letter_associated  = 'd',
                                                      programme = prog_to_accredit)
        #Test the display strings
        display_string_1 = DisplayOutcomeValidity(peo_1.id, accreditation_outcome_type.PEO)
        display_string_2 = DisplayOutcomeValidity(peo_2.id, accreditation_outcome_type.PEO)
        display_string_3 = DisplayOutcomeValidity(peo_3.id, accreditation_outcome_type.PEO)
        display_string_4 = DisplayOutcomeValidity(peo_4.id, accreditation_outcome_type.PEO)
        self.assertEqual(display_string_1, "Valid from 2012-2013 until 2015-2016")
        self.assertEqual(display_string_2, "Valid since 2012-2013")
        self.assertEqual(display_string_3, "Valid until 2015-2016")
        self.assertEqual(display_string_4, "Always")

        #Test the true/false method
        self.assertEqual(IsOutcomeValidForYear(peo_1.id,accreditation_outcome_type.PEO,2011), False)#Starts in 2012
        self.assertEqual(IsOutcomeValidForYear(peo_1.id,accreditation_outcome_type.PEO,2012), True)
        self.assertEqual(IsOutcomeValidForYear(peo_1.id,accreditation_outcome_type.PEO,2013), True)
        self.assertEqual(IsOutcomeValidForYear(peo_1.id,accreditation_outcome_type.PEO,2014), True)
        self.assertEqual(IsOutcomeValidForYear(peo_1.id,accreditation_outcome_type.PEO,2015), True)
        self.assertEqual(IsOutcomeValidForYear(peo_1.id,accreditation_outcome_type.PEO,2016), False)

        self.assertEqual(IsOutcomeValidForYear(peo_2.id,accreditation_outcome_type.PEO,2011), False)#Starts in 2012
        self.assertEqual(IsOutcomeValidForYear(peo_2.id,accreditation_outcome_type.PEO,2012), True)
        self.assertEqual(IsOutcomeValidForYear(peo_2.id,accreditation_outcome_type.PEO,2013), True)
        self.assertEqual(IsOutcomeValidForYear(peo_2.id,accreditation_outcome_type.PEO,2014), True)
        self.assertEqual(IsOutcomeValidForYear(peo_2.id,accreditation_outcome_type.PEO,2015), True)
        self.assertEqual(IsOutcomeValidForYear(peo_2.id,accreditation_outcome_type.PEO,2016), True)#Noe nd dat for this one

        self.assertEqual(IsOutcomeValidForYear(peo_3.id,accreditation_outcome_type.PEO,2011), True)#No start date for this one
        self.assertEqual(IsOutcomeValidForYear(peo_3.id,accreditation_outcome_type.PEO,2012), True)
        self.assertEqual(IsOutcomeValidForYear(peo_3.id,accreditation_outcome_type.PEO,2013), True)
        self.assertEqual(IsOutcomeValidForYear(peo_3.id,accreditation_outcome_type.PEO,2014), True)
        self.assertEqual(IsOutcomeValidForYear(peo_3.id,accreditation_outcome_type.PEO,2015), True)
        self.assertEqual(IsOutcomeValidForYear(peo_3.id,accreditation_outcome_type.PEO,2016), False)

        self.assertEqual(IsOutcomeValidForYear(peo_4.id,accreditation_outcome_type.PEO,2011), True)#No start date for this one
        self.assertEqual(IsOutcomeValidForYear(peo_4.id,accreditation_outcome_type.PEO,2012), True)
        self.assertEqual(IsOutcomeValidForYear(peo_4.id,accreditation_outcome_type.PEO,2013), True)
        self.assertEqual(IsOutcomeValidForYear(peo_4.id,accreditation_outcome_type.PEO,2014), True)
        self.assertEqual(IsOutcomeValidForYear(peo_4.id,accreditation_outcome_type.PEO,2015), True)
        self.assertEqual(IsOutcomeValidForYear(peo_4.id,accreditation_outcome_type.PEO,2016), True)#No end date

        mod_code_1 = 'AA101'
        mod_code_2 = 'AA201'
        mod_code_3 = 'AA301'
        mod_code_4 = 'AA401'

        mlo_1 = ModuleLearningOutcome.objects.create(mlo_description = "hello1", mlo_short_description = 'h4', module_code = mod_code_4,\
            mlo_valid_from = acad_year_1, mlo_valid_to = acad_year_4)
        mlo_2 = ModuleLearningOutcome.objects.create(mlo_description = "hello2", mlo_short_description = 'h2', module_code = mod_code_2,\
            mlo_valid_from = acad_year_1)
        mlo_3 = ModuleLearningOutcome.objects.create(mlo_description = "hello3", mlo_short_description = 'h3', module_code = mod_code_3,\
            mlo_valid_to = acad_year_4)
        mlo_4 = ModuleLearningOutcome.objects.create(mlo_description = "hello4", mlo_short_description = 'h1', module_code = mod_code_1)

        #Test the display strings
        display_string_1 = DisplayOutcomeValidity(mlo_1.id, accreditation_outcome_type.MLO)
        display_string_2 = DisplayOutcomeValidity(mlo_2.id, accreditation_outcome_type.MLO)
        display_string_3 = DisplayOutcomeValidity(mlo_3.id, accreditation_outcome_type.MLO)
        display_string_4 = DisplayOutcomeValidity(mlo_4.id, accreditation_outcome_type.MLO)
        self.assertEqual(display_string_1, "Valid from 2012-2013 until 2015-2016")
        self.assertEqual(display_string_2, "Valid since 2012-2013")
        self.assertEqual(display_string_3, "Valid until 2015-2016")
        self.assertEqual(display_string_4, "Always")

        #Test the true/false method
        self.assertEqual(IsOutcomeValidForYear(mlo_1.id,accreditation_outcome_type.MLO,2011), False)#Starts in 2012
        self.assertEqual(IsOutcomeValidForYear(mlo_1.id,accreditation_outcome_type.MLO,2012), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_1.id,accreditation_outcome_type.MLO,2013), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_1.id,accreditation_outcome_type.MLO,2014), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_1.id,accreditation_outcome_type.MLO,2015), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_1.id,accreditation_outcome_type.MLO,2016), False)#Ends in 2015

        self.assertEqual(IsOutcomeValidForYear(mlo_2.id,accreditation_outcome_type.MLO,2011), False)#Starts in 2012
        self.assertEqual(IsOutcomeValidForYear(mlo_2.id,accreditation_outcome_type.MLO,2012), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_2.id,accreditation_outcome_type.MLO,2013), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_2.id,accreditation_outcome_type.MLO,2014), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_2.id,accreditation_outcome_type.MLO,2015), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_2.id,accreditation_outcome_type.MLO,2016), True)#No end dat for this one

        self.assertEqual(IsOutcomeValidForYear(mlo_3.id,accreditation_outcome_type.MLO,2011), True)#No start date for this one
        self.assertEqual(IsOutcomeValidForYear(mlo_3.id,accreditation_outcome_type.MLO,2012), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_3.id,accreditation_outcome_type.MLO,2013), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_3.id,accreditation_outcome_type.MLO,2014), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_3.id,accreditation_outcome_type.MLO,2015), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_3.id,accreditation_outcome_type.MLO,2016), False)#ends in 2015

        self.assertEqual(IsOutcomeValidForYear(mlo_4.id,accreditation_outcome_type.MLO,2011), True)#No start date for this one
        self.assertEqual(IsOutcomeValidForYear(mlo_4.id,accreditation_outcome_type.MLO,2012), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_4.id,accreditation_outcome_type.MLO,2013), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_4.id,accreditation_outcome_type.MLO,2014), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_4.id,accreditation_outcome_type.MLO,2015), True)
        self.assertEqual(IsOutcomeValidForYear(mlo_4.id,accreditation_outcome_type.MLO,2016), True)#No end date

    def test_report_simple(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        #create 4 academic years
        start_year = 2012
        acad_year_1 = Academicyear.objects.create(start_year=start_year)
        acad_year_2 = Academicyear.objects.create(start_year=start_year+1)
        acad_year_3 = Academicyear.objects.create(start_year=start_year+2)
        acad_year_4 = Academicyear.objects.create(start_year=start_year+3)
        out_of_range_aa_1 = Academicyear.objects.create(start_year=start_year-30)
        out_of_range_aa_2 = Academicyear.objects.create(start_year=start_year-20)

        #Create 4 worklaod scenarios
        scenario_1 = WorkloadScenario.objects.create(label='a workload 1', academic_year=acad_year_1, status = WorkloadScenario.OFFICIAL)
        scenario_2 = WorkloadScenario.objects.create(label='a workload 2', academic_year=acad_year_2, status = WorkloadScenario.OFFICIAL)
        scenario_3 = WorkloadScenario.objects.create(label='a workload 3', academic_year=acad_year_3, status = WorkloadScenario.OFFICIAL)
        scenario_4 = WorkloadScenario.objects.create(label='a workload 4', academic_year=acad_year_4, status = WorkloadScenario.OFFICIAL)
        scenario_4_draft = WorkloadScenario.objects.create(label='a workload 4', academic_year=acad_year_1, status = WorkloadScenario.DRAFT)

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        new_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        prog_to_accredit = ProgrammeOffered.objects.create(programme_name="test_prog", primary_dept = new_dept)
        prog_to_accredit_2 = ProgrammeOffered.objects.create(programme_name="test_prog_2", primary_dept = new_dept)
        prog_to_accredit_3 = ProgrammeOffered.objects.create(programme_name="test_prog_3", primary_dept = new_dept)
        track_1 = EmploymentTrack.objects.create(track_name = "track_1", track_adjustment = 2.0, is_adjunct = False)
        service_role_1 = ServiceRole.objects.create(role_name = "role_1", role_adjustment = 2.0)

        #Create SLOs
        slo_1_prog_1 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_1', \
                                                      slo_short_description = 'slo_1', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'a',
                                                      programme = prog_to_accredit)

        slo_2_prog_1 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_2', \
                                                      slo_short_description = 'slo_2', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'b',
                                                      programme = prog_to_accredit)
        slo_3_prog_1 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_3', \
                                                      slo_short_description = 'slo_3', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'c',
                                                      programme = prog_to_accredit)
        #Create SLOs - prog 2
        slo_1_prog_2 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_1', \
                                                      slo_short_description = 'slo_1', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'a',
                                                      programme = prog_to_accredit_2)

        slo_2_prog_2 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_2', \
                                                      slo_short_description = 'slo_2', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'b',
                                                      programme = prog_to_accredit_2)
        slo_3_prog_2 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_3', \
                                                      slo_short_description = 'slo_3', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'c',
                                                      programme = prog_to_accredit_2)
        #Create SLOs - prog 3
        slo_1_prog_3 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_1', \
                                                      slo_short_description = 'slo_1', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'a',
                                                      programme = prog_to_accredit_3)

        slo_2_prog_3 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_2', \
                                                      slo_short_description = 'slo_2', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'b',
                                                      programme = prog_to_accredit_3)
        slo_3_prog_3 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_3', \
                                                      slo_short_description = 'slo_3', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'c',
                                                      programme = prog_to_accredit_3)
        #Create a lecturer, a module and an assignment
        mod_code_1 = "AA101"
        mod_code_2 = "AA102"
        new_lec_1 = Lecturer.objects.create(name='Bob', fraction_appointment=1.0,workload_scenario=scenario_1,employment_track = track_1, service_role=service_role_1)
        #Mod 1 is compulsory in all 3 programmes
        mod_1 = Module.objects.create(module_code = mod_code_1, module_title = mod_code_1+'-title', scenario_ref=scenario_1,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True,\
                                                                     secondary_programme = prog_to_accredit_2, compulsory_in_secondary_programme = True,\
                                                                     tertiary_programme = prog_to_accredit_3, compulsory_in_tertiary_programme = True,students_year_of_study=1)
        #Mod 2 is elective in the primary and compulsory in the secondary. Does not have a teritiary
        mod_2 = Module.objects.create(module_code = mod_code_2, module_title = mod_code_2+'-title', scenario_ref=scenario_1,primary_programme = prog_to_accredit, compulsory_in_primary_programme = False,\
                                                                     secondary_programme = prog_to_accredit_2, compulsory_in_secondary_programme = True,students_year_of_study=1)
        mlo_mod_1 =  ModuleLearningOutcome.objects.create(mlo_description = "MLO_1-mod 1", mlo_short_description="short-MLO_1-mod 1", module_code = mod_code_1)
        mlo_mod_2 =  ModuleLearningOutcome.objects.create(mlo_description = "MLO_1-mod 2", mlo_short_description="short-MLO_1-mod 2", module_code = mod_code_2)

        #MLO1 maps to slo A of prog 1, slo B of prog 2 and slo C of prog 3
        mod_1_prog_1 = MLOSLOMapping.objects.create(mlo = mlo_mod_1, slo=slo_1_prog_1, strength = 3)
        mod_1_prog_2 = MLOSLOMapping.objects.create(mlo = mlo_mod_1, slo=slo_2_prog_2, strength = 3)
        mod_1_prog_2 = MLOSLOMapping.objects.create(mlo = mlo_mod_1, slo=slo_3_prog_3, strength = 3)
        #MLO for MOD 2 is mapped to sLO3 of prog 1 and SLO1 of prog 2 (no prog 3)
        mod_2_prog_1 = MLOSLOMapping.objects.create(mlo = mlo_mod_2, slo=slo_3_prog_1, strength = 3)
        mod_2_prog_2 = MLOSLOMapping.objects.create(mlo = mlo_mod_2, slo=slo_1_prog_2, strength = 3)
        
        #Test the big slo mlo table - PROG 1
        #COmpulsory only (only mod 1 shows up)
        main_body_table = CalculateTableForOverallSLOMapping(prog_to_accredit.id, 2020,2021, compulsory_only=1)['main_body_table']
        self.assertEqual(len(main_body_table), 0) #No workloads in the period
        big_table = CalculateTableForOverallSLOMapping(prog_to_accredit.id, 2010,2021,compulsory_only=1)
        main_body_table = big_table['main_body_table']
        self.assertEqual(len(main_body_table), 1) 
        self.assertEqual(main_body_table[0]["module_code"], mod_code_1)
        self.assertEqual(len(main_body_table[0]["slo_identifiers"]), 3)
        self.assertEqual(len(main_body_table[0]["numerical_mappings"]), 3)
        self.assertEqual(main_body_table[0]["numerical_mappings"][0], 3)#SLO 1 - MOD 1 
        self.assertEqual(main_body_table[0]["numerical_mappings"][1], 0)#SLO 2 - MOD 1
        self.assertEqual(main_body_table[0]["numerical_mappings"][2], 0)#SLO 3 - MOD 1
        #All modules - mod 2 should show up as well
        big_table = CalculateTableForOverallSLOMapping(prog_to_accredit.id, 2010,2021,compulsory_only=0)
        main_body_table = big_table['main_body_table']
        self.assertEqual(len(main_body_table), 2) 
        self.assertEqual(main_body_table[0]["module_code"], mod_code_1)
        self.assertEqual(len(main_body_table[0]["slo_identifiers"]), 3)
        self.assertEqual(len(main_body_table[0]["numerical_mappings"]), 3)
        self.assertEqual(main_body_table[0]["numerical_mappings"][0], 3)#SLO 1 - MOD 1 
        self.assertEqual(main_body_table[0]["numerical_mappings"][1], 0)#SLO 2 - MOD 1
        self.assertEqual(main_body_table[0]["numerical_mappings"][2], 0)#SLO 3 - MOD 1
        self.assertEqual(main_body_table[1]["module_code"], mod_code_2)
        self.assertEqual(len(main_body_table[1]["slo_identifiers"]), 3)
        self.assertEqual(len(main_body_table[1]["numerical_mappings"]), 3)
        self.assertEqual(main_body_table[1]["numerical_mappings"][0], 0)#SLO 1 - MOD 2 
        self.assertEqual(main_body_table[1]["numerical_mappings"][1], 0)#SLO 2 - MOD 2
        self.assertEqual(main_body_table[1]["numerical_mappings"][2], 3)#SLO 3 - MOD 2

        #Test the big slo mlo table - PROG 2
        #Compulosry only - both modules should show up
        big_table = CalculateTableForOverallSLOMapping(prog_to_accredit_2.id, 2010,2021,compulsory_only=1)
        main_body_table = big_table['main_body_table']
        self.assertEqual(len(main_body_table), 2) 
        self.assertEqual(main_body_table[0]["module_code"], mod_code_1)
        self.assertEqual(len(main_body_table[0]["slo_identifiers"]), 3)
        self.assertEqual(len(main_body_table[0]["numerical_mappings"]), 3)
        self.assertEqual(main_body_table[0]["numerical_mappings"][0], 0)#SLO 1 - MOD 1 
        self.assertEqual(main_body_table[0]["numerical_mappings"][1], 3)#SLO 2 - MOD 1
        self.assertEqual(main_body_table[0]["numerical_mappings"][2], 0)#SLO 3 - MOD 1
        self.assertEqual(main_body_table[1]["module_code"], mod_code_2)
        self.assertEqual(len(main_body_table[1]["slo_identifiers"]), 3)
        self.assertEqual(len(main_body_table[1]["numerical_mappings"]), 3)
        self.assertEqual(main_body_table[1]["numerical_mappings"][0], 3)#SLO 1 - MOD 2 
        self.assertEqual(main_body_table[1]["numerical_mappings"][1], 0)#SLO 2 - MOD 2
        self.assertEqual(main_body_table[1]["numerical_mappings"][2], 0)#SLO 3 - MOD 2
        #All modules - both modules should show up
        big_table = CalculateTableForOverallSLOMapping(prog_to_accredit_2.id, 2010,2021,compulsory_only=0)
        main_body_table = big_table['main_body_table']
        self.assertEqual(len(main_body_table), 2) 
        self.assertEqual(main_body_table[0]["module_code"], mod_code_1)
        self.assertEqual(len(main_body_table[0]["slo_identifiers"]), 3)
        self.assertEqual(len(main_body_table[0]["numerical_mappings"]), 3)
        self.assertEqual(main_body_table[0]["numerical_mappings"][0], 0)#SLO 1 - MOD 1 
        self.assertEqual(main_body_table[0]["numerical_mappings"][1], 3)#SLO 2 - MOD 1
        self.assertEqual(main_body_table[0]["numerical_mappings"][2], 0)#SLO 3 - MOD 1
        self.assertEqual(main_body_table[1]["module_code"], mod_code_2)
        self.assertEqual(len(main_body_table[1]["slo_identifiers"]), 3)
        self.assertEqual(len(main_body_table[1]["numerical_mappings"]), 3)
        self.assertEqual(main_body_table[1]["numerical_mappings"][0], 3)#SLO 1 - MOD 2 
        self.assertEqual(main_body_table[1]["numerical_mappings"][1], 0)#SLO 2 - MOD 2
        self.assertEqual(main_body_table[1]["numerical_mappings"][2], 0)#SLO 3 - MOD 2

        #Test the big slo mlo table - PROG 3
        #COmpulsory only (only mod 1 shows up)
        big_table = CalculateTableForOverallSLOMapping(prog_to_accredit_3.id, 2010,2021,compulsory_only=1)
        main_body_table = big_table['main_body_table']
        self.assertEqual(len(main_body_table), 1) 
        self.assertEqual(main_body_table[0]["module_code"], mod_code_1)
        self.assertEqual(len(main_body_table[0]["slo_identifiers"]), 3)
        self.assertEqual(len(main_body_table[0]["numerical_mappings"]), 3)
        self.assertEqual(main_body_table[0]["numerical_mappings"][0], 0)#SLO 1 - MOD 1 
        self.assertEqual(main_body_table[0]["numerical_mappings"][1], 0)#SLO 2 - MOD 1
        self.assertEqual(main_body_table[0]["numerical_mappings"][2], 3)#SLO 3 - MOD 1
        #All module only (only mod 1 shows up, same as above) - MOD 2 not present in prg 3
        big_table = CalculateTableForOverallSLOMapping(prog_to_accredit_3.id, 2010,2021,compulsory_only=1)
        main_body_table = big_table['main_body_table']
        self.assertEqual(len(main_body_table), 1) 
        self.assertEqual(main_body_table[0]["module_code"], mod_code_1)
        self.assertEqual(len(main_body_table[0]["slo_identifiers"]), 3)
        self.assertEqual(len(main_body_table[0]["numerical_mappings"]), 3)
        self.assertEqual(main_body_table[0]["numerical_mappings"][0], 0)#SLO 1 - MOD 1 
        self.assertEqual(main_body_table[0]["numerical_mappings"][1], 0)#SLO 2 - MOD 1
        self.assertEqual(main_body_table[0]["numerical_mappings"][2], 3)#SLO 3 - MOD 1

        assign_comp = TeachingAssignment.objects.create(assigned_module = mod_1, assigned_lecturer=new_lec_1, workload_scenario = scenario_1, number_of_hours = 15) 
        assign_elective = TeachingAssignment.objects.create(assigned_module = mod_2, assigned_lecturer=new_lec_1, workload_scenario = scenario_1, number_of_hours = 15)

        measure_mod_1 = MLOPerformanceMeasure.objects.create(description = 'test 1', academic_year = acad_year_1, associated_mlo = mlo_mod_1,percentage_score=45)
        measure_mod_2 = MLOPerformanceMeasure.objects.create(description = 'test 2', academic_year = acad_year_1, associated_mlo = mlo_mod_2,percentage_score=90)
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),2)
        #Call for programme 1, compulosry only, module 2 is not compulosry and should not show up
        table_slo_1 = CalculateTableForMLODirectMeasures(slo_id = slo_1_prog_1.id,start_year = acad_year_1.start_year, end_year = acad_year_2.start_year, compulsory_only=1)
        self.assertEqual(len(table_slo_1), 2)#one measure plus the totals row
        self.assertEqual(len(table_slo_1[0]), 3)
        self.assertEqual(len(table_slo_1[1]), 3)
        self.assertEqual(table_slo_1[0][0], mod_code_1)
        self.assertEqual(table_slo_1[0][1], 45)#one measure in first academic year
        self.assertEqual(table_slo_1[0][2], '')#no measure in second academic year
        self.assertEqual(table_slo_1[1][0], 'Weighted average')
        self.assertEqual(table_slo_1[1][1], 45)#Only one measure
        self.assertAlmostEqual(table_slo_1[1][2],0)#no measure in second academic year -> totals row is zero
        
        #Now include electives also: module 2 should show up for SLO 3 of prog 1
        table_slo_3 = CalculateTableForMLODirectMeasures(slo_id = slo_3_prog_1.id,start_year = acad_year_1.start_year, end_year = acad_year_2.start_year, compulsory_only=0)
        self.assertEqual(len(table_slo_3), 2)#1 measure plus the totals row
        self.assertEqual(len(table_slo_3[0]), 3)
        self.assertEqual(len(table_slo_3[1]), 3)
        self.assertEqual(table_slo_3[0][0], mod_code_2)
        self.assertEqual(table_slo_3[0][1], 90)#one measure in first academic year
        self.assertEqual(table_slo_3[0][2], '')#no measure in second academic year
        self.assertEqual(table_slo_3[1][0], 'Weighted average')
        self.assertAlmostEqual(table_slo_3[1][1], 90)#One measure
        self.assertAlmostEqual(table_slo_3[1][2],0)#no measure in second academic year -> totals row is zero

        #same as above, but asking for compulsory only. Module 2 should disappear.
        table_slo_3_compulsory = CalculateTableForMLODirectMeasures(slo_id = slo_3_prog_1.id,start_year = acad_year_1.start_year, end_year = acad_year_2.start_year, compulsory_only=1)
        self.assertEqual(len(table_slo_3_compulsory), 1)#No measures, only the totals row
        self.assertEqual(len(table_slo_3_compulsory[0]), 3)
        self.assertEqual(table_slo_3_compulsory[0][0], 'Weighted average')
        self.assertAlmostEqual(table_slo_3_compulsory[0][1], 0)#No measure
        self.assertAlmostEqual(table_slo_3_compulsory[0][2],0)#no measure

        ###DO MLO surveys now - we survey MLO for module 2
        mlo_survey = Survey.objects.create(survey_title = "first mlo survey for mod 2", opening_date = datetime.datetime(2012, 9, 17),\
                                                                                closing_date = datetime.datetime(2012, 9, 27),\
                                                                                cohort_targeted = acad_year_1,\
                                                                                programme_associated = prog_to_accredit,\
                                                                                max_respondents = 100)
        #Create the responses
        response_1 = SurveyQuestionResponse.objects.create(question_text = mlo_mod_2.mlo_description,\
                                                           n_highest_score = 50,\
                                                           n_second_highest_score = 30,\
                                                           n_third_highest_score = 5,\
                                                           n_fourth_highest_score = 15,\
                                                           associated_mlo = mlo_mod_2,\
                                                           parent_survey = mlo_survey )
        props = response_1.CalculateRepsonsesProprties()
        # #Generate the table for SLO 3, programme 1 - Including electives (module 2 should show up)
        mlo_table_slo_3 = CalculateTableForMLOSurveys(slo_id = slo_3_prog_1.id,start_year = 2012, end_year = 2013, compulsory_only=0)
        self.assertEqual(len(mlo_table_slo_3), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_3[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_3[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_3[0][0], mlo_mod_2.module_code)
        self.assertAlmostEqual(mlo_table_slo_3[0][1],props['percentage_positive'])#MLO of module 2 mapped to slo 3
        self.assertAlmostEqual(mlo_table_slo_3[0][2],'')#Nothing in 2013
        self.assertEqual(mlo_table_slo_3[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_3[1][1],props['percentage_positive'])#MLO 1of module 3 mapped to slo 3
        self.assertAlmostEqual(mlo_table_slo_3[1][2],0)#Nothing in 2013

        # Do the same, table for SLO 3, programme 1 - Including compulsory only: module 2 should disappear
        mlo_table_slo_3 = CalculateTableForMLOSurveys(slo_id = slo_3_prog_1.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(mlo_table_slo_3), 1)#Totals only
        self.assertEqual(len(mlo_table_slo_3[0]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_3[0][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_3[0][1],0)#Nothing
        self.assertAlmostEqual(mlo_table_slo_3[0][2],0)#Nothing in 2013

        #IF we calculate the table for SLO 1 of prog 2, compulsory only, mod 2 should appear
        # #Generate the table for SLO 1, programme 2 - compulsory only
        mlo_table_slo_1_2 = CalculateTableForMLOSurveys(slo_id = slo_1_prog_2.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(mlo_table_slo_1_2), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_1_2[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_1_2[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_1_2[0][0], mlo_mod_2.module_code)
        self.assertAlmostEqual(mlo_table_slo_1_2[0][1],props['percentage_positive'])#MLO of module 2 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_1_2[0][2],'')#Nothing in 2013
        self.assertEqual(mlo_table_slo_1_2[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_1_2[1][1],props['percentage_positive'])#MLO 1 of module 2 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_1_2[1][2],0)#Nothing in 2013



        #Test the attention score tables - PROG 1
        #Compulsory only first
        att_score_table = CalculateAttentionScoresSummaryTable(prog_to_accredit.id,2012,2013, compulsory_only=1)        
        #print(att_score_table)
        self.assertEqual(len(att_score_table),3)#There are 3 SLOs
        self.assertEqual(att_score_table[0]["letter"],'a')#first SLO, letter
        self.assertEqual(att_score_table[1]["letter"],'b')#second SLO, letter
        self.assertEqual(att_score_table[2]["letter"],'c')#third SLO, letter
        self.assertEqual(len(att_score_table[0]["attention_scores_direct"]),2)#2 years from 2102 to 2013 included
        self.assertEqual(len(att_score_table[0]["attention_scores_mlo_surveys"]),2)#2 years from 2102 to 2013 included
        self.assertEqual(len(att_score_table[0]["attention_scores_slo_surveys"]),2)#2 years from 2102 to 2013 included
        self.assertEqual(len(att_score_table[1]["attention_scores_direct"]),2)#2 years from 2102 to 2013 included
        self.assertEqual(len(att_score_table[1]["attention_scores_mlo_surveys"]),2)#2 years from 2102 to 2013 included
        self.assertEqual(len(att_score_table[1]["attention_scores_slo_surveys"]),2)#2 years from 2102 to 2013 included

        self.assertAlmostEqual(att_score_table[0]["attention_scores_direct"][0],1)#SLO a, direct measures, 2012 -> There is one mapping, strength 3
        self.assertAlmostEqual(att_score_table[0]["attention_scores_direct"][1],0)#SLO a, direct measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[1]["attention_scores_direct"][0],0)#SLO b, direct measures, 2012 -> None
        self.assertAlmostEqual(att_score_table[1]["attention_scores_direct"][1],0)#SLO b, direct measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[2]["attention_scores_direct"][0],0)#SLO c, direct measures, 2012 -> One measure, but it is elective (no show)
        self.assertAlmostEqual(att_score_table[2]["attention_scores_direct"][1],0)#SLO c, direct measures, 2013 -> None

        self.assertAlmostEqual(att_score_table[0]["attention_scores_mlo_surveys"][0],0)#SLO a, MLO survey measures, 2012 ->None
        self.assertAlmostEqual(att_score_table[0]["attention_scores_mlo_surveys"][1],0)#SLO a, MLO  survey measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[1]["attention_scores_mlo_surveys"][0],0)#SLO b, MLO  survey measures, 2012 -> None
        self.assertAlmostEqual(att_score_table[1]["attention_scores_mlo_surveys"][1],0)#SLO b, MLO  survey measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[2]["attention_scores_mlo_surveys"][0],0)#SLO c, MLO  survey measures, 2012 -> One question, but it is elective (no show)
        self.assertAlmostEqual(att_score_table[2]["attention_scores_mlo_surveys"][1],0)#SLO c, MLO survey measures, 2013 -> None

        #Now same, but allow electives to be counted
        att_score_table = CalculateAttentionScoresSummaryTable(prog_to_accredit.id,2012,2013, compulsory_only=0)        
        #print(att_score_table)
        self.assertEqual(len(att_score_table),3)#There are 3 SLOs
        self.assertEqual(att_score_table[0]["letter"],'a')#first SLO, letter
        self.assertEqual(att_score_table[1]["letter"],'b')#second SLO, letter
        self.assertEqual(att_score_table[2]["letter"],'c')#third SLO, letter
        self.assertEqual(len(att_score_table[0]["attention_scores_direct"]),2)#2 years from 2102 to 2013 included
        self.assertEqual(len(att_score_table[0]["attention_scores_mlo_surveys"]),2)#2 years from 2102 to 2013 included
        self.assertEqual(len(att_score_table[0]["attention_scores_slo_surveys"]),2)#2 years from 2102 to 2013 included
        self.assertEqual(len(att_score_table[1]["attention_scores_direct"]),2)#2 years from 2102 to 2013 included
        self.assertEqual(len(att_score_table[1]["attention_scores_mlo_surveys"]),2)#2 years from 2102 to 2013 included
        self.assertEqual(len(att_score_table[1]["attention_scores_slo_surveys"]),2)#2 years from 2102 to 2013 included

        self.assertAlmostEqual(att_score_table[0]["attention_scores_direct"][0],1)#SLO a, direct measures, 2012 -> There is one measure, strength 3
        self.assertAlmostEqual(att_score_table[0]["attention_scores_direct"][1],0)#SLO a, direct measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[1]["attention_scores_direct"][0],0)#SLO b, direct measures, 2012 -> None
        self.assertAlmostEqual(att_score_table[1]["attention_scores_direct"][1],0)#SLO b, direct measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[2]["attention_scores_direct"][0],1)#SLO c, direct measures, 2012 -> One measure, ELECTIVE SHOULD SHOW UP
        self.assertAlmostEqual(att_score_table[2]["attention_scores_direct"][1],0)#SLO c, direct measures, 2013 -> None

        self.assertAlmostEqual(att_score_table[0]["attention_scores_mlo_surveys"][0],0)#SLO a, MLO survey measures, 2012 ->None
        self.assertAlmostEqual(att_score_table[0]["attention_scores_mlo_surveys"][1],0)#SLO a, MLO  survey measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[1]["attention_scores_mlo_surveys"][0],0)#SLO b, MLO  survey measures, 2012 -> None
        self.assertAlmostEqual(att_score_table[1]["attention_scores_mlo_surveys"][1],0)#SLO b, MLO  survey measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[2]["attention_scores_mlo_surveys"][0],1)#SLO c, MLO  survey measures, 2012 -> One question, ELECTIVE SHOULD SHOW UP
        self.assertAlmostEqual(att_score_table[2]["attention_scores_mlo_surveys"][1],0)#SLO c, MLO survey measures, 2013 -> None


    def test_report_realistic(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        #create 4 academic years
        start_year = 2012
        acad_year_1 = Academicyear.objects.create(start_year=start_year)
        acad_year_2 = Academicyear.objects.create(start_year=start_year+1)
        acad_year_3 = Academicyear.objects.create(start_year=start_year+2)
        acad_year_4 = Academicyear.objects.create(start_year=start_year+3)
        out_of_range_aa_1 = Academicyear.objects.create(start_year=start_year-30)
        out_of_range_aa_2 = Academicyear.objects.create(start_year=start_year-20)

        #Create 4 worklaod scenarios
        scenario_1 = WorkloadScenario.objects.create(label='a workload 1', academic_year=acad_year_1, status = WorkloadScenario.OFFICIAL)
        scenario_2 = WorkloadScenario.objects.create(label='a workload 2', academic_year=acad_year_2, status = WorkloadScenario.OFFICIAL)
        scenario_3 = WorkloadScenario.objects.create(label='a workload 3', academic_year=acad_year_3, status = WorkloadScenario.OFFICIAL)
        scenario_4 = WorkloadScenario.objects.create(label='a workload 4', academic_year=acad_year_4, status = WorkloadScenario.OFFICIAL)
        scenario_4_draft = WorkloadScenario.objects.create(label='a workload 4', academic_year=acad_year_1, status = WorkloadScenario.DRAFT)

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        new_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        prog_to_accredit = ProgrammeOffered.objects.create(programme_name="test_prog", primary_dept = new_dept)
        track_1 = EmploymentTrack.objects.create(track_name = "track_1", track_adjustment = 2.0, is_adjunct = False)
        service_role_1 = ServiceRole.objects.create(role_name = "role_1", role_adjustment = 2.0)
        #Create a lecturer (these will be in charge of all modules)
        new_lec_1 = Lecturer.objects.create(name='Bob', fraction_appointment=1.0,workload_scenario=scenario_1,employment_track = track_1, service_role=service_role_1)
        new_lec_2 = Lecturer.objects.create(name='Bob', fraction_appointment=1.0,workload_scenario=scenario_2,employment_track = track_1, service_role=service_role_1)
        new_lec_3 = Lecturer.objects.create(name='Bob', fraction_appointment=1.0,workload_scenario=scenario_3,employment_track = track_1, service_role=service_role_1)
        new_lec_4 = Lecturer.objects.create(name='Bob', fraction_appointment=1.0,workload_scenario=scenario_4,employment_track = track_1, service_role=service_role_1)
        new_lec_1_draft = Lecturer.objects.create(name='Bob', fraction_appointment=1.0,workload_scenario=scenario_4_draft,employment_track = track_1, service_role=service_role_1)
        
        mod_code_1 = 'AA101'
        mod_code_2 = 'AA201'
        mod_code_3 = 'AA301'
        mod_code_4 = 'AA401'
        #Module one present in 4 scenarios
        mod_1_1 = Module.objects.create(module_code = mod_code_1, module_title = mod_code_1+'-title', scenario_ref=scenario_1,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=1)
        mod_1_2 = Module.objects.create(module_code = mod_code_1, module_title = mod_code_1+'-title', scenario_ref=scenario_2,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=1)
        mod_1_3 = Module.objects.create(module_code = mod_code_1, module_title = mod_code_1+'-title', scenario_ref=scenario_3,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=1)
        mod_1_4 = Module.objects.create(module_code = mod_code_1, module_title = mod_code_1+'-title', scenario_ref=scenario_4,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=1)
        mod_1_1_draft = Module.objects.create(module_code = mod_code_1, module_title = mod_code_1+'-title', scenario_ref=scenario_4_draft,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=1)
        
        #Module two present in 4 scenarios
        mod_2_1 = Module.objects.create(module_code = mod_code_2, module_title = mod_code_2+'-title', scenario_ref=scenario_1,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=2)
        mod_2_2 = Module.objects.create(module_code = mod_code_2, module_title = mod_code_2+'-title', scenario_ref=scenario_2,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=2)
        mod_2_3 = Module.objects.create(module_code = mod_code_2, module_title = mod_code_2+'-title', scenario_ref=scenario_3,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=2)
        mod_2_4 = Module.objects.create(module_code = mod_code_2, module_title = mod_code_2+'-title', scenario_ref=scenario_4,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=2)

        #Module 3 present in 4 scenarios
        mod_3_1 = Module.objects.create(module_code = mod_code_3, module_title = mod_code_3+'-title', scenario_ref=scenario_1,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=3)
        mod_3_2 = Module.objects.create(module_code = mod_code_3, module_title = mod_code_3+'-title', scenario_ref=scenario_2,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=3)
        mod_3_3 = Module.objects.create(module_code = mod_code_3, module_title = mod_code_3+'-title', scenario_ref=scenario_3,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=3)
        mod_3_4 = Module.objects.create(module_code = mod_code_3, module_title = mod_code_3+'-title', scenario_ref=scenario_4,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=3)

        #Module 4 present in 4 scenarios
        mod_4_1 = Module.objects.create(module_code = mod_code_4, module_title = mod_code_4+'-title', scenario_ref=scenario_1,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=4)
        mod_4_2 = Module.objects.create(module_code = mod_code_4, module_title = mod_code_4+'-title', scenario_ref=scenario_2,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=4)
        mod_4_3 = Module.objects.create(module_code = mod_code_4, module_title = mod_code_4+'-title', scenario_ref=scenario_3,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=4)
        mod_4_4 = Module.objects.create(module_code = mod_code_4, module_title = mod_code_4+'-title', scenario_ref=scenario_4,primary_programme = prog_to_accredit, compulsory_in_primary_programme = True, students_year_of_study=4)

        self.assertEqual(Module.objects.all().count(),17)#16 OK, plus one in draft wl
        #Have all modules assigned
        assign_1_1 = TeachingAssignment.objects.create(assigned_module = mod_1_1, assigned_lecturer=new_lec_1, workload_scenario = scenario_1, number_of_hours = 15) 
        assign_1_2 = TeachingAssignment.objects.create(assigned_module = mod_1_2, assigned_lecturer=new_lec_2, workload_scenario = scenario_2, number_of_hours = 15)
        assign_1_3 = TeachingAssignment.objects.create(assigned_module = mod_1_3, assigned_lecturer=new_lec_3, workload_scenario = scenario_3, number_of_hours = 15)
        assign_1_4 = TeachingAssignment.objects.create(assigned_module = mod_1_4, assigned_lecturer=new_lec_4, workload_scenario = scenario_4, number_of_hours = 15)

        assign_1_1_draft = TeachingAssignment.objects.create(assigned_module = mod_1_1_draft, assigned_lecturer=new_lec_1_draft, workload_scenario = scenario_4_draft, number_of_hours = 15)

        assign_2_1 = TeachingAssignment.objects.create(assigned_module = mod_2_1, assigned_lecturer=new_lec_1, workload_scenario = scenario_1, number_of_hours = 15) 
        assign_2_2 = TeachingAssignment.objects.create(assigned_module = mod_2_2, assigned_lecturer=new_lec_2, workload_scenario = scenario_2, number_of_hours = 15)
        assign_2_3 = TeachingAssignment.objects.create(assigned_module = mod_2_3, assigned_lecturer=new_lec_3, workload_scenario = scenario_3, number_of_hours = 15)
        assign_2_4 = TeachingAssignment.objects.create(assigned_module = mod_2_4, assigned_lecturer=new_lec_4, workload_scenario = scenario_4, number_of_hours = 15)

        assign_3_1 = TeachingAssignment.objects.create(assigned_module = mod_3_1, assigned_lecturer=new_lec_1, workload_scenario = scenario_1, number_of_hours = 15) 
        assign_3_2 = TeachingAssignment.objects.create(assigned_module = mod_3_2, assigned_lecturer=new_lec_2, workload_scenario = scenario_2, number_of_hours = 15)
        assign_3_3 = TeachingAssignment.objects.create(assigned_module = mod_3_3, assigned_lecturer=new_lec_3, workload_scenario = scenario_3, number_of_hours = 15)
        assign_3_4 = TeachingAssignment.objects.create(assigned_module = mod_3_4, assigned_lecturer=new_lec_4, workload_scenario = scenario_4, number_of_hours = 15)

        assign_4_1 = TeachingAssignment.objects.create(assigned_module = mod_4_1, assigned_lecturer=new_lec_1, workload_scenario = scenario_1, number_of_hours = 15) 
        assign_4_2 = TeachingAssignment.objects.create(assigned_module = mod_4_2, assigned_lecturer=new_lec_2, workload_scenario = scenario_2, number_of_hours = 15)
        assign_4_3 = TeachingAssignment.objects.create(assigned_module = mod_4_3, assigned_lecturer=new_lec_3, workload_scenario = scenario_3, number_of_hours = 15)
        assign_4_4 = TeachingAssignment.objects.create(assigned_module = mod_4_4, assigned_lecturer=new_lec_4, workload_scenario = scenario_4, number_of_hours = 15)

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
        mlo_4_2_out_of_range = ModuleLearningOutcome.objects.create(mlo_description = "MLO_2-mod 4", mlo_short_description="short-MLO_2-mod 4", module_code = mod_code_4,\
                                                                    mlo_valid_from = out_of_range_aa_1, mlo_valid_to = out_of_range_aa_2)

        mlo_1_1_draft = ModuleLearningOutcome.objects.create(mlo_description = "MLO_1-mod-1-DRAFT", mlo_short_description="short-MLO_1-mod 1 draft", module_code = mod_code_1)

        self.assertEqual(ModuleLearningOutcome.objects.all().count(),13)#11 plus one out of range, plus one intended for a draft wl

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
        slo_4 = StudentLearningOutcome.objects.create(slo_description = 'This is slo_4', \
                                                      slo_short_description = 'slo_4', \
                                                      is_default_by_accreditor = True,\
                                                      letter_associated  = 'c1',
                                                      cohort_valid_from = out_of_range_aa_1,
                                                      cohort_valid_to = out_of_range_aa_2,
                                                      programme = prog_to_accredit)
        
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
        # MOD 4 - MLO 2 (out of range)                     2 
        
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
        out_of_range_mapping = MLOSLOMapping.objects.create(mlo = mlo_4_2_out_of_range,slo=slo_2, strength=2)
        self.assertEqual(MLOSLOMapping.objects.all().count(),16)#overall count. 15 in range, 1 out of range

        #Start testing the direct measures
        #First measure added performed in acad_year_2 on module 1_2, which is taken by students in year 1. Measure should appear in second academic year 
        measure_1 = MLOPerformanceMeasure.objects.create(description = 'test 1', academic_year = acad_year_2, associated_mlo = mlo_1_1,percentage_score=75)
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),1)
        table_slo_1 = CalculateTableForMLODirectMeasures(slo_id = slo_1.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
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
        
        table_slo_2 = CalculateTableForMLODirectMeasures(slo_id = slo_2.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
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

        table_slo_3 = CalculateTableForMLODirectMeasures(slo_id = slo_3.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
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

        # #Call the collective method - test the data for plotting
        all_info_slo_1 = CalculateAllInforAboutOneSLO(slo_id = slo_1.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
        self.assertEqual(len(all_info_slo_1["slo_measures_plot_data"]),4)
        self.assertEqual(len(all_info_slo_1["slo_measures_plot_data"][0]),4)#years
        self.assertEqual(len(all_info_slo_1["slo_measures_plot_data"][1]),4)#direct emasures
        self.assertEqual(len(all_info_slo_1["slo_measures_plot_data"][2]),4)#mlo surveys
        self.assertAlmostEqual(all_info_slo_1["slo_measures_plot_data"][0][0],acad_year_1.start_year)
        self.assertAlmostEqual(all_info_slo_1["slo_measures_plot_data"][0][1],acad_year_1.start_year+1)
        self.assertAlmostEqual(all_info_slo_1["slo_measures_plot_data"][0][2],acad_year_1.start_year+2)
        self.assertAlmostEqual(all_info_slo_1["slo_measures_plot_data"][0][3],acad_year_1.start_year+3)
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][1][0],0)
        self.assertAlmostEqual(all_info_slo_1["slo_measures_plot_data"][1][1],75.0)
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][1][2],0)
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][1][3],0)
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][2][0],0)#NOT yet any mlo survey
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][2][1],0)#NOT yet any mlo survey
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][2][2],0)#NOT yet any mlo survey
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][2][3],0)#NOT yet any mlo survey
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][3][0],0)#NOT yet any slo survey
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][3][1],0)#NOT yet any slo survey
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][3][2],0)#NOT yet any slo survey
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][3][3],0)#NOT yet any slo survey

        #Now add another measure for MLO 2, still module 1. This is mapped to SLO 1 (strength 2). So only the table for SLO1 should change - SAME academic year
        measure_2 = MLOPerformanceMeasure.objects.create(description = 'test 2', academic_year = acad_year_2, associated_mlo = mlo_1_2,percentage_score=45)
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),2)
        table_slo_1 = CalculateTableForMLODirectMeasures(slo_id = slo_1.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
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
        
        table_slo_2 = CalculateTableForMLODirectMeasures(slo_id = slo_2.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
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

        table_slo_3 = CalculateTableForMLODirectMeasures(slo_id = slo_3.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
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

        #Now add another measure for MLO 1, for module 2, taken by students in year 2, measure taken in acad_year_3 -> measure should affect cohort in second acad_year
        # This is mapped to SLO 1 (strength 2) and SLO 2 (strength 3). 
        # Tables for SLO1 and SLO2 should change. Tbale for SLO3 should remain unaltered
        measure_3 = MLOPerformanceMeasure.objects.create(description = 'test 3', academic_year = acad_year_3, associated_mlo = mlo_2_1,percentage_score=65)
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),3)
        table_slo_1 = CalculateTableForMLODirectMeasures(slo_id = slo_1.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
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
        self.assertEqual(table_slo_1[1][2], 65)#65 measure in second academic year for module 2
        self.assertAlmostEqual(table_slo_1[1][3], '')#no measure in third academic year for module 2
        self.assertEqual(table_slo_1[1][4], '')#no measure in last academic year for module 2
        self.assertEqual(table_slo_1[2][0], 'Weighted average')
        self.assertEqual(table_slo_1[2][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_1[2][2], Decimal((75*3+45*2+65*2)/(3+2+2)))#75 measure in second academic year, plus 45 measure, plus 65 from mod 2 ->Weighted average
        self.assertAlmostEqual(table_slo_1[2][3], 0)#no measure in third academic year (module 2, MLO 1)
        self.assertEqual(table_slo_1[2][4], 0)#no measure in last academic year -> totals row is zero

        table_slo_2 = CalculateTableForMLODirectMeasures(slo_id = slo_2.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
        self.assertEqual(len(table_slo_2), 3)#MOD 1, MOD 2 plus the totals row
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
        self.assertEqual(table_slo_2[1][2], 65)# 65 measure in second academic year from mod 2
        self.assertEqual(table_slo_2[1][3], '')#NO measure in third academic year
        self.assertEqual(table_slo_2[1][4], '')#no measure in last academic year
        self.assertEqual(table_slo_2[2][0], 'Weighted average')
        self.assertEqual(table_slo_2[2][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_2[2][2], (75.0*3+65*3)/(3+3))#75 measure in second academic year plus 65 ->weigthed average
        self.assertAlmostEqual(table_slo_2[2][3], 0)#No measure in third academic year
        self.assertEqual(table_slo_2[2][4], 0)#no measure in last academic year -> totals row is zero

        table_slo_3 = CalculateTableForMLODirectMeasures(slo_id = slo_3.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
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

        # #Now add another measure for MLO 1, for module 3, taken by stduents in year 3
        # # This is mapped to SLO 1 (strength 2) and SLO 3 (strength 1).Measure taken in acad_year 3 should affect acad_year_1 cohort
        # # Tables for SLO1 and SLO3 should change. Table for SLO2 should remain unaltered
        measure_4 = MLOPerformanceMeasure.objects.create(description = 'test 3', academic_year = acad_year_3, associated_mlo = mlo_3_1,percentage_score=15)
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),4)
        table_slo_1 = CalculateTableForMLODirectMeasures(slo_id = slo_1.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
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
        self.assertEqual(table_slo_1[1][2], 65)#65 measure in second academic year for module 2
        self.assertEqual(table_slo_1[1][3], '')#no measure in third academic year for module 2
        self.assertEqual(table_slo_1[1][4], '')#no measure in last academic year for module 2
        self.assertEqual(table_slo_1[2][0], mod_code_3)
        self.assertEqual(table_slo_1[2][1],15)#15 measure in first academic year for module 3
        self.assertEqual(table_slo_1[2][2], '')#No measure in second academic year
        self.assertEqual(table_slo_1[2][3], '')#no measure in third academic year
        self.assertEqual(table_slo_1[2][4], '')#no measure in last academic year
        self.assertEqual(table_slo_1[3][0], 'Weighted average')
        self.assertEqual(table_slo_1[3][1], 15)#Only 15 measure in first academic year -> totals row is 15
        self.assertAlmostEqual(table_slo_1[3][2], Decimal((75*3+45*2+65*2)/(3+2+2)))#75 measure in second academic year, plus 45 measure, plus 65 from mod 2 ->Weighted average
        self.assertAlmostEqual(table_slo_1[3][3], 0)#No measure in third academic year -> total is zero
        self.assertEqual(table_slo_1[3][4], 0)#no measure in last academic year -> totals row is zero

        # #unchanged
        table_slo_2 = CalculateTableForMLODirectMeasures(slo_id = slo_2.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
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
        self.assertEqual(table_slo_2[1][2], 65)# 65 measure in second academic year from mod 2
        self.assertEqual(table_slo_2[1][3], '')#NO measure in third academic year
        self.assertEqual(table_slo_2[1][4], '')#no measure in last academic year
        self.assertEqual(table_slo_2[2][0], 'Weighted average')
        self.assertEqual(table_slo_2[2][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_2[2][2], (75.0*3+65*3)/(3+3))#75 measure in second academic year plus 65 ->weigthed average
        self.assertAlmostEqual(table_slo_2[2][3], 0)#No measure in third academic year
        self.assertEqual(table_slo_2[2][4], 0)#no measure in last academic year -> totals row is zero
        self.assertEqual(table_slo_2[2][0], 'Weighted average')
        self.assertEqual(table_slo_2[2][1], 0)#no measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_2[2][2], (75.0*3+65*3)/(3+3))#75 measure in second academic year plus 65 ->weigthed average
        self.assertAlmostEqual(table_slo_2[2][3], 0)#No measure in third academic year
        self.assertEqual(table_slo_2[2][4], 0)#no measure in last academic year -> totals row is zero

        table_slo_3 = CalculateTableForMLODirectMeasures(slo_id = slo_3.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
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
        self.assertEqual(table_slo_3[1][1], 15)#15 measure in first academic year
        self.assertAlmostEqual(table_slo_3[1][2], '')#No measure in second academic year from mod 3
        self.assertEqual(table_slo_3[1][3], '')#no measure in third academic year
        self.assertEqual(table_slo_3[1][4], '')#no measure in last academic year
        self.assertEqual(table_slo_3[2][0], 'Weighted average')
        self.assertEqual(table_slo_3[2][1], 15)#15 measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_3[2][2], 75)#75 measure in second academic year (strength 1) ONLY
        self.assertEqual(table_slo_3[2][3], 0)#no measure in third academic year -> totals row is zero
        self.assertEqual(table_slo_3[2][4], 0)#no measure in last academic year -> totals row is zero

        # #Now add another measure for MLO 1, for module 4. This is taken in year 4. Measure taken in acad_year_4, should affect acad_year_1
        # # This is mapped to SLO 2 (strength 1).
        # # Tables for SLO2 should change. Tables for SLO1 and SLO3 should remain unaltered
        measure_5 = MLOPerformanceMeasure.objects.create(description = 'test 4', academic_year = acad_year_4, associated_mlo = mlo_4_1,percentage_score=12.6)
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),5)
        #unchanged
        table_slo_1 = CalculateTableForMLODirectMeasures(slo_id = slo_1.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
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
        self.assertEqual(table_slo_1[1][2], 65)#65 measure in second academic year for module 2
        self.assertEqual(table_slo_1[1][3], '')#no measure in third academic year for module 2
        self.assertEqual(table_slo_1[1][4], '')#no measure in last academic year for module 2
        self.assertEqual(table_slo_1[2][0], mod_code_3)
        self.assertEqual(table_slo_1[2][1],15)#15 measure in first academic year for module 3
        self.assertEqual(table_slo_1[2][2], '')#No measure in second academic year
        self.assertEqual(table_slo_1[2][3], '')#no measure in third academic year
        self.assertEqual(table_slo_1[2][4], '')#no measure in last academic year
        self.assertEqual(table_slo_1[3][0], 'Weighted average')
        self.assertEqual(table_slo_1[3][1], 15)#Only 15 measure in first academic year -> totals row is 15
        self.assertAlmostEqual(table_slo_1[3][2], Decimal((75*3+45*2+65*2)/(3+2+2)))#75 measure in second academic year, plus 45 measure, plus 65 from mod 2 ->Weighted average
        self.assertAlmostEqual(table_slo_1[3][3], 0)#No measure in third academic year -> total is zero
        self.assertEqual(table_slo_1[3][4], 0)#no measure in last academic year -> totals row is zero

        
        table_slo_2 = CalculateTableForMLODirectMeasures(slo_id = slo_2.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
        self.assertEqual(len(table_slo_2), 4)#MOD 1, MOS 2 plus the totals row
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
        self.assertEqual(table_slo_2[1][2], 65)# 65 measure in second academic year from mod 2
        self.assertEqual(table_slo_2[1][3], '')#NO measure in third academic year
        self.assertEqual(table_slo_2[1][4], '')#no measure in last academic year
        self.assertEqual(table_slo_2[2][0], mod_code_4)
        self.assertAlmostEqual(table_slo_2[2][1], Decimal(12.6))#12.6 measure in first academic year for MOD 4
        self.assertAlmostEqual(table_slo_2[2][2], '')#No measure in second academic year
        self.assertAlmostEqual(table_slo_2[2][3], '')#No measure in third academic year
        self.assertEqual(table_slo_2[2][4], '')#no measure in last academic year -> totals row is zero
        self.assertEqual(table_slo_2[3][0], 'Weighted average')
        self.assertAlmostEqual(table_slo_2[3][1], Decimal(12.6))#12.6 measure in first academic year
        self.assertAlmostEqual(table_slo_2[3][2], (75.0*3+65*3)/(3+3))#75 measure in second academic year plus 65 ->weigthed average
        self.assertAlmostEqual(table_slo_2[3][3], 0)#No measure in third academic year
        self.assertEqual(table_slo_2[3][4], 0)#no measure in last academic year -> totals row is zero


        # #unachanged
        table_slo_3 = CalculateTableForMLODirectMeasures(slo_id = slo_3.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
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
        self.assertEqual(table_slo_3[1][1], 15)#15 measure in first academic year
        self.assertAlmostEqual(table_slo_3[1][2], '')#No measure in second academic year from mod 3
        self.assertEqual(table_slo_3[1][3], '')#no measure in third academic year
        self.assertEqual(table_slo_3[1][4], '')#no measure in last academic year
        self.assertEqual(table_slo_3[2][0], 'Weighted average')
        self.assertEqual(table_slo_3[2][1], 15)#15 measure in first academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_3[2][2], 75)#75 measure in second academic year (strength 1) ONLY
        self.assertEqual(table_slo_3[2][3], 0)#no measure in third academic year -> totals row is zero
        self.assertEqual(table_slo_3[2][4], 0)#no measure in last academic year -> totals row is zero

        # #Call the colelctive method - test the data for plotting (SLO 3, years andd direct measures)
        all_info_slo_3 = CalculateAllInforAboutOneSLO(slo_id = slo_3.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
        self.assertEqual(len(all_info_slo_3["slo_measures_plot_data"]),4)
        self.assertEqual(len(all_info_slo_3["slo_measures_plot_data"][0]),4)#years
        self.assertEqual(len(all_info_slo_3["slo_measures_plot_data"][1]),4)#direct measures
        self.assertEqual(len(all_info_slo_3["slo_measures_plot_data"][2]),4)#MLO surveys
        self.assertAlmostEqual(all_info_slo_3["slo_measures_plot_data"][0][0],acad_year_1.start_year)
        self.assertAlmostEqual(all_info_slo_3["slo_measures_plot_data"][0][1],acad_year_1.start_year+1)
        self.assertAlmostEqual(all_info_slo_3["slo_measures_plot_data"][0][2],acad_year_1.start_year+2)
        self.assertAlmostEqual(all_info_slo_3["slo_measures_plot_data"][0][3],acad_year_1.start_year+3)
        self.assertEqual(all_info_slo_3["slo_measures_plot_data"][1][0],15)#First academic year
        self.assertAlmostEqual(all_info_slo_3["slo_measures_plot_data"][1][1],75.0)#second academic year
        self.assertEqual(all_info_slo_3["slo_measures_plot_data"][1][2],0)
        self.assertEqual(all_info_slo_3["slo_measures_plot_data"][1][3],0)
        self.assertEqual(all_info_slo_3["slo_measures_plot_data"][2][0],0)#NOT yet any mlo survey
        self.assertEqual(all_info_slo_3["slo_measures_plot_data"][2][1],0)#NOT yet any mlo survey
        self.assertEqual(all_info_slo_3["slo_measures_plot_data"][2][2],0)#NOT yet any mlo survey
        self.assertEqual(all_info_slo_3["slo_measures_plot_data"][2][3],0)#NOT yet any mlo survey
        self.assertEqual(all_info_slo_3["slo_measures_plot_data"][3][0],0)#NOT yet any slo survey
        self.assertEqual(all_info_slo_3["slo_measures_plot_data"][3][1],0)#NOT yet any slo survey
        self.assertEqual(all_info_slo_3["slo_measures_plot_data"][3][2],0)#NOT yet any slo survey
        self.assertEqual(all_info_slo_3["slo_measures_plot_data"][3][3],0)#NOT yet any slo survey

        #Now ad a measure with secondary and tertiary target. This is mod_1, taken in year 1. So it should affect cohort in acad_year_4 (where measure is taken)
        #Mlo 1_2 is mapped to SLO 1 (strength 2)
        #MLO 1_3 is mapped to SLO 1 (strength 1), and SLO 3 (strength 2)
        #MLO 1_4 is mapped to SLO 2 (strength 2)
        measure_6 = MLOPerformanceMeasure.objects.create(description = 'test 6', academic_year = acad_year_4, associated_mlo = mlo_1_2,\
                                                        secondary_associated_mlo = mlo_1_3,
                                                        tertiary_associated_mlo = mlo_1_4,
                                                        percentage_score=89.9)
        self.assertEqual(MLOPerformanceMeasure.objects.all().count(),6)
        table_slo_1 = CalculateTableForMLODirectMeasures(slo_id = slo_1.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
        self.assertEqual(len(table_slo_1), 4)#measures for Module 1, Module 2 and module 3 plus the totals row
        self.assertEqual(len(table_slo_1[0]), 5)
        self.assertEqual(len(table_slo_1[1]), 5)
        self.assertEqual(len(table_slo_1[2]), 5)
        self.assertEqual(len(table_slo_1[3]), 5)
        self.assertEqual(table_slo_1[0][0], mod_code_1)
        self.assertEqual(table_slo_1[0][1], '')#no measure in first academic year for module 1
        self.assertAlmostEqual(table_slo_1[0][2], (75*3+45*2)/5)#75 measure in second academic year, plus 45 measure ->Weighted average
        self.assertEqual(table_slo_1[0][3], '')#no measure in third academic year
        self.assertAlmostEqual(table_slo_1[0][4], Decimal((89.9*2+89.9*1)/(2.0+1.0)))#this last measure 89.9 from 2 mlo mapped differently
        self.assertEqual(table_slo_1[1][0], mod_code_2)
        self.assertEqual(table_slo_1[1][1], '')#no measure in first academic year for module 2
        self.assertEqual(table_slo_1[1][2], 65)#65 measure in second academic year for module 2
        self.assertEqual(table_slo_1[1][3], '')#no measure in third academic year for module 2
        self.assertEqual(table_slo_1[1][4], '')#no measure in last academic year for module 2
        self.assertEqual(table_slo_1[2][0], mod_code_3)
        self.assertEqual(table_slo_1[2][1],15)#15 measure in first academic year for module 3
        self.assertEqual(table_slo_1[2][2], '')#No measure in second academic year
        self.assertEqual(table_slo_1[2][3], '')#no measure in third academic year
        self.assertEqual(table_slo_1[2][4], '')#no measure in last academic year
        self.assertEqual(table_slo_1[3][0], 'Weighted average')
        self.assertEqual(table_slo_1[3][1], 15)#Only 15 measure in first academic year -> totals row is 15
        self.assertAlmostEqual(table_slo_1[3][2], Decimal((75*3+45*2+65*2)/(3+2+2)))#75 measure in second academic year, plus 45 measure, plus 65 from mod 2 ->Weighted average
        self.assertAlmostEqual(table_slo_1[3][3], 0)#No measure in third academic year -> total is zero
        self.assertAlmostEqual(table_slo_1[3][4], Decimal((89.9*2+89.9*1)/(2.0+1.0)))#4th academic year -> totals row is weighted average

        
        table_slo_2 = CalculateTableForMLODirectMeasures(slo_id = slo_2.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
        self.assertEqual(len(table_slo_2), 4)#MOD 1, MOD 2 , MOD 4 plus the totals row
        self.assertEqual(len(table_slo_2[0]), 5)
        self.assertEqual(len(table_slo_2[1]), 5)
        self.assertEqual(len(table_slo_2[2]), 5)
        self.assertEqual(table_slo_2[0][0], mod_code_1)
        self.assertEqual(table_slo_2[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_2[0][2], 75)#75 measure in second academic year
        self.assertEqual(table_slo_2[0][3], '')#no measure in third academic year
        self.assertAlmostEqual(table_slo_2[0][4], Decimal(89.9))#89.9 measure in last academic year
        self.assertEqual(table_slo_2[1][0], mod_code_2)
        self.assertEqual(table_slo_2[1][1], '')#no measure in first academic year
        self.assertEqual(table_slo_2[1][2], 65)# 65 measure in second academic year from mod 2
        self.assertEqual(table_slo_2[1][3], '')#NO measure in third academic year
        self.assertEqual(table_slo_2[1][4], '')#no measure in last academic year
        self.assertEqual(table_slo_2[2][0], mod_code_4)
        self.assertAlmostEqual(table_slo_2[2][1], Decimal(12.6))#12.6 measure in first academic year for MOD 4
        self.assertAlmostEqual(table_slo_2[2][2], '')#No measure in second academic year
        self.assertAlmostEqual(table_slo_2[2][3], '')#No measure in third academic year
        self.assertEqual(table_slo_2[2][4], '')#no measure in last academic year -> totals row is zero
        self.assertEqual(table_slo_2[3][0], 'Weighted average')
        self.assertAlmostEqual(table_slo_2[3][1], Decimal(12.6))#12.6 measure in first academic year
        self.assertAlmostEqual(table_slo_2[3][2], (75.0*3+65*3)/(3+3))#75 measure in second academic year plus 65 ->weigthed average
        self.assertAlmostEqual(table_slo_2[3][3], 0)#No measure in third academic year
        self.assertAlmostEqual(table_slo_2[3][4], Decimal(89.9))#only one  measure in last academic year


        table_slo_3 = CalculateTableForMLODirectMeasures(slo_id = slo_3.id,start_year = acad_year_1.start_year, end_year = acad_year_4.start_year, compulsory_only=1)
        self.assertEqual(len(table_slo_3), 3)#two moduleswith measure plus the totals row
        self.assertEqual(len(table_slo_3[0]), 5)
        self.assertEqual(len(table_slo_3[1]), 5)
        self.assertEqual(len(table_slo_3[2]), 5)
        self.assertEqual(table_slo_3[0][0], mod_code_1)
        self.assertEqual(table_slo_3[0][1], '')#no measure in first academic year
        self.assertAlmostEqual(table_slo_3[0][2], 75)#75 measure in second academic year
        self.assertEqual(table_slo_3[0][3], '')#no measure in third academic year
        self.assertAlmostEqual(table_slo_3[0][4],  Decimal(89.9))#this last measure 89.9
        self.assertEqual(table_slo_3[1][0], mod_code_3)
        self.assertEqual(table_slo_3[1][1], 15)#15 measure in first academic year
        self.assertAlmostEqual(table_slo_3[1][2], '')#No measure in second academic year from mod 3
        self.assertEqual(table_slo_3[1][3], '')#no measure in third academic year
        self.assertEqual(table_slo_3[1][4], '')#no measure in last academic year
        self.assertEqual(table_slo_3[2][0], 'Weighted average')
        self.assertEqual(table_slo_3[2][1], 15)#15 measure in first academic year -> 
        self.assertAlmostEqual(table_slo_3[2][2], 75)#75 measure in second academic year (strength 1) ONLY
        self.assertEqual(table_slo_3[2][3], 0)#no measure in third academic year -> totals row is zero
        self.assertAlmostEqual(table_slo_3[2][4], Decimal(89.9))#this last measure just added 

        table_slo_wrong_range = CalculateTableForMLODirectMeasures(slo_id = slo_3.id,start_year = acad_year_1.start_year-50, end_year = acad_year_4.start_year-50, compulsory_only=1)
        self.assertEqual(len(table_slo_wrong_range), 1)#totals only

        # #####################################################################
        # # Test the MLO survey table
        # #####################################################################
        mlo_survey_1 = Survey.objects.create(survey_title = "first mlo survey", opening_date = datetime.datetime(2012, 9, 17),\
                                                                                closing_date = datetime.datetime(2012, 9, 27),\
                                                                                cohort_targeted = acad_year_1,\
                                                                                programme_associated = prog_to_accredit,\
                                                                                max_respondents = 100)
        #Create the responses
        response_1 = SurveyQuestionResponse.objects.create(question_text = mlo_1_1.mlo_description,\
                                                           n_highest_score = 50,\
                                                           n_second_highest_score = 30,\
                                                           n_third_highest_score = 5,\
                                                           n_fourth_highest_score = 15,\
                                                           associated_mlo = mlo_1_1,\
                                                           parent_survey = mlo_survey_1 )
        props = response_1.CalculateRepsonsesProprties()
        # #Generate the table for SLO 1
        mlo_table_slo_1 = CalculateTableForMLOSurveys(slo_id = slo_1.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(mlo_table_slo_1), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_1[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_1[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_1[0][0], mlo_1_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_1[0][1],props['percentage_positive'])#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_1[0][2],'')#Nothing in 2013
        self.assertEqual(mlo_table_slo_1[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_1[1][1],props['percentage_positive'])#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_1[1][2],0)#Nothing in 2013
        
        #call the collective method - test the structures for plotting
        all_info_slo_1 = CalculateAllInforAboutOneSLO(slo_id = slo_1.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(all_info_slo_1["slo_measures_plot_data"]),4)
        self.assertEqual(len(all_info_slo_1["slo_measures_plot_data"][0]),2)#years
        self.assertEqual(len(all_info_slo_1["slo_measures_plot_data"][1]),2)#direct measures
        self.assertEqual(len(all_info_slo_1["slo_measures_plot_data"][2]),2)#mlo surveys
        self.assertEqual(len(all_info_slo_1["slo_measures_plot_data"][3]),2)#slo surveys
        self.assertAlmostEqual(all_info_slo_1["slo_measures_plot_data"][0][0],2012)#index 0, years
        self.assertAlmostEqual(all_info_slo_1["slo_measures_plot_data"][0][1],2013)#index 0, years
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][1][0],15)#index 0,direct measures, year 2012 ->15 (See above)
        self.assertAlmostEqual(all_info_slo_1["slo_measures_plot_data"][1][1],Decimal((75*3+45*2+65*2)/(3+2+2)))#index 0, direct meausres for year 2013 (see above)
        self.assertAlmostEqual(all_info_slo_1["slo_measures_plot_data"][2][0],props['percentage_positive'])#
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][2][1],0)#NO mlo survey in 2013
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][3][0],0)#NO slo surveys
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][3][1],0)#NO slo surveys 

        #Generate the table for SLO 2 - at this stage this is the same as the one for SLO 1, with just one measure
        mlo_table_slo_2 = CalculateTableForMLOSurveys(slo_id = slo_2.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(mlo_table_slo_2), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_2[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_2[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_2[0][0], mlo_1_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_2[0][1],props['percentage_positive'])#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_2[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_2[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_2[1][1],props['percentage_positive'])#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_2[1][2],0)#Nothing in 2021

        #Generate the table for SLO 3 - at this stage this is the same as the one for SLO 1, with just one measure
        mlo_table_slo_3 = CalculateTableForMLOSurveys(slo_id = slo_3.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(mlo_table_slo_3), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_3[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_3[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_3[0][0], mlo_1_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_3[0][1],props['percentage_positive'])#MLO 1 of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_3[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_3[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_3[1][1],props['percentage_positive'])#MLO 1 of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_3[1][2],0)#Nothing in 2021

        #Create another response in the same survey, for MLO 2 of module 1
        response_2 = SurveyQuestionResponse.objects.create(question_text = mlo_1_2.mlo_description,\
                                                           n_highest_score = 5,\
                                                           n_second_highest_score = 15,\
                                                           n_third_highest_score = 55,\
                                                           n_fourth_highest_score = 25,\
                                                           associated_mlo = mlo_1_2,\
                                                           parent_survey = mlo_survey_1 )
        props_2 = response_2.CalculateRepsonsesProprties()
        #Generate the table for SLO 1 - CHANGED
        mlo_table_slo_1 = CalculateTableForMLOSurveys(slo_id = slo_1.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(mlo_table_slo_1), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_1[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_1[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_1[0][0], mlo_1_1.module_code)
        expected_weigthed_average = (3.0*props['percentage_positive']  + \
                                     2.0*props_2['percentage_positive'])/(3.0+2.0)
        self.assertAlmostEqual(mlo_table_slo_1[0][1],expected_weigthed_average)#MLO 1of module 1 mapped to slo 1, but also MLO 2 of module 1
        self.assertAlmostEqual(mlo_table_slo_1[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_1[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_1[1][1],expected_weigthed_average)#same as above
        self.assertAlmostEqual(mlo_table_slo_1[1][2],0)#Nothing in 2021

        #Generate the table for SLO 2 - UNCHANGED as MLO 2 of module 1 does not map to slo 3
        mlo_table_slo_2 = CalculateTableForMLOSurveys(slo_id = slo_2.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(mlo_table_slo_2), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_2[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_2[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_2[0][0], mlo_1_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_2[0][1],props['percentage_positive'])#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_2[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_2[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_2[1][1],props['percentage_positive'])#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_2[1][2],0)#Nothing in 2021

        #Generate the table for SLO 3 - UNCHANGED as MLO 2 of module 1 does not map to slo 3
        mlo_table_slo_3 = CalculateTableForMLOSurveys(slo_id = slo_3.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(mlo_table_slo_3), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_3[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_3[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_3[0][0], mlo_1_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_3[0][1],props['percentage_positive'])#MLO 1 of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_3[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_3[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_3[1][1],props['percentage_positive'])#MLO 1 of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_3[1][2],0)#Nothing in 2021

        #Now create another survey
        #As we are tesing the weighted average calculations, we target the  same cohort
        mlo_survey_2 = Survey.objects.create(survey_title = "second mlo survey", opening_date = datetime.datetime(2012, 5, 17),\
                                                                                closing_date = datetime.datetime(2012, 5, 27),\
                                                                                cohort_targeted = acad_year_2,\
                                                                                programme_associated = prog_to_accredit,\
                                                                                max_respondents = 100)
        #Create another response for MLO 1 of module 2
        response_3 = SurveyQuestionResponse.objects.create(question_text = mlo_2_1.mlo_description,\
                                                           n_highest_score = 15,\
                                                           n_second_highest_score = 28,\
                                                           n_third_highest_score = 2,\
                                                           n_fourth_highest_score = 55,\
                                                           associated_mlo = mlo_2_1,\
                                                           parent_survey = mlo_survey_2 ) #mapped to slo 1 (2) and slo 2 (3)
        props_3 = response_3.CalculateRepsonsesProprties()
        mlo_table_slo_1 = CalculateTableForMLOSurveys(slo_id = slo_1.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(mlo_table_slo_1), 3)#Two meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_1[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_1[1]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_1[2]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_1[0][0], mlo_1_1.module_code)
        expected_weigthed_average = (3.0*props['percentage_positive'] + \
                                     2.0*props_2['percentage_positive'])/(3.0+2.0)
        self.assertAlmostEqual(mlo_table_slo_1[0][1],expected_weigthed_average)#MLO 1of module 1 mapped to slo 1, but also MLO 2 of module 1
        self.assertAlmostEqual(mlo_table_slo_1[0][2],'')#Nothing in second academic year
        self.assertEqual(mlo_table_slo_1[1][0], mlo_2_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_1[1][1],props_3['percentage_positive'])#MLO 1 of module 2 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_1[1][2],'')#Nothing in second academic year
        self.assertEqual(mlo_table_slo_1[2][0], "Weighted average")
        expected_weigthed_average_2 = (3.0*props['percentage_positive'] + \
                                      2.0*props_2['percentage_positive'] + \
                                      2.0*props_3['percentage_positive'])/(3.0+2.0+2.0)
        self.assertAlmostEqual(mlo_table_slo_1[2][1],expected_weigthed_average_2)#same as above
        self.assertAlmostEqual(mlo_table_slo_1[2][2],0)#Nothing in second academic year

        # #Generate the table for SLO 2 
        mlo_table_slo_2 = CalculateTableForMLOSurveys(slo_id = slo_2.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(mlo_table_slo_2), 3)#Three meausures, plus the totals
        self.assertEqual(len(mlo_table_slo_2[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_2[1]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_2[2]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_2[0][0], mlo_1_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_2[0][1],props['percentage_positive'])#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_2[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_2[1][0], mlo_2_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_2[1][1],props_3['percentage_positive'])#MLO 1of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_2[1][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_2[2][0], "Weighted average")
        expected_weighted_average_3 = (3.0* props['percentage_positive'] +\
                                       3.0*props_3['percentage_positive'])/(3.0+3.0)
        self.assertAlmostEqual(mlo_table_slo_2[2][1],expected_weighted_average_3)
        self.assertAlmostEqual(mlo_table_slo_2[2][2],0)#Nothing in 2021

        #Generate the table for SLO 3 - UNCHANGED as MLO 1 of module 2 does not map to slo 3
        mlo_table_slo_3 = CalculateTableForMLOSurveys(slo_id = slo_3.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(mlo_table_slo_3), 2)#One meausre, plus the totals
        self.assertEqual(len(mlo_table_slo_3[0]), 3)#Two years plus the label
        self.assertEqual(len(mlo_table_slo_3[1]), 3)#Two years plus the label
        self.assertEqual(mlo_table_slo_3[0][0], mlo_1_1.module_code)
        self.assertAlmostEqual(mlo_table_slo_3[0][1],props['percentage_positive'])#MLO 1 of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_3[0][2],'')#Nothing in 2021
        self.assertEqual(mlo_table_slo_3[1][0], "Weighted average")
        self.assertAlmostEqual(mlo_table_slo_3[1][1],props['percentage_positive'])#MLO 1 of module 1 mapped to slo 1
        self.assertAlmostEqual(mlo_table_slo_3[1][2],0)#Nothing in 2021

        #Cover the empty table because of dates out of range
        empty_mlo_table_slo = CalculateTableForMLOSurveys(slo_id = slo_3.id,start_year = 1990, end_year = 1994, compulsory_only=1)
        self.assertEqual(len(empty_mlo_table_slo), 1)#Only the totals

        # #####################################################################
        # # Test the SLO survey table
        # #####################################################################

        slo_survey_1 = Survey.objects.create(survey_title = "first slo survey", opening_date = datetime.datetime(2012, 5, 17),\
                                                                                closing_date = datetime.datetime(2013, 5, 17),\
                                                                                cohort_targeted = acad_year_1,\
                                                                                programme_associated = prog_to_accredit,\
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
        props_slo_1 = slo_response_1.CalculateRepsonsesProprties()
        props_slo_2 = slo_response_2.CalculateRepsonsesProprties()
        # #Generate table for SLO 1
        slo_1_survey_table = CalculateTableForSLOSurveys(slo_id = slo_1.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(slo_1_survey_table),1)
        self.assertEqual(slo_1_survey_table[0]['question'],slo_1.slo_description)
        self.assertAlmostEqual(slo_1_survey_table[0]['percent_positive'],props_slo_1['percentage_positive'])
        self.assertEqual(slo_1_survey_table[0]['n_questions'],1)

        all_info_slo_1 = CalculateAllInforAboutOneSLO(slo_id = slo_1.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(all_info_slo_1["slo_measures_plot_data"]),4)
        self.assertEqual(len(all_info_slo_1["slo_measures_plot_data"][0]),2)#years
        self.assertEqual(len(all_info_slo_1["slo_measures_plot_data"][1]),2)#direct measures
        self.assertEqual(len(all_info_slo_1["slo_measures_plot_data"][2]),2)#mlo surveys
        self.assertEqual(len(all_info_slo_1["slo_measures_plot_data"][3]),2)#slo surveys
        self.assertAlmostEqual(all_info_slo_1["slo_measures_plot_data"][3][0],props_slo_1['percentage_positive'])#1 slo survey
        self.assertEqual(all_info_slo_1["slo_measures_plot_data"][3][1],0)#NO slo surveys 

        #Generate table for SLO 2
        slo_2_survey_table = CalculateTableForSLOSurveys(slo_id = slo_2.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(slo_2_survey_table),1)
        self.assertEqual(slo_2_survey_table[0]['question'],slo_2.slo_description)
        self.assertAlmostEqual(slo_2_survey_table[0]['percent_positive'],props_slo_2['percentage_positive'])
        self.assertEqual(slo_2_survey_table[0]['n_questions'],1)

        #Generate table for SLO 3 (this one is empty)
        slo_3_survey_table = CalculateTableForSLOSurveys(slo_id = slo_3.id,start_year = 2012, end_year = 2013, compulsory_only=1)
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
        
        props_slo_alternate = slo_response_1_alternate.CalculateRepsonsesProprties()
        #Generate table for SLO 1
        slo_1_survey_table = CalculateTableForSLOSurveys(slo_id = slo_1.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(slo_1_survey_table),1)
        self.assertEqual(slo_1_survey_table[0]['question'],slo_1.slo_description + ', ' + alternate_question)
        expected_perc = 0.5*(props_slo_1['percentage_positive']+ props_slo_alternate['percentage_positive'])
        self.assertAlmostEqual(slo_1_survey_table[0]['percent_positive'],expected_perc)
        self.assertEqual(slo_1_survey_table[0]['n_questions'],2)#2 questions now

        #Generate table for SLO 2 - UNCHANGED
        slo_2_survey_table = CalculateTableForSLOSurveys(slo_id = slo_2.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(slo_2_survey_table),1)
        self.assertEqual(slo_2_survey_table[0]['question'],slo_2.slo_description)
        self.assertAlmostEqual(slo_2_survey_table[0]['percent_positive'],props_slo_2['percentage_positive'])
        self.assertEqual(slo_2_survey_table[0]['n_questions'],1)

        #Generate table for SLO 3 (this one is empty) - UNCHANGED
        slo_3_survey_table = CalculateTableForSLOSurveys(slo_id = slo_3.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(slo_3_survey_table),0)

        #Do another survey. Test ability to create new lines in the table
        slo_survey_2 = Survey.objects.create(survey_title = "second slo survey", opening_date = datetime.datetime(2012, 7, 17),\
                                                                                closing_date = datetime.datetime(2012, 9, 17),\
                                                                                cohort_targeted = acad_year_1,\
                                                                                programme_associated = prog_to_accredit,\
                                                                                max_respondents = 100)
        slo_response_2_srv2 = SurveyQuestionResponse.objects.create(question_text = slo_2.slo_description,\
                                                           n_highest_score = 15,\
                                                           n_second_highest_score = 28,\
                                                           n_third_highest_score = 2,\
                                                           n_fourth_highest_score = 55,\
                                                           associated_slo = slo_2,\
                                                           parent_survey = slo_survey_2)
        
        props_new_slo_2_srv_2 = slo_response_2_srv2.CalculateRepsonsesProprties()
        #Generate table for SLO 1 - UNCHANGED
        slo_1_survey_table = CalculateTableForSLOSurveys(slo_id = slo_1.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(slo_1_survey_table),1)
        self.assertEqual(slo_1_survey_table[0]['question'],slo_1.slo_description + ', ' + alternate_question)
        expected_perc = 0.5*(props_slo_1['percentage_positive'] + props_slo_alternate['percentage_positive'])
        self.assertAlmostEqual(slo_1_survey_table[0]['percent_positive'],expected_perc)
        self.assertEqual(slo_1_survey_table[0]['n_questions'],2)#2 questions now

        #Generate table for SLO 2 - new line added here
        slo_2_survey_table = CalculateTableForSLOSurveys(slo_id = slo_2.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(slo_2_survey_table),2)
        self.assertEqual(slo_2_survey_table[0]['question'],slo_2.slo_description)
        self.assertAlmostEqual(slo_2_survey_table[0]['percent_positive'],props_slo_2['percentage_positive'])
        self.assertEqual(slo_2_survey_table[0]['n_questions'],1)
        self.assertEqual(slo_2_survey_table[1]['question'],slo_2.slo_description)
        self.assertAlmostEqual(slo_2_survey_table[1]['percent_positive'],props_new_slo_2_srv_2['percentage_positive'])
        self.assertEqual(slo_2_survey_table[1]['n_questions'],1)

        #Generate table for SLO 3 (this one is empty) - UNCHANGED
        slo_3_survey_table = CalculateTableForSLOSurveys(slo_id = slo_3.id,start_year = 2012, end_year = 2013, compulsory_only=1)
        self.assertEqual(len(slo_3_survey_table),0)

        # #Test the MLO-SLO mapping table for a single SLO
        slo_1_table = CalculateMLOSLOMappingTable(slo_1.id, 2012,2015, compulsory_only=1)
        self.assertEqual(len(slo_1_table), 3) #3 mods mapped
        self.assertEqual(slo_1_table[0]["module_code"], mod_code_1)
        self.assertEqual(slo_1_table[1]["module_code"], mod_code_2)
        self.assertEqual(slo_1_table[2]["module_code"], mod_code_3)
        self.assertEqual(len(slo_1_table[0]["numerical_mappings"]), 4)
        self.assertEqual(slo_1_table[0]["numerical_mappings"][0], 3)#SLO 1 - MOD 1 - 2012
        self.assertEqual(slo_1_table[0]["numerical_mappings"][1], 3)#SLO 1 - MOD 1 - 2013
        self.assertEqual(slo_1_table[0]["numerical_mappings"][2], 3)#SLO 1 - MOD 1 - 2014
        self.assertEqual(slo_1_table[0]["numerical_mappings"][3], 3)#SLO 1 - MOD 1 - 2015

        self.assertEqual(slo_1_table[0]["n_mlo_mapped"][0], 3)#SLO 1 - MOD 1 - 2012
        self.assertEqual(slo_1_table[0]["n_mlo_mapped"][1], 3)#SLO 1 - MOD 1 - 2013
        self.assertEqual(slo_1_table[0]["n_mlo_mapped"][2], 3)#SLO 1 - MOD 1 - 2014
        self.assertEqual(slo_1_table[0]["n_mlo_mapped"][3], 3)#SLO 1 - MOD 1 - 2015

        self.assertEqual(slo_1_table[1]["numerical_mappings"][0], 3)#SLO 1 - MOD 2 - 2012
        self.assertEqual(slo_1_table[1]["numerical_mappings"][1], 3)#SLO 1 - MOD 2 - 2013
        self.assertEqual(slo_1_table[1]["numerical_mappings"][2], 3)#SLO 1 - MOD 2 - 2014
        self.assertEqual(slo_1_table[1]["numerical_mappings"][3], 0)#SLO 1 - MOD 2 - 2015 -> 2015 cohort hasn't taken MODE 2 yet

        self.assertEqual(slo_1_table[1]["n_mlo_mapped"][0], 2)#SLO 1 - MOD 2 - 2012
        self.assertEqual(slo_1_table[1]["n_mlo_mapped"][1], 2)#SLO 1 - MOD 2 - 2013
        self.assertEqual(slo_1_table[1]["n_mlo_mapped"][2], 2)#SLO 1 - MOD 2 - 2014
        self.assertEqual(slo_1_table[1]["n_mlo_mapped"][3], 0)#SLO 1 - MOD 2 - 2015

        self.assertEqual(slo_1_table[2]["numerical_mappings"][0], 2)#SLO 1 - MOD 3 - 2012
        self.assertEqual(slo_1_table[2]["numerical_mappings"][1], 2)#SLO 1 - MOD 3 - 2013
        self.assertEqual(slo_1_table[2]["numerical_mappings"][2], 0)#SLO 1 - MOD 3 - 2014 -> 2014 ccohort hasn't taken MOD 3 yet
        self.assertEqual(slo_1_table[2]["numerical_mappings"][3], 0)#SLO 1 - MOD 3 - 2015 -> 2015 ccohort hasn't taken MOD 3 yet

        self.assertEqual(slo_1_table[2]["n_mlo_mapped"][0], 1)#SLO 1 - MOD 3 - 2012
        self.assertEqual(slo_1_table[2]["n_mlo_mapped"][1], 1)#SLO 1 - MOD 3 - 2013
        self.assertEqual(slo_1_table[2]["n_mlo_mapped"][2], 0)#SLO 1 - MOD 3 - 2014
        self.assertEqual(slo_1_table[2]["n_mlo_mapped"][3], 0)#SLO 1 - MOD 3 - 2015


        slo_2_table = CalculateMLOSLOMappingTable(slo_2.id, 2012,2015, compulsory_only=1)
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
        self.assertEqual(slo_2_table[1]["numerical_mappings"][3], 0)#SLO 2 - MOD 2 - 2015 -> 2015 cohort hasn't taken MODE 2 yet

        self.assertEqual(slo_2_table[1]["n_mlo_mapped"][0], 1)#SLO 2 - MOD 2 - 2012
        self.assertEqual(slo_2_table[1]["n_mlo_mapped"][1], 1)#SLO 2 - MOD 2 - 2013
        self.assertEqual(slo_2_table[1]["n_mlo_mapped"][2], 1)#SLO 2 - MOD 2 - 2014
        self.assertEqual(slo_2_table[1]["n_mlo_mapped"][3], 0)#SLO 2 - MOD 2 - 2015 -> 2015 cohort hasn't taken MODE 2 yet

        self.assertEqual(slo_2_table[2]["numerical_mappings"][0], 1)#SLO 2 - MOD 4 - 2012
        self.assertEqual(slo_2_table[2]["numerical_mappings"][1], 0)#SLO 2 - MOD 4 - 2013 -> 2013 cohort hasn't taken MOD 4 yet
        self.assertEqual(slo_2_table[2]["numerical_mappings"][2], 0)#SLO 2 - MOD 4 - 2014 -> 2014 cohort hasn't taken MOD 4 yet
        self.assertEqual(slo_2_table[2]["numerical_mappings"][3], 0)#SLO 2 - MOD 4 - 2015 -> 2015 cohort hasn't taken MOD 4 yet

        self.assertEqual(slo_2_table[2]["n_mlo_mapped"][0], 1)#SLO 2 - MOD 4 - 2012
        self.assertEqual(slo_2_table[2]["n_mlo_mapped"][1], 0)#SLO 2 - MOD 4 - 2013
        self.assertEqual(slo_2_table[2]["n_mlo_mapped"][2], 0)#SLO 2 - MOD 4 - 2014
        self.assertEqual(slo_2_table[2]["n_mlo_mapped"][3], 0)#SLO 2 - MOD 4 - 2015

        slo_3_table = CalculateMLOSLOMappingTable(slo_3.id, 2012,2015, compulsory_only=1)
        self.assertEqual(len(slo_3_table), 3) #3 mods mapped
        self.assertEqual(slo_3_table[0]["module_code"], mod_code_1)
        self.assertEqual(slo_3_table[1]["module_code"], mod_code_2)
        self.assertEqual(slo_3_table[2]["module_code"], mod_code_3)
        self.assertEqual(len(slo_3_table[0]["numerical_mappings"]), 4)
        self.assertEqual(slo_3_table[0]["numerical_mappings"][0], 2)#SLO 3 - MOD 1 - 2012
        self.assertEqual(slo_3_table[0]["numerical_mappings"][1], 2)#SLO 3 - MOD 1 - 2013
        self.assertEqual(slo_3_table[0]["numerical_mappings"][2], 2)#SLO 3 - MOD 1 - 2014
        self.assertEqual(slo_3_table[0]["numerical_mappings"][3], 2)#SLO 3 - MOD 1 - 2015

        self.assertEqual(slo_3_table[0]["n_mlo_mapped"][0], 2)#SLO 3 - MOD 1 - 2012
        self.assertEqual(slo_3_table[0]["n_mlo_mapped"][1], 2)#SLO 3 - MOD 1 - 2013
        self.assertEqual(slo_3_table[0]["n_mlo_mapped"][2], 2)#SLO 3 - MOD 1 - 2014
        self.assertEqual(slo_3_table[0]["n_mlo_mapped"][3], 2)#SLO 3 - MOD 1 - 2015

        self.assertEqual(slo_3_table[1]["numerical_mappings"][0], 1)#SLO 3 - MOD 2 - 2012
        self.assertEqual(slo_3_table[1]["numerical_mappings"][1], 1)#SLO 3 - MOD 2 - 2013
        self.assertEqual(slo_3_table[1]["numerical_mappings"][2], 1)#SLO 3 - MOD 2 - 2014
        self.assertEqual(slo_3_table[1]["numerical_mappings"][3], 0)#SLO 3 - MOD 2 - 2015 -> 2015 cohort hasn't taken MOD 2 yet

        self.assertEqual(slo_3_table[1]["n_mlo_mapped"][0], 1)#SLO 3 - MOD 2 - 2012
        self.assertEqual(slo_3_table[1]["n_mlo_mapped"][1], 1)#SLO 3 - MOD 2 - 2013
        self.assertEqual(slo_3_table[1]["n_mlo_mapped"][2], 1)#SLO 3 - MOD 2 - 2014
        self.assertEqual(slo_3_table[1]["n_mlo_mapped"][3], 0)#SLO 3 - MOD 2 - 2015  -> 2015 cohort hasn't taken MOD 2 yet

        self.assertEqual(slo_3_table[2]["numerical_mappings"][0], 3)#SLO 3 - MOD 3 - 2012
        self.assertEqual(slo_3_table[2]["numerical_mappings"][1], 3)#SLO 3 - MOD 3 - 2013 
        self.assertEqual(slo_3_table[2]["numerical_mappings"][2], 0)#SLO 3 - MOD 3 - 2014 -> 2014 cohort hasn't taken MOD 3 yet
        self.assertEqual(slo_3_table[2]["numerical_mappings"][3], 0)#SLO 3 - MOD 3 - 2015 -> 2015 cohort hasn't taken MOD 3 yet

        self.assertEqual(slo_3_table[2]["n_mlo_mapped"][0], 2)#SLO 3 - MOD 3 - 2012 -> 2 MLO, both 3
        self.assertEqual(slo_3_table[2]["n_mlo_mapped"][1], 2)#SLO 3 - MOD 3 - 2013 -> 2 MLO, both 3
        self.assertEqual(slo_3_table[2]["n_mlo_mapped"][2], 0)#SLO 3 - MOD 3 - 2014
        self.assertEqual(slo_3_table[2]["n_mlo_mapped"][3], 0)#SLO 3 - MOD 3 - 2015

        #Test the attention score tables
        att_score_table = CalculateAttentionScoresSummaryTable(prog_to_accredit.id,acad_year_1.start_year,acad_year_4.start_year, compulsory_only=1)        
        #print(att_score_table)
        self.assertEqual(len(att_score_table),4)#There are 4 SLOs
        self.assertEqual(att_score_table[0]["letter"],'a')#first SLO, letter
        self.assertEqual(att_score_table[1]["letter"],'b')#second SLO, letter
        self.assertEqual(att_score_table[2]["letter"],'c')#third SLO, letter
        self.assertEqual(att_score_table[3]["letter"],'c1')#fourth SLO, letter
        self.assertEqual(len(att_score_table[0]["attention_scores_direct"]),4)#4 years from 2102 to 2015 included
        self.assertEqual(len(att_score_table[0]["attention_scores_mlo_surveys"]),4)#4 years from 2102 to 2015 included
        self.assertEqual(len(att_score_table[0]["attention_scores_slo_surveys"]),4)#4 years from 2102 to 2015 included
        self.assertEqual(len(att_score_table[1]["attention_scores_direct"]),4)#4 years from 2102 to 2015 included
        self.assertEqual(len(att_score_table[1]["attention_scores_mlo_surveys"]),4)#4 years from 2102 to 2015 included
        self.assertEqual(len(att_score_table[1]["attention_scores_slo_surveys"]),4)#4 years from 2102 to 2015 included
        self.assertEqual(len(att_score_table[2]["attention_scores_direct"]),4)#4 years from 2102 to 2015 included
        self.assertEqual(len(att_score_table[2]["attention_scores_mlo_surveys"]),4)#4 years from 2102 to 2015 included
        self.assertEqual(len(att_score_table[2]["attention_scores_slo_surveys"]),4)#4 years from 2102 to 2015 included
        self.assertEqual(len(att_score_table[3]["attention_scores_direct"]),4)#4 years from 2102 to 2015 included
        self.assertEqual(len(att_score_table[3]["attention_scores_mlo_surveys"]),4)#4 years from 2102 to 2015 included
        self.assertEqual(len(att_score_table[3]["attention_scores_slo_surveys"]),4)#4 years from 2102 to 2015 included

        self.assertAlmostEqual(att_score_table[0]["attention_scores_direct"][0],2/3)#SLO a, direct measures, 2012 -> There is one mapping, strenth 2
        self.assertAlmostEqual(att_score_table[0]["attention_scores_direct"][1],1+2/3+2/3)#SLO a, direct measures, 2013 -> 3 measures (3 and 2 and 2) -> 1+2/3 +2/3
        self.assertAlmostEqual(att_score_table[0]["attention_scores_direct"][2],0)#SLO a, direct measures, 2014 ->None
        self.assertAlmostEqual(att_score_table[0]["attention_scores_direct"][3],1/3+2/3)#SLO a, direct measures, 2015 ->Two measures

        self.assertAlmostEqual(att_score_table[1]["attention_scores_direct"][0],1/3)#SLO b, direct measures, 2012 -> There is one mapping, strenth 1 (from mod 4 to slo 2)
        self.assertAlmostEqual(att_score_table[1]["attention_scores_direct"][1],3/3 + 3/3)#SLO b, direct measures, 2013 -> 2 measures (3 and 3) -> 3/3 +3/3
        self.assertAlmostEqual(att_score_table[1]["attention_scores_direct"][2],0)#SLO b, direct measures, 2014 ->None
        self.assertAlmostEqual(att_score_table[1]["attention_scores_direct"][3],2/3)#SLO b, direct measures, 2015 -> One measure from mod 1, mlo 4 as tertiary associated. Strength 2

        self.assertAlmostEqual(att_score_table[2]["attention_scores_direct"][0],3/3)#SLO c, direct measures, 2012 -> There is one mapping, from mlo 3 (mod 1) sterngth 3 
        self.assertAlmostEqual(att_score_table[2]["attention_scores_direct"][1],1/3)#SLO c, direct measures, 2013 -> 1 measure, from mlo 1 (mod 1) strength is 1
        self.assertAlmostEqual(att_score_table[2]["attention_scores_direct"][2],0)#SLO c, direct measures, 2014 ->None
        self.assertAlmostEqual(att_score_table[2]["attention_scores_direct"][3],2/3)#SLO c, direct measures, 2015 -> One measure from mod 1, mlo 3 as secondary associated. Strength 2

        self.assertAlmostEqual(att_score_table[3]["attention_scores_direct"][0],0)#SLO c1, NO direct measures, 2012
        self.assertAlmostEqual(att_score_table[3]["attention_scores_direct"][1],0)#SLO c1, NO direct measures, 2013 
        self.assertAlmostEqual(att_score_table[3]["attention_scores_direct"][2],0)#SLO c1, NO direct measures, 2014 
        self.assertAlmostEqual(att_score_table[3]["attention_scores_direct"][3],0)#SLO c1, NO direct measures, 2015

        self.assertAlmostEqual(att_score_table[0]["attention_scores_mlo_surveys"][0],3/3 + 2/3 + 2/3)#SLO a, MLO survey measures, 2012 -> Three questions
        self.assertAlmostEqual(att_score_table[0]["attention_scores_mlo_surveys"][1],0)#SLO a, MLO  survey measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[0]["attention_scores_mlo_surveys"][2],0)#SLO a, MLO  survey measures, 2014 ->None
        self.assertAlmostEqual(att_score_table[0]["attention_scores_mlo_surveys"][3],0)#SLO a, MLOsurvey measures, 2015 -> None

        self.assertAlmostEqual(att_score_table[1]["attention_scores_mlo_surveys"][0],3/3 + 3/3)#SLO b, MLO  survey measures, 2012 -> Two questions
        self.assertAlmostEqual(att_score_table[1]["attention_scores_mlo_surveys"][1],0)#SLO b, MLO  survey measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[1]["attention_scores_mlo_surveys"][2],0)#SLO b, MLO  survey measures, 2014 ->None
        self.assertAlmostEqual(att_score_table[1]["attention_scores_mlo_surveys"][3],0)#SLO b, MLO  survey measures, 2015 -> None

        self.assertAlmostEqual(att_score_table[2]["attention_scores_mlo_surveys"][0],1/3)#SLO c, MLO  survey measures, 2012 -> One question
        self.assertAlmostEqual(att_score_table[2]["attention_scores_mlo_surveys"][1],0)#SLO c, MLO survey measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[2]["attention_scores_mlo_surveys"][2],0)#SLO c, MLO survey measures, 2014 ->None
        self.assertAlmostEqual(att_score_table[2]["attention_scores_mlo_surveys"][3],0)#SLO c, vsurvey measures, 2015 -> None

        self.assertAlmostEqual(att_score_table[3]["attention_scores_mlo_surveys"][0],0)#SLO c1, MLO  survey measures, 2012 -> None
        self.assertAlmostEqual(att_score_table[3]["attention_scores_mlo_surveys"][1],0)#SLO c1, MLO survey measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[3]["attention_scores_mlo_surveys"][2],0)#SLO c1, MLO survey measures, 2014 ->None
        self.assertAlmostEqual(att_score_table[3]["attention_scores_mlo_surveys"][3],0)#SLO c1, vsurvey measures, 2015 -> None

        self.assertAlmostEqual(att_score_table[0]["attention_scores_slo_surveys"][0],2)#SLO a, MLO survey measures, 2012 -> two questions
        self.assertAlmostEqual(att_score_table[0]["attention_scores_slo_surveys"][1],0)#SLO a, MLO  survey measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[0]["attention_scores_slo_surveys"][2],0)#SLO a, MLO  survey measures, 2014 ->None
        self.assertAlmostEqual(att_score_table[0]["attention_scores_slo_surveys"][3],0)#SLO a, MLOsurvey measures, 2015 -> None

        self.assertAlmostEqual(att_score_table[1]["attention_scores_slo_surveys"][0],2)#SLO b, MLO  survey measures, 2012 -> Two questions
        self.assertAlmostEqual(att_score_table[1]["attention_scores_slo_surveys"][1],0)#SLO b, MLO  survey measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[1]["attention_scores_slo_surveys"][2],0)#SLO b, MLO  survey measures, 2014 ->None
        self.assertAlmostEqual(att_score_table[1]["attention_scores_slo_surveys"][3],0)#SLO b, MLO  survey measures, 2015 -> None

        self.assertAlmostEqual(att_score_table[2]["attention_scores_slo_surveys"][0],0)#SLO c, MLO  survey measures, 2012 -> None
        self.assertAlmostEqual(att_score_table[2]["attention_scores_slo_surveys"][1],0)#SLO c, MLO survey measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[2]["attention_scores_slo_surveys"][2],0)#SLO c, MLO survey measures, 2014 ->None
        self.assertAlmostEqual(att_score_table[2]["attention_scores_slo_surveys"][3],0)#SLO c, vsurvey measures, 2015 -> None

        self.assertAlmostEqual(att_score_table[3]["attention_scores_slo_surveys"][0],0)#SLO c1, MLO  survey measures, 2012 -> None
        self.assertAlmostEqual(att_score_table[3]["attention_scores_slo_surveys"][1],0)#SLO c1, MLO survey measures, 2013 -> None
        self.assertAlmostEqual(att_score_table[3]["attention_scores_slo_surveys"][2],0)#SLO c1, MLO survey measures, 2014 ->None
        self.assertAlmostEqual(att_score_table[3]["attention_scores_slo_surveys"][3],0)#SLO c1, vsurvey measures, 2015 -> None

        #Test the big slo mlo table
        main_body_table = CalculateTableForOverallSLOMapping(prog_to_accredit.id, 2020,2021, compulsory_only=1)['main_body_table']
        self.assertEqual(len(main_body_table), 0) #No workloads in the period
        big_table = CalculateTableForOverallSLOMapping(prog_to_accredit.id, 2010,2021, compulsory_only=0)
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
                                                                                         'start_year' : 2020, 'end_year':2021, 'compulsory_only':1}))
        self.assertEqual(response.status_code, 200) #No issues

        self.assertEqual(response.context['programme_id'], prog_to_accredit.id)
        self.assertEqual(response.context['programme_name'], prog_to_accredit.programme_name)
        self.assertEqual(response.context['start_year'], '2020/2021')
        self.assertEqual(response.context['end_year'], '2021/2022')
        self.assertEqual(len(response.context['slo_measures']),StudentLearningOutcome.objects.filter(programme__id = prog_to_accredit.id).count())
        main_body_table = CalculateTableForOverallSLOMapping(prog_to_accredit.id, 2020,2021,compulsory_only=1)['main_body_table']
        self.assertEqual(len(main_body_table), 0) #No workloads in the period
        self.assertEqual(len(response.context['big_mlo_slo_table']),len(main_body_table))

        