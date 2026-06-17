from .models import Institucion
from .selectors import get_selected_institution


def school_context(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {}

    return {
        "nav_instituciones": Institucion.objects.filter(activa=True).order_by("nombre"),
        "nav_selected_institution": get_selected_institution(request),
    }
