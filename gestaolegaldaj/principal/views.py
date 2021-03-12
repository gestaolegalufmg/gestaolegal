from flask import render_template, Blueprint, flash, request
from gestaolegaldaj import app, login_required

from gestaolegaldaj.usuario.models import Usuario
from gestaolegaldaj.plantao.models import Atendido, Assistido, AssistidoPessoaJuridica
from gestaolegaldaj.casos.models import Caso

principal = Blueprint('principal', __name__, template_folder='templates')

@principal.route('/')
@login_required()
def index():
    return render_template('home.html')

@app.errorhandler(404)
def error_404(error):
    return render_template('erros/404.html') , 404

@app.errorhandler(403)
def error_403(error):
    return render_template('erros/403.html') , 403

@app.errorhandler(500)
def error_500(error):
    return render_template('erros/500.html') , 403
    
@principal.route('/termos_de_uso')
@login_required()
def termos():
    return render_template('termos_de_uso.html')

@principal.route('/busca_geral',methods=['GET','POST'])
@login_required()
def busca_geral():
    page_assistido_pfisica = request.args.get('page_assistido_pfisica', 1, type=int)
    page_assistido_pjuridica = request.args.get('page_assistido_pjuridica', 1, type=int)
    page_usuario = request.args.get('page_usuario', 1, type=int)
    page_caso = request.args.get('page_caso', 1, type=int)

    if request.method == 'POST':
        busca = request.form['busca_geral']
    else:
        busca = request.args.get('busca_atual', '', type=str)
 
    assistidos = Atendido.query.join(Assistido).filter(Atendido.nome.contains(busca)).order_by('nome').paginate(page_assistido_pfisica, app.config['ATENDIDOS_POR_PAGINA'], False)
    assistidos_pjuridica = Atendido.query.join(Assistido).join(AssistidoPessoaJuridica).filter(Atendido.nome.contains(busca)).order_by('nome').paginate(page_assistido_pjuridica, app.config['ATENDIDOS_POR_PAGINA'], False)
    usuarios = Usuario.query.filter(Usuario.nome.contains(busca), Usuario.status != False).order_by('nome').paginate(page_usuario, app.config['USUARIOS_POR_PAGINA'], False)
    
    casos = None
    if busca.isdigit():
        casos = Caso.query.filter_by(status = True, id = int(busca)).paginate(page_caso, app.config['CASOS_POR_PAGINA'], False)

    return render_template("busca_geral.html", assistidos = assistidos, assistidos_pjuridica = assistidos_pjuridica, usuarios = usuarios, casos = casos, busca_atual = busca)
