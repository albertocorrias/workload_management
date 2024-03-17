import datetime
from .models import Survey,SurveyQuestionResponse, StudentLearningOutcome,MLOSLOMapping, MLOPerformanceMeasure, Module,ModuleLearningOutcome
from .helper_methods_survey import CalulatePositiveResponsesFractionForQuestion

#Calculate a table with surveys for a given SLO within a given period for HTML visualization.
#It returns a list of dictionaries, each intended as row in the table
#Each dictionary is a survey, with info for
# - dates of the survey (opening and closing)
# - question targeting teh SLO
# - % positive (if more than one question, the average score is taken)
# -  number of questions 
def CalculateTableForSLOSurveys(slo_id, start_year,end_year):
    slo=StudentLearningOutcome.objects.filter(id = slo_id).get()
    slo_survey_measures = [] #A list of all the slo survey measures. This one is ready for HTML
    #First look among the surveys, to see if any SLO measure is found
    for survey in Survey.objects.filter(opening_date__gte=datetime.date(start_year, 1, 1)).filter(opening_date__lte=datetime.date(end_year, 12, 31)):
        single_slo_survey_measure = {
            'date' : survey.opening_date,
            'survey' : survey.survey_title,
            'question' : '',
            'percent_positive' : 0,
            'n_questions' : 0
        }
        n_questions = 0
        fraction_positive = 0
        questions = ''
        #Look, within this survey for all responses associated with this SLO. We will condense them in one line of the table
        for response in SurveyQuestionResponse.objects.filter(parent_survey__id = survey.id).filter(associated_slo__id = slo.id):
            fraction_positive += CalulatePositiveResponsesFractionForQuestion(response.id)
            questions += response.question_text + ', '
            n_questions+=1
        if (n_questions > 0):
            single_slo_survey_measure['question'] = questions[:-2]
            single_slo_survey_measure['percent_positive'] = 100*fraction_positive/n_questions
            single_slo_survey_measure['n_questions'] = n_questions
            slo_survey_measures.append(single_slo_survey_measure)
    return slo_survey_measures

#Calculate a table with MLO survey measures for the given SLO and 
#a given period between start_year and end_year
#It returns a list of items, one per row of the table. 
#The columns of the table are the years.
#Each row has the module code at first position and then the strengths of the
#the survey measures for each year. If more MLOs contribute to the SLo for that year,
#the weighted average is computed, with the mapping strength as weight.
#After all the module codes (one per table row, as mentioned above),
#the method appends a final row to be displayed which contains "Weighted average" at the start, 
#and then, for each year, the weighted average of all the MLO survey measures for that year, 
# with, again, the mapping strength as the weight
def CalculateTableForMLOSurveys(slo_id, start_year,end_year):
    slo=StudentLearningOutcome.objects.filter(id = slo_id).get()
    mlo_survey_measures = []
    for survey in Survey.objects.filter(opening_date__gte=datetime.date(start_year, 1, 1)).filter(opening_date__lte=datetime.date(end_year, 12, 31)):
        #Look, within this survey for all responses associated with relevant MLO. 
        #First determine the relevant MLOs by looking at the mapping
        for mlo_mapping in MLOSLOMapping.objects.filter(slo__id = slo.id):
            mod_code = mlo_mapping.mlo.module_code
            single_survey_mlo_measure = {
                'year' : survey.opening_date.year,
                'module_code' : mod_code,
                'percentage_positive' : 0,
                'strength' : mlo_mapping.strength,
                'n_questions' : 0
            }
            n_questions = 0
            positive_for_survey  = 0
            for response in SurveyQuestionResponse.objects.filter(parent_survey__id = survey.id).filter(associated_mlo = mlo_mapping.mlo):
                positive_for_survey += CalulatePositiveResponsesFractionForQuestion(response.id)
                n_questions +=1
            if (n_questions > 0):
                single_survey_mlo_measure['n_questions'] = n_questions
                single_survey_mlo_measure['percentage_positive'] = 100*positive_for_survey/n_questions
                mlo_survey_measures.append(single_survey_mlo_measure)
    
    #After we are done with all the surveys for this SLO, we assemble the table for the MLO survey mesures
    mlo_slo_survey_table_rows = []

    #Before starting, we allocate memory for the grand total (weigthed average) of the table. One number per year
    total_row_scores = []
    total_row_weights = []
    for year in range(start_year, end_year+1):
        total_row_scores.append(0)
        total_row_weights.append(0)
        
    #Determine the rows of the table, by extracting the unique module codes present
    mod_codes_present = []
    for meas in mlo_survey_measures:
        mod_codes_present.append(meas['module_code'])
    mod_codes_present = list(dict.fromkeys(mod_codes_present))#eliminate duplicates
    #For each row, calculates the score for each year
    for mod_code in mod_codes_present:
        single_table_row = []
        single_table_row.append(mod_code)
        year_index = 0
        for year in range(start_year, end_year+1):
            to_display_in_row = ''
            score = 0
            strengths = 0
            for meas in mlo_survey_measures:
                if (meas['year'] == year and meas['module_code'] == mod_code):
                    #Weigthed average of all the contributions of the various MLO of this module to this SLO
                    score += meas['percentage_positive']*meas['strength']
                    strengths += meas['strength']

            if (score > 0): to_display_in_row = score/strengths
            single_table_row.append(to_display_in_row)
            #Update the totals for the last row
            total_row_scores[year_index] += score
            total_row_weights[year_index] += strengths
            year_index +=1

        mlo_slo_survey_table_rows.append(single_table_row)
    #Calulate the totals and append "totals" row
    year_index = 0
    for year in range(start_year, end_year+1):
        if (total_row_weights[year_index] > 0):
            total_row_scores[year_index] = total_row_scores[year_index]/total_row_weights[year_index]
        year_index+=1
    total_row_scores.insert(0, 'Weighted average')#Insert the label at the start
    mlo_slo_survey_table_rows.append(total_row_scores)#Append to the overall table

    return mlo_slo_survey_table_rows

