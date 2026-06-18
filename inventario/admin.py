from django.contrib import admin
from .models import Insumo, UsoHistorico, EstadisticasUso, AlertaMensaje


@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'id_codigo', 'cantidad', 'unidad', 'fecha_expiracion', 'activo')
    list_filter = ('unidad', 'activo', 'fecha_expiracion')
    search_fields = ('nombre', 'id_codigo')
    readonly_fields = ('fecha_entrada', 'cantidad_original')
    fieldsets = (
        ('Información del Producto', {
            'fields': ('nombre', 'id_codigo', 'cantidad', 'cantidad_original', 'unidad')
        }),
        ('Fechas', {
            'fields': ('fecha_entrada', 'fecha_expiracion')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )


@admin.register(UsoHistorico)
class UsoHistoricoAdmin(admin.ModelAdmin):
    list_display = ('insumo', 'cantidad_usada', 'fecha')
    list_filter = ('fecha', 'insumo')
    search_fields = ('insumo__nombre',)
    readonly_fields = ('fecha',)
    date_hierarchy = 'fecha'


@admin.register(EstadisticasUso)
class EstadisticasUsoAdmin(admin.ModelAdmin):
    list_display = ('insumo', 'uso_promedio_diario', 'ultima_actualizacion')
    readonly_fields = ('ultima_actualizacion',)


@admin.register(AlertaMensaje)
class AlertaMensajeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'fecha_creacion', 'activa')
    list_filter = ('tipo', 'activa', 'fecha_creacion')
    search_fields = ('titulo', 'descripcion')
    readonly_fields = ('fecha_creacion',)

