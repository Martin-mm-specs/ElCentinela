from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from .models import Insumo, UsoHistorico, EstadisticasUso, AlertaMensaje
from .forms import InsumoForm, UsoHistoricoForm


def buscar_insumos_api(request):
    """
    Endpoint API para búsqueda interactiva de insumos.
    Retorna JSON con insumos activos que coincidan con la búsqueda.
    """
    query = request.GET.get('q', '').strip()
    hoy = timezone.now().date()
    
    # Obtener insumos activos ordenados por fecha de expiración
    insumos = Insumo.objects.filter(
        activo=True,
        fecha_expiracion__gte=hoy
    ).order_by('fecha_expiracion')
    
    # Filtrar por búsqueda (case-insensitive)
    if query:
        insumos = insumos.filter(
            Q(nombre__icontains=query) | Q(id_codigo__icontains=query)
        )
    
    # Preparar datos para retornar
    insumos_data = []
    for insumo in insumos:
        dias_para_expirar = insumo.dias_para_expirar
        insumos_data.append({
            'id': insumo.id,
            'id_codigo': insumo.id_codigo,
            'nombre': insumo.nombre,
            'cantidad': float(insumo.cantidad),
            'unidad': insumo.unidad,
            'fecha_expiracion': insumo.fecha_expiracion.strftime('%d/%m/%Y'),
            'dias_para_expirar': dias_para_expirar,
            'esta_proxima_a_expirar': insumo.esta_proxima_a_expirar,
            'display_text': f"[{insumo.id_codigo}] {insumo.nombre} - Vence: {insumo.fecha_expiracion.strftime('%d/%m/%Y')} ({dias_para_expirar}d)"
        })
    
    return JsonResponse({'insumos': insumos_data})


def generar_alertas_insumo(insumo):
    """Genera alertas para un insumo específico sin duplicar"""
    if not insumo.activo:
        return
    
    hoy = timezone.now().date()
    
    # Determinar qué tipo de alerta se debe mostrar
    alerta_tipo = None
    alerta_titulo = None
    alerta_descripcion = None
    
    if insumo.esta_expirado:
        alerta_tipo = 'expirado'
        alerta_titulo = f'⚠️ {insumo.nombre} ha expirado'
        alerta_descripcion = (
            f'El insumo "{insumo.nombre}" expiró el {insumo.fecha_expiracion.strftime("%d/%m/%Y")}. '
            f'Por favor, verifica su estado antes de usarlo.'
        )
    elif insumo.esta_proxima_a_expirar:
        alerta_tipo = 'vencimiento'
        dias = insumo.dias_para_expirar
        alerta_titulo = f'⏰ {insumo.nombre} vence pronto'
        alerta_descripcion = (
            f'El insumo "{insumo.nombre}" vencerá en {dias} día(s) ({insumo.fecha_expiracion.strftime("%d/%m/%Y")}). '
            f'Considera usarlo primero para evitar desperdicio.'
        )
    
    # Si hay una alerta que mostrar
    if alerta_tipo:
        # Buscar si ya existe una alerta activa de este tipo para este insumo
        alerta_existente = AlertaMensaje.objects.filter(
            insumo=insumo,
            tipo=alerta_tipo,
            activa=True
        ).first()
        
        if alerta_existente:
            # Solo actualizar si el contenido cambió
            if alerta_existente.titulo != alerta_titulo or alerta_existente.descripcion != alerta_descripcion:
                alerta_existente.titulo = alerta_titulo
                alerta_existente.descripcion = alerta_descripcion
                alerta_existente.save()
        else:
            # Crear nueva alerta
            AlertaMensaje.objects.create(
                titulo=alerta_titulo,
                descripcion=alerta_descripcion,
                tipo=alerta_tipo,
                insumo=insumo,
                activa=True
            )
    else:
        # Si no hay alerta que mostrar, desactivar las existentes de este insumo
        AlertaMensaje.objects.filter(insumo=insumo, activa=True).update(activa=False)


def generar_todas_alertas():
    """Genera alertas para todos los insumos activos"""
    insumos = Insumo.objects.filter(activo=True)
    for insumo in insumos:
        generar_alertas_insumo(insumo)


def dashboard(request):
    """Vista principal del dashboard"""
    # Generar alertas
    generar_todas_alertas()
    
    insumos_activos = Insumo.objects.filter(activo=True)
    
    # Obtener alertas activas
    alertas = AlertaMensaje.objects.filter(activa=True).order_by('-fecha_creacion')
    
    # Estadísticas generales
    total_insumos = insumos_activos.count()
    insumos_proximos_a_expirar = [i for i in insumos_activos if i.esta_proxima_a_expirar and not i.esta_expirado]
    insumos_expirados = [i for i in insumos_activos if i.esta_expirado]
    cantidad_por_expirar = len(insumos_proximos_a_expirar)
    cantidad_expirados = len(insumos_expirados)
    
    # Usos del día de hoy
    hoy = timezone.now().date()
    usos_hoy = UsoHistorico.objects.filter(fecha=hoy)
    
    context = {
        'total_insumos': total_insumos,
        'cantidad_por_expirar': cantidad_por_expirar,
        'cantidad_expirados': cantidad_expirados,
        'insumos_proximos_a_expirar': insumos_proximos_a_expirar,
        'insumos_expirados': insumos_expirados,
        'usos_hoy': usos_hoy,
        'alertas': alertas,
    }
    
    return render(request, 'inventario/dashboard.html', context)


