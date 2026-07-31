from django import forms

from .models import Alumno, AsignacionDocenteMateria, CicloEscolar, ContratoDocente, Docente, DocumentoAlumno, Grupo, Institucion, KardexDocente, Materia, Tutor


class AlumnoForm(forms.ModelForm):
    tutor_nombre = forms.CharField(label="Nombre del tutor", max_length=120, required=False)
    tutor_parentesco = forms.CharField(label="Parentesco del tutor", max_length=40, required=False)
    tutor_telefono = forms.CharField(label="Telefono del tutor", max_length=20, required=False)
    tutor_telefono_alterno = forms.CharField(label="Telefono alterno del tutor", max_length=20, required=False)
    tutor_correo = forms.EmailField(label="Correo del tutor", required=False)
    tutor_direccion = forms.CharField(label="Direccion del tutor", max_length=220, required=False)
    tutor_ocupacion = forms.CharField(label="Ocupacion del tutor", max_length=100, required=False)

    class Meta:
        model = Alumno
        fields = [
            "matricula",
            "nombres",
            "apellidos",
            "fecha_nacimiento",
            "curp",
            "genero",
            "direccion",
            "telefono",
            "contacto_emergencia",
            "telefono_emergencia",
            "parentesco_emergencia",
            "tipo_sangre",
            "numero_seguridad_social",
            "institucion_medica",
            "alergias",
            "padecimientos",
            "medicamentos",
            "observaciones_medicas",
            "activo",
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
            "alergias": forms.Textarea(attrs={"rows": 3}),
            "padecimientos": forms.Textarea(attrs={"rows": 3}),
            "medicamentos": forms.Textarea(attrs={"rows": 3}),
            "observaciones_medicas": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tutor = self.instance.tutor if self.instance and self.instance.pk else None
        if tutor:
            self.fields["tutor_nombre"].initial = tutor.nombre
            self.fields["tutor_parentesco"].initial = tutor.parentesco
            self.fields["tutor_telefono"].initial = tutor.telefono
            self.fields["tutor_telefono_alterno"].initial = tutor.telefono_alterno
            self.fields["tutor_correo"].initial = tutor.correo
            self.fields["tutor_direccion"].initial = tutor.direccion
            self.fields["tutor_ocupacion"].initial = tutor.ocupacion

    def save(self, commit=True):
        alumno = super().save(commit=False)
        tutor_nombre = self.cleaned_data.get("tutor_nombre")

        if tutor_nombre:
            tutor = alumno.tutor or Tutor(nombre=tutor_nombre)
            tutor.nombre = tutor_nombre
            tutor.parentesco = self.cleaned_data.get("tutor_parentesco", "")
            tutor.telefono = self.cleaned_data.get("tutor_telefono", "")
            tutor.telefono_alterno = self.cleaned_data.get("tutor_telefono_alterno", "")
            tutor.correo = self.cleaned_data.get("tutor_correo", "")
            tutor.direccion = self.cleaned_data.get("tutor_direccion", "")
            tutor.ocupacion = self.cleaned_data.get("tutor_ocupacion", "")
            if commit:
                tutor.save()
            alumno.tutor = tutor

        if commit:
            if alumno.tutor and not alumno.tutor.pk:
                alumno.tutor.save()
            alumno.save()
        return alumno


class DocumentoAlumnoForm(forms.ModelForm):
    class Meta:
        model = DocumentoAlumno
        fields = ["tipo", "nombre", "archivo", "notas"]


class DocenteForm(forms.ModelForm):
    horas_semanales = forms.IntegerField(label="Horas semanales", min_value=0, max_value=60, initial=0)
    es_tutor = forms.BooleanField(label="Es tutor", required=False)

    class Meta:
        model = Docente
        fields = ["numero_empleado", "nombres", "apellidos", "correo", "telefono", "foto", "activo"]
        widgets = {
            "foto": forms.FileInput(attrs={"accept": "image/*"}),
        }

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


class MovimientoDocenteForm(forms.Form):
    motivo = forms.ChoiceField(label="Motivo", choices=KardexDocente.MotivoMovimiento.choices)
    documento_referencia = forms.CharField(label="Documento o folio", max_length=80, required=False)
    descripcion = forms.CharField(
        label="Observaciones",
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Explica por que se oculta, da de baja o reincorpora al docente.",
    )


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
