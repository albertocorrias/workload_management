from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from decimal import *
from workload_app.global_constants import  DEFAULT_PROGRAMME_OFFERED_NAME,DEFAULT_DEPARTMENT_NAME
from workload_app.models import ProgrammeOffered, Department, Module, ModuleType, WorkloadScenario,SubProgrammeOffered,UniversityStaff

class TestProgramme(TestCase):
    def setup_user(self):
        #The test client. We pass workload as referer as the add_module method checks if the word "department" is there for the department summary page
        self.client = Client(HTTP_REFERER = 'department')
        self.user = User.objects.create_user('test_user', 'test@user.com', 'test_user_password')
        self.user.is_superuser = True
        self.user.save()
        uni_user = UniversityStaff.objects.create(user = self.user, department=None,faculty=None)
        
    def test_add_remove_programme(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(ProgrammeOffered.objects.all().count(),0)
        #Test the GET
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        self.assertEqual(ProgrammeOffered.objects.all().count(),0) 

        self.assertEqual(Department.objects.all().count(),1) #One is created by default
        self.assertEqual(Department.objects.filter(department_name = DEFAULT_DEPARTMENT_NAME).count(),1) 
        dept = Department.objects.filter(department_name = DEFAULT_DEPARTMENT_NAME).get()
        
        #Test the POST now
        new_programme_name = 'Masters'
        self.client.post(reverse('workload_app:manage_programme_offered', kwargs={'dept_id': dept.id}),{'programme_name':new_programme_name, 'primary_dept': dept.id,'fresh_record':True})
        
        self.assertEqual(ProgrammeOffered.objects.all().count(),1) #One offered
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = new_programme_name).count(),1)

        response = self.client.get(reverse('workload_app:department', kwargs={'department_id': dept.id}))
        self.assertEqual(response.status_code, 200) #No issues

        #Add another one
        another_programme_name = 'Second Masters'
        self.client.post(reverse('workload_app:manage_programme_offered', kwargs={'dept_id': dept.id}),{'programme_name':another_programme_name, 'primary_dept': dept.id,'fresh_record':True})

        self.assertEqual(ProgrammeOffered.objects.all().count(),2) #Two offered
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = new_programme_name).count(),1)
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = another_programme_name).count(),1)
        
        response = self.client.get(reverse('workload_app:department', kwargs={'department_id': dept.id}))
        self.assertEqual(response.status_code, 200) #No issues

        #Try adding one with the same name
        self.client.post(reverse('workload_app:manage_programme_offered', kwargs={'dept_id': dept.id}),{'programme_name':another_programme_name, 'primary_dept': dept.id,'fresh_record':True})
        #check no change to the DB
        self.assertEqual(ProgrammeOffered.objects.all().count(),2) #Two offered
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = new_programme_name).count(),1)
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = another_programme_name).count(),1)

        #Try editing the first one by giving the same name as the second
        #first, get the object of the second programme
        first_prog = ProgrammeOffered.objects.filter(programme_name = new_programme_name).get() 
        self.client.post(reverse('workload_app:manage_programme_offered', kwargs={'dept_id': dept.id}),{'programme_name':new_programme_name, 'primary_dept': dept.id,'prog_id' : first_prog.id,'fresh_record':False})
        #Check nothing changed (validation of the form should have failed)
        self.assertEqual(ProgrammeOffered.objects.all().count(),2) #Two offered
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = new_programme_name).count(),1)
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = another_programme_name).count(),1)

        #Try editing the first one by giving a new valid name
        new_valid_name = "yet another one"
        self.client.post(reverse('workload_app:manage_programme_offered', kwargs={'dept_id': dept.id}),{'programme_name':new_valid_name, 'primary_dept': dept.id,'prog_id' : first_prog.id,'fresh_record':False})
        self.assertEqual(ProgrammeOffered.objects.all().count(),2) #Two offered
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = new_programme_name).count(),0)
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = another_programme_name).count(),1)
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = new_valid_name).count(),1)

        #Now remove the first programme
        second_prog = ProgrammeOffered.objects.filter(programme_name = another_programme_name).get() 
        self.client.post(reverse('workload_app:remove_programme_offered',kwargs={'dept_id': dept.id}),{'select_programme_to_remove':second_prog.id})
        self.assertEqual(ProgrammeOffered.objects.all().count(),1) #One left
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = new_programme_name).count(),0)
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = another_programme_name).count(),0)
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = new_valid_name).count(),1)

    def test_add_remove_programme_with_modules(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(ProgrammeOffered.objects.all().count(),0)
        #Test the GET
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues

        self.assertEqual(ProgrammeOffered.objects.all().count(),0) 

        self.assertEqual(Department.objects.all().count(),1) #One is created by default
        self.assertEqual(Department.objects.filter(department_name = DEFAULT_DEPARTMENT_NAME).count(),1) 
        dept = Department.objects.filter(department_name = DEFAULT_DEPARTMENT_NAME).get()
        
        #Test the POST now
        new_programme_name = 'Masters'
        self.client.post(reverse('workload_app:manage_programme_offered', kwargs={'dept_id': dept.id}),{'programme_name':new_programme_name, 'primary_dept': dept.id,'fresh_record':True})
        new_prog = ProgrammeOffered.objects.filter(programme_name=new_programme_name).get()

        self.assertEqual(ProgrammeOffered.objects.all().count(),1) #One offered
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = new_programme_name).count(),1)

        first_scenario = WorkloadScenario.objects.create(label="test scen", dept=dept)
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE")
        #now create a module
        mod_code='AX2211'
        self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': first_scenario.id}), \
                               {'module_code': mod_code, \
                                'module_title' : 'testing', 
                                'total_hours' : '234', 
                                'module_type' : mod_type_1.id, 
                                'semester_offered' : Module.UNASSIGNED, 
                                'number_of_tutorial_groups' : '2',  
                                'primary_programme' : new_prog.id,
                                'fresh_record' : True})
        self.assertEqual(Module.objects.all().count(),1)
        self.assertEqual(Module.objects.filter(primary_programme__programme_name=new_programme_name).count(),1)
        self.assertEqual(Module.objects.filter(primary_programme__isnull=True).count(),0)
        self.assertEqual(Module.objects.filter(secondary_programme__isnull=True).count(),1)#NULL by default. Not specified in the form

        #Edit the module by adding a secondary programme
        seondary_name = "UG"
        self.client.post(reverse('workload_app:manage_programme_offered', kwargs={'dept_id': dept.id}),{'programme_name':seondary_name, 'primary_dept': dept.id,'fresh_record':True})
        secondary_prog_obj = ProgrammeOffered.objects.filter(programme_name=seondary_name).get()
        self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': first_scenario.id}), \
                               {'module_code': mod_code, \
                                'module_title' : 'testing', 
                                'total_hours' : '234', 
                                'module_type' : mod_type_1.id, 
                                'semester_offered' : Module.UNASSIGNED, 
                                'number_of_tutorial_groups' : '2',  
                                'primary_programme' : new_prog.id,
                                'secondary_programme' : secondary_prog_obj.id,
                                'fresh_record' : False})
        self.assertEqual(Module.objects.all().count(),1)
        self.assertEqual(Module.objects.filter(primary_programme__programme_name=new_programme_name).count(),1)
        self.assertEqual(Module.objects.filter(secondary_programme__programme_name=seondary_name).count(),1)
        self.assertEqual(Module.objects.filter(primary_programme__isnull=True).count(),0)
        self.assertEqual(Module.objects.filter(secondary_programme__isnull=True).count(),0)
        
        #Now remove the programme
        self.client.post(reverse('workload_app:remove_programme_offered',kwargs={'dept_id': dept.id}),{'select_programme_to_remove':new_prog.id})
        self.assertEqual(Module.objects.filter(primary_programme__programme_name=new_programme_name).count(),0)
        self.assertEqual(Module.objects.filter(module_code=mod_code).count(),1)#Module still there
        self.assertEqual(Module.objects.filter(primary_programme__isnull=True).count(),1)#but with NULL reference (SET_NULL in foreign key was set)
        self.assertEqual(Module.objects.filter(secondary_programme__programme_name=seondary_name).count(),1)#Secondary programme still there
        self.assertEqual(Module.objects.filter(secondary_programme__isnull=True).count(),0)

        #Remove the secondary programme
        self.client.post(reverse('workload_app:remove_programme_offered',kwargs={'dept_id': dept.id}),{'select_programme_to_remove':secondary_prog_obj.id})
        self.assertEqual(Module.objects.filter(primary_programme__programme_name=new_programme_name).count(),0)
        self.assertEqual(Module.objects.filter(module_code=mod_code).count(),1)#Module still there
        self.assertEqual(Module.objects.filter(primary_programme__isnull=True).count(),1)#but with NULL reference (SET_NULL in foreign key was set)
        self.assertEqual(Module.objects.filter(secondary_programme__programme_name=seondary_name).count(),0)#Secondary programme NOT there
        self.assertEqual(Module.objects.filter(secondary_programme__isnull=True).count(),1)#Referecne set to NULL (SET_NULL option)


    def test_add_remove_subprogramme(self):

        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')

        self.assertEqual(ProgrammeOffered.objects.all().count(),0)
        #Test the GET
        response = self.client.get(reverse('workload_app:workloads_index'))
        self.assertEqual(response.status_code, 200) #No issues
        self.assertEqual(ProgrammeOffered.objects.all().count(),0) 
        self.assertEqual(Department.objects.all().count(),1) #One is created by default
        self.assertEqual(Department.objects.filter(department_name = DEFAULT_DEPARTMENT_NAME).count(),1) 
        dept = Department.objects.filter(department_name = DEFAULT_DEPARTMENT_NAME).get()
        
        #Test the POST now. Add one programme
        new_programme_name = 'Masters'
        self.client.post(reverse('workload_app:manage_programme_offered', kwargs={'dept_id': dept.id}),{'programme_name':new_programme_name, 'primary_dept': dept.id,'fresh_record':True})
        new_prog = ProgrammeOffered.objects.filter(programme_name=new_programme_name).get()

        self.assertEqual(ProgrammeOffered.objects.all().count(),1) #One offered
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = new_programme_name).count(),1)

        self.assertEqual(SubProgrammeOffered.objects.all().count(),0) #0 offered
        #Now add a sub-programme to it
        new_subprogramme_name = "special_sub"
        self.client.post(reverse('workload_app:manage_subprogramme_offered', kwargs={'dept_id': dept.id}),{'sub_programme_name':new_subprogramme_name, 'main_programme': new_prog.id,'fresh_record':True})
        self.assertEqual(SubProgrammeOffered.objects.all().count(),1)
        self.assertEqual(SubProgrammeOffered.objects.filter(sub_programme_name = new_subprogramme_name).count(),1)
        self.assertEqual(SubProgrammeOffered.objects.filter(main_programme__id = new_prog.id).count(),1)
        #Try removing it
        sub_prog = SubProgrammeOffered.objects.filter(sub_programme_name = new_subprogramme_name).get()
        self.client.post(reverse('workload_app:remove_subprogramme_offered', kwargs={'dept_id': dept.id}),{'select_subprogramme_to_remove' : sub_prog.id})
        self.assertEqual(SubProgrammeOffered.objects.all().count(),0)
        self.assertEqual(SubProgrammeOffered.objects.filter(sub_programme_name = new_subprogramme_name).count(),0)
        self.assertEqual(SubProgrammeOffered.objects.filter(main_programme__id = new_prog.id).count(),0)
        #re-add a sub-programme
        self.client.post(reverse('workload_app:manage_subprogramme_offered', kwargs={'dept_id': dept.id}),{'sub_programme_name':new_subprogramme_name, 'main_programme': new_prog.id,'fresh_record':True})
        self.assertEqual(SubProgrammeOffered.objects.all().count(),1)
        self.assertEqual(SubProgrammeOffered.objects.filter(sub_programme_name = new_subprogramme_name).count(),1)
        self.assertEqual(SubProgrammeOffered.objects.filter(main_programme__id = new_prog.id).count(),1)
        #edit its name
        new_name = "changed_name"
        sub_prog_object = SubProgrammeOffered.objects.filter(sub_programme_name = new_subprogramme_name).get()
        self.client.post(reverse('workload_app:manage_subprogramme_offered', kwargs={'dept_id': dept.id}),{'sub_programme_name':new_name, 'sub_prog_id': sub_prog_object.id, 'main_programme': new_prog.id,'fresh_record':False})
        self.assertEqual(SubProgrammeOffered.objects.all().count(),1)
        self.assertEqual(SubProgrammeOffered.objects.filter(sub_programme_name = new_subprogramme_name).count(),0)
        self.assertEqual(SubProgrammeOffered.objects.filter(sub_programme_name = new_name).filter(main_programme__isnull = True).count(),0)#NOT NULL to main programme
        self.assertEqual(SubProgrammeOffered.objects.filter(sub_programme_name = new_name).count(),1)
        self.assertEqual(SubProgrammeOffered.objects.filter(main_programme__id = new_prog.id).count(),1)
        #Now remove the main programme (the SET_NULL feature should put the foreign key to NULL)
        self.client.post(reverse('workload_app:remove_programme_offered',kwargs={'dept_id': dept.id}),{'select_programme_to_remove':new_prog.id})
        self.assertEqual(SubProgrammeOffered.objects.all().count(),1)
        self.assertEqual(SubProgrammeOffered.objects.filter(sub_programme_name = new_subprogramme_name).count(),0)
        self.assertEqual(SubProgrammeOffered.objects.filter(sub_programme_name = new_name).count(),1)#still there
        self.assertEqual(SubProgrammeOffered.objects.filter(sub_programme_name = new_name).filter(main_programme__isnull = True).count(),1)#NULL main programme
        self.assertEqual(SubProgrammeOffered.objects.filter(main_programme__id = new_prog.id).count(),0)

    def test_add_remove_programme_with_modules(self):
        self.setup_user()
        self.client.login(username='test_user', password='test_user_password')
        response = self.client.get(reverse('workload_app:workloads_index')) #Create default dept, faculty, etc
        dept = Department.objects.filter(department_name = DEFAULT_DEPARTMENT_NAME).get()
        first_scenario = WorkloadScenario.objects.create(label="test scen", dept=dept)

        #Add one programme
        new_programme_name = 'Masters'
        self.client.post(reverse('workload_app:manage_programme_offered', kwargs={'dept_id': dept.id}),{'programme_name':new_programme_name, 'primary_dept': dept.id,'fresh_record':True})
        new_prog = ProgrammeOffered.objects.filter(programme_name=new_programme_name).get()

        self.assertEqual(ProgrammeOffered.objects.all().count(),1) #One offered
        self.assertEqual(ProgrammeOffered.objects.filter(programme_name = new_programme_name).count(),1)
        self.assertEqual(SubProgrammeOffered.objects.all().count(),0) #0 offered

        #Now add a sub-programme to it
        new_subprogramme_name = "special_sub"
        self.client.post(reverse('workload_app:manage_subprogramme_offered', kwargs={'dept_id': dept.id}),{'sub_programme_name':new_subprogramme_name, 'main_programme': new_prog.id,'fresh_record':True})
        self.assertEqual(SubProgrammeOffered.objects.all().count(),1)
        self.assertEqual(SubProgrammeOffered.objects.filter(sub_programme_name = new_subprogramme_name).count(),1)
        self.assertEqual(SubProgrammeOffered.objects.filter(main_programme__id = new_prog.id).count(),1)
        new_sub_prog = SubProgrammeOffered.objects.filter(sub_programme_name = new_subprogramme_name).get()
        #now create a module
        mod_code='AX2211'
        mod_type_1 = ModuleType.objects.create(type_name="TEST_MOD_TYPE")
        self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': first_scenario.id}), \
                               {'module_code': mod_code, \
                                'module_title' : 'testing', 
                                'total_hours' : '234', 
                                'module_type' : mod_type_1.id, 
                                'semester_offered' : Module.UNASSIGNED, 
                                'number_of_tutorial_groups' : '2',  
                                'primary_programme' : new_prog.id,
                                'sub_programme' : new_sub_prog.id,
                                'fresh_record' : True})
        self.assertEqual(Module.objects.all().count(),1)
        self.assertEqual(Module.objects.filter(primary_programme__programme_name=new_programme_name).count(),1)
        self.assertEqual(Module.objects.filter(primary_programme__isnull=True).count(),0)
        self.assertEqual(Module.objects.filter(secondary_programme__isnull=True).count(),1)#NULL by default. Not specified in the form
        self.assertEqual(Module.objects.filter(sub_programme__isnull=True).count(),0)
        self.assertEqual(Module.objects.filter(sub_programme__sub_programme_name=new_subprogramme_name).count(),1)
        self.assertEqual(Module.objects.filter(secondary_sub_programme__isnull=True).count(),1) #Seocndary sub-programme NULL byd efault (not supplied in the form)

        #Edit the module and add a secondary subprogramme
        secondary_subprogramme_name = "sec_sub"
        self.client.post(reverse('workload_app:manage_subprogramme_offered', kwargs={'dept_id': dept.id}),{'sub_programme_name':secondary_subprogramme_name, 'main_programme': new_prog.id,'fresh_record':True})
        self.assertEqual(SubProgrammeOffered.objects.all().count(),2)
        self.assertEqual(SubProgrammeOffered.objects.filter(main_programme__programme_name =new_programme_name).count(),2)
        self.assertEqual(SubProgrammeOffered.objects.filter(sub_programme_name=secondary_subprogramme_name).count(),1)

        secondary_subprogramme_obj = SubProgrammeOffered.objects.filter(sub_programme_name=secondary_subprogramme_name).get()
        #EDit to add a secondary sub programme
        self.client.post(reverse('workload_app:add_module', kwargs={'workloadscenario_id': first_scenario.id}), \
                               {'module_code': mod_code, \
                                'module_title' : 'testing', 
                                'total_hours' : '234', 
                                'module_type' : mod_type_1.id, 
                                'semester_offered' : Module.UNASSIGNED, 
                                'number_of_tutorial_groups' : '2',  
                                'primary_programme' : new_prog.id,
                                'sub_programme' : new_sub_prog.id,
                                'secondary_sub_programme' : secondary_subprogramme_obj.id,
                                'fresh_record' : False})
        
        self.assertEqual(Module.objects.all().count(),1)
        self.assertEqual(Module.objects.filter(primary_programme__programme_name=new_programme_name).count(),1)
        self.assertEqual(Module.objects.filter(primary_programme__isnull=True).count(),0)
        self.assertEqual(Module.objects.filter(secondary_programme__isnull=True).count(),1)#NULL by default. Not specified in the form
        self.assertEqual(Module.objects.filter(sub_programme__isnull=True).count(),0)
        self.assertEqual(Module.objects.filter(sub_programme__sub_programme_name=new_subprogramme_name).count(),1)
        self.assertEqual(Module.objects.filter(secondary_sub_programme__isnull=True).count(),0)
        self.assertEqual(Module.objects.filter(secondary_sub_programme__sub_programme_name=secondary_subprogramme_name).count(),1)