import datetime
from .models import Lecturer, Module, TeachingAssignment, ModuleType, EmploymentTrack,ServiceRole, Department, WorkloadScenario,Faculty
from .helper_methods import CalculateSummaryData
from .forms import SelectFacultyForReport

def GetLastFiveYears():
    this_year = datetime.datetime.now().year
    labels = [str(this_year-4),str(this_year-3), str(this_year-2), str(this_year-1), str(this_year)]
    years = [this_year-4,this_year-3, this_year-2, this_year-1, this_year]
    ret = {"labels" : labels, "years" : years}
    return ret

#Helper method to calculate the report table
#It returns a list with as many rows as modules that "prof_name" 
# was assigned to in any of the last 5 years, plus two extra summary lists
# Each item in the list is a list with (except the two extra summatry lists)
# Position 0: module code
# Position 1: module title
# Position 2: total assigned hours to prof_name in workloads in the year (this year -5)
# Position 3: total assigned hours to prof_name in workloads in the year (this year -4)
# Position 4: total assigned hours to prof_name in workloads in the year (this year -3)
# Position 5: total assigned hours to prof_name in workloads in the year (this year -4)
# Position 6: total assigned hours to prof_name in workloads in the year (this year -1)
#The two extra summatyt lists 
# First list: total hours for each of the last five years
# tFTE of teh prof for each of the last five years
def CalculateProfessorIndividualWorkload(prof_name):    
    ret = [];
    time_info = GetLastFiveYears()
    years = time_info["years"]
    all_mod_codes = []
    all_mod_titles = []
    #Figure out the modules involved
    for assign in TeachingAssignment.objects.filter(assigned_lecturer__name = prof_name).filter(workload_scenario__status=WorkloadScenario.OFFICIAL):
        mod_code = assign.assigned_module.module_code
        mod_title = assign.assigned_module.module_title
        if (mod_code not in all_mod_codes):
            all_mod_codes.append(mod_code)
            all_mod_titles.append(mod_title)

    #Loop over the modules involved 
    for index, md_code in enumerate(all_mod_codes):
        table_row = [None] * (len(years) + 2) #+2 for module code and title (below)
        table_row[0] =  md_code
        table_row[1] =  all_mod_titles[index]
        #Loop over years
        for idx, year in enumerate(years):
            assigns_of_mod_per_year = TeachingAssignment.objects.filter(assigned_lecturer__name = prof_name).\
                                                 filter(workload_scenario__academic_year__start_year = year).\
                                                 filter(assigned_module__module_code = md_code).filter(workload_scenario__status=WorkloadScenario.OFFICIAL)
            total_hours=0
            for assign in assigns_of_mod_per_year:
                total_hours = total_hours + assign.number_of_hours
            table_row[idx+2] = total_hours
        ret.append(table_row)

    #Calculate total for each year
    total_years = [0] * (len(years)+2)
    tFTEs = [0] * (len(years)+2)
    total_years[0] = "Total"
    total_years[1] = " "
    tFTEs[0]  = "tFTE"
    tFTEs[1]  = " "
    for idx, year in enumerate(years):
        for row in ret:
            total_years[idx+2] = total_years[idx+2] + row[idx+2] #+2 for module code and title (see above)
        lecturer = Lecturer.objects.filter(workload_scenario__academic_year__start_year = year).\
                                           filter(name = prof_name).filter(workload_scenario__status=WorkloadScenario.OFFICIAL)
        if (lecturer.count() >0):
            lect_obj = lecturer.first()
            empl_track_adj = lect_obj.employment_track.track_adjustment
            service_role_adj = lect_obj.service_role.role_adjustment
            tFTEs[idx+2] = lect_obj.fraction_appointment*empl_track_adj*service_role_adj
    
    ret.append(total_years)
    ret.append(tFTEs)
    
    return ret;    

def CalculateFacultyReportTable(faculty, report_type):
    ret =[]
    time_info = GetLastFiveYears()
    years = time_info["years"]
    for dept in Department.objects.filter(faculty__faculty_name = faculty):
        table_row = [None] * (len(years) + 2) #+2 for module code and title (below)
        table_row[0] =  dept.department_name
        table_row[1] =  dept.department_acronym
        #Loop over years
        for idx, year in enumerate(years):
            #Figure out workload for this year
            workload_query = WorkloadScenario.objects.filter(dept = dept).filter(academic_year__start_year = year).filter(status = WorkloadScenario.OFFICIAL)
            if (workload_query.count() < 1):
                relevant_data = 0
            else:
                workload_id = workload_query.get().id
                summary_data = CalculateSummaryData(workload_scenario_id = workload_id)
                if (report_type == SelectFacultyForReport.EXPECTATION_PER_tFTE):
                    relevant_data = summary_data["expected_hours_per_tFTE"]
                if (report_type == SelectFacultyForReport.TOTAL_TFTE):
                    relevant_data = summary_data["total_tFTE_for_workload"]
            table_row[idx+2] = relevant_data        

        ret.append(table_row)
    return ret
