import random
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from .forms import CustomUserCreationForm, UserProfileForm
from .models import CustomUser



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            if not user.is_admin() and not user.is_manager():
                messages.error(request, 'Este panel es solo para administradores.')
                return render(request, 'pages/examples/login.html')
            login(request, user)
            messages.success(request, f'Bienvenido {user.username}.')
            return redirect(request.GET.get('next', 'dashboard:home'))
        try:
            u = CustomUser.objects.get(username=username)
            if not u.is_active:
                messages.error(request, 'Debes verificar tu correo primero. Revisa tu bandeja de entrada.')
                return render(request, 'pages/examples/login.html')
        except CustomUser.DoesNotExist:
            pass
        messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'pages/examples/login.html')


def logout_view(request):
    is_admin = request.user.is_authenticated and (request.user.is_admin() or request.user.is_staff)
    logout(request)
    messages.success(request, 'Sesión cerrada.')
    return redirect('login' if is_admin else '/')


def password_reset_code_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        user = CustomUser.objects.filter(email__iexact=email).first()
        if user:
            code = f'{random.randint(100000, 999999)}'
            user.reset_code = code
            user.reset_code_expiry = timezone.now() + timezone.timedelta(minutes=15)
            user.save()
            subject = 'Código de recuperación - GameStore'
            html_message = render_to_string('registration/password_reset_email.html', {'code': code})
            send_mail(subject, '', None, [email], html_message=html_message, fail_silently=False)
        messages.success(request, 'Si el correo existe, recibirás un código de verificación.')
        request.session['reset_email'] = email
        return redirect('password_reset_code_verify')
    return render(request, 'registration/password_reset_form.html')


def password_reset_verify_view(request):
    email = request.session.get('reset_email', '')
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        users = CustomUser.objects.filter(reset_code=code, reset_code_expiry__gte=timezone.now())
        user = users.first()
        if user:
            user.reset_code = None
            user.reset_code_expiry = None
            user.save()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            return redirect('password_reset_confirm', uidb64=uidb64, token=token)
        messages.error(request, 'Código inválido o expirado.')
    return render(request, 'registration/password_reset_code.html', {'email': email})


def password_reset_resend_code(request):
    email = request.session.get('reset_email', '')
    if not email:
        messages.error(request, 'Sesión expirada. Solicita el código nuevamente.')
        return redirect('password_reset')
    user = CustomUser.objects.filter(email__iexact=email).first()
    if not user:
        messages.error(request, 'Correo no encontrado.')
        return redirect('password_reset')
    code = f'{random.randint(100000, 999999)}'
    user.reset_code = code
    user.reset_code_expiry = timezone.now() + timezone.timedelta(minutes=15)
    user.save()
    subject = 'Código de recuperación - GameStore'
    html_message = render_to_string('registration/password_reset_email.html', {'code': code})
    send_mail(subject, '', None, [email], html_message=html_message, fail_silently=False)
    messages.success(request, 'Código reenviado a tu correo.')
    return redirect('password_reset_code_verify')


@login_required
def set_theme(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        theme = request.POST.get('theme', 'dark')
        if theme in ('dark', 'light'):
            request.user.theme = theme
            request.user.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


@login_required
def profile_view(request):
    base_tpl = 'starter.html' if request.user.is_staff else 'base_cliente.html'
    return render(request, 'users/profile.html', {'user': request.user, 'profile_base': base_tpl})


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    base_tpl = 'starter.html' if request.user.is_staff else 'base_cliente.html'
    return render(request, 'users/profile_edit.html', {'form': form, 'profile_base': base_tpl})
