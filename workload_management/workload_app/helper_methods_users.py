from .models import Department, UniversityStaff, Module

def DetermineUserHomePage(user_id,error_text = "ERROR"):
    usr = UniversityStaff.objects.filter(id = user_id).get()
    if (usr.user.is_superuser == True):
        return 'workloads_index/'
    if usr.user.groups.filter(name__in = ['DepartmentAdminStaff']):
        if (usr.department is None): return error_text
        dept_id = usr.department.id
        return 'department/' + str(dept_id)
    if usr.user.groups.filter(name__in = ['FacultyAdminStaff']):
        if (usr.faculty is None): return error_text
        return 'workloads_index/'
    if usr.user.groups.filter(name__in = ['LecturerStaff']):
        if (usr.lecturer is None): return error_text
        lec_id = usr.user.lecturer.id
        return 'lecturer/' + str(lec_id)
    return error_text
    
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
    return False