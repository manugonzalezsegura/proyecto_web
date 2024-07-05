from django.urls import path
from . import views
from .views import  gestionar_pacientes_y_mensajes
urlpatterns = [
    path('',views.home,name='inicio'),
    path('registro/', views.registro, name='registro'),
    path('agregr_paciente/', views.gestionar_pacientes_y_mensajes, name='addPaciente'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='salir'),
    path('enviar_mensaje/', views.enviar_mensaje, name='enviar_mensaje'),
    path('recibidos/', views.mensajes_recibidos, name='recibidos'),
    path('listar/',views.listar_pacientes,name='listar'),
    path('nuevo',views.miFuncion ),
    path('medicamento/', views.medicamento, name='medicamento'),
     path('guardar-nombre-medicamento/', views.guardar_nombre_medicamento, name='guardar_nombre_medicamento'),
     path('coso/', views.coso, name='coso'),
]






