import datetime
import copy
from .models import Survey,SurveyQuestionResponse, StudentLearningOutcome,MLOSLOMapping, \
                    MLOPerformanceMeasure, Module,ModuleLearningOutcome, ProgrammeEducationalObjective,\
                    TeachingAssignment
from .helper_methods_survey import CalulatePositiveResponsesFractionForQuestion
from .global_constants import accreditation_outcome_type


#Little short-hand method to figure out the string to display for 
#the validity period of an outcome
# outcome_id is the Id of the ourcome in the DB
# outcome_type is the type of outcome (accreditation_outcome_type enum class)
def DisplayOutcomeValidity(outcome_id, outcome_type):
    start = None
    end = None
    if (outcome_type == accreditation_outcome_type.SLO):
        slo = StudentLearningOutcome.objects.filter(id = outcome_id)
        if slo.count()==1:#it should really be one, if, not, do nothing instead of trhowing errors
            slo_obj = slo.get()
            if (slo_obj.cohort_valid_from is not None):
                start = slo_obj.cohort_valid_from.__str__()
            if (slo_obj.cohort_valid_to is not None):
                end = slo_obj.cohort_valid_to.__str__()
    if (outcome_type == accreditation_outcome_type.PEO):
        peo = ProgrammeEducationalObjective.objects.filter(id = outcome_id)
        if peo.count()==1:#it should really be one, if, not, do nothing instead of trhowing errors
            peo_obj = peo.get()
            if (peo_obj.peo_cohort_valid_from is not None):
                start = peo_obj.peo_cohort_valid_from.__str__()
            if (peo_obj.peo_cohort_valid_to is not None):
                end = peo_obj.peo_cohort_valid_to.__str__()
    if (outcome_type == accreditation_outcome_type.MLO):
        mlo = ModuleLearningOutcome.objects.filter(id = outcome_id)
        if mlo.count()==1:#it should really be one, if, not, do nothing instead of trhowing errors
            mlo_obj = mlo.get()
            if (mlo_obj.mlo_valid_from is not None):
                start = mlo_obj.mlo_valid_from.__str__()
            if (mlo_obj.mlo_valid_to is not None):
                end = mlo_obj.mlo_valid_to.__str__()
    ret = ""
    if (start == None) and (end ==None):
        ret =  "Always"
    if (start == None) and (end is not None):
        ret = "Valid until " + end
    if (start is not None) and (end is None):
        ret =  "Valid since " + start
    if (start is not None) and (end is not None):
        ret = "Valid from " + start + " until " + end
    return ret

