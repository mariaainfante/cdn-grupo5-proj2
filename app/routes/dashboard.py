
from flask import Blueprint, render_template, request

dashboard_bp = Blueprint("dashboard", __name__)


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
def projeto():
    return render_template("dashboard/projeto.html")


@dashboard_bp.route("/novo-projeto", methods=["GET", "POST"])
def novo_projeto():
    mensagem = None
    erro = None
    dados = {}

    if request.method == "POST":
        dados = request.form

        cliente = request.form.get("cliente", "").strip()
        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        inicio = request.form.get("inicio", "").strip()
        termino = request.form.get("termino", "").strip()

        if not cliente or not nome or not descricao:
            erro = "Preencha todos os campos obrigatórios."

        elif inicio and termino and termino < inicio:
            erro = "A data de término não pode ser anterior à data de início."

        else:
            mensagem = "Projeto recebido e validado com sucesso!"

    return render_template(
        "dashboard/novo-projeto.html",
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
    clientes = [
        {
            "nome": "Cliente exemplo",
            "contato": "contato@example.com"
        }
    ]

    return render_template(
        "dashboard/clientes.html",
        clientes=clientes
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
    return render_template("dashboard/info-cliente.html")


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