class InsumoListView(ListView):
    """Lista de insumos activos"""
    model = Insumo
    template_name = 'inventario/insumo_list.html'
    context_object_name = 'insumos'
    paginate_by = 20
    
    def get_queryset(self):
        return Insumo.objects.filter(activo=True).order_by('-fecha_entrada')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar información de días para expirar
        for insumo in context['insumos']:
            insumo.dias_para_expirar_display = insumo.dias_para_expirar
        return context


class InsumoDetailView(DetailView):
    """Detalle de un insumo específico"""
    model = Insumo
    template_name = 'inventario/insumo_detail.html'
    context_object_name = 'insumo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        insumo = self.get_object()
        
        # Historial de uso
        context['usos'] = UsoHistorico.objects.filter(insumo=insumo).order_by('-fecha')[:30]
        
        # Estadísticas
        try:
            stats = EstadisticasUso.objects.get(insumo=insumo)
            context['uso_promedio'] = stats.uso_promedio_diario
        except EstadisticasUso.DoesNotExist:
            context['uso_promedio'] = 0
        
        return context


class InsumoCreateView(CreateView):
    """Crear un nuevo insumo"""
    model = Insumo
    form_class = InsumoForm
    template_name = 'inventario/insumo_form.html'
    success_url = reverse_lazy('inventario:insumo_list')
    
    def form_valid(self, form):
        # Establecer cantidad_original igual a cantidad
        insumo = form.save(commit=False)
        insumo.cantidad_original = insumo.cantidad
        insumo.save()
        
        # Generar alertas para este insumo
        generar_alertas_insumo(insumo)
        
        return redirect(self.success_url)


class InsumoUpdateView(UpdateView):
    """Actualizar insumo"""
    model = Insumo
    form_class = InsumoForm
    template_name = 'inventario/insumo_form.html'
    success_url = reverse_lazy('inventario:insumo_list')


class InsumoDeleteView(DeleteView):
    """Eliminar insumo (marcar como inactivo)"""
    model = Insumo
    template_name = 'inventario/insumo_confirm_delete.html'
    success_url = reverse_lazy('inventario:insumo_list')
    
    def delete(self, request, *args, **kwargs):
        """En lugar de eliminar, marcamos como inactivo"""
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        return redirect(self.success_url)


class UsoHistoricoListView(ListView):
    """Historial de uso diario"""
    model = UsoHistorico
    template_name = 'inventario/uso_historico_list.html'
    context_object_name = 'usos'
    paginate_by = 50
    
    def get_queryset(self):
        return UsoHistorico.objects.all().order_by('-fecha')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agrupar por fecha para mejor visualización
        usos_por_fecha = {}
        for uso in context['usos']:
            fecha = str(uso.fecha)
            if fecha not in usos_por_fecha:
                usos_por_fecha[fecha] = []
            usos_por_fecha[fecha].append(uso)
        
        context['usos_por_fecha'] = sorted(usos_por_fecha.items(), reverse=True)
        return context


class UsoHistoricoCreateView(CreateView):
    """Registrar nuevo uso de insumo"""
    model = UsoHistorico
    form_class = UsoHistoricoForm
    template_name = 'inventario/uso_historico_form.html'
    success_url = reverse_lazy('inventario:dashboard')
    
    def form_valid(self, form):
        # Obtener el uso antes de guardarlo
        uso = form.save(commit=True)
        
        # Restar la cantidad del insumo
        insumo = uso.insumo
        insumo.cantidad -= uso.cantidad_usada
        insumo.save()
        
        # Actualizar estadísticas después de registrar uso
        try:
            stats = EstadisticasUso.objects.get(insumo=insumo)
        except EstadisticasUso.DoesNotExist:
            stats = EstadisticasUso.objects.create(insumo=insumo)
        
        stats.uso_promedio_diario = EstadisticasUso.calcular_promedio(insumo)
        stats.save()
        
        # Regenerar alertas para este insumo
        generar_alertas_insumo(insumo)
        
        return redirect(self.success_url)


def proyeccion_compra(request):
    """Vista que muestra proyección de compra basada en uso promedio"""
    insumos_activos = Insumo.objects.filter(activo=True)
    
    proyecciones = []
    for insumo in insumos_activos:
        try:
            stats = EstadisticasUso.objects.get(insumo=insumo)
            uso_diario = stats.uso_promedio_diario
        except EstadisticasUso.DoesNotExist:
            uso_diario = 0
        
        # Proyectar para los próximos 7 días
        cantidad_recomendada = round(uso_diario * 7, 2) if uso_diario > 0 else 0
        
        # Calcular días disponibles
        if uso_diario > 0:
            dias_disponibles = round(insumo.cantidad / uso_diario, 1)
        else:
            dias_disponibles = float('inf')
        
        # Calcular porcentaje de recomendación
        if cantidad_recomendada > 0:
            porcentaje = round((insumo.cantidad / cantidad_recomendada) * 100, 1)
        else:
            porcentaje = 100
        
        proyecciones.append({
            'insumo': insumo,
            'uso_promedio_diario': uso_diario,
            'cantidad_actual': insumo.cantidad,
            'cantidad_recomendada': cantidad_recomendada,
            'dias_disponibles': dias_disponibles,
            'porcentaje': porcentaje,
        })
    
    context = {
        'proyecciones': proyecciones,
    }
    
    return render(request, 'inventario/proyeccion_compra.html', context)


def descartar_alerta(request, alerta_id):
    """Descartar/eliminar una alerta de forma idempotente"""
    # Marcar como inactiva si existe; no lanzar 404 si no existe
    AlertaMensaje.objects.filter(id=alerta_id, activa=True).update(activa=False)
    return redirect('inventario:dashboard')