#Little convenience method to figure out whether an outcome is valid for that year.
#Works for MLO, PEO and SLO
# outcome_id is the Id of the ourcome in the DB
# outcome_type is the type of outcome (accreditation_outcome_type enum class)
# year is a number of the start year of the academic year under consideration
def IsOutcomeValidForYear(outcome_id,outcome_type,year):
    if (outcome_type == accreditation_outcome_type.SLO):
        slo = StudentLearningOutcome.objects.filter(id = outcome_id).get()
        if (slo.cohort_valid_from is None):
            if (slo.cohort_valid_to is None):
                return True
            if (slo.cohort_valid_to.start_year >= year):
                return True
            return False
        if (slo.cohort_valid_to is None):#Note None-None case is above...no need here
            if (slo.cohort_valid_from.start_year <= year):
                return True
            return False
        if (slo.cohort_valid_from.start_year <= year and slo.cohort_valid_to.start_year >= year):
            return True
    if (outcome_type == accreditation_outcome_type.PEO):
        peo = ProgrammeEducationalObjective.objects.filter(id = outcome_id).get()
        if (peo.peo_cohort_valid_from is None):
            if (peo.peo_cohort_valid_to is None):
                return True
            if (peo.peo_cohort_valid_to.start_year >= year):
                return True
            return False
        if (peo.peo_cohort_valid_to is None):#Note None-None case is above...no need here
            if (peo.peo_cohort_valid_from.start_year <= year):
                return True
            return False
        if (peo.peo_cohort_valid_from.start_year <= year and peo.peo_cohort_valid_to.start_year >= year):
            return True
    if (outcome_type == accreditation_outcome_type.MLO):
        mlo = ModuleLearningOutcome.objects.filter(id = outcome_id).get()
        if (mlo.mlo_valid_from is None):
            if (mlo.mlo_valid_to is None):
                return True
            if (mlo.mlo_valid_to.start_year >= year):
                return True
            return False
        if (mlo.mlo_valid_to is None):#Note None-None case is above...no need here
            if (mlo.mlo_valid_from.start_year <= year):
                return True
            return False
        if (mlo.mlo_valid_from.start_year <= year and mlo.mlo_valid_to.start_year >= year):
            return True
    return False

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
        for measure in (MLOPerformanceMeasure.objects.filter(associated_mlo = mlo_mapping.mlo) or \
                        MLOPerformanceMeasure.objects.filter(secondary_associated_mlo = mlo_mapping.mlo) or \
                        MLOPerformanceMeasure.objects.filter(tertiary_associated_mlo = mlo_mapping.mlo)):
            year_of_measurement = measure.academic_year.start_year
            module_obj_qs = Module.objects.filter(module_code = mod_code).filter(scenario_ref__academic_year__start_year = year_of_measurement)
            if (module_obj_qs.count()==1):#Nothing if it wasn't offered...
                year_of_study = module_obj_qs.get().students_year_of_study
                target_cohort = year_of_measurement - year_of_study + 1#Figure out targeted cohort
                if (target_cohort >= start_year and target_cohort<= end_year ):
                    #Before adding, check validity of the MLO involved
                    if (IsOutcomeValidForYear(mlo_mapping.mlo.id,accreditation_outcome_type.MLO,target_cohort)):
                        single_mlo_direct_measure= {
                            'module_code' : mod_code,
                            'mapping_strength' : mlo_mapping.strength,
                            'year' : target_cohort,
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

#This function calculates all the info about one particular SLO. It calls the 4 methods above and computes
#summary data as well
def CalculateAllInforAboutOneSLO(slo_id, start_year,end_year):
    ret = {}
    ret["mlo_mapping_for_slo"] = CalculateMLOSLOMappingTable(slo_id, start_year,end_year)
    ret["mlo_direct_measures_for_slo"] =CalculateTableForMLODirectMeasures(slo_id, start_year,end_year)
    ret["mlo_surveys_for_slo"] = CalculateTableForMLOSurveys(slo_id, start_year,end_year)
    ret["slo_surveys"] = CalculateTableForSLOSurveys(slo_id, start_year,end_year)
    
    #Calculate data for plot
    years =[]
    slo_survey_plot = []
    for year in range(start_year,end_year+1):
        years.append(year)
        slo_survey_plot.append(0)
    mlo_direct_plot = copy.deepcopy(ret["mlo_direct_measures_for_slo"][-1])
    mlo_survey_plot = copy.deepcopy(ret["mlo_surveys_for_slo"][-1])

    del mlo_direct_plot[0] #remove firts element, it is a lebl "weighted average"
    del mlo_survey_plot[0] #remove firts element, it is a lebl "weighted average"

    all_slo_surveys = copy.deepcopy(ret["slo_surveys"])
    for srv in all_slo_surveys:
        for i in range (0,len(years)):
            n_for_year = 0
            if (srv["date"].year == years[i]):
                slo_survey_plot[i] += srv["percent_positive"]
                n_for_year +=1
            #calculate average for year
            if (n_for_year > 0):
                slo_survey_plot[i] = slo_survey_plot[i]/n_for_year
                

    #indices: 0: years, 1:direct measures, 2: mlo survey measures, 3 slo survey measures
    ret["slo_measures_plot_data"] = []
    ret["slo_measures_plot_data"].append(years)
    ret["slo_measures_plot_data"].append(mlo_direct_plot)
    ret["slo_measures_plot_data"].append(mlo_survey_plot)
    ret["slo_measures_plot_data"].append(slo_survey_plot)

    return ret

#This function generates the big MLO-SLO table for HTML viewing.
#Referred to a programme from start_year to end_year
#Each row is a module code as long as 
#     1) it is offered in the given period,
# and 2) it has at least one MLO mapped to one SLO
#Each column is a SLO for the given programme
#It returns a list, where each item is inteded as a table row (a dictionary)
# - module code (unique)
# - SLO identifiers (the letters associated) - A list
# - The numerical mapping strengths - A list with same length as above. This will contain the highest mapping for the period
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
            'summation_strengths' : [],#A list of the sum of alls trengths of all MLO mapped to each SLO
            'icons' : [],#Same as above, but icons instead
            'n_mlo_mapped' : []#Same as above. For each SLO, how many MLO of this mod were mapped?
        }
        worth_appending = False #this will be switched to true as long as at least one mapping is found to ANY SLO
        for slo in StudentLearningOutcome.objects.filter(programme__id = programme_id).order_by('letter_associated'):
            overall_strength = 0 #Thisw ill store the maximal strength (used for half-moon/full-moon)
            summation_strength = 0 #Thisw ill store the total strength, adding up all the strengths of all MLOs
            n_mlo_mapped = 0
            for mlo in ModuleLearningOutcome.objects.filter(module_code = mod_code):
                for mapping in MLOSLOMapping.objects.filter(slo = slo).filter(mlo = mlo):
                    if (mapping.strength > overall_strength): #The table will show the highest of the mappings (e.g., one 3 and one 1, only full moon will be shown)
                        overall_strength = mapping.strength
                    summation_strength = summation_strength + mapping.strength #add anyway for the grand total
                    n_mlo_mapped = n_mlo_mapped + 1
            table_row_item['slo_identifiers'].append(slo.letter_associated)
            table_row_item['numerical_mappings'].append(overall_strength)
            table_row_item['summation_strengths'].append(summation_strength)
            table_row_item['icons'].append(DetermineIconBasedOnStrength(overall_strength))
            table_row_item['n_mlo_mapped'].append(n_mlo_mapped)
            if (overall_strength > 0): #if there is any mapping, switch it true, this will be displayed
                worth_appending = True
        
        if (worth_appending):        
            table_rows.append(table_row_item)
    #Done with the modules. Now compute the totals
    slo_index = 0
    totals_strengths_row = []
    totals_n_mods_row = []
    for slo in StudentLearningOutcome.objects.filter(programme__id = programme_id).order_by('letter_associated'):
        total_mapping_strength = 0
        total_n_mlo_mapped = 0
        for row in table_rows:
            total_n_mlo_mapped = total_n_mlo_mapped + row['n_mlo_mapped'][slo_index]
            total_mapping_strength = total_mapping_strength + row['summation_strengths'][slo_index]
        slo_index = slo_index +1
        totals_strengths_row.append(total_mapping_strength)
        totals_n_mods_row.append(total_n_mlo_mapped)

    ret = {
        'main_body_table' : table_rows,
        'totals_strengths_row' : totals_strengths_row,
        'totals_n_mlo_row' :totals_n_mods_row
    }
    return ret            

