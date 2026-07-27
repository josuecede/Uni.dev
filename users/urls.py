from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomSetPasswordForm

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('set-theme/', views.set_theme, name='set_theme'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('password-reset/', views.password_reset_code_view, name='password_reset'),
    path('password-reset/verify/', views.password_reset_verify_view, name='password_reset_code_verify'),
    path('password-reset/resend/', views.password_reset_resend_code, name='password_reset_resend'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(form_class=CustomSetPasswordForm), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
