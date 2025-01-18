from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Materia(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    icone = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.nome
        
    def get_progresso(self, user):
        # Calcula o progresso do usuário nesta matéria
        total_recursos = Recurso.objects.filter(materia=self).count()
        concluidos = RecursoUsuario.objects.filter(
            usuario=user,
            recurso__materia=self,
            concluido=True
        ).count()
        return (concluidos / total_recursos * 100) if total_recursos > 0 else 0

class Recurso(models.Model):
    TIPOS = [
        ('video', 'Videoaula'),
        ('pdf', 'PDF'),
        ('exercicio', 'Exercício'),
        ('resumo', 'Resumo'),
    ]
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    url = models.URLField()
    thumbnail = models.URLField(blank=True)
    duracao = models.CharField(max_length=20, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('Tag', blank=True)
    visualizacoes = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.titulo
        
    @property
    def tipo_class(self):
        return {
            'video': 'primary',
            'pdf': 'danger',
            'exercicio': 'success',
            'resumo': 'info'
        }.get(self.tipo, 'secondary')
        
    @property
    def tipo_icon(self):
        return {
            'video': 'fa-play-circle',
            'pdf': 'fa-file-pdf',
            'exercicio': 'fa-tasks',
            'resumo': 'fa-book'
        }.get(self.tipo, 'fa-file')

class Tag(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nome
        
    @property
    def count(self):
        return self.recurso_set.count()

class RecursoUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE)
    favorito = models.BooleanField(default=False)
    concluido = models.BooleanField(default=False)
    ultima_visualizacao = models.DateTimeField(auto_now=True)
    avaliacao = models.PositiveSmallIntegerField(null=True, blank=True)
    
    class Meta:
        unique_together = ['usuario', 'recurso']

class Favorito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    concurso = models.ForeignKey('Concurso', on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(default=datetime.utcnow)
    
    class Meta:
        unique_together = ('usuario', 'concurso')

class Alerta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    concurso = models.ForeignKey('Concurso', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20)  # email, push, sms
    antecedencia = models.IntegerField()  # dias
    eventos = models.CharField(max_length=100)  # lista de eventos separados por vírgula
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(default=datetime.utcnow)
