from .models import Department, UniversityStaff, Module,TeachingAssignment,Faculty, Lecturer, ProgrammeOffered

def DetermineUserHomePage(user_id,is_super_user = False, error_text = "ERROR"):
    if (UniversityStaff.objects.filter(id = user_id).exists()):
        usr = UniversityStaff.objects.filter(id = user_id).get()
        if (is_super_user == True):
            return '/workloads_index'
        if usr.user.groups.filter(name__in = ['DepartmentAdminStaff']):
            if (usr.department is None): return error_text
            dept_id = usr.department.id
            return '/department/' + str(dept_id)
        if usr.user.groups.filter(name__in = ['FacultyAdminStaff']):
            if (usr.faculty is None): return error_text
            fac_id = usr.faculty.id
            return '/school_page/' + str(fac_id)
        if usr.user.groups.filter(name__in = ['LecturerStaff']):
            if (usr.lecturer is None): return error_text
            lec_id = usr.lecturer.id
            return '/lecturer/' + str(lec_id)
    return error_text

def CanUserAdminUniversity(user_id,is_super_user = False):
    usr = UniversityStaff.objects.filter(id = user_id).get()
    if (is_super_user == True): return True #No questions asked. Super user can
    return False

def CanUserAdminThisFaculty(user_id, fac_id, is_super_user=False):
    if Faculty.objects.filter(id = fac_id).exists():
        usr = UniversityStaff.objects.filter(id = user_id).get()
        if (is_super_user == True): return True #No questions asked. Super user can
        if usr.user.groups.filter(name__in = ['FacultyAdminStaff']):#Admin of faculty of dept also can
            if usr.faculty is None: return False
            faculty_id = usr.faculty.id
            if (faculty_id == fac_id):
                return True        
    return False

def CanUserAdminThisDepartment(user_id, dept_id, is_super_user = False):
    if Department.objects.filter(id = dept_id).exists():
        usr = UniversityStaff.objects.filter(id = user_id).get()
        if (is_super_user == True): return True #No questions asked. Super user can
        if usr.user.groups.filter(name__in = ['DepartmentAdminStaff']):#Admin of same dpeartment can
            if usr.department is None: return False
            user_dept_id = usr.department.id
            if (user_dept_id == dept_id):
                return True
        if usr.user.groups.filter(name__in = ['FacultyAdminStaff']):#Admin of faculty of dept also can
            if usr.faculty is None: return False
            faculty_id = usr.faculty.id
            fac_id = Department.objects.filter(id = dept_id).get().faculty.id
            if (faculty_id == fac_id):
                return True        
    return False

def CanUserAdminThisModule(user_id, module_code,is_super_user = False):
    if Module.objects.filter(module_code = module_code).exists():
        usr = UniversityStaff.objects.filter(id = user_id).get()
        if (is_super_user == True): return True #No questions asked. Super user can
        if usr.user.groups.filter(name__in = ['DepartmentAdminStaff']):#Admin of same dpeartment can
            if usr.department is None: return False
            user_dept_id = usr.department.id
            module_department_id = Module.objects.filter(module_code = module_code).first().scenario_ref.dept.id #We take the first instance of such module
            if (user_dept_id == module_department_id):
                return True
        if usr.user.groups.filter(name__in = ['FacultyAdminStaff']):#Admin of faculty of dept also can
            if usr.faculty is None: return False
            faculty_id = usr.faculty.id
            fac_id = module_department_id = Module.objects.filter(module_code = module_code).first().scenario_ref.dept.faculty.id #We take the first instance of such module
            if (faculty_id == fac_id):
                return True
        if usr.user.groups.filter(name__in = ['LecturerStaff']):#Case of the lecturer staff...can only admin what he is teaching
            if usr.lecturer is None: return False #Must be assigned a lecturer
            lec_id = usr.lecturer.id
            #we return true only if the lecturer has been assigned to teach the module, at least once...
            if (TeachingAssignment.objects.filter(assigned_module__module_code = module_code).filter(assigned_lecturer__id = lec_id).exists()):
                return True
    return False

def CanUserAdminThisLecturer(user_id, lecturer_id,is_super_user = False):
    if Lecturer.objects.filter(id = lecturer_id).exists():
        usr = UniversityStaff.objects.filter(id = user_id).get()
        if (is_super_user == True): return True #No questions asked. Super user can
        supplied_lec_name = Lecturer.objects.filter(id=lecturer_id).get().name
        if usr.user.groups.filter(name__in = ['DepartmentAdminStaff']):#Admin of same dpeartment can
            if usr.department is None: return False
            user_dept_id = usr.department.id
            module_department_id = Lecturer.objects.filter(name = supplied_lec_name).first().workload_scenario.dept.id #We take the first instance of such lecturer (ASSUMES NO TRANSFERS!)
            if (user_dept_id == module_department_id):
                return True
        if usr.user.groups.filter(name__in = ['FacultyAdminStaff']):#Admin of faculty of dept also can
            if usr.faculty is None: return False
            faculty_id = usr.faculty.id
            fac_id = Lecturer.objects.filter(name = supplied_lec_name).first().workload_scenario.dept.faculty.id #We take the first instance of such lecturer
            if (faculty_id == fac_id):
                return True
        if usr.user.groups.filter(name__in = ['LecturerStaff']):#Case of the lecturer staff...can only admin what he is teaching
            if usr.lecturer is None: return False #Must be assigned a lecturer
            lec_name = usr.lecturer.name
            #we return true only if the lecturer has been assigned to teach the module, at least once...
            if (lec_name == supplied_lec_name):
                return True
    return False

def DetermineUserMenu(user_id, is_super_user=False):
    ret ={
        'departments' : [],
        'accreditations' : [],
        'lecturers' : [],
        'courses' : []
    }
    for dep in Department.objects.all():
        dep_item = {
            "label" : dep.department_name,
            'url' :'/department/' + str(dep.id)
        }
        if (CanUserAdminThisDepartment(user_id,dept_id=dep.id,is_super_user=is_super_user)):
            ret["departments"].append(dep_item)
    for prog in ProgrammeOffered.objects.all():
        prog_item = {
            "label" : prog.programme_name,
            'url' :'/accreditation/' + str(prog.id)
        }
        if (prog.primary_dept is not None):
            dep_id = prog.primary_dept.id
            if (CanUserAdminThisDepartment(user_id,dept_id=dep_id,is_super_user=is_super_user)):
                ret["accreditations"].append(prog_item)
    added_lecturers = []
    for lec in Lecturer.objects.all():
        if lec.name not in added_lecturers:
            lect_item = {
                "label" : lec.name,
                'url' :'/lecturer_page/' +str(lec.id)
            }
            if (CanUserAdminThisLecturer(user_id, lecturer_id = lec.id,is_super_user = is_super_user)):
                ret["lecturers"].append(lect_item)
                added_lecturers.append(lec.name)
    added_modules = []
    for mod in Module.objects.all():
        if mod.module_code not in added_modules:
            mod_item = {
                "label" : mod.module_code,
                'url' :'/module/' + mod.module_code
            }
            if (CanUserAdminThisModule(user_id, module_code = mod.module_code,is_super_user=is_super_user)):
                ret["courses"].append(mod_item)
                added_modules.append(mod.module_code)              
    return ret