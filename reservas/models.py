from django.db import models
from usuarios.models import Usuario
from ambientes.models import Ambiente


class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('cancelada', 'Cancelada'),
        ('recibida', 'Ambiente recibido'),
        ('completada', 'Completada'),
    ]

    TIPO_RESERVA_CHOICES = [
        ('clase', 'Clase'),
        ('reunion', 'Reunión'),
        ('evento', 'Evento'),
        ('capacitacion', 'Capacitación'),
        ('examen', 'Examen'),
        ('otros', 'Otros'),
    ]

    
    TIPO_PROBLEMA_CHOICES = [
        ('sonido', 'Sonido'),
        ('inventario', 'Inventario (equipos, muebles, etc.)'),
        ('iluminacion', 'Iluminación'),
        ('aseo', 'Aseo / limpieza'),
        ('infraestructura', 'Infraestructura'),
        ('conectividad', 'Conectividad (red / energía)'),
        ('otros', 'Otros'),
    ]

    cod_reserva = models.AutoField(primary_key=True)
    titulo_reserva = models.CharField(max_length=100, verbose_name="Título de la Reserva")
    tipo_reserva = models.CharField(max_length=100, choices=TIPO_RESERVA_CHOICES, verbose_name="Tipo de Reserva")
    fecha = models.DateField(verbose_name="Fecha")
    hora_ini = models.TimeField(verbose_name="Hora Inicio")
    hora_fin = models.TimeField(verbose_name="Hora Fin")
    motivo = models.CharField(max_length=256, verbose_name="Motivo")
    num_personas = models.IntegerField(verbose_name="Número de Personas")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name="Estado")

    tipos_problema = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        db_column='tipos_problema',
        verbose_name='Tipos de problema reportados'
    )

    comen_funcionario = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        db_column='comen_funcionario',
        verbose_name='Comentario funcionario'
    )
    comen_admin = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        db_column='comen_admin',
        verbose_name='Comentario administrador'
    )

    cod_usuario_fk = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='cod_usuario_fk',
        verbose_name='Usuario'
    )

    cod_ambiente_fk = models.ForeignKey(
        Ambiente,
        on_delete=models.CASCADE,
        db_column='cod_ambiente_fk',
        verbose_name='Ambiente'
    )

    def __str__(self):
        return f"{self.titulo_reserva} - {self.fecha}"

    class Meta:
        db_table = 'reserva'
