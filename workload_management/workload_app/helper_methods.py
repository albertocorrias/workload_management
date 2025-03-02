import csv
from curses.ascii import isspace
from .models import Lecturer, Module, TeachingAssignment, ModuleType, EmploymentTrack,ServiceRole, Department, \
                   WorkloadScenario,Faculty,ProgrammeOffered,SubProgrammeOffered,Academicyear
from .forms import ProfessorForm, ModuleForm,EditTeachingAssignmentForm,EditModuleAssignmentForm,AddTeachingAssignmentForm,\
                    EmplymentTrackForm, ServiceRoleForm,DepartmentForm, FacultyForm
from .global_constants import DetermineColorBasedOnBalance, ShortenString, \
                              csv_file_type, requested_table_type, DEFAULT_TRACK_NAME, \
                                DEFAULT_SERVICE_ROLE_NAME,NUMBER_OF_WEEKS_PER_SEM, DEFAULT_MODULE_TYPE_NAME


#Helper method to calculate the table of workloads
#It returns a list of items, where each item is a dictionary.
#There are as many items as workloads in the database
#Each item contains name and other info on the workload
def CalculateWorkloadsIndexTable(faculty_id = -1):    
    ret = []
    queryset = WorkloadScenario.objects.all()
    if (faculty_id>0):
        queryset = WorkloadScenario.objects.filter(dept__faculty__id = faculty_id)
    for wl_scen in queryset.order_by('label'):
        summary_data = CalculateSummaryData(wl_scen.id)
        item = {"wl_name" : wl_scen.label,
                "wl_id" : wl_scen.id,
                "acad_year" : wl_scen.academic_year.__str__(),
                "dept_acronym" : wl_scen.dept.department_acronym,
                "faculty_acronym" : wl_scen.dept.faculty.faculty_acronym,
                "status" : wl_scen.status,
                "total_hours_delivered" : summary_data["total_hours_for_workload"],
                "total_fte" : summary_data["total_department_tFTE"],
                "expected_hrs" : summary_data["expected_hours_per_tFTE"]
                }
        ret.append(item)
    return ret

#Helper method to calculate the table of employment tracks
#It returns a list of items, where each item is a dictionary.
#There are as many items as employment tracks in the database
#Each item contains name, teaching adjustment of the track, and necessary forms for editing
def CalculateEmploymentTracksTable(faculty_id = -1):    
    ret = []
    queryset = EmploymentTrack.objects.all()
    if (faculty_id>0):
        queryset = EmploymentTrack.objects.filter(faculty__id = faculty_id)
    for empl_track in queryset.order_by('track_name'):
        if (empl_track.track_name != DEFAULT_TRACK_NAME):#Wed o not show the ugly "no track" in the table. Also do not want user to edit it
            item = {"track_name" : empl_track.track_name,
                    "no_space_track_name" : RegularizeName(empl_track.track_name),
                    "track_adjustment" : empl_track.track_adjustment,
                    "edit_track_form" : EmplymentTrackForm(initial= {'track_name' : empl_track.track_name, \
                                                                    'track_adjustment' : empl_track.track_adjustment, \
                                                                    'fresh_record' : False,
                                                                    'employment_track_id' : empl_track.id})}
            ret.append(item)
    return ret

#Helper method to calculate the table of service roles
#It returns a list of items, where each item is a dictionary.
#There are as many items as service roles in the database
#Each item contains name, teaching adjustment of the role, and necessary forms for editing
def CalculateServiceRolesTable(faculty_id=-1):    
    ret = []
    queryset = ServiceRole.objects.all()
    if (faculty_id>0):
        queryset = ServiceRole.objects.filter(faculty__id = faculty_id)
    for svc_role in queryset.order_by('role_name'):
        if (svc_role.role_name != DEFAULT_SERVICE_ROLE_NAME):
            item = {"role_name" : svc_role.role_name,\
                    "no_space_role_name" : RegularizeName(svc_role.role_name),\
                    "role_adjustment" : svc_role.role_adjustment, \
                    "edit_role_form" : ServiceRoleForm(initial= {'role_name' : svc_role.role_name, \
                                                                        'role_adjustment' : svc_role.role_adjustment, \
                                                                        'fresh_record' : False,\
                                                                        'role_id' : svc_role.id}) }
            ret.append(item)
    return ret

#Helper method to calculate the table of module types
#It returns a list of items, where each item is a dictionary.
#There are as many items as module typess in the database
#Each item contains name and other info on the type
def CalculateModuleTypeTable(department_id):    
    ret = []
    for mod_tp in ModuleType.objects.filter(department__id=department_id).order_by('type_name'):
        item = {"type_name" : mod_tp.type_name}
        ret.append(item)
    return ret

#Helper method to calculate the table of departments
#It returns a list of items, where each item is a dictionary.
#There are as many items as departments in the database
#Each item contains name and acronym of the department, form and other useful info
def CalculateDepartmentTable(faculty_id=-1):    
    ret = []
    queryset = Department.objects.all()
    if (faculty_id>0):
        queryset = Department.objects.filter(faculty__id = faculty_id)
    for dept in queryset.order_by('department_name'):
        item = {"department_name" : dept.department_name,
                "department_acronym" : dept.department_acronym,
                "dept_id" : dept.id,
                "faculty" : dept.faculty.faculty_acronym,
                'no_space_dept_name' : RegularizeName(dept.department_name),
                "edit_dept_form" : DepartmentForm(initial = {'department_name' : dept.department_name, \
                                                             'department_acronym' : dept.department_acronym, \
                                                              'faculty' : dept.faculty.id,\
                                                             'fresh_record' : False, 'dept_id' : dept.id})
                }    
        ret.append(item)
    return ret

