from django.db import models

class Centro(models.Model):
    CENTROS_BOGOTA = [
        ("Centro de Electricidad, Electrónica y Telecomunicaciones", "Centro de Electricidad, Electrónica y Telecomunicaciones"),
        ("Centro de Gestión Industrial", "Centro de Gestión Industrial"),
        ("Centro de Diseño y Metrología", "Centro de Diseño y Metrología"),
        ("Centro Metalmecánico", "Centro Metalmecánico"),
        ("Centro Nacional de Hotelería, Turismo y Alimentos", "Centro Nacional de Hotelería, Turismo y Alimentos"),
        ("Centro de Manufactura en Textil y Cuero", "Centro de Manufactura en Textil y Cuero"),
        ("Centro de Materiales y Ensayos", "Centro de Materiales y Ensayos"),
        ("Centro de Tecnologías para la Construcción y la Madera", "Centro de Tecnologías para la Construcción y la Madera"),
        ("Centro de Servicios Financieros", "Centro de Servicios Financieros"),
        ("Centro de Gestión Administrativa", "Centro de Gestión Administrativa"),
        ("Centro de Gestión de Mercados, Logística y Tecnologías de la Información", "Centro de Gestión de Mercados, Logística y Tecnologías de la Información"),
        ("Centro de Formación de Talento Humano en Salud", "Centro de Formación de Talento Humano en Salud"),
        ("Centro para la Industria de la Comunicación Gráfica", "Centro para la Industria de la Comunicación Gráfica"),
        ("Centro de Tecnologías del Transporte", "Centro de Tecnologías del Transporte"),
        ("Centro de Formación en Actividad Física y Cultura", "Centro de Formación en Actividad Física y Cultura"),
    ]

    cod_centro = models.AutoField(primary_key=True)
    nom_centro = models.CharField(max_length=100, choices=CENTROS_BOGOTA, unique=True)
    ciudad_centro = models.CharField(max_length=30, default='Bogotá', editable=False)

    def __str__(self):
        return f"{self.nom_centro} ({self.ciudad_centro})"

    class Meta:
        db_table = 'centro_formacion'
        managed = False
