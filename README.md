**This project is no longer used, as of June 2021. Cf [AT+VPAL discussion in TLT Slack on June 15, 2021](https://tlt.slack.com/archives/C0213GV2F33/p1623769360002400).**

django-project-template
=======================

Use this template to create a new Django project like this:

django-admin.py startproject _projectname_ --template=https://github.com/Harvard-University-iCommons/django-project-template/archive/stable/v1.9.x.zip --extension=py,pp,sh,example

## Customizations

* For production deployments, static assets from all app-level static directories are collected into a project level `http_static` directory, which is ignored by git.
* Added `settings` and `requirements` directories under the project subdirectory.
* Default to using a postgres db (installed on local VM via `vagrant up`) with
username, db name, and password defaulting to the project name
* Default to including a redis cache (installed on local VM via `vagrant up`)
