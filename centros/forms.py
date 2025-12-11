from django import forms
from .models import Centro

class CentroForm(forms.ModelForm):
    class Meta:
        model = Centro
        fields = ['nom_centro']
        widgets = {
            'nom_centro': forms.Select(attrs={'class': 'form-select'}),
        }
