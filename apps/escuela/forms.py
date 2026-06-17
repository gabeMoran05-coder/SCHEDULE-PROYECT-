from django import forms

from .models import Alumno, AsignacionDocenteMateria, CicloEscolar, ContratoDocente, Docente, Grupo, Institucion, Materia, Tutor


class AlumnoForm(forms.ModelForm):
    tutor_nombre = forms.CharField(label="Nombre del tutor", max_length=120, required=False)
    tutor_telefono = forms.CharField(label="Telefono del tutor", max_length=20, required=False)
    tutor_correo = forms.EmailField(label="Correo del tutor", required=False)

    class Meta:
        model = Alumno
        fields = ["matricula", "nombres", "apellidos", "fecha_nacimiento", "activo"]
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
        fields = ["ciclo", "grado", "letra", "turno", "aula_base", "tutor", "activo"]

    def __init__(self, *args, institucion=None, **kwargs):
        super().__init__(*args, **kwargs)
        if institucion:
            self.fields["ciclo"].queryset = self.fields["ciclo"].queryset.filter(institucion=institucion)
            self.fields["tutor"].queryset = self.fields["tutor"].queryset.filter(institucion=institucion)


class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ["clave", "nombre", "grado", "horas_semanales", "activo"]

    def __init__(self, *args, institucion=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.institucion = institucion

    def clean_clave(self):
        clave = self.cleaned_data["clave"]
        exists = Materia.objects.filter(institucion=self.institucion, clave=clave)
        if self.instance.pk:
            exists = exists.exclude(pk=self.instance.pk)
        if self.institucion and exists.exists():
            raise forms.ValidationError("Ya existe una materia con esta clave en la escuela seleccionada.")
        return clave


class InstitucionForm(forms.ModelForm):
    class Meta:
        model = Institucion
        fields = ["nombre", "clave_cct", "direccion", "activa"]


class CicloEscolarForm(forms.ModelForm):
    class Meta:
        model = CicloEscolar
        fields = ["nombre", "fecha_inicio", "fecha_fin", "activo"]
        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, institucion=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.institucion = institucion

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"]
        if self.institucion and CicloEscolar.objects.filter(institucion=self.institucion, nombre=nombre).exists():
            raise forms.ValidationError("Ya existe un ciclo con ese nombre en la escuela seleccionada.")
        return nombre


class ContratoDocenteForm(forms.ModelForm):
    class Meta:
        model = ContratoDocente
        fields = ["docente", "institucion", "ciclo", "horas_semanales", "es_tutor", "activo"]


class AsignacionMateriaForm(forms.ModelForm):
    class Meta:
        model = AsignacionDocenteMateria
        fields = ["materia", "grupos", "horas_semanales", "notas"]
        widgets = {
            "grupos": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, ciclo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["materia"].queryset = Materia.objects.all().order_by("grado", "nombre")
        self.fields["materia"].label = "Materia"
        self.fields["grupos"].label = "Grupos donde la imparte"
        self.fields["horas_semanales"].label = "Horas por semana"
        self.fields["notas"].label = "Notas"
        self.fields["horas_semanales"].min_value = 1
        self.fields["horas_semanales"].max_value = 40
        if ciclo:
            self.fields["materia"].queryset = self.fields["materia"].queryset.filter(institucion=ciclo.institucion)
            self.fields["grupos"].queryset = Grupo.objects.filter(ciclo=ciclo).order_by("grado", "letra")
