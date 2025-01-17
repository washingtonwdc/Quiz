# Documentação do Setup Inicial

## Estrutura de Arquivos
```
Quiz/
│
├── app/
│   ├── __init__.py
│   ├── routes/
│   │   └── main.py
│   └── templates/
│       └── base.html
│
├── provas/
│   └── provas.json
│
├── config.py
├── run.py
└── requirements.txt
```

## Configuração do Ambiente

1. Criar ambiente virtual:
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

2. Instalar dependências:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Arquivos Principais

### requirements.txt
```text
Flask>=2.2.0
flask-pymongo>=2.3.0
python-dotenv>=0.19.0
Werkzeug>=2.2.3
Jinja2>=3.0.0
MarkupSafe>=2.0.0
```

### .env
```
FLASK_APP=run.py
FLASK_ENV=development
MONGO_URI=mongodb://localhost:27017/quiz
```

## Estrutura do Banco de Dados

### Coleção: provas
- id: string
- nome: string
- banca: string
- ano: number
- nivel: string
- cargo: string
- questoes: array

### Coleção: questoes
- id: string
- banca: string
- prova_id: string
- questao_numero: string
- area: string
- enunciado: string
- alternativas: array
- resposta_correta: string

## Como Executar

1. Ativar ambiente virtual:
```powershell
.\venv\Scripts\Activate
```

2. Executar aplicação:
```powershell
python run.py
```

3. Acessar:
- http://localhost:5000

## Status Atual

### Funcionando:
- ✅ Configuração básica do Flask
- ✅ Conexão com MongoDB
- ✅ Template base
- ✅ Rota principal

### Próximos Passos:
1. Implementar autenticação
2. Criar CRUD de questões
3. Desenvolver interface para simulados
4. Implementar sistema de pontuação

## Notas
- MongoDB deve estar rodando em localhost:27017
- Banco de dados será criado automaticamente na primeira execução
- Estrutura modular permite fácil expansão