#Helper method to calculate the table of faculties/schools
#It returns a list of items, where each item is a dictionary.
#There are as many items as faculties in the database
#Each item contains name and acronym of the aculty
def CalculateFacultiesTable():    
    ret = []
    for fac in Faculty.objects.all().order_by('faculty_name'):
        item = {"faculty_name" : fac.faculty_name,
                "faculty_acronym" : fac.faculty_acronym,
                'no_space_fac_name' : RegularizeName(fac.faculty_name),
                "faculty_id" : fac.id,
                "edit_fac_form" : FacultyForm(initial = {'faculty_name' : fac.faculty_name, \
                                                         'faculty_acronym' : fac.faculty_acronym, \
                                                         'fresh_record' : False, 'fac_id' : fac.id})
                }      
        ret.append(item)
    return ret 

###################################
# A helper method that takes in a form (assumed valid)
# of the type ScenarioForm duly populated. The second parameter
# is teh id of thed epartment where the scenario is suppsed to belong to.
# The form is assumed valid (must check before using this).
# This method came about because we needed to create workload
# scenarios from two different places: one from the department page, which 
# should not be allowed to create for other departemnts, and one from 
# the workloads index page, which should be allowed to choose dpeartment.
# To avoid code repetition, this little helper method is created.
# The entire logic of cretaing workload scenario in the database, 
# copying over what is needed, if necessary, and setting all the draft/official flags
# are handled here.
######################################
def HandleScenarioForm(form,department_id):

    supplied_label = form.cleaned_data['label']
    supplied_dept = Department.objects.filter(id = department_id)
    supplied_status = form.cleaned_data['status']
    supplied_acad_year = form.cleaned_data['academic_year']
    id_involved = 0
    if (form.cleaned_data['fresh_record'] == True):
        #create a new one, this is a fresh record
        new_scen = WorkloadScenario.objects.create(label=supplied_label,dept = supplied_dept.get(),\
                                                    academic_year = supplied_acad_year, status = supplied_status)
        id_involved = new_scen.id
        
        #check if we need to copy teaching assignments, profs and modules over
        supplied_copy_from = form.cleaned_data['copy_from']
        if (supplied_copy_from != None):
            #Copy the modules. #See here for the pk tricks below
            # https://docs.djangoproject.com/en/5.1/topics/db/queries/#copying-model-instances
            for mod in Module.objects.filter(scenario_ref__label = supplied_copy_from):
                mod.pk = None
                mod.scenario_ref = new_scen
                mod.save()
            
            #Copy the profs
            for prof in Lecturer.objects.filter(workload_scenario__label = supplied_copy_from):
                prof.pk = None
                prof.workload_scenario = new_scen
                prof.save()
                
            #Now copy all assignments
            for to_be_copied in  TeachingAssignment.objects.filter(workload_scenario__label = supplied_copy_from):
                #Make sure to involve the profs and mods in the new scenario
                module_involved = Module.objects.filter(module_code = to_be_copied.assigned_module.module_code).filter(scenario_ref__label = supplied_label).get()
                prof_involved = Lecturer.objects.filter(name = to_be_copied.assigned_lecturer.name).filter(workload_scenario__label = supplied_label).get()
                #Then create the new assignment
                TeachingAssignment.objects.create(assigned_module=module_involved,\
                                                assigned_lecturer=prof_involved,\
                                                number_of_hours=int(to_be_copied.number_of_hours),\
                                                counted_towards_workload = to_be_copied.counted_towards_workload,\
                                                workload_scenario=new_scen)
    else: #This is an edit
        id_involved = form.cleaned_data['scenario_id'] #for edits, the form has the info on which scenario to be edited
        #Update
        WorkloadScenario.objects.filter(id = int(id_involved)).update(label=supplied_label,dept = supplied_dept.get(), \
                                                                        status = supplied_status, academic_year = supplied_acad_year)

    #After adding or modifying, here we check that we maintain one OFFICIAL workload per academic year per department
    #We do so by autmatically turning all the "same year", "same dept" workloads into draft mode, except, of course, the official one
    #we wanted to become official, if any.
    if(supplied_status==WorkloadScenario.OFFICIAL):
        WorkloadScenario.objects.filter(academic_year = supplied_acad_year).filter(dept = supplied_dept.get()).exclude(id=id_involved)\
                                    .update(status=WorkloadScenario.DRAFT)
    
