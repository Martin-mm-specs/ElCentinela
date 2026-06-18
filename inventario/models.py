from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid


class Insumo(models.Model):
    """Modelo para representar un insumo/producto en el inventario"""
    UNIDADES_CHOICES = [
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('ml', 'Mililitros'),
        ('l', 'Litros'),
        ('unidad', 'Unidad'),
        ('docena', 'Docena'),
    ]
    
    id_codigo = models.IntegerField(unique=True, null=True, blank=True, editable=False)  # INT auto-generado
    nombre = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)  # Cantidad actual
    cantidad_original = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Cantidad al ingresarse
    unidad = models.CharField(max_length=20, choices=UNIDADES_CHOICES, default='kg')
    fecha_entrada = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateField()
    activo = models.BooleanField(default=True)  # Para marcar como agotado sin eliminar
    
    class Meta:
        ordering = ['-fecha_entrada']
    
    def __str__(self):
        return f"{self.nombre} ({self.cantidad} {self.unidad})"
    
    def save(self, *args, **kwargs):
        """Auto-generar id_codigo basado en el pk si es necesario"""
        if not self.pk:
            # Primera vez que se guarda: guardar sin id_codigo
            super().save(*args, **kwargs)
            # Ahora que tiene pk, asignar id_codigo
            if not self.id_codigo:
                self.id_codigo = self.pk
                super().save(update_fields=['id_codigo'])
        else:
            # Actualizaciones posteriores: solo guardar normalmente
            super().save(*args, **kwargs)
    
    @property
    def dias_para_expirar(self):
        """Retorna los días faltantes para que expire el producto"""
        hoy = timezone.now().date()
        delta = self.fecha_expiracion - hoy
        return delta.days
    
    @property
    def esta_proxima_a_expirar(self):
        """Retorna True si el producto expira en 3 días o menos"""
        return 0 <= self.dias_para_expirar <= 3
    
    @property
    def esta_expirado(self):
        """Retorna True si el producto ya expiró"""
        hoy = timezone.now().date()
        return self.fecha_expiracion < hoy


class UsoHistorico(models.Model):
    """Modelo para registrar el uso de insumos por día"""
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='usos')
    cantidad_usada = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    notas = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha']
        verbose_name_plural = "Usos Históricos"
    
    def __str__(self):
        return f"{self.insumo.nombre} - {self.cantidad_usada} {self.insumo.unidad} ({self.fecha})"


class EstadisticasUso(models.Model):
    """Modelo para almacenar estadísticas de uso promedio por insumo"""
    insumo = models.OneToOneField(Insumo, on_delete=models.CASCADE, related_name='estadisticas')
    uso_promedio_diario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )  # Promedio calculado
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Stats: {self.insumo.nombre} - {self.uso_promedio_diario} {self.insumo.unidad}/día"
    
    @staticmethod
    def calcular_promedio(insumo):
        """Calcula el promedio de uso de los últimos 7 días"""
        hace_7_dias = timezone.now().date() - timedelta(days=7)
        usos = UsoHistorico.objects.filter(
            insumo=insumo,
            fecha__gte=hace_7_dias
        )
        
        if usos.exists():
            total = sum(uso.cantidad_usada for uso in usos)
            promedio = total / 7
            return round(promedio, 2)
        return 0


class AlertaMensaje(models.Model):
    """Modelo para almacenar alertas y mensajes que se muestran en el dashboard"""
    TIPOS_ALERTA = [
        ('vencimiento', 'Vencimiento próximo'),
        ('expirado', 'Producto expirado'),
        ('bajo_stock', 'Stock bajo'),
        ('info', 'Información general'),
    ]
    
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS_ALERTA, default='info')
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, null=True, blank=True, related_name='alertas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name_plural = "Alertas y Mensajes"
    
    def __str__(self):
        return f"{self.titulo} ({self.tipo})"
