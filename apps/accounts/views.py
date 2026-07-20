from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from apps.accounts.forms import (
    RegisterForm, LoginForm, ForgotPasswordForm,
    OTPVerificationForm, ResetPasswordForm, ChangeUsernameForm
)
from apps.accounts.models import OTPRequest

User = get_user_model()


def _rate_limit_check(email):
    recent_count = OTPRequest.objects.filter(
        email=email,
        created_at__gte=timezone.now() - timedelta(minutes=10)
    ).count()
    return recent_count < 3


def _send_otp_email(email, otp):
    try:
        send_mail(
            subject='Your OTP for Password Reset',
            message=f'Your OTP is: {otp}\nThis OTP expires in 5 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )
    except Exception:
        pass


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_account_locked():
                messages.error(request, 'Account temporarily locked due to too many failed attempts. Please try again later.')
                return redirect('login')
            login(request, user)
            user.reset_failed_login()
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            email = request.POST.get('username', '').strip()
            try:
                user_obj = User.objects.get(email=email)
                user_obj.increment_failed_login()
            except User.DoesNotExist:
                pass
            messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@require_http_methods(["GET", "POST"])
@login_required
def change_username_view(request):
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Username changed successfully.')
            return redirect('dashboard')
    else:
        form = ChangeUsernameForm(instance=request.user)
    return render(request, 'auth/change_username.html', {'form': form})


@require_http_methods(["GET", "POST"])
def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, 'Please enter a valid email address.')
                return redirect('forgot_password')

            if not _rate_limit_check(email):
                messages.error(request, 'Too many OTP requests. Please try again later.')
                return redirect('forgot_password')

            user = User.objects.filter(email=email).first()
            if user:
                otp = user.generate_otp()
                _send_otp_email(email, otp)
                OTPRequest.objects.create(
                    email=email,
                    otp=otp,
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                request.session['reset_email'] = email
                messages.success(request, 'OTP sent to your email.')
                return redirect('verify_otp')
            else:
                messages.error(request, 'No account found with this email address.')
    else:
        form = ForgotPasswordForm()
    return render(request, 'auth/forgot_password.html', {'form': form})


@require_http_methods(["GET", "POST"])
def verify_otp_view(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Session expired. Please request a new OTP.')
        return redirect('forgot_password')

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            otp_request = OTPRequest.objects.filter(
                email=email, otp=otp, is_used=False
            ).first()
            if otp_request and otp_request.is_valid():
                otp_request.is_used = True
                otp_request.save()
                request.session['otp_verified'] = True
                messages.success(request, 'OTP verified successfully.')
                return redirect('reset_password')
            else:
                messages.error(request, 'Invalid or expired OTP.')
    else:
        form = OTPVerificationForm()
    return render(request, 'auth/verify_otp.html', {'form': form})


@require_http_methods(["GET", "POST"])
def reset_password_view(request):
    if not request.session.get('otp_verified'):
        messages.error(request, 'Please verify OTP first.')
        return redirect('forgot_password')

    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Session expired. Please try again.')
        return redirect('forgot_password')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.filter(email=email).first()
            if user:
                user.set_password(form.cleaned_data['password'])
                user.clear_otp()
                user.save()
                messages.success(request, 'Password reset successfully. Please login.')
                request.session.pop('reset_email', None)
                request.session.pop('otp_verified', None)
                return redirect('login')
    else:
        form = ResetPasswordForm()
    return render(request, 'auth/reset_password.html', {'form': form})