# Helper method to compute the workload table by professor
# It queries the database and returns a list of dictonaries
# The list has as many items as professors in the database 
# For each professor, there dictionary has the following items
# prof_name : Name of the lecturer 
# assignments: modules assigned to this lecturer by module code with hours (one formatted string, ready for display)
#              If no assignments, then this string will be "No teaching assignments"
# total_hours_for_prof: the total number of assigned hours to the lecturer 
# prof_tfte: the teaching FTE for the professor
# prof_expected_hours: the expected hours to be taught by that professor: calculated based on equal distribution
#                      of the total workload hours, scaled by tFTE
# prof_balance: the balance(actualk minus expected): total_hours_for_prof - prof_expected_hours
# prof_hex_code: the HEX code (a string) of the balance (e..g, red if negative, green if positive, etc)
# "prof_id": the Id of the prof in the database
# "prof_form": a form, initialized to current prof details, for editing purposes
# "edit_assign_form" : a form to edit the teaching assignments of the prof.
# "add_assignment_for_prof_form": a form to add new teaching assignment to the prof
# "num_assigns_for_prof": the number of assignment for the prof. Includes both counted and not counted
def CalculateDepartmentWorkloadTable(workloadscenario_id):
    ret = []
    total_assigned_hours = 0
    total_workload_FTE = 0
    for prof in Lecturer.objects.filter(workload_scenario__id=workloadscenario_id).order_by('name'):

        assignment_for_this_prof = TeachingAssignment.objects.filter(assigned_lecturer__name = prof.name).filter(workload_scenario__id = workloadscenario_id)
        prof_total_assigned_hours = 0
        not_counted_total_hours = 0
        assign_counter = 0
        formatted_string = ''
        not_counted_formatted_string = ''
        for assign in assignment_for_this_prof:
            if (assign.counted_towards_workload == True):
                formatted_string += assign.assigned_module.module_code + ' (' + str(assign.number_of_hours) + '), '
                prof_total_assigned_hours = prof_total_assigned_hours + assign.number_of_hours
            else:
                not_counted_formatted_string += assign.assigned_module.module_code + ' (' + str(assign.number_of_hours) + '), '
                not_counted_total_hours += assign.number_of_hours
            assign_counter = assign_counter + 1

        if (assign_counter == 0): formatted_string = 'No teaching assignments  ' #Note the two spaces at the end, chopped off later
        if (formatted_string == ''): formatted_string = '  '
        if (not_counted_formatted_string == ''): not_counted_formatted_string = '  '
        
        #Calculate and store teaching FTE
        empl_track_adj = prof.employment_track.track_adjustment
        service_role_adj = prof.service_role.role_adjustment
        prof_fte = prof.fraction_appointment * empl_track_adj * service_role_adj

        item  = {
            "prof_name" : prof.name,
            "assignments" : formatted_string[:-2],
            "not_counted_assignments" : not_counted_formatted_string[:-2],
            "not_counted_total_hours" : not_counted_total_hours,
            "total_hours_for_prof" : prof_total_assigned_hours,
            "prof_tfte" : prof_fte,
            "prof_expected_hours" : 0, #Placeholder, will update later
            "prof_balance" : 0,#Placeholder, will update later
            "prof_hex_code" : '#FFFFFF', #White as default. May be updated later
            "no_space_name" : RegularizeName(prof.name),
            "prof_id" : prof.id,
            "prof_form" : ProfessorForm(initial = {'name' : prof.name, 'fraction_appointment' : prof.fraction_appointment,\
                                                       'employment_track' : prof.employment_track.id, \
                                                        'service_role' : prof.service_role.id, 'is_external': prof.is_external, 'fresh_record' : False}),
            "edit_assign_form" : EditTeachingAssignmentForm(prof_id = prof.id),
            "add_assignment_for_prof_form" : AddTeachingAssignmentForm(prof_id = prof.id, module_id=-1, workloadscenario_id = workloadscenario_id),
            "num_assigns_for_prof" : TeachingAssignment.objects.filter(assigned_lecturer__id = prof.id).count()
        }
        #Keep track of dept total assigned hours
        total_assigned_hours = total_assigned_hours + prof_total_assigned_hours
        #Keep track of dept total assigned hours
        total_workload_FTE = total_workload_FTE + prof_fte
        ret.append(item)

    #Now that we calculated total tFTE and total hours, we re-loop to assign expectations and balance
    index = 0
    for prof in Lecturer.objects.filter(workload_scenario__id=workloadscenario_id).order_by('name'):
        #Update expectation
        expectation = total_assigned_hours * ret[index]['prof_tfte']/total_workload_FTE
        ret[index]['prof_expected_hours'] = expectation
        #Calculate balance
        balance = float(float(ret[index]['total_hours_for_prof']) - float(ret[index]['prof_expected_hours']))
        #Store the difference, just for ease of HTML displaying later
        ret[index]['prof_balance'] = balance
        ret[index]['prof_hex_code'] = DetermineColorBasedOnBalance(balance)
        index = index + 1
    
    return ret


# Helper method to compute the module table with allocations
# It queries the database and returns a list of dictioanries
# The list has as many items as modules in the database.
# For each module, the dictionary contains
# "module_code" :the moduel code,
# "module_title" : The module ttile as a shortened string (see ShortenString method)
# "module_lecturers" : a formatted string with the list of lecturers and, for each, the hours
# "module_assigned_hours" : the total hours assigned forr this module
# "module_type" : the module type
# "num_tut_groups" : Number of tutroial groups
# "module_hours_needed" :The hours needed as stored in the module object
# "module_id" : the Id of the module
# "mod_form" : a form to edit module details. initialised to the current module data
# "edit_module_assign_form" : A form to edit the assignments for this module
# "add_assignment_for_mod_form" : A form to add a fresh assignment to this module
# "num_assigns_for_module" : The total number of teachinga ssignments for this module (includes counted and not counted)
def CalculateModuleWorkloadTable(workloadscenario_id):
    ret = []
    department = WorkloadScenario.objects.filter(id = workloadscenario_id).get().dept

    for mod in Module.objects.filter(scenario_ref__id = workloadscenario_id):

        assignment_for_this_mod = TeachingAssignment.objects.filter(assigned_module__module_code = mod.module_code).filter(workload_scenario__id = workloadscenario_id)
        total_hours_assigned_for_this_mod = 0
        total_hours_assigned_for_this_mod_not_counted = 0
        assign_counter = 0
        formatted_string = ''
        not_counted_formatted_string = ''
        for assign in assignment_for_this_mod:
            if (assign.counted_towards_workload == True):
                formatted_string += assign.assigned_lecturer.name + ' (' + str(assign.number_of_hours) + '), '
                total_hours_assigned_for_this_mod = total_hours_assigned_for_this_mod + assign.number_of_hours
            else:
                not_counted_formatted_string += assign.assigned_lecturer.name + ' (' + str(assign.number_of_hours) + '), '
                total_hours_assigned_for_this_mod_not_counted += assign.number_of_hours

            assign_counter = assign_counter + 1

        if (assign_counter==0): formatted_string = "No lecturer assigned  " #Note the two spaces at the end
        if (formatted_string == ''): formatted_string = '  '
        if (not_counted_formatted_string == ''): not_counted_formatted_string = '  '
        student_year_of_study=0
        if(mod.students_year_of_study is not None): student_year_of_study = mod.students_year_of_study

        display_mod_type = DEFAULT_MODULE_TYPE_NAME
        if (mod.module_type is not None): display_mod_type = mod.module_type.type_name

        item = {
            "module_code" : mod.module_code,
            "module_title" : ShortenString(mod.module_title),
            "module_full_title" : mod.module_title,
            "module_lecturers" : formatted_string[:-2],
            "module_lecturers_not_counted" : not_counted_formatted_string[:-2],
            "module_assigned_hours" : total_hours_assigned_for_this_mod,
            "module_assigned_hours_not_counted" : total_hours_assigned_for_this_mod_not_counted,
            "module_type" : display_mod_type,
            "num_tut_groups" : mod.number_of_tutorial_groups,
            "module_hours_needed" : mod.total_hours,
            "module_id" : mod.id,
            "mod_form" : ModuleForm(dept_id = department.id, initial = {'module_code' : mod.module_code, 'module_title' : mod.module_title,\
                                          'total_hours' : mod.total_hours, 'module_type' : mod.module_type,\
                                          'semester_offered' : mod.semester_offered,\
                                          'number_of_tutorial_groups' : mod.number_of_tutorial_groups, \
                                          'primary_programme' : mod.primary_programme,\
                                          'compulsory_in_primary_programme' : mod.compulsory_in_primary_programme,\
                                          'students_year_of_study' : student_year_of_study,\
                                          'secondary_programme' : mod.secondary_programme,\
                                          'sub_programme' : mod.sub_programme,\
                                          'secondary_sub_programme' : mod.secondary_sub_programme,\
                                          'fresh_record' : False}),
            "edit_module_assign_form" : EditModuleAssignmentForm(module_id = mod.id),
            "add_assignment_for_mod_form" : AddTeachingAssignmentForm(prof_id = -1, module_id=mod.id, workloadscenario_id = workloadscenario_id),
            "num_assigns_for_module" : TeachingAssignment.objects.filter(assigned_module__id = mod.id).count()
        }
        ret.append(item)
    return ret


