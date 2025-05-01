import csv
import random
import datetime
from curses.ascii import isspace
from .models import Lecturer, Module, TeachingAssignment, ModuleType, EmploymentTrack,ServiceRole, Department, \
                   WorkloadScenario,Faculty,ProgrammeOffered,SubProgrammeOffered,Academicyear,StudentLearningOutcome,\
                   ModuleLearningOutcome,MLOSLOMapping,MLOPerformanceMeasure,Survey,SurveyQuestionResponse
from .forms import ProfessorForm, ModuleForm,EditTeachingAssignmentForm,EditModuleAssignmentForm,AddTeachingAssignmentForm,\
                    EmplymentTrackForm, ServiceRoleForm,DepartmentForm, FacultyForm
from .global_constants import DetermineColorBasedOnBalance, ShortenString, \
                              csv_file_type, requested_table_type, DEFAULT_TRACK_NAME, \
                                DEFAULT_SERVICE_ROLE_NAME,NUMBER_OF_WEEKS_PER_SEM, DEFAULT_MODULE_TYPE_NAME
from .helper_methods_survey import DetermineSurveyLabelsForProgramme

def clear_database():
    Lecturer.objects.all().delete()
    Module.objects.all().delete()
    TeachingAssignment.objects.all().delete() 
    ModuleType.objects.all().delete()
    EmploymentTrack.objects.all().delete()
    ServiceRole.objects.all().delete()
    Department.objects.all().delete(), \
    WorkloadScenario.objects.all().delete()
    Faculty.objects.all().delete()
    ProgrammeOffered.objects.all().delete()
    SubProgrammeOffered.objects.all().delete()
    Academicyear.objects.all().delete()
    StudentLearningOutcome.objects.all().delete(),\
    ModuleLearningOutcome.objects.all().delete()
    MLOSLOMapping.objects.all().delete()
    MLOPerformanceMeasure.objects.all().delete()
    SurveyQuestionResponse.objects.all().delete()
    Survey.objects.all().delete()

