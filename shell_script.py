from django.contrib.auth.models import User
from casos.models import Cliente, EstadoCaso, Caso, Expediente, Pago, PerfilAbogado
from datetime import date
from decimal import Decimal

# Crear Cliente
cliente = Cliente.objects.create(
    nombres="Empresa ABC", 
    documento="20123456789", 
    telefono="999888777", 
    correo="contacto@abc.com"
)

# Crear Estados
estado_iniciado = EstadoCaso.objects.create(nombre="iniciado", permite_pagos=True)
estado_en_proceso = EstadoCaso.objects.create(nombre="en proceso", permite_pagos=True)

# Crear Usuarios y Abogados
user1 = User.objects.create_user(username="abogado1", first_name="Juan", last_name="Perez")
user2 = User.objects.create_user(username="abogado2", first_name="Maria", last_name="Gomez")

abogado1 = PerfilAbogado.objects.create(usuario=user1, numero_colegiatura="CAL-1001", especialidad="Penal")
abogado2 = PerfilAbogado.objects.create(usuario=user2, numero_colegiatura="CAL-1002", especialidad="Civil")

# Crear 2 Casos
caso1 = Caso.objects.create(
    codigo="C-2026-001", 
    titulo="Demanda Civil ABC", 
    descripcion="Demanda por daños", 
    fecha_inicio=date.today(), 
    cliente=cliente, 
    estado=estado_iniciado
)
caso2 = Caso.objects.create(
    codigo="C-2026-002", 
    titulo="Asesoria Penal ABC", 
    descripcion="Asesoria corporativa", 
    fecha_inicio=date.today(), 
    cliente=cliente, 
    estado=estado_en_proceso
)

# Asignar 2 abogados a uno de ellos (caso1)
caso1.abogados.add(abogado1, abogado2)

# Registrar 2 expedientes para caso1
exp1 = Expediente.objects.create(
    numero="EXP-001-2026", 
    juzgado="1er Juzgado Civil", 
    fecha_presentacion=date.today(), 
    caso=caso1
)
exp2 = Expediente.objects.create(
    numero="EXP-002-2026", 
    juzgado="2do Juzgado Civil", 
    fecha_presentacion=date.today(), 
    caso=caso1
)

# Registrar 3 pagos para caso1
Pago.objects.create(caso=caso1, monto=Decimal('1500.00'), fecha=date.today(), descripcion="Adelanto")
Pago.objects.create(caso=caso1, monto=Decimal('2000.50'), fecha=date.today(), descripcion="Hito 1")
Pago.objects.create(caso=caso1, monto=Decimal('500.00'), fecha=date.today(), descripcion="Gastos notariales")

# MOSTRAR RESULTADOS
print("\n--- RESULTADOS DEL SHELL ---")
print(f"Cliente: {cliente.nombres}")

print("\nCasos del cliente:")
for c in cliente.caso_set.all():
    print(f" - {c.codigo}: {c.titulo}")

print(f"\nAbogados del caso {caso1.codigo}:")
for a in caso1.abogados.all():
    print(f" - {a.usuario.get_full_name()} ({a.especialidad})")

print(f"\nExpedientes del caso {caso1.codigo}:")
for e in caso1.expediente_set.all():
    print(f" - {e.numero} en {e.juzgado}")

print(f"\nTotal pagado del caso {caso1.codigo}:")
print(f" - S/ {caso1.total_pagado()}")
print("----------------------------\n")
