from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from centros.models import Centro
from coordinaciones.models import Coordinacion

class Usuario(models.Model):
    
    TIPOS_USUARIO = [
        ('admin', 'Administrador'),
        ('funcionario', 'Funcionario'),
    ]

    
    id = models.CharField(primary_key=True, max_length=20, verbose_name="Número de Documento")
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    password = models.CharField(max_length=128, verbose_name="Contraseña")  
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    tipo = models.CharField(max_length=20, choices=TIPOS_USUARIO, verbose_name="Tipo de Usuario")
    
    cod_coordinacion_fk = models.ForeignKey(
        Coordinacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='cod_coordinacion_fk',
        verbose_name='Coordinación'
    )
    
    cod_centro_fk = models.ForeignKey(
        Centro,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='cod_centro_fk',
        verbose_name='Centro'
    )
    
    def __str__(self):
        return f"{self.nombre} - {self.email}"
    
    class Meta:
        db_table = 'usuario'
        managed = False