from .models import Department, UniversityStaff, Module,TeachingAssignment,Faculty

def DetermineUserHomePage(user_id,error_text = "ERROR"):
    if (UniversityStaff.objects.filter(id = user_id).exists()):
        usr = UniversityStaff.objects.filter(id = user_id).get()
        if (usr.user.is_superuser == True):
            return '/workloads_index/'
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

def CanUserAdminUniversity(user_id):
    usr = UniversityStaff.objects.filter(id = user_id).get()
    if (usr.user.is_superuser == True): return True #No questions asked. Super user can
    return False

def CanUserAdminThisFaculty(user_id, fac_id):
    if Faculty.objects.filter(id = fac_id).exists():
        usr = UniversityStaff.objects.filter(id = user_id).get()
        if (usr.user.is_superuser == True): return True #No questions asked. Super user can
        if usr.user.groups.filter(name__in = ['FacultyAdminStaff']):#Admin of faculty of dept also can
            if usr.faculty is None: return False
            faculty_id = usr.faculty.id
            if (faculty_id == fac_id):
                return True        
    return False

def CanUserAdminThisDepartment(user_id, dept_id):
    if Department.objects.filter(id = dept_id).exists():
        usr = UniversityStaff.objects.filter(id = user_id).get()
        if (usr.user.is_superuser == True): return True #No questions asked. Super user can
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

def CanUserAdminThisModule(user_id, module_code):
    if Module.objects.filter(module_code = module_code).exists():
        usr = UniversityStaff.objects.filter(id = user_id).get()
        if (usr.user.is_superuser == True): return True #No questions asked. Super user can
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