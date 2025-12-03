from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserPasswordResetView.as_view(), name='password_reset'),
    path('done/', views.UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('confirm/<uidb64>/<token>/', views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('complete/', views.UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]