#This helper method helps creating a databse for the demo
def populate_database():
    clear_database()    
    f = open("workload_app/others/random_names.txt", "r")
    names = []
    for x in f:
        names.append(x)
    start_year = 2020

    acad_year_0,created = Academicyear.objects.get_or_create(start_year=start_year)
    acad_year_1,created = Academicyear.objects.get_or_create(start_year=start_year+1)
    acad_year_2,created = Academicyear.objects.get_or_create(start_year=start_year+2)
    acad_year_3,created = Academicyear.objects.get_or_create(start_year=start_year+3)
    acad_year_4,created = Academicyear.objects.get_or_create(start_year=start_year+4)
    acad_year_5,created = Academicyear.objects.get_or_create(start_year=start_year+5)
    all_acad_years = [acad_year_0,acad_year_1,acad_year_2,acad_year_3,acad_year_4,acad_year_5]
    
    #Faculty and Departments
    cde_fac, created = Faculty.objects.get_or_create(faculty_name="College of Design and Engineering", faculty_acronym="CDE")
    me_dept, created = Department.objects.get_or_create(department_name="Mechanical Engineering", department_acronym="ME", faculty = cde_fac)
    ece_dept, created = Department.objects.get_or_create(department_name="Electrical and Computer Engineering", department_acronym="ECE", faculty = cde_fac)
    bme_dept, created = Department.objects.get_or_create(department_name="Biomedical Engineering", department_acronym="BME", faculty = cde_fac)

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


    num_lecturers_me = 40
    num_lecturers_ece = 43
    num_lecturers_bme = 20

    all_bme_wls = []
    all_me_wls = []
    all_ece_wls = []
    for acad_year in all_acad_years:
        this_start_year = acad_year.start_year
        me_wl_scen = WorkloadScenario.objects.create(label="ME workload " + str(this_start_year)+"/"+str(this_start_year+1),
                                                dept = me_dept, academic_year = acad_year,status = WorkloadScenario.OFFICIAL)

        ece_wl_scen = WorkloadScenario.objects.create(label="ECE workload " + str(this_start_year)+"/"+str(this_start_year+1),
                                                dept = ece_dept, academic_year = acad_year,status = WorkloadScenario.OFFICIAL)
        
        bme_wl_scen = WorkloadScenario.objects.create(label="BME workload " + str(this_start_year)+"/"+str(this_start_year+1),
                                                dept = bme_dept, academic_year = acad_year,status = WorkloadScenario.OFFICIAL)
        all_me_wls.append(me_wl_scen)
        all_ece_wls.append(ece_wl_scen)
        all_bme_wls.append(bme_wl_scen)
    
     
    frac_appontments = [1.0,1.0,1.0,0.5,0.6,0.7]
    empl_tracks = [tenure,tenure,tenure,educator,educator,adjunct]

    for i in range(0,num_lecturers_me):
        lec = Lecturer.objects.create(name = names[i],workload_scenario = all_me_wls[0],\
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
        #Now that the lecturers is created for the first wl scenario, we make copies for the other wl scenarios as well
        for i in range (1,len(all_me_wls)):
            wlscen = all_me_wls[i]
            lec.pk = None
            lec.save()
            lec.workload_scenario = wlscen
            lec.save()

    for i in range(num_lecturers_me,num_lecturers_me+num_lecturers_ece):
        lec = Lecturer.objects.create(name = names[i],workload_scenario = all_ece_wls[0],\
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
        #Now that the lecturers is created for the first wl scenario, we make copies for the other wl scenarios as well
        for i in range (1,len(all_ece_wls)):
            wlscen = all_ece_wls[i]
            lec.pk = None
            lec.save()
            lec.workload_scenario = wlscen
            lec.save()

    for i in range(num_lecturers_me+num_lecturers_ece,num_lecturers_me+num_lecturers_ece+num_lecturers_bme):
        lec = Lecturer.objects.create(name = names[i],workload_scenario = all_bme_wls[0],\
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
        #Now that the lecturers is created for the first wl scenario, we make copies for the other wl scenarios as well
        for i in range (1,len(all_bme_wls)):
            wlscen = all_bme_wls[i]
            lec.pk = None
            lec.save()
            lec.workload_scenario = wlscen
            lec.save()

    
    all_semesters_offered = [Module.SEM_1, Module.SEM_2,Module.SEM_1,Module.SEM_2,Module.BOTH_SEMESTERS]
    #######
    #Create ME modules
    #####
    mme1103,created = Module.objects.get_or_create(module_code = "ME1103", module_title="Principles of Mechanics and Materials", students_year_of_study=1,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 90,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me2105,created = Module.objects.get_or_create(module_code = "ME2105", module_title="Principles of Mechatronics and Automation", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me2102,created = Module.objects.get_or_create(module_code = "ME2102", module_title="Engineering Innovation and Modelling", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me2116,created = Module.objects.get_or_create(module_code = "ME2116", module_title="Mechanics of Materials", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me2121,created = Module.objects.get_or_create(module_code = "ME2121", module_title="Engineering Thermodynamics and Heat Transfer", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me2104,created = Module.objects.get_or_create(module_code = "ME2104", module_title="Fluid Mechanics I", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered),\
                                               sub_programme = aero_spec)
    me2162,created = Module.objects.get_or_create(module_code = "ME2162", module_title="Manufacturing Processes", students_year_of_study=2,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me3112,created = Module.objects.get_or_create(module_code = "ME3112", module_title="Mechanics of Machines", students_year_of_study=3,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me3123,created = Module.objects.get_or_create(module_code = "ME3123", module_title="Applied Thermofluids", students_year_of_study=3,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me3142,created = Module.objects.get_or_create(module_code = "ME3142", module_title="Feedback Control Systems", students_year_of_study=3,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    #Some electives
    me4212,created = Module.objects.get_or_create(module_code = "ME4212", module_title="Aircraft Structures", students_year_of_study=4,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered),\
                                                sub_programme = aero_spec)
    me4231,created = Module.objects.get_or_create(module_code = "ME4231", module_title="Aerodynamics", students_year_of_study=4,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered),\
                                                sub_programme = aero_spec)
    me4241,created = Module.objects.get_or_create(module_code = "ME4241", module_title="Aircraft Performance and Stability", students_year_of_study=4,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered),\
                                               sub_programme = aero_spec)
    me4242,created = Module.objects.get_or_create(module_code = "ME4242", module_title="Soft Robotics", students_year_of_study=4,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered),\
                                               sub_programme = robo_spec)
    me4262,created = Module.objects.get_or_create(module_code = "ME4262", module_title="Automation in Manufacturing", students_year_of_study=4,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered),\
                                               sub_programme = robo_spec)
    me4245,created = Module.objects.get_or_create(module_code = "ME4245", module_title="Robot Mechanics and Control", students_year_of_study=4,\
                                               primary_programme = me_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered),\
                                               sub_programme = robo_spec)

    #RMI courses
    rb1101,created = Module.objects.get_or_create(module_code = "RB1101", module_title="Fundamentals of Robotics I", students_year_of_study=1,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 90,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    rb2101,created = Module.objects.get_or_create(module_code = "RB2101", module_title="Fundamentals of Robotics II", students_year_of_study=1,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 90,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    rb2202,created = Module.objects.get_or_create(module_code = "RB2202", module_title="Kinematics and Dynamics for Robotics", students_year_of_study=2,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))   
    rb2203,created = Module.objects.get_or_create(module_code = "RB2203", module_title="Robot Control", students_year_of_study=2,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))       
    rb2301,created = Module.objects.get_or_create(module_code = "RB2301", module_title="Robot Programming", students_year_of_study=2,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    rb2302,created = Module.objects.get_or_create(module_code = "RB2302", module_title="Fundamentals of Artificial Neural Networks", students_year_of_study=2,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    rb3301,created = Module.objects.get_or_create(module_code = "RB3301", module_title="Introduction to Machine Intelligence", students_year_of_study=3,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    rb3302,created = Module.objects.get_or_create(module_code = "RB3302", module_title="Planning and Navigation", students_year_of_study=3,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    rb3303,created = Module.objects.get_or_create(module_code = "RB3303", module_title="Robotic System Design and Applications", students_year_of_study=3,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    #some electives
    rb3201,created = Module.objects.get_or_create(module_code = "RB3201", module_title="Sensors and Actuators for Robots", students_year_of_study=3,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    rb4107,created = Module.objects.get_or_create(module_code = "RB4107", module_title="Robotics and Machine Intelligence Design Project", students_year_of_study=4,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    rb4203,created = Module.objects.get_or_create(module_code = "RB3201", module_title="Robot Learning", students_year_of_study=4,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    bn4203,created = Module.objects.get_or_create(module_code = "BN4203", module_title="Robotics in Rehabilitation", students_year_of_study=4,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))  

    #M.Sc ME courses
    me5303,created = Module.objects.get_or_create(module_code = "ME5303", module_title="Industrial Aerodynamics", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    me5304,created = Module.objects.get_or_create(module_code = "ME5304", module_title="Experimental Fluid Mechanics", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    me5413,created = Module.objects.get_or_create(module_code = "ME5413", module_title="Autonomous Mobile Robotics", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False, secondary_programme = me_robotics, compulsory_in_secondary_programme = False,\
                                                total_hours = 39, scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    me5401,created = Module.objects.get_or_create(module_code = "ME5304", module_title="Linear Systems", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    me5402,created = Module.objects.get_or_create(module_code = "ME5402", module_title="Advanced Robotics", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    me5404,created = Module.objects.get_or_create(module_code = "ME5404", module_title="Neural Networks", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me5418,created = Module.objects.get_or_create(module_code = "ME5418", module_title="Machine Learning in Robotics", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False, secondary_programme = me_robotics, compulsory_in_secondary_programme = False,\
                                                total_hours = 39, scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 
    me5103,created = Module.objects.get_or_create(module_code = "ME5103", module_title="Plates and Shells", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me5107,created = Module.objects.get_or_create(module_code = "ME5103", module_title="Vibration Theory and Applications", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me5106,created = Module.objects.get_or_create(module_code = "ME5106", module_title="Engineering Acoustics", students_year_of_study=1,\
                                               primary_programme = me_msc,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))

    #M.Sc robotics courses
    me5421,created = Module.objects.get_or_create(module_code = "ME5421", module_title="Robot Kinematics", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))   
    me5409,created = Module.objects.get_or_create(module_code = "ME5409", module_title="Robot Dynamics and Control ", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))  
    me5410,created = Module.objects.get_or_create(module_code = "ME5410", module_title="Materials, Sensors, Actuators and Fabrication in Robotics", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))  
    me5411,created = Module.objects.get_or_create(module_code = "ME5411", module_title="Robot Vision and AI", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))  
    me5401,created = Module.objects.get_or_create(module_code = "ME5401", module_title="Linear Systems", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me5412,created = Module.objects.get_or_create(module_code = "ME5412", module_title="Robotics for Healthcare", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me5414,created = Module.objects.get_or_create(module_code = "ME5414", module_title="Optimization Techniques for Dynamic Systems", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered))
    me5415,created = Module.objects.get_or_create(module_code = "ME5415", module_title="Advanced Soft Robotics", students_year_of_study=1,\
                                               primary_programme = me_robotics,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = random.choice(all_me_types), semester_offered= random.choice(all_semesters_offered)) 

    #Create common modules for ME
    es2631,created = Module.objects.get_or_create(module_code = "ES2631", module_title="Critical Thinking and Writing", students_year_of_study=2,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,\
                                               secondary_programme = me_beng, compulsory_in_secondary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = all_me_types[-1], semester_offered= random.choice(all_semesters_offered))
    cs1010e,created = Module.objects.get_or_create(module_code = "CS1010E", module_title="Programming Methodology", students_year_of_study=1,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,\
                                               secondary_programme = me_beng, compulsory_in_secondary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = all_me_types[-1], semester_offered= random.choice(all_semesters_offered))
    gea1000,created = Module.objects.get_or_create(module_code = "GEA1000", module_title="Quantitative Reasoning with Data", students_year_of_study=1,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,\
                                               secondary_programme = me_beng, compulsory_in_secondary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = all_me_types[-1], semester_offered= random.choice(all_semesters_offered))
    dtk1234,created = Module.objects.get_or_create(module_code = "DTK1234", module_title="Design Thinking", students_year_of_study=1,\
                                               primary_programme = rmi_beng,compulsory_in_primary_programme=True,\
                                               secondary_programme = me_beng, compulsory_in_secondary_programme=True,total_hours = 39,\
                                               scenario_ref = all_me_wls[0], module_type = all_me_types[-1], semester_offered= random.choice(all_semesters_offered))
    #Now that we created all modules for one scenario, we copy them across to all scenarios
    for i in range (1,len(all_me_wls)): #Start at 1, the 0 is already populated
        wlscen = all_me_wls[i]
        for mod in Module.objects.filter(scenario_ref = all_me_wls[0]):
            mod.pk = None
            mod.save()
            mod.scenario_ref = wlscen


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

    #Now that we created all modules for one scenario, we copy them across to all scenarios
    for i in range (1,len(all_ece_wls)): #Start at 1, the 0 is already populated
        wlscen = all_ece_wls[i]
        for mod in Module.objects.filter(scenario_ref = all_ece_wls[0]):
            mod.pk = None
            mod.save()
            mod.scenario_ref = wlscen
    #######
    #Create BME modules
    #####
    #Create common modules for ECE
    es2631_ece,created = Module.objects.get_or_create(module_code = "ES2631", module_title="Critical Thinking and Writing", students_year_of_study=2,\
                                               primary_programme = bme_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = all_bme_types[-1], semester_offered= random.choice(all_semesters_offered))
    eg_1311_ece,created = Module.objects.get_or_create(module_code = "EG13111", module_title="Design and make", students_year_of_study=1,\
                                                primary_programme = bme_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = all_bme_types[-1], semester_offered= random.choice(all_semesters_offered))
    gea1000_ece,created = Module.objects.get_or_create(module_code = "GEA1000", module_title="Quantitative Reasoning with Data", students_year_of_study=1,\
                                                primary_programme = bme_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = all_bme_types[-1], semester_offered= random.choice(all_semesters_offered))
    dtk1234_ece,created = Module.objects.get_or_create(module_code = "DTK1234", module_title="Design Thinking", students_year_of_study=1,\
                                               primary_programme = bme_beng,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = all_bme_types[-1], semester_offered= random.choice(all_semesters_offered))
    #BME UG core
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
    #BME UG some electives
    bn3301,created = Module.objects.get_or_create(module_code = "BN3301", module_title="Intordiuction to Biomeaterials", students_year_of_study=3,\
                                               primary_programme = bme_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn4206,created = Module.objects.get_or_create(module_code = "BN4206", module_title="Computational Methods in BME", students_year_of_study=4,\
                                               primary_programme = bme_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    BN4301,created = Module.objects.get_or_create(module_code = "BN4301", module_title="Intordiuction to Tissue Engineering", students_year_of_study=3,\
                                               primary_programme = bme_beng,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    #BME MSc
    bn5101,created = Module.objects.get_or_create(module_code = "BN5101", module_title="Bioomedical Engineering Systems", students_year_of_study=1,\
                                               primary_programme = msc_bme,compulsory_in_primary_programme=True,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn5102,created = Module.objects.get_or_create(module_code = "BN5102", module_title="Clinical Instrumentation", students_year_of_study=1,\
                                               primary_programme = msc_bme,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))   
    bn5104,created = Module.objects.get_or_create(module_code = "BN5104", module_title="Quantitative Physiology Principles In Bioengineering", students_year_of_study=1,\
                                               primary_programme = msc_bme,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))      
    bn5201,created = Module.objects.get_or_create(module_code = "BN5201", module_title="Advanced Biomaterials", students_year_of_study=1,\
                                               primary_programme = msc_bme,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))   
    bn5202,created = Module.objects.get_or_create(module_code = "BN5202", module_title="Orthopaedic Biomechanics", students_year_of_study=1,\
                                               primary_programme = msc_bme,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn5203,created = Module.objects.get_or_create(module_code = "BN5203", module_title="Advanced Tissue Engineering", students_year_of_study=1,\
                                               primary_programme = msc_bme,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn5206,created = Module.objects.get_or_create(module_code = "BN5206", module_title="Computational Methods in Biomedical Engineering", students_year_of_study=1,\
                                               primary_programme = msc_bme,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn5207,created = Module.objects.get_or_create(module_code = "BN5207", module_title="Medical Imaging Systems", students_year_of_study=1,\
                                               primary_programme = msc_bme,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn5208,created = Module.objects.get_or_create(module_code = "BN5208", module_title="Biomedical Quality and Regulatory Systems", students_year_of_study=1,\
                                               primary_programme = msc_bme,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn5302,created = Module.objects.get_or_create(module_code = "BN5208", module_title="Organs in a Dish: Organoid Bioengineering", students_year_of_study=1,\
                                               primary_programme = msc_bme,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered))
    bn5303,created = Module.objects.get_or_create(module_code = "BN5303", module_title="Tissue Engineering for Designing Food", students_year_of_study=1,\
                                               primary_programme = msc_bme,compulsory_in_primary_programme=False,total_hours = 39,\
                                               scenario_ref = bme_wl_scen, module_type = random.choice(all_bme_types), semester_offered= random.choice(all_semesters_offered)) 
    #Now that we created all modules for one scenario, we copy them across to all scenarios
    for i in range (1,len(all_bme_wls)): #Start at 1, the 0 is already populated
        wlscen = all_bme_wls[i]
        for mod in Module.objects.filter(scenario_ref = all_bme_wls[0]):
            mod.pk = None
            mod.save()
            mod.scenario_ref = wlscen
    
    #Now do teaching assignemnts
    num_lecturers = [1,1,1,1,2,2,3,3] #how many lecturers per class
    for wlscen in all_ece_wls:
        ece_profs = list(Lecturer.objects.filter(workload_scenario=wlscen))
        for mod in Module.objects.filter(scenario_ref=wlscen):
            num_lecs = random.choice(num_lecturers)
            random_lec_index = random.randint(0,len(ece_profs)-1)
            if (num_lecs + random_lec_index >= len(ece_profs)): random_lec_index -= 4
            for i in range(0,num_lecs):
                assign, created = TeachingAssignment.objects.get_or_create(assigned_module = mod, \
                                                                    assigned_lecturer=ece_profs[random_lec_index+i], \
                                                                    assigned_manually=True,\
                                                                    number_of_hours=int(mod.total_hours/num_lecs),\
                                                                    workload_scenario=wlscen)
    for wlscen in all_me_wls:
        me_profs = list(Lecturer.objects.filter(workload_scenario=wlscen))
        for mod in Module.objects.filter(scenario_ref=wlscen):
            num_lecs = random.choice(num_lecturers)
            random_lec_index = random.randint(0,len(me_profs)-1)
            if (num_lecs + random_lec_index >= len(me_profs)): random_lec_index -= 4
            for i in range(0,num_lecs):
                assign, created = TeachingAssignment.objects.get_or_create(assigned_module = mod, \
                                                                    assigned_lecturer=ece_profs[random_lec_index+i], \
                                                                    assigned_manually=True,\
                                                                    number_of_hours=int(mod.total_hours/num_lecs),\
                                                                    workload_scenario=wlscen)
    for wlscen in all_bme_wls:
        bme_profs = list(Lecturer.objects.filter(workload_scenario=wlscen))
        for mod in Module.objects.filter(scenario_ref=wlscen):
            num_lecs = random.choice(num_lecturers)
            random_lec_index = random.randint(0,len(bme_profs)-1)
            if (num_lecs + random_lec_index >= len(bme_profs)): random_lec_index -= 4
            for i in range(0,num_lecs):
                assign, created = TeachingAssignment.objects.get_or_create(assigned_module = mod, \
                                                                    assigned_lecturer=ece_profs[random_lec_index+i], \
                                                                    assigned_manually=True,\
                                                                    number_of_hours=int(mod.total_hours/num_lecs),\
                                                                    workload_scenario=wlscen)
    ############################
    # Accreditation
    ############################

    ##SLO for B eng in ME
    slo_me_a,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Apply the knowledge of mathematics, natural science, engineering fundamentals, and an engineering specialisation to the solution of complex engineering problems.",\
                                                            slo_short_description = "Engineering knowledge",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'a',\
                                                            programme = me_beng)
    slo_me_b,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Identify, formulate, research literature, and analyse complex engineering problems reaching substantiated conclusions using first principles of mathematics, natural sciences, and engineering sciences.",\
                                                            slo_short_description = "Problem Analysis",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'b',\
                                                            programme = me_beng)
    slo_me_c,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Design solutions for complex engineering problems and design systems, components or processes that meet t h e specified needs with appropriate consideration for public health and safety, cultural, societal, and environmental considerations.",\
                                                            slo_short_description = "Design/development of Solutions",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'c',\
                                                            programme = me_beng)
    slo_me_d,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Conduct investigations of complex problems using research-based knowledge (WK8) and research methods including design of experiments, analysis and interpretation of data, and synthesis of the information to provide valid conclusions.",\
                                                            slo_short_description = "Investigation",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'd',\
                                                            programme = me_beng)
    slo_me_e,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Create, select, and apply appropriate techniques, resources, and modern engineering and IT tools including prediction and modelling to complex engineering problems, with an understanding of the limitations.",\
                                                            slo_short_description = "Modern Tool Usage",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'e',\
                                                            programme = me_beng)
    slo_me_f,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Apply reasoning informed by the contextual knowledge to assess societal, health, safety, legal, and cultural issues and the consequent responsibilities relevant to the professional engineering practice.",\
                                                            slo_short_description = "The engineer and Society",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'f',\
                                                            programme = me_beng)
    slo_me_g,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Understand the impact of the professional engineering solutions in societal and environmental contexts, and demonstrate the knowledge of, and need for t h e sustainable development.",\
                                                            slo_short_description = "Environment and Sustainability",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'g',\
                                                            programme = me_beng)
    slo_me_h,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Apply ethical principles and commit to professional ethics and responsibilities and norms of the engineering practice.",\
                                                            slo_short_description = "Ethics",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'h',\
                                                            programme = me_beng)
    slo_me_i,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Function effectively as an individual, and as a member or leader in diverse teams and in multidisciplinary settings.",\
                                                            slo_short_description = "Individual and Team Work",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'i',\
                                                            programme = me_beng)    
    slo_me_j,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Communicate effectively on complex engineering activities with the engineering community and with society at large, such as being able to comprehend and write effective reports and design documentation, make effective presentations, and give and receive clear instructions.",\
                                                            slo_short_description = "Communication",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'j',\
                                                            programme = me_beng)
    slo_me_k,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Demonstrate knowledge and understanding of t h e engineering management principles and economic decision-making, and apply these to one’s own work, as a member and leader in a team, to manage projects and in multidisciplinary environments.",\
                                                            slo_short_description = "Project Management and Finance",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'k',\
                                                            programme = me_beng) 
    slo_me_l,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Recognise the need for, and have the preparation and ability to engage in independent and life-long learning in the broadest context of technological change.",\
                                                            slo_short_description = "Life-long Learning",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'l',\
                                                            programme = me_beng)
    all_me_slo = [slo_me_a,slo_me_b,slo_me_c,slo_me_d,slo_me_e,slo_me_f, slo_me_g,slo_me_h,slo_me_i,slo_me_j,slo_me_k,slo_me_l]

    ##SLO for B eng in RMI
    slo_rmi_a,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Apply the knowledge of mathematics, natural science, engineering fundamentals, and an engineering specialisation to the solution of complex engineering problems.",\
                                                            slo_short_description = "Engineering knowledge",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'a',\
                                                            programme = rmi_beng)
    slo_rmi_b,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Identify, formulate, research literature, and analyse complex engineering problems reaching substantiated conclusions using first principles of mathematics, natural sciences, and engineering sciences.",\
                                                            slo_short_description = "Problem Analysis",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'b',\
                                                            programme = rmi_beng)
    slo_rmi_c,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Design solutions for complex engineering problems and design systems, components or processes that meet t h e specified needs with appropriate consideration for public health and safety, cultural, societal, and environmental considerations.",\
                                                            slo_short_description = "Design/development of Solutions",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'c',\
                                                            programme = rmi_beng)
    slo_rmi_d,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Conduct investigations of complex problems using research-based knowledge (WK8) and research methods including design of experiments, analysis and interpretation of data, and synthesis of the information to provide valid conclusions.",\
                                                            slo_short_description = "Investigation",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'd',\
                                                            programme = rmi_beng)
    slo_rmi_e,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Create, select, and apply appropriate techniques, resources, and modern engineering and IT tools including prediction and modelling to complex engineering problems, with an understanding of the limitations.",\
                                                            slo_short_description = "Modern Tool Usage",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'e',\
                                                            programme = rmi_beng)
    slo_rmi_f,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Apply reasoning informed by the contextual knowledge to assess societal, health, safety, legal, and cultural issues and the consequent responsibilities relevant to the professional engineering practice.",\
                                                            slo_short_description = "The engineer and Society",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'f',\
                                                            programme = rmi_beng)
    slo_rmi_g,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Understand the impact of the professional engineering solutions in societal and environmental contexts, and demonstrate the knowledge of, and need for t h e sustainable development.",\
                                                            slo_short_description = "Environment and Sustainability",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'g',\
                                                            programme = rmi_beng)
    slo_rmi_h,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Apply ethical principles and commit to professional ethics and responsibilities and norms of the engineering practice.",\
                                                            slo_short_description = "Ethics",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'h',\
                                                            programme = rmi_beng)
    slo_rmi_i,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Function effectively as an individual, and as a member or leader in diverse teams and in multidisciplinary settings.",\
                                                            slo_short_description = "Individual and Team Work",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'i',\
                                                            programme = rmi_beng)    
    slo_rmi_j,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Communicate effectively on complex engineering activities with the engineering community and with society at large, such as being able to comprehend and write effective reports and design documentation, make effective presentations, and give and receive clear instructions.",\
                                                            slo_short_description = "Communication",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'j',\
                                                            programme = rmi_beng)
    slo_rmi_k,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Demonstrate knowledge and understanding of t h e engineering management principles and economic decision-making, and apply these to one’s own work, as a member and leader in a team, to manage projects and in multidisciplinary environments.",\
                                                            slo_short_description = "Project Management and Finance",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'k',\
                                                            programme = rmi_beng) 
    slo_rmi_l,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Recognise the need for, and have the preparation and ability to engage in independent and life-long learning in the broadest context of technological change.",\
                                                            slo_short_description = "Life-long Learning",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'l',\
                                                            programme = rmi_beng) 
    all_rmi_slo = [slo_rmi_a,slo_rmi_b,slo_rmi_c,slo_rmi_d,slo_rmi_e,slo_rmi_f, slo_rmi_g,slo_rmi_h,slo_rmi_i,slo_rmi_j,slo_rmi_k,slo_rmi_l]

    ##SLO for B eng in EE
    slo_ee_a,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Apply the knowledge of mathematics, natural science, engineering fundamentals, and an engineering specialisation to the solution of complex engineering problems.",\
                                                            slo_short_description = "Engineering knowledge",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'a',\
                                                            programme = ee_beng)
    slo_ee_b,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Identify, formulate, research literature, and analyse complex engineering problems reaching substantiated conclusions using first principles of mathematics, natural sciences, and engineering sciences.",\
                                                            slo_short_description = "Problem Analysis",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'b',\
                                                            programme = ee_beng)
    slo_ee_c,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Design solutions for complex engineering problems and design systems, components or processes that meet t h e specified needs with appropriate consideration for public health and safety, cultural, societal, and environmental considerations.",\
                                                            slo_short_description = "Design/development of Solutions",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'c',\
                                                            programme = ee_beng)
    slo_ee_d,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Conduct investigations of complex problems using research-based knowledge (WK8) and research methods including design of experiments, analysis and interpretation of data, and synthesis of the information to provide valid conclusions.",\
                                                            slo_short_description = "Investigation",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'd',\
                                                            programme = ee_beng)
    slo_ee_e,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Create, select, and apply appropriate techniques, resources, and modern engineering and IT tools including prediction and modelling to complex engineering problems, with an understanding of the limitations.",\
                                                            slo_short_description = "Modern Tool Usage",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'e',\
                                                            programme = ee_beng)
    slo_ee_f,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Apply reasoning informed by the contextual knowledge to assess societal, health, safety, legal, and cultural issues and the consequent responsibilities relevant to the professional engineering practice.",\
                                                            slo_short_description = "The engineer and Society",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'f',\
                                                            programme = ee_beng)
    slo_ee_g,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Understand the impact of the professional engineering solutions in societal and environmental contexts, and demonstrate the knowledge of, and need for t h e sustainable development.",\
                                                            slo_short_description = "Environment and Sustainability",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'g',\
                                                            programme = ee_beng)
    slo_ee_h,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Apply ethical principles and commit to professional ethics and responsibilities and norms of the engineering practice.",\
                                                            slo_short_description = "Ethics",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'h',\
                                                            programme = ee_beng)
    slo_ee_i,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Function effectively as an individual, and as a member or leader in diverse teams and in multidisciplinary settings.",\
                                                            slo_short_description = "Individual and Team Work",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'i',\
                                                            programme = ee_beng)    
    slo_ee_j,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Communicate effectively on complex engineering activities with the engineering community and with society at large, such as being able to comprehend and write effective reports and design documentation, make effective presentations, and give and receive clear instructions.",\
                                                            slo_short_description = "Communication",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'j',\
                                                            programme = ee_beng)
    slo_ee_k,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Demonstrate knowledge and understanding of t h e engineering management principles and economic decision-making, and apply these to one’s own work, as a member and leader in a team, to manage projects and in multidisciplinary environments.",\
                                                            slo_short_description = "Project Management and Finance",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'k',\
                                                            programme = ee_beng) 
    slo_ee_l,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Recognise the need for, and have the preparation and ability to engage in independent and life-long learning in the broadest context of technological change.",\
                                                            slo_short_description = "Life-long Learning",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'l',\
                                                            programme = ee_beng)
    all_ee_slo = [slo_ee_a,slo_ee_b,slo_ee_c,slo_ee_d,slo_ee_e,slo_ee_f, slo_ee_g,slo_ee_h,slo_ee_i,slo_ee_j,slo_ee_k,slo_ee_l]

    ##SLO for B eng in CEG
    slo_ceg_a,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Apply the knowledge of mathematics, natural science, engineering fundamentals, and an engineering specialisation to the solution of complex engineering problems.",\
                                                            slo_short_description = "Engineering knowledge",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'a',\
                                                            programme = ceg_beng)
    slo_ceg_b,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Identify, formulate, research literature, and analyse complex engineering problems reaching substantiated conclusions using first principles of mathematics, natural sciences, and engineering sciences.",\
                                                            slo_short_description = "Problem Analysis",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'b',\
                                                            programme = ceg_beng)
    slo_ceg_c,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Design solutions for complex engineering problems and design systems, components or processes that meet t h e specified needs with appropriate consideration for public health and safety, cultural, societal, and environmental considerations.",\
                                                            slo_short_description = "Design/development of Solutions",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'c',\
                                                            programme = ceg_beng)
    slo_ceg_d,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Conduct investigations of complex problems using research-based knowledge (WK8) and research methods including design of experiments, analysis and interpretation of data, and synthesis of the information to provide valid conclusions.",\
                                                            slo_short_description = "Investigation",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'd',\
                                                            programme = ceg_beng)
    slo_ceg_e,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Create, select, and apply appropriate techniques, resources, and modern engineering and IT tools including prediction and modelling to complex engineering problems, with an understanding of the limitations.",\
                                                            slo_short_description = "Modern Tool Usage",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'e',\
                                                            programme = ceg_beng)
    slo_ceg_f,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Apply reasoning informed by the contextual knowledge to assess societal, health, safety, legal, and cultural issues and the consequent responsibilities relevant to the professional engineering practice.",\
                                                            slo_short_description = "The engineer and Society",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'f',\
                                                            programme = ceg_beng)
    slo_ceg_g,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Understand the impact of the professional engineering solutions in societal and environmental contexts, and demonstrate the knowledge of, and need for t h e sustainable development.",\
                                                            slo_short_description = "Environment and Sustainability",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'g',\
                                                            programme = ceg_beng)
    slo_ceg_h,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Apply ethical principles and commit to professional ethics and responsibilities and norms of the engineering practice.",\
                                                            slo_short_description = "Ethics",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'h',\
                                                            programme = ceg_beng)
    slo_ceg_i,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Function effectively as an individual, and as a member or leader in diverse teams and in multidisciplinary settings.",\
                                                            slo_short_description = "Individual and Team Work",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'i',\
                                                            programme = ceg_beng)    
    slo_ceg_j,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Communicate effectively on complex engineering activities with the engineering community and with society at large, such as being able to comprehend and write effective reports and design documentation, make effective presentations, and give and receive clear instructions.",\
                                                            slo_short_description = "Communication",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'j',\
                                                            programme = ceg_beng)
    slo_ceg_k,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Demonstrate knowledge and understanding of t h e engineering management principles and economic decision-making, and apply these to one’s own work, as a member and leader in a team, to manage projects and in multidisciplinary environments.",\
                                                            slo_short_description = "Project Management and Finance",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'k',\
                                                            programme = ceg_beng) 
    slo_ceg_l,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Recognise the need for, and have the preparation and ability to engage in independent and life-long learning in the broadest context of technological change.",\
                                                            slo_short_description = "Life-long Learning",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'l',\
                                                            programme = ceg_beng)
    all_ceg_slo = [slo_ceg_a,slo_ceg_b,slo_ceg_c,slo_ceg_d,slo_ceg_e,slo_ceg_f, slo_ceg_g,slo_ceg_h,slo_ceg_i,slo_ceg_j,slo_ceg_k,slo_ceg_l] 
    
    ##SLO for B eng in BME
    slo_bme_a,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Apply the knowledge of mathematics, natural science, engineering fundamentals, and an engineering specialisation to the solution of complex engineering problems.",\
                                                            slo_short_description = "Engineering knowledge",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'a',\
                                                            programme = bme_beng)
    slo_bme_b,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Identify, formulate, research literature, and analyse complex engineering problems reaching substantiated conclusions using first principles of mathematics, natural sciences, and engineering sciences.",\
                                                            slo_short_description = "Problem Analysis",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'b',\
                                                            programme = bme_beng)
    slo_bme_c,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Design solutions for complex engineering problems and design systems, components or processes that meet t h e specified needs with appropriate consideration for public health and safety, cultural, societal, and environmental considerations.",\
                                                            slo_short_description = "Design/development of Solutions",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'c',\
                                                            programme = bme_beng)
    slo_bme_d,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Conduct investigations of complex problems using research-based knowledge (WK8) and research methods including design of experiments, analysis and interpretation of data, and synthesis of the information to provide valid conclusions.",\
                                                            slo_short_description = "Investigation",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'd',\
                                                            programme = bme_beng)
    slo_bme_e,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Create, select, and apply appropriate techniques, resources, and modern engineering and IT tools including prediction and modelling to complex engineering problems, with an understanding of the limitations.",\
                                                            slo_short_description = "Modern Tool Usage",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'e',\
                                                            programme = bme_beng)
    slo_bme_f,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Apply reasoning informed by the contextual knowledge to assess societal, health, safety, legal, and cultural issues and the consequent responsibilities relevant to the professional engineering practice.",\
                                                            slo_short_description = "The engineer and Society",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'f',\
                                                            programme = bme_beng)
    slo_bme_g,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Understand the impact of the professional engineering solutions in societal and environmental contexts, and demonstrate the knowledge of, and need for t h e sustainable development.",\
                                                            slo_short_description = "Environment and Sustainability",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'g',\
                                                            programme = bme_beng)
    slo_bme_h,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Apply ethical principles and commit to professional ethics and responsibilities and norms of the engineering practice.",\
                                                            slo_short_description = "Ethics",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'h',\
                                                            programme = bme_beng)
    slo_bme_i,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Function effectively as an individual, and as a member or leader in diverse teams and in multidisciplinary settings.",\
                                                            slo_short_description = "Individual and Team Work",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'i',\
                                                            programme = bme_beng)    
    slo_bme_j,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Communicate effectively on complex engineering activities with the engineering community and with society at large, such as being able to comprehend and write effective reports and design documentation, make effective presentations, and give and receive clear instructions.",\
                                                            slo_short_description = "Communication",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'j',\
                                                            programme = bme_beng)
    slo_bme_k,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Demonstrate knowledge and understanding of t h e engineering management principles and economic decision-making, and apply these to one’s own work, as a member and leader in a team, to manage projects and in multidisciplinary environments.",\
                                                            slo_short_description = "Project Management and Finance",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'k',\
                                                            programme = bme_beng) 
    slo_bme_l,created = StudentLearningOutcome.objects.get_or_create(slo_description = "Recognise the need for, and have the preparation and ability to engage in independent and life-long learning in the broadest context of technological change.",\
                                                            slo_short_description = "Life-long Learning",\
                                                            is_default_by_accreditor = True,\
                                                            letter_associated = 'l',\
                                                            programme = bme_beng)
    all_bme_slo = [slo_bme_a,slo_bme_b,slo_bme_c,slo_bme_d,slo_bme_e,slo_bme_f,slo_bme_g,slo_bme_h,slo_bme_i,slo_bme_j,slo_bme_k,slo_bme_l]

    #Now create the MLO
    verbs = ["Describe", "Identify", "Apply","Analyze","Appraise","Construct"]
    objects = ["the fundamental tenets of", "the key principles of","the relevant aspects of"]
    me_descr = ["mechanical engineering","power and control","solid mechanics","fluid mechanics","automation"]
    rmi_descr = ["robotic movements","robotic control", "robotic vision", "robotic intelligence"]
    ee_descr = ["electricity","power generation","circuit analysis","operational amplifiers","circuit boards"]
    ceg_descr = ["computer architecture","network communication","logic gates","circuit boards","memory management"]
    bme_descr = ["human body","biomaterials","tissue engineering","design of medical devices","cellular engineering"]

    mapped_to_how_many = [3,3,3,4,4,4,5,5,6]
    how_many_mlos = [4,4,4,4,5,6]
    strengths = [1,2,3]
    #Do BME MLOs and mappings 
    for mod in Module.objects.filter(scenario_ref = all_bme_wls[0]).filter(primary_programme=bme_beng):
        module_code = mod.module_code
        num_mlos = random.choice(how_many_mlos)
        for i in range(0,num_mlos):
            how_many_slos = random.choice(mapped_to_how_many)
            disicipline_description = random.choice(bme_descr)
            description = random.choice(verbs) + " " + random.choice(objects) + " " + disicipline_description
            short_description = disicipline_description
            mlo,created = ModuleLearningOutcome.objects.get_or_create(mlo_description = description,mlo_short_description=short_description,module_code=module_code)
            for k in range(0,how_many_slos):
                mapping,createed = MLOSLOMapping.objects.get_or_create(mlo=mlo,slo = random.choice(all_bme_slo),strength = random.choice(strengths))
    #Do ME MLOs and mappings 
    for mod in Module.objects.filter(scenario_ref = all_me_wls[0]).filter(primary_programme=me_beng):
        module_code = mod.module_code
        num_mlos = random.choice(how_many_mlos)
        for i in range(0,num_mlos):
            how_many_slos = random.choice(mapped_to_how_many)
            disicipline_description = random.choice(me_descr)
            description = random.choice(verbs) + " " + random.choice(objects) + " " + disicipline_description
            short_description = disicipline_description
            mlo,created = ModuleLearningOutcome.objects.get_or_create(mlo_description = description,mlo_short_description=short_description,module_code=module_code)
            for k in range(0,how_many_slos):
                mapping,createed = MLOSLOMapping.objects.get_or_create(mlo=mlo,slo = random.choice(all_me_slo),strength = random.choice(strengths))

    #Do RMI MLOs and mappings 
    for mod in Module.objects.filter(scenario_ref = all_me_wls[0]).filter(primary_programme=rmi_beng):
        module_code = mod.module_code
        num_mlos = random.choice(how_many_mlos)
        for i in range(0,num_mlos):
            how_many_slos = random.choice(mapped_to_how_many)
            disicipline_description = random.choice(rmi_descr)
            description = random.choice(verbs) + " " + random.choice(objects) + " " + disicipline_description
            short_description = disicipline_description
            mlo,created = ModuleLearningOutcome.objects.get_or_create(mlo_description = description,mlo_short_description=short_description,module_code=module_code)
            for k in range(0,how_many_slos):
                mapping,createed = MLOSLOMapping.objects.get_or_create(mlo=mlo,slo = random.choice(all_me_slo),strength = random.choice(strengths))

    #Do EE MLOs and mappings 
    for mod in Module.objects.filter(scenario_ref = all_ece_wls[0]).filter(primary_programme=ee_beng):
        module_code = mod.module_code
        num_mlos = random.choice(how_many_mlos)
        for i in range(0,num_mlos):
            how_many_slos = random.choice(mapped_to_how_many)
            disicipline_description = random.choice(ee_descr)
            description = random.choice(verbs) + " " + random.choice(objects) + " " + disicipline_description
            short_description = disicipline_description
            mlo,created = ModuleLearningOutcome.objects.get_or_create(mlo_description = description,mlo_short_description=short_description,module_code=module_code)
            for k in range(0,how_many_slos):
                mapping,createed = MLOSLOMapping.objects.get_or_create(mlo=mlo,slo = random.choice(all_me_slo),strength = random.choice(strengths))
    #Do CEG MLOs and mappings 
    for mod in Module.objects.filter(scenario_ref = all_ece_wls[0]).filter(primary_programme=ceg_beng):
        module_code = mod.module_code
        num_mlos = random.choice(how_many_mlos)
        for i in range(0,num_mlos):
            how_many_slos = random.choice(mapped_to_how_many)
            disicipline_description = random.choice(ceg_descr)
            description = random.choice(verbs) + " " + random.choice(objects) + " " + disicipline_description
            short_description = disicipline_description
            mlo,created = ModuleLearningOutcome.objects.get_or_create(mlo_description = description,mlo_short_description=short_description,module_code=module_code)
            for k in range(0,how_many_slos):
                mapping,createed = MLOSLOMapping.objects.get_or_create(mlo=mlo,slo = random.choice(all_me_slo),strength = random.choice(strengths))
    
    #Do direct measures
    direct_measure_types = ["final exam questions 1-5",\
                            "final exam questions 6-10",\
                            "mid-term test, question 7-10",\
                            "mid-term test, question 1-6",\
                            "student presentatioins", "lab reports",\
                            "project report","project achievement score","homework assignment","weekly online quizzes"]
    possible_num_mlos = [1,2,3]
    class_sizes = [25,45,58,90,124,156,189,212]

    unique_mod_cdes = []
    for mod in Module.objects.all():
        mod_code = mod.module_code
        if (mod_code not in unique_mod_cdes):
            unique_mod_cdes.append(mod_code)

    all_progs_accr = [rmi_beng,bme_beng,me_beng,ee_beng,ceg_beng]
    for ac_year in all_acad_years:
        #Do programme survey
        for this_prog in all_progs_accr:
            srv,created = Survey.objects.get_or_create(survey_title = "Exit survey for "+this_prog.programme_name+" ("+str(ac_year.start_year)+"/"+str(ac_year.start_year+1)+")",\
                                            opening_date = datetime.datetime(ac_year.start_year+1, 4, 10),\
                                            closing_date = datetime.datetime(ac_year.start_year+1, 5, 12),\
                                            cohort_targeted = ac_year,\
                                            likert_labels = DetermineSurveyLabelsForProgramme(this_prog.id)["slo_survey_labels_object"],\
                                            survey_type = Survey.SurveyType.SLO,\
                                            max_respondents =  100, comments = "Exit survey",\
                                            programme_associated = this_prog)
            full_labels = srv.likert_labels.GetFullListOfLabels()
            actual_labels = srv.likert_labels.GetListOfLabels()
            survey_scores = [0]*len(full_labels)
            for i in range(0,len(actual_labels)):
                survey_scores.append(int(random.uniform(0,120)))
            tot_respondents = sum(survey_scores)
            srv.max_respondents = tot_respondents
            srv.save()
            for slo in StudentLearningOutcome.objects.filter(programme = this_prog):
                    new_response,created = SurveyQuestionResponse.objects.get_or_create(question_text = slo.slo_short_description,\
                        label_highest_score = full_labels[0],\
                        n_highest_score = survey_scores[0],
                        label_second_highest_score = full_labels[1],\
                        n_second_highest_score = survey_scores[1],
                        label_third_highest_score = full_labels[2],\
                        n_third_highest_score = survey_scores[2],
                        label_fourth_highest_score = full_labels[3],\
                        n_fourth_highest_score = survey_scores[3],\
                        label_fifth_highest_score = full_labels[4],\
                        n_fifth_highest_score = survey_scores[4],\
                        label_sixth_highest_score = full_labels[5],\
                        n_sixth_highest_score = survey_scores[5],\
                        label_seventh_highest_score = full_labels[6],\
                        n_seventh_highest_score = survey_scores[6],\
                        label_eighth_highest_score = full_labels[7],\
                        n_eighth_highest_score = survey_scores[7],\
                        label_ninth_highest_score = full_labels[8],\
                        n_ninth_highest_score = survey_scores[8],\
                        label_tenth_highest_score = full_labels[9],\
                        n_tenth_highest_score = survey_scores[9],\
                        associated_slo = slo, parent_survey = srv)

        #DO module-based measures (direct and surveys)
        for module_code in unique_mod_cdes:
            perf_desc = random.choice(direct_measure_types)
            perf_score = random.uniform(10,98)
            how_many_mlos = random.choice(possible_num_mlos)
            mlo_list = list(ModuleLearningOutcome.objects.filter(module_code=module_code))
            prog = mod.primary_programme
            if(len(mlo_list)>0):#exclude courses with no MLO
                if how_many_mlos==1:
                    direct_meas,created = MLOPerformanceMeasure.objects.get_or_create(description=perf_desc,academic_year=ac_year,associated_mlo=mlo_list[0],percentage_score=perf_score)
                if how_many_mlos ==2:
                    direct_meas,created = MLOPerformanceMeasure.objects.get_or_create(description=perf_desc,academic_year=ac_year,associated_mlo=mlo_list[0],\
                                                                                    secondary_associated_mlo = mlo_list[1],\
                                                                                    percentage_score=perf_score)
                if how_many_mlos ==3:
                    direct_meas,created = MLOPerformanceMeasure.objects.get_or_create(description=perf_desc,academic_year=ac_year,associated_mlo=mlo_list[0],\
                                                                                    secondary_associated_mlo = mlo_list[1],tertiary_associated_mlo = mlo_list[2],\
                                                                                    percentage_score=perf_score)
                #Create MLO surveys
                class_size = random.choice(class_sizes)
                srv,created = Survey.objects.get_or_create(survey_title = "MLO survey for "+module_code+" ("+str(ac_year.start_year)+"/"+str(ac_year.start_year+1)+")",\
                                                           opening_date = datetime.datetime(ac_year.start_year+1, 4, 10),\
                                                           closing_date = datetime.datetime(ac_year.start_year+1, 5, 12),\
                                                           cohort_targeted = ac_year,\
                                                           likert_labels = DetermineSurveyLabelsForProgramme(prog.id)["mlo_survey_labels_object"],\
                                                           survey_type = Survey.SurveyType.MLO,\
                                                           max_respondents =  class_size, comments = "None",\
                                                           programme_associated = prog)
                full_labels = srv.likert_labels.GetFullListOfLabels()
                actual_labels = srv.likert_labels.GetListOfLabels()
                survey_scores = [0]*len(full_labels)
                for i in range(0,len(actual_labels)):
                    survey_scores.append(random.uniform(0,class_size/len(actual_labels)))
                tot_respondents = sum(survey_scores)
                srv.max_respondents = tot_respondents
                srv.save()
                
                for mlo in mlo_list:
                    new_response,created = SurveyQuestionResponse.objects.get_or_create(question_text = mlo.mlo_short_description,\
                        label_highest_score = full_labels[0],\
                        n_highest_score = survey_scores[0],
                        label_second_highest_score = full_labels[1],\
                        n_second_highest_score = survey_scores[1],
                        label_third_highest_score = full_labels[2],\
                        n_third_highest_score = survey_scores[2],
                        label_fourth_highest_score = full_labels[3],\
                        n_fourth_highest_score = survey_scores[3],\
                        label_fifth_highest_score = full_labels[4],\
                        n_fifth_highest_score = survey_scores[4],\
                        label_sixth_highest_score = full_labels[5],\
                        n_sixth_highest_score = survey_scores[5],\
                        label_seventh_highest_score = full_labels[6],\
                        n_seventh_highest_score = survey_scores[6],\
                        label_eighth_highest_score = full_labels[7],\
                        n_eighth_highest_score = survey_scores[7],\
                        label_ninth_highest_score = full_labels[8],\
                        n_ninth_highest_score = survey_scores[8],\
                        label_tenth_highest_score = full_labels[9],\
                        n_tenth_highest_score = survey_scores[9],\
                        associated_mlo = mlo, parent_survey = srv)
    