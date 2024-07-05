

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Usuario

class UsuarioTestCase(TestCase):
    def setUp(self):
        # Configuración inicial de datos para las pruebas
        self.medico_user = User.objects.create(username='medico1', password='password')
        self.medico = Usuario.objects.create(user=self.medico_user, tipo_usuario='medico')

        self.paciente_user1 = User.objects.create(username='paciente1', password='password')
        self.paciente1 = Usuario.objects.create(user=self.paciente_user1, tipo_usuario='paciente', medico=self.medico)

        self.paciente_user2 = User.objects.create(username='paciente2', password='password')
        self.paciente2 = Usuario.objects.create(user=self.paciente_user2, tipo_usuario='paciente', medico=self.medico)

    def test_pacientes_del_medico(self):
        # Verificar que el médico tiene los pacientes correctos asignados
        pacientes_del_medico = self.medico.pacientes.all()
        self.assertEqual(pacientes_del_medico.count(), 2)

        # Verificar que los pacientes están correctamente asociados al médico
        self.assertIn(self.paciente1, pacientes_del_medico)
        self.assertIn(self.paciente2, pacientes_del_medico)

