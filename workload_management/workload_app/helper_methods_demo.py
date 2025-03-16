import csv
import random
from curses.ascii import isspace
from .models import Lecturer, Module, TeachingAssignment, ModuleType, EmploymentTrack,ServiceRole, Department, \
                   WorkloadScenario,Faculty,ProgrammeOffered,SubProgrammeOffered,Academicyear
from .forms import ProfessorForm, ModuleForm,EditTeachingAssignmentForm,EditModuleAssignmentForm,AddTeachingAssignmentForm,\
                    EmplymentTrackForm, ServiceRoleForm,DepartmentForm, FacultyForm
from .global_constants import DetermineColorBasedOnBalance, ShortenString, \
                              csv_file_type, requested_table_type, DEFAULT_TRACK_NAME, \
                                DEFAULT_SERVICE_ROLE_NAME,NUMBER_OF_WEEKS_PER_SEM, DEFAULT_MODULE_TYPE_NAME


#This helper method helps creating a databse for the demo
def populate_database():    
    f = open("workload_app/others/random_names.txt", "r")
    names = []
    for x in f:
        names.append(x)
    start_year = 2020

    acad_year,created = Academicyear.objects.get_or_create(start_year=start_year)
    
    #Faculty and Departments
    cde_fac, created = Faculty.objects.get_or_create(faculty_name="College of Design and Engineering", faculty_acronym="CDE")
    me_dept, created = Department.objects.get_or_create(department_name="Mechanical Engineering", department_acronym="ME", faculty = cde_fac)
    ece_dept, created = Department.objects.get_or_create(department_name="Electrical and Computer Engineering", department_acronym="ECE", faculty = cde_fac)
    bme_dept, created = Department.objects.get_or_create(department_name="Biomedical Engineering", department_acronym="BME", faculty = cde_fac)
    chem_dept, created = Department.objects.get_or_create(department_name="Chemical Engineering", department_acronym="CHEM", faculty = cde_fac)

    #Module types
    fluids, created = ModuleType.objects.get_or_create(type_name="Fluids",department=me_dept)
    solids, created = ModuleType.objects.get_or_create(type_name="Solids",department=me_dept)
    thermo, created = ModuleType.objects.get_or_create(type_name="Thermo",department=me_dept)
    robotics,created = ModuleType.objects.get_or_create(type_name="Robotics",department=me_dept)
    all_me_types = [fluids,solids,thermo,robotics]
    #ECE types
    power,created = ModuleType.objects.get_or_create(type_name="Power",department=ece_dept)
    circuits,created = ModuleType.objects.get_or_create(type_name="Circuits",department=ece_dept)
    chp_design,created = ModuleType.objects.get_or_create(type_name="Chip design",department=ece_dept)
    all_ece_types = [power,circuits,chp_design]
    #BME types
    biologics,created = ModuleType.objects.get_or_create(type_name="Cell biology",department=bme_dept)
    biomechanics,created = ModuleType.objects.get_or_create(type_name="Biomecahnics",department=bme_dept)
    medical_devices,created = ModuleType.objects.get_or_create(type_name="Medical Devices",department=bme_dept)
    diagnostics,created = ModuleType.objects.get_or_create(type_name="Diagnostics",department=bme_dept)
    all_bme_types = [biologics,biomechanics,medical_devices,diagnostics]
    #CHEM types
    oil,created = ModuleType.objects.get_or_create(type_name="Petroleum",department=chem_dept)
    biopharma,created = ModuleType.objects.get_or_create(type_name="Biopharma",department=chem_dept)
    energy_systems,created = ModuleType.objects.get_or_create(type_name="Energy systems",department=chem_dept)
    all_chem_types = [oil,biopharma,energy_systems]

    #Service role
    normal, created = ServiceRole.objects.get_or_create(role_name=DEFAULT_SERVICE_ROLE_NAME,role_adjustment=1,faculty=cde_fac)
    hod, created  = ServiceRole.objects.get_or_create(role_name = "Head of Department", role_adjustment = 0, faculty=cde_fac)
    dy, created  = ServiceRole.objects.get_or_create(role_name = "Deputy Head of Department", role_adjustment = 0.5, faculty=cde_fac)
    asst_dean, created  = ServiceRole.objects.get_or_create(role_name = "Assistant Dean", role_adjustment = 0.4, faculty=cde_fac)
    vice_dean, created  = ServiceRole.objects.get_or_create(role_name = "Vice Dean", role_adjustment = 0.2, faculty=cde_fac)
    #employment tracks
    tenure, created = EmploymentTrack.objects.get_or_create(track_name="Tenure track", track_adjustment = 1.0,is_adjunct=False,faculty=cde_fac)
    educator, created = EmploymentTrack.objects.get_or_create(track_name="Educator track", track_adjustment = 2.0,is_adjunct=False,faculty=cde_fac)
    adjunct, created = EmploymentTrack.objects.get_or_create(track_name="Adjunct professor", track_adjustment = 0.1,is_adjunct=True,faculty=cde_fac)

    #Programme offered
    me_beng, created = ProgrammeOffered.objects.get_or_create(programme_name = 'B. Eng (ME)', primary_dept = me_dept)
    rmi_beng, created = ProgrammeOffered.objects.get_or_create(programme_name = 'B. Eng (RMI)', primary_dept = me_dept)
    me_msc, created = ProgrammeOffered.objects.get_or_create(programme_name = 'M. Sc (ME)', primary_dept = me_dept)
    me_robotics, created = ProgrammeOffered.objects.get_or_create(programme_name = 'M. Sc (Robotics)', primary_dept = me_dept)

    ee_beng, created = ProgrammeOffered.objects.get_or_create(programme_name = 'B. Eng (EE)', primary_dept = ece_dept)
    ceg_beng, created = ProgrammeOffered.objects.get_or_create(programme_name = 'B. Eng (Computer Eng)', primary_dept = ece_dept)
    msc_ee, created = ProgrammeOffered.objects.get_or_create(programme_name = 'M. Sc (EE)', primary_dept = ece_dept)
    msc_ceg, created = ProgrammeOffered.objects.get_or_create(programme_name = 'M. Sc (CEG)', primary_dept = ece_dept)

    bme_beng, created = ProgrammeOffered.objects.get_or_create(programme_name = 'B. Eng (EE)', primary_dept = bme_dept)
    msc_bme, created = ProgrammeOffered.objects.get_or_create(programme_name = 'M. Sc (BME)', primary_dept = bme_dept)

    chem_beng, created = ProgrammeOffered.objects.get_or_create(programme_name = 'B. Eng (CHEM)', primary_dept = chem_dept)
    chem_mse, created = ProgrammeOffered.objects.get_or_create(programme_name = 'M. Sc (CHEM)', primary_dept = chem_dept)

    num_lecturers_me = 40
    num_lecturers_ece = 43
    num_lecturers_bme = 20
    num_lecturers_chem = 25

    me_wl_scen = WorkloadScenario.objects.create(label="ME workload " + str(start_year)+"/"+str(start_year+1),
                                              dept = me_dept, academic_year = acad_year,status = WorkloadScenario.OFFICIAL)

    ece_wl_scen = WorkloadScenario.objects.create(label="ECE workload " + str(start_year)+"/"+str(start_year+1),
                                              dept = ece_dept, academic_year = acad_year,status = WorkloadScenario.OFFICIAL)
    
    bme_wl_scen = WorkloadScenario.objects.create(label="BME workload " + str(start_year)+"/"+str(start_year+1),
                                              dept = bme_dept, academic_year = acad_year,status = WorkloadScenario.OFFICIAL)
    
    chem_wl_scen = WorkloadScenario.objects.create(label="CHEM workload " + str(start_year)+"/"+str(start_year+1),
                                              dept = chem_dept, academic_year = acad_year,status = WorkloadScenario.OFFICIAL)           
    frac_appontments = [1.0,1.0,1.0,0.5,0.6,0.7]
    empl_tracks = [tenure,tenure,tenure,educator,educator,adjunct]
    for i in range(0,num_lecturers_me):
        lec = Lecturer.objects.create(name = names[i],workload_scenario = me_wl_scen,\
                                    fraction_appointment = random.choice(frac_appontments),
                                    service_role = normal,
                                    employment_track = random.choice(empl_tracks),
                                    is_external = False)
        if (i==num_lecturers_me-1): 
            lec.service_role = hod
        if (i==num_lecturers_me-2): 
            lec.service_role = dy
        if (i==num_lecturers_me-3): 
            lec.service_role = asst_dean
        if (i==num_lecturers_me-4): 
            lec.service_role = vice_dean
        if (i==num_lecturers_me-5): 
            lec.is_external = True
        if (i==num_lecturers_me-6): 
            lec.is_external = True
        lec.save()
    for i in range(num_lecturers_me,num_lecturers_me+num_lecturers_ece):
        lec = Lecturer.objects.create(name = names[i],workload_scenario = ece_wl_scen,\
                                    fraction_appointment = random.choice(frac_appontments),
                                    service_role = normal,
                                    employment_track = random.choice(empl_tracks),
                                    is_external = False)
        if (i==num_lecturers_me+num_lecturers_ece-1): 
            lec.service_role = hod
        if (i==num_lecturers_me+num_lecturers_ece-2): 
            lec.service_role = dy
        if (i==num_lecturers_me+num_lecturers_ece-3): 
            lec.service_role = asst_dean
        if (i==num_lecturers_me+num_lecturers_ece-4): 
            lec.service_role = vice_dean
        if (i==num_lecturers_me+num_lecturers_ece-5): 
            lec.is_external = True
        if (i==num_lecturers_me+num_lecturers_ece-6): 
            lec.is_external = True
        lec.save()
    for i in range(num_lecturers_me+num_lecturers_ece,num_lecturers_me+num_lecturers_ece+num_lecturers_bme):
        lec = Lecturer.objects.create(name = names[i],workload_scenario = bme_wl_scen,\
                                    fraction_appointment = random.choice(frac_appontments),
                                    service_role = normal,
                                    employment_track = random.choice(empl_tracks),
                                    is_external = False)
        if (i==num_lecturers_me+num_lecturers_ece+num_lecturers_bme-1): 
            lec.service_role = hod
        if (i==num_lecturers_me+num_lecturers_ece+num_lecturers_bme-2): 
            lec.service_role = dy
        if (i==num_lecturers_me+num_lecturers_ece+num_lecturers_bme-3): 
            lec.service_role = asst_dean
        if (i==num_lecturers_me+num_lecturers_ece+num_lecturers_bme-4): 
            lec.service_role = vice_dean
        if (i==num_lecturers_me+num_lecturers_ece+num_lecturers_bme-5): 
            lec.is_external = True
        if (i==num_lecturers_me+num_lecturers_ece+num_lecturers_bme-6): 
            lec.is_external = True
        lec.save()
    for i in range(num_lecturers_me+num_lecturers_ece+num_lecturers_bme,num_lecturers_me+num_lecturers_ece+num_lecturers_bme+num_lecturers_chem):
        lec = Lecturer.objects.create(name = names[i],workload_scenario = chem_wl_scen,\
                                    fraction_appointment = random.choice(frac_appontments),
                                    service_role = normal,
                                    employment_track = random.choice(empl_tracks),
                                    is_external = False)
        if (i==num_lecturers_me+num_lecturers_ece+num_lecturers_bme+num_lecturers_chem-1): 
            lec.service_role = hod
        if (i==num_lecturers_me+num_lecturers_ece+num_lecturers_bme+num_lecturers_chem-2): 
            lec.service_role = dy
        if (i==num_lecturers_me+num_lecturers_ece+num_lecturers_bme+num_lecturers_chem-3): 
            lec.service_role = asst_dean
        if (i==num_lecturers_me+num_lecturers_ece+num_lecturers_bme+num_lecturers_chem-4): 
            lec.service_role = vice_dean
        if (i==num_lecturers_me+num_lecturers_ece+num_lecturers_bme+num_lecturers_chem-5): 
            lec.is_external = True
        if (i==num_lecturers_me+num_lecturers_ece+num_lecturers_bme+num_lecturers_chem-6): 
            lec.is_external = True
        lec.save()
    #######
    #Create ME modules
    #####
    all_semesters_offered = [Module.SEM_1, Module.SEM_2,Module.SEM_1,Module.SEM_2,Module.BOTH_SEMESTERS]
    mod,created = Module.objects.get_or_create(module_code = "ME1103", module_title="Principles of Mechanics and Materials", students_year_of_study=1,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 90,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    mod,created = Module.objects.get_or_create(module_code = "ME2105", module_title="Principles of Mechatronics and Automation", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    mod,created = Module.objects.get_or_create(module_code = "ME2102", module_title="Engineering Innovation and Modelling", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    mod,created = Module.objects.get_or_create(module_code = "ME2116", module_title="Mechanics of Materials", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    mod,created = Module.objects.get_or_create(module_code = "ME2121", module_title="Engineering Thermodynamics and Heat Transfer", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    return 0

