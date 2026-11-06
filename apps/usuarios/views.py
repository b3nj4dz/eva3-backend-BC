from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.cotizaciones.models import SolicitudCotizacion
from .forms import RegistroForm, LoginForm


def registro_usuario(request):
    if request.user.is_authenticated:
        return redirect('inventario:lista')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido {user.first_name}! Tu cuenta corporativa ha sido registrada.")
            return redirect('inventario:lista')
        else:
            messages.error(request, "Por favor corrige los errores indicados en el formulario de registro.")
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})


def login_usuario(request):
    if request.user.is_authenticated:
        return redirect('inventario:lista')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "¡Sesión iniciada correctamente!")
            return redirect(request.POST.get('next') or 'inventario:lista')
        else:
            messages.error(request, "Usuario, correo o contraseña incorrectos. Revisa tus datos e inténtalo de nuevo.")
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form, 'next': request.GET.get('next', 'inventario:lista')})


def logout_usuario(request):
    logout(request)
    messages.info(request, "Has cerrado sesión de forma segura.")
    return redirect('core:inicio')


@login_required
def perfil_usuario(request):
    historial = SolicitudCotizacion.objects.filter(usuario=request.user).prefetch_related('items')
    return render(request, 'usuarios/perfil.html', {
        'usuario': request.user,
        'historial': historial
    })