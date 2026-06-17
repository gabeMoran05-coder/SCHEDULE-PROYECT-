from .models import CicloEscolar, Institucion


def get_selected_institution(request):
    selected_id = request.session.get("selected_institution_id")
    queryset = Institucion.objects.filter(activa=True).order_by("nombre")

    if selected_id:
        institucion = queryset.filter(id=selected_id).first()
        if institucion:
            return institucion

    institucion = queryset.first() or Institucion.objects.order_by("nombre").first()
    if institucion:
        request.session["selected_institution_id"] = institucion.id
    return institucion


def get_selected_cycle(request):
    institucion = get_selected_institution(request)
    if not institucion:
        return None
    return (
        CicloEscolar.objects.filter(institucion=institucion, activo=True)
        .select_related("institucion")
        .first()
    )
