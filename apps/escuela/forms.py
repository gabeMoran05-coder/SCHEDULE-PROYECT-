from django import forms

from .models import Alumno, ContratoDocente, Docente, Grupo, Institucion, Materia, Tutor


class AlumnoForm(forms.ModelForm):
    tutor_nombre = forms.CharField(label="Nombre del tutor", max_length=120, required=False)
    tutor_telefono = forms.CharField(label="Telefono del tutor", max_length=20, required=False)
    tutor_correo = forms.EmailField(label="Correo del tutor", required=False)

    class Meta:
        model = Alumno
        fields = ["institucion", "matricula", "nombres", "apellidos", "fecha_nacimiento", "activo"]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
        }

    def save(self, commit=True):
        alumno = super().save(commit=False)
        tutor_nombre = self.cleaned_data.get("tutor_nombre")

        if tutor_nombre:
            tutor, _ = Tutor.objects.get_or_create(
                nombre=tutor_nombre,
                defaults={
                    "telefono": self.cleaned_data.get("tutor_telefono", ""),
                    "correo": self.cleaned_data.get("tutor_correo", ""),
                },
            )
            alumno.tutor = tutor

        if commit:
            alumno.save()
        return alumno


class DocenteForm(forms.ModelForm):
    horas_semanales = forms.IntegerField(label="Horas semanales", min_value=0, max_value=60, initial=0)
    es_tutor = forms.BooleanField(label="Es tutor", required=False)

    class Meta:
        model = Docente
        fields = ["numero_empleado", "nombres", "apellidos", "correo", "telefono", "activo"]

    def clean_numero_empleado(self):
        numero = self.cleaned_data.get("numero_empleado")
        return numero or None


class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ["ciclo", "grado", "letra", "turno", "aula_base", "tutor"]


class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ["clave", "nombre", "grado"]


class InstitucionForm(forms.ModelForm):
    class Meta:
        model = Institucion
        fields = ["nombre", "clave_cct", "direccion", "activa"]


class ContratoDocenteForm(forms.ModelForm):
    class Meta:
        model = ContratoDocente
        fields = ["docente", "institucion", "ciclo", "horas_semanales", "es_tutor", "activo"]
