===================================
Workload Management
===================================

-----------------------
Overview
-----------------------
Therer are 4 types of users with cascading access priviliges. At the bottom, the lecturer can see the courses he/she is assigned to. The Department admin manages the programmes offered by the department and the teaching wrokloads. The Faculty admin manages all the Departments in the Faculty, while the University admin has access to all Faculties.

.. image:: ../images/overview.svg
   :alt: Overview of access and entities
   :width: 100%

---------------------
The workload scenario
---------------------
The workload scenario consists of a series of **teaching assignments** for a given academic year. Each teaching assignment is made of a lecturer, a course, and a number of hours assigned.
In the example below, the lecturer Lionel Duffy is assigned to teach the course ME3123. The **teaching assignment type** can be selected from the drop-down list.
The types of teaching assignments are set by the faculty. In the example, Lionel Duffy is assigned to teach 3 groups of stduents for a design project. 
Each group counts for 13 hours. 

.. image:: ../images/add_assignment.gif
   :alt: Adding a teaching assignment
   :width: 80%

After this operation, Lionel Duffy willl be loaded with 39 hours (13X3). 

.. image:: ../images/workload_table.png
   :alt: Sample workload table
   :width: 100%

The **workload scenario** contains a table where each row is a lecturer, and for each lecturer

* The name of the lecturer
* The lectrer teaching Full TIme Equivalent (see `The concept of tFTE`_ below)
* The list of teaching assignments (with hours in brackets). Assignments in grey are not counted towards the workload.
* The total hours assigned
* The expected hours (see `The calculation of expected workload`_ below)
* The balance (hours aasssigned - expected hours)


Each Department can have as many workload scenarios as wanted. Workload scenarios can be created, copied and modified over many years.

-------------------
The concept of tFTE
-------------------

Workload computation is based on the concept of **teaching Full Time Equivalent** (tFTE). It is calculated as follows

.. math::

   tFTE = T_{adj}*R_{adj}*FTE

where 

  * :math:`FTE` is the Full-Time equivalent of the staff with the Department (1.0 if fully employed by the Department)
  * :math:`T_{adj}` is the adjustment due to possible different employment tracks (e.g., this could be 2.0 for educator track to signal a need for double workload)
  * :math:`R_{adj}` is the adjustment due to any possible service role that entitles the staff to teaching discounts (e.g., this could be 0 or 0.1 to lighten the load of heads of departments).

------------------------------------
The calculation of expected workload
------------------------------------

The software is based on the principle of **fair distribution of workload**. Let :math:`TOT` be the total number of teaching hours assigned by the Department in a given scenario

.. math::

   TOT = \sum_{i=1}^{N} t_{i}

where :math:`t_{i}` is the number of hours for each of the :math:`N` teaching assignments. In the example above, one of these :math:`t_{i}` would be 39. We then define :math:`Dept_{tFTE}`
as the summation of all the :math:`tFTE` of the all the individual lecturers of the Department for that year

.. math::
   Dept_{tFTE} = \sum_{i=1}^{n} tFTE_{i}

where :math:`tFTE_{i}` is the :math:`tFTE` of each inidvidual lecturer of the :math:`n` lecturers in the Department for that year. Under the principle of 
fair distributioin of workload, :math:`TOT` hours should be spread equally among the Department staff. Each unitary :math:`tFTE` is therefore expected 
to teach :math:`E` hours, where 

.. math::
   E = \frac{TOT}{Dept_{tFTE}}

As such, each individual lecturer :math:`i` is expected to teach

.. math::
   E_{i} = E*tFTE_{i}

The number :math:`E_{i}` is calculated and reported in the workload table and labelled as **Expected hours**.




===================================
Accreditation Management
===================================
