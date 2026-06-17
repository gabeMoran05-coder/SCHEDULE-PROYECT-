from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render


class CustomLoginView(LoginView):
    template_name = "usuarios/login.html"
    redirect_authenticated_user = True


@login_required
def perfil(request):
    return render(request, "usuarios/perfil.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("usuarios:login")
