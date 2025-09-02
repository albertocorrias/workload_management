# Workload management and accreditation app

## Overall structure

This Django app is intended to ehlp with management of workload within a department of an academic institution. It also handles programme-level evaluation following the data collection procedures typical of engineering accreditation. The app is developed using Django.

## Setup

-  Create a virtual environment `python3 -m venv .my_virtual_environment`
-  Activate it `source my_virtual_environment/bin/activate`
-  Make sure to have a system-wide installation of postgreSQL and follow step 1 and 2 of [this guide](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu)
-  Install what's needed
    * `pip install django`
    * `pip install psycopg2-binary`
    * `pip install django-dbbackup`
    * `pip install django-crontab`
    * `pip install python-dotenv`
    * `pip install django-debug-toolbar` (for devel settings only)
- Append, at the end of `my_virtual_environment/bin/activate` the definition of the follwoing variables
    * export DEVEL_DB_PASSWORD='YOUR PASSWORD HERE'
    * export DJANGO_DEVEL_KEY='LONG STRING HERE'
    * export DJANGO_SECRET_KEY='LONG STRING HERE'
    * export LOCAL_DB_BACKUP_DIR='SOME EXISTING DIR'

  

