from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from datetime import date
from decimal import Decimal
from .models import Cliente, Caso, EstadoCaso, Pago, Expediente

# --- MANTENEDOR DE CLIENTES ---
class ClienteList(ListView):
    model = Cliente
    template_name = 'casos/cliente_list.html'
    context_object_name = 'clientes'

class ClienteCreate(CreateView):
    model = Cliente
    fields = ['nombres', 'documento', 'telefono', 'correo']
    template_name = 'casos/cliente_form.html'
    success_url = reverse_lazy('cliente_list')

class ClienteUpdate(UpdateView):
    model = Cliente
    fields = ['nombres', 'documento', 'telefono', 'correo']
    template_name = 'casos/cliente_form.html'
    success_url = reverse_lazy('cliente_list')

class ClienteDelete(DeleteView):
    model = Cliente
    template_name = 'casos/cliente_confirm_delete.html'
    success_url = reverse_lazy('cliente_list')

# --- PORTAL DE CASOS ---
def lista_casos(request):
    estado_id = request.GET.get('estado')
    if not estado_id:
        estado_id = request.COOKIES.get('ultimo_estado')
    
    casos = Caso.objects.all()
    if estado_id:
        casos = casos.filter(estado_id=estado_id)
        
    estados = EstadoCaso.objects.all()
    
    response = render(request, 'casos/lista_casos.html', {
        'casos': casos,
        'estados': estados,
        'estado_actual': int(estado_id) if estado_id else ''
    })
    
    if estado_id:
        response.set_cookie('ultimo_estado', estado_id)
        
    return response

def detalle_caso(request, id):
    caso = get_object_or_404(Caso, id=id)
    error_pago = None
    
    if request.method == 'POST':
        monto = request.POST.get('monto')
        descripcion = request.POST.get('descripcion')
        if caso.estado.permite_pagos:
            try:
                Pago.objects.create(
                    caso=caso,
                    monto=Decimal(monto),
                    fecha=date.today(),
                    descripcion=descripcion
                )
                return redirect('detalle_caso', id=id)
            except Exception as e:
                error_pago = str(e)
        else:
            error_pago = "El estado actual del caso no permite registrar pagos."

    return render(request, 'casos/detalle_caso.html', {'caso': caso, 'error_pago': error_pago})

def subir_documento(request, exp_id):
    expediente = get_object_or_404(Expediente, id=exp_id)
    if request.method == 'POST' and request.FILES.get('documento'):
        expediente.documento = request.FILES['documento']
        expediente.save()
    return redirect('detalle_caso', id=expediente.caso.id)

# --- API ---
def api_caso(request, id):
    caso = get_object_or_404(Caso, id=id)
    abogados = [a.usuario.get_full_name() or a.usuario.username for a in caso.abogados.all()]
    data = {
        'codigo': caso.codigo,
        'cliente': caso.cliente.nombres,
        'estado': caso.estado.nombre,
        'abogados': abogados,
        'num_expedientes': caso.expediente_set.count(),
        'total_pagado': str(caso.total_pagado())
    }
    return JsonResponse(data)
