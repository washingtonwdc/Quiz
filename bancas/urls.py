from flask import Blueprint
from . import views

bp = Blueprint('bancas', __name__)

bp.add_url_rule('/', view_func=views.index)
bp.add_url_rule('/filtrar', 'filtrar_concursos', views.filtrar_concursos, methods=['POST'])
bp.add_url_rule('/favoritos/<int:concurso_id>', 'toggle_favorito', views.toggle_favorito, methods=['POST'])
bp.add_url_rule('/alertas/<int:concurso_id>', 'configurar_alerta', views.configurar_alerta, methods=['POST'])
