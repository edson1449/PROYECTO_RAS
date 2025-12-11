from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Centro
from .forms import CentroForm

def listar_centros(request):
    centros = Centro.objects.all()
    return render(request, 'centros/listar_centros.html', {'centros': centros})

def crear_centro(request):
    if request.method == 'POST':
        form = CentroForm(request.POST)
        if form.is_valid():
            centro = form.save(commit=False)
            centro.save()
            messages.success(request, 'Centro creado exitosamente.')
            return redirect('centros:listar_centros')
    else:
        form = CentroForm()
    return render(request, 'centros/crear_centro.html', {'form': form})

def editar_centro(request, cod_centro):
    centro = get_object_or_404(Centro, cod_centro=cod_centro)
    if request.method == 'POST':
        form = CentroForm(request.POST, instance=centro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Centro actualizado exitosamente.')
            return redirect('centros:listar_centros')
    else:
        form = CentroForm(instance=centro)
    return render(request, 'centros/editar_centro.html', {'form': form, 'centro': centro})

def eliminar_centro(request, cod_centro):
    centro = get_object_or_404(Centro, cod_centro=cod_centro)
    if request.method == 'POST':
        nombre_centro = centro.nom_centro
        centro.delete()
        messages.success(request, f'Centro "{nombre_centro}" eliminado exitosamente.')
        return redirect('centros:listar_centros')
    return render(request, 'centros/eliminar_centro.html', {'centro': centro})