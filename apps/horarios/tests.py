from django.test import TestCase


class HorariosSmokeTest(TestCase):
    def test_horarios_requires_login(self):
        response = self.client.get("/horarios/")
        self.assertEqual(response.status_code, 302)
