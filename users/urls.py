from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('registration/', views.UserRegistrationView.as_view(), name='registration'),
    path('profile/<int:pk>', login_required(views.UserProfileView.as_view()), name='profile'),
    path('logout/', LogoutView.as_view(http_method_names=["post", "get", "options"]), name='logout'),
    path('verify/<str:email>/<uuid:code>/', views.EmailVerificationView.as_view(), name='email_verification'),
    path('password-reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views.UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
