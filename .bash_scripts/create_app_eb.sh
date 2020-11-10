# First activate conda
conda activate django-p3.7
# Create application
eb init -p python-3.7 django-tutorial
# create environment
eb create django-env
# check enviroment
eb status
# associate a git branch to an enviroment
eb use django-env
# deploy git staged files
eb deploy --staged
# terminate an enviroment
eb terminate
# abort if there is a pending operation
eb abort
# ssh
eb shh