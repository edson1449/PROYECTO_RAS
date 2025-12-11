from django import forms
from .models import Reserva


class EstadoReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['estado']
        widgets = {
            'estado': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'estado': 'Estado de la reserva',
        }
class ComentarioFuncionarioForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['comen_funcionario']
        widgets = {
            'comen_funcionario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escriba aquí sus comentarios sobre el ambiente recibido'
            })
        }
        labels = {
            'comen_funcionario': 'Comentario del funcionario',
        }

class ComentarioAdminForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['comen_admin']
        widgets = {
            'comen_admin': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escriba aquí sus comentarios como administrador'
            })
        }
        labels = {
            'comen_admin': 'Comentario del administrador',
        }
        
class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = [
            'titulo_reserva', 'tipo_reserva', 'fecha', 'hora_ini', 
            'hora_fin', 'motivo', 'num_personas', 'estado', 'cod_ambiente_fk'
        ]
        widgets = {
            'titulo_reserva': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ingrese título de la reserva'
            }),
            'tipo_reserva': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'hora_ini': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el motivo de la reserva',
                'rows': 3
            }),
            'num_personas': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de personas'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            }),
            'cod_ambiente_fk': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        
        labels = {
            'titulo_reserva': 'Título de la Reserva',
            'tipo_reserva': 'Tipo de Reserva',
            'fecha': 'Fecha',
            'hora_ini': 'Hora Inicio',
            'hora_fin': 'Hora Fin',
            'motivo': 'Motivo',
            'num_personas': 'Número de Personas',
            'estado': 'Estado',
            'cod_ambiente_fk': 'Ambiente',
        }