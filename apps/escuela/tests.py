from django.contrib.auth.models import User
from django.test import TestCase


class EscuelaSmokeTest(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get("/escuela/")
        self.assertEqual(response.status_code, 302)

    def test_dashboard_loads_for_user(self):
        User.objects.create_user(username="demo", password="demo12345")
        self.client.login(username="demo", password="demo12345")
        response = self.client.get("/escuela/")
        self.assertEqual(response.status_code, 200)
