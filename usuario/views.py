from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from usuarios.decorators import login_required, admin_required
from .models import Usuario
from .forms import RegistroUsuarioForm


@login_required
@admin_required
def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuario/listar_usuarios.html', {'usuarios': usuarios})


@login_required
@admin_required
def crear_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            try:
                usuario = form.save()
                messages.success(request, f'Usuario {usuario.nombre} creado exitosamente.')
                return redirect('listar_usuarios')
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label if field in form.fields else field}: {error}')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'usuario/crear_usuario.html', {'form': form})


@login_required
@admin_required
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Usuario actualizado exitosamente.')
                return redirect('listar_usuarios')
            except Exception as e:
                messages.error(request, f'Error al actualizar el usuario: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label if field in form.fields else field}: {error}')
    else:
        form = RegistroUsuarioForm(instance=usuario)
    
    return render(request, 'usuario/editar_usuario.html', {'form': form, 'usuario': usuario})


@login_required
@admin_required
def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    
    if request.method == 'POST':
        nombre_usuario = usuario.nombre
        usuario.delete()
        messages.success(request, f'Usuario "{nombre_usuario}" eliminado exitosamente.')
        return redirect('listar_usuarios')
    
    return render(request, 'usuario/eliminar_usuario.html', {'usuario': usuario})
