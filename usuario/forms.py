from django import forms
from django.contrib.auth.hashers import make_password
from .models import Usuario
from centros.models import Centro
from coordinaciones.models import Coordinacion

class RegistroUsuarioForm(forms.ModelForm):
    nueva_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese contraseña'
        }),
        label="Contraseña",
        help_text="Contraseña requerida para nuevo usuario"
    )
    
    confirmar_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme la contraseña'
        }),
        label="Confirmar Contraseña"
    )
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'nombre', 'telefono', 'email', 
            'tipo', 'cod_centro_fk', 'cod_coordinacion_fk'
        ]
        widgets = {
            'id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese número de documento'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese nombre completo'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese número telefónico'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese correo electrónico'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'cod_centro_fk': forms.Select(attrs={
                'class': 'form-control'
            }),
            'cod_coordinacion_fk': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'id': 'Número de Documento',
            'nombre': 'Nombre Completo',
            'telefono': 'Teléfono',
            'email': 'Correo Electrónico',
            'tipo': 'Tipo de Usuario',
            'cod_centro_fk': 'Centro',
            'cod_coordinacion_fk': 'Coordinación',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cod_centro_fk'].queryset = Centro.objects.all()
        self.fields['cod_coordinacion_fk'].queryset = Coordinacion.objects.all()
        
        # Si estamos editando, hacer los campos de contraseña opcionales
        if self.instance and self.instance.pk:
            self.fields['nueva_password'].required = False
            self.fields['nueva_password'].help_text = "Dejar en blanco para mantener contraseña actual"
            self.fields['confirmar_password'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        nueva_password = cleaned_data.get("nueva_password")
        confirmar_password = cleaned_data.get("confirmar_password")
        
        # Si estamos creando un usuario, la contraseña es obligatoria
        if not self.instance.pk and (not nueva_password or not confirmar_password):
            raise forms.ValidationError("La contraseña es obligatoria para crear un usuario")
        
        # Validar que las contraseñas coincidan
        if nueva_password and confirmar_password:
            if nueva_password != confirmar_password:
                raise forms.ValidationError("Las contraseñas no coinciden")
        
        return cleaned_data
    
    def save(self, commit=True):
        usuario = super().save(commit=False)
        
        # Solo actualizar contraseña si se proporcionó una nueva
        nueva_password = self.cleaned_data.get('nueva_password')
        if nueva_password:
            usuario.password = make_password(nueva_password)
        # Si estamos editando y no se cambia la contraseña, mantener la actual
        elif self.instance and self.instance.pk:
            usuario.password = self.instance.password
        
        if commit:
            usuario.save()
        
        return usuario