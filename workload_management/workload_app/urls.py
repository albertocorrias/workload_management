from django.urls import path, include
from django.contrib import admin
from . import views

app_name = 'workload_app'

urlpatterns = [
    path('workloads_index', views.workloads_index, name='workloads_index'),
    path('scenario_view/<int:workloadscenario_id>/', views.scenario_view, name='scenario_view'),
    path('add_assignment/<int:workloadscenario_id>/', views.add_assignment, name='add_assignment'),
    path('remove_assignment/<int:workloadscenario_id>/', views.remove_assignment, name='remove_assignment'),
    path('edit_lecturer_assignments/<int:prof_id>/', views.edit_lecturer_assignments, name='edit_lecturer_assignments'),
    path('add_professor/<int:workloadscenario_id>/', views.add_professor, name='add_professor'),
    path('remove_professor/<int:workloadscenario_id>/', views.remove_professor, name='remove_professor'),
    path('add_module/<int:workloadscenario_id>/', views.add_module, name='add_module'),
    path('remove_module/<int:workloadscenario_id>/', views.remove_module, name='remove_module'),
    path('manage_module_type/<int:department_id>/', views.manage_module_type, name='manage_module_type'),
    path('remove_module_type/<int:department_id>/', views.remove_module_type, name='remove_module_type'),
    path('manage_department', views.manage_department, name='manage_department'),
    path('remove_department', views.remove_department, name='remove_department'),
    path('manage_faculty', views.manage_faculty, name='manage_faculty'),
    path('remove_faculty', views.remove_faculty, name='remove_faculty'),
    path('manage_employment_track', views.manage_employment_track, name='manage_employment_track'),
    path('remove_employment_track', views.remove_employment_track, name='remove_employment_track'),
    path('manage_service_role', views.manage_service_role, name='manage_service_role'),
    path('remove_service_role', views.remove_service_role, name='remove_service_role'),
    path('edit_module_assignments/<int:module_id>/', views.edit_module_assignments, name='edit_module_assignments'),
    path('manage_scenario', views.manage_scenario, name='manage_scenario'),
    path('remove_scenario', views.remove_scenario, name='remove_scenario'),
    path('individual_report/', views.individual_report, name='individual_report'),
    path('faculty_report/', views.faculty_report, name='faculty_report'),
    path('accreditation/<int:programme_id>/', views.accreditation, name='accreditation'),
    path('accreditation_report/<int:programme_id>/<int:start_year>-<int:end_year>/', views.accreditation_report, name='accreditation_report'),
    path('input_programme_survey_results/<int:programme_id>/<int:survey_id>/', views.input_programme_survey_results, name='input_programme_survey_results'),
    path('input_module_survey_results/<slug:module_code>/<int:survey_id>/',views.input_module_survey_results, name='input_module_survey_results'),
    path('survey_results/<int:survey_id>/', views.survey_results, name='survey_results'),
    path('department/<int:department_id>/', views.department, name='department'),
    path('module/<slug:module_code>/', views.module, name='module'),
    path('manage_programme_offered/<int:dept_id>/', views.manage_programme_offered, name='manage_programme_offered'),
    path('remove_programme_offered/<int:dept_id>/', views.remove_programme_offered, name='remove_programme_offered'),
    path('manage_subprogramme_offered/<int:dept_id>/', views.manage_subprogramme_offered, name='manage_subprogramme_offered'),
    path('remove_subprogramme_offered/<int:dept_id>/', views.remove_subprogramme_offered, name='remove_subprogramme_offered'),
    path('accounts/', include('django.contrib.auth.urls')),
    path("admin/", admin.site.urls),
]



