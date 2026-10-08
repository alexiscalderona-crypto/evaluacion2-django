from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Cliente, EstadoCaso, Caso, Expediente, Pago, PerfilAbogado

# 1. PerfilAbogado como StackedInline en el mantenedor de usuarios
class PerfilAbogadoInline(admin.StackedInline):
    model = PerfilAbogado
    can_delete = False
    verbose_name_plural = 'Perfil de Abogado'

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilAbogadoInline,)

# Re-registrar User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 2. Registros con list_display, search_fields y list_filter
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'documento', 'telefono', 'correo')
    search_fields = ('nombres', 'documento')

@admin.register(EstadoCaso)
class EstadoCasoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'permite_pagos')
    list_filter = ('permite_pagos',)

# Inlines para Caso
class ExpedienteInline(admin.TabularInline):
    model = Expediente
    extra = 1

class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1

@admin.register(Caso)
class CasoAdmin(admin.ModelAdmin):
    # list_display con cliente, estado y total_pagado
    list_display = ('codigo', 'titulo', 'cliente', 'estado', 'total_pagado')
    search_fields = ('codigo', 'titulo', 'cliente__nombres')
    list_filter = ('estado', 'fecha_inicio')
    
    # filter_horizontal para asignar abogados
    filter_horizontal = ('abogados',)
    
    # Expediente y Pago como TabularInline
    inlines = [ExpedienteInline, PagoInline]

@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    list_display = ('numero', 'juzgado', 'fecha_presentacion', 'caso')
    search_fields = ('numero', 'juzgado', 'caso__codigo')
    list_filter = ('fecha_presentacion',)
