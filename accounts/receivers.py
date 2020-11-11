#from django.core.signals import request_finished
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

from django.conf import settings


from .models import CustomUser, Invitation, EmailVerification, PasswordResetRequest


@receiver(pre_save)
def lower_email_addresses(sender, instance, **kwargs):
    if isinstance(instance, CustomUser):
        email = getattr(instance, 'email', None)
        if email:
            instance.email = email.lower()


# TODO remove invitations
# @receiver(post_save)
# def send_invitation_email(sender, instance, created, **kwargs):


@receiver(post_save)
def create_verification(sender, instance, created, **kwargs):
    if isinstance(instance, CustomUser):
        if instance.email:
            verifications = EmailVerification.objects.filter(
                user=instance, email=instance.email)
            if not verifications.count():
                create_v = True
            else:
                verified = any([i.verified for i in verifications])
                # create_v = not verified
                create_v = False

            if create_v:
                verification = EmailVerification(
                    user=instance, email=instance.email)
                verification.save()


@receiver(post_save)
def send_verification_email(sender, instance, created, **kwargs):
    if created and isinstance(instance, EmailVerification):
        subject, from_email, to = 'Please confirm your account on Hackergrows', 'noreply@hackergrows.com', instance.email
        text_content = """
Please confirm your email address here:

{site_redirect_uri}{url}

-- 
Hackergrows links products to online discussions.

""".format(url=instance.get_verify_url(), site_redirect_uri=settings.SITE_REDIRECT_URI)
        #html_content = '<p>This is an <strong>important</strong> message.</p>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        #msg.attach_alternative(html_content, "text/html")
        msg.send()


@receiver(post_save)
def send_password_reset_email(sender, instance, created, **kwargs):
    if created and isinstance(instance, PasswordResetRequest):
        subject, from_email, to = 'Reset password for your account on Hackergrows', 'noreply@hackergrows.com', instance.user.email
        text_content = """
Please confirm your email address here:

{site_redirect_uri}{url}

-- 
Hackergrows links products to online discussions.

""".format(url=instance.get_verify_url(), site_redirect_uri=settings.SITE_REDIRECT_URI)
        #html_content = '<p>This is an <strong>important</strong> message.</p>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        #msg.attach_alternative(html_content, "text/html")
        msg.send()
