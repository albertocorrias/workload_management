# Workload management app

## Overall structure

### Database model

The key model is called "TeachingAssignment" where one module is assigned to one lecturer for a given amount of hours in a given workload scenario. Module and Lecturer are simple database models which are self-explanatory. The "workload scenario" can be thought of as a list of teaching assignments for a given year, or, alternatively, a scenario that the user wants to play with.

### Web pages

At the moment, there is only one page with two key output tables. One table has all the lecturers who have been assigned a module in tha scenario, all the modules they have been assigned and the total hours assigned. On top of that, there is the number of expected hours. This is calculated at line 77 of views.py. The module table is similar, but has one row per module, all the lecturers assigned to it and the balance of hours.


## Some notes while learning Django.

Importnat steps for handling databases

1. Change your models (in models.py).
1. Run python manage.py makemigrations to create migrations for those changes
1. Run python manage.py migrate to apply those changes to the database.

