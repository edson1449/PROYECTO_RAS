from django.db import models

class Ambiente(models.Model):
    ESTADOS_AMBIENTE = [
        ('disponible', 'Disponible'),
        ('mantenimiento', 'En Mantenimiento'),
        ('ocupado', 'Ocupado'),
        ('recibido', 'Ambiente Recibido'),
    ]

    cod_amb = models.AutoField(primary_key=True, verbose_name='Código Ambiente')
    nom_amb = models.CharField(max_length=50, verbose_name='Nombre del Ambiente')
    info_amb = models.CharField(max_length=100, verbose_name='Información del Ambiente')
    capacidad_amb = models.IntegerField(verbose_name='Capacidad')
    piso_amb = models.IntegerField(verbose_name='Piso')
    estado_amb = models.CharField(max_length=20, choices=ESTADOS_AMBIENTE, verbose_name='Estado')
    imagen_amb = models.ImageField(
        upload_to='ambientes/', 
        null=True, 
        blank=True, 
        verbose_name='Imagen del Ambiente'
    )

    def __str__(self):
        return self.nom_amb

    class Meta:
        db_table = 'ambiente'
        verbose_name = 'Ambiente'
        verbose_name_plural = 'Ambientes'
        managed = False