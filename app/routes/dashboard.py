
from flask import Blueprint, render_template, request, abort

dashboard_bp = Blueprint("dashboard", __name__)


# ==================================================
# CLIENTES DE EXEMPLO
# ==================================================

CLIENTES_EXEMPLO = [
    {
        "id": 1,
        "nome": "Cliente exemplo",
        "contato": "contato@example.com"
    }
]


# ==================================================
# PROJETOS DE EXEMPLO
# ==================================================

PROJETOS_EXEMPLO = [
    {
        "id": 1,
        "nome": "Projeto exemplo",
        "cliente": "Cliente exemplo"
    }
]


# ==================================================
# HISTÓRICO DOS PROJETOS
# ==================================================

HISTORICO_PROJETOS = {
    1: []
}


# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================

def buscar_projeto(projeto_id):
    for projeto in PROJETOS_EXEMPLO:
        if projeto["id"] == projeto_id:
            return projeto

    abort(404)


def adicionar_historico(projeto_id, tipo, data, descricao):
    if projeto_id not in HISTORICO_PROJETOS:
        HISTORICO_PROJETOS[projeto_id] = []

    registro = {
        "tipo": tipo,
        "data": data,
        "descricao": descricao,
        "responsavel": "Gestor"
    }

    HISTORICO_PROJETOS[projeto_id].append(registro)


# ==================================================
# TELA PRINCIPAL DO GESTOR
# ==================================================

@dashboard_bp.get("/gestor")
def gestor():
    return render_template("dashboard/gestor.html")


# ==================================================
# PROJETO
# ==================================================

@dashboard_bp.get("/projeto")
@dashboard_bp.get("/projeto/<int:projeto_id>")
def projeto(projeto_id=1):
    projeto_atual = buscar_projeto(projeto_id)

    return render_template(
        "dashboard/projeto.html",
        projeto=projeto_atual,
        propriedade=None
    )


@dashboard_bp.route("/novo-projeto", methods=["GET", "POST"])
def novo_projeto():
    mensagem = None
    erro = None
    dados = {}

    clientes = CLIENTES_EXEMPLO

    if request.method == "POST":
        dados = request.form

        cliente = request.form.get("cliente", "").strip()
        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        inicio = request.form.get("inicio", "").strip()
        termino = request.form.get("termino", "").strip()

        ids_clientes = [str(c["id"]) for c in clientes]

        if not cliente or not nome or not descricao:
            erro = "Preencha todos os campos obrigatórios."

        elif cliente not in ids_clientes:
            erro = "Selecione um cliente válido."

        elif inicio and termino and termino < inicio:
            erro = "A data de término não pode ser anterior à data de início."

        else:
            mensagem = "Projeto recebido e validado com sucesso!"

    return render_template(
        "dashboard/novo-projeto.html",
        clientes=clientes,
        mensagem=mensagem,
        erro=erro,
        dados=dados
    )


@dashboard_bp.route("/editar-projeto", methods=["GET", "POST"])
def editar_projeto():
    mensagem = None
    erro = None

    dados = {
        "nome": "Projeto exemplo",
        "descricao": "Projeto ilustrativo de automação residencial. Dados fictícios para visualização do layout.",
        "inicio": "2026-10-28",
        "termino": "2026-12-18",
        "estado": "em-andamento"
    }

    if request.method == "POST":
        dados = request.form

        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        inicio = request.form.get("inicio", "").strip()
        termino = request.form.get("termino", "").strip()
        estado = request.form.get("estado", "").strip()

        if not nome or not descricao or not inicio or not termino or not estado:
            erro = "Preencha todos os campos obrigatórios."

        elif termino < inicio:
            erro = "A data de término não pode ser anterior à data de início."

        elif estado not in ["planejado", "em-andamento"]:
            erro = "Selecione um estado válido."

        else:
            mensagem = "Alterações recebidas e validadas com sucesso!"

    return render_template(
        "dashboard/editar-projeto.html",
        mensagem=mensagem,
        erro=erro,
        dados=dados
    )


# ==================================================
# PARTICIPANTES
# ==================================================

@dashboard_bp.get("/participantes")
def participantes():
    return render_template("dashboard/participantes.html")


@dashboard_bp.route("/adicionar-participante", methods=["GET", "POST"])
def adicionar_participante():
    mensagem = None
    erro = None
    dados = {}

    usuarios = [
        {
            "id": 1,
            "nome": "Participante exemplo",
            "email": "participante@example.com"
        }
    ]

    if request.method == "POST":
        dados = request.form

        usuario = request.form.get("usuario", "").strip()
        papel = request.form.get("papel", "").strip()

        ids_usuarios = [str(u["id"]) for u in usuarios]

        if not usuario or not papel:
            erro = "Preencha todos os campos obrigatórios."

        elif usuario not in ids_usuarios:
            erro = "Selecione um usuário válido."

        elif papel not in ["gestor", "arquiteto"]:
            erro = "Selecione um papel válido."

        else:
            mensagem = "Participante recebido e validado com sucesso!"

    return render_template(
        "dashboard/adicionar-participante.html",
        usuarios=usuarios,
        mensagem=mensagem,
        erro=erro,
        dados=dados
    )


