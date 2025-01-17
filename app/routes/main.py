from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session, current_app
from app.routes import mongo
from datetime import datetime
from bson.objectid import ObjectId
import random
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.forms.contact import ContactForm
from app.utils.email import send_email
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5 per minute", "100 per day"]
)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/provas')
def provas():
    provas = mongo.db.provas.find()
    return render_template('provas.html', provas=provas)

@main.route('/add_prova', methods=['POST'])
def add_prova():
    data = request.get_json()
    mongo.db.provas.insert_one(data)
    return jsonify({"message": "Prova adicionada com sucesso!"}), 201

@main.route('/add_questao', methods=['POST'])
def add_questao():
    data = request.get_json()
    mongo.db.questoes.insert_one(data)
    return jsonify({"message": "Questão adicionada com sucesso!"}), 201

@main.route('/buscar_questoes', methods=['GET'])
def buscar_questoes():
    # Obter parâmetros de filtro
    disciplinas = request.args.getlist('disciplinas')
    bancas = request.args.getlist('bancas')
    ano = request.args.get('ano')
    nivel = request.args.get('nivel')

    # Construir query
    query = {}
    if disciplinas:
        query['area'] = {'$in': disciplinas}
    if bancas:
        query['banca'] = {'$in': bancas}
    if ano:
        query['ano'] = ano
    if nivel:
        query['nivel'] = nivel

    # Buscar questões com paginação
    page = int(request.args.get('page', 1))
    per_page = 10
    skip = (page - 1) * per_page

    questoes = list(mongo.db.questoes.find(query).skip(skip).limit(per_page))
    total = mongo.db.questoes.count_documents(query)

    # Adicionar informações de resolução e comentários
    for questao in questoes:
        questao['resolucao'] = "Explicação detalhada da resolução..."  # Adicione a resolução real
        questao['comentarios'] = list(mongo.db.comentarios.find({'questao_id': questao['_id']}))

    return render_template(
        'questoes.html',
        questoes=questoes,
        total=total,
        page=page,
        pages=(total + per_page - 1) // per_page
    )

@main.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        mongo.db.usuarios.insert_one({'email': email, 'senha': senha, 'data_cadastro': datetime.utcnow()})
        return redirect(url_for('main.index'))
    return render_template('cadastro.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        user = mongo.db.usuarios.find_one({'email': email, 'senha': senha})
        if user:
            session['user_id'] = str(user['_id'])
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Email ou senha incorretos.', 'danger')
    return render_template('login.html')

@main.route('/perfil')
def perfil():
    user_id = session.get('user_id')
    if user_id:
        user = mongo.db.usuarios.find_one({'_id': ObjectId(user_id)})
        return render_template('perfil.html', user=user)
    else:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('main.login'))

@main.route('/simulados', methods=['GET', 'POST'])
@login_required
def criar_simulado():
    if request.method == 'POST':
        disciplinas = request.form['disciplinas'].split(',')
        num_questoes = int(request.form['num_questoes'])
        nivel_dificuldade = request.form['nivel_dificuldade']
        
        questoes = list(mongo.db.questoes.find({'area': {'$in': disciplinas}, 'dificuldade': nivel_dificuldade}))
        random.shuffle(questoes)
        questoes_selecionadas = questoes[:num_questoes]
        
        session['simulado'] = [str(questao['_id']) for questao in questoes_selecionadas]
        return redirect(url_for('main.simulado'))
    return render_template('simulados.html')

@main.route('/simulado', methods=['GET', 'POST'])
def simulado():
    if request.method == 'POST':
        respostas = request.form.to_dict()
        questoes_ids = session.get('simulado', [])
        questoes = [mongo.db.questoes.find_one({'_id': ObjectId(questao_id)}) for questao_id in questoes_ids]
        
        acertos = 0
        for questao in questoes:
            questao['sua_resposta'] = respostas.get(str(questao['_id']))
            if questao['sua_resposta'] == questao['resposta_correta']:
                acertos += 1
        
        return render_template('simulado_resultado.html', questoes=questoes, acertos=acertos, total=len(questoes))
    
    questoes_ids = session.get('simulado', [])
    questoes = [mongo.db.questoes.find_one({'_id': ObjectId(questao_id)}) for questao_id in questoes_ids]
    return render_template('simulado.html', questoes=questoes)

@main.route('/simulado/novo')
@login_required
def novo_simulado():
    questions = Question.get_random_questions(mongo, count=10)
    return render_template('simulado.html', questions=questions)