#This helper method looks at the current database and produces a dictionary
#with useful summary data to be displayed. 
#It looks at the workload scenario whose id is passed in
def CalculateSummaryData(workload_scenario_id):
    
    all_teaching_assignments = TeachingAssignment.objects.filter(workload_scenario__id = workload_scenario_id)

    total_FTE_for_workload = 0
    total_hrs_for_workload = 0
    total_hours_not_counted = 0
    hours_sem_1 = 0
    hours_sem_2 = 0
    hours_other = 0
    profs_involved = []
    labels = []
    counts = []

    hours_prog = []
    labels_prog = []
    dept_id = WorkloadScenario.objects.filter(id = workload_scenario_id).get().dept.id
    for assign in all_teaching_assignments:
        mod_involved = assign.assigned_module
        prof_involved = assign.assigned_lecturer
        #make sure we don'tcount towards the workload the assignments to external profs
        if (prof_involved.is_external == True):
            assign.counted_towards_workload = False #no matter what was stored... 

        if (mod_involved.module_type is not None):
            if (mod_involved.module_type.department.id == dept_id):
                if (mod_involved.module_type.type_name not in labels):
                    labels.append(mod_involved.module_type.type_name)
                    counts.append(assign.number_of_hours)
                else:#the type is alreday there, must be in the labels array
                    indx = labels.index(mod_involved.module_type.type_name)
                    counts[indx] = counts[indx] + assign.number_of_hours
        else:
            if (DEFAULT_MODULE_TYPE_NAME not in labels):
                labels.append(DEFAULT_MODULE_TYPE_NAME)
                counts.append(assign.number_of_hours)
            else:#already there add up
                indx = labels.index(DEFAULT_MODULE_TYPE_NAME)
                counts[indx] = counts[indx] + assign.number_of_hours
                
        if (assign.counted_towards_workload == True):    
            if (mod_involved.semester_offered == Module.SEM_1):
                hours_sem_1 = hours_sem_1 + assign.number_of_hours
            if (mod_involved.semester_offered == Module.SEM_2):
                hours_sem_2 = hours_sem_2 + assign.number_of_hours
            if (mod_involved.semester_offered == Module.BOTH_SEMESTERS):
                hours_sem_1 = hours_sem_1 + assign.number_of_hours
                hours_sem_2 = hours_sem_2 + assign.number_of_hours
            if (mod_involved.semester_offered == Module.UNASSIGNED) or\
            (mod_involved.semester_offered == Module.SPECIAL_TERM_1) or\
            (mod_involved.semester_offered == Module.SPECIAL_TERM_2):
                hours_other = hours_other + assign.number_of_hours
            if (prof_involved.name not in profs_involved):
                profs_involved.append(prof_involved.name)
                track_adj = prof_involved.employment_track.track_adjustment
                empl_adj = prof_involved.service_role.role_adjustment
                total_FTE_for_workload = total_FTE_for_workload + prof_involved.fraction_appointment*track_adj*empl_adj
        
            total_hrs_for_workload = total_hrs_for_workload + assign.number_of_hours
        else:
            total_hours_not_counted = total_hours_not_counted + assign.number_of_hours

        #Calculate hours by programme offered
        no_programme_string = 'No programme'
        if (mod_involved.primary_programme is None):
            if (no_programme_string in labels_prog):
                index = labels_prog.index(no_programme_string)
                hours_prog[index] = hours_prog[index] + assign.number_of_hours #Position 0 is for "No programme"
            else:
                labels_prog.append(no_programme_string)
                hours_prog.append(assign.number_of_hours)
        else:
            prog_name = mod_involved.primary_programme.programme_name
            if (prog_name in labels_prog): #alreday there, add up
                index = labels_prog.index(prog_name)
                hours_prog[index] = hours_prog[index] + assign.number_of_hours
            else: #not there, add at the end
                labels_prog.append(prog_name)
                hours_prog.append(assign.number_of_hours)

    total_dept_fte = 0
    total_module_hours = 0
    total_adjunct_tFTE = 0
    total_number_of_adjuncts = 0
    total_number_external_staff = 0
    for prof in Lecturer.objects.filter(workload_scenario__id = workload_scenario_id):
        track_adj = prof.employment_track.track_adjustment
        empl_adj = prof.service_role.role_adjustment
        if (prof.is_external == False):
            total_dept_fte = total_dept_fte + prof.fraction_appointment*track_adj*empl_adj
        else:
            total_number_external_staff = total_number_external_staff + 1
        if (prof.employment_track.is_adjunct == True):
            total_adjunct_tFTE = total_adjunct_tFTE + prof.fraction_appointment*track_adj*empl_adj
            total_number_of_adjuncts = total_number_of_adjuncts + 1

    for mods in Module.objects.filter(scenario_ref__id=workload_scenario_id):
        total_module_hours =total_module_hours + mods.total_hours

    expected_hrs = 0
    if (total_FTE_for_workload>0):
        expected_hrs = total_hrs_for_workload/total_dept_fte

    ret = {
            'module_type_labels' : labels, #Used by the chart
            'hours_by_type' : counts, #Used by the chart
            'labels_prog' : labels_prog, #used by the chart
            'hours_prog' : hours_prog,#used by chart
            'total_tFTE_for_workload' : total_FTE_for_workload,
            'total_hours_for_workload' : total_hrs_for_workload,
            'expected_hours_per_tFTE' : expected_hrs,
            'hours_sem_1' : hours_sem_1,
            'hours_sem_2' : hours_sem_2,
            'hours_other_sems' : hours_other,
            'total_department_tFTE' : total_dept_fte,
            'total_module_hours_for_dept' : total_module_hours,
            'total_adjunct_tFTE' : total_adjunct_tFTE,
            'total_number_of_adjuncts' : total_number_of_adjuncts,
            'total_number_of_external' : total_number_external_staff,
            'total_hours_not_counted' : total_hours_not_counted
            }
    return ret

