from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
import re
from django.core.validators import FileExtensionValidator
from .models import Usuario
from centros.models import Centro
from coordinaciones.models import Coordinacion


class LoginForm(forms.Form):
    """Formulario simple de login con validaciones estrictas"""
    numero_documento = forms.CharField(
        label='Número de Documento',
        max_length=15,
        min_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 12345678',
            'autocomplete': 'off'
        }),
        error_messages={
            'required': 'El número de documento es obligatorio.',
            'max_length': 'Máximo 15 dígitos.',
            'min_length': 'Mínimo 5 dígitos.'
        }
    )
    password = forms.CharField(
        label='Contraseña',
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 6 caracteres',
            'autocomplete': 'current-password'
        }),
        error_messages={
            'required': 'La contraseña es obligatoria.',
            'min_length': 'Mínimo 6 caracteres.'
        }
    )

    def clean_numero_documento(self):
        numero = self.cleaned_data.get('numero_documento')
        if numero:
            if not numero.isdigit():
                raise ValidationError('Solo números, sin puntos ni guiones.')
            if len(numero) < 5 or len(numero) > 15:
                raise ValidationError('Longitud inválida (5-15 dígitos).')
        return numero

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and len(password) < 6:
            raise ValidationError('La contraseña debe tener al menos 6 caracteres.')
        return password


class RegistroUsuarioForm(forms.Form):
    """Formulario de registro con validaciones internacionales"""
    
   
    numero_documento = forms.CharField(
        label='Número de Documento',
        max_length=20,  # ← AUMENTADO
        min_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 12345678 o pasaporte',
            'autocomplete': 'off'
        }),
        error_messages={
            'required': 'El número de documento es obligatorio.',
            'max_length': 'Máximo 20 caracteres.',
            'min_length': 'Mínimo 5 caracteres.'
        }
    )
    nombre = forms.CharField(
        label='Nombres Completos',
        max_length=100,
        min_length=2,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre completo'
        }),
        error_messages={
            'required': 'Los nombres son obligatorios.',
            'max_length': 'Máximo 100 caracteres.',
            'min_length': 'Mínimo 2 caracteres.'
        }
    )
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'cualquier@dominio.com'
        }),
        error_messages={
            'required': 'El correo es obligatorio.',
            'invalid': 'Ingrese un correo válido.'
        }
    )
    telefono = forms.CharField(
        label='Teléfono',
        max_length=20,  # ← AUMENTADO
        min_length=8,   # ← TELEFONO MÁS CORTOS
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '3001234567, +1234567890, etc.'
        }),
        error_messages={
            'required': 'El teléfono es obligatorio.',
            'max_length': 'Máximo 20 caracteres.',
            'min_length': 'Mínimo 8 caracteres.'
        }
    )
    cod_centro_fk = forms.ModelChoiceField(
        label='Centro SENA',
        queryset=Centro.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control form-select'
        }),
        empty_label="-- Selecciona un centro --",
        to_field_name='cod_centro',
        error_messages={'required': 'Seleccione su centro SENA.'}
    )
    cod_coordinacion_fk = forms.ModelChoiceField(
        label='Coordinación',
        queryset=Coordinacion.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control form-select'
        }),
        empty_label="-- Selecciona una coordinación --",
        to_field_name='cod_coordinacion',
        error_messages={'required': 'Seleccione su coordinación.'}
    )
    password = forms.CharField(
        label='Contraseña',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres'
        }),
        error_messages={
            'required': 'La contraseña es obligatoria.',
            'min_length': 'Mínimo 8 caracteres.'
        }
    )
    password_confirm = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    
    def clean_tipo_documento(self):
        tipo = self.cleaned_data.get('tipo_documento')
        if tipo not in [choice[0] for choice in self.TIPO_DOCUMENTO_CHOICES]:
            raise ValidationError('Tipo de documento inválido.')
        return tipo
    
    def clean_numero_documento(self):
        numero = self.cleaned_data.get('numero_documento')
        if numero:
            # ← CAMBIO: permite letras para pasaportes internacionales
            if len(numero) < 5 or len(numero) > 20:
                raise ValidationError('Número inválido (5-20 caracteres).')
            tipo_doc = self.cleaned_data.get('tipo_documento')
            if tipo_doc and Usuario.objects.filter(
                tipo_documento=tipo_doc, 
                numero_documento=numero
            ).exists():
                raise ValidationError('Este documento ya está registrado.')
        return numero
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
                raise ValidationError('Solo letras y espacios permitidos.')
            nombre = nombre.strip().title()
        return nombre
    
    def clean_email(self):
        """✅ CAMBIO: CUALQUIER EMAIL VÁLIDO"""
        email = self.cleaned_data.get('email')
        if email:
            # Solo valida formato, no dominio
            if Usuario.objects.filter(email=email).exists():
                raise ValidationError('Este correo ya está registrado.')
        return email
    
    def clean_telefono(self):
        """✅ CAMBIO: CUALQUIER TELÉFONO INTERNACIONAL"""
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Formato internacional flexible: +1234567890, 3001234567, etc.
            if not re.match(r'^\+?[\d\s\-\(\)]{8,20}$', telefono):
                raise ValidationError('Teléfono inválido. Ej: 3001234567, +1234567890')
        return telefono
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 8:
                raise ValidationError('Mínimo 8 caracteres.')
            if not re.search(r'(?=.*[A-Z])(?=.*\d)', password):
                raise ValidationError('Debe tener al menos 1 mayúscula y 1 número.')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data


