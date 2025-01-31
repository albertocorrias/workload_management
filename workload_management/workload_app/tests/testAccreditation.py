from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *
from workload_app.global_constants import DEFAULT_TRACK_NAME,DEFAULT_SERVICE_ROLE_NAME
from workload_app.models import StudentLearningOutcome, ProgrammeOffered, Faculty, Department, ProgrammeEducationalObjective,PEOSLOMapping, Academicyear


class TestAccreditation(TestCase):
    def setup_user(self):
        #The tets client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'workload')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
    
    def test_add_remove_slo_and_peo(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        new_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        self.assertEqual(ProgrammeOffered.objects.all().count(),0)
        self.assertEqual(StudentLearningOutcome.objects.all().count(),0)
        new_prog = ProgrammeOffered.objects.create(programme_name="test_prog", primary_dept = new_dept)
        slo_descr = "hello hello"
        slo_short_desc = "hello"
        response = self.client.post(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}),
                        {'slo_description':slo_descr, 'slo_short_description': slo_short_desc, 'is_default_by_accreditor' : True, 'letter_associated' : 'a',\
                        'fresh_record' : True})
        self.assertEqual(response.status_code, 302) #Re-direct
        self.assertEqual(StudentLearningOutcome.objects.all().count(),1)
        self.assertEqual(StudentLearningOutcome.objects.filter(slo_description=slo_descr).count(),1)
        self.assertEqual(StudentLearningOutcome.objects.filter(slo_short_description=slo_short_desc).count(),1)
        self.assertEqual(StudentLearningOutcome.objects.filter(is_default_by_accreditor=True).count(),1)
        self.assertEqual(StudentLearningOutcome.objects.filter(is_default_by_accreditor=False).count(),0)
        self.assertEqual(StudentLearningOutcome.objects.filter(letter_associated='a').count(),1)
        self.assertEqual(StudentLearningOutcome.objects.filter(programme=new_prog).count(),1)
        self.assertEqual(StudentLearningOutcome.objects.filter(cohort_valid_from__isnull=True).count(),1)
        self.assertEqual(StudentLearningOutcome.objects.filter(cohort_valid_to__isnull=True).count(),1)
        #Try editing
        slo_in_db = StudentLearningOutcome.objects.filter(slo_description=slo_descr).get()
        new_description = "new one"
        response = self.client.post(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}),
                        {'slo_description':new_description, 'slo_short_description':slo_short_desc, 'is_default_by_accreditor' : True, 'letter_associated' : 'a',\
                        'fresh_record' : False, 'slo_id' : slo_in_db.id })
        self.assertEqual(response.status_code, 302) #Re-direct
        self.assertEqual(StudentLearningOutcome.objects.all().count(),1)
        self.assertEqual(StudentLearningOutcome.objects.filter(slo_short_description=slo_short_desc).count(),1)
        self.assertEqual(StudentLearningOutcome.objects.filter(slo_description=slo_descr).count(),0)
        self.assertEqual(StudentLearningOutcome.objects.filter(slo_description=new_description).count(),1)

        #Now remove it
        response = self.client.post(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}),
                        {'select_slo_to_remove':slo_in_db.id })
        self.assertEqual(response.status_code, 302) #Re-direct
        self.assertEqual(StudentLearningOutcome.objects.all().count(),0)

        acad_year_1 = Academicyear.objects.create(start_year=2020)
        acad_year_2 = Academicyear.objects.create(start_year=2022)
        #Add another one with "Expiry dates"
        response = self.client.post(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}),
                        {'slo_description':"hello", 'slo_short_description': "h", 'is_default_by_accreditor' : True, 'letter_associated' : 'a',\
                        'fresh_record' : True, 'cohort_valid_from':acad_year_1.id, 'cohort_valid_to':acad_year_2.id})
        self.assertEqual(StudentLearningOutcome.objects.all().count(),1)
        self.assertEqual(StudentLearningOutcome.objects.filter(cohort_valid_from__isnull=True).count(),0)
        self.assertEqual(StudentLearningOutcome.objects.filter(cohort_valid_to__isnull=True).count(),0)
        self.assertEqual(StudentLearningOutcome.objects.filter(cohort_valid_from__start_year=2020).count(),1)
        self.assertEqual(StudentLearningOutcome.objects.filter(cohort_valid_to__start_year=2022).count(),1)
        #now edit this one
        acad_year_3 = Academicyear.objects.create(start_year=2018)
        acad_year_4 = Academicyear.objects.create(start_year=2024)
        slo_in_db = StudentLearningOutcome.objects.filter(slo_description='hello').get()
        response = self.client.post(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}),
                        {'slo_description':"hello", 'slo_short_description': "h", 'is_default_by_accreditor' : True, 'letter_associated' : 'a',\
                        'fresh_record' : False, 'cohort_valid_from':acad_year_3.id, 'cohort_valid_to':acad_year_4.id, 'slo_id' : slo_in_db.id})
        self.assertEqual(StudentLearningOutcome.objects.all().count(),1)
        self.assertEqual(StudentLearningOutcome.objects.filter(cohort_valid_from__isnull=True).count(),0)
        self.assertEqual(StudentLearningOutcome.objects.filter(cohort_valid_to__isnull=True).count(),0)
        self.assertEqual(StudentLearningOutcome.objects.filter(cohort_valid_from__start_year=2020).count(),0)
        self.assertEqual(StudentLearningOutcome.objects.filter(cohort_valid_to__start_year=2022).count(),0)
        self.assertEqual(StudentLearningOutcome.objects.filter(cohort_valid_from__start_year=2018).count(),1)
        self.assertEqual(StudentLearningOutcome.objects.filter(cohort_valid_to__start_year=2024).count(),1)


        self.assertEqual(ProgrammeEducationalObjective.objects.all().count(),0)
        #Add a PEO
        peo_descr = "hello new PEO"
        peo_short_desc = "hello PEO"
        response = self.client.post(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}),
                        {'peo_description':peo_descr, 'peo_short_description': peo_short_desc,'letter_associated' : 'a',\
                        'fresh_record' : True})
        self.assertEqual(response.status_code, 302) #Re-direct
        self.assertEqual(ProgrammeEducationalObjective.objects.all().count(),1)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_description=peo_descr).count(),1)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_short_description=peo_short_desc).count(),1)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(letter_associated='a').count(),1)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_cohort_valid_from__isnull=True).count(),1)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_cohort_valid_to__isnull=True).count(),1)

        peo_in_db = ProgrammeEducationalObjective.objects.filter(peo_description  = peo_descr).get()
        #edit
        new_peo_descr = "this is the new descrition"
        response = self.client.post(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}),
                        {'peo_description':new_peo_descr, 'peo_short_description': peo_short_desc, 'letter_associated' : 'a','peo_id' : peo_in_db.id,\
                        'fresh_record' : False})
        self.assertEqual(response.status_code, 302) #Re-direct
        self.assertEqual(ProgrammeEducationalObjective.objects.all().count(),1)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_description=peo_descr).count(),0)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_description=new_peo_descr).count(),1)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_short_description=peo_short_desc).count(),1)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(letter_associated='a').count(),1)
        
        #Now remove it
        response = self.client.post(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}),
                        {'select_peo_to_remove':peo_in_db.id })
        self.assertEqual(response.status_code, 302) #Re-direct
        self.assertEqual(ProgrammeEducationalObjective.objects.all().count(),0)

        #Create another one with "expiry dates"
        response = self.client.post(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}),
                        {'peo_description':peo_descr, 'peo_short_description': peo_short_desc,'letter_associated' : 'a',\
                         'peo_cohort_valid_from': acad_year_1.id,'peo_cohort_valid_to': acad_year_2.id,
                        'fresh_record' : True})
        self.assertEqual(ProgrammeEducationalObjective.objects.all().count(),1)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_cohort_valid_from__isnull=True).count(),0)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_cohort_valid_to__isnull=True).count(),0)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_cohort_valid_from__start_year=2020).count(),1)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_cohort_valid_to__start_year=2022).count(),1)
        #Now edit this one
        peo_in_db = ProgrammeEducationalObjective.objects.filter(peo_description  = peo_descr).get()
        response = self.client.post(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}),
                        {'peo_description':new_peo_descr, 'peo_short_description': peo_short_desc, 'letter_associated' : 'a','peo_id' : peo_in_db.id,\
                         'peo_cohort_valid_from': acad_year_3.id,'peo_cohort_valid_to': acad_year_4.id,
                        'fresh_record' : False})
        self.assertEqual(ProgrammeEducationalObjective.objects.all().count(),1)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_cohort_valid_from__isnull=True).count(),0)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_cohort_valid_to__isnull=True).count(),0)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_cohort_valid_from__start_year=2020).count(),0)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_cohort_valid_to__start_year=2022).count(),0)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_cohort_valid_from__start_year=2018).count(),1)
        self.assertEqual(ProgrammeEducationalObjective.objects.filter(peo_cohort_valid_to__start_year=2024).count(),1)

        #Test the survey table settings
        response = self.client.get(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(len(response.context["slo_survey_table"]),0)
        self.assertEqual(len(response.context["survey_settings_table"]),3)
        self.assertEqual(len(response.context["survey_settings_table"][0]),6)#Defaults is a 5-points scale + the "PEO label"
        self.assertEqual(len(response.context["survey_settings_table"][1]),6)
        self.assertEqual(len(response.context["survey_settings_table"][2]),6)
        #TEst the default values
        self.assertEqual(response.context["survey_settings_table"][0][1],"Strongly agree")
        self.assertEqual(response.context["survey_settings_table"][1][1],"Strongly agree")
        self.assertEqual(response.context["survey_settings_table"][2][1],"Strongly agree")
        self.assertEqual(response.context["survey_settings_table"][0][2],"Agree")
        self.assertEqual(response.context["survey_settings_table"][1][2],"Agree")
        self.assertEqual(response.context["survey_settings_table"][2][2],"Agree")
        self.assertEqual(response.context["survey_settings_table"][0][3],"Neutral")
        self.assertEqual(response.context["survey_settings_table"][1][3],"Neutral")
        self.assertEqual(response.context["survey_settings_table"][2][3],"Neutral")
        self.assertEqual(response.context["survey_settings_table"][0][4],"Disagree")
        self.assertEqual(response.context["survey_settings_table"][1][4],"Disagree")
        self.assertEqual(response.context["survey_settings_table"][2][4],"Disagree")
        self.assertEqual(response.context["survey_settings_table"][0][5],"Strongly disagree")
        self.assertEqual(response.context["survey_settings_table"][1][5],"Strongly disagree")
        self.assertEqual(response.context["survey_settings_table"][2][5],"Strongly disagree")
        #Now change one SLO labels,for example
        # response = self.client.post(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}),
        #                 {'slo_id': slo_list[0]["slo_id"],
        #                  'peo_id' : slo_list[0]["peo_mapping"][1]["peo_id"],
        #                  'mapping_strength'+str(slo_list[0]["peo_mapping"][1]["peo_id"]) : 3,
        #                  'peo_id' : slo_list[0]["peo_mapping"][0]["peo_id"],
        #                  'mapping_strength'+str(slo_list[0]["peo_mapping"][0]["peo_id"]) : 0})

    def testSLOPEOMapping(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        new_fac = Faculty.objects.create(faculty_name="test_fac", faculty_acronym="FFCC")
        new_dept = Department.objects.create(department_name="test_dept", department_acronym="TTDD", faculty=new_fac)
        self.assertEqual(ProgrammeOffered.objects.all().count(),0)
        self.assertEqual(StudentLearningOutcome.objects.all().count(),0)
        new_prog = ProgrammeOffered.objects.create(programme_name="test_prog", primary_dept = new_dept)
        self.assertEqual(PEOSLOMapping.objects.all().count(),0)
        #Create 3 SLO and 2 PEO
        slo_a = StudentLearningOutcome.objects.create(slo_description="SLO A", slo_short_description ="short slo A", is_default_by_accreditor=True, letter_associated="a", programme=new_prog)
        slo_b = StudentLearningOutcome.objects.create(slo_description="SLO B", slo_short_description ="short slo B", is_default_by_accreditor=True, letter_associated="b", programme=new_prog)
        slo_c = StudentLearningOutcome.objects.create(slo_description="SLO C", slo_short_description ="short slo C", is_default_by_accreditor=True, letter_associated="c", programme=new_prog)
        peo_a = ProgrammeEducationalObjective.objects.create(peo_description="PEO A", peo_short_description = "PEO short A", letter_associated="a", programme=new_prog)
        peo_b = ProgrammeEducationalObjective.objects.create(peo_description="PEO B", peo_short_description = "PEO short B", letter_associated="b", programme=new_prog)
        self.assertEqual(ProgrammeEducationalObjective.objects.all().count(),2)
        self.assertEqual(StudentLearningOutcome.objects.all().count(),3)
        self.assertEqual(PEOSLOMapping.objects.all().count(),0)
        #Test the get
        response = self.client.get(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}))
        self.assertEqual(response.status_code, 200) #No issues
        #The view should have created default mappings with 0 strength for all
        self.assertEqual(PEOSLOMapping.objects.all().count(),6) #3 SLO times 2 PEO
        for mapping in PEOSLOMapping.objects.all():
            self.assertEqual(mapping.strength,0)
        #Get again and check that it doens't create any more mappings
        response = self.client.get(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}))
        self.assertEqual(response.status_code, 200) #No issues
        #Same as above. Must not create additional
        self.assertEqual(PEOSLOMapping.objects.all().count(),6) #3 SLO times 2 PEO
        for mapping in PEOSLOMapping.objects.all():
            self.assertEqual(mapping.strength,0)
        #Check the context
        self.assertEqual(len(response.context["peo_list"]),2)
        self.assertEqual(len(response.context["slo_list"]),3)
        self.assertEqual(len(response.context["slo_list"][0]["peo_mapping"]),2)
        self.assertEqual(len(response.context["slo_list"][1]["peo_mapping"]),2)
        self.assertEqual(len(response.context["slo_list"][2]["peo_mapping"]),2)
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][0]["strength"],0)
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][1]["strength"],0)
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][0]["strength"],0)
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][1]["strength"],0)
        self.assertEqual(response.context["slo_list"][2]["peo_mapping"][0]["strength"],0)
        self.assertEqual(response.context["slo_list"][2]["peo_mapping"][1]["strength"],0)
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][0]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][1]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][0]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][1]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][2]["peo_mapping"][0]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][2]["peo_mapping"][1]["mapping_icon"],'circle.svg')
        
        #assign a mapping strength
        slo_list = response.context["slo_list"]
        response = self.client.post(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}),
                        {'slo_id': slo_list[0]["slo_id"],
                         'peo_id' : slo_list[0]["peo_mapping"][1]["peo_id"],
                         'mapping_strength'+str(slo_list[0]["peo_mapping"][1]["peo_id"]) : 3,
                         'peo_id' : slo_list[0]["peo_mapping"][0]["peo_id"],
                         'mapping_strength'+str(slo_list[0]["peo_mapping"][0]["peo_id"]) : 0})

        self.assertEqual(response.status_code, 302) #Re-direct
        response = self.client.get(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}))
        self.assertEqual(PEOSLOMapping.objects.all().count(),6)#still 6
        self.assertEqual(len(response.context["peo_list"]),2)
        self.assertEqual(len(response.context["slo_list"]),3)
        self.assertEqual(len(response.context["slo_list"][0]["peo_mapping"]),2)
        self.assertEqual(len(response.context["slo_list"][1]["peo_mapping"]),2)
        self.assertEqual(len(response.context["slo_list"][2]["peo_mapping"]),2)
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][0]["strength"],0)
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][1]["strength"],3)#Edited strength
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][0]["strength"],0)
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][1]["strength"],0)
        self.assertEqual(response.context["slo_list"][2]["peo_mapping"][0]["strength"],0)
        self.assertEqual(response.context["slo_list"][2]["peo_mapping"][1]["strength"],0)
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][0]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][1]["mapping_icon"],'circle-fill.svg')#new icon here
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][0]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][1]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][2]["peo_mapping"][0]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][2]["peo_mapping"][1]["mapping_icon"],'circle.svg')

        #Add a partial mapping
        response = self.client.post(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}),
                        {'slo_id': slo_list[2]["slo_id"],
                         'peo_id' : slo_list[2]["peo_mapping"][1]["peo_id"],
                         'mapping_strength'+str(slo_list[0]["peo_mapping"][0]["peo_id"]) : 0,
                         'peo_id' : slo_list[2]["peo_mapping"][0]["peo_id"],
                         'mapping_strength'+str(slo_list[0]["peo_mapping"][1]["peo_id"]) : 1})
        
        response = self.client.get(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}))
        self.assertEqual(PEOSLOMapping.objects.all().count(),6)#still 6
        self.assertEqual(len(response.context["peo_list"]),2)
        self.assertEqual(len(response.context["slo_list"]),3)
        self.assertEqual(len(response.context["slo_list"][0]["peo_mapping"]),2)
        self.assertEqual(len(response.context["slo_list"][1]["peo_mapping"]),2)
        self.assertEqual(len(response.context["slo_list"][2]["peo_mapping"]),2)
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][0]["strength"],0)
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][1]["strength"],3)#Edited strength
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][0]["strength"],0)
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][1]["strength"],0)
        self.assertEqual(response.context["slo_list"][2]["peo_mapping"][0]["strength"],0)
        self.assertEqual(response.context["slo_list"][2]["peo_mapping"][1]["strength"],1)#Edited to 1 
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][0]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][1]["mapping_icon"],'circle-fill.svg')#new icon here
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][0]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][1]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][2]["peo_mapping"][0]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][2]["peo_mapping"][1]["mapping_icon"],'circle-half.svg')#Edited icon as well

        #Remove one SLO
        slo_to_remove = StudentLearningOutcome.objects.filter(slo_description="SLO C").get()
        response = self.client.post(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}),
                        {'select_slo_to_remove':slo_to_remove.id })
        self.assertEqual(response.status_code, 302) #Re-direct

        response = self.client.get(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}))
        self.assertEqual(StudentLearningOutcome.objects.all().count(),2)
        self.assertEqual(ProgrammeEducationalObjective.objects.all().count(),2)
        self.assertEqual(PEOSLOMapping.objects.all().count(),4)#2 SLO times 2 PEO
        self.assertEqual(len(response.context["peo_list"]),2)
        self.assertEqual(len(response.context["slo_list"]),2)
        self.assertEqual(len(response.context["slo_list"][0]["peo_mapping"]),2)
        self.assertEqual(len(response.context["slo_list"][1]["peo_mapping"]),2)
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][0]["strength"],0)
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][1]["strength"],3)#same as above
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][0]["strength"],0)
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][1]["strength"],0)
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][0]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][1]["mapping_icon"],'circle-fill.svg')#new icon here from above
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][0]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][1]["mapping_icon"],'circle.svg')

        #Remove one PEO
        peo_to_remove = ProgrammeEducationalObjective.objects.filter(peo_description="PEO B").get()
        response = self.client.post(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}),
                        {'select_peo_to_remove':peo_to_remove.id })
        self.assertEqual(response.status_code, 302) #Re-direct
        
        response = self.client.get(reverse('workload_app:accreditation',  kwargs={'programme_id': new_prog.id}))
        self.assertEqual(StudentLearningOutcome.objects.all().count(),2)
        self.assertEqual(ProgrammeEducationalObjective.objects.all().count(),1)
        self.assertEqual(PEOSLOMapping.objects.all().count(),2)#2 SLO times 1 PEO
        self.assertEqual(len(response.context["peo_list"]),1)
        self.assertEqual(len(response.context["slo_list"]),2)
        self.assertEqual(len(response.context["slo_list"][0]["peo_mapping"]),1)
        self.assertEqual(len(response.context["slo_list"][1]["peo_mapping"]),1)
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][0]["strength"],0)
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][0]["strength"],0)
        self.assertEqual(response.context["slo_list"][0]["peo_mapping"][0]["mapping_icon"],'circle.svg')
        self.assertEqual(response.context["slo_list"][1]["peo_mapping"][0]["mapping_icon"],'circle.svg')