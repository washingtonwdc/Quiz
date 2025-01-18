from djongo import models
from django.contrib.auth.models import User

class Questao(models.Model):
    _id = models.ObjectIdField()
    titulo = models.CharField(max_length=200)
    enunciado = models.TextField()
    dificuldade = models.CharField(max_length=1)
    alternativas = models.JSONField()
    resposta_correta = models.CharField(max_length=1)
    explicacao = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'questoes'

    def __str__(self):
        return self.titulo

class Resposta(models.Model):
    _id = models.ObjectIdField()
    usuario_id = models.CharField(max_length=100)
    questao_id = models.CharField(max_length=100)
    resposta = models.CharField(max_length=1)
    correta = models.BooleanField()
    data = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'respostas'