def CalculateTableForMLODirectMeasures(slo_id, start_year,end_year):
    slo=StudentLearningOutcome.objects.filter(id = slo_id).get()
    all_mlo_measures = []# A list of direct MLO measurements for the mlo mapped to this SLO

    #We look at all the mapped measures
    for mlo_mapping in MLOSLOMapping.objects.filter(slo = slo):
        mod_code = mlo_mapping.mlo.module_code
        for measure in (MLOPerformanceMeasure.objects.filter(associated_mlo = mlo_mapping.mlo)| \
                        MLOPerformanceMeasure.objects.filter(secondary_associated_mlo = mlo_mapping.mlo) | \
                        MLOPerformanceMeasure.objects.filter(tertiary_associated_mlo = mlo_mapping.mlo)):
            if (measure.academic_year.start_year >= start_year and measure.academic_year.start_year <= end_year ):
                single_mlo_direct_measure= {
                    'module_code' : mod_code,
                    'mapping_strength' : mlo_mapping.strength,
                    'year' : measure.academic_year.start_year,
                    'score' : measure.percentage_score
                }
                all_mlo_measures.append(single_mlo_direct_measure)
    #Now we have an array with all the measures, we start preparing the HTML table rows
    #First we get a list of all the module codes involved, and make it unique
    mod_codes_present_direct = []
    for meas in all_mlo_measures:
        mod_codes_present_direct.append(meas["module_code"])
    mod_codes_present_direct = list(dict.fromkeys(mod_codes_present_direct))#eliminate duplicates

    #Before starting, we allocate memory for the grand total (weigthed average) of the table. One number per year
    total_row_scores_direct = []
    total_row_weights_direct = []
    for year in range(start_year, end_year+1):
        total_row_scores_direct.append(0)
        total_row_weights_direct.append(0)

    mlo_direct_measures_table_rows = [] #This one will be arranged to be displayed in HTML

    #For each row, calculates the score for each year
    for mod_code in mod_codes_present_direct:
        single_table_row_direct = []
        single_table_row_direct.append(mod_code)
        year_index = 0
        for year in range(start_year, end_year+1):
            to_display_in_row = ''
            score = 0
            strengths = 0
            for meas in all_mlo_measures:
                if (meas['year'] == year and meas['module_code'] == mod_code):
                    #Weigthed average of all the contributions of the various MLO of this module to this SLO
                    score += meas['score']*meas['mapping_strength']
                    strengths += meas['mapping_strength']

            if (score > 0): to_display_in_row = score/strengths
            single_table_row_direct.append(to_display_in_row)
            #Update the totals for the last row
            total_row_scores_direct[year_index] += score
            total_row_weights_direct[year_index] += strengths
            year_index +=1
        mlo_direct_measures_table_rows.append(single_table_row_direct)
    #Calulate the totals (weighted average) for each year and append "totals" row
    year_index = 0
    for year in range(start_year, end_year+1):
        if (total_row_weights_direct[year_index] > 0):
            total_row_scores_direct[year_index] = total_row_scores_direct[year_index]/total_row_weights_direct[year_index]
        year_index+=1
    total_row_scores_direct.insert(0, 'Weighted average')#Insert the label at the start
    mlo_direct_measures_table_rows.append(total_row_scores_direct)#Append to the overall table
    return mlo_direct_measures_table_rows

#A helper method to figure out the full-moon/half-mmon/empty moon icons to show
def DetermineIconBasedOnStrength(strength):
    icon = 'circle.svg'
    if (strength == 1 or strength ==2) : icon = 'circle-half.svg'
    if (strength ==3) : icon = 'circle-fill.svg'

    return icon