def CalculateAttentionScoresSummaryTable(programme_id, start_year,end_year):
    table_rows = []
    for slo in StudentLearningOutcome.objects.filter(programme__id = programme_id).order_by('letter_associated'):
        table_row = {
            'letter' : slo.letter_associated,
            'description' : slo.slo_short_description,
            'attention_scores_direct' : [],
            'attention_scores_mlo_surveys' : [],
            'attention_scores_slo_surveys' : []
        }
        for matric_year in range(start_year,end_year+1):
            if (IsOutcomeValidForYear(slo.id,accreditation_outcome_type.SLO,matric_year)):
                mlo_direct_attention_score = 0
                mlo_survey_attention_score = 0
                slo_survey_attention_score = 0
                for mapping in MLOSLOMapping.objects.filter(slo__id = slo.id):
                    mlo = mapping.mlo
                    if (IsOutcomeValidForYear(mlo.id,accreditation_outcome_type.MLO,matric_year)):
                        for measure in MLOPerformanceMeasure.objects.filter(associated_mlo__id = mlo.id):
                            mod_code = measure.associated_mlo.module_code
                            
                            for module in  Module.objects.filter(module_code=mod_code).filter(compulsory_in_primary_programme=True):#Only compulsory courses
                                year_delivered = module.scenario_ref.academic_year.start_year
                                student_year_of_study = module.students_year_of_study
                                if (year_delivered - student_year_of_study == matric_year) and\
                                    TeachingAssignment.objects.filter(assigned_module__id=module.id).count()>0 : #make sure it was offered...
                                    mlo_direct_attention_score += mapping.strength/3 #3 is the highest possible
                        for srv_resp in SurveyQuestionResponse.objects.filter(associated_mlo__id = mlo.id):
                            mod_code = mlo.module_code
                            for module in  Module.objects.filter(module_code=mod_code).filter(compulsory_in_primary_programme=True):#Only compulsory courses
                                year_delivered = module.scenario_ref.academic_year.start_year
                                student_year_of_study = module.students_year_of_study
                                if (year_delivered - student_year_of_study == matric_year) and\
                                    TeachingAssignment.objects.filter(assigned_module__id=module.id).count()>0 : #make sure it was offered...
                                    mlo_survey_attention_score += mapping.strength/3 #3 is the highest possible
                for slo_srv_resp in SurveyQuestionResponse.objects.filter(associated_slo__id = slo.id).filter(parent_survey__cohort_targeted__start_year = matric_year):
                    slo_survey_attention_score +=1

                table_row['attention_scores_direct'].append(mlo_direct_attention_score)
                table_row['attention_scores_mlo_surveys'].append(mlo_survey_attention_score)
                table_row['attention_scores_slo_surveys'].append(slo_survey_attention_score)
            else:#SLO not valid for that year
                table_row['attention_scores_direct'].append("N/A")
                table_row['attention_scores_mlo_surveys'].append("N/A")
                table_row['attention_scores_slo_surveys'].append("N/A")

        table_rows.append(table_row)

    return table_rows
                    
