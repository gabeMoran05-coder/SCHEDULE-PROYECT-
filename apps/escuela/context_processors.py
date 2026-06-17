from .models import CicloEscolar, Institucion
from .selectors import get_selected_cycle, get_selected_institution


def school_context(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {}

    institucion = get_selected_institution(request)

    return {
        "nav_instituciones": Institucion.objects.filter(activa=True).order_by("nombre"),
        "nav_selected_institution": institucion,
        "nav_ciclos": CicloEscolar.objects.filter(institucion=institucion).order_by("-nombre") if institucion else [],
        "nav_selected_cycle": get_selected_cycle(request),
    }
