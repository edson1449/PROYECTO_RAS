from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Ambiente
from .forms import AmbienteForm
from usuarios.models import Usuario
from usuarios.decorators import login_required, admin_required


def listar_ambientes(request):
    """Lista todos los ambientes disponibles"""
    
    
    if 'user_id' not in request.session or 'user_name' not in request.session:
        messages.error(request, 'Debe iniciar sesión para acceder a esta página')
        return redirect('/login/?next=/ambientes/')
    
    try:
        usuario_id = request.session['user_id']
        usuario_actual = Usuario.objects.get(id=usuario_id)
        
        
        if 'user_tipo' not in request.session:
            request.session['user_tipo'] = usuario_actual.tipo
            request.session.modified = True  
        
        
        ambientes = Ambiente.objects.all().order_by('nom_amb')
        
        context = {
            'ambientes': ambientes,
            'user_tipo': usuario_actual.tipo,
        }
        
        return render(request, 'ambientes/listar_ambientes.html', context)
    
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('/login/')
    
    except Exception as e:
        print(f"Error en listar_ambientes: {e}")
        messages.error(request, 'Error al cargar los ambientes.')
        return render(request, 'ambientes/listar_ambientes.html', {'ambientes': []})

@login_required
@admin_required
def crear_ambiente(request):
    """Crear ambiente - Solo Admin"""
    if request.method == 'POST':
        form = AmbienteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ambiente creado exitosamente.')
            return redirect('ambientes:listar_ambientes')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = AmbienteForm()
    
    return render(request, 'ambientes/crear_ambiente.html', {'form': form})


@login_required
@admin_required
def editar_ambiente(request, cod_amb):
    
    ambiente = get_object_or_404(Ambiente, cod_amb=cod_amb)
    
    if request.method == 'POST':
        form = AmbienteForm(request.POST, request.FILES, instance=ambiente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ambiente actualizado exitosamente.')
            return redirect('ambientes:listar_ambientes')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = AmbienteForm(instance=ambiente)
    
    return render(request, 'ambientes/editar_ambiente.html', {'form': form, 'ambiente': ambiente})


@login_required
@admin_required
def eliminar_ambiente(request, cod_amb):
    
    ambiente = get_object_or_404(Ambiente, cod_amb=cod_amb)
    
    if request.method == 'POST':
        ambiente.delete()
        messages.success(request, 'Ambiente eliminado exitosamente.')
        return redirect('ambientes:listar_ambientes')
    
    return render(request, 'ambientes/eliminar_ambiente.html', {'ambiente': ambiente})

@login_required
def listar_ambientes_funcionario(request):
    
    try:
        ambientes = Ambiente.objects.filter(estado_amb='disponible').order_by('nom_amb')
        
        usuario_id = request.session['user_id']
        usuario_actual = Usuario.objects.get(id=usuario_id)
        
        if 'user_tipo' not in request.session:
            request.session['user_tipo'] = usuario_actual.tipo
            request.session['user_name'] = usuario_actual.nombre
        
        context = {
            'ambientes': ambientes,
        }
        
        return render(request, 'ambientes/listar_ambientes.html', context)
        
    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, 'Error al cargar los ambientes')
        return redirect('panel_funcionario')
