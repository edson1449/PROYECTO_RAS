# soporte/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

from usuarios.models import Usuario


def admin_required(view_func):
    """
    Restringe el acceso a la vista solo a usuarios con tipo 'admin'.
    Usa el sistema de sesión que ya tienes (user_id, user_tipo).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Si no hay user_id en sesión, redirigir a login
        if 'user_id' not in request.session:
            messages.error(request, 'Debe iniciar sesión para acceder a esta página.')
            return redirect('login')

        try:
            usuario = Usuario.objects.get(id=request.session['user_id'])
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado. Inicie sesión nuevamente.')
            return redirect('login')

        # Guardar tipo en sesión si aún no está
        if 'user_tipo' not in request.session:
            request.session['user_tipo'] = usuario.tipo

        # Verificar rol
        if usuario.tipo != 'admin':
            messages.error(request, 'No tiene permisos para acceder a esta sección.')
            # Ajusta el redirect según tu proyecto
            return redirect('panel_funcionario')

        return view_func(request, *args, **kwargs)

    return _wrapped_view
