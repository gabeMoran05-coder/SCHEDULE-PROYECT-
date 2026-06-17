from django.test import TestCase


class UsuariosSmokeTest(TestCase):
    def test_login_page_loads(self):
        response = self.client.get("/usuarios/login/")
        self.assertEqual(response.status_code, 200)
