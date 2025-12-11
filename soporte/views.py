from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from usuarios.decorators import login_required, admin_required
from usuarios.models import Usuario

from .models import Soporte, MensajeSoporte
from .forms import SoporteForm, ResponderSoporteForm, MensajeSoporteForm


@login_required
@admin_required
def listar_soportes(request):
    try:
        soportes = Soporte.objects.all().order_by('-creado_en')

        usuario_id = request.session['user_id']
        usuario_actual = Usuario.objects.get(id=usuario_id)

        if 'user_tipo' not in request.session:
            request.session['user_tipo'] = usuario_actual.tipo
            request.session['user_name'] = usuario_actual.nombre

        context = {
            'soportes': soportes,
        }

        return render(request, 'listar_soportes.html', context)

    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, 'Error al cargar las solicitudes de soporte.')
        return redirect('panel_admin')


@login_required
def crear_soporte(request):
    usuario_id = request.session.get('user_id')
    usuario_actual = Usuario.objects.get(id=usuario_id)

    if request.method == 'POST':
        form = SoporteForm(request.POST, funcionario=usuario_actual)
        if form.is_valid():
            soporte = form.save(commit=False)
            soporte.usuario = usuario_actual
            soporte.save()
            messages.success(request, 'Solicitud de soporte creada exitosamente.')
            return redirect('soporte:listar_mis_soportes')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = SoporteForm(funcionario=usuario_actual)

    return render(request, 'crear_soporte.html', {'form': form})


@login_required
def listar_mis_soportes(request):
    try:
        usuario_id = request.session['user_id']
        usuario_actual = Usuario.objects.get(id=usuario_id)

        if 'user_tipo' not in request.session:
            request.session['user_tipo'] = usuario_actual.tipo
            request.session['user_name'] = usuario_actual.nombre

        soportes = Soporte.objects.filter(usuario=usuario_actual).order_by('-creado_en')

        context = {
            'soportes': soportes,
        }

        return render(request, 'listar_mis_soportes.html', context)

    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, 'Error al cargar tus solicitudes de soporte.')
        return redirect('panel_funcionario')


@login_required
@admin_required
def responder_soporte(request, soporte_id):
    soporte = get_object_or_404(Soporte, id=soporte_id)

    if request.method == 'POST':
        form = ResponderSoporteForm(request.POST, instance=soporte)
        if form.is_valid():
            form.save()
            messages.success(request, 'Soporte actualizado exitosamente.')
            return redirect('soporte:listar_soportes')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ResponderSoporteForm(instance=soporte)

    return render(request, 'responder_soporte.html', {'form': form, 'soporte': soporte})


@login_required
@admin_required
def eliminar_soporte(request, soporte_id):
    soporte = get_object_or_404(Soporte, id=soporte_id)

    if request.method == 'POST':
        soporte.delete()
        messages.success(request, 'Soporte eliminado exitosamente.')
        return redirect('soporte:listar_soportes')

    return render(request, 'eliminar_soporte.html', {'soporte': soporte})


@login_required
def detalle_soporte(request, soporte_id):
    soporte = get_object_or_404(Soporte, id=soporte_id)
    usuario_id = request.session['user_id']
    usuario_actual = Usuario.objects.get(id=usuario_id)

    if usuario_actual != soporte.usuario and request.session.get('user_tipo') != 'admin':
        messages.error(request, 'No tiene permiso para ver este soporte.')
        return redirect('soporte:listar_mis_soportes')

    mensajes = soporte.mensajes.select_related('usuario').all()
    es_admin = request.session.get('user_tipo') == 'admin'

    # ✅ CAMBIO 1: QUITAR 'and es_admin' para que TODOS puedan enviar mensajes
    if request.method == 'POST':
        msg_form = MensajeSoporteForm(request.POST)

        if msg_form.is_valid():
            texto = msg_form.cleaned_data.get('texto')

            # Guardar mensaje si hay texto
            if texto:
                mensaje = msg_form.save(commit=False)
                mensaje.soporte = soporte
                mensaje.usuario = usuario_actual
                mensaje.save()

            # ✅ CAMBIO 2: Solo admins actualizan estado
            if es_admin:
                nuevo_estado = request.POST.get('estado')
                if nuevo_estado and nuevo_estado in dict(Soporte.ESTADO_CHOICES):
                    soporte.estado = nuevo_estado
                    soporte.save(update_fields=['estado'])
                messages.success(request, 'Mensaje enviado y estado actualizado.')
            else:
                messages.success(request, 'Mensaje enviado correctamente.')

            return redirect('soporte:detalle_soporte', soporte_id=soporte.id)
        # ✅ CAMBIO 3: msg_form SIEMPRE se pasa, incluso con errores
        # No hace falta else aquí
    else:
        msg_form = MensajeSoporteForm()

    # Form solo para pintar el select de estado (no se valida en el POST)
    resp_form = ResponderSoporteForm(instance=soporte) if es_admin else None

    context = {
        'soporte': soporte,
        'mensajes': mensajes,
        'msg_form': msg_form,  # ✅ SIEMPRE presente
        'resp_form': resp_form,
        'es_admin': es_admin,
    }
    return render(request, 'detalle_soporte.html', context)
