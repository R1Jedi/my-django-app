from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

from .tasks import send_verification_email_async


class User(AbstractUser):
    image = models.ImageField(upload_to='users_images', null=True, blank=True)
    is_verified_email = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    def __str__(self):
        return f"EmailVerification object for {self.user.email}"

    def send_verification_email_async(self):
        send_verification_email_async.delay(
            user_id=self.user.id,
            code=str(self.code),
            user_email=self.user.email,
            username=self.user.username
        )

    def is_expired(self):
        return True if now() >= self.expiration else False
