# Estrutura do Site de Estudos

## Menu Principal
1. **Área de Estudos**
  - Concursos Públicos
  - Concursos Militares
  - OAB
  - ENEM
  - Vestibular

2. **Recursos de Estudo**
  - Banco de Questões
  - Videoaulas e Materiais
  - Simulados
  - Guias de Estudo
  - Provas Anteriores
  - Aulas ao Vivo

3. **Catálogo**
  - Disciplinas
  - Instituições
  - Bancas Examinadoras
  - Cargos
  - Professores

4. **Informações**
  - Notícias
  - Planos e Assinaturas
  - Suporte
  - Livraria

## Funcionalidades Principais

### Página Inicial
- Sistema de Busca Inteligente
- Destaques e Promoções
- Acesso Rápido
- Métricas e Depoimentos

### Sistema de Questões
- Filtros Avançados
- Gabarito Comentado
- Sistema de Comentários
- Estatísticas de Resolução
- Cadernos Personalizados
- Anotações

### Área do Usuário
- Dashboard de Desempenho
- Simulados Personalizados
- Sistema de Notificações
- Cadernos Salvos
- Histórico de Estudos

### Recursos Técnicos
- Autenticação Social
- Sistema de Pagamentos
- Reportar Erros
- Solicitação de Comentários
- Política de Privacidade


Quiz/
├── manage.py
├── requirements.txt
├── quiz/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── ...
├── apps/
│   ├── __init__.py
│   ├── concursos/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── ...
│   ├── exames/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── ...
│   ├── recursos/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── ...
│   └── ...
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── base.html
│   ├── index.html
│   └── ...
└── ...