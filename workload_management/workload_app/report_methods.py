import datetime
from .models import Lecturer, Module, TeachingAssignment, ModuleType, EmploymentTrack,ServiceRole, Department, WorkloadScenario,Faculty
from .helper_methods import CalculateAllWorkloadTables,getIdsOfValidTeachingAssignmentsTypeForYear
from .forms import SelectFacultyForReport

def GetLastNYears(num_years):
    this_year = datetime.datetime.now().year + 1        
    labels = []
    years = []
    for i in range(0,num_years):
        labels.append(str(this_year-num_years+i)+'/'+ str(this_year-num_years+i+1))
        years.append(this_year - num_years + i)
    ret = {"labels" : labels, "years" : years}
    return ret

#Helper method to calculate the report table
#It returns a list with as many rows as modules that "prof_name" 
# was assigned to in any of the last 5 years, plus two extra summary lists
# Each item in the list is a list with (except the two extra summary lists)
# Position 0: module code
# Position 1: module title
# Position 2: total assigned hours to prof_name in workloads in the year (this year -5)
# Position 3: total assigned hours to prof_name in workloads in the year (this year -4)
# Position 4: total assigned hours to prof_name in workloads in the year (this year -3)
# Position 5: total assigned hours to prof_name in workloads in the year (this year -4)
# Position 6: total assigned hours to prof_name in workloads in the year (this year -1)
#The two extra summary lists 
# First list: total hours for each of the last five years
# tFTE of the prof for each of the last five years
def CalculateProfessorIndividualWorkload(prof_name):    
    ret = []
    time_info = GetLastNYears(5)
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
    total_years[1] = ""
    tFTEs[0]  = "tFTE"
    tFTEs[1]  = ""
    for idx, year in enumerate(years):
        for row in ret:
            total_years[idx+2] = total_years[idx+2] + row[idx+2] #+2 for module code and title (see above)
        lecturer = Lecturer.objects.select_related("employment_track","service_role").filter(workload_scenario__academic_year__start_year = year).\
                                           filter(name = prof_name).filter(workload_scenario__status=WorkloadScenario.OFFICIAL)
        if (lecturer.count() >0):
            lect_obj = lecturer.first()
            empl_track_adj = lect_obj.employment_track.track_adjustment
            service_role_adj = lect_obj.service_role.role_adjustment
            tFTEs[idx+2] = lect_obj.fraction_appointment*empl_track_adj*service_role_adj
    
    ret.append(total_years)
    ret.append(tFTEs)
    
    return ret;    

def CalculateProfessorChartData(lec_name):
    time_info  = GetLastNYears(5)
    labels = time_info["labels"]
    years = time_info["years"]
    
    hours_expected = [0]*len(years)
    hours_delivered = [0]*len(years)
    
    all_assignments = TeachingAssignment.objects.select_related("workload_scenario","workload_scenario__academic_year").filter(assigned_lecturer__name = lec_name).filter(workload_scenario__status=WorkloadScenario.OFFICIAL)
    workload_ids = []
    for assign in all_assignments:
        for index, year in enumerate(years):
            if (assign.workload_scenario.academic_year.start_year == year):
                hours_delivered[index] = hours_delivered[index] + assign.number_of_hours
                wl_id = assign.workload_scenario.id
                if (wl_id not in workload_ids):
                    workload_ids.append(wl_id)

    for wl in workload_ids:
        wl_object = WorkloadScenario.objects.filter(id=wl).get()
        if (wl_object.expected_hrs_per_tfte>-1):#already calculated, if not, it is -1
            total_hrs_delivered = wl_object.total_hours_delivered
            total_fte = wl_object.total_tfte_overall
            expected_per_FTE = wl_object.expected_hrs_per_tfte
        else:#need to reecalculate
            all_valid_assignment_types = getIdsOfValidTeachingAssignmentsTypeForYear(wl_object.academic_year.start_year)#
            summary_data = CalculateAllWorkloadTables(wl,all_valid_assignment_types)['summary_data']
            total_hrs_delivered = summary_data["total_hours_for_workload"]
            total_fte = summary_data["total_department_tFTE"],
            expected_per_FTE = summary_data["expected_hours_per_tFTE"]

        prof = Lecturer.objects.filter(name = lec_name).filter(workload_scenario = wl).get()
        track_adj = prof.employment_track.track_adjustment
        empl_adj = prof.service_role.role_adjustment
        prof_fte =  prof.fraction_appointment*track_adj*empl_adj #for worload wl

        index = years.index(WorkloadScenario.objects.filter(id = wl).get().academic_year.start_year)

        hours_expected[index] = expected_per_FTE*prof_fte
    hrs_expected_upper_boundary = []
    hrs_expected_lower_boundary = []
    for i in range(0,len(hours_expected)):
        hrs_expected_upper_boundary.append(hours_expected[i] + 15)
        hrs_expected_lower_boundary.append(hours_expected[i] - 15)
    return {
        'labels_temp_individual' : labels,
        'hrs_temp_individual_expected'  : hours_expected,
        'hrs_temp_individual_delivered' : hours_delivered,
        'hrs_expected_upper_boundary' : hrs_expected_upper_boundary,
        'hrs_expected_lower_boundary':  hrs_expected_lower_boundary
    }


def CalculateFacultyReportTable(faculty, report_type):
    ret =[]
    time_info = GetLastNYears(5)
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
                workload_obj = workload_query.get()
                if (workload_obj.expected_hrs_per_tfte>-1):#already calculated, if not, it is -1
                    total_hrs_delivered = workload_obj.total_hours_delivered
                    total_fte = workload_obj.total_tfte_overall
                    expected_hrs = workload_obj.expected_hrs_per_tfte
                else:#need to reecalculate
                    summary_data = CalculateAllWorkloadTables(workload_obj.id)['summary_data']
                    total_hrs_delivered = summary_data["total_hours_for_workload"]
                    total_fte = summary_data["total_department_tFTE"],
                    expected_hrs = summary_data["expected_hours_per_tFTE"]

                if (report_type == SelectFacultyForReport.EXPECTATION_PER_tFTE):
                    relevant_data =expected_hrs
                if (report_type == SelectFacultyForReport.TOTAL_TFTE):
                    relevant_data = total_hrs_delivered
            table_row[idx+2] = relevant_data        

        ret.append(table_row)
    return ret
