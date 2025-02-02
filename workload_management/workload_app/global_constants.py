
import csv
from enum import Enum

DEFAULT_WORKLOAD_NAME = 'Workload 1'

DEFAULT_MODULE_TYPE_NAME = 'Not assigned'

MAX_NUMBER_OF_CHARACTERS_IN_TABLE_CELL = 20

#The numbe rof weeks in one semester
NUMBER_OF_WEEKS_PER_SEM = 13

#Coefficient for repeated tutorials
REPEATED_TUTORIAL_MULTIPLIER = 1.0

DEFAULT_DEPARTMENT_NAME = 'No Department'

DEFAULT_DEPT_ACRONYM = 'NDPT'

DEFAULT_FACULTY_NAME = 'No faculty/school'

DEFAULT_FACULTY_ACRONYM = 'NFAC'

DEFAULT_TRACK_NAME = 'No track'

DEFAULT_SERVICE_ROLE_NAME = 'No special service role'

DEFAULT_PROGRAMME_OFFERED_NAME = 'Undegraduate'

class csv_file_type(Enum):
    PROFESSOR_FILE = 1
    MODULE_FILE = 2

#This class is used when clauclating tables to be displayed in the dpeartment page.
class requested_table_type(Enum):
    PROGRAMME = 1
    SUB_PROGRAMME = 2

#This is the colour scheme for the department porgramme tables.
colour_scheme_1 = {#green
    "darkest" : "#024606",
    "medium" : "#036108",
    "lightest" : "#06810C"
}
colour_scheme_2 = {#red
    "darkest" : "#520319",
    "medium" : "#800628",
    "lightest" : "#B20938"
}

colour_scheme_3 = {#blue
    "darkest" : "#07026F",
    "medium" : "#0B058A",
    "lightest" : "#1008B7"
}
COLOUR_SCHEMES = [colour_scheme_1,colour_scheme_2, colour_scheme_3]

#This enum class is used to for methods that calculate things for all types of outcomes.
class accreditation_outcome_type(Enum):
    SLO = 1
    PEO = 2
    MLO = 3

def CalculateNumHoursBasedOnWeeklyInfo(weekly_lect_hrs, weekly_tut_hrs, weeks_assigned, num_tut_grps):

    if (weekly_lect_hrs <= 0) and (weekly_tut_hrs <= 0):
        return 0
    if weeks_assigned<=0:
        return 0;

    return int(weekly_lect_hrs*weeks_assigned + weekly_tut_hrs*weeks_assigned + (num_tut_grps - 1)*(weeks_assigned*weekly_tut_hrs)*REPEATED_TUTORIAL_MULTIPLIER)

#This is a quick method to retrun a string with a HEX color code for the
# color of the "balance" column in the HTML table.
#If more color-grading is needed, simply modify this method.
def DetermineColorBasedOnBalance(bal):
    ok_threshold = 15;#within +/-15 hours it is OK
    if (bal > -ok_threshold and bal < ok_threshold):
        return '#FFFFFF' #White as OK
    if (bal > ok_threshold):
        return '#B5F5DC'
    if (bal < -ok_threshold):
        return '#FCCACA'
    
#This method returns and HTML-ready rgb string to be used as background colour
#In RGBA format. Depending on the score that is passed in
def DetermineColourBasedOnAttentionScore(score):
    green =     "rgba(144, 238, 82, 0.5)"
    neutral  = "rgba(255,255,255,0)"
    yellow = "rgba(223, 181, 41, 0.5)"
    red = "rgba(255, 99, 71, 0.6)"
    if score < 1:
        return red
    if score >=1 and score < 2:
        return yellow
    if score >=2:
        return green
    return neutral

#A helper method to shorten a long string.
#This prevents long module names to ruin table appearance
#If the string is longer than MAX_NUMBER_OF_CHARACTERS_IN_TABLE_CELL
#It returns a string with 
# - The first n characters as the original string, where n = MAX_NUMBER_OF_CHARACTERS_IN_TABLE_CELL - 3 - 4 (see below)
# - three dots
# - the last 4 characters as the original last 4 characters.
#If thes tring is shorter than MAX_NUMBER_OF_CHARACTERS_IN_TABLE_CELL
# then it just returns the string unmodified
def ShortenString(string,max_number = MAX_NUMBER_OF_CHARACTERS_IN_TABLE_CELL):
    if (len(string)<=max_number):
        return string
    else:
        ret = '';
        for i in range (0,max_number - 4 - 3):
                ret += string[i]

        ret+='...'
        ret+=string[-4]
        ret+=string[-3]
        ret+=string[-2]
        ret+=string[-1]
                
        return ret
    
    