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

#Given a number of options "num_options", this method
#will return a list of labels considered "default" labels
def DetermineDefaultLabels(num_options):
    if (num_options == 2):
        return ["Yes", "No"]
    if (num_options == 3):
        return ["Agree", "Neutral", "Disagree"]
    if (num_options == 4):
        return ["Stronly agree", "Agree", "Disagree", "Strongly disagree"]
    if (num_options ==5):
        return ["Stronly agree", "Agree", "Neutral", "Disagree", "Strongly disagree"]
    if (num_options ==6):
        return ["Stronly agree", "Agree", "Somewhat agree", "Somewhat disagree", "Disagree", "Strongly disagree"]
    if (num_options ==7):
        return ["Stronly agree", "Agree", "Somewhat agree", "Neither agree nor disagree", "Somewhat disagree", "Disagree", "Strongly disagree"]
    if (num_options >7):
        ret = []
        for i in range(0,num_options):
            ret.append(str(i))
        return ret
    return []#Should really never be here

