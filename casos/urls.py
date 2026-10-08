from django.urls import path
from . import views

urlpatterns = [
    # Mantenedor de clientes
    path('clientes/', views.ClienteList.as_view(), name='cliente_list'),
    path('clientes/nuevo/', views.ClienteCreate.as_view(), name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.ClienteUpdate.as_view(), name='cliente_update'),
    path('clientes/<int:pk>/eliminar/', views.ClienteDelete.as_view(), name='cliente_delete'),
    
    # Portal de casos
    path('casos/', views.lista_casos, name='lista_casos'),
    path('casos/<int:id>/', views.detalle_caso, name='detalle_caso'),
    path('casos/expediente/<int:exp_id>/subir/', views.subir_documento, name='subir_documento'),
    
    # API
    path('casos/api/<int:id>/', views.api_caso, name='api_caso'),
]
