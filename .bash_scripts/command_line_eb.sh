cd /var/app/current/
source $(find /var/app/venv/ -name activate)
export $(sudo egrep -v '^#' /opt/elasticbeanstalk/deployment/env | xargs)
# in case run tests
python manage.py shell
# tests
python manage.py test
