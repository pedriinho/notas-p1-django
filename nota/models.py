from django.db import models

# Create your models here.

class Aluno(models.Model):
    nome = models.CharField(max_length=100)
    id_huxley = models.IntegerField(default=0)
    turma = models.CharField(null=True, max_length=2)

    prova1 = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    lista1 = models.DecimalField(default=0.0, max_digits=4, decimal_places=0)
    lista2 = models.DecimalField(default=0.0, max_digits=4, decimal_places=0)

    prova2 = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    lista3 = models.DecimalField(default=0.0, max_digits=4, decimal_places=0)
    lista4 = models.DecimalField(default=0.0, max_digits=4, decimal_places=0)

    prova3 = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    lista5 = models.DecimalField(default=0.0, max_digits=4, decimal_places=0)
    lista6 = models.DecimalField(default=0.0, max_digits=4, decimal_places=0)

    prova4 = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    lista7 = models.DecimalField(default=0.0, max_digits=4, decimal_places=0)
    lista8 = models.DecimalField(default=0.0, max_digits=4, decimal_places=0)

    def __str__(self):
        return self.nome
    

class NotaAluno(models.Model):
    nome = models.CharField(max_length=100)
    id_huxley = models.IntegerField(default=0)
    turma = models.CharField(null=True, max_length=2)
    
    ab1 = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    ab2 = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    reav = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    final = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    mediaFinal = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    situacao = models.CharField(max_length=20, default='EM ANÁLISE')

    def __str__(self):
        return self.nome

class DataAttNota(models.Model):
    registro = models.CharField(max_length=150)

    def __str__(self):
        return self.registro
    
class Turma(models.Model):
    turma = models.CharField(max_length=4)
    id_prova1 = models.IntegerField(default=0)
    id_prova2 = models.IntegerField(default=0)
    id_prova3 = models.IntegerField(default=0)
    id_prova4 = models.IntegerField(default=0)

    id_lista1 = models.IntegerField(default=0)
    id_lista2 = models.IntegerField(default=0)
    id_lista3 = models.IntegerField(default=0)
    id_lista4 = models.IntegerField(default=0)
    id_lista5 = models.IntegerField(default=0)
    id_lista6 = models.IntegerField(default=0)
    id_lista7 = models.IntegerField(default=0)
    id_lista8 = models.IntegerField(default=0)

    id_reav = models.IntegerField(default=0)
    id_final = models.IntegerField(default=0)

    def __str__(self):
        return self.turma