from django.shortcuts import render
from reservas.models import Reserva
from historial.models import HistorialReserva

def mis_reservas(request):
    usuario_actual = request.user if request.user.is_authenticated else None
    
    if usuario_actual:
        todas_reservas = Reserva.objects.filter(
            cod_usuario_fk=usuario_actual
        ).order_by('-fecha', 'hora_ini')
        
        historial_reservas = HistorialReserva.objects.filter(
            id_usuario_fk=usuario_actual
        ).order_by('-fecha')
    else:
        todas_reservas = []
        historial_reservas = []
    
    context = {
        'todas_reservas': todas_reservas,
        'historial_reservas': historial_reservas,
    }
    
    return render(request, 'mis_reservas.html', context)
