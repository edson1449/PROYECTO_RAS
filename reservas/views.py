from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_http_methods, require_POST
from django.shortcuts import render, redirect
from .models import Reserva
from .models import Reserva, Ambiente
from .forms import ReservaForm, ComentarioFuncionarioForm, EstadoReservaForm, ComentarioAdminForm
from usuarios.models import Usuario
import json
from django.core.mail import send_mail
from django.db import transaction
from django.conf import settings


def listar_reservas(request):
    if 'user_id' not in request.session or 'user_name' not in request.session:
        messages.error(request, 'Debe iniciar sesión para acceder a esta página')
        return redirect('/login/?next=/reservas/')
    
    try:
        usuario_id = request.session['user_id']
        usuario_actual = Usuario.objects.get(id=usuario_id)
        rol_usuario = usuario_actual.tipo
        
        if rol_usuario == 'funcionario':
            reservas = Reserva.objects.filter(
                cod_usuario_fk=usuario_actual
            ).order_by('-fecha', '-hora_ini')
        else:
            reservas = Reserva.objects.all().order_by('-fecha', '-hora_ini')
        
        context = {
            'reservas': reservas,
            'rol_usuario': rol_usuario
        }
        return render(request, 'reservas/listar_reservas.html', context)
    
    except Exception as e:
        print(f"Error en listar_reservas: {e}")
        messages.error(request, 'Error al cargar las reservas.')
        return render(request, 'reservas/listar_reservas.html', {'reservas': [], 'rol_usuario': None})


