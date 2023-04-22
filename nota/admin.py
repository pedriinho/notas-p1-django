from django.contrib import admin

from .models import Aluno, NotaAluno, DataAttNota, Turma

# Register your models here.

admin.site.register(Aluno)
admin.site.register(NotaAluno)
admin.site.register(DataAttNota)
admin.site.register(Turma)