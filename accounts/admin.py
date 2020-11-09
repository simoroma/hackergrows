from django.contrib import admin

from .models import CustomUser, Invitation, EmailVerification

admin.site.register(CustomUser)
admin.site.register(Invitation)
admin.site.register(EmailVerification)
