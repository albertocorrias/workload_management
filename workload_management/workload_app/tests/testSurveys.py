import datetime
from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *
from workload_app.models import Department, Faculty, Survey, Module, ModuleLearningOutcome,WorkloadScenario,Academicyear, SurveyQuestionResponse, \
                                ModuleType,StudentLearningOutcome,ProgrammeOffered, ProgrammeEducationalObjective
from workload_app.helper_methods_survey import CalculateSurveyDetails
from workload_app.global_constants import NUS_MLO_SURVEY_LABELS, NUS_SLO_SURVEY_LABELS

class TestSurveys(TestCase):
    def setup_user(self):
        #The tets client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
    def test_add_MLO_survey(self):

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(Faculty.objects.all().count(),0) #0 to start with
        self.assertEqual(Department.objects.all().count(),0) #0 to start with
        self.assertEqual(Survey.objects.all().count(),0) #0 to start with
        self.assertEqual(Module.objects.all().count(),0) #0 to start with
        self.assertEqual(ModuleLearningOutcome.objects.all().count(),0) #0 to start with
        self.assertEqual(SurveyQuestionResponse.objects.all().count(),0) #0 to start with
        
        new_mod_type = ModuleType.objects.create(type_name="test_type")
        new_faculty = Faculty.objects.create(faculty_name = "new faculty", faculty_acronym = "NFC")
        new_dept = Department.objects.create(department_name = "new_dept", department_acronym = "NDPT",faculty=new_faculty)
        acad_year = Academicyear.objects.create(start_year=2023)
        wl_scen = WorkloadScenario.objects.create(label = "test_scen", status = WorkloadScenario.OFFICIAL,\
                                                  dept = new_dept,academic_year = acad_year )
        module_code = "BN2102"
        module_1 = Module.objects.create(module_code = module_code, module_title = "test_title", scenario_ref = wl_scen, total_hours = 150, module_type = new_mod_type)
        self.assertEqual(WorkloadScenario.objects.all().count(),1)
        self.assertEqual(Module.objects.all().count(),1)
        self.assertEqual(ModuleLearningOutcome.objects.all().count(),0)
        #Create 3 MLOs
        mlo_1 = ModuleLearningOutcome.objects.create(mlo_description = "First MLO", mlo_short_description = "1", module_code = module_code)
        mlo_2 = ModuleLearningOutcome.objects.create(mlo_description = "Second MLO", mlo_short_description = "2", module_code = module_code)
        mlo_3 = ModuleLearningOutcome.objects.create(mlo_description = "Third MLO", mlo_short_description = "3", module_code = module_code)
        self.assertEqual(ModuleLearningOutcome.objects.all().count(),3)

        #test the get 
        response = self.client.get(reverse('workload_app:module',kwargs={'module_code' : module_code}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertContains(response, mlo_1.mlo_description)
        self.assertContains(response, mlo_2.mlo_description)
        self.assertContains(response, mlo_3.mlo_description)
        survey_comment = "hello, this is a test survey"
        #Now try the POST witha dding a module survey
        response = self.client.post(reverse('workload_app:module',kwargs={'module_code' : module_code}),{
            'start_date_month' : 1,
            'start_date_day' : 15,
            'start_date_year' : 2021,
            'end_date_month' : 1,
            'end_date_day' : 15,
            'end_date_year' : 2023,
            'cohort_targeted' : acad_year.id,
            'totoal_N_recipients' : "150",
            'comments' : survey_comment,
            'mlo_descr' + str(mlo_1.id) : mlo_1.mlo_description,
            'n_highest_score' + str(mlo_1.id): "100",            
            'n_second_highest_score' + str(mlo_1.id) : "10",
            'n_third_highest_score' + str(mlo_1.id): "10",
            'n_fourth_highest_score' + str(mlo_1.id): "20",
            'mlo_descr' + str(mlo_2.id) : mlo_2.mlo_description,
            'n_highest_score' + str(mlo_2.id): "99",            
            'n_second_highest_score' + str(mlo_2.id): "10",
            'n_third_highest_score' + str(mlo_2.id): "10",
            'n_fourth_highest_score' + str(mlo_2.id) : "20",
            'mlo_descr' + str(mlo_3.id) : mlo_3.mlo_description,
            'n_highest_score' + str(mlo_3.id) : "98",            
            'n_second_highest_score' + str(mlo_3.id) : "1",
            'n_third_highest_score' + str(mlo_3.id) : "1",
            'n_fourth_highest_score' + str(mlo_3.id) : "48",
        })
        self.assertEqual(response.status_code, 302) #post re-directs
        self.assertEqual(Survey.objects.all().count(),1) #one survey should have been created
        survey_label = "MLO survey for module " + module_code
        self.assertEqual(Survey.objects.filter(survey_title = survey_label).count(),1) #check name
        self.assertEqual(Survey.objects.filter(cohort_targeted__id = acad_year.id).count(),1) #check cohort targeted
        self.assertEqual(Survey.objects.filter(max_respondents = 150).count(),1) #check max respondents
        self.assertEqual(SurveyQuestionResponse.objects.all().count(),3) #One response for each MLO
        self.assertEqual(SurveyQuestionResponse.objects.filter(associated_mlo = mlo_1).count(),1)
        self.assertEqual(SurveyQuestionResponse.objects.filter(associated_mlo = mlo_2).count(),1)
        self.assertEqual(SurveyQuestionResponse.objects.filter(associated_mlo = mlo_3).count(),1)
        self.assertEqual(SurveyQuestionResponse.objects.filter(associated_slo__isnull = True).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(associated_peo__isnull = True).count(),3)
        survey_created = Survey.objects.all().first()
        self.assertEqual(SurveyQuestionResponse.objects.filter(parent_survey = survey_created).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(label_highest_score = NUS_MLO_SURVEY_LABELS[0]).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(label_second_highest_score = NUS_MLO_SURVEY_LABELS[1]).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(label_third_highest_score = NUS_MLO_SURVEY_LABELS[2]).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(label_fourth_highest_score = NUS_MLO_SURVEY_LABELS[3]).count(),3)

        self.assertEqual(SurveyQuestionResponse.objects.filter(n_highest_score = 100).count(),1)#one with 100
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_highest_score = 99).count(),1)#one with 100
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_highest_score = 98).count(),1)#one with 100
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_second_highest_score = 10).count(),2)#only the first two
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_second_highest_score = 1).count(),1)#the last
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_third_highest_score = 10).count(),2)#only the first two
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_third_highest_score = 1).count(),1)#the last
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fourth_highest_score = 20).count(),2)#only the first two
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fourth_highest_score = 48).count(),1)#the last
        
        #Examine MLO 1 in detail
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_highest_score = 100).filter(associated_mlo=mlo_1).count(),1)
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_second_highest_score = 10).filter(associated_mlo=mlo_1).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_third_highest_score = 10).filter(associated_mlo=mlo_1).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fourth_highest_score = 20).filter(associated_mlo=mlo_1).count(),1)#
        #Examine MLO 3 in detail
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_highest_score = 98).filter(associated_mlo=mlo_3).count(),1)
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_second_highest_score = 1).filter(associated_mlo=mlo_3).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_third_highest_score = 1).filter(associated_mlo=mlo_3).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fourth_highest_score = 48).filter(associated_mlo=mlo_3).count(),1)#
        
        surv_obj = Survey.objects.filter(survey_title = survey_label).get()
        #Test the helper method
        srv_details = CalculateSurveyDetails(surv_obj.id)
        self.assertEqual(srv_details["title"], survey_label)
        self.assertEqual(srv_details["file"], '')
        self.assertEqual(srv_details["start_date"], surv_obj.opening_date)
        self.assertEqual(srv_details["end_date"], surv_obj.closing_date)
        self.assertEqual(srv_details["recipients"], 150)
        self.assertEqual(srv_details["comments"], survey_comment)
        self.assertEqual(srv_details["type_of_survey"], 'MLO')
        self.assertAlmostEqual(srv_details["average_response_rate"],100.0*((100+10+10+20)/150.0 + (99+10+10+20)/150.0 + (98+1+1+48)/150.0)/3.0)
        #Coverage for helper method (invalid ID passed in)
        self.assertEqual(CalculateSurveyDetails(surv_obj.id+1), 'Invalid ID')
        
        #Now call the module page. It should list the survey in its context
        response = self.client.get(reverse('workload_app:module', kwargs={'module_code': module_code}))
        self.assertEqual(response.status_code, 200)
        calculated_survey_table= response.context["mlo_survey_table"]
        self.assertEqual(len(calculated_survey_table),1)
        self.assertEqual(calculated_survey_table[0]["survey_name"],survey_label)
        self.assertEqual(calculated_survey_table[0]["survey_comments"],survey_comment)
        self.assertEqual(calculated_survey_table[0]["n_respondents"],150)
        self.assertEqual(calculated_survey_table[0]["survey_start_date"],surv_obj.opening_date)
        self.assertEqual(calculated_survey_table[0]["survey_end_date"],surv_obj.closing_date)

        #Now call the survey results page (simulate user clicking on "view results")
        response = self.client.get(reverse('workload_app:survey_results', kwargs={'survey_id': surv_obj.id}))
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.context["back_address"],'/workload_app/module/'+module_code)
        self.assertEqual(response.context["back_text"],'Back to module page')
        self.assertEqual(len(response.context["question_texts"]),3)#3 questions
        self.assertEqual(len(response.context["bar_chart_data"]),3)
        self.assertEqual(len(response.context["total_responses_per_question"]),3)
        self.assertEqual(len(response.context["percentages"]),3)
        self.assertEqual(len(response.context["cumulative_percentages"]),3)
        self.assertEqual(len(response.context["labels"]),4)
        self.assertEqual(response.context["labels"][0],NUS_MLO_SURVEY_LABELS[0])
        self.assertEqual(response.context["labels"][1],NUS_MLO_SURVEY_LABELS[1])
        self.assertEqual(response.context["labels"][2],NUS_MLO_SURVEY_LABELS[2])
        self.assertEqual(response.context["labels"][3],NUS_MLO_SURVEY_LABELS[3])
        self.assertEqual(response.context["question_texts"][0], mlo_1.mlo_description)
        self.assertEqual(response.context["question_texts"][1], mlo_2.mlo_description)
        self.assertEqual(response.context["question_texts"][2], mlo_3.mlo_description)
        self.assertEqual(len(response.context["bar_chart_data"][0]), 4)
        self.assertEqual(len(response.context["bar_chart_data"][1]), 4)
        self.assertEqual(len(response.context["bar_chart_data"][2]), 4)
        self.assertEqual(response.context["bar_chart_data"][0][0], 100)
        self.assertEqual(response.context["bar_chart_data"][0][1], 10)
        self.assertEqual(response.context["bar_chart_data"][0][2], 10)
        self.assertEqual(response.context["bar_chart_data"][0][3], 20)
        self.assertEqual(response.context["bar_chart_data"][1][0], 99)
        self.assertEqual(response.context["bar_chart_data"][1][1], 10)
        self.assertEqual(response.context["bar_chart_data"][1][2], 10)
        self.assertEqual(response.context["bar_chart_data"][1][3], 20)
        self.assertEqual(response.context["bar_chart_data"][2][0], 98)
        self.assertEqual(response.context["bar_chart_data"][2][1], 1)
        self.assertEqual(response.context["bar_chart_data"][2][2], 1)
        self.assertEqual(response.context["bar_chart_data"][2][3], 48)
        self.assertEqual(response.context["total_responses_per_question"][0], 100+10+10+20)
        self.assertEqual(response.context["total_responses_per_question"][1], 99+10+10+20)
        self.assertEqual(response.context["total_responses_per_question"][2], 98+1+1+48)

        self.assertEqual(len(response.context["percentages"][0]), 4)
        self.assertEqual(len(response.context["percentages"][1]), 4)
        self.assertEqual(len(response.context["percentages"][2]), 4)
        self.assertAlmostEqual(response.context["percentages"][0][0], 100*100/(100+10+10+20))
        self.assertAlmostEqual(response.context["percentages"][0][1], 100*10/(100+10+10+20))
        self.assertAlmostEqual(response.context["percentages"][0][2], 100*10/(100+10+10+20))
        self.assertAlmostEqual(response.context["percentages"][0][3], 100*20/(100+10+10+20))
        self.assertAlmostEqual(response.context["percentages"][1][0], 100*99/(99+10+10+20))
        self.assertAlmostEqual(response.context["percentages"][1][1], 100*10/(99+10+10+20))
        self.assertAlmostEqual(response.context["percentages"][1][2], 100*10/(99+10+10+20))
        self.assertAlmostEqual(response.context["percentages"][1][3], 100*20/(99+10+10+20))
        self.assertAlmostEqual(response.context["percentages"][2][0], 100*98/(98+1+1+48))
        self.assertAlmostEqual(response.context["percentages"][2][1], 100*1/(98+1+1+48))
        self.assertAlmostEqual(response.context["percentages"][2][2], 100*1/(98+1+1+48))
        self.assertAlmostEqual(response.context["percentages"][2][3], 100*48/(98+1+1+48))

        self.assertEqual(len(response.context["cumulative_percentages"][0]), 4)
        self.assertEqual(len(response.context["cumulative_percentages"][1]), 4)
        self.assertEqual(len(response.context["cumulative_percentages"][2]), 4)
        self.assertAlmostEqual(response.context["cumulative_percentages"][0][0], 100*100/(100+10+10+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][0][1], 100*(100+10)/(100+10+10+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][0][2], 100*(100+10+10)/(100+10+10+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][0][3], 100*(100+10+10+20)/(100+10+10+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][1][0], 100*99/(99+10+10+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][1][1], 100*(99+10)/(99+10+10+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][1][2], 100*(99+10+10)/(99+10+10+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][1][3], 100*(99+10+10+20)/(99+10+10+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][2][0], 100*98/(98+1+1+48))
        self.assertAlmostEqual(response.context["cumulative_percentages"][2][1], 100*(98+1)/(98+1+1+48))
        self.assertAlmostEqual(response.context["cumulative_percentages"][2][2], 100*(98+1+1)/(98+1+1+48))
        self.assertAlmostEqual(response.context["cumulative_percentages"][2][3], 100*(98+1+1+48)/(98+1+1+48))

        #Now try the POST with REMOVING
        self.assertEqual(Survey.objects.all().count(),1) #one survey should still be there
        self.assertEqual(SurveyQuestionResponse.objects.all().count(),3) #3 responses still there
        response = self.client.post(reverse('workload_app:module',kwargs={'module_code' : module_code}),{
            'select_MLO_survey_to_remove' : Survey.objects.first().id
        })
        self.assertEqual(response.status_code, 302)#Post redirects here
        #Nothing should be left
        self.assertEqual(Survey.objects.all().count(),0) #one survey should still be there
        self.assertEqual(SurveyQuestionResponse.objects.all().count(),0)
        response = self.client.get(reverse('workload_app:module', kwargs={'module_code': module_code}))
        self.assertEqual(response.status_code, 200)
        calculated_survey_table= response.context["mlo_survey_table"]
        self.assertEqual(len(calculated_survey_table),0)

    def test_add_SLO_survey(self):

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(Faculty.objects.all().count(),0) #0 to start with
        self.assertEqual(Department.objects.all().count(),0) #0 to start with
        self.assertEqual(Survey.objects.all().count(),0) #0 to start with
        self.assertEqual(Module.objects.all().count(),0) #0 to start with
        self.assertEqual(StudentLearningOutcome.objects.all().count(),0) #0 to start with
        self.assertEqual(ProgrammeOffered.objects.all().count(),0 ) #0 to start with
        self.assertEqual(SurveyQuestionResponse.objects.all().count(),0) #0 to start with
        
        new_faculty = Faculty.objects.create(faculty_name = "new faculty", faculty_acronym = "NFC")
        new_dept = Department.objects.create(department_name = "new_dept", department_acronym = "NDPT",faculty=new_faculty)
        acad_year = Academicyear.objects.create(start_year=2023)
        wl_scen = WorkloadScenario.objects.create(label = "test_scen", status = WorkloadScenario.OFFICIAL,\
                                                  dept = new_dept,academic_year = acad_year )
    
        prog_off  = ProgrammeOffered.objects.create(programme_name="test_prog", primary_dept = new_dept)
        #Create 3 MLOs
        slo_1 = StudentLearningOutcome.objects.create(slo_description = "First SLO", slo_short_description = "1", letter_associated = "a)", programme = prog_off)
        slo_2 = StudentLearningOutcome.objects.create(slo_description = "Second SLO", slo_short_description = "2", letter_associated = "b)", programme = prog_off)
        slo_3 = StudentLearningOutcome.objects.create(slo_description = "Third SLO", slo_short_description = "3", letter_associated = "c)", programme = prog_off)
        self.assertEqual(StudentLearningOutcome.objects.all().count(),3)

        #test the get 
        response = self.client.get(reverse('workload_app:accreditation',kwargs={'programme_id' : prog_off.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertContains(response, slo_1.slo_description)
        self.assertContains(response, slo_2.slo_description)
        self.assertContains(response, slo_3.slo_description)
        survey_comment = "hello, this is a test survey"
        survey_title = "title of teh survey"
        #Now try the POST with adding a SLO survey
        response = self.client.post(reverse('workload_app:accreditation',kwargs={'programme_id' : prog_off.id}),{
            'slo_survey_title' : survey_title,
            'start_date_month' : 1,
            'start_date_day' : 15,
            'start_date_year' : 2021,
            'end_date_month' : 1,
            'end_date_day' : 15,
            'end_date_year' : 2023,
            'totoal_N_recipients' : "150",
            'comments' : survey_comment,
            'slo_descr' + str(slo_1.id) : slo_1.slo_description,
            'n_highest_score' + str(slo_1.id): "100",            
            'n_second_highest_score' + str(slo_1.id) : "10",
            'n_third_highest_score' + str(slo_1.id): "10",
            'n_fourth_highest_score' + str(slo_1.id): "20",
            'n_fifth_highest_score' + str(slo_1.id): "20",
            'slo_descr' + str(slo_2.id) : slo_2.slo_description,
            'n_highest_score' + str(slo_2.id): "99",            
            'n_second_highest_score' + str(slo_2.id): "10",
            'n_third_highest_score' + str(slo_2.id): "10",
            'n_fourth_highest_score' + str(slo_2.id) : "20",
            'n_fifth_highest_score' + str(slo_2.id): "120",
            'slo_descr' + str(slo_3.id) : slo_3.slo_description,
            'n_highest_score' + str(slo_3.id) : "98",            
            'n_second_highest_score' + str(slo_3.id) : "1",
            'n_third_highest_score' + str(slo_3.id) : "1",
            'n_fourth_highest_score' + str(slo_3.id) : "48",
            'n_fifth_highest_score' + str(slo_3.id): "20",
        })
        self.assertEqual(response.status_code, 302) #post re-directs
        self.assertEqual(Survey.objects.all().count(),1) #one survey should have been created
        self.assertEqual(Survey.objects.filter(survey_title = survey_title).count(),1) #check name
        self.assertEqual(Survey.objects.filter(comments = survey_comment).count(),1) #check comment
        self.assertEqual(Survey.objects.filter(cohort_targeted__isnull = True).count(),1)#Default is NULL if not specified
        self.assertEqual(SurveyQuestionResponse.objects.all().count(),3) #One response for each SLO
        self.assertEqual(SurveyQuestionResponse.objects.filter(associated_slo = slo_1).count(),1)
        self.assertEqual(SurveyQuestionResponse.objects.filter(associated_slo = slo_2).count(),1)
        self.assertEqual(SurveyQuestionResponse.objects.filter(associated_slo = slo_3).count(),1)
        self.assertEqual(SurveyQuestionResponse.objects.filter(associated_mlo__isnull = True).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(associated_peo__isnull = True).count(),3)
        survey_created = Survey.objects.all().first()
        self.assertEqual(SurveyQuestionResponse.objects.filter(parent_survey = survey_created).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(label_highest_score = NUS_SLO_SURVEY_LABELS[0]).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(label_second_highest_score = NUS_SLO_SURVEY_LABELS[1]).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(label_third_highest_score = NUS_SLO_SURVEY_LABELS[2]).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(label_fourth_highest_score = NUS_SLO_SURVEY_LABELS[3]).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(label_fifth_highest_score = NUS_SLO_SURVEY_LABELS[4]).count(),3)

        self.assertEqual(SurveyQuestionResponse.objects.filter(n_highest_score = 100).count(),1)#one with 100
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_highest_score = 99).count(),1)#one with 99
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_highest_score = 98).count(),1)#one with 98
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_second_highest_score = 10).count(),2)#only the first two
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_second_highest_score = 1).count(),1)#the last
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_third_highest_score = 10).count(),2)#only the first two
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_third_highest_score = 1).count(),1)#the last
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fourth_highest_score = 20).count(),2)#only the first two
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fourth_highest_score = 48).count(),1)#the last
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fifth_highest_score = 20).count(),2)#first and last
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fifth_highest_score = 120).count(),1)#the second
        
        #Examine SLO 1 in detail
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_highest_score = 100).filter(associated_slo=slo_1).count(),1)
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_second_highest_score = 10).filter(associated_slo=slo_1).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_third_highest_score = 10).filter(associated_slo=slo_1).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fourth_highest_score = 20).filter(associated_slo=slo_1).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fifth_highest_score = 20).filter(associated_slo=slo_1).count(),1)#
        #Examine SLO 3 in detail
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_highest_score = 98).filter(associated_slo=slo_3).count(),1)
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_second_highest_score = 1).filter(associated_slo=slo_3).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_third_highest_score = 1).filter(associated_slo=slo_3).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fourth_highest_score = 48).filter(associated_slo=slo_3).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fifth_highest_score = 20).filter(associated_slo=slo_3).count(),1)#

        surv_obj = Survey.objects.filter(survey_title = survey_title).get()
        #Now call the survey results page (simulate user clicking on "view results")
        response = self.client.get(reverse('workload_app:survey_results', kwargs={'survey_id': surv_obj.id}))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["back_address"],'/workload_app/accreditation/'+str(prog_off.id))
        self.assertEqual(response.context["back_text"],'Back to accreditation page')
        self.assertEqual(len(response.context["question_texts"]),3)#3 questions
        self.assertEqual(len(response.context["bar_chart_data"]),3)
        self.assertEqual(len(response.context["total_responses_per_question"]),3)
        self.assertEqual(len(response.context["percentages"]),3)
        self.assertEqual(len(response.context["cumulative_percentages"]),3)
        self.assertEqual(len(response.context["labels"]),5)
        self.assertEqual(response.context["labels"][0],NUS_SLO_SURVEY_LABELS[0])
        self.assertEqual(response.context["labels"][1],NUS_SLO_SURVEY_LABELS[1])
        self.assertEqual(response.context["labels"][2],NUS_SLO_SURVEY_LABELS[2])
        self.assertEqual(response.context["labels"][3],NUS_SLO_SURVEY_LABELS[3])
        self.assertEqual(response.context["labels"][4],NUS_SLO_SURVEY_LABELS[4])
        self.assertEqual(response.context["question_texts"][0], slo_1.slo_description)
        self.assertEqual(response.context["question_texts"][1], slo_2.slo_description)
        self.assertEqual(response.context["question_texts"][2], slo_3.slo_description)
        self.assertEqual(len(response.context["bar_chart_data"][0]), 5)
        self.assertEqual(len(response.context["bar_chart_data"][1]), 5)
        self.assertEqual(len(response.context["bar_chart_data"][2]), 5)
        self.assertEqual(response.context["bar_chart_data"][0][0], 100)
        self.assertEqual(response.context["bar_chart_data"][0][1], 10)
        self.assertEqual(response.context["bar_chart_data"][0][2], 10)
        self.assertEqual(response.context["bar_chart_data"][0][3], 20)
        self.assertEqual(response.context["bar_chart_data"][0][4], 20)
        self.assertEqual(response.context["bar_chart_data"][1][0], 99)
        self.assertEqual(response.context["bar_chart_data"][1][1], 10)
        self.assertEqual(response.context["bar_chart_data"][1][2], 10)
        self.assertEqual(response.context["bar_chart_data"][1][3], 20)
        self.assertEqual(response.context["bar_chart_data"][1][4], 120)
        self.assertEqual(response.context["bar_chart_data"][2][0], 98)
        self.assertEqual(response.context["bar_chart_data"][2][1], 1)
        self.assertEqual(response.context["bar_chart_data"][2][2], 1)
        self.assertEqual(response.context["bar_chart_data"][2][3], 48)
        self.assertEqual(response.context["bar_chart_data"][2][4], 20)
        self.assertEqual(response.context["total_responses_per_question"][0], 100+10+10+20+20)
        self.assertEqual(response.context["total_responses_per_question"][1], 99+10+10+20+120)
        self.assertEqual(response.context["total_responses_per_question"][2], 98+1+1+48+20)

        self.assertEqual(len(response.context["percentages"][0]), 5)
        self.assertEqual(len(response.context["percentages"][1]), 5)
        self.assertEqual(len(response.context["percentages"][2]), 5)
        self.assertAlmostEqual(response.context["percentages"][0][0], 100*100/(100+10+10+20+20))
        self.assertAlmostEqual(response.context["percentages"][0][1], 100*10/(100+10+10+20+20))
        self.assertAlmostEqual(response.context["percentages"][0][2], 100*10/(100+10+10+20+20))
        self.assertAlmostEqual(response.context["percentages"][0][3], 100*20/(100+10+10+20+20))
        self.assertAlmostEqual(response.context["percentages"][0][4], 100*20/(100+10+10+20+20))
        self.assertAlmostEqual(response.context["percentages"][1][0], 100*99/(99+10+10+20+120))
        self.assertAlmostEqual(response.context["percentages"][1][1], 100*10/(99+10+10+20+120))
        self.assertAlmostEqual(response.context["percentages"][1][2], 100*10/(99+10+10+20+120))
        self.assertAlmostEqual(response.context["percentages"][1][3], 100*20/(99+10+10+20+120))
        self.assertAlmostEqual(response.context["percentages"][1][4], 100*120/(99+10+10+20+120))
        self.assertAlmostEqual(response.context["percentages"][2][0], 100*98/(98+1+1+48+20))
        self.assertAlmostEqual(response.context["percentages"][2][1], 100*1/(98+1+1+48+20))
        self.assertAlmostEqual(response.context["percentages"][2][2], 100*1/(98+1+1+48+20))
        self.assertAlmostEqual(response.context["percentages"][2][3], 100*48/(98+1+1+48+20))
        self.assertAlmostEqual(response.context["percentages"][2][4], 100*20/(98+1+1+48+20))

        self.assertEqual(len(response.context["cumulative_percentages"][0]), 5)
        self.assertEqual(len(response.context["cumulative_percentages"][1]), 5)
        self.assertEqual(len(response.context["cumulative_percentages"][2]), 5)
        self.assertAlmostEqual(response.context["cumulative_percentages"][0][0], 100*100/(100+10+10+20+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][0][1], 100*(100+10)/(100+10+10+20+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][0][2], 100*(100+10+10)/(100+10+10+20+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][0][3], 100*(100+10+10+20)/(100+10+10+20+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][0][4], 100*(100+10+10+20+20)/(100+10+10+20+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][1][0], 100*99/(99+10+10+20+120))
        self.assertAlmostEqual(response.context["cumulative_percentages"][1][1], 100*(99+10)/(99+10+10+20+120))
        self.assertAlmostEqual(response.context["cumulative_percentages"][1][2], 100*(99+10+10)/(99+10+10+20+120))
        self.assertAlmostEqual(response.context["cumulative_percentages"][1][3], 100*(99+10+10+20)/(99+10+10+20+120))
        self.assertAlmostEqual(response.context["cumulative_percentages"][1][4], 100*(99+10+10+20+120)/(99+10+10+20+120))
        self.assertAlmostEqual(response.context["cumulative_percentages"][2][0], 100*98/(98+1+1+48+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][2][1], 100*(98+1)/(98+1+1+48+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][2][2], 100*(98+1+1)/(98+1+1+48+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][2][3], 100*(98+1+1+48)/(98+1+1+48+20))
        self.assertAlmostEqual(response.context["cumulative_percentages"][2][4], 100*(98+1+1+48+20)/(98+1+1+48+20))

        #Cover the helper method in case of SLO
        surv_obj = Survey.objects.filter(survey_title = survey_title).get()
        srv_details = CalculateSurveyDetails(surv_obj.id)
        self.assertEqual(srv_details["title"], survey_title)
        self.assertEqual(srv_details["file"], '')
        self.assertEqual(srv_details["start_date"], surv_obj.opening_date)
        self.assertEqual(srv_details["end_date"], surv_obj.closing_date)
        self.assertEqual(srv_details["cohort_targeted"], 'N/A')
        self.assertEqual(srv_details["recipients"], 150)
        self.assertEqual(srv_details["comments"], survey_comment)
        self.assertEqual(srv_details["type_of_survey"], 'SLO')
        
        #Now try the POST with REMOVING
        self.assertEqual(Survey.objects.all().count(),1) #one survey should still be there
        self.assertEqual(SurveyQuestionResponse.objects.all().count(),3) #3 responses still there
        response = self.client.post(reverse('workload_app:accreditation',kwargs={'programme_id' : prog_off.id}),{
            'select_SLO_survey_to_remove' : Survey.objects.first().id
        })
        self.assertEqual(response.status_code, 302)#Post redirects here
        #Nothing should be left
        self.assertEqual(Survey.objects.all().count(),0) #
        self.assertEqual(SurveyQuestionResponse.objects.all().count(),0)#Responses deleted by cascade policy
        response = self.client.get(reverse('workload_app:accreditation', kwargs={'programme_id': prog_off.id}))
        self.assertEqual(response.status_code, 200)
        calculated_survey_table= response.context["slo_survey_table"]
        self.assertEqual(len(calculated_survey_table),0)


        #Now add abother one, same as beforem  but with targeted cohort
        cohort_year = Academicyear.objects.create(start_year=2020)
        response = self.client.post(reverse('workload_app:accreditation',kwargs={'programme_id' : prog_off.id}),{
            'slo_survey_title' : survey_title + "number_2",
            'start_date_month' : 1,
            'start_date_day' : 15,
            'start_date_year' : 2021,
            'end_date_month' : 1,
            'end_date_day' : 15,
            'end_date_year' : 2023,
            'totoal_N_recipients' : "150",
            'cohort_targeted' : cohort_year.id,
            'comments' : survey_comment,
            'slo_descr' + str(slo_1.id) : slo_1.slo_description,
            'n_highest_score' + str(slo_1.id): "100",            
            'n_second_highest_score' + str(slo_1.id) : "10",
            'n_third_highest_score' + str(slo_1.id): "10",
            'n_fourth_highest_score' + str(slo_1.id): "20",
            'n_fifth_highest_score' + str(slo_1.id): "20",
            'slo_descr' + str(slo_2.id) : slo_2.slo_description,
            'n_highest_score' + str(slo_2.id): "99",            
            'n_second_highest_score' + str(slo_2.id): "10",
            'n_third_highest_score' + str(slo_2.id): "10",
            'n_fourth_highest_score' + str(slo_2.id) : "20",
            'n_fifth_highest_score' + str(slo_2.id): "120",
            'slo_descr' + str(slo_3.id) : slo_3.slo_description,
            'n_highest_score' + str(slo_3.id) : "98",            
            'n_second_highest_score' + str(slo_3.id) : "1",
            'n_third_highest_score' + str(slo_3.id) : "1",
            'n_fourth_highest_score' + str(slo_3.id) : "48",
            'n_fifth_highest_score' + str(slo_3.id): "20",
        })
        self.assertEqual(response.status_code, 302) #post re-directs
        self.assertEqual(Survey.objects.all().count(),1) #one survey should have been created
        self.assertEqual(Survey.objects.filter(cohort_targeted__isnull = True).count(),0)#should be specified
        self.assertEqual(Survey.objects.filter(cohort_targeted__start_year =2020).count(),1)#should be specified as 2020 (see above)

    def test_add_remove_peo_survey(self):

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(Faculty.objects.all().count(),0) #0 to start with
        self.assertEqual(Department.objects.all().count(),0) #0 to start with
        self.assertEqual(Survey.objects.all().count(),0) #0 to start with
        self.assertEqual(Module.objects.all().count(),0) #0 to start with
        self.assertEqual(StudentLearningOutcome.objects.all().count(),0) #0 to start with
        self.assertEqual(ProgrammeOffered.objects.all().count(),0 ) #0 to start with
        self.assertEqual(SurveyQuestionResponse.objects.all().count(),0) #0 to start with
        
        new_faculty = Faculty.objects.create(faculty_name = "new faculty", faculty_acronym = "NFC")
        new_dept = Department.objects.create(department_name = "new_dept", department_acronym = "NDPT",faculty=new_faculty)
        acad_year = Academicyear.objects.create(start_year=2023)
        wl_scen = WorkloadScenario.objects.create(label = "test_scen", status = WorkloadScenario.OFFICIAL,\
                                                  dept = new_dept,academic_year = acad_year )
    
        prog_off  = ProgrammeOffered.objects.create(programme_name="test_prog", primary_dept = new_dept)
        #Create 3 PEO
        peo_1 = ProgrammeEducationalObjective.objects.create(peo_description = "First PEO", peo_short_description = "1", letter_associated = "a)", programme = prog_off)
        peo_2 = ProgrammeEducationalObjective.objects.create(peo_description = "Second SLO", peo_short_description = "2", letter_associated = "b)", programme = prog_off)
        peo_3 = ProgrammeEducationalObjective.objects.create(peo_description = "Third SLO", peo_short_description = "3", letter_associated = "c)", programme = prog_off)
        self.assertEqual(ProgrammeEducationalObjective.objects.all().count(),3)

        #test the get 
        response = self.client.get(reverse('workload_app:accreditation',kwargs={'programme_id' : prog_off.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertContains(response, peo_1.peo_description)
        self.assertContains(response, peo_2.peo_description)
        self.assertContains(response, peo_3.peo_description)

        survey_comment = "hello, this is a test PEO survey"
        survey_title = "title of the PEO survey"

        #Now try the POST witha dding a PEO survey
        response = self.client.post(reverse('workload_app:accreditation',kwargs={'programme_id' : prog_off.id}),{
            'peo_survey_title' : survey_title,
            'start_date_month' : 1,
            'start_date_day' : 15,
            'start_date_year' : 2021,
            'end_date_month' : 1,
            'end_date_day' : 15,
            'end_date_year' : 2023,
            'totoal_N_recipients' : "150",
            'comments' : survey_comment,
            'peo_descr' + str(peo_1.id) : peo_1.peo_description,
            'n_highest_score' + str(peo_1.id): "100",            
            'n_second_highest_score' + str(peo_1.id) : "10",
            'n_third_highest_score' + str(peo_1.id): "10",
            'n_fourth_highest_score' + str(peo_1.id): "20",
            'n_fifth_highest_score' + str(peo_1.id): "20",
            'peo_descr' + str(peo_2.id) : peo_2.peo_description,
            'n_highest_score' + str(peo_2.id): "99",            
            'n_second_highest_score' + str(peo_2.id): "10",
            'n_third_highest_score' + str(peo_2.id): "10",
            'n_fourth_highest_score' + str(peo_2.id) : "20",
            'n_fifth_highest_score' + str(peo_2.id): "120",
            'peo_descr' + str(peo_3.id) : peo_3.peo_description,
            'n_highest_score' + str(peo_3.id) : "98",            
            'n_second_highest_score' + str(peo_3.id) : "1",
            'n_third_highest_score' + str(peo_3.id) : "1",
            'n_fourth_highest_score' + str(peo_3.id) : "48",
            'n_fifth_highest_score' + str(peo_3.id): "20",
        })
        self.assertEqual(response.status_code, 302) #post re-directs
        self.assertEqual(Survey.objects.all().count(),1) #one survey should have been created
        self.assertEqual(Survey.objects.filter(survey_title = survey_title).count(),1) #check name
        self.assertEqual(Survey.objects.filter(comments = survey_comment).count(),1) #check comment
        self.assertEqual(SurveyQuestionResponse.objects.all().count(),3) #One response for each PEO
        self.assertEqual(SurveyQuestionResponse.objects.filter(associated_peo = peo_1).count(),1)
        self.assertEqual(SurveyQuestionResponse.objects.filter(associated_peo = peo_2).count(),1)
        self.assertEqual(SurveyQuestionResponse.objects.filter(associated_peo = peo_3).count(),1)
        self.assertEqual(SurveyQuestionResponse.objects.filter(associated_mlo__isnull = True).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(associated_slo__isnull = True).count(),3)
        survey_created = Survey.objects.all().first()
        self.assertEqual(SurveyQuestionResponse.objects.filter(parent_survey = survey_created).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(label_highest_score = NUS_SLO_SURVEY_LABELS[0]).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(label_second_highest_score = NUS_SLO_SURVEY_LABELS[1]).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(label_third_highest_score = NUS_SLO_SURVEY_LABELS[2]).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(label_fourth_highest_score = NUS_SLO_SURVEY_LABELS[3]).count(),3)
        self.assertEqual(SurveyQuestionResponse.objects.filter(label_fifth_highest_score = NUS_SLO_SURVEY_LABELS[4]).count(),3)

        self.assertEqual(SurveyQuestionResponse.objects.filter(n_highest_score = 100).count(),1)#one with 100
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_highest_score = 99).count(),1)#one with 99
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_highest_score = 98).count(),1)#one with 98
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_second_highest_score = 10).count(),2)#only the first two
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_second_highest_score = 1).count(),1)#the last
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_third_highest_score = 10).count(),2)#only the first two
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_third_highest_score = 1).count(),1)#the last
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fourth_highest_score = 20).count(),2)#only the first two
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fourth_highest_score = 48).count(),1)#the last
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fifth_highest_score = 20).count(),2)#first and last
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fifth_highest_score = 120).count(),1)#the second
        
        #Examine PEO 1 in detail
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_highest_score = 100).filter(associated_peo=peo_1).count(),1)
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_second_highest_score = 10).filter(associated_peo=peo_1).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_third_highest_score = 10).filter(associated_peo=peo_1).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fourth_highest_score = 20).filter(associated_peo=peo_1).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fifth_highest_score = 20).filter(associated_peo=peo_1).count(),1)#
        #Examine PEO 3 in detail
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_highest_score = 98).filter(associated_peo=peo_3).count(),1)
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_second_highest_score = 1).filter(associated_peo=peo_3).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_third_highest_score = 1).filter(associated_peo=peo_3).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fourth_highest_score = 48).filter(associated_peo=peo_3).count(),1)#
        self.assertEqual(SurveyQuestionResponse.objects.filter(n_fifth_highest_score = 20).filter(associated_peo=peo_3).count(),1)#
        
        #Cover the helper method in case of PEO
        surv_obj = Survey.objects.filter(survey_title = survey_title).get()
        srv_details = CalculateSurveyDetails(surv_obj.id)
        self.assertEqual(srv_details["title"], survey_title)
        self.assertEqual(srv_details["file"], '')
        self.assertEqual(srv_details["start_date"], surv_obj.opening_date)
        self.assertEqual(srv_details["end_date"], surv_obj.closing_date)
        self.assertEqual(srv_details["recipients"], 150)
        self.assertEqual(srv_details["comments"], survey_comment)
        self.assertEqual(srv_details["type_of_survey"], 'PEO')
        
        #Now try the POST with REMOVING
        self.assertEqual(Survey.objects.all().count(),1) #one survey should still be there
        self.assertEqual(SurveyQuestionResponse.objects.all().count(),3) #3 responses still there
        response = self.client.post(reverse('workload_app:accreditation',kwargs={'programme_id' : prog_off.id}),{
            'select_PEO_survey_to_remove' : Survey.objects.first().id
        })
        self.assertEqual(response.status_code, 302)#Post redirects here
        #Nothing should be left
        self.assertEqual(Survey.objects.all().count(),0) #
        self.assertEqual(SurveyQuestionResponse.objects.all().count(),0)#Responses deleted by cascade policy
