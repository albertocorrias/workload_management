import csv
from curses.ascii import isspace
from .models import Lecturer, Module, TeachingAssignment, ModuleType, EmploymentTrack,ServiceRole, Department, \
                   WorkloadScenario,Faculty,ProgrammeOffered,SubProgrammeOffered,Academicyear
from .forms import ProfessorForm, ModuleForm,EditTeachingAssignmentForm,EditModuleAssignmentForm,AddTeachingAssignmentForm,\
                    EmplymentTrackForm, ServiceRoleForm,DepartmentForm, FacultyForm
from .global_constants import DetermineColorBasedOnBalance, ShortenString, \
                              csv_file_type, requested_table_type, DEFAULT_TRACK_NAME, \
                                DEFAULT_SERVICE_ROLE_NAME,NUMBER_OF_WEEKS_PER_SEM, DEFAULT_MODULE_TYPE_NAME


#This helper method helps creating a databse for the demo
def populate_database(num_lecturers):    
    f = open("workload_app/others/random_names.txt", "r")
    names = []
    for x in f:
        names.append(x)
    start_year = 2020
    if Academicyear.objects.filter(start_year = start_year).count() == 1:
        acad_year = Academicyear.objects.filter(start_year = start_year).get()
    else:
        acad_year = Academicyear.objects.create(start_year=start_year)

    if (Faculty.objects.filter(faculty_acronym="CDE").count()==1):
        fac = Faculty.objects.filter(faculty_acronym="CDE").get()
    else:
        fac = Faculty.objects.create(faculty_name="College of Design and Engineering", faculty_acronym="CDE")

    if (Department.objects.filter(department_name="Mechanical Engineering").count()==1):
        dept = Department.objects.filter(department_name="Mechanical Engineering").get()
    else:
        dept = Department.objects.create(department_name="Mechanical Engineering", department_acronym="ME", faculty = fac)

    normal, created = ServiceRole.objects.get_or_create(role_name=DEFAULT_SERVICE_ROLE_NAME,role_adjustment=1,faculty=fac)
    hod, created  = ServiceRole.objects.get_or_create(role_name = "Head of Department", role_adjustment = 0)
    dy, created  = ServiceRole.objects.get_or_create(role_name = "Deputy Head of Department", role_adjustment = 0.5)
    wl_scen = WorkloadScenario.objects.create(label="ME workload " + str(start_year)+"/"+str(start_year+1),
                                              dept = dept, academic_year = acad_year,status = WorkloadScenario.OFFICIAL)
    tenure, created = EmploymentTrack.objects.get_or_create(track_name=DEFAULT_TRACK_NAME, track_adjustment = 1.0,is_adjunct=False,faculty=fac)
    
    for i in range(0,num_lecturers):
        Lecturer.objects.create(name = names[i],workload_scenario = wl_scen,\
                                fraction_appointment = 1.0,
                                service_role = normal,
                                employment_track = tenure)
    
    
    return 0

