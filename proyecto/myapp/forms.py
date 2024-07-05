from django import forms
from .models import Paciente
from .models import Mensaje,Usuario





    
class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['destinatario', 'contenido']        