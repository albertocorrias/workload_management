from .models import Survey,SurveyQuestionResponse,ProgrammeOffered, SurveyLabelSet, StudentLearningOutcome,ModuleLearningOutcome, ProgrammeEducationalObjective


def CalculateTotalResponsesForQuestion(response_id):
    response = SurveyQuestionResponse.objects.filter(id = response_id).get()
    n_for_question  = 0
    if (response.n_highest_score >= 0) : n_for_question += response.n_highest_score
    if (response.n_second_highest_score >= 0) : n_for_question += response.n_second_highest_score
    if (response.n_third_highest_score >= 0) : n_for_question += response.n_third_highest_score
    if (response.n_fourth_highest_score >= 0) : n_for_question += response.n_fourth_highest_score
    if (response.n_fifth_highest_score >= 0) : n_for_question += response.n_fifth_highest_score
    if (response.n_sixth_highest_score >= 0) : n_for_question += response.n_sixth_highest_score
    return n_for_question

def CalulatePositiveResponsesFractionForQuestion(response_id):
    total_respondents = CalculateTotalResponsesForQuestion(response_id)
    response = SurveyQuestionResponse.objects.filter(id = response_id).get()
    #For now, we count the top 2 as "positive". If more sophistiaction is needed, adjust here
    return (response.n_highest_score + response.n_second_highest_score)/total_respondents

#Given and ID, it returns info on the survey
def CalculateSurveyDetails(survey_id):
    ret = 'Invalid ID'
    if (Survey.objects.filter(id = survey_id).count() ==1):
        survey = Survey.objects.filter(id = survey_id).get()
        original_file_url = ''#Templates may check length
        if (len(Survey.objects.filter(id = survey_id).get().original_file.name) > 0):
            original_file_url = Survey.objects.filter(id = survey_id).get().original_file.url
        #Calculate average response rate
        av_response_rate = 0
        how_many_questions = 0
        n_recipients = survey.max_respondents
        for response in SurveyQuestionResponse.objects.filter(parent_survey__id = survey_id):
            av_response_rate += CalculateTotalResponsesForQuestion(response.id)/n_recipients
            how_many_questions = how_many_questions + 1
        if (how_many_questions > 0 ):
            av_response_rate = 100*av_response_rate/how_many_questions

        survey_type = survey.survey_type
        cohort_targeted = 'N/A'
        if (survey.cohort_targeted is not None):
            cohort_targeted = survey.cohort_targeted.__str__()
        
        ret = {
        'survey_id' : survey_id,
        'type_of_survey' : survey_type,
        'title' : survey.survey_title,
        'file' : original_file_url,
        'start_date' : survey.opening_date,
        'end_date' : survey.closing_date,
        'cohort_targeted' : cohort_targeted,
        'recipients' : n_recipients,
        'comments' : survey.comments,
        'average_response_rate' : av_response_rate
        }
    return ret


