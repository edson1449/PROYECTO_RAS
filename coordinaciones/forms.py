from django import forms
from .models import Coordinacion

class CoordinacionForm(forms.ModelForm):
    class Meta:
        model = Coordinacion
        fields = ['nom_coordinacion', 'cod_centro_fk']
        widgets = {
            'nom_coordinacion': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ingrese nombre de la coordinación'
            }),
            'cod_centro_fk': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'nom_coordinacion': 'Nombre de la Coordinación',
            'cod_centro_fk': 'Centro',
        }