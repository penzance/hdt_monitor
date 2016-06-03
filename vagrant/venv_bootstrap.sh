#!/bin/bash
# Set up virtualenv and migrate project
export HOME=/home/vagrant
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv -a /home/vagrant/hdt_monitor -r /home/vagrant/hdt_monitor/hdt_monitor/requirements/local.txt hdt_monitor 
workon hdt_monitor
python manage.py migrate
