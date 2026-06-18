from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # API
    path('api/buscar-insumos/', views.buscar_insumos_api, name='buscar_insumos_api'),
    
    # Insumos
    path('insumos/', views.InsumoListView.as_view(), name='insumo_list'),
    path('insumos/crear/', views.InsumoCreateView.as_view(), name='insumo_create'),
    path('insumos/<int:pk>/', views.InsumoDetailView.as_view(), name='insumo_detail'),
    path('insumos/<int:pk>/editar/', views.InsumoUpdateView.as_view(), name='insumo_update'),
    path('insumos/<int:pk>/eliminar/', views.InsumoDeleteView.as_view(), name='insumo_delete'),
    
    # Historial de uso
    path('historial/', views.UsoHistoricoListView.as_view(), name='uso_list'),
    path('historial/registrar/', views.UsoHistoricoCreateView.as_view(), name='uso_create'),
    
    # Proyección de compra
    path('proyeccion/', views.proyeccion_compra, name='proyeccion'),
    
    # Alertas
    path('alertas/<int:alerta_id>/descartar/', views.descartar_alerta, name='descartar_alerta'),
]