@dashboard_bp.route("/alterar-papel", methods=["GET", "POST"])
def alterar_papel():
    mensagem = None
    erro = None

    dados = {"papel": "arquiteto"}

    if request.method == "POST":
        papel = request.form.get("papel", "").strip()
        dados = request.form

        if papel not in ["gestor", "arquiteto"]:
            erro = "Selecione um papel válido."

        else:
            mensagem = "Papel recebido e validado com sucesso!"

    return render_template(
        "dashboard/alterar-papel.html",
        mensagem=mensagem,
        erro=erro,
        dados=dados
    )


@dashboard_bp.route("/desativar-participante", methods=["GET", "POST"])
def desativar_participante():
    mensagem = None

    if request.method == "POST":
        mensagem = "Solicitação de desativação recebida com sucesso!"

    return render_template(
        "dashboard/desativar-participante.html",
        mensagem=mensagem
    )


# ==================================================
# CLIENTES
# ==================================================

@dashboard_bp.get("/clientes")
def clientes():
    return render_template(
        "dashboard/clientes.html",
        clientes=CLIENTES_EXEMPLO
    )


@dashboard_bp.route("/novo-cliente", methods=["GET", "POST"])
def novo_cliente():
    mensagem = None
    erro = None
    dados = {}

    if request.method == "POST":
        dados = request.form

        nome = request.form.get("nome", "").strip()
        contato = request.form.get("contato", "").strip()

        if not nome:
            erro = "O nome do cliente é obrigatório."

        else:
            mensagem = "Cliente recebido e validado com sucesso!"

    return render_template(
        "dashboard/novo-cliente.html",
        mensagem=mensagem,
        erro=erro,
        dados=dados
    )


@dashboard_bp.get("/info-cliente")
def info_cliente():
    cliente = CLIENTES_EXEMPLO[0]

    return render_template(
        "dashboard/info-cliente.html",
        cliente=cliente
    )


@dashboard_bp.route("/editar-cliente", methods=["GET", "POST"])
def editar_cliente():
    mensagem = None
    erro = None

    dados = {
        "nome": "Cliente exemplo",
        "contato": "contato@example.com"
    }

    if request.method == "POST":
        dados = request.form

        nome = request.form.get("nome", "").strip()
        contato = request.form.get("contato", "").strip()

        if not nome:
            erro = "O nome do cliente é obrigatório."

        else:
            mensagem = "Alterações recebidas e validadas com sucesso!"

    return render_template(
        "dashboard/editar-cliente.html",
        mensagem=mensagem,
        erro=erro,
        dados=dados
    )


# ==================================================
# PROPRIEDADE
# ==================================================

@dashboard_bp.route("/nova-propriedade", methods=["GET", "POST"])
def nova_propriedade():
    mensagem = None
    erro = None
    dados = {}

    if request.method == "POST":
        dados = request.form

        nome = request.form.get("nome", "").strip()
        tipo = request.form.get("tipo", "").strip()
        endereco = request.form.get("endereco", "").strip()
        cidade = request.form.get("cidade", "").strip()
        area = request.form.get("area", "").strip()
        descricao = request.form.get("descricao", "").strip()
        foto = request.files.get("foto")

        tipos_validos = [
            "residencial",
            "comercial",
            "industrial",
            "outro"
        ]

        if not nome or not tipo:
            erro = "Preencha os campos obrigatórios."

        elif tipo not in tipos_validos:
            erro = "Selecione um tipo de propriedade válido."

        elif area:
            try:
                if float(area) <= 0:
                    erro = "A área deve ser maior que zero."
            except ValueError:
                erro = "Informe uma área numérica válida."

        if not erro and foto and foto.filename:
            extensao = foto.filename.rsplit(".", 1)[-1].lower()

            if extensao not in ["jpg", "jpeg", "png"]:
                erro = "A imagem deve estar no formato JPG, JPEG ou PNG."

        if not erro:
            mensagem = "Propriedade recebida e validada com sucesso!"

    return render_template(
        "dashboard/nova-propriedade.html",
        mensagem=mensagem,
        erro=erro,
        dados=dados
    )


# ==================================================
# AMBIENTES DA PROPRIEDADE
# ==================================================

@dashboard_bp.get("/ambientes")
def ambientes():
    propriedade = {
        "nome": "Residência Principal",
        "endereco": "Endereço da propriedade — São Paulo, SP"
    }

    ambientes = [
        {
            "nome": "Sala de estar",
            "tipo": "Sala",
            "area": 25,
            "caracteristicas": "TV, ar-condicionado"
        },
        {
            "nome": "Cozinha",
            "tipo": "Cozinha",
            "area": 15,
            "caracteristicas": "Geladeira, fogão"
        },
        {
            "nome": "Quarto principal",
            "tipo": "Quarto",
            "area": 18,
            "caracteristicas": "Ar-condicionado"
        }
    ]

    return render_template(
        "dashboard/ambientes.html",
        propriedade=propriedade,
        ambientes=ambientes
    )


