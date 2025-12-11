import datetime
from django import forms
from .models import Soporte, MensajeSoporte
from reservas.models import Reserva


class ResponderSoporteForm(forms.ModelForm):
    class Meta:
        model = Soporte
        fields = ['estado', 'prioridad', 'respuesta_admin']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'respuesta_admin': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Escribe aquí la respuesta para el usuario, pasos a seguir o solución aplicada.',
                }
            ),
        }


class SoporteForm(forms.ModelForm):
    class Meta:
        model = Soporte
        fields = ['reserva', 'asunto', 'descripcion', 'prioridad']
        widgets = {
            'reserva': forms.Select(attrs={'class': 'form-select'}),
            'asunto': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej: Problema con la reserva del ambiente 301',
                    'maxlength': 200,
                }
            ),
            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Describe detalladamente el problema...',
                }
            ),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        funcionario = kwargs.pop('funcionario', None)
        super().__init__(*args, **kwargs)

        hoy = datetime.date.today()

        qs = Reserva.objects.filter(
            fecha__gte=hoy
        ).order_by('fecha', 'hora_ini')

        if funcionario:
            qs = qs.filter(cod_usuario_fk=funcionario)

        self.fields['reserva'].queryset = qs


class MensajeSoporteForm(forms.ModelForm):
    class Meta:
        model = MensajeSoporte
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Escribe tu mensaje...',
                }
            ),
        }
