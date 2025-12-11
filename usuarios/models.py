from django.db import models
from centros.models import Centro
from coordinaciones.models import Coordinacion

class Usuario(models.Model):
    TIPOS_USUARIO = [
        ('admin', 'Administrador'),
        ('funcionario', 'Funcionario'),
    ]

    id = models.BigIntegerField(primary_key=True)
    nombre = models.CharField(max_length=60, null=True, blank=True)
    telefono = models.BigIntegerField(null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=60, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_USUARIO, null=True, blank=True)

    # usar la misma columna de BD pero como ForeignKey de Django
    cod_centro_fk = models.ForeignKey(
        Centro,
        db_column='cod_centro_fk',
        to_field='cod_centro',            
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='usuarios'
    )
    cod_coordinacion_fk = models.ForeignKey(
        Coordinacion,
        db_column='cod_coordinacion_fk',
        to_field='cod_coordinacion',      # si la PK de Coordinacion es cod_coordinacion
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='usuarios'
    )

    def __str__(self):
        return f"{self.nombre} (ID: {self.id})"

    class Meta:
        db_table = 'usuarios'

        
