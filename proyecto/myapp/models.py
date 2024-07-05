from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class proyect(models.Model):
    name=models.CharField(max_length=200)



class Usuario(models.Model):
    # Relación OneToOneField con el modelo User de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username
    
    
class Paciente(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rut = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=10)
    apellido = models.CharField(max_length=10)
    fono = models.CharField(max_length=10)
    email = models.CharField(max_length=25)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Mensaje(models.Model):
    remitente = models.ForeignKey(User, related_name='mensajes_enviados', on_delete=models.CASCADE)
    destinatario = models.ForeignKey(User, related_name='mensajes_recibidos', on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Mensaje de {self.remitente.username} a {self.destinatario.username}'

    
class Carta(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
    
    