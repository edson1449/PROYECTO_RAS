from django.db import models
from django.contrib.auth import get_user_model
from usuarios.models import Usuario

User = get_user_model()


class Soporte(models.Model):
    PRIORIDAD_BAJA = 'baja'
    PRIORIDAD_MEDIA = 'media'
    PRIORIDAD_ALTA = 'alta'

    PRIORIDAD_CHOICES = [
        (PRIORIDAD_BAJA, 'Baja'),
        (PRIORIDAD_MEDIA, 'Media'),
        (PRIORIDAD_ALTA, 'Alta'),
    ]

    ESTADO_ABIERTO = 'abierto'
    ESTADO_EN_PROCESO = 'en_proceso'
    ESTADO_CERRADO = 'cerrado'

    ESTADO_CHOICES = [
        (ESTADO_ABIERTO, 'Abierto'),
        (ESTADO_EN_PROCESO, 'En proceso'),
        (ESTADO_CERRADO, 'Cerrado'),
    ]

    id = models.AutoField(primary_key=True)

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='soportes'
    )

    reserva = models.ForeignKey(
        'reservas.Reserva',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='soportes'
    )

    asunto = models.CharField(max_length=200)

    descripcion = models.TextField()

    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDAD_CHOICES,
        default=PRIORIDAD_MEDIA
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_ABIERTO
    )

    respuesta_admin = models.TextField(
        null=True,
        blank=True
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = 'soporte'
        ordering = ['-creado_en']

    def __str__(self):
        return f'Soporte #{self.id} - {self.asunto}'


class MensajeSoporte(models.Model):
    soporte = models.ForeignKey(
        Soporte,
        on_delete=models.CASCADE,
        related_name='mensajes'
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='mensajes_soporte'
    )
    texto = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mensaje_soporte'
        ordering = ['creado_en']

    def __str__(self):
        return f"Mensaje #{self.id} en Soporte #{self.soporte_id}"
