from django.urls import path
from apps.accounts import views as accounts_views

urlpatterns = [
    path('register/', accounts_views.register_view, name='register'),
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('forgot-password/', accounts_views.forgot_password_view, name='forgot_password'),
    path('verify-otp/', accounts_views.verify_otp_view, name='verify_otp'),
    path('reset-password/', accounts_views.reset_password_view, name='reset_password'),
    path('change-username/', accounts_views.change_username_view, name='change_username'),
]
