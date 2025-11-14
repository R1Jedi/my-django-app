from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


@shared_task
def send_verification_email_async(user_id, code, user_email, username):
    try:
        link = reverse('users:email_verification', kwargs={
            'email': user_email,
            'code': code
        })
        verification_link = f'{settings.DOMAIN_NAME}{link}'

        subject = f'Подтверждение учетной записи для {username}'
        message = f'''
        Здравствуйте, {username}!

        Для подтверждения вашей учетной записи перейдите по ссылке:
        {verification_link}

        Ссылка действительна в течение 48 часов.
        '''
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user_email],
            fail_silently=False,
        )

        return f'Email верификации отправлен на {user_email}'

    except Exception as e:
        return f'Ошибка отправки email: {str(e)}'
