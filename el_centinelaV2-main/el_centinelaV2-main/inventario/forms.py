from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Insumo, UsoHistorico


class InsumoForm(forms.ModelForm):
    """Formulario para crear/editar insumos"""
    
    class Meta:
        model = Insumo
        fields = ['nombre', 'cantidad', 'unidad', 'fecha_expiracion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del insumo'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'unidad': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fecha_expiracion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': 'DD/MM/YYYY'
            }),
        }
    
    def clean_fecha_expiracion(self):
        """Validar que la fecha de expiración no sea en el pasado"""
        fecha_expiracion = self.cleaned_data.get('fecha_expiracion')
        hoy = timezone.now().date()
        
        if fecha_expiracion and fecha_expiracion < hoy:
            raise ValidationError(
                '❌ Error: El insumo ya expiró. No puedes ingresar una fecha que ya pasó. '
                'Por favor, ingresa una fecha futura.',
                code='fecha_pasada'
            )
        
        return fecha_expiracion
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que id_codigo sea opcional (se puede auto-generar)
        # self.fields['id_codigo'].required = False


class UsoHistoricoForm(forms.ModelForm):
    """Formulario para registrar uso de insumos"""
    
    class Meta:
        model = UsoHistorico
        fields = ['insumo', 'cantidad_usada', 'notas']
        widgets = {
            'insumo': forms.Select(attrs={
                'class': 'form-control',
                'id': 'insumo_select',
                'required': 'required'
            }),
            'cantidad_usada': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtener insumos activos ordenados por vencimiento próximo (para el select como respaldo)
        hoy = timezone.now().date()
        
        # Queryset ordenado: primero los que vencen pronto
        self.fields['insumo'].queryset = Insumo.objects.filter(
            activo=True,
            fecha_expiracion__gte=hoy
        ).order_by('fecha_expiracion')
    
    def clean_cantidad_usada(self):
        """Validar que la cantidad usada sea positiva"""
        cantidad_usada = self.cleaned_data.get('cantidad_usada')
        
        if cantidad_usada and cantidad_usada <= 0:
            raise ValidationError('La cantidad usada debe ser mayor a 0.')
        
        return cantidad_usada

