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
    common_me,created = ModuleType.objects.get_or_create(type_name="Common Curriculum",department=me_dept)
    all_me_types = [fluids,solids,thermo,robotics, common_me]
    #ECE types
    power,created = ModuleType.objects.get_or_create(type_name="Power",department=ece_dept)
    circuits,created = ModuleType.objects.get_or_create(type_name="Circuits",department=ece_dept)
    chp_design,created = ModuleType.objects.get_or_create(type_name="Chip design",department=ece_dept)
    common_ece,created = ModuleType.objects.get_or_create(type_name="Common Curriculum",department=ece_dept)
    all_ece_types = [power,circuits,chp_design, common_ece]
    #BME types
    biologics,created = ModuleType.objects.get_or_create(type_name="Cell biology",department=bme_dept)
    biomechanics,created = ModuleType.objects.get_or_create(type_name="Biomecahnics",department=bme_dept)
    medical_devices,created = ModuleType.objects.get_or_create(type_name="Medical Devices",department=bme_dept)
    diagnostics,created = ModuleType.objects.get_or_create(type_name="Diagnostics",department=bme_dept)
    common_bme,created = ModuleType.objects.get_or_create(type_name="Common Curriculum",department=bme_dept)
    all_bme_types = [biologics,biomechanics,medical_devices,diagnostics,common_bme]
    #CHEM types
    oil,created = ModuleType.objects.get_or_create(type_name="Petroleum",department=chem_dept)
    biopharma,created = ModuleType.objects.get_or_create(type_name="Biopharma",department=chem_dept)
    energy_systems,created = ModuleType.objects.get_or_create(type_name="Energy systems",department=chem_dept)
    common_chem,created = ModuleType.objects.get_or_create(type_name="Common Curriculum",department=chem_dept)
    all_chem_types = [oil,biopharma,energy_systems,common_chem]

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

    #Programmes and sub-programmes offered
    me_beng, created = ProgrammeOffered.objects.get_or_create(programme_name = 'B. Eng (ME)', primary_dept = me_dept)
    rmi_beng, created = ProgrammeOffered.objects.get_or_create(programme_name = 'B. Eng (RMI)', primary_dept = me_dept)
    me_msc, created = ProgrammeOffered.objects.get_or_create(programme_name = 'M. Sc (ME)', primary_dept = me_dept)
    me_robotics, created = ProgrammeOffered.objects.get_or_create(programme_name = 'M. Sc (Robotics)', primary_dept = me_dept)

    aero_spec, created = SubProgrammeOffered.objects.get_or_create(sub_programme_name="Aeronautical specialization", main_programme=me_beng)
    robo_spec, created = SubProgrammeOffered.objects.get_or_create(sub_programme_name="Robotics specialization", main_programme=me_beng)

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
    
    all_semesters_offered = [Module.SEM_1, Module.SEM_2,Module.SEM_1,Module.SEM_2,Module.BOTH_SEMESTERS]
    #######
    #Create ME modules
    #####
    mme1103,created = Module.objects.get_or_create(module_code = "ME1103", module_title="Principles of Mechanics and Materials", students_year_of_study=1,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 90,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me2105,created = Module.objects.get_or_create(module_code = "ME2105", module_title="Principles of Mechatronics and Automation", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me2102,created = Module.objects.get_or_create(module_code = "ME2102", module_title="Engineering Innovation and Modelling", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me2116,created = Module.objects.get_or_create(module_code = "ME2116", module_title="Mechanics of Materials", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me2121,created = Module.objects.get_or_create(module_code = "ME2121", module_title="Engineering Thermodynamics and Heat Transfer", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me2104,created = Module.objects.get_or_create(module_code = "ME2104", module_title="Fluid Mechanics I", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered),\
                                               sub_programme = aero_spec)
    me2162,created = Module.objects.get_or_create(module_code = "ME2162", module_title="Manufacturing Processes", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me3112,created = Module.objects.get_or_create(module_code = "ME3112", module_title="Mechanics of Machines", students_year_of_study=3,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me3123,created = Module.objects.get_or_create(module_code = "ME3123", module_title="Applied Thermofluids", students_year_of_study=3,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me3142,created = Module.objects.get_or_create(module_code = "ME3142", module_title="Feedback Control Systems", students_year_of_study=3,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    #Some electives
    me4212,created = Module.objects.get_or_create(module_code = "ME4212", module_title="Aircraft Structures", students_year_of_study=4,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered),\
                                                sub_programme = aero_spec)
    me4231,created = Module.objects.get_or_create(module_code = "ME4231", module_title="Aerodynamics", students_year_of_study=4,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered),\
                                                sub_programme = aero_spec)
    me4241,created = Module.objects.get_or_create(module_code = "ME4241", module_title="Aircraft Performance and Stability", students_year_of_study=4,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered),\
                                               sub_programme = aero_spec)
    me4242,created = Module.objects.get_or_create(module_code = "ME4242", module_title="Soft Robotics", students_year_of_study=4,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered),\
                                               sub_programme = robo_spec)
    me4262,created = Module.objects.get_or_create(module_code = "ME4262", module_title="Automation in Manufacturing", students_year_of_study=4,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered),\
                                               sub_programme = robo_spec)
    me4245,created = Module.objects.get_or_create(module_code = "ME4245", module_title="Robot Mechanics and Control", students_year_of_study=4,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered),\
                                               sub_programme = robo_spec)

    #RMI courses
    rb1101,created = Module.objects.get_or_create(module_code = "RB1101", module_title="Fundamentals of Robotics I", students_year_of_study=1,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 90,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    rb2101,created = Module.objects.get_or_create(module_code = "RB2101", module_title="Fundamentals of Robotics II", students_year_of_study=1,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 90,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    rb2202,created = Module.objects.get_or_create(module_code = "RB2202", module_title="Kinematics and Dynamics for Robotics", students_year_of_study=2,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))   
    rb2203,created = Module.objects.get_or_create(module_code = "RB2203", module_title="Robot Control", students_year_of_study=2,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))       
    rb2301,created = Module.objects.get_or_create(module_code = "RB2301", module_title="Robot Programming", students_year_of_study=2,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    rb2302,created = Module.objects.get_or_create(module_code = "RB2302", module_title="Fundamentals of Artificial Neural Networks", students_year_of_study=2,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    rb3301,created = Module.objects.get_or_create(module_code = "RB3301", module_title="Introduction to Machine Intelligence", students_year_of_study=3,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    rb3302,created = Module.objects.get_or_create(module_code = "RB3302", module_title="Planning and Navigation", students_year_of_study=3,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    rb3303,created = Module.objects.get_or_create(module_code = "RB3303", module_title="Robotic System Design and Applications", students_year_of_study=3,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    #some electives
    rb3201,created = Module.objects.get_or_create(module_code = "RB3201", module_title="Sensors and Actuators for Robots", students_year_of_study=3,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    rb4107,created = Module.objects.get_or_create(module_code = "RB4107", module_title="Robotics and Machine Intelligence Design Project", students_year_of_study=4,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    rb4203,created = Module.objects.get_or_create(module_code = "RB3201", module_title="Robot Learning", students_year_of_study=4,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    bn4203,created = Module.objects.get_or_create(module_code = "BN4203", module_title="Robotics in Rehabilitation", students_year_of_study=4,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))  

    #M.Sc ME courses
    me5303,created = Module.objects.get_or_create(module_code = "ME5303", module_title="Industrial Aerodynamics", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    me5304,created = Module.objects.get_or_create(module_code = "ME5304", module_title="Experimental Fluid Mechanics", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 

    me5413,created = Module.objects.get_or_create(module_code = "ME5413", module_title="Autonomous Mobile Robotics", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False, secondary_programme = me_robotics, compulsory_in_secondary_programme = False,\
                                                total_hours = 39, scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    me5401,created = Module.objects.get_or_create(module_code = "ME5304", module_title="Linear Systems", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    me5402,created = Module.objects.get_or_create(module_code = "ME5402", module_title="Advanced Robotics", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    me5404,created = Module.objects.get_or_create(module_code = "ME5404", module_title="Neural Networks", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me5418,created = Module.objects.get_or_create(module_code = "ME5418", module_title="Machine Learning in Robotics", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False, secondary_programme = me_robotics, compulsory_in_secondary_programme = False,\
                                                total_hours = 39, scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    me5103,created = Module.objects.get_or_create(module_code = "ME5103", module_title="Plates and Shells", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me5107,created = Module.objects.get_or_create(module_code = "ME5103", module_title="Vibration Theory and Applications", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me5106,created = Module.objects.get_or_create(module_code = "ME5106", module_title="Engineering Acoustics", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))

    #M.Sc robotics courses
    me5421,created = Module.objects.get_or_create(module_code = "ME5421", module_title="Robot Kinematics", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))   
    me5409,created = Module.objects.get_or_create(module_code = "ME5409", module_title="Robot Dynamics and Control ", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))  
    me5410,created = Module.objects.get_or_create(module_code = "ME5410", module_title="Materials, Sensors, Actuators and Fabrication in Robotics", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))  
    me5411,created = Module.objects.get_or_create(module_code = "ME5411", module_title="Robot Vision and AI", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))  
    me5401,created = Module.objects.get_or_create(module_code = "ME5401", module_title="Linear Systems", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me5412,created = Module.objects.get_or_create(module_code = "ME5412", module_title="Robotics for Healthcare", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me5414,created = Module.objects.get_or_create(module_code = "ME5414", module_title="Optimization Techniques for Dynamic Systems", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me5415,created = Module.objects.get_or_create(module_code = "ME5415", module_title="Advanced Soft Robotics", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 

    #Create common modules for ME
    es2631,created = Module.objects.get_or_create(module_code = "ES2631", module_title="Critical Thinking and Writing", students_year_of_study=2,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,\
                                               secondary_programme = me_beng, compulsory_in_secondary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = all_me_types[-1], semester_offered= random.choice(all_semesters_offered))
    cs1010e,created = Module.objects.get_or_create(module_code = "CS1010E", module_title="Programming Methodology", students_year_of_study=1,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,\
                                               secondary_programme = me_beng, compulsory_in_secondary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = all_me_types[-1], semester_offered= random.choice(all_semesters_offered))
    gea1000,created = Module.objects.get_or_create(module_code = "GEA1000", module_title="Quantitative Reasoning with Data", students_year_of_study=1,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,\
                                               secondary_programme = me_beng, compulsory_in_secondary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = all_me_types[-1], semester_offered= random.choice(all_semesters_offered))
    dtk1234,created = Module.objects.get_or_create(module_code = "DTK1234", module_title="Design Thinking", students_year_of_study=1,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,\
                                               secondary_programme = me_beng, compulsory_in_secondary_programme=True,total_hours = 39,\
                                               scenario_ref = me_wl_scen, module_type = all_me_types[-1], semester_offered= random.choice(all_semesters_offered))
    #################
    ##ECE modules
    #################

    #EE modules
    ee1111a,created = Module.objects.get_or_create(module_code = "EE1111A", module_title="Electrical Engineering Principles and Practice I", students_year_of_study=1,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=True,total_hours = 90,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    ee2111a,created = Module.objects.get_or_create(module_code = "EE2111A", module_title="Electrical Engineering Principles and Practice II", students_year_of_study=1,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=True,total_hours = 90,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    ee2012,created = Module.objects.get_or_create(module_code = "EE2012", module_title="Analytical Methods in Electrical and Computer Engineering", students_year_of_study=2,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=True, total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))   
    ee2022,created = Module.objects.get_or_create(module_code = "EE2022", module_title="Electrical Energy Systems", students_year_of_study=2,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))       
    ee2023,created = Module.objects.get_or_create(module_code = "EE2023", module_title="Signals and Systems", students_year_of_study=2,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    ee2026,created = Module.objects.get_or_create(module_code = "EE2026", module_title="Digital Design", students_year_of_study=2,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               secondary_programme  =ceg_beng, compulsory_in_secondary_programme = True,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 
    ee2028,created = Module.objects.get_or_create(module_code = "EE2028", module_title="Microcontroller Programming and Interfacing", students_year_of_study=2,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 
    ee2027,created = Module.objects.get_or_create(module_code = "EE2027", module_title="Electronic Circuits", students_year_of_study=2,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    ee3033,created = Module.objects.get_or_create(module_code = "EE3033", module_title="Systems Integration and Design Lab", students_year_of_study=3,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 

    #Some EE electives
    ee4407,created = Module.objects.get_or_create(module_code = "EE4407", module_title="Analog Electronics", students_year_of_study=4,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    ee4218,created = Module.objects.get_or_create(module_code = "EE4218", module_title="Embedded Hardware System Design", students_year_of_study=4,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               secondary_programme = ceg_beng, compulsory_in_secondary_programme=False,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    ee4415,created = Module.objects.get_or_create(module_code = "EE4415", module_title="Integrated Digital Design", students_year_of_study=4,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               secondary_programme = ceg_beng, compulsory_in_secondary_programme=False,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))   
    ee4501,created = Module.objects.get_or_create(module_code = "EE4501", module_title="Power System Management and Protection", students_year_of_study=4,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))  
    ee4502,created = Module.objects.get_or_create(module_code = "EE4502", module_title="Electric Drives and Control", students_year_of_study=4,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    ee4503,created = Module.objects.get_or_create(module_code = "EE4503", module_title="Power Electronics for Sustainable Energy Technologies", students_year_of_study=4,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))    
 
    #CEG core
    cg1111A,created = Module.objects.get_or_create(module_code = "CG1111A", module_title="Engineering Principles and Practice I", students_year_of_study=1,\
                                               primary_programme = ceg_beng,compulsory_in_primary_programme=True,total_hours = 90,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    cg2111A,created = Module.objects.get_or_create(module_code = "CG2111A", module_title="Engineering Principles and Practice II", students_year_of_study=1,\
                                               primary_programme = ceg_beng,compulsory_in_primary_programme=True,total_hours = 90,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    cs2131,created = Module.objects.get_or_create(module_code = "CS1231", module_title="Discrete Structures", students_year_of_study=2,\
                                               primary_programme = ceg_beng,compulsory_in_primary_programme=True, total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))   
    cg2023,created = Module.objects.get_or_create(module_code = "CG2023", module_title="Signals and  Systems", students_year_of_study=2,\
                                               primary_programme = ceg_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))       
    cg2027,created = Module.objects.get_or_create(module_code = "CG2027", module_title="Transistor-level Digital Circuit", students_year_of_study=2,\
                                               primary_programme = ceg_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    cg2028,created = Module.objects.get_or_create(module_code = "CG2028", module_title="Computer Organization", students_year_of_study=2,\
                                               primary_programme = ceg_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 
    cg2271,created = Module.objects.get_or_create(module_code = "CG2271", module_title="Real-time Operating System", students_year_of_study=2,\
                                               primary_programme = ceg_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 
    cg3201,created = Module.objects.get_or_create(module_code = "CG3201", module_title="Machine Learning and Deep Learning", students_year_of_study=3,\
                                               primary_programme = ceg_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    cg3207,created = Module.objects.get_or_create(module_code = "CG3207", module_title="Computer Architecture", students_year_of_study=3,\
                                               primary_programme = ceg_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    #Some CEG electives
    cs4222,created = Module.objects.get_or_create(module_code = "CS4222", module_title="Wireless Networking", students_year_of_study=4,\
                                               primary_programme = ceg_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    cs4223,created = Module.objects.get_or_create(module_code = "CS4223", module_title="Multi-Core Architectures", students_year_of_study=4,\
                                               primary_programme = ceg_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 
    cs3241,created = Module.objects.get_or_create(module_code = "CS3241", module_title="Computer Graphics", students_year_of_study=4,\
                                               primary_programme = ceg_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 
        
     #Create common modules for ECE
    es2631_ece,created = Module.objects.get_or_create(module_code = "ES2631", module_title="Critical Thinking and Writing", students_year_of_study=2,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=True,\
                                               secondary_programme = ceg_beng, compulsory_in_secondary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = all_ece_types[-1], semester_offered= random.choice(all_semesters_offered))
    eg_1311_ece,created = Module.objects.get_or_create(module_code = "EG13111", module_title="Design and make", students_year_of_study=1,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=True,\
                                               secondary_programme = ceg_beng, compulsory_in_secondary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = all_ece_types[-1], semester_offered= random.choice(all_semesters_offered))
    gea1000_ece,created = Module.objects.get_or_create(module_code = "GEA1000", module_title="Quantitative Reasoning with Data", students_year_of_study=1,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=True,\
                                               secondary_programme = ceg_beng, compulsory_in_secondary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = all_ece_types[-1], semester_offered= random.choice(all_semesters_offered))
    dtk1234_ece,created = Module.objects.get_or_create(module_code = "DTK1234", module_title="Design Thinking", students_year_of_study=1,\
                                               primary_programme = ee_beng,compulsory_in_primary_programme=True,\
                                               secondary_programme = ceg_beng, compulsory_in_secondary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = all_ece_types[-1], semester_offered= random.choice(all_semesters_offered))

    #Msc in CEG
    ceg5101,created = Module.objects.get_or_create(module_code = "CEG5101", module_title="Modern Computer Networking", students_year_of_study=1,\
                                               primary_programme = msc_ceg,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 

    ceg5201,created = Module.objects.get_or_create(module_code = "CEG5201", module_title="Hardware Technologies, Principles, and Platforms", students_year_of_study=1,\
                                               primary_programme = msc_ceg,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    ceg5301,created = Module.objects.get_or_create(module_code = "CEG5301", module_title="Machine Learning with Applications", students_year_of_study=1,\
                                               primary_programme = msc_ceg,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 
    ceg5102,created = Module.objects.get_or_create(module_code = "CEG5102", module_title="Wireless Communications for IoT", students_year_of_study=1,\
                                               primary_programme = msc_ceg,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    ceg5103,created = Module.objects.get_or_create(module_code = "CEG5103", module_title="Wireless and Sensor Networks for IoT", students_year_of_study=1,\
                                               primary_programme = msc_ceg,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 
    ceg5104,created = Module.objects.get_or_create(module_code = "CEG5104", module_title="Cellular Networks", students_year_of_study=1,\
                                               primary_programme = msc_ceg,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    ceg5104,created = Module.objects.get_or_create(module_code = "CEG5105", module_title="Cyber Security for Computer Systems", students_year_of_study=1,\
                                               primary_programme = msc_ceg,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))  
    ceg5302,created = Module.objects.get_or_create(module_code = "CEG5302", module_title="Evolutionary Computation and Applications", students_year_of_study=1,\
                                               primary_programme = msc_ceg,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))  
    ceg5303,created = Module.objects.get_or_create(module_code = "CEG5303", module_title="Intelligent Autonomous Robotic Systems", students_year_of_study=1,\
                                               primary_programme = msc_ceg,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))  
    ceg5304,created = Module.objects.get_or_create(module_code = "CEG5304", module_title="Deep Learning for Digitalization Technologies", students_year_of_study=1,\
                                               primary_programme = msc_ceg,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))  
    #Msc in EE
    ee5101,created = Module.objects.get_or_create(module_code = "EE5101", module_title="Linear Systems", students_year_of_study=1,\
                                               primary_programme = msc_ee,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 
    ee5103,created = Module.objects.get_or_create(module_code = "EE5103", module_title="Computer Control Systems", students_year_of_study=1,\
                                               primary_programme = msc_ee,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 
    ee5711,created = Module.objects.get_or_create(module_code = "EE5711", module_title="Power Electronic Systems", students_year_of_study=1,\
                                               primary_programme = msc_ee,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))
    ee5134,created = Module.objects.get_or_create(module_code = "EE5134", module_title="Optical Communications and Networks", students_year_of_study=1,\
                                               primary_programme = msc_ee,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))   
    ee5137,created = Module.objects.get_or_create(module_code = "EE5137", module_title="Stochastic Processes", students_year_of_study=1,\
                                               primary_programme = msc_ee,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 
    ee5138,created = Module.objects.get_or_create(module_code = "EE5138", module_title="Optimization for Communication Systems", students_year_of_study=1,\
                                               primary_programme = msc_ee,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 
    ee5303,created = Module.objects.get_or_create(module_code = "EE5303", module_title="Microwave Electronics", students_year_of_study=1,\
                                               primary_programme = msc_ee,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 
    ee5308,created = Module.objects.get_or_create(module_code = "EE5308", module_title="Antenna Engineering", students_year_of_study=1,\
                                               primary_programme = msc_ee,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered)) 
    ee5314,created = Module.objects.get_or_create(module_code = "EE5134", module_title="Optical Communications and Networks", students_year_of_study=1,\
                                               primary_programme = msc_ee,compulsory_in_primary_programme=False,total_hours = 39,\
                                               secondary_programme = msc_ceg, compulsory_in_secondary_programme=False,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))  
    ee5731,created = Module.objects.get_or_create(module_code = "EE5731", module_title="Visual Computing", students_year_of_study=1,\
                                               primary_programme = msc_ee,compulsory_in_primary_programme=False,total_hours = 39,\
                                               secondary_programme = msc_ceg, compulsory_in_secondary_programme=False,\
                                               scenario_ref = ece_wl_scen, module_type = random.choice(all_ece_types), semester_offered= random.choice(all_semesters_offered))  

    #######
    #Create BME modules
    #####
    bn1112,created = Module.objects.get_or_create(module_code = "BN1112", module_title="Introduction to BME design and manufacturing", students_year_of_study=1,\
                                               primary_programme = bme_beng,compulsory_in_primary_programme=True,total_hours = 90,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn2112,created = Module.objects.get_or_create(module_code = "B2112", module_title="Cell and molecular biology for BME", students_year_of_study=2,\
                                               primary_programme = bme_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn2104,created = Module.objects.get_or_create(module_code = "BN2104", module_title="Quantitative approaches to public and global health", students_year_of_study=2,\
                                               primary_programme = bme_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn2301,created = Module.objects.get_or_create(module_code = "BN2301", module_title="Biochemistry and Biomaterials for Bioengineers", students_year_of_study=2,\
                                               primary_programme = bme_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn2201,created = Module.objects.get_or_create(module_code = "BN2201", module_title="Quantitative Physiology for Bioengineers", students_year_of_study=2,\
                                               primary_programme = bme_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn3101,created = Module.objects.get_or_create(module_code = "BN3101", module_title="Biomedical Engineering design", students_year_of_study=2,\
                                               primary_programme = bme_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn3406,created = Module.objects.get_or_create(module_code = "BN3406", module_title="Medical imaging and AI applications", students_year_of_study=2,\
                                               primary_programme = bme_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn3402,created = Module.objects.get_or_create(module_code = "BN3402", module_title="Bio-analytics for engineers", students_year_of_study=3,\
                                               primary_programme = bme_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn2105,created = Module.objects.get_or_create(module_code = "BN2105", module_title="Medical Device life cycle management", students_year_of_study=2,\
                                               primary_programme = bme_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn2204,created = Module.objects.get_or_create(module_code = "BN2204", module_title="Fundamentals of Biomechanics ", students_year_of_study=3,\
                                               primary_programme = bme_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    
    #Now do teaching assignemnts
    num_lecturers = [1,1,1,1,2,2,3,3]

    ece_profs = list(Lecturer.objects.filter(workload_scenario=ece_wl_scen))
    for mod in Module.objects.filter(scenario_ref=ece_wl_scen):
        num_lecs = random.choice(num_lecturers)
        random_lec_index = random.randint(0,len(ece_profs)-1)
        if (num_lecs + random_lec_index >= len(ece_profs)): random_lec_index -= 4
        for i in range(0,num_lecs):
            assign, created = TeachingAssignment.objects.get_or_create(assigned_module = mod, \
                                                                assigned_lecturer=ece_profs[random_lec_index+i], \
                                                                assigned_manually=True,\
                                                                number_of_hours=int(mod.total_hours/num_lecs),\
                                                                workload_scenario=ece_wl_scen)
    me_profs = list(Lecturer.objects.filter(workload_scenario=me_wl_scen))
    for mod in Module.objects.filter(scenario_ref=me_wl_scen):
        num_lecs = random.choice(num_lecturers)
        random_lec_index = random.randint(0,len(me_profs)-1)
        if (num_lecs + random_lec_index >= len(me_profs)): random_lec_index -= 4
        for i in range(0,num_lecs):
            assign, created = TeachingAssignment.objects.get_or_create(assigned_module = mod, \
                                                                assigned_lecturer=ece_profs[random_lec_index+i], \
                                                                assigned_manually=True,\
                                                                number_of_hours=int(mod.total_hours/num_lecs),\
                                                                workload_scenario=me_wl_scen)
 
    print(ece_profs)