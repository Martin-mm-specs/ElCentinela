# 🏪 El Centinela - Sistema de Gestión de Inventario

Sistema web en Django para gestionar inventario de restaurantes, reducir desperdicio y optimizar compras basándose en datos históricos de consumo.

## 🚀 Inicio Rápido

### Requisitos
- Python 3.8+
- Django 6.0.6 (ya instalado)


**Acceso:**
- 🌐 Sitio: http://127.0.0.1:8000/
- 🔐 Admin: http://127.0.0.1:8000/admin/ (admin / admin123)

## ✨ Características v2.0 - 7 Cambios Implementados

| # | Característica | Descripción |
|---|---|---|
| 1 | **ID Auto-increment** | ✅ Cada insumo obtiene ID único automático |
| 2 | **Validación Fecha** | ✅ Rechaza fechas en el pasado con mensaje de error |
| 3 | **Formato DD/MM/YYYY** | ✅ Input clara con ejemplo del formato esperado |
| 4 | **Error Proyección** | ✅ Proyección de compra 100% funcional (línea 67 corregida) |
| 5 | **Cantidad Original** | ✅ Tracking: cantidad original vs cantidad actual con progreso |
| 6 | **Buscador Inteligente** | ✅ Filtro en tiempo real, ordenado por vencimiento automáticamente |
| 7 | **Alertas en BD** | ✅ Persistentes, descartables, se regeneran automáticamente |

## 📋 Funcionalidades Principales

✅ **Dashboard** - Alertas persistentes con botón descartar  
✅ **Gestión de Insumos** - Crear, editar, eliminar (soft delete)  
✅ **Cantidad Inteligente** - Original vs actual con barra de progreso  
✅ **Registro de Uso** - Buscador filtrado, resta automática  
✅ **Historial** - Visualizar consumo por fecha con estadísticas  
✅ **Proyección** - Recomendaciones basadas en promedio 7 días  
✅ **Alertas DB** - Guardadas, descartables, auto-regeneran  

## 📁 Estructura del Proyecto

```
ElCentinela/
├── inventario/              # Aplicación principal
│   ├── templates/           # Archivos HTML
│   ├── models.py           # Base de datos
│   ├── views.py            # Lógica
│   ├── forms.py            # Formularios
│   └── urls.py             # Rutas
├── ElCentinela/            # Configuración Django
├── manage.py
├── db.sqlite3              # Base de datos
└── PROYECTO_INFO.txt       # Documentación completa
```

## 🔧 Comandos Útiles

```bash
# Crear nuevas migraciones después de cambiar modelos
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear nuevo superusuario
python manage.py createsuperuser

# Shell interactivo
python manage.py shell

# Detener el servidor
Ctrl+C
```

## 📚 Documentación Completa

Consulta `PROYECTO_INFO.txt` para:
- Descripción detallada de modelos
- Rutas y vistas disponibles
- Guía de uso completa
- Troubleshooting
- Características futuras

## 🎯 Flujo Típico de Uso

1. **Agregar Insumos** → Ingresa productos iniciales con fecha de vencimiento
2. **Registrar Uso** → Cada día registra lo que se consume
3. **Ver Alertas** → Dashboard muestra vencimientos próximos
4. **Comprar Inteligente** → Usa Proyección para saber exactamente qué comprar
5. **Reducir Desperdicio** → Evita comprar de más

## 💡 Características Clave

- **IDs/QR únicos** para cada producto
- **Fechas de expiración** con alertas automáticas
- **Historial detallado** de uso diario
- **Promedios automáticos** de consumo
- **Proyecciones inteligentes** para la próxima semana
- **Soft delete** - Los datos nunca se pierden

## 🛡️ Seguridad

- Panel admin protegido con contraseña
- Base de datos SQLite local
- CSRF protection habilitado

## 📈 Próximas Mejoras

- Autenticación de usuarios
- Reportes en PDF/Excel
- Integración con QR scanners
- Multi-restaurante
- Análisis de costos

---

**Estado:** ✅ Completo y Funcional  
**Última actualización:** 2026-06-14