#This function generates the big MLO-SLO table for HTML viewing.
#Referred to a programme from start_year to end_year
#Each row is a module code as long as it is offered in the given period.
#Each column is a SLO for the given programme
#It returns a list, where each item is inteded as a table row (a dictionary)
# - module code (unique)
# - SLO identifiers (the letters ssociated) - A list
# - The numerical mapping strengths - A list with same length as above
# - The icons to be visualized based on strengths - A list with same length as above
# - The number of MLO that each moduel contributes to that SLO
def CalculateTableForOverallSLOMapping(programme_id, start_year,end_year):
    all_module_codes = []
    for mod in (Module.objects.filter(primary_programme__id = programme_id) |\
                Module.objects.filter(secondary_programme__id = programme_id)):
                if (mod.scenario_ref.academic_year.start_year >= start_year and\
                    mod.scenario_ref.academic_year.start_year <= end_year):
                    all_module_codes.append(mod.module_code)
    all_module_codes = list(dict.fromkeys(all_module_codes))#eliminate duplicates
    #Prepare the HTMl table
    table_rows = []
    for mod_code in all_module_codes:
        table_row_item = {
            'module_code' : mod_code,
            'slo_identifiers' : [],
            'numerical_mappings' : [],#A list as long as the SLOs of the programme
            'icons' : [],#Same as above, but icons instead
            'n_mlo_mapped' : []#Same as above. For each SLO, how many MLO opf this mod were mapped?
        }
        for slo in StudentLearningOutcome.objects.filter(programme__id = programme_id).order_by('letter_associated'):
            overall_strength = 0
            n_mlo_mapped = 0
            for mlo in ModuleLearningOutcome.objects.filter(module_code = mod_code):
                for mapping in MLOSLOMapping.objects.filter(slo = slo).filter(mlo = mlo):
                    if (mapping.strength > overall_strength): #The table will show the highest of the mappings (e.g., one 3 and one 1, only full moon will be shown)
                        overall_strength = mapping.strength
                    n_mlo_mapped = n_mlo_mapped + 1
            table_row_item['slo_identifiers'].append(slo.letter_associated)
            table_row_item['numerical_mappings'].append(overall_strength)
            table_row_item['icons'].append(DetermineIconBasedOnStrength(overall_strength))
            table_row_item['n_mlo_mapped'].append(n_mlo_mapped)
        table_rows.append(table_row_item)
    return table_rows

#This function generates the MLO-SLO table for HTML viewing
#Referred to a single SLO from start_year to end_year
#Each row is a module code as long as it is offered in the given period.
#It returns a list, where each item is inteded as a table row (a dictionary)
# one column for each year
# - module code (unique)
# - Maximal numerical mapping strength of the MLO - A list with same length as above
# - The icons to be visualized based on strengths - A list with same length as above
# - The number of MLO that each moduel contributes to the SLO that year
def CalculateMLOSLOMappingTable(slo_id, start_year,end_year):
    slo=StudentLearningOutcome.objects.filter(id = slo_id).get()
    mlo_mappings_table_rows = []# A list of table rows with mappings
    all_mods_involved = []
    #We look at all the mapped measures
    for mlo_mapping in MLOSLOMapping.objects.filter(slo = slo).order_by('mlo__module_code'):
        all_mods_involved.append(mlo_mapping.mlo.module_code)
    all_mods_involved = list(dict.fromkeys(all_mods_involved))#eliminate duplicates

    for mod_code in all_mods_involved:
        table_row_item = {
                'module_code' : mod_code,
                'numerical_mappings' : [],#A list as long as the number of years under consideration
                'icons' : [],#Same as above, but icons instead
                'n_mlo_mapped' : [],#Same as above. For each SLO, how many MLO opf this mod were mapped for that year?
        }
        for year in range(start_year, end_year+1):
            numerical_mapping_for_year = 0
            total_mapping_for_year = 0
            n_mlo_mapped_for_year = 0
            #check if the module with this code was offered this year
            if (Module.objects.filter(module_code = mod_code).filter(scenario_ref__academic_year__start_year = year)):
                for mlo in ModuleLearningOutcome.objects.filter(module_code = mod_code):
                    for mapping in MLOSLOMapping.objects.filter(slo = slo).filter(mlo = mlo):
                        total_mapping_for_year += mapping.strength
                        if mapping.strength > numerical_mapping_for_year: #It will get the max mapping throughout... Limitation of linking MLO to mod code and not module...
                            numerical_mapping_for_year = mapping.strength
                        n_mlo_mapped_for_year += 1
            table_row_item['numerical_mappings'].append(numerical_mapping_for_year)
            table_row_item['icons'].append(DetermineIconBasedOnStrength(numerical_mapping_for_year))
            table_row_item['n_mlo_mapped'].append(n_mlo_mapped_for_year)
        
        mlo_mappings_table_rows.append(table_row_item)
    return mlo_mappings_table_rows
                

            