def DeteremineSurveyInitialValues(survey_id, module_code):
    ''''
    This method determines the initial values of a survey
    '''
    ret = {}
    surv_obj =  Survey.objects.filter(id = survey_id).get()
    labels = surv_obj.likert_labels.GetListOfLabels()
    question_index = 0
    for resp in SurveyQuestionResponse.objects.filter(parent_survey__id = survey_id):
        lo_id_involved = 0
        question_text = ''
        if (resp.associated_slo is not None):
            lo_id_involved = resp.associated_slo.id
            #question_text = StudentLearningOutcome.objects.filter(id = lo_id_involved).get().slo_description
        if (resp.associated_mlo is not None):
            lo_id_involved = resp.associated_mlo.id
            #question_text = ModuleLearningOutcome.objects.filter(id = lo_id_involved).get().mlo_description
        if (resp.associated_peo is not None):
            lo_id_involved = resp.associated_peo.id
            #question_text = ProgrammeEducationalObjective.objects.filter(id = lo_id_involved).get().peo_description

        ret['survey_' + str(survey_id) + '_question_'+ str(question_index)] = resp.question_text
        ret['survey_' + str(survey_id) + '_associated_lo_of_question_'+ str(question_index)] = lo_id_involved
        all_scores = [resp.n_highest_score,\
                      resp.n_second_highest_score, \
                      resp.n_third_highest_score,\
                      resp.n_fourth_highest_score,\
                      resp.n_fifth_highest_score,\
                      resp.n_sixth_highest_score,\
                      resp.n_seventh_highest_score,\
                      resp.n_eighth_highest_score,\
                      resp.n_ninth_highest_score,\
                      resp.n_tenth_highest_score]
        for opt_idx in range(0,len(labels)):
            #Note concatenation used in the form
            ret['survey_' + str(survey_id) + '_question_' +  str(question_index) + 'response_' + str(opt_idx)] = all_scores[opt_idx]
        question_index += 1

    if (question_index == 0): #This is when there were no previous responses - fresh input
        programme_id = surv_obj.programme_associated.id
        qn_txt = []
        lo_ids = []
        if (surv_obj.survey_type == Survey.SurveyType.SLO):
            relevant_lo_queryset = StudentLearningOutcome.objects.filter(programme__id = programme_id)
            for qs in relevant_lo_queryset:
                qn_txt.append(qs.slo_description)
                lo_ids.append(qs.id)    
        if (surv_obj.survey_type == Survey.SurveyType.MLO):
            #lo_id_involved = resp.associated_mlo.id
            relevant_lo_queryset = ModuleLearningOutcome.objects.filter(module_code = module_code)
            for qs in relevant_lo_queryset:
                qn_txt.append(qs.mlo_description)
                lo_ids.append(qs.id)    
        if (surv_obj.survey_type == Survey.SurveyType.PEO):
            relevant_lo_queryset = ProgrammeEducationalObjective.objects.filter(programme__id = programme_id)
            for qs in relevant_lo_queryset:
                qn_txt.append(qs.peo_description)
                lo_ids.append(qs.id)    
        
        for question_index in range(0,relevant_lo_queryset.count()):
            ret['survey_' + str(survey_id) + '_question_'+ str(question_index)] = qn_txt[question_index]
            ret['survey_' + str(survey_id) + '_associated_lo_of_question_'+ str(question_index)] =lo_ids[question_index]  
            for opt_idx in range(0,len(labels)):
                #Note concatenation 
                ret['survey_' + str(survey_id) + '_question_' +  str(question_index) + 'response_' + str(opt_idx)] = 0
    return ret


def DetermineSurveyLabelsForProgramme(prog_id):
    prog_qs = ProgrammeOffered.objects.filter(id = prog_id)
    if (prog_qs.count() != 1):
        return []#return empty list if this is called with a wrong ID. Should really never happen...
    prog_obj = prog_qs.get()#should be safe now
    
    if prog_obj.slo_survey_labels is None:#No link
        default_slo_set =  SurveyLabelSet.objects.create(highest_score_label = "Strongly agree",\
                                        second_highest_score_label = "Agree",\
                                        third_highest_score_label = "Neutral",\
                                        fourth_highest_score_label = "Disagree",\
                                        fifth_highest_score_label = "Strongly disagree")
        prog_obj.slo_survey_labels = default_slo_set

    if prog_obj.mlo_survey_labels is None:#No link
        default_mlo_set =  SurveyLabelSet.objects.create(highest_score_label = "Strongly agree",\
                                        second_highest_score_label = "Agree",\
                                        third_highest_score_label = "Neutral",\
                                        fourth_highest_score_label = "Disagree",\
                                        fifth_highest_score_label = "Strongly disagree")
        prog_obj.mlo_survey_labels = default_mlo_set

    if prog_obj.peo_survey_labels is None:#No link
        default_peo_set =  SurveyLabelSet.objects.create(highest_score_label = "Strongly agree",\
                                        second_highest_score_label = "Agree",\
                                        third_highest_score_label = "Neutral",\
                                        fourth_highest_score_label = "Disagree",\
                                        fifth_highest_score_label = "Strongly disagree")
        prog_obj.peo_survey_labels = default_peo_set
    
    prog_obj.save(force_update=True)
    prog_obj = ProgrammeOffered.objects.filter(id = prog_id).get()
    #At this stage, the programme will have links to objects 
    return {
        'slo_survey_labels' : prog_obj.slo_survey_labels.GetListOfLabels(),
        'peo_survey_labels' : prog_obj.peo_survey_labels.GetListOfLabels(),
        'mlo_survey_labels' : prog_obj.mlo_survey_labels.GetListOfLabels(),
        'slo_survey_labels_object' : prog_obj.slo_survey_labels,
        'peo_survey_labels_object' : prog_obj.peo_survey_labels,
        'mlo_survey_labels_object' : prog_obj.mlo_survey_labels
    }


        