#This method helps calculating the table for a given workload scenario
#and a given programme offered by the dept. You need to pass in the workload scenario Id and the programme ID.
#Optional parameter: Whether it is a programme (default) or a sub-programme is requested (enum type "requested_table_type")
#
#It returns a structure (dictionary) that
#contains ifnormation about various tables and is convenient to visualize. The returned structure contains:
#   "scenario_name": the name of the workload scenario
#   "programme_name": the name of the programme offeered under consideration
#   "table_rows_with_mods_and_hours":  # A list of dictionaries. Each list item is a dictionary, intended as a row of an HTMl table for easy visualization
                            # ["edit_form_mod_sem_1"] the form to edit the module in sem 1, 
                            # ["regularized_mod_code_sem_1"] the regularized module code, 
                            # ["mod_code_sem_1"] mod code in sem 1, 
                            # ["hours_mod_sem_1"] hours for that module in sem 1
                            # ["edit_form_mod_sem_2"] the form to edit the module in sem 2, 
                            # ["regularized_mod_code_sem_2"] the regularized module code, ["mod_code_sem_2"] mod code in sem 2, ["hours_mod_sem_2"] hours for that module in sem 2
                            # Note that if there are, say, more mods in sem 1 than sem 2
                            # the items where there is only the module in sem 1, will have an emtpy
                            # string for the module and for the hours (fore asy HTMl visualization)
