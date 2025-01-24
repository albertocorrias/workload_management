from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# Register your models here.
from .models import Lecturer, Module, TeachingAssignment, WorkloadScenario, ModuleType, ModuleLearningOutcome, StudentLearningOutcome, Survey, SurveyQuestionResponse,Academicyear,\
ProgrammeOffered,SubProgrammeOffered,Department,Faculty,MLOSLOMapping, ProgrammeEducationalObjective, PEOSLOMapping, MLOPerformanceMeasure, CorrectiveAction, UniversityStaff

admin.site.register(Lecturer)
admin.site.register(Module)
admin.site.register(ModuleType)
admin.site.register(TeachingAssignment)
admin.site.register(WorkloadScenario)
admin.site.register(ModuleLearningOutcome)
admin.site.register(StudentLearningOutcome)
admin.site.register(Survey)
admin.site.register(SurveyQuestionResponse)
admin.site.register(Academicyear)
admin.site.register(ProgrammeOffered)
admin.site.register(SubProgrammeOffered)
admin.site.register(Department)
admin.site.register(Faculty)
admin.site.register(MLOSLOMapping)
admin.site.register(ProgrammeEducationalObjective)
admin.site.register(PEOSLOMapping)
admin.site.register(MLOPerformanceMeasure)
admin.site.register(CorrectiveAction)


#Following lines follow official Django documentation
#To add UniversityStaff to sjango admin

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class EmployeeInline(admin.StackedInline):
    model = UniversityStaff
    can_delete = False
    verbose_name_plural = "university_staff"


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = [EmployeeInline]


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)