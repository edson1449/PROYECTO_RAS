from django.db import models
from usuarios.models import Usuario
from reservas.models import Reserva 

class HistorialReserva(models.Model):
    id_historial = models.AutoField(primary_key=True)
    cod_reserva_fk = models.ForeignKey(Reserva, on_delete=models.CASCADE, db_column='cod_reserva_fk')
    id_usuario_fk = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario_fk')
    accion = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    detalles = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.accion} - {self.cod_reserva_fk.titulo_reserva}"
    
    class Meta:
        db_table = 'historial_reserva'