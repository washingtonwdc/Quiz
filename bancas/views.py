from flask import render_template, request, jsonify, current_app
from flask_caching import Cache
from flask_login import current_user
import redis
from datetime import datetime, timedelta

# Configuração do Redis para cache
redis_client = redis.Redis(host='localhost', port=6379, db=0)
cache = Cache(config={'CACHE_TYPE': 'redis'})

def get_cached_results(key, callback, timeout=300):
    """Gerencia cache de resultados com Redis"""
    cached = redis_client.get(key)
    if cached:
        return eval(cached)
    results = callback()
    redis_client.setex(key, timeout, str(results))
    return results

def index():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Cache key baseada nos parâmetros da página
    cache_key = f'bancas_page_{page}_per_{per_page}'
    
    def get_fresh_data():
        # Dados que seriam buscados do banco
        return {
            'estatisticas': {
                'total_questoes': 15000,
                'bancas_cobertas': 12,
                'media_dificuldade': 7.5
            },
            'filtros': {
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
            'concursos': get_concursos(page, per_page)
        }
    
    data = get_cached_results(cache_key, get_fresh_data)
    return render_template('bancas/index.html', **data)

def filtrar_concursos():
    filtros = request.get_json()
    page = filtros.pop('page', 1)
    per_page = filtros.pop('per_page', 10)
    order_by = filtros.pop('order_by', '-data_prova')
    
    # Cache key baseada nos filtros
    cache_key = f'concursos_{"_".join([f"{k}_{v}" for k,v in filtros.items()])}_p{page}'
    
    def apply_filters():
        concursos = get_concursos_base()
        
        # Aplicar filtros
        if filtros.get('banca'):
            concursos = [c for c in concursos if c['banca'] == filtros['banca']]
            
        if filtros.get('area'):
            concursos = [c for c in concursos if c['area'] == filtros['area']]
            
        if filtros.get('nivel'):
            concursos = [c for c in concursos if c['nivel'] == filtros['nivel']]
            
        if filtros.get('estado'):
            concursos = [c for c in concursos if c['estado'] == filtros['estado']]
            
        if filtros.get('salario_min'):
            concursos = [c for c in concursos if c['salario'] >= float(filtros['salario_min'])]
            
        if filtros.get('salario_max'):
            concursos = [c for c in concursos if c['salario'] <= float(filtros['salario_max'])]
            
        if filtros.get('status'):
            concursos = [c for c in concursos if c['status'] in filtros['status']]
        
        # Ordenação
        reverse = order_by.startswith('-')
        order_key = order_by.lstrip('-')
        concursos.sort(key=lambda x: x[order_key], reverse=reverse)
        
        # Paginação
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'concursos': concursos[start:end],
            'total': len(concursos),
            'pages': (len(concursos) + per_page - 1) // per_page
        }
    
    return jsonify(get_cached_results(cache_key, apply_filters))

def toggle_favorito(concurso_id):
    """Toggle favorito status para um concurso"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Login required'}), 401
        
    favorito = Favorito.query.filter_by(
        usuario_id=current_user.id,
        concurso_id=concurso_id
    ).first()
    
    if favorito:
        db.session.delete(favorito)
    else:
        favorito = Favorito(
            usuario_id=current_user.id,
            concurso_id=concurso_id
        )
        db.session.add(favorito)
    
    db.session.commit()
    return jsonify({'status': 'added' if favorito else 'removed'})

def configurar_alerta(concurso_id):
    """Configura alertas para um concurso"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Login required'}), 401
        
    config = request.get_json()
    alerta = Alerta(
        usuario_id=current_user.id,
        concurso_id=concurso_id,
        tipo=config['tipo'],  # email, push, sms
        antecedencia=config['antecedencia'],  # dias antes
        eventos=config['eventos']  # inscricoes, provas, resultados
    )
    
    db.session.add(alerta)
    db.session.commit()
    
    return jsonify({'status': 'configured'})

# Funções auxiliares
def get_concursos_base():
    """Retorna lista base de concursos para filtragem"""
    # Aqui você buscaria do banco de dados
    return [
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
            'data_prova': '28/04/2024',
            'status': 'Em breve',
            'status_class': 'warning'
        },
        # ... mais concursos ...
    ]

def get_concursos(page, per_page):
    """Retorna concursos paginados"""
    concursos = get_concursos_base()
    start = (page - 1) * per_page
    end = start + per_page
    return concursos[start:end]
