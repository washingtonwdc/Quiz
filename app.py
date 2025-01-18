from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask import Blueprint
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para sessões e flash messages

# Blueprints
concursos = Blueprint('concursos', __name__)
exames = Blueprint('exames', __name__)
bancas = Blueprint('bancas', __name__)
simulados_bp = Blueprint('simulados', __name__, url_prefix='/simulados')

# Rotas principais
@app.route('/')
def index():
    return render_template('index.html')

# Adicionar classes para gerenciar o estado do simulado
class Questao:
    def __init__(self, id, texto, alternativas, resposta_correta, area, nivel, banca=None):
        self.id = id
        self.texto = texto
        self.alternativas = alternativas
        self.resposta_correta = resposta_correta
        self.area = area
        self.nivel = nivel
        self.banca = banca
        self.tempo_medio = 0
        self.taxa_acerto = 0

class SimuladoStats:
    def __init__(self):
        self.acertos_por_area = defaultdict(int)
        self.total_por_area = defaultdict(int)
        self.tempo_por_questao = {}
        self.sequencia_acertos = 0
        self.maior_sequencia = 0

    def registrar_resposta(self, questao, resposta, tempo_gasto):
        self.tempo_por_questao[questao.id] = tempo_gasto
        self.total_por_area[questao.area] += 1
        
        if resposta == questao.resposta_correta:
            self.acertos_por_area[questao.area] += 1
            self.sequencia_acertos += 1
            self.maior_sequencia = max(self.maior_sequencia, self.sequencia_acertos)
        else:
            self.sequencia_acertos = 0

