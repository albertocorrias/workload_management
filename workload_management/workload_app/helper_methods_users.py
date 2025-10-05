from .models import Department, UniversityStaff, Module,TeachingAssignment,Faculty, Lecturer, ProgrammeOffered

def DetermineUserHomePage(user_obj,is_super_user = False, error_text = "ERROR"):

    if (is_super_user == True):
        return '/workloads_index'
    if user_obj.user.groups.filter(name__in = ['DepartmentAdminStaff']):
        if (user_obj.department is None): return error_text
        dept_id = user_obj.department.id
        return '/department/' + str(dept_id)
    if user_obj.user.groups.filter(name__in = ['FacultyAdminStaff']):
        if (user_obj.faculty is None): return error_text
        fac_id = user_obj.faculty.id
        return '/school_page/' + str(fac_id)
    if user_obj.user.groups.filter(name__in = ['LecturerStaff']):
        if (user_obj.lecturer is None): return error_text
        lec_id = user_obj.lecturer.id
        return '/lecturer_page/' + str(lec_id)
    return error_text

def CanUserAdminUniversity(user_obj,is_super_user = False):
    #usr = UniversityStaff.objects.filter(user__id = user_id).get()
    if (is_super_user == True): return True #No questions asked. Super user can
    return False

def CanUserAdminThisFaculty(user_obj, fac_id, is_super_user=False):
    if (is_super_user == True): return True #No questions asked. Super user can
    if user_obj.user.groups.filter(name__in = ['FacultyAdminStaff']):#Admin of faculty of dept also can
        if user_obj.faculty is None: return False
        faculty_id = user_obj.faculty.id
        if (faculty_id == fac_id):
            return True        
    return False

def CanUserAdminThisDepartment(user_obj, dept_id, is_super_user = False):

    if (is_super_user == True): return True #No questions asked. Super user can
    if user_obj.user.groups.filter(name__in = ['DepartmentAdminStaff']):#Admin of same dpeartment can
        if user_obj.department is None: return False
        user_dept_id = user_obj.department.id
        if (user_dept_id == dept_id):
            return True
    if user_obj.user.groups.filter(name__in = ['FacultyAdminStaff']):#Admin of faculty of dept also can
        if user_obj.faculty is None: return False
        faculty_id = user_obj.faculty.id
        fac_id = Department.objects.filter(id = dept_id).get().faculty.id
        if (faculty_id == fac_id):
            return True        
    return False

def CanUserAdminThisModule(user_obj, module_code, dept, fac ,is_super_user = False):

    if (is_super_user == True): return True #No questions asked. Super user can
    if user_obj.user.groups.filter(name__in = ['DepartmentAdminStaff']):#Admin of same dpeartment can
        if user_obj.department is None: return False
        user_dept_id = user_obj.department.id
        module_department_id = dept.id#Module.objects.filter(module_code = module_code).first().scenario_ref.dept.id #We take the first instance of such module
        if (user_dept_id == module_department_id):
            return True
    if user_obj.user.groups.filter(name__in = ['FacultyAdminStaff']):#Admin of faculty of dept also can
        if user_obj.faculty is None: return False
        faculty_id = user_obj.faculty.id
        fac_id = fac.id
        if (faculty_id == fac_id):
            return True
    if user_obj.user.groups.filter(name__in = ['LecturerStaff']):#Case of the lecturer staff...can only admin what he is teaching
        if user_obj.lecturer is None: return False #Must be assigned a lecturer
        lec_id = user_obj.lecturer.id
        lec_name=Lecturer.objects.filter(id = lec_id).get().name
        #we return true only if the lecturer has been assigned to teach the module, at least once...
        if (TeachingAssignment.objects.filter(assigned_module__module_code = module_code).filter(assigned_lecturer__name = lec_name).exists()):
            return True
    return False

def CanUserAdminThisLecturer(user_obj, lect_name, dept, fac ,is_super_user = False):

    if (is_super_user == True): return True #No questions asked. Super user can
    if user_obj.user.groups.filter(name__in = ['DepartmentAdminStaff']):#Admin of same dpeartment can
        if user_obj.department is None: return False
        user_dept_id = user_obj.department.id
        module_department_id = dept.id #We take the first instance of such lecturer (ASSUMES NO TRANSFERS!)
        if (user_dept_id == module_department_id):
            return True
    if user_obj.user.groups.filter(name__in = ['FacultyAdminStaff']):#Admin of faculty of dept also can
        if user_obj.faculty is None: return False
        faculty_id = user_obj.faculty.id
        fac_id = fac.id #We take the first instance of such lecturer
        if (faculty_id == fac_id):
            return True
    if user_obj.user.groups.filter(name__in = ['LecturerStaff']):#Case of the lecturer staff...can only admin what he is teaching
        if user_obj.lecturer is None: return False #Must be assigned a lecturer
        lec_name = user_obj.lecturer.name
        #we return true only if the lecturer has been assigned to teach the module, at least once...
        if (lec_name == lect_name):
            return True
    return False

