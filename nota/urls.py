from django.urls import path

from .views import index, notasAcumuladas, resolution, searchNotaGeral, searchNotaIndividual, updateGradesThreading, changeClass, addTurmaAluno

urlpatterns = [
    path('', index, name='index'),
    path('init_threading/', updateGradesThreading, name='threading'),
    path('resolution/', resolution, name='resolution'),
    path('notas/', notasAcumuladas, name='notas'),
    path('resolution/search/', searchNotaIndividual, name='searchindividual'),
    path('notas/search/', searchNotaGeral, name='searchgeral'),
    path('change_class/', changeClass, name='change_class'),
    path('add_turma_aluno/', addTurmaAluno, name='add_turma_aluno'),
]