class Simulado:
    def __init__(self, id, titulo, questoes, tempo_total):
        self.id = id
        self.titulo = titulo
        self.questoes = questoes
        self.tempo_total = tempo_total
        self.tempo_inicio = None
        self.respostas = {}
        self.marcadas_revisao = set()
        self.anotacoes = {}
        self.stats = SimuladoStats()
        self.ultima_questao_respondida = 0
        self.questao_atual = 0

    def responder_questao(self, questao_id, resposta, tempo_gasto):
        self.respostas[questao_id] = resposta
        self.stats.registrar_resposta(
            self.questoes[questao_id-1], 
            resposta, 
            tempo_gasto
        )
        self.ultima_questao_respondida = max(self.ultima_questao_respondida, questao_id)
        return resposta == self.questoes[questao_id-1].resposta_correta

    def get_dict(self):
        """Retorna uma versão serializada do simulado para o template"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'total_questoes': len(self.questoes),
            'tempo_total': self.tempo_total
        }

    def get_questao_dict(self, numero):
        """Retorna uma versão serializada da questão para o template"""
        questao = self.questoes[numero - 1]
        return {
            'id': questao.id,
            'numero': numero,
            'texto': questao.texto,
            'alternativas': questao.alternativas,
            'area': questao.area,
            'nivel': questao.nivel
        }

# Dicionário para armazenar simulados ativos
simulados_ativos = {}

# Alterar a rota do simulados no blueprint
@simulados_bp.route('/')
def index():  # Renomeado de 'simulados' para 'index'
    # Dados simulados para exemplo
    simulado_atual = {
        'titulo': 'Simulado PF - Agente',
        'total_questoes': 60,
        'respondidas': 36,
        'acertos': 28,
        'tempo_restante': '02:15:33',
        'progresso': 60
    }
    
    historico = [
        {
            'data': '15/01/2024',
            'titulo': 'PF - Agente',
            'questoes': '60/60',
            'acertos': '48 (80%)',
            'tempo': '4h12min'
        },
        {
            'data': '10/01/2024',
            'titulo': 'Direito Constitucional',
            'questoes': '30/30',
            'acertos': '25 (83%)',
            'tempo': '1h45min'
        }
    ]
    
    return render_template('simulados/index.html', 
                         simulado_atual=simulado_atual,
                         historico=historico)

@simulados_bp.route('/questao/<int:numero>')
def questao(numero):
    simulado_id = session.get('simulado_atual')
    if not simulado_id or simulado_id not in simulados_ativos:
        flash('Nenhum simulado em andamento.', 'warning')
        return redirect(url_for('simulados.index'))
    
    simulado = simulados_ativos[simulado_id]
    if not simulado.tempo_inicio:
        simulado.tempo_inicio = datetime.now().timestamp()
    
    # Verificar se o número da questão é válido
    if numero < 1 or numero > len(simulado.questoes):
        flash('Questão inválida.', 'error')
        return redirect(url_for('simulados.index'))
    
    tempo_decorrido = int(datetime.now().timestamp() - simulado.tempo_inicio)
    tempo_restante = max(0, simulado.tempo_total - tempo_decorrido)
    
    # Se o tempo acabou, redirecionar para o resultado
    if tempo_restante <= 0:
        return redirect(url_for('simulados.resultado_simulado', simulado_id=simulado.id))
    
    return render_template('simulados/questao.html',
                         simulado=simulado.get_dict(),
                         questao=simulado.get_questao_dict(numero),
                         total_questoes=len(simulado.questoes),
                         tempo_restante=formatar_tempo(tempo_restante),
                         tempo_restante_segundos=tempo_restante,
                         respondidas=list(simulado.respostas.keys()),  # Converter para lista
                         marcadas_revisao=list(simulado.marcadas_revisao),  # Converter para lista
                         anotacao_atual=simulado.anotacoes.get(numero, ''))

@simulados_bp.route('/iniciar', methods=['POST'])
def iniciar_simulado():
    tipo = request.form.get('tipo')
    materia = request.form.get('materia')
    tempo_total = int(request.form.get('tempo', 7200))
    
    # Gerar questões baseadas no tipo e matéria
    questoes = gerar_questoes(tipo, materia)
    
    simulado = Simulado(
        id=len(simulados_ativos) + 1,
        titulo=f"Simulado {tipo.title()} - {materia}",
        questoes=questoes,
        tempo_total=tempo_total
    )
    simulado.tempo_inicio = datetime.now().timestamp()
    
    simulados_ativos[simulado.id] = simulado
    session['simulado_atual'] = simulado.id
    
    # Redirecionar para a primeira questão
    return redirect(url_for('simulados.questao', numero=1))

@simulados_bp.route('/responder/<int:questao_id>', methods=['POST'])
def responder_questao(questao_id):
    simulado = simulados_ativos.get(session.get('simulado_atual'))
    if not simulado:
        return redirect(url_for('simulados.index'))
    
    resposta = request.form.get('resposta')
    tempo_gasto = request.form.get('tempo_gasto', 0)
    
    if resposta:
        questao = simulado.questoes[questao_id - 1]  # Pegar o objeto Questao
        acertou = simulado.responder_questao(questao_id, int(resposta), int(tempo_gasto))
        flash('Resposta registrada!', 'success' if acertou else 'warning')
    
    proxima_questao = questao_id + 1
    if proxima_questao > len(simulado.questoes):
        return redirect(url_for('simulados.resultado_simulado', simulado_id=simulado.id))
    
    return redirect(url_for('simulados.questao', numero=proxima_questao))

@simulados_bp.route('/marcar-revisao/<int:questao_id>', methods=['POST'])
def marcar_revisao(questao_id):
    simulado = simulados_ativos.get(session.get('simulado_atual'))
    if not simulado:
        return jsonify({'success': False})
    
    if questao_id in simulado.marcadas_revisao:
        simulado.marcadas_revisao.remove(questao_id)
        marcada = False
    else:
        simulado.marcadas_revisao.add(questao_id)
        marcada = True
    
    return jsonify({'success': True, 'marcada': marcada})

@simulados_bp.route('/salvar-anotacao/<int:questao_id>', methods=['POST'])
def salvar_anotacao(questao_id):
    simulado = simulados_ativos.get(session.get('simulado_atual'))
    if not simulado:
        return jsonify({'success': False})
    
    dados = request.get_json()
    simulado.anotacoes[questao_id] = dados.get('texto', '')
    
    return jsonify({'success': True})

@simulados_bp.route('/status/<int:simulado_id>')
def status_simulado(simulado_id):
    simulado = simulados_ativos.get(simulado_id)
    if not simulado:
        return jsonify({'error': 'Simulado não encontrado'}), 404
        
    stats = simulado.stats
    return jsonify({
        'progresso': len(simulado.respostas) / len(simulado.questoes) * 100,
        'acertos_por_area': dict(stats.acertos_por_area),
        'total_por_area': dict(stats.total_por_area),
        'maior_sequencia': stats.maior_sequencia,
        'sequencia_atual': stats.sequencia_acertos,
        'tempo_medio': sum(stats.tempo_por_questao.values()) / len(stats.tempo_por_questao) if stats.tempo_por_questao else 0
    })

def formatar_tempo(segundos):
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segundos = segundos % 60
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

def gerar_questoes(tipo, materia):
    # Criar objetos Questao ao invés de dicionários
    questoes = []
    for i in range(1, 61):
        alternativas = [
            {'id': j, 'texto': f"Alternativa {j}"} 
            for j in range(1, 6)
        ]
        questao = Questao(
            id=i,
            texto=f"Questão {i} sobre {materia}",
            alternativas=alternativas,
            resposta_correta=3,  # Exemplo
            area=materia,
            nivel='Médio'  # Exemplo
        )
        questoes.append(questao)
    return questoes

# Mover a rota de resultado para o blueprint também
@simulados_bp.route('/resultado/<int:simulado_id>')
def resultado_simulado(simulado_id):
    # Simulando dados do resultado
    resultado = {
        'simulado_id': simulado_id,
        'percentual_acertos': 80,
        'acertos': 48,
        'total_questoes': 60,
        'tempo_total': '4h 12min',
        'tempo_medio': '4min 12s',
        'areas': [
            {
                'nome': 'Direito Constitucional',
                'acertos': 15,
                'total': 20,
                'percentual': 75
            },
            {
                'nome': 'Direito Administrativo',
                'acertos': 18,
                'total': 20,
                'percentual': 90
            },
            {
                'nome': 'Direito Penal',
                'acertos': 15,
                'total': 20,
                'percentual': 75
            }
        ],
        'pontos_fortes': [
            'Excelente desempenho em Direito Administrativo',
            'Bom tempo médio por questão',
            'Consistência nas respostas'
        ],
        'pontos_melhorar': [
            'Revisar tópicos de Direito Constitucional',
            'Melhorar gestão de tempo em questões complexas',
            'Praticar mais questões de Direito Penal'
        ],
        'materiais_recomendados': [
            {
                'titulo': 'Revisão Direito Constitucional',
                'descricao': 'Videoaula com principais pontos',
                'url': '#'
            },
            {
                'titulo': 'Exercícios Direito Penal',
                'descricao': 'Banco de questões comentadas',
                'url': '#'
            },
            {
                'titulo': 'Resumo Direito Administrativo',
                'descricao': 'Material complementar em PDF',
                'url': '#'
            }
        ]
    }
    
    return render_template('simulados/resultado.html', resultado=resultado)

@app.route('/busca')
def busca():
    query = request.args.get('q', '')
    return render_template('busca.html', query=query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

class User:
    def __init__(self, name, email, created_at):
        self.name = name
        self.email = email
        self.created_at = created_at

class Stats:
    def __init__(self, total_questions, correct_answers):
        self.total_questions = total_questions
        self.correct_answers = correct_answers
        self.accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0

@app.route('/perfil')
def perfil():
    if not session.get('user_id'):
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    # Simulando dados do usuário
    user = User('Usuário Exemplo', 'usuario@exemplo.com', datetime.now())
    stats = Stats(150, 120)
    activities = [
        {
            'title': 'Simulado ENEM',
            'description': 'Completou simulado com 80% de acerto',
            'date': '17/01/2024'
        },
        {
            'title': 'Questões de Português',
            'description': 'Praticou 20 questões',
            'date': '16/01/2024'
        }
    ]
    
    return render_template('perfil.html', user=user, stats=stats, activities=activities)

# Rotas para concursos
@concursos.route('/')
def index():
    return render_template('concursos/index.html')

@concursos.route('/<concurso_id>')
def detalhe(concurso_id):
    concursos_info = {
        'pf': {
            'titulo': 'Polícia Federal',
            'vagas': 1500,
            'salario': 12522.50,
            'escolaridade': 'Nível Superior',
            'materias': [
                {'nome': 'Direito Constitucional', 'aulas': 12},
                {'nome': 'Direito Administrativo', 'aulas': 10},
                {'nome': 'Direito Penal', 'aulas': 15}
            ],
            'cronograma': {
                'edital': 'Março/2024',
                'inscricoes': 'Abril/2024',
                'prova': 'Junho/2024'
            }
        },
        'rf': {
            'titulo': 'Receita Federal',
            'vagas': 699,
            'salario': 21029.09,
            'escolaridade': 'Nível Superior',
            'materias': [
                {'nome': 'Direito Tributário', 'aulas': 15},
                {'nome': 'Contabilidade', 'aulas': 12},
                {'nome': 'Legislação Aduaneira', 'aulas': 10}
            ],
            'cronograma': {
                'edital': 'Abril/2024',
                'inscricoes': 'Maio/2024',
                'prova': 'Julho/2024'
            }
        }
    }
    
    concurso_info = concursos_info.get(concurso_id)
    return render_template('concursos/detalhe.html', 
                         concurso_id=concurso_id, 
                         concurso_info=concurso_info)

# Rotas para exames
@exames.route('/')
def index():
    exames_data = {
        'progresso_geral': 75,
        'exames_concluidos': 12,
        'total_exames': 15,
        'media_acertos': 82,
        'proximo_exame': {
            'nome': 'ENEM 2024',
            'data': 'Novembro/2024',
            'dias': 45
        },
        'proximos_exames': [
            {
                'nome': 'ENEM 2024',
                'data': 'Novembro/2024',
                'inscricoes': 'Maio/2024',
                'status': 'Em breve'
            },
            {
                'nome': 'OAB XXXV',
                'data': 'Agosto/2024',
                'inscricoes': 'Junho/2024',
                'status': 'Previsto'
            }
        ],
        'materiais_estudo': [
            {
                'titulo': 'Redação ENEM',
                'descricao': 'Guia completo com exemplos',
                'duracao': '2h',
                'url': '#'
            },
            {
                'titulo': 'Questões OAB Comentadas',
                'descricao': 'Últimos 5 exames',
                'duracao': '4h',
                'url': '#'
            }
        ],
        'cronograma': [
            {
                'data': 'Janeiro/2024',
                'titulo': 'Início das aulas',
                'descricao': 'Começo do cronograma de estudos'
            },
            {
                'data': 'Março/2024',
                'titulo': 'Simulado Geral',
                'descricao': 'Primeira avaliação completa'
            }
        ]
    }
    
    disciplinas = [
        {'id': 1, 'nome': 'Matemática'},
        {'id': 2, 'nome': 'Português'},
        {'id': 3, 'nome': 'História'},
        {'id': 4, 'nome': 'Geografia'}
    ]
    
    exames = [
        {
            'id': 1,
            'nome': 'Simulado ENEM 1',
            'disciplina': 'Geral',
            'data': '25/02/2024',
            'duracao': 180
        },
        {
            'id': 2,
            'nome': 'Prova de Matemática',
            'disciplina': 'Matemática',
            'data': '01/03/2024',
            'duracao': 120
        }
    ]
    
    return render_template('exames/index.html', 
                         dados=exames_data,
                         disciplinas=disciplinas,
                         exames=exames)

@exames.route('/<exame_id>')
def detalhe(exame_id):
    # Simulando dados do exame
    exame = {
        'titulo': 'ENEM 2024',
        'descricao': 'Exame Nacional do Ensino Médio',
        'status': 'Em breve',
        'status_class': 'warning',
        'data': 'Novembro/2024',
        'duracao': '5h30min'
    }
    
    progresso = {
        'geral': 65,
        'materias': [
            {'nome': 'Matemática', 'progresso': 70},
            {'nome': 'Português', 'progresso': 85},
            {'nome': 'Ciências', 'progresso': 60},
            {'nome': 'História', 'progresso': 45}
        ]
    }
    
    materiais = [
        {
            'titulo': 'Redação Nota 1000',
            'tipo': 'Videoaula',
            'descricao': 'Aprenda as técnicas para uma redação perfeita',
            'duracao': '45min',
            'visualizacoes': 1500,
            'url': '#'
        },
        # ...mais materiais...
    ]
    
    cronograma = [
        {
            'titulo': 'Início das Inscrições',
            'data': 'Maio/2024',
            'completo': False
        },
        # ...mais eventos...
    ]
    
    metas = [
        {
            'id': 1,
            'descricao': 'Resolver 10 simulados',
            'completa': False
        },
        # ...mais metas...
    ]
    
    return render_template('exames/detalhe.html',
                         exame=exame,
                         progresso=progresso,
                         materiais=materiais,
                         cronograma=cronograma,
                         metas=metas)

# Rotas para bancas
@bancas.route('/')
def index():
    bancas_data = {
        'estatisticas': {
            'total_questoes': 15000,
            'bancas_cobertas': 12,
            'media_dificuldade': 7.5
        },
        'filtros': {  # Adicionando os filtros aqui
            'bancas': [
                {'id': 1, 'nome': 'CESPE/CEBRASPE'},
                {'id': 2, 'nome': 'FGV'},
                {'id': 3, 'nome': 'VUNESP'},
                {'id': 4, 'nome': 'IBFC'},
                {'id': 5, 'nome': 'AOCP'}
            ],
            'areas': [
                'Administrativa',
                'Fiscal',
                'Policial',
                'Jurídica',
                'Educação',
                'Saúde'
            ],
            'niveis': [
                'Fundamental',
                'Médio',
                'Superior',
                'Especialização'
            ],
            'estados': [
                'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
                'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
                'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
            ]
        },
        'concursos': [
            {
                'id': 1,
                'banca': 'CESPE/CEBRASPE',
                'titulo': 'Polícia Federal 2024',
                'area': 'Policial',
                'nivel': 'Superior',
                'estado': 'DF',
                'salario': 12522.50,
                'vagas': 1500,
                'inscricoes_ate': '15/03/2024',
                'prova': '28/04/2024',
                'status': 'Em breve',
                'status_class': 'warning'
            },
            {
                'id': 2,
                'banca': 'FGV',
                'titulo': 'Receita Federal 2024',
                'area': 'Fiscal',
                'nivel': 'Superior',
                'estado': 'DF',
                'salario': 21029.09,
                'vagas': 699,
                'inscricoes_ate': '20/03/2024',
                'prova': '05/05/2024',
                'status': 'Inscrições Abertas',
                'status_class': 'success'
            }
        ]
    }
    
    return render_template('bancas/index.html', **bancas_data)

@bancas.route('/filtrar', methods=['POST'])
def filtrar_concursos():
    filtros = request.get_json()
    # Implementar lógica de filtro aqui
    return jsonify({'concursos': []})

# API endpoints para as funcionalidades
@app.route('/api/metas/<int:meta_id>/toggle', methods=['POST'])
def toggle_meta(meta_id):
    # Implementar lógica de toggle da meta
    return {'success': True}

@app.route('/api/notificacoes/config', methods=['POST'])
def configurar_notificacoes():
    config = request.json
    # Implementar lógica de salvamento das configurações
    return {'success': True}

# Adicionar novas rotas para políticas
@app.route('/termos')
def termos():
    return render_template('politicas/termos.html')

@app.route('/privacidade')
def privacidade():
    return render_template('politicas/privacidade.html')

@app.route('/cookies')
def cookies():
    return render_template('politicas/cookies.html')

@app.route('/api/cookie-preferences', methods=['POST'])
def save_cookie_preferences():
    preferences = request.json
    # Implementar lógica para salvar preferências
    return {'success': True}

# Verificar se o context processor está no lugar correto (antes do registro dos blueprints)
@app.context_processor
def utility_processor():
    return {
        'now': datetime.now()
    }

# Registrar blueprints
app.register_blueprint(concursos, url_prefix='/concursos')
app.register_blueprint(exames, url_prefix='/exames')
app.register_blueprint(bancas, url_prefix='/bancas')
app.register_blueprint(simulados_bp)

if __name__ == '__main__':

    app.run(debug=True)
