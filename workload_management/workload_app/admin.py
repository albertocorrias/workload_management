from django.contrib import admin

# Register your models here.
from .models import Lecturer
from .models import Module
from .models import TeachingAssignment
from .models import WorkloadScenario
from .models import ModuleType

admin.site.register(Lecturer)
admin.site.register(Module)
admin.site.register(ModuleType)
admin.site.register(TeachingAssignment)
admin.site.register(WorkloadScenario)