#   "mods_present" :  the number of modules present (used as a flag to display or not)
#   "total_num_mods_sem_1": the number of modules present in sem 1
#   "total_num_mods_sem_2": the number of modules present in sem 2
#   "total_hours_sem_1"  : the total hours delivered in semester 1 for this programme
#   "total_hours_sem_2"  : the total hours delivered in semester 2 for this programme
#   "unused_modules" : A list of dictionaries. Each list time contains (for easy HTML table visualization)
#                           ["unused_mod_code_sem_1"]: the code of the sem 1 module being present, but with no hours assigned in sem 1
#                           ["edit_form_unused_mod_sem_1"] the edit form for the unused module in sem 1
#                           ["unused_mod_code_sem_2"]: the code of the sem 2 module being present, but with no hours assigned in sem 2
#                           ["edit_form_unused_mod_sem_2"] the edit form for the unused module in sem 2
def CalculateModuleHourlyTableForProgramme(scenario_id,programme_id, request_type = requested_table_type.PROGRAMME):
    #TO be filled and returned
    main_table_data = {
            "scenario_name":"",
            "programme_name":"",
            "table_rows_with_mods_and_hours":[],
            "total_num_mods_sem_1" : 0,
            "total_num_mods_sem_2" : 0,
            "total_hours_sem_1" : 0,
            "total_hours_sem_2" : 0,
            "unused_modules" :[]
    }

    scenario_qs = WorkloadScenario.objects.filter(id = scenario_id)
    programme_qs = ProgrammeOffered.objects.filter(id = programme_id)
    if (scenario_qs.count()==1) : department = scenario_qs.get().dept
    
    if (request_type == requested_table_type.SUB_PROGRAMME): programme_qs = SubProgrammeOffered.objects.filter(id = programme_id)

    if ((scenario_qs.count() != 1) or (programme_qs.count() != 1)): #wrong ids for scenario or programme
        return main_table_data

    main_table_data["scenario_name"] = scenario_qs.get().label
    if (request_type == requested_table_type.PROGRAMME):
        main_table_data["programme_name"] = programme_qs.get().programme_name
    else:#sub-programme
        main_table_data["programme_name"] = programme_qs.get().sub_programme_name

    #find the modules
    mods_sem_1 = []
    mods_sem_2 = []
    unused_mods_sem_1 = []
    unused_mods_sem_2 = []
    num_mods_identified = 0
    num_mods_sem_1 = 0
    num_mods_sem_2 = 0
    total_hours_sem_1 = 0
    total_hours_sem_2 = 0
    
    if (request_type == requested_table_type.PROGRAMME):
        mod_qs = ( Module.objects.filter(scenario_ref = scenario_id).filter(primary_programme = programme_id) |
                 Module.objects.filter(scenario_ref = scenario_id).filter(secondary_programme = programme_id) )
    else:#sub-programme
        mod_qs = ( Module.objects.filter(scenario_ref = scenario_id).filter(sub_programme = programme_id) |
                 Module.objects.filter(scenario_ref = scenario_id).filter(secondary_sub_programme = programme_id) )

    for mod in mod_qs:
        #Calculate the hours assigned
        hours_assigned=0
        for assign in TeachingAssignment.objects.filter(assigned_module = mod.id):
            hours_assigned += assign.number_of_hours

        #if both semesters, we assume an equal split among the two semesters
        if (mod.semester_offered == Module.BOTH_SEMESTERS) : hours_assigned /= 2

        #Avoid problems if the year of study is None...
        student_year_of_study=0
        if(mod.students_year_of_study is not None): student_year_of_study = mod.students_year_of_study
        
        mods_row_item = {"mod_code" : mod.module_code,
            "module_title" : mod.module_title,
            "mod_hours" : hours_assigned,
            "regularized_module_code" : RegularizeName(mod.module_code),
            "mod_form" : ModuleForm(dept_id = department.id, initial = {'module_code' : mod.module_code, 'module_title' : mod.module_title,\
                                          'total_hours' : mod.total_hours, 'module_type' : mod.module_type,\
                                          'semester_offered' : mod.semester_offered,\
                                          'number_of_tutorial_groups' : mod.number_of_tutorial_groups, \
                                          'primary_programme' : mod.primary_programme,\
                                          'compulsory_in_primary_programme' : mod.compulsory_in_primary_programme,\
                                          'students_year_of_study' : student_year_of_study,\
                                          'secondary_programme' : mod.secondary_programme,\
                                          'sub_programme' : mod.sub_programme,\
                                          'secondary_sub_programme' : mod.secondary_sub_programme,\
                                          'fresh_record' : False})}
                                          
        if (mod.semester_offered == Module.SEM_1 or mod.semester_offered == Module.BOTH_SEMESTERS):
            total_hours_sem_1 += hours_assigned
            if (hours_assigned > 0):
                mods_sem_1.append(mods_row_item)
                num_mods_identified += 1
                num_mods_sem_1 += 1
            else: #store the modules not offered, or not belonging to any programme
                unused_mods_sem_1.append(mods_row_item)

        if (mod.semester_offered == Module.SEM_2 or mod.semester_offered == Module.BOTH_SEMESTERS):
            total_hours_sem_2 += hours_assigned
            if (hours_assigned > 0):
                mods_sem_2.append(mods_row_item)
                num_mods_identified += 1
                num_mods_sem_2 += 1
            else: #store the modules not offered, or not belonging to any programme
                unused_mods_sem_2.append(mods_row_item)
    
    #Now arrange the module in rows, for easy HTML visualization 
    for i in range(0,max(len(mods_sem_1),len(mods_sem_2))):
        table_row_to_append = {
            "edit_form_mod_sem_1" : "", 
            "mod_code_sem_1" : "",#MUST BE EMPTY STRING if there is no module (temaplte will check)
            "mod_title_sem_1" : "", #Will be used by the template for "title"
            "hours_mod_sem_1" : "",
            "regularized_mod_code_sem_1" : "",
            "edit_form_mod_sem_2" : "", 
            "mod_code_sem_2" : "",#MUST BE EMPTY STRING if there is no module (temaplte will check)
            "mod_title_sem_2" : "", #Will be used by the template for "title"
            "hours_mod_sem_2" : "",
            "regularized_mod_code_sem_2" : ""
        }
        if ( i < len(mods_sem_1)):
            table_row_to_append["edit_form_mod_sem_1"] = mods_sem_1[i]["mod_form"]
            table_row_to_append["mod_code_sem_1"] = mods_sem_1[i]["mod_code"]
            table_row_to_append["mod_title_sem_1"] = mods_sem_1[i]["module_title"]
            table_row_to_append["hours_mod_sem_1"] = mods_sem_1[i]["mod_hours"]
            table_row_to_append["regularized_mod_code_sem_1"] = mods_sem_1[i]["regularized_module_code"]
        if ( i < len(mods_sem_2)):
            table_row_to_append["edit_form_mod_sem_2"] = mods_sem_2[i]["mod_form"]
            table_row_to_append["mod_code_sem_2"] = mods_sem_2[i]["mod_code"]
            table_row_to_append["mod_title_sem_2"] = mods_sem_2[i]["module_title"]
            table_row_to_append["hours_mod_sem_2"] = mods_sem_2[i]["mod_hours"]
            table_row_to_append["regularized_mod_code_sem_2"] = mods_sem_2[i]["regularized_module_code"]
        main_table_data['table_rows_with_mods_and_hours'].append(table_row_to_append)
    
    for i in range(0,max(len(unused_mods_sem_1), len(unused_mods_sem_2))):
        table_row_unused_to_append = {
            "edit_form_unused_mod_sem_1" : "", 
            "unused_mod_code_sem_1" : "",#MUST BE EMPTY STRING if there is no module (temaplte will check)
            "regularized_unused_mod_code_sem_1" : "",
            "edit_form_unused_mod_sem_2" : "", 
            "unused_mod_code_sem_2" : "",#MUST BE EMPTY STRING if there is no module (temaplte will check)
            "regularized_unused_mod_code_sem_2" : ""
        }
        if ( i < len(unused_mods_sem_1)):
            table_row_unused_to_append["unused_mod_code_sem_1"] = unused_mods_sem_1[i]["mod_code"]
            table_row_unused_to_append["edit_form_unused_mod_sem_1"] = unused_mods_sem_1[i]["mod_form"]
            table_row_unused_to_append["regularized_unused_mod_code_sem_1"] = RegularizeName(unused_mods_sem_1[i]["mod_code"])
        if ( i < len(unused_mods_sem_2)):
            table_row_unused_to_append["unused_mod_code_sem_2"] = unused_mods_sem_2[i]["mod_code"]
            table_row_unused_to_append["edit_form_unused_mod_sem_2"] = unused_mods_sem_2[i]["mod_form"]
            table_row_unused_to_append["regularized_unused_mod_code_sem_2"] = RegularizeName(unused_mods_sem_2[i]["mod_code"])
        main_table_data["unused_modules"].append(table_row_unused_to_append)

    main_table_data["mods_present"] = num_mods_identified
    main_table_data["total_num_mods_sem_1"] = num_mods_sem_1
    main_table_data["total_num_mods_sem_2"] = num_mods_sem_2
    main_table_data["total_hours_sem_1"] = total_hours_sem_1
    main_table_data["total_hours_sem_2"] = total_hours_sem_2
    return main_table_data

