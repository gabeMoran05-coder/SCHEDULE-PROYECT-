from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def sort_url(context, field):
    request = context["request"]
    params = request.GET.copy()
    current_sort = params.get("sort")
    current_dir = params.get("dir", "asc")
    params["sort"] = field
    params["dir"] = "desc" if current_sort == field and current_dir == "asc" else "asc"
    return f"?{params.urlencode()}"


@register.simple_tag(takes_context=True)
def sort_arrow(context, field):
    request = context["request"]
    if request.GET.get("sort") != field:
        return "↕"
    return "↑" if request.GET.get("dir", "asc") == "asc" else "↓"


@register.simple_tag(takes_context=True)
def status_url(context, estado):
    request = context["request"]
    params = request.GET.copy()
    if estado:
        params["estado"] = estado
    else:
        params.pop("estado", None)
    return f"?{params.urlencode()}"