def DetermineUserMenu(user_obj, is_super_user=False,force_population=False):
    ret ={
        'departments' : [],
        'accreditations' : [],
        'lecturers' : [],
        'modules' : []
    }

    if (user_obj.is_menu_populated and force_population == False):
        for dept_id in user_obj.departments_in_menu:
            dep_item = {
                    'label' : Department.objects.filter(id=dept_id).get().department_name,
                    'id' : dept_id,
                    'url' :'/department/' + str(dept_id)
                }
            ret["departments"].append(dep_item)
        for lect_id in user_obj.lecturers_in_menu:
            lec_item = {
                    'label' : Lecturer.objects.filter(id=lect_id).get().name,
                    'id' : lect_id,
                    'url' :'/lecturer_page/' + str(lect_id)
                }
            ret["lecturers"].append(lec_item)
        for prog_id in user_obj.programmes_in_menu:
            prog_item = {
                    'label' : ProgrammeOffered.objects.filter(id=prog_id).get().programme_name,
                    'id' : prog_id,
                    'url' :'/accreditation/' + str(prog_id)
                }
            ret["accreditations"].append(prog_item)        
        for mod_id in user_obj.modules_in_menu:
            mod_item = {
                    'label' : Module.objects.filter(id=mod_id).get().module_code,
                    'id' : mod_id,
                    'url' :'/module/' + str(mod_id)
                }
            ret["modules"].append(mod_item)   
            
    else:#populate the menu -should happen rarely, and only at the start for a user
        user_obj.departments_in_menu = []
        user_obj.programmes_in_menu = []
        user_obj.lecturers_in_menu = []
        user_obj.modules_in_menu = []
        user_obj.save()

        for dep in Department.objects.all():
            if (CanUserAdminThisDepartment(user_obj,dept_id=dep.id,is_super_user=is_super_user)):
                dep_item = {
                    'label' : dep.department_name,
                    'id' : dep.id,
                    'url' :'/department/' + str(dep.id)
                }
                user_obj.departments_in_menu.append(dep.id)
                ret["departments"].append(dep_item)

        for prog in ProgrammeOffered.objects.select_related("primary_dept").all():
            prog_item = {
                "label" : prog.programme_name,
                'id' : prog.id,
                'url' :'/accreditation/' + str(prog.id)
            }
            if (prog.primary_dept is not None):
                dep_id = prog.primary_dept.id
                if (CanUserAdminThisDepartment(user_obj,dept_id=dep_id,is_super_user=is_super_user)):
                    user_obj.programmes_in_menu.append(prog.id)
                    ret["accreditations"].append(prog_item)
        
        added_lecturers = []
        for lec in Lecturer.objects.select_related("workload_scenario","workload_scenario__dept","workload_scenario__dept__faculty").all():
            lect_name = lec.name
            lect_id = lec.id
            ws = lec.workload_scenario
            dept = ws.dept
            fac = dept.faculty    
            if lect_name not in added_lecturers:
                if CanUserAdminThisLecturer(user_obj, lect_name, dept, fac, is_super_user = is_super_user):
                    lect_item = {
                        "label" : lect_name,
                        'id' : lect_id,
                        'url' :'/lecturer_page/' +str(lect_id)
                    }
                    added_lecturers.append(lect_name)
                    user_obj.lecturers_in_menu.append(lect_id)
                    ret["lecturers"].append(lect_item)
            
        added_modules = []
        for mod in Module.objects.select_related("scenario_ref","scenario_ref__dept","scenario_ref__dept__faculty").all():
            module_code = mod.module_code
            ws = mod.scenario_ref
            dept = ws.dept
            fac = dept.faculty
            
            if mod.module_code not in added_modules:
                if (CanUserAdminThisModule(user_obj, module_code, dept, fac ,is_super_user=is_super_user)):
                    mod_item = {
                        'label' : mod.module_code,
                        'id' : mod.id,
                        'url' :'/module/' + mod.module_code
                    }
                    ret["modules"].append(mod_item)
                    user_obj.modules_in_menu.append(mod.id)
                    added_modules.append(mod.module_code)        
        user_obj.is_menu_populated = True
        user_obj.save()
      
    return ret