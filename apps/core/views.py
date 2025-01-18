from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .forms import UserRegistrationForm
from apps.concursos.models import Questao
from apps.recursos.models import Simulado

@login_required
def dashboard(request):
    context = {
        'total_questoes': Questao.objects.count(),
        'questoes_respondidas': request.user.respostas.count(),
        'simulados_realizados': Simulado.objects.filter(usuario=request.user).count(),
        'desempenho': calcular_desempenho(request.user)
    }
    return render(request, 'core/dashboard.html', context)

def calcular_desempenho(user):
    respostas = user.respostas.all()
    if not respostas:
        return 0
    acertos = respostas.filter(correta=True).count()
    return (acertos / respostas.count()) * 100