class EditarPerfilForm(forms.Form):
    """Formulario para editar perfil internacional"""
    
    email = forms.EmailField(
        label='Correo Electrónico',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'cualquier@dominio.com'
        })
    )
    telefono = forms.CharField(
        label='Teléfono',
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '3001234567, +1234567890'
        })
    )
    cod_centro_fk = forms.ModelChoiceField(
        label='Centro SENA',
        queryset=Centro.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control form-select'
        }),
        to_field_name='cod_centro'
    )
    cod_coordinacion_fk = forms.ModelChoiceField(
        label='Coordinación',
        queryset=Coordinacion.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control form-select'
        }),
        to_field_name='cod_coordinacion'
    )
    password_actual = forms.CharField(
        label='Contraseña Actual',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password'
        })
    )
    password_nueva = forms.CharField(
        label='Nueva Contraseña',
        required=False,
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    password_confirm = forms.CharField(
        label='Confirmar Nueva',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and self.usuario:
            if Usuario.objects.exclude(id=self.usuario.id).filter(email=email).exists():
                raise ValidationError('Este correo ya está en uso.')
        return email
    
    def clean_telefono(self):
        """✅ CAMBIO: TELEFONO INTERNACIONAL"""
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            if not re.match(r'^\+?[\d\s\-\(\)]{8,20}$', telefono):
                raise ValidationError('Teléfono inválido. Ej: 3001234567, +1234567890')
        return telefono
    
    def clean(self):
        cleaned_data = super().clean()
        password_actual = cleaned_data.get('password_actual')
        password_nueva = cleaned_data.get('password_nueva')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password_nueva or password_confirm:
            if not password_actual:
                raise ValidationError('Ingrese contraseña actual para cambiarla.')
            if self.usuario and not check_password(password_actual, self.usuario.password):
                raise ValidationError('Contraseña actual incorrecta.')
            if password_nueva != password_confirm:
                raise ValidationError('Las contraseñas nuevas no coinciden.')
            if len(password_nueva) < 8 or not re.search(r'(?=.*[A-Z])(?=.*\d)', password_nueva):
                raise ValidationError('Nueva contraseña: 8+ chars, 1 mayús, 1 número.')
        
        return cleaned_data


class CargaMasivausuariosForm(forms.Form):
    """Formulario para carga masiva"""
    archivo = forms.FileField(
        label='Archivo CSV/Excel',
        help_text='Formatos: .csv, .xlsx, .xls',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['csv', 'xlsx', 'xls']
            )
        ],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls'
        })
    )