def obtener_reservas_json(request):
    """API endpoint para obtener las reservas en formato JSON para FullCalendar"""
    if 'user_id' not in request.session or 'user_name' not in request.session:
        return JsonResponse({'error': 'No autorizado'}, status=401)
    
    try:
        usuario_id = request.session['user_id']
        usuario_actual = Usuario.objects.get(id=usuario_id)
        rol_usuario = usuario_actual.tipo
        
        if rol_usuario == 'funcionario':
            reservas = Reserva.objects.filter(
                cod_usuario_fk=usuario_actual
            ).select_related('cod_ambiente_fk', 'cod_usuario_fk')
        else:
            reservas = Reserva.objects.all().select_related('cod_ambiente_fk', 'cod_usuario_fk')
        
        eventos = []
        for reserva in reservas:
            evento = {
                'id': reserva.cod_reserva,
                'title': reserva.titulo_reserva,
                'start': f"{reserva.fecha}T{reserva.hora_ini}",
                'end': f"{reserva.fecha}T{reserva.hora_fin}",
                'estado': reserva.estado,
                'estadoDisplay': reserva.get_estado_display(),
                'tipo': reserva.get_tipo_reserva_display(),
                'tipoRaw': reserva.tipo_reserva,
                'ambiente': reserva.cod_ambiente_fk.nom_amb,
                'motivo': reserva.motivo,
                'numPersonas': reserva.num_personas,
                'usuario': f"{reserva.cod_usuario_fk.nom_usuario} {reserva.cod_usuario_fk.ape_usuario}",
                'codigo': reserva.cod_reserva,
                'className': f'estado-{reserva.estado}'
            }
            eventos.append(evento)
        
        print(f"API: Enviando {len(eventos)} reservas para calendario")
        return JsonResponse(eventos, safe=False)
    
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        print(f"ERROR en obtener_reservas_json: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    
def _render_error_response(
    request,
    ambientes,
    funcionarios,
    reservas_data,
    usuario_actual,
    step='1',
    num_personas=None,
    cod_ambiente_fk_id=None,
    fecha=None,
    hora_ini=None,
    hora_fin=None,
    titulo_reserva=None,
    tipo_reserva=None,
    motivo=None,
    usuario_asignado_id=None,
):
    return render(request, 'reservas/crear_reserva.html', {
        'ambientes': ambientes,
        'funcionarios': funcionarios,
        'es_administrador': usuario_actual.tipo == 'admin' if usuario_actual else False,
        'reservas_json': json.dumps(reservas_data),
        'rol_usuario': usuario_actual.tipo if usuario_actual else 'funcionario',
        'step_error': step,
        'num_personas_error': num_personas,
        'form_cod_ambiente_fk_id': cod_ambiente_fk_id,
        'form_fecha': fecha,
        'form_hora_ini': hora_ini,
        'form_hora_fin': hora_fin,
        'form_titulo_reserva': titulo_reserva,
        'form_tipo_reserva': tipo_reserva,
        'form_motivo': motivo,
        'form_usuario_asignado_id': usuario_asignado_id,
    })


def crear_reserva(request):
    if 'user_id' not in request.session or 'user_name' not in request.session:
        messages.error(request, 'Debe iniciar sesión para acceder a esta página')
        return redirect('/login/?next=/reservas/crear/')

    ambientes = []
    funcionarios = []
    reservas_data = []
    usuario_actual = None

    try:
        ambientes = Ambiente.objects.filter(estado_amb='disponible').order_by('nom_amb')

        usuario_id = request.session['user_id']
        usuario_actual = Usuario.objects.get(id=usuario_id)

        if 'user_tipo' not in request.session:
            request.session['user_tipo'] = usuario_actual.tipo

        if usuario_actual.tipo == 'admin':
            funcionarios = Usuario.objects.filter(tipo='funcionario').order_by('nombre')

        reservas_existentes = Reserva.objects.select_related(
            'cod_ambiente_fk',
            'cod_usuario_fk'
        ).filter(
            estado__in=['aprobada', 'completada', 'rechazada', 'cancelada']
        ).order_by('fecha', 'hora_ini')

        for reserva in reservas_existentes:
            reservas_data.append({
                'id': reserva.cod_reserva,
                'titulo_reserva': reserva.titulo_reserva,
                'fecha': reserva.fecha.strftime('%Y-%m-%d'),
                'hora_ini': reserva.hora_ini.strftime('%H:%M'),
                'hora_fin': reserva.hora_fin.strftime('%H:%M'),
                'ambiente': reserva.cod_ambiente_fk.nom_amb,
                'ambiente_id': reserva.cod_ambiente_fk.cod_amb,
                'estado': reserva.estado,
                'usuario': reserva.cod_usuario_fk.nombre,
            })

    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado. Por favor, inicie sesión nuevamente.')
        return redirect('login')

    except Exception as e:
        messages.error(request, f'Error al cargar los datos: {str(e)}')
        return render(request, 'reservas/crear_reserva.html', {
            'ambientes': [],
            'funcionarios': [],
            'es_administrador': False,
            'reservas_json': '[]',
            'rol_usuario': 'funcionario',
        })

    if request.method == 'POST':
        try:
            cod_ambiente_fk_id = request.POST.get('cod_ambiente_fk')
            fecha = request.POST.get('fecha')
            hora_ini = request.POST.get('hora_ini')
            hora_fin = request.POST.get('hora_fin')
            titulo_reserva = request.POST.get('titulo_reserva')
            tipo_reserva = request.POST.get('tipo_reserva')
            num_personas = request.POST.get('num_personas')
            motivo = request.POST.get('motivo')

            if usuario_actual.tipo == 'admin':
                usuario_asignado_id = request.POST.get('usuario_asignado')
                if usuario_asignado_id:
                    try:
                        usuario_reserva = Usuario.objects.get(
                            id=usuario_asignado_id,
                            tipo='funcionario',
                        )
                    except Usuario.DoesNotExist:
                        messages.error(request, 'El funcionario seleccionado no existe.')
                        return _render_error_response(
                            request, ambientes, funcionarios, reservas_data, usuario_actual,
                            step='3',
                            num_personas=num_personas,
                            cod_ambiente_fk_id=cod_ambiente_fk_id,
                            fecha=fecha,
                            hora_ini=hora_ini,
                            hora_fin=hora_fin,
                            titulo_reserva=titulo_reserva,
                            tipo_reserva=tipo_reserva,
                            motivo=motivo,
                            usuario_asignado_id=usuario_asignado_id,
                        )
                else:
                    messages.error(request, 'Debe seleccionar un funcionario para la reserva.')
                    return _render_error_response(
                        request, ambientes, funcionarios, reservas_data, usuario_actual,
                        step='3',
                        num_personas=num_personas,
                        cod_ambiente_fk_id=cod_ambiente_fk_id,
                        fecha=fecha,
                        hora_ini=hora_ini,
                        hora_fin=hora_fin,
                        titulo_reserva=titulo_reserva,
                        tipo_reserva=tipo_reserva,
                        motivo=motivo,
                    )
            else:
                usuario_reserva = usuario_actual
                usuario_asignado_id = None

            if not all([
                cod_ambiente_fk_id,
                fecha,
                hora_ini,
                hora_fin,
                titulo_reserva,
                tipo_reserva,
                num_personas,
                motivo,
            ]):
                messages.error(request, 'Todos los campos son requeridos.')
                return _render_error_response(
                    request, ambientes, funcionarios, reservas_data, usuario_actual,
                    step='3',
                    num_personas=num_personas,
                    cod_ambiente_fk_id=cod_ambiente_fk_id,
                    fecha=fecha,
                    hora_ini=hora_ini,
                    hora_fin=hora_fin,
                    titulo_reserva=titulo_reserva,
                    tipo_reserva=tipo_reserva,
                    motivo=motivo,
                    usuario_asignado_id=usuario_asignado_id,
                )

            try:
                ambiente_seleccionado = Ambiente.objects.get(cod_amb=cod_ambiente_fk_id)
                num_personas_int = int(num_personas)

                if num_personas_int <= 0:
                    messages.error(request, 'El número de personas debe ser mayor a 0.')
                    return _render_error_response(
                        request, ambientes, funcionarios, reservas_data, usuario_actual,
                        step='3',
                        num_personas=num_personas,
                        cod_ambiente_fk_id=cod_ambiente_fk_id,
                        fecha=fecha,
                        hora_ini=hora_ini,
                        hora_fin=hora_fin,
                        titulo_reserva=titulo_reserva,
                        tipo_reserva=tipo_reserva,
                        motivo=motivo,
                        usuario_asignado_id=usuario_asignado_id,
                    )

                if num_personas_int > ambiente_seleccionado.capacidad_amb:
                    messages.error(
                        request,
                        f'El número de personas ({num_personas_int}) excede la capacidad '
                        f'del ambiente "{ambiente_seleccionado.nom_amb}" '
                        f'(max {ambiente_seleccionado.capacidad_amb}).',
                    )
                    return _render_error_response(
                        request, ambientes, funcionarios, reservas_data, usuario_actual,
                        step='3',
                        num_personas=num_personas,
                        cod_ambiente_fk_id=cod_ambiente_fk_id,
                        fecha=fecha,
                        hora_ini=hora_ini,
                        hora_fin=hora_fin,
                        titulo_reserva=titulo_reserva,
                        tipo_reserva=tipo_reserva,
                        motivo=motivo,
                        usuario_asignado_id=usuario_asignado_id,
                    )

            except Ambiente.DoesNotExist:
                messages.error(request, 'El ambiente seleccionado no existe.')
                return _render_error_response(
                    request, ambientes, funcionarios, reservas_data, usuario_actual,
                    step='2',
                    num_personas=num_personas,
                    cod_ambiente_fk_id=cod_ambiente_fk_id,
                    fecha=fecha,
                    hora_ini=hora_ini,
                    hora_fin=hora_fin,
                    titulo_reserva=titulo_reserva,
                    tipo_reserva=tipo_reserva,
                    motivo=motivo,
                    usuario_asignado_id=usuario_asignado_id,
                )

            except ValueError:
                messages.error(request, 'El número de personas debe ser numérico.')
                return _render_error_response(
                    request, ambientes, funcionarios, reservas_data, usuario_actual,
                    step='3',
                    num_personas=num_personas,
                    cod_ambiente_fk_id=cod_ambiente_fk_id,
                    fecha=fecha,
                    hora_ini=hora_ini,
                    hora_fin=hora_fin,
                    titulo_reserva=titulo_reserva,
                    tipo_reserva=tipo_reserva,
                    motivo=motivo,
                    usuario_asignado_id=usuario_asignado_id,
                )

            reserva_existente = Reserva.objects.filter(
                cod_ambiente_fk_id=cod_ambiente_fk_id,
                fecha=fecha,
                hora_ini__lt=hora_fin,
                hora_fin__gt=hora_ini,
                estado__in=['aprobada', 'completada', 'rechazada', 'cancelada'],
            ).exists()

            if reserva_existente:
                messages.error(
                    request,
                    f'Ya existe una reserva en este horario para el ambiente '
                    f'"{ambiente_seleccionado.nom_amb}". Por favor, seleccione '
                    f'otro horario o ambiente.',
                )
                return _render_error_response(
                    request, ambientes, funcionarios, reservas_data, usuario_actual,
                    step='2',
                    num_personas=num_personas,
                    cod_ambiente_fk_id=cod_ambiente_fk_id,
                    fecha=fecha,
                    hora_ini=hora_ini,
                    hora_fin=hora_fin,
                    titulo_reserva=titulo_reserva,
                    tipo_reserva=tipo_reserva,
                    motivo=motivo,
                    usuario_asignado_id=usuario_asignado_id,
                )

            with transaction.atomic():
                reserva = Reserva(
                    cod_ambiente_fk=ambiente_seleccionado,
                    fecha=fecha,
                    hora_ini=hora_ini,
                    hora_fin=hora_fin,
                    titulo_reserva=titulo_reserva,
                    tipo_reserva=tipo_reserva,
                    num_personas=num_personas_int,
                    motivo=motivo,
                    estado='pendiente',
                    cod_usuario_fk=usuario_reserva,
                )
                reserva.save()

            messages.success(
                request,
                f'Reserva creada exitosamente: "{titulo_reserva}" para '
                f'{num_personas_int} personas en {ambiente_seleccionado.nom_amb}. '
                f'Estado: Pendiente de aprobación.',
            )
            return redirect('reservas:listar_reservas')

        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
            return redirect('login')

        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error al crear la reserva: {str(e)}')
            return _render_error_response(
                request, ambientes, funcionarios, reservas_data, usuario_actual,
                step='3',
                num_personas=request.POST.get('num_personas'),
                cod_ambiente_fk_id=request.POST.get('cod_ambiente_fk'),
                fecha=request.POST.get('fecha'),
                hora_ini=request.POST.get('hora_ini'),
                hora_fin=request.POST.get('hora_fin'),
                titulo_reserva=request.POST.get('titulo_reserva'),
                tipo_reserva=request.POST.get('tipo_reserva'),
                motivo=request.POST.get('motivo'),
                usuario_asignado_id=request.POST.get('usuario_asignado'),
            )

    es_administrador = usuario_actual and usuario_actual.tipo == 'admin'

    context = {
        'ambientes': ambientes,
        'funcionarios': funcionarios,
        'es_administrador': es_administrador,
        'reservas_json': json.dumps(reservas_data),
        'rol_usuario': usuario_actual.tipo if usuario_actual else 'funcionario',
        'step_error': '1',
        'num_personas_error': None,
        'form_cod_ambiente_fk_id': None,
        'form_fecha': None,
        'form_hora_ini': None,
        'form_hora_fin': None,
        'form_titulo_reserva': None,
        'form_tipo_reserva': None,
        'form_motivo': None,
        'form_usuario_asignado_id': None,
    }

    return render(request, 'reservas/crear_reserva.html', context)


def detalles_reserva(request, cod_reserva):
    try:
        reserva = Reserva.objects.select_related('cod_ambiente_fk', 'cod_usuario_fk').get(cod_reserva=cod_reserva)
        data = {
            'titulo_reserva': reserva.titulo_reserva,
            'ambiente': reserva.cod_ambiente_fk.nom_amb,
            'fecha': reserva.fecha,
            'hora_ini': reserva.hora_ini,
            'hora_fin': reserva.hora_fin,
            'estado': reserva.estado,
            'funcionario': reserva.cod_usuario_fk.nombre,
        }
        return JsonResponse(data)
    except Reserva.DoesNotExist:
        return JsonResponse({'error': 'Reserva no encontrada'}, status=404)



def cancelar_reservas_solapadas(reserva_aprobada):
    print('DEBUG reserva_aprobada:',
          reserva_aprobada.cod_reserva,
          reserva_aprobada.cod_ambiente_fk_id,
          reserva_aprobada.fecha,
          reserva_aprobada.hora_ini,
          reserva_aprobada.hora_fin)

    qs = Reserva.objects.filter(
        cod_ambiente_fk=reserva_aprobada.cod_ambiente_fk,
        fecha=reserva_aprobada.fecha,
        estado='pendiente',
        hora_ini__lt=reserva_aprobada.hora_fin,
        hora_fin__gt=reserva_aprobada.hora_ini,
    ).exclude(
        cod_reserva=reserva_aprobada.cod_reserva
    )

    print('DEBUG conflictivas SQL:', str(qs.query))
    print('DEBUG conflictivas count BEFORE:', qs.count())


    reservas_a_cancelar = list(qs.select_related('cod_usuario_fk', 'cod_ambiente_fk'))
    
    total = len(reservas_a_cancelar)
    qs.update(estado='cancelada')

    print('DEBUG conflictivas count AFTER update:', total)

    for reserva_cancelada in reservas_a_cancelar:
        funcionario = reserva_cancelada.cod_usuario_fk
        destinatario = funcionario.email
        
        if destinatario:
            asunto = 'Reserva cancelada - Sistema R.A.S SENA'
            
            mensaje = (
                f"Sistema R.A.S - SENA\n\n"
                f"Hola {funcionario.nombre},\n\n"
                f"Tu reserva '{reserva_cancelada.titulo_reserva}' (código {reserva_cancelada.cod_reserva}) "
                f"para el ambiente '{reserva_cancelada.cod_ambiente_fk.nom_amb}' "
                f"el día {reserva_cancelada.fecha} de {reserva_cancelada.hora_ini} a {reserva_cancelada.hora_fin} "
                f"ha sido CANCELADA.\n\n"
                f"Motivo: Otra reserva fue aprobada en el mismo horario y ambiente.\n\n"
                f"Por favor, ingresa al sistema de reservas para revisar los detalles "
                f"o crear una nueva solicitud en otro horario.\n\n"
                f"Atentamente,\n"
                f"R.A.S - SENA"
            )
            
            contenido_html = f"""
            <!DOCTYPE html>
            <html lang="es">
              <body style="margin:0;padding:0;background-color:#f3f4f6;font-family:Arial,Helvetica,sans-serif;">
                <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background-color:#f3f4f6;padding:20px 0;">
                  <tr>
                    <td align="center">
                      <table role="presentation" cellpadding="0" cellspacing="0" width="600" style="background-color:#ffffff;border-radius:8px;overflow:hidden;border:1px solid #e5e7eb;">
                        <tr>
                          <td style="background:#991b1b;padding:16px 24px;color:#ffffff;">
                            <h2 style="margin:0;font-size:20px;">Sistema R.A.S - SENA</h2>
                            <p style="margin:4px 0 0;font-size:12px;opacity:0.9;">Notificación de reserva cancelada</p>
                          </td>
                        </tr>
                        <tr>
                          <td style="padding:20px 24px;">
                            <p style="margin:0 0 12px;font-size:14px;color:#111827;">
                              Hola <strong>{funcionario.nombre}</strong>,
                            </p>

                            <div style="margin:8px 0 16px;padding:12px 14px;border-left:4px solid #b91c1c;background-color:#fef2f2;font-size:14px;color:#111827;">
                              Tu reserva <strong>{reserva_cancelada.titulo_reserva}</strong> (código
                              <strong>{reserva_cancelada.cod_reserva}</strong>) para el ambiente
                              <strong>{reserva_cancelada.cod_ambiente_fk.nom_amb}</strong> el día
                              <strong>{reserva_cancelada.fecha}</strong> de
                              <strong>{reserva_cancelada.hora_ini}</strong> a
                              <strong>{reserva_cancelada.hora_fin}</strong> ha sido
                              <strong>cancelada</strong>.
                              <br><br>
                              Motivo: otra reserva fue aprobada en el mismo horario y ambiente.
                            </div>

                            <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="font-size:13px;color:#374151;margin-bottom:16px;">
                              <tr>
                                <td style="padding:2px 0;width:130px;font-weight:bold;">Código reserva:</td>
                                <td>{reserva_cancelada.cod_reserva}</td>
                              </tr>
                              <tr>
                                <td style="padding:2px 0;font-weight:bold;">Fecha:</td>
                                <td>{reserva_cancelada.fecha} {reserva_cancelada.hora_ini} - {reserva_cancelada.hora_fin}</td>
                              </tr>
                              <tr>
                                <td style="padding:2px 0;font-weight:bold;">Ambiente:</td>
                                <td>{reserva_cancelada.cod_ambiente_fk.nom_amb}</td>
                              </tr>
                            </table>

                            <p style="margin:0 0 4px;font-size:12px;color:#6b7280;">
                              Puedes ingresar al Sistema R.A.S para revisar el detalle o crear una nueva reserva en otro horario.
                            </p>
                            <p style="margin:0;font-size:12px;color:#6b7280;">
                              Atentamente,<br>Equipo Sistema R.A.S - SENA
                            </p>
                          </td>
                        </tr>
                        <tr>
                          <td style="background:#f9fafb;padding:10px 24px;text-align:center;font-size:11px;color:#9ca3af;">
                            Este es un mensaje automático generado por el sistema de reservas.
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </body>
            </html>
            """

            def _enviar_correo_cancelacion():
                try:
                    send_mail(
                        asunto,
                        mensaje,
                        settings.DEFAULT_FROM_EMAIL,
                        [destinatario],
                        html_message=contenido_html,
                        fail_silently=False,
                    )
                    print(f'DEBUG email enviado a {destinatario} (reserva {reserva_cancelada.cod_reserva})')
                except Exception as e:
                    print(f'ERROR enviando email a {destinatario}: {e}')

            transaction.on_commit(_enviar_correo_cancelacion)

    return total



@require_http_methods(["GET", "POST"])
@transaction.atomic
def cambiar_estado_reserva(request, cod_reserva):

    if 'user_id' not in request.session or 'user_name' not in request.session:
        messages.error(request, 'Debe iniciar sesión para acceder a esta página')
        return redirect(f'/login/?next=/reservas/cambiar-estado/{cod_reserva}/')

    usuario_actual = get_object_or_404(Usuario, id=request.session['user_id'])

    if usuario_actual.tipo != 'admin':
        messages.error(request, 'Solo un administrador puede cambiar el estado de la reserva.')
        return redirect('reservas:listar_reservas')

    reserva = get_object_or_404(Reserva, cod_reserva=cod_reserva)

    if request.method == 'POST':
        print('DEBUG POST DATA:', request.POST)
        form = EstadoReservaForm(request.POST, instance=reserva)

        if form.is_valid():
            estado_anterior = reserva.estado
            print('DEBUG estado_anterior:', estado_anterior)

            reserva_actualizada = form.save(commit=False)
            print('DEBUG estado_nuevo_form:', reserva_actualizada.estado)

            reserva_actualizada.save()

            canceladas = 0

            
            if estado_anterior != 'pendiente' and reserva_actualizada.estado == 'aprobada':
                print('DEBUG entro_a_cancelar_reservas_solapadas')
                canceladas = cancelar_reservas_solapadas(reserva_actualizada)
            else:
                print('DEBUG NO entro_a_cancelar: anterior=',
                      estado_anterior, 'nuevo=', reserva_actualizada.estado)

            msg = 'Estado de la reserva actualizado correctamente.'
            if canceladas > 0:
                msg += f" Se cancelaron automáticamente {canceladas} reserva(s) en conflicto."
            messages.success(request, msg)
            return redirect('reservas:listar_reservas')

        messages.error(request, 'Hubo un error al actualizar el estado.')
        return render(request, 'reservas/cambiar_estado.html', {
            'form': form,
            'reserva': reserva,
            'rol_usuario': usuario_actual.tipo,
        })

    else:
        form = EstadoReservaForm(instance=reserva)
        return render(request, 'reservas/cambiar_estado.html', {
            'form': form,
            'reserva': reserva,
            'rol_usuario': usuario_actual.tipo,
        })


@require_POST
@transaction.atomic
def marcar_ambiente_recibido(request, cod_reserva):
    if 'user_id' not in request.session or 'user_name' not in request.session:
        messages.error(request, 'Debe iniciar sesión para realizar esta acción.')
        return redirect('login')

    usuario_actual = get_object_or_404(Usuario, id=request.session['user_id'])
    reserva = get_object_or_404(Reserva, cod_reserva=cod_reserva)

   
    if reserva.cod_usuario_fk_id != usuario_actual.id:
        messages.error(request, 'No tiene permiso para marcar esta reserva como recibida.')
        return redirect('reservas:listar_reservas')

    
    if reserva.estado != 'aprobada':
        messages.error(request, 'Solo se puede marcar como recibido una reserva aprobada.')
        return redirect('reservas:listar_reservas')

    reserva.estado = 'recibida'
    reserva.save()

    messages.success(request, 'Ambiente marcado como recibido correctamente.')
    return redirect('reservas:listar_reservas')


@require_http_methods(["GET", "POST"])
@transaction.atomic
def editar_reserva(request, cod_reserva):
    if 'user_id' not in request.session or 'user_name' not in request.session:
        messages.error(request, 'Debe iniciar sesion para acceder a esta pagina')
        return redirect('/login/?next=/reservas/editar/{}/'.format(cod_reserva))

    reserva = get_object_or_404(
        Reserva.objects.select_related('cod_ambiente_fk', 'cod_usuario_fk'),
        cod_reserva=cod_reserva
    )

    usuario_actual = get_object_or_404(Usuario, id=request.session['user_id'])
    if 'user_tipo' not in request.session:
        request.session['user_tipo'] = usuario_actual.tipo

    if usuario_actual.tipo == 'funcionario' and reserva.estado in ['aprobada', 'completada', 'rechazada', 'cancelada']:
        messages.error(
            request,
            'Ya no se puede editar esta reserva.'
        )
        return redirect('reservas:listar_reservas')

    ambientes = Ambiente.objects.filter(
        Q(estado_amb='disponible') | Q(cod_amb=reserva.cod_ambiente_fk_id)
    ).order_by('nom_amb')

    funcionarios = Usuario.objects.filter(tipo='funcionario').order_by('nombre') if usuario_actual.tipo == 'admin' else []

    if request.method == 'POST':
        cod_ambiente_fk_id = request.POST.get('cod_ambiente_fk')
        fecha = request.POST.get('fecha')
        hora_ini = request.POST.get('hora_ini')
        hora_fin = request.POST.get('hora_fin')
        titulo_reserva = request.POST.get('titulo_reserva')
        tipo_reserva = request.POST.get('tipo_reserva')
        motivo = request.POST.get('motivo')
        num_personas = request.POST.get('num_personas')
        estado_nuevo = request.POST.get('estado')

        
        if usuario_actual.tipo == 'admin':
            usuario_asignado_id = request.POST.get('usuario_asignado')
            if usuario_asignado_id:
                try:
                    usuario_reserva = Usuario.objects.get(id=usuario_asignado_id, tipo='funcionario')
                except Usuario.DoesNotExist:
                    messages.error(request, 'El funcionario seleccionado no existe.')
                    return render(request, 'reservas/editar_reserva.html', {
                        'reserva': reserva,
                        'ambientes': ambientes,
                        'funcionarios': funcionarios,
                        'rol_usuario': usuario_actual.tipo,
                        'es_administrador': True
                    })
            else:
                usuario_reserva = reserva.cod_usuario_fk
        else:
            usuario_reserva = reserva.cod_usuario_fk

        
        if not all([cod_ambiente_fk_id, fecha, hora_ini, hora_fin, titulo_reserva, tipo_reserva, motivo, num_personas, estado_nuevo]):
            messages.error(request, 'Todos los campos son requeridos.')
            return render(request, 'reservas/editar_reserva.html', {
                'reserva': reserva,
                'ambientes': ambientes,
                'funcionarios': funcionarios,
                'rol_usuario': usuario_actual.tipo,
                'es_administrador': usuario_actual.tipo == 'admin'
            })

        try:
            ambiente = Ambiente.objects.get(cod_amb=cod_ambiente_fk_id)
        except Ambiente.DoesNotExist:
            messages.error(request, 'El ambiente seleccionado no existe.')
            return render(request, 'reservas/editar_reserva.html', {
                'reserva': reserva,
                'ambientes': ambientes,
                'funcionarios': funcionarios,
                'rol_usuario': usuario_actual.tipo,
                'es_administrador': usuario_actual.tipo == 'admin'
            })

        try:
            num_personas_int = int(num_personas)
        except ValueError:
            messages.error(request, 'El numero de personas debe ser numerico.')
            return render(request, 'reservas/editar_reserva.html', {
                'reserva': reserva,
                'ambientes': ambientes,
                'funcionarios': funcionarios,
                'rol_usuario': usuario_actual.tipo,
                'es_administrador': usuario_actual.tipo == 'admin'
            })

        if num_personas_int <= 0:
            messages.error(request, 'El numero de personas debe ser mayor a 0.')
            return render(request, 'reservas/editar_reserva.html', {
                'reserva': reserva,
                'ambientes': ambientes,
                'funcionarios': funcionarios,
                'rol_usuario': usuario_actual.tipo,
                'es_administrador': usuario_actual.tipo == 'admin'
            })

        if num_personas_int > ambiente.capacidad_amb:
            messages.error(
                request,
                'El numero de personas ({}) excede la capacidad del ambiente "{}" (max {}).'.format(
                    num_personas_int, ambiente.nom_amb, ambiente.capacidad_amb
                )
            )
            return render(request, 'reservas/editar_reserva.html', {
                'reserva': reserva,
                'ambientes': ambientes,
                'funcionarios': funcionarios,
                'rol_usuario': usuario_actual.tipo,
                'es_administrador': usuario_actual.tipo == 'admin'
            })

        field = Reserva._meta.get_field('estado')
        estados_validos = {c[0] for c in field.choices} if field.choices else set()
        if estados_validos and estado_nuevo not in estados_validos:
            messages.error(request, 'Estado invalido.')
            return render(request, 'reservas/editar_reserva.html', {
                'reserva': reserva,
                'ambientes': ambientes,
                'funcionarios': funcionarios,
                'rol_usuario': usuario_actual.tipo,
                'es_administrador': usuario_actual.tipo == 'admin'
            })

        
        hay_conflicto = Reserva.objects.filter(
            cod_ambiente_fk_id=cod_ambiente_fk_id,
            fecha=fecha,
            hora_ini__lt=hora_fin,
            hora_fin__gt=hora_ini,
            estado__in=['aprobada', 'completada', 'rechazada', 'cancelada'],
        ).exclude(cod_reserva=reserva.cod_reserva).exists()

        if hay_conflicto:
            messages.error(request, 'Ya existe una reserva en ese horario para el ambiente seleccionado.')
            return render(request, 'reservas/editar_reserva.html', {
                'reserva': reserva,
                'ambientes': ambientes,
                'funcionarios': funcionarios,
                'rol_usuario': usuario_actual.tipo,
                'es_administrador': usuario_actual.tipo == 'admin'
            })

        estado_anterior = reserva.estado

        reserva.cod_ambiente_fk = ambiente
        reserva.fecha = fecha
        reserva.hora_ini = hora_ini
        reserva.hora_fin = hora_fin
        reserva.titulo_reserva = titulo_reserva
        reserva.tipo_reserva = tipo_reserva
        reserva.motivo = motivo
        reserva.num_personas = num_personas_int
        reserva.estado = estado_nuevo
        reserva.cod_usuario_fk = usuario_reserva
        reserva.save()

        canceladas = 0
        if estado_anterior != 'aprobada' and estado_nuevo == 'aprobada':
            canceladas = cancelar_reservas_solapadas(reserva)

        msg = 'Reserva actualizada correctamente.'
        if canceladas:
            msg += f' Se cancelaron automáticamente {canceladas} reserva(s) en conflicto.'
        messages.success(request, msg)

        return redirect('reservas:listar_reservas')

    return render(request, 'reservas/editar_reserva.html', {
        'reserva': reserva,
        'ambientes': ambientes,
        'funcionarios': funcionarios,
        'rol_usuario': usuario_actual.tipo,
        'es_administrador': usuario_actual.tipo == 'admin'
    })



def eliminar_reserva(request, cod_reserva):
    if 'user_id' not in request.session or 'user_name' not in request.session:
        messages.error(request, 'Debe iniciar sesión para acceder a esta página')
        return redirect(f'/login/?next=/reservas/eliminar/{cod_reserva}/')
    
    reserva = get_object_or_404(Reserva, cod_reserva=cod_reserva)
    
    if request.method == 'POST':
        titulo_reserva = reserva.titulo_reserva
        reserva.delete()
        messages.success(request, f'Reserva "{titulo_reserva}" eliminada exitosamente.')
        return redirect('reservas:listar_reservas')
    
    return render(request, 'reservas/eliminar_reserva.html', {'reserva': reserva})


def ambientes_disponibles(request):
    try:
        ambientes = Ambiente.objects.filter(estado_amb='disponible').values('cod_amb', 'nom_amb')
        return JsonResponse(list(ambientes), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def reservas_por_ambiente(request, ambiente_id):
    reservas = Reserva.objects.filter(
        cod_ambiente_fk=ambiente_id,
        estado__in=['aprobada', 'completada', 'rechazada', 'cancelada']
    ).values('fecha', 'hora_ini', 'hora_fin', 'titulo_reserva')
    return JsonResponse(list(reservas), safe=False)


def reservas_json(request):
    ambiente_id = request.GET.get('ambiente')
    reservas = Reserva.objects.filter(cod_ambiente_fk_id=ambiente_id)
    eventos = []
    for r in reservas:
        eventos.append({
            "title": r.titulo_reserva,
            "start": f"{r.fecha}T{r.hora_ini}",
            "end": f"{r.fecha}T{r.hora_fin}",
            "color": "#dc3545"
        })
    return JsonResponse(eventos, safe=False)


def obtener_reservas_api(request):
    """API para obtener todas las reservas en tiempo real"""
    try:
        reservas_existentes = Reserva.objects.select_related(
            'cod_ambiente_fk', 'cod_usuario_fk'
        ).filter(
            estado__in=['aprobada', 'completada', 'rechazada', 'cancelada', 'recibida']
        ).order_by('fecha', 'hora_ini')
        
        reservas_data = []
        for reserva in reservas_existentes:
            try:
                reserva_data = {
                    'cod_reserva': reserva.cod_reserva,
                    'titulo_reserva': reserva.titulo_reserva,
                    'fecha': reserva.fecha.strftime('%Y-%m-%d'),
                    'hora_ini': reserva.hora_ini.strftime('%H:%M'),
                    'hora_fin': reserva.hora_fin.strftime('%H:%M'),
                    'ambiente': reserva.cod_ambiente_fk.nom_amb,
                    'ambiente_id': reserva.cod_ambiente_fk.cod_amb,
                    'estado': reserva.estado,
                    'usuario': reserva.cod_usuario_fk.nombre
                }
                reservas_data.append(reserva_data)
            except Exception as e:
                print(f"Error procesando reserva {reserva.cod_reserva}: {e}")
                continue
        
        print(f"API: Enviando {len(reservas_data)} reservas")
        return JsonResponse({
            'success': True,
            'reservas': reservas_data,
            'total': len(reservas_data)
        })
    
    except Exception as e:
        print(f"ERROR en API reservas: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def enviar_correo_vista(request, cod_reserva):
    """Vista para que el admin escriba y envíe el correo"""
    if 'user_id' not in request.session:
        return redirect('login')
    
    try:
        reserva = Reserva.objects.select_related('cod_usuario_fk').get(cod_reserva=cod_reserva)
        usuario_admin = Usuario.objects.get(id=request.session['user_id'])
        
        if request.method == 'POST':
            asunto = request.POST.get('asunto')
            mensaje = request.POST.get('mensaje')
            
            contenido_html = f"""
            <!DOCTYPE html>
            <html>
            <body>
                <h2>Sistema R.A.S - SENA</h2>
                <p>Hola <strong>{reserva.cod_usuario_fk.nombre}</strong>,</p>
                <div padding: 15px; border-left: 4px solid #255639;">
                    <p>{mensaje}</p>
                </div>
                <p><strong>Administrador:</strong> {usuario_admin.nombre}</p>
                <p><strong>Reserva:</strong> {reserva.titulo_reserva} (Código: {reserva.cod_reserva})</p>
                <p>R.A.S - SENA</p>
            </body>
            </html>
            """
            
            send_mail(
                asunto,
                mensaje,
                None,
                [reserva.cod_usuario_fk.email],
                html_message=contenido_html,
            )
            
            messages.success(request, f'Correo enviado a {reserva.cod_usuario_fk.nombre}')
            return redirect('reservas:listar_reservas')
        
        return render(request, 'reservas/enviar_correo.html', {
            'reserva': reserva,
            'rol_usuario': usuario_admin.tipo
        })
    
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('reservas:listar_reservas')


@require_POST
def comentar_reserva_funcionario(request, pk):
    if 'user_id' not in request.session or 'user_name' not in request.session:
        messages.error(request, 'Debe iniciar sesión para acceder a esta página')
        return redirect(f'/login/?next=/reservas/comentar/{pk}/')

    usuario_actual = get_object_or_404(Usuario, id=request.session['user_id'])
    reserva = get_object_or_404(Reserva, cod_reserva=pk)

    if reserva.cod_usuario_fk_id != usuario_actual.id:
        messages.error(request, 'No tiene permiso para comentar esta reserva.')
        return redirect('reservas:listar_reservas')

    if reserva.estado not in ['recibida', 'completada']:
        messages.error(request, 'Solo puede comentar una reserva con ambiente recibido.')
        return redirect('reservas:listar_reservas')

    form = ComentarioFuncionarioForm(request.POST, instance=reserva)
    if form.is_valid():
        reserva_obj = form.save(commit=False)

        tipos = request.POST.getlist('tipos_problema') 
        reserva_obj.tipos_problema = ','.join(tipos) if tipos else None

        reserva_obj.save()
        messages.success(request, 'Comentario guardado correctamente.')
    else:
        messages.error(request, 'Hubo un error al guardar el comentario.')

    return redirect('reservas:listar_reservas')


@require_POST
def comentar_reserva_admin(request, pk):
    if 'user_id' not in request.session or 'user_name' not in request.session:
        messages.error(request, 'Debe iniciar sesión para acceder a esta página')
        return redirect(f'/login/?next=/reservas/comentar-admin/{pk}/')

    usuario = get_object_or_404(Usuario, id=request.session['user_id'])
    if usuario.tipo != 'admin':
        messages.error(request, 'Solo un administrador puede guardar este comentario.')
        return redirect('reservas:listar_reservas')

    reserva = get_object_or_404(Reserva, cod_reserva=pk)
    comentario = request.POST.get('comen_funcionario', '').strip()

    if comentario:
        reserva.comen_admin = comentario
        reserva.save(update_fields=['comen_admin'])
        messages.success(request, 'Comentario del administrador guardado correctamente.')
    else:
        messages.warning(request, 'No se envió ningún comentario.')

    return redirect('reservas:listar_reservas')

TIPO_PROBLEMA_CHOICES = [
    ('sonido', 'Sonido'),
    ('inventario', 'Inventario (equipos, muebles, etc.)'),
    ('iluminacion', 'Iluminación'),
    ('aseo', 'Aseo / limpieza'),
    ('infraestructura', 'Infraestructura'),
    ('conectividad', 'Conectividad (red / energía)'),
    ('otros', 'Otros'),
]

def listar_reservas_tabla(request):
    if 'user_id' not in request.session or 'user_name' not in request.session:
        messages.error(request, 'Debe iniciar sesión para acceder a esta página')
        return redirect('/login/?next=/reservas/lista/')

    usuario_id = request.session['user_id']
    usuario_actual = Usuario.objects.get(id=usuario_id)

    if usuario_actual.tipo == 'funcionario':
        reservas = Reserva.objects.filter(
            cod_usuario_fk=usuario_actual
        ).order_by('-fecha', '-hora_ini')
    else:
        reservas = Reserva.objects.all().order_by('-fecha', '-hora_ini')

    ambiente_id = request.GET.get('ambiente') or ''
    if ambiente_id:
        reservas = reservas.filter(cod_ambiente_fk_id=ambiente_id)

    tipo_problema = request.GET.get('tipo_problema') or ''
    if tipo_problema:
        reservas = reservas.filter(tipos_problema__icontains=tipo_problema)

    ambientes = Ambiente.objects.all().order_by('nom_amb')

    return render(
        request,
        'reservas/listar_reservas_tabla.html',
        {
            'reservas': reservas,
            'rol_usuario': usuario_actual.tipo,
            'ambientes': ambientes,
            'ambiente_seleccionado': ambiente_id,
            'tipo_problema_seleccionado': tipo_problema,
            'TIPO_PROBLEMA_CHOICES': TIPO_PROBLEMA_CHOICES,
        },
    )