#This method calculates the table of module types for a given workload scenario and a given programme
#It returns a stucture (dictionary) containing
# "scenario_name": The name of the workload scenario
# "programme_name":the name of the programme
# "table_rows_with_types_and_numbers": a list of dictionaries, as long as there are module types
#                                      with at least some teaching assignments. the dictionary contains
#                   "mod_type" : the name of the module type
#                   "hours_assigned_sem_1" : the total hours assigned to that module type in sem 1
#                   "hours_assigned_sem_2" : the total hours assigned to that module type in sem 2
#                   "no_mods_sem_1" : 0: the number of modules offered in sem 1 of that type
#                   "no_mods_sem_2" : 0: the number of modules offered in sem 2 of that type
# "total_num_mods_sem_1" : the total number of modules in semester 1
# "total_num_mods_sem_2" : the total number of modules in semester 1
# "total_hours_assigned_sem_1": the total hours assigned in semester 1
# "total_hours_assigned_sem_2": the total hours assigned in semester 2
def CalculateModuleTypesTableForProgramme(scenario_id,programme_id):
    #To be filled and returned
    main_table_data = {
            "scenario_name":"",
            "programme_name":"",
            "table_rows_with_types_and_numbers":[],
            "total_num_mods_sem_1" : 0,
            "total_num_mods_sem_2" : 0,
            "total_hours_assigned_sem_1":0,
            "total_hours_assigned_sem_2":0,
    }
    scenario_qs = WorkloadScenario.objects.filter(id = scenario_id)
    programme_qs = ProgrammeOffered.objects.filter(id = programme_id)
    if ((scenario_qs.count() != 1) or (programme_qs.count() != 1)): #wrong ids for scenario or programme
        return main_table_data
    main_table_data["scenario_name"] = scenario_qs.get().label
    main_table_data["programme_name"] = programme_qs.get().programme_name

    department_id = scenario_qs.get().dept.id
    for mod_type in ModuleType.objects.filter(department__id = department_id):
        mod_type_structure = {
            "mod_type" : "",
            "hours_assigned_sem_1" : 0,
            "hours_assigned_sem_2" : 0,
            "no_mods_sem_1" : 0,
            "no_mods_sem_2" : 0
        }
        mod_type_structure["mod_type"] = mod_type.type_name

        for mod in (Module.objects.filter(scenario_ref = scenario_id).filter(primary_programme = programme_id).filter(module_type = mod_type) |
                   Module.objects.filter(scenario_ref = scenario_id).filter(module_type = mod_type).filter(secondary_programme = programme_id) ):
            #Calculate the hours assigned
            hours_assigned=0
            for assign in TeachingAssignment.objects.filter(assigned_module = mod.id):
                hours_assigned += assign.number_of_hours
            #if both semesters, we assume an equal split among the two semesters
            if (mod.semester_offered == Module.BOTH_SEMESTERS) : hours_assigned /= 2

            if (mod.semester_offered == Module.SEM_1 or mod.semester_offered == Module.BOTH_SEMESTERS) and (hours_assigned > 0):
                mod_type_structure["no_mods_sem_1"] += 1
                mod_type_structure["hours_assigned_sem_1"] += hours_assigned
                main_table_data["total_num_mods_sem_1"] +=1
                main_table_data["total_hours_assigned_sem_1"] += hours_assigned
            if (mod.semester_offered == Module.SEM_2 or mod.semester_offered == Module.BOTH_SEMESTERS) and (hours_assigned > 0):
                mod_type_structure["no_mods_sem_2"] += 1
                mod_type_structure["hours_assigned_sem_2"] += hours_assigned
                main_table_data["total_num_mods_sem_2"] +=1
                main_table_data["total_hours_assigned_sem_2"] += hours_assigned
        if (mod_type_structure["no_mods_sem_1"] > 0 or mod_type_structure["no_mods_sem_2"] > 0):
            main_table_data["table_rows_with_types_and_numbers"].append(mod_type_structure)
        
    return main_table_data        
        
