from django.shortcuts import render,HttpResponse
from django.http import HttpResponse
from .models import Paciente,Usuario
from django.db import IntegrityError
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from .forms import MensajeForm
from .models import Carta
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from .forms import MensajeForm
import json
from .models import Mensaje
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse


from .models import Mensaje
from django.contrib import messages

# Create your views here.
def home(request):
    return render(request, 'index.html',{'usuario':request.user})


def medicamento(request):
    return render(request, 'carro1.html')

def coso(request):
    return render(request, 'coso.html')



# views.py

from django.contrib.auth.models import User
from .models import Usuario

def registro(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        
        if password1 == password2:
            user = User.objects.create_user(username=username, email=email, password=password1)
            Usuario.objects.create(user=user)
            return redirect('login')
        else:
            return render(request, 'registro.html', {'error': 'Las contraseñas no coinciden'})
    return render(request, 'registro.html')









@login_required
def gestionar_pacientes_y_mensajes(request):
    # Variables iniciales
    form_mensaje = MensajeForm()
    mensajes = Mensaje.objects.filter(destinatario=request.user).order_by('-fecha_envio')
    error_message = None

    # Obtener la instancia del usuario
    usuario = Usuario.objects.get(user=request.user)

    if request.method == 'POST':
        # Procesar el formulario de agregar paciente
        if 'rut' in request.POST:
            rut = request.POST.get('rut')
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            email = request.POST.get('email')
            fono = request.POST.get('tlf')
            
            try:
                Paciente.objects.create(usuario=usuario, rut=rut, nombre=nombre, apellido=apellido, email=email, fono=fono)
            except IntegrityError:
                error_message = "El correo ya existe"
        
        # Procesar el formulario de enviar mensaje
        elif 'contenido' in request.POST:
            form_mensaje = MensajeForm(request.POST)
            if form_mensaje.is_valid():
                mensaje = form_mensaje.save(commit=False)
                mensaje.remitente = request.user
                mensaje.save()
                messages.success(request, 'Mensaje enviado correctamente.')

        # Procesar eliminación de pacientes
        elif 'delete_paciente' in request.POST:
            pacientes_ids = request.POST.getlist('paciente_ids')
            Paciente.objects.filter(rut__in=pacientes_ids, usuario=usuario).delete()

    # Obtener la lista de pacientes
    pacientes = Paciente.objects.filter(usuario=usuario)

    context = {
        'pacientes': pacientes,
        'mensajes': mensajes,
        'form_mensaje': form_mensaje,
        'error_message': error_message
    }
    
    return render(request, 'agregr_paciente.html', context)

                
               

        

def iniciar_sesion(request):
    try:
        if request.method == 'POST':
            usuario = request.POST.get('usuario')
            contraseña = request.POST.get('password')
            user = authenticate(request, username=usuario, password=contraseña)





            if user is not None:
                login(request, user)
                return redirect('inicio')  # Redirige a la página de inicio después de un inicio de sesión exitoso
            else:
                return render(request, 'login.html', {'mensaje': 'Usuario o contraseña incorrectos'})
        elif request.method == 'GET':
            return render(request, 'login.html')
    except Exception as error:
        print(error)
        return render(request, 'login.html', {'mensaje': 'Ocurrió un error. Inténtalo de nuevo.'})
    
    
    
    
def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')

def enviar_mensaje(request):
    if request.method == 'POST':
        form = MensajeForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.remitente = request.user
            mensaje.save()
            messages.success(request, 'Mensaje enviado correctamente.')
    
    
            return redirect('enviar_mensaje')
    elif request.method == 'GET':
        mensajes = Mensaje.objects.filter(destinatario=request.user).order_by('-fecha_envio')
        return render(request, 'recibidos.html', {'mensajes': mensajes})            
            
    else:
        form = MensajeForm()
    return render(request, 'mensaje.html', {'form': form})


@login_required
def mensajes_recibidos(request):
    mensajes = Mensaje.objects.filter(destinatario=request.user).order_by('-fecha_envio')
    return render(request, 'recibidos.html', {'mensajes': mensajes})            


def listar_pacientes(request):
    usuario = Usuario.objects.get(user=request.user)  # Obtén la instancia de Usuario asociada al usuario autenticado
    
    # Filtra los pacientes asociados al usuario de Django
    pacientes = Paciente.objects.filter(usuario=usuario)
    
    return render(request, 'agregr_paciente.html', {'pacientes': pacientes})







def guardar_nombre_medicamento(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        nombre_medicamento = data.get('nombre_medicamento')
        if nombre_medicamento:
            nueva_carta = Carta(nombre=nombre_medicamento)
            nueva_carta.save()
            return JsonResponse({'success': True, 'message': 'Nombre de medicamento guardado exitosamente.'})
        else:
            return JsonResponse({'success': False, 'message': 'Nombre de medicamento no proporcionado.'})
    return render(request, 'carro1.html')  # Ajusta el nombre de tu template




    

def miFuncion (request):
    return render(request,'nuevo.html')