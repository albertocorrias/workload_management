from django.contrib import admin

# Register your models here.
from .models import Lecturer, Module, TeachingAssignment, WorkloadScenario, ModuleType, ModuleLearningOutcome, StudentLearningOutcome, Survey, SurveyQuestionResponse,Academicyear,\
ProgrammeOffered,SubProgrammeOffered,Department,Faculty,MLOSLOMapping, ProgrammeEducationalObjective, PEOSLOMapping, MLOPerformanceMeasure, CorrectiveAction

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