@dashboard_bp.route("/novo-ambiente", methods=["GET", "POST"])
def novo_ambiente():
    mensagem = None
    erro = None
    dados = {}

    tipos_validos = [
        "sala",
        "cozinha",
        "quarto",
        "banheiro",
        "escritorio",
        "area_externa",
        "outro"
    ]

    if request.method == "POST":
        dados = request.form

        nome = request.form.get("nome", "").strip()
        tipo = request.form.get("tipo", "").strip()
        area = request.form.get("area", "").strip()
        caracteristicas = request.form.get("caracteristicas", "").strip()
        observacoes = request.form.get("observacoes", "").strip()

        if not nome or not tipo:
            erro = "Preencha os campos obrigatórios."

        elif tipo not in tipos_validos:
            erro = "Selecione um tipo de ambiente válido."

        elif area:
            try:
                if float(area) <= 0:
                    erro = "A área deve ser maior que zero."
            except ValueError:
                erro = "Informe uma área numérica válida."

        if not erro:
            mensagem = "Ambiente recebido e validado com sucesso!"

    return render_template(
        "dashboard/novo-ambiente.html",
        mensagem=mensagem,
        erro=erro,
        dados=dados
    )


# ==================================================
# HISTÓRICO DO PROJETO
# ==================================================

@dashboard_bp.get("/historico")
@dashboard_bp.get("/projeto/<int:projeto_id>/historico")
def historico(projeto_id=1):
    projeto_atual = buscar_projeto(projeto_id)

    historico_projeto = HISTORICO_PROJETOS.get(projeto_id, [])

    return render_template(
        "dashboard/historico.html",
        projeto=projeto_atual,
        historico=historico_projeto
    )


# ==================================================
# NOVO EVENTO
# ==================================================

@dashboard_bp.route("/novo-evento", methods=["GET", "POST"])
@dashboard_bp.route(
    "/projeto/<int:projeto_id>/novo-evento",
    methods=["GET", "POST"]
)
def novo_evento(projeto_id=1):
    mensagem = None
    erro = None
    dados = {}

    projeto_atual = buscar_projeto(projeto_id)

    if request.method == "POST":
        dados = request.form

        titulo = request.form.get("titulo", "").strip()
        data = request.form.get("data", "").strip()
        descricao = request.form.get("descricao", "").strip()

        if not titulo or not data or not descricao:
            erro = "Preencha todos os campos obrigatórios."

        else:
            adicionar_historico(
                projeto_id,
                "Evento",
                data,
                f"{titulo}: {descricao}"
            )

            mensagem = "Evento registrado com sucesso!"

    return render_template(
        "dashboard/novo-evento.html",
        projeto=projeto_atual,
        projeto_id=projeto_id,
        mensagem=mensagem,
        erro=erro,
        dados=dados
    )


# ==================================================
# NOVO COMENTÁRIO
# ==================================================

@dashboard_bp.route("/novo-comentario", methods=["GET", "POST"])
@dashboard_bp.route(
    "/projeto/<int:projeto_id>/novo-comentario",
    methods=["GET", "POST"]
)
def novo_comentario(projeto_id=1):
    mensagem = None
    erro = None
    dados = {}

    projeto_atual = buscar_projeto(projeto_id)

    if request.method == "POST":
        dados = request.form

        comentario = request.form.get("comentario", "").strip()

        if not comentario:
            erro = "Escreva um comentário antes de publicar."

        else:
            adicionar_historico(
                projeto_id,
                "Comentário",
                "",
                comentario
            )

            mensagem = "Comentário registrado com sucesso!"

    return render_template(
        "dashboard/novo-comentario.html",
        projeto=projeto_atual,
        projeto_id=projeto_id,
        mensagem=mensagem,
        erro=erro,
        dados=dados
    )


# ==================================================
# NOVA DECISÃO
# ==================================================

@dashboard_bp.route("/nova-decisao", methods=["GET", "POST"])
@dashboard_bp.route(
    "/projeto/<int:projeto_id>/nova-decisao",
    methods=["GET", "POST"]
)
def nova_decisao(projeto_id=1):
    mensagem = None
    erro = None
    dados = {}

    projeto_atual = buscar_projeto(projeto_id)

    if request.method == "POST":
        dados = request.form

        titulo = request.form.get("titulo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        data = request.form.get("data", "").strip()

        if not titulo or not descricao or not data:
            erro = "Preencha todos os campos obrigatórios."

        else:
            adicionar_historico(
                projeto_id,
                "Decisão",
                data,
                f"{titulo}: {descricao}"
            )

            mensagem = "Decisão registrada com sucesso!"

    return render_template(
        "dashboard/nova-decisao.html",
        projeto=projeto_atual,
        projeto_id=projeto_id,
        mensagem=mensagem,
        erro=erro,
        dados=dados
    )