#Helper method to calculate the table with information
#about teh moculde whose module code is passed in.
#It looks at past official workloads only
def CalculateSingleModuleInformationTable(module_code): 
    ret = []
    for acad_year in Academicyear.objects.all():
        for workload in WorkloadScenario.objects.filter(academic_year = acad_year).filter(status=WorkloadScenario.OFFICIAL):
            for module in Module.objects.filter(module_code=module_code).filter(scenario_ref=workload):
                text_for_compulsory = "No"
                if (module.compulsory_in_primary_programme): text_for_compulsory = "Yes"
                #Infer the year of study to display
                display_year_of_study = ""
                if module.students_year_of_study == 0 and len(module_code)>2:
                    display_year_of_study = str(module_code[3])
                else:
                    display_year_of_study = str(module.students_year_of_study)

                display_mod_type = DEFAULT_MODULE_TYPE_NAME
                if (module.module_type is not None): display_mod_type = module.module_type.type_name

                table_row_item = {
                    "academic_year": acad_year.__str__(),
                    "module_type" : display_mod_type,
                    "semester_offered" : module.semester_offered,
                    "year_of_study" :  display_year_of_study,
                    "compulsory_in_primary_programme" : text_for_compulsory,
                    "primary_programme" : "",
                    "secondary_programme" : "",
                    "primary_subprogramme" : "",
                    "secondary_subprogramme" : "",
                    "total_hours_delivered" : 0,
                    "lecturers_involved" : ""}
                formatted_string = ""
                for assign in TeachingAssignment.objects.filter(workload_scenario=workload).filter(assigned_module__module_code=module_code):
                    table_row_item["total_hours_delivered"] += assign.number_of_hours
                    formatted_string+= (assign.assigned_lecturer.name + " (" + str(assign.number_of_hours) + "), ")
                if (len(formatted_string) > 0): table_row_item["lecturers_involved"] = formatted_string[:-2] #Otherwise it stays empty

                if (module.primary_programme is not None): table_row_item["primary_programme"] = module.primary_programme.programme_name
                if (module.secondary_programme is not None): table_row_item["secondary_programme"] = module.secondary_programme.programme_name
                if (module.sub_programme is not None): table_row_item["primary_subprogramme"] = module.sub_programme.sub_programme_name
                if (module.secondary_sub_programme is not None): table_row_item["secondary_subprogramme"] = module.secondary_sub_programme.sub_programme_name
                ret.append(table_row_item)
    return ret

    
def RegularizeName(name):
    ret = name.replace(" ", "")
    ret = ret.replace(",", "")
    ret = ret.replace("/", "")
    return ret

def ReadInCsvFile(filename,skip_header=0, file_type = csv_file_type.PROFESSOR_FILE):
    '''
    Method that reads in a file in csv format.

    If file_type = PROFESSOR_FILE
        then the file is intended as 
        Professor_name_1, appt_fraction_1
        Professor_name_1, appt_fraction_2
        etc
        For example:
        John Smith, 0.5
        Paul Moprhy, 1.0
        etc
    If file_type = MODULE_FILE
        then the file is intended as 
        Module code 1, Module title 1
        Module code 2, Module title 2
        etc
        For example
        MA1101, Mathematics 1
        PH202, Physics 3
        etc

    If the second column is empty, this method will interpret it as 1 for professors and "No title" for modules
    If, for professors, the appointment fraction is > 1, this method will force it to be 1

    The filename parameter is the path to the csv filename.
    The optional parameter skip_header will make the method skip the number of lines at the start 
    It returns a dictionary with the following keys
    - "errors" : boolean (True if there are errors in reading and False if not)
    - "data" : is present only if the file is open. It contains two lists of equal lengths: 
            - Names of the professor is the list at position 0 (or a list of module codes if file_type=MODULE_FILE)
            - Appointment of the professors is the list at position 1 (or a list of module titles if file_type=MODULE_FILE )
    '''

    ret = {
        "errors" : False
    }
    first_info = []#Name of prof or module code for modules
    second_info = []#Appointment (0 to 1) or module title for modules

    try:
        with open(filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 1
            for row in csv_reader:
                if line_count > skip_header:
                    if len(row) > 0 :#Handle the name or module code
                        if (row[0] != '' and row[0].isspace() == False): 
                            first_info.append(row[0])
                        else:
                            continue 
                    else:
                        continue #ignore empty lines
                    if len(row) > 1 : #Handle the appointment or module title
                        if (row[1] != '' and row[1].isspace() == False): #If not empty and not only spaces
                            if file_type == csv_file_type.PROFESSOR_FILE:
                                if float(row[1]) > 1:
                                    second_info.append('1')
                                else:
                                    second_info.append(row[1])
                            else:#Module file
                                second_info.append(row[1])
                        else:#append the value of 1 if in the file there is no indication (empty or only spaces)
                            if file_type == csv_file_type.PROFESSOR_FILE:
                                second_info.append('1')
                            else:#If it is a  module file
                                second_info.append('No title')
                    else: #No appointment indicated. We get here if there was never a second column
                            if file_type == csv_file_type.PROFESSOR_FILE:
                                second_info.append('1')
                            else:#If it is a  module file
                                second_info.append('No title')
                line_count += 1
        ret.update({"data" : [first_info,second_info]})
    except:
        ret["errors"] = True
    
    return ret

def CalculateTotalModuleHours(num_tut_groups, mod_type):
    ret = NUMBER_OF_WEEKS_PER_SEM*3
    
    if (mod_type.type_name=="Core"):
        ret = NUMBER_OF_WEEKS_PER_SEM*2 + num_tut_groups*2*NUMBER_OF_WEEKS_PER_SEM
    if (mod_type.type_name=="Faculty module"):
        ret = num_tut_groups*NUMBER_OF_WEEKS_PER_SEM*2
    if (mod_type.type_name == "EPP module"):    
        ret = num_tut_groups*3*13+2*13
    if (mod_type.type_name =="Design module"):    
        ret = num_tut_groups*1*13+2*13
    return ret