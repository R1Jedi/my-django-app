import uuid
from datetime import timedelta

from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import CreateView, TemplateView, UpdateView

from common.views import TitleMixin
from users.forms import UserLoginForm, UserProfileForm, UserRegistrationForm
from users.models import EmailVerification, User


class UserLoginView(TitleMixin, LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm
    title = "Store - Авторизация"


class UserRegistrationView(TitleMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    success_message = "Вы успешно зарегестрировались!"
    title = "Store - Регистрация"

    def form_valid(self, form):
        response = super().form_valid(form)

        expiration = now() + timedelta(hours=48)
        email_verification = EmailVerification.objects.create(
            user=self.object,
            code=uuid.uuid4(),
            expiration=expiration
        )

        email_verification.send_verification_email_async()

        return response


class UserProfileView(TitleMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    title = "Store - Профиль"

    def get_success_url(self):
        return reverse_lazy('users:profile', args=(self.object.id,))


class EmailVerificationView(TitleMixin, TemplateView):
    title = "Store - Потверждение электронной почты"
    template_name = 'users/email_verification.html'

    def get(self, request, *args, **kwargs):
        code = kwargs['code']
        user = User.objects.get(email=kwargs['email'])
        email_verifications = EmailVerification.objects.filter(user=user, code=code)
        if email_verifications.exists() and not email_verifications.first().is_expired():
            user.is_verified_email = True
            user.save()
            return super(EmailVerificationView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('users:index'))


class UserPasswordResetView(TitleMixin, SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')
    success_message = "Письмо с инструкциями по восстановлению пароля отправлено на ваш email"
    title = "Store - Восстановление пароля"


class UserPasswordResetDoneView(TitleMixin, PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'
    title = 'Store - Письмо отправлено'


class UserPasswordResetConfirmView(TitleMixin, PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')
    title = "Store - Ввод нового пароля"


class UserPasswordResetCompleteView(TitleMixin, PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'
    title = "Store - Пароль изменен"

