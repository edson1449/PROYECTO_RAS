from django import forms
from .models import Ambiente

class AmbienteForm(forms.ModelForm):
    class Meta:
        model = Ambiente
        fields = ['nom_amb', 'info_amb', 'capacidad_amb', 'piso_amb', 'estado_amb', 'imagen_amb']
        widgets = {
            'nom_amb': forms.TextInput(attrs={'class': 'form-control'}),
            'info_amb': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sillas, computadores, televisores, etc.'}),
            'capacidad_amb': forms.NumberInput(attrs={'class': 'form-control'}),
            'piso_amb': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado_amb': forms.Select(attrs={'class': 'form-control'}),
            'imagen_amb': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'imagen_amb': 'Imagen del Ambiente',
        }