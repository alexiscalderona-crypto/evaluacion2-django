from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum

class Cliente(models.Model):
    nombres = models.CharField(max_length=150)
    documento = models.CharField(max_length=20, unique=True) # DNI o RUC
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()

    def __str__(self):
        return self.nombres

class EstadoCaso(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    permite_pagos = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

class PerfilAbogado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    numero_colegiatura = models.CharField(max_length=20)
    especialidad = models.CharField(max_length=100)

    def __str__(self):
        return f"Abogado: {self.usuario.get_full_name() or self.usuario.username}"

class Caso(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    
    # Justificación Caso-Cliente: Usamos PROTECT porque no debería poder eliminarse un cliente 
    # que ya tiene casos registrados. Esto asegura que el historial legal quede intacto y no se pierdan datos en cascada.
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    
    # Justificación Caso-EstadoCaso: Usamos PROTECT. Si un estado (ej. "En proceso") se intenta eliminar,
    # no queremos que todos los casos con ese estado se borren por error, ni queremos casos sin estado.
    estado = models.ForeignKey(EstadoCaso, on_delete=models.PROTECT)
    
    abogados = models.ManyToManyField(PerfilAbogado)

    def __str__(self):
        return f"{self.codigo} - {self.titulo}"

    def total_pagado(self):
        resultado = self.pago_set.aggregate(total=Sum('monto'))
        return resultado['total'] or 0

class Expediente(models.Model):
    numero = models.CharField(max_length=50, unique=True)
    juzgado = models.CharField(max_length=100)
    fecha_presentacion = models.DateField()
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE)
    documento = models.FileField(upload_to='expedientes/', null=True, blank=True)

    def __str__(self):
        return self.numero

class Pago(models.Model):
    # Justificación Pago-Caso: Usamos PROTECT (o restrict). Si un caso tiene pagos asociados,
    # no se debería eliminar el caso a la ligera para no causar descuadres contables en el estudio.
    caso = models.ForeignKey(Caso, on_delete=models.PROTECT)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return f"Pago de {self.monto} para {self.caso.codigo}"

    def clean(self):
        if self.pk is None and hasattr(self, 'caso') and self.caso and not self.caso.estado.permite_pagos:
            raise ValidationError("El estado actual del caso no permite registrar pagos.")
        super().clean()
