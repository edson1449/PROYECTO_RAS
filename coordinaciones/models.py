from django.db import models
from centros.models import Centro

class Coordinacion(models.Model):
    cod_coordinacion = models.AutoField(primary_key=True)
    nom_coordinacion = models.CharField(max_length=35, null=True, blank=True)
    cod_centro_fk = models.ForeignKey(
        Centro, 
        on_delete=models.CASCADE, 
        db_column='cod_centro_fk', 
        verbose_name='Centro'
    )
    
    def __str__(self):
        return f"{self.nom_coordinacion} - {self.cod_centro_fk.nom_centro}"

    class Meta:
        db_table = 'coordinacion'
       