python manage.py shell << EOF
from accounts.models import EmailVerification
for e in EmailVerification.objects.filter(verified=True): 
  print(e.email)
exit()
EOF