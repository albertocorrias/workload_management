from .models import Survey,SurveyQuestionResponse,ProgrammeOffered, SurveyLabelSet, StudentLearningOutcome


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

#TO BE CHECKED AND TESTED!!!!!!!!!!!!!!!!!!!!!!
def DeteremineSurveyInitialValues(survey_id):
    ret = {}
    surv_obj =  Survey.objects.filter(id = survey_id).get()
    labels = surv_obj.likert_labels.GetListOfLabels()
    
    for resp in SurveyQuestionResponse.objects.filter(parent_survey__id = survey_id):
        lo_id_involved = 0
        if (resp.associated_slo is not None):
            lo_id_involved = resp.associated_slo.id
        if (resp.associated_mlo is not None):
            lo_id_involved = resp.associated_mlo.id
        if (resp.associated_peo is not None):
            lo_id_involved = resp.associated_peo.id

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
            #Note concatenation between option index and slo-id (used in the form)
            ret[str(opt_idx)+str(lo_id_involved)] = all_scores[opt_idx]

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


        