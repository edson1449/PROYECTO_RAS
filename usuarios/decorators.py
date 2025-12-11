from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def login_required(view_func):
    """Decorador para verificar que el usuario esté autenticado"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, 'Debes iniciar sesión')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorador para verificar que el usuario sea administrador"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, 'Debes iniciar sesión')
            return redirect('login')
        
        if request.session.get('user_type') != 'admin':
            messages.error(request, 'No tienes permiso para acceder a esta sección')
            return redirect('panel_funcionario')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def funcionario_required(view_func):
    """Decorador para verificar que el usuario sea funcionario"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, 'Debes iniciar sesión')
            return redirect('login')
        
        if request.session.get('user_type') != 'funcionario':
            messages.error(request, 'Acceso denegado')
            return redirect('panel_admin')
        
        return view_func(request, *args, **kwargs)
    return wrapper
