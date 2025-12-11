from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Coordinacion
from .forms import CoordinacionForm

def listar_coordinaciones(request):
    if 'user_id' not in request.session or 'user_name' not in request.session:
        messages.error(request, 'Debe iniciar sesión para acceder a esta página')
        return redirect('/login/?next=/coordinaciones/')
    
    try:
        coordinaciones = Coordinacion.objects.all()
        return render(request, 'coordinaciones/listar_coordinaciones.html', {'coordinaciones': coordinaciones})
    except Exception as e:
        messages.error(request, f'Error al cargar las coordinaciones: {str(e)}')
        return render(request, 'coordinaciones/listar_coordinaciones.html', {'coordinaciones': []})

def crear_coordinacion(request):
    if request.method == 'POST':
        form = CoordinacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coordinación creada exitosamente.')
            return redirect('coordinaciones:listar_coordinaciones')
    else:
        form = CoordinacionForm()
    return render(request, 'coordinaciones/crear_coordinacion.html', {'form': form})

def editar_coordinacion(request, cod_coordinacion):
    coordinacion = get_object_or_404(Coordinacion, cod_coordinacion=cod_coordinacion)
    if request.method == 'POST':
        form = CoordinacionForm(request.POST, instance=coordinacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coordinación actualizada exitosamente.')
            return redirect('coordinaciones:listar_coordinaciones')
    else:
        form = CoordinacionForm(instance=coordinacion)
    return render(request, 'coordinaciones/editar_coordinacion.html', {'form': form, 'coordinacion': coordinacion})

def eliminar_coordinacion(request, cod_coordinacion):
    coordinacion = get_object_or_404(Coordinacion, cod_coordinacion=cod_coordinacion)
    if request.method == 'POST':
        nombre_coordinacion = coordinacion.nom_coordinacion
        coordinacion.delete()
        messages.success(request, f'Coordinación "{nombre_coordinacion}" eliminada exitosamente.')
        return redirect('coordinaciones:listar_coordinaciones')
    return render(request, 'coordinaciones/eliminar_coordinacion.html', {'coordinacion': coordinacion})