@main.route('/simulado/submit', methods=['POST'])
@login_required
def submit_simulado():
    answers = {}
    score = 0
    total_questions = 0
    
    for key, value in request.form.items():
        if key.startswith('question-'):
            question_id = key.split('-')[1]
            answers[question_id] = int(value)
            
            question = mongo.db.questions.find_one({'_id': ObjectId(question_id)})
            if question and int(value) == question['correct_answer']:
                score += 1
            total_questions += 1
    
    # Salvar resultado do simulado
    simulado_result = {
        'user_id': current_user.id,
        'date': datetime.now(),
        'score': score,
        'total_questions': total_questions,
        'answers': answers,
        'time_taken': request.form.get('time_taken', '')
    }
    
    mongo.db.simulados.insert_one(simulado_result)
    
    flash(f'Simulado concluído! Pontuação: {score}/{total_questions}', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/questao/<questao_id>')
def questao(questao_id):
    questao = mongo.db.questoes.find_one({'_id': ObjectId(questao_id)})
    if not questao:
        flash('Questão não encontrada', 'danger')
        return redirect(url_for('main.buscar_questoes'))
    
    # Buscar estatísticas da questão
    total_respostas = mongo.db.respostas.count_documents({'questao_id': ObjectId(questao_id)})
    acertos = mongo.db.respostas.count_documents({
        'questao_id': ObjectId(questao_id),
        'correta': True
    })
    questao['acertos'] = round((acertos / total_respostas * 100) if total_respostas > 0 else 0)
    
    # Buscar comentários
    comentarios = list(mongo.db.comentarios.find({'questao_id': ObjectId(questao_id)}))
    
    return render_template('questao.html', questao=questao, comentarios=comentarios)

@main.route('/responder/<questao_id>', methods=['POST'])
def responder(questao_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    data = request.get_json()
    questao = mongo.db.questoes.find_one({'_id': ObjectId(questao_id)})
    correta = data['resposta'] == questao['resposta_correta']
    
    # Registrar resposta
    resposta = {
        'usuario_id': ObjectId(session['user_id']),
        'questao_id': ObjectId(questao_id),
        'resposta': data['resposta'],
        'correta': correta,
        'data': datetime.utcnow()
    }
    mongo.db.respostas.insert_one(resposta)
    
    # Atualizar pontuação do usuário
    if correta:
        mongo.db.usuarios.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$inc': {'pontos': 10}}
        )
    
    return jsonify({
        'correta': correta,
        'resolucao': questao['resolucao']
    })

@main.route('/favoritar/<questao_id>', methods=['POST'])
def favoritar(questao_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    usuario_id = ObjectId(session['user_id'])
    questao_id = ObjectId(questao_id)
    
    favorito = mongo.db.favoritos.find_one({
        'usuario_id': usuario_id,
        'questao_id': questao_id
    })
    
    if favorito:
        mongo.db.favoritos.delete_one({'_id': favorito['_id']})
        status = 'removido'
    else:
        mongo.db.favoritos.insert_one({
            'usuario_id': usuario_id,
            'questao_id': questao_id,
            'data': datetime.utcnow()
        })
        status = 'adicionado'
    
    return jsonify({'status': status})

@main.route('/comentar/<questao_id>', methods=['POST'])
def comentar(questao_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    data = request.get_json()
    comentario = {
        'usuario_id': ObjectId(session['user_id']),
        'questao_id': ObjectId(questao_id),
        'texto': data['texto'],
        'data': datetime.utcnow()
    }
    
    result = mongo.db.comentarios.insert_one(comentario)
    
    return jsonify({
        'status': 'success',
        'comentario_id': str(result.inserted_id)
    })

@main.route('/sobre')
def sobre():
    return render_template('sobre.html')

@main.route('/planos')
def planos():
    return render_template('planos.html')

@main.route('/contato', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def contato():
    form = ContactForm()
    
    if form.validate_on_submit():
        # Verificar honeypot
        if form.honeypot.data:
            return redirect(url_for('main.index'))
        
        try:
            # Enviar email
            send_email(
                subject=f'Contato: {form.subject.data}',
                sender=form.email.data,
                recipients=['seu-email@exemplo.com'],
                text_body=f"""
                Nome: {form.name.data}
                Email: {form.email.data}
                Assunto: {form.subject.data}
                Mensagem: {form.message.data}
                """,
                html_body=render_template('email/contact.html', form=form)
            )
            
            # Registrar contato no banco de dados
            mongo.db.contacts.insert_one({
                'name': form.name.data,
                'email': form.email.data,
                'subject': form.subject.data,
                'message': form.message.data,
                'date': datetime.utcnow(),
                'ip': request.remote_addr
            })
            
            flash('Mensagem enviada com sucesso!', 'success')
            return redirect(url_for('main.contato'))
            
        except Exception as e:
            flash('Erro ao enviar mensagem. Tente novamente mais tarde.', 'danger')
            current_app.logger.error(f'Erro no contato: {str(e)}')
    
    return render_template('contato.html', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('main.login'))
    
    user = mongo.db.usuarios.find_one({'_id': ObjectId(session['user_id'])})
    
    # Buscar estatísticas do usuário
    total_questoes = mongo.db.questoes.count_documents({})
    user['questoes_respondidas'] = mongo.db.respostas.count_documents({'usuario_id': ObjectId(session['user_id'])})
    user['acertos'] = mongo.db.respostas.count_documents({
        'usuario_id': ObjectId(session['user_id']),
        'correta': True
    })
    
    # Buscar atividades recentes
    atividades = list(mongo.db.atividades.find(
        {'usuario_id': ObjectId(session['user_id'])}
    ).sort('data', -1).limit(10))
    
    # Buscar metas diárias
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    user['questoes_hoje'] = mongo.db.respostas.count_documents({
        'usuario_id': ObjectId(session['user_id']),
        'data': {'$gte': hoje}
    })
    
    user['tempo_estudo_hoje'] = mongo.db.sessoes_estudo.aggregate([
        {
            '$match': {
                'usuario_id': ObjectId(session['user_id']),
                'data': {'$gte': hoje}
            }
        },
        {
            '$group': {
                '_id': None,
                'total_minutos': {'$sum': '$duracao'}
            }
        }
    ]).next().get('total_minutos', 0)
    
    return render_template('dashboard.html',
                         user=user,
                         total_questoes=total_questoes,
                         atividades=atividades)

@main.route('/questions')
@login_required
def questions():
    # Mock data - substituir por dados do banco
    subjects = [
        {'id': 1, 'name': 'Português'},
        {'id': 2, 'name': 'Matemática'},
        {'id': 3, 'name': 'Direito Constitucional'}
    ]
    
    bancas = [
        {'id': 1, 'name': 'CESPE'},
        {'id': 2, 'name': 'FCC'},
        {'id': 3, 'name': 'VUNESP'}
    ]
    
    anos = range(2024, 2019, -1)
    
    # Mock questions - substituir por consulta ao banco
    questions = [
        {
            'id': 1,
            'subject': 'Português',
            'banca': 'CESPE',
            'year': 2023,
            'text': 'Questão exemplo de português...',
            'options': [
                {'id': 'a', 'text': 'Opção A'},
                {'id': 'b', 'text': 'Opção B'},
                {'id': 'c', 'text': 'Opção C'},
                {'id': 'd', 'text': 'Opção D'}
            ]
        }
        # Adicionar mais questões aqui
    ]
    
    return render_template('questions.html', 
                         subjects=subjects,
                         bancas=bancas,
                         anos=anos,
                         questions=questions)

@main.route('/profile')
@login_required
def profile():
    # Buscar estatísticas do usuário
    stats = {
        'total_questions': mongo.db.answers.count_documents({'user_id': current_user.id}),
        'accuracy': calculate_accuracy(current_user.id),
        'study_hours': calculate_study_hours(current_user.id)
    }
    return render_template('profile.html', stats=stats)

@main.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username')
    email = request.form.get('email')
    new_password = request.form.get('new_password')
    
    # Atualizar dados do usuário
    update_data = {'username': username, 'email': email}
    if new_password:
        update_data['password'] = generate_password_hash(new_password)
    
    mongo.db.users.update_one(
        {'_id': ObjectId(current_user.id)},
        {'$set': update_data}
    )
    
    flash('Perfil atualizado com sucesso!', 'success')
    return redirect(url_for('main.profile'))

@main.route('/settings')
@login_required
def settings():
    user_data = mongo.db.users.find_one({'_id': ObjectId(current_user.id)})
    return render_template('profile/settings.html', user=user_data)

@main.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    preferences = {
        'study_mode': request.form.get('study_mode', 'random'),
        'questions_per_quiz': int(request.form.get('questions_per_quiz', 10)),
        'theme': request.form.get('theme', 'light')
    }
    
    mongo.db.users.update_one(
        {'_id': ObjectId(current_user.id)},
        {'$set': {'preferences': preferences}}
    )
    
    flash('Configurações atualizadas com sucesso!', 'success')
    return redirect(url_for('main.settings'))

@main.route('/terms')
def terms():
    return render_template('terms.html')

@main.route('/accept-terms', methods=['POST'])
@login_required
def accept_terms():
    user_id = current_user.id
    mongo.db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'terms_accepted': True, 'terms_accepted_date': datetime.now()}}
    )
    flash('Termos aceitos com sucesso!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main.route('/accept-privacy', methods=['POST'])
@login_required
def accept_privacy():
    user_id = current_user.id
    mongo.db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'privacy_accepted': True, 'privacy_accepted_date': datetime.now()}}
    )
    flash('Política de Privacidade aceita com sucesso!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/about')
def about():
    stats = {
        'users': '17M+',
        'questions': '100K+',
        'year_founded': '2024'
    }
    return render_template('about.html', stats=stats)

def calculate_accuracy(user_id):
    answers = mongo.db.answers.find({'user_id': user_id})
    total = correct = 0
    for answer in answers:
        total += 1
        if answer.get('is_correct'):
            correct += 1
    return (correct / total * 100) if total > 0 else 0

def calculate_study_hours(user_id):
    # Implementar cálculo de horas de estudo
    return 0  # Placeholder

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/faq')
def faq():
    return render_template('faq.html')