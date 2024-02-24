from .models import Survey,SurveyQuestionResponse


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
        av_response_rate = 100*av_response_rate/how_many_questions

        survey_type = ''
        #take one response 
        resp = SurveyQuestionResponse.objects.filter(parent_survey__id = survey_id).first()
        if (resp.associated_peo is not None): survey_type = 'PEO'
        if (resp.associated_slo is not None): survey_type = 'SLO'
        if (resp.associated_mlo is not None): survey_type = 'MLO'

        ret = {
        'survey_id' : survey_id,
        'type_of_survey' : survey_type,
        'title' : survey.survey_title,
        'file' : original_file_url,
        'start_date' : survey.opening_date,
        'end_date' : survey.closing_date,
        'recipients' : n_recipients,
        'comments' : survey.comments,
        'average_response_rate' : av_response_rate
        }
    return ret

    