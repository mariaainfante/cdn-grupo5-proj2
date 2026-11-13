
from flask import Blueprint, render_template, request, abort, redirect, url_for, session

from app.database import conectar_banco

dashboard_bp = Blueprint("dashboard", __name__)


# ==================================================
# PROTEÇÃO DE ACESSO
# ==================================================

@dashboard_bp.before_request
def verificar_login():

    if "id_user" not in session:
        return redirect(url_for("auth.login"))


# ==================================================
# VERIFICAÇÃO DE PERMISSÃO DO GESTOR GLOBAL
# ==================================================

def verificar_gestor_global():

    if session.get("papel_global") != "gestor":
        abort(403)


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

    verificar_gestor_global()

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                p.id_projeto AS id,
                p.nm_projeto AS nome,
                c.nm_cliente AS cliente,
                p.estado_projeto AS estado,
                v.papel_no_projeto AS papel
            FROM projeto p

            INNER JOIN cliente c
                ON p.id_cliente = c.id_cliente

            INNER JOIN vinculo_projeto_usuario v
                ON p.id_projeto = v.id_projeto

            WHERE v.id_user = %s
              AND v.ativo = 1

            ORDER BY p.criado_em DESC
            """,
            (session["id_user"],)
        )

        projetos = cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()

    return render_template(
        "dashboard/gestor.html",
        projetos=projetos
    )


# ==================================================
# VERIFICAÇÃO DE PERMISSÃO NO PROJETO
# ==================================================

def verificar_gestor_no_projeto(projeto_id):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:

        cursor.execute(
            """
            SELECT id_vinculo
            FROM vinculo_projeto_usuario
            WHERE id_projeto = %s
              AND id_user = %s
              AND papel_no_projeto = 'gestor'
              AND ativo = 1
            """,
            (projeto_id, session["id_user"])
        )

        vinculo = cursor.fetchone()

        if not vinculo:
            abort(403)

    finally:
        cursor.close()
        conexao.close()


# ==================================================
# PROJETO
# ==================================================


# ==================================================
# PROJETO
# ==================================================

@dashboard_bp.get("/projeto")
@dashboard_bp.get("/projeto/<int:projeto_id>")
def projeto(projeto_id=1):

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                p.id_projeto AS id,
                p.nm_projeto AS nome,
                p.desc_projeto AS descricao,
                p.estado_projeto AS estado,
                p.inicio_previsto AS inicio,
                p.fim_previsto AS termino,
                p.criado_em AS criado_em,
                c.nm_cliente AS cliente,
                c.contato_cliente AS contato_cliente,
                v.papel_no_projeto AS papel

            FROM projeto p

            INNER JOIN cliente c
                ON p.id_cliente = c.id_cliente

            INNER JOIN vinculo_projeto_usuario v
                ON p.id_projeto = v.id_projeto

            WHERE p.id_projeto = %s
              AND v.id_user = %s
              AND v.ativo = 1
            """,
            (projeto_id, session["id_user"])
        )

        projeto_atual = cursor.fetchone()

        if not projeto_atual:
            abort(404)

        # Busca todas as propriedades vinculadas ao projeto
        cursor.execute(
            """
            SELECT
                id_propiedade AS id,
                nm_propriedade AS nome,
                tp_propriedade AS tipo,
                endereco_propriedade AS endereco
            FROM propriedade
            WHERE id_projeto = %s
            ORDER BY id_propiedade DESC
            """,
            (projeto_id,)
        )

        propriedades = cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()

    return render_template(
        "dashboard/projeto.html",
        projeto=projeto_atual,
        propriedades=propriedades
    )



# ==================================================
# NOVO PROJETO
# ==================================================

@dashboard_bp.route("/novo-projeto", methods=["GET", "POST"])
def novo_projeto():

    verificar_gestor_global()

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


# ==================================================
# EDITAR PROJETO
# ==================================================

@dashboard_bp.route("/editar-projeto/<int:projeto_id>", methods=["GET", "POST"])
def editar_projeto(projeto_id):

    verificar_gestor_no_projeto(projeto_id)

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                id_projeto,
                nm_projeto,
                desc_projeto,
                estado_projeto,
                inicio_previsto,
                fim_previsto
            FROM projeto
            WHERE id_projeto = %s
            """,
            (projeto_id,)
        )

        projeto_atual = cursor.fetchone()

        if not projeto_atual:
            abort(404)

        dados = {
            "nome": projeto_atual["nm_projeto"],
            "descricao": projeto_atual["desc_projeto"],
            "inicio": (
                projeto_atual["inicio_previsto"].strftime("%Y-%m-%d")
                if projeto_atual["inicio_previsto"]
                else ""
            ),
            "termino": (
                projeto_atual["fim_previsto"].strftime("%Y-%m-%d")
                if projeto_atual["fim_previsto"]
                else ""
            ),
            "estado": projeto_atual["estado_projeto"]
        }

        mensagem = None
        erro = None

        if request.method == "POST":

            dados = {
                "nome": request.form.get("nome", "").strip(),
                "descricao": request.form.get("descricao", "").strip(),
                "inicio": request.form.get("inicio", "").strip(),
                "termino": request.form.get("termino", "").strip(),
                "estado": request.form.get("estado", "").strip()
            }

            nome = dados["nome"]
            descricao = dados["descricao"]
            inicio = dados["inicio"] or None
            termino = dados["termino"] or None
            estado = dados["estado"]

            if not nome or not descricao or not estado:
                erro = "Preencha todos os campos obrigatórios."

            elif inicio and termino and termino < inicio:
                erro = "A data de término não pode ser anterior à data de início."

            elif estado not in ["planejado", "em_andamento", "concluido"]:
                erro = "Selecione um estado válido."

            else:

                cursor.execute(
                    """
                    UPDATE projeto
                    SET
                        nm_projeto = %s,
                        desc_projeto = %s,
                        inicio_previsto = %s,
                        fim_previsto = %s,
                        estado_projeto = %s
                    WHERE id_projeto = %s
                    """,
                    (
                        nome,
                        descricao,
                        inicio,
                        termino,
                        estado,
                        projeto_id
                    )
                )

                conexao.commit()

                return redirect(url_for("dashboard.gestor"))

        return render_template(
            "dashboard/editar-projeto.html",
            mensagem=mensagem,
            erro=erro,
            dados=dados,
            projeto_id=projeto_id
        )

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()


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

    verificar_gestor_global()

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

    verificar_gestor_global()

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

@dashboard_bp.route(
    "/projeto/<int:projeto_id>/nova-propriedade",
    methods=["GET", "POST"]
)
def nova_propriedade(projeto_id):

    # Verifica se o usuário é gestor ativo do projeto
    verificar_gestor_no_projeto(projeto_id)

    mensagem = None
    erro = None
    dados = {}

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        # Busca o projeto para exibir seu nome na tela
        cursor.execute(
            """
            SELECT
                id_projeto AS id,
                nm_projeto AS nome
            FROM projeto
            WHERE id_projeto = %s
            """,
            (projeto_id,)
        )

        projeto_atual = cursor.fetchone()

        if not projeto_atual:
            abort(404)

        if request.method == "POST":

            dados = request.form

            nome = request.form.get("nome", "").strip()
            tipo = request.form.get("tipo", "").strip()
            endereco = request.form.get("endereco", "").strip()

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

            else:

                cursor.execute(
                    """
                    INSERT INTO propriedade (
                        id_projeto,
                        nm_propriedade,
                        tp_propriedade,
                        endereco_propriedade
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        projeto_id,
                        nome,
                        tipo,
                        endereco or None
                    )
                )

                conexao.commit()

                return redirect(
                    url_for(
                        "dashboard.projeto",
                        projeto_id=projeto_id
                    )
                )

        return render_template(
            "dashboard/nova-propriedade.html",
            mensagem=mensagem,
            erro=erro,
            dados=dados,
            projeto=projeto_atual
        )

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()


# ==================================================
# AMBIENTES DA PROPRIEDADE
# ==================================================

@dashboard_bp.get("/propriedade/<int:propriedade_id>/ambientes")
def ambientes(propriedade_id):

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        # Busca a propriedade e verifica o vínculo do usuário
        cursor.execute(
            """
            SELECT
                pr.id_propiedade AS id,
                pr.nm_propriedade AS nome,
                pr.endereco_propriedade AS endereco,
                pr.id_projeto
            FROM propriedade pr

            INNER JOIN vinculo_projeto_usuario v
                ON pr.id_projeto = v.id_projeto

            WHERE pr.id_propiedade = %s
              AND v.id_user = %s
              AND v.ativo = 1
            """,
            (propriedade_id, session["id_user"])
        )

        propriedade = cursor.fetchone()

        if not propriedade:
            abort(404)

        # Busca os ambientes pertencentes à propriedade
        cursor.execute(
            """
            SELECT
                id_ambiente AS id,
                nm_ambiente AS nome,
                tp_ambiente AS tipo
            FROM ambiente
            WHERE id_propiedade = %s
            ORDER BY id_ambiente
            """,
            (propriedade_id,)
        )

        ambientes = cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()

    return render_template(
        "dashboard/ambientes.html",
        propriedade=propriedade,
        ambientes=ambientes
    )


# ==================================================
# NOVO AMBIENTE
# ==================================================

@dashboard_bp.route(
    "/propriedade/<int:propriedade_id>/novo-ambiente",
    methods=["GET", "POST"]
)
def novo_ambiente(propriedade_id):

    mensagem = None
    erro = None
    dados = {}

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        # Verifica se o usuário é gestor ativo do projeto
        cursor.execute(
            """
            SELECT
                pr.id_propiedade AS id,
                pr.nm_propriedade AS nome,
                pr.endereco_propriedade AS endereco,
                pr.id_projeto
            FROM propriedade pr

            INNER JOIN vinculo_projeto_usuario v
                ON pr.id_projeto = v.id_projeto

            WHERE pr.id_propiedade = %s
              AND v.id_user = %s
              AND v.papel_no_projeto = 'gestor'
              AND v.ativo = 1
            """,
            (propriedade_id, session["id_user"])
        )

        propriedade = cursor.fetchone()

        if not propriedade:
            abort(404)

        if request.method == "POST":

            dados = request.form

            nome = request.form.get("nome", "").strip()
            tipo = request.form.get("tipo", "").strip()

            if not nome:
                erro = "O nome do ambiente é obrigatório."

            else:

                cursor.execute(
                    """
                    INSERT INTO ambiente (
                        id_propiedade,
                        nm_ambiente,
                        tp_ambiente
                    )
                    VALUES (%s, %s, %s)
                    """,
                    (
                        propriedade_id,
                        nome,
                        tipo or None
                    )
                )

                conexao.commit()

                return redirect(
                    url_for(
                        "dashboard.ambientes",
                        propriedade_id=propriedade_id
                    )
                )

        return render_template(
            "dashboard/novo-ambiente.html",
            propriedade=propriedade,
            mensagem=mensagem,
            erro=erro,
            dados=dados
        )

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()


# ==================================================
# EDITAR AMBIENTE
# ==================================================

@dashboard_bp.route(
    "/ambiente/<int:ambiente_id>/editar",
    methods=["GET", "POST"]
)
def editar_ambiente(ambiente_id):

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        # Busca o ambiente e verifica a permissão do gestor
        cursor.execute(
            """
            SELECT
                a.id_ambiente AS id,
                a.nm_ambiente AS nome,
                a.tp_ambiente AS tipo,
                pr.id_propiedade AS propriedade_id,
                pr.nm_propriedade AS propriedade_nome
            FROM ambiente a

            INNER JOIN propriedade pr
                ON a.id_propiedade = pr.id_propiedade

            INNER JOIN vinculo_projeto_usuario v
                ON pr.id_projeto = v.id_projeto

            WHERE a.id_ambiente = %s
              AND v.id_user = %s
              AND v.papel_no_projeto = 'gestor'
              AND v.ativo = 1
            """,
            (ambiente_id, session["id_user"])
        )

        ambiente = cursor.fetchone()

        if not ambiente:
            abort(404)

        mensagem = None
        erro = None

        dados = {
            "nome": ambiente["nome"],
            "tipo": ambiente["tipo"] or ""
        }

        if request.method == "POST":

            nome = request.form.get("nome", "").strip()
            tipo = request.form.get("tipo", "").strip()

            dados = {
                "nome": nome,
                "tipo": tipo
            }

            if not nome:
                erro = "O nome do ambiente é obrigatório."

            else:

                cursor.execute(
                    """
                    UPDATE ambiente
                    SET
                        nm_ambiente = %s,
                        tp_ambiente = %s
                    WHERE id_ambiente = %s
                    """,
                    (
                        nome,
                        tipo or None,
                        ambiente_id
                    )
                )

                conexao.commit()

                return redirect(
                    url_for(
                        "dashboard.ambientes",
                        propriedade_id=ambiente["propriedade_id"]
                    )
                )

        return render_template(
            "dashboard/editar-ambiente.html",
            ambiente=ambiente,
            dados=dados,
            mensagem=mensagem,
            erro=erro
        )

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()


# ==================================================
# EXCLUIR AMBIENTE
# ==================================================

@dashboard_bp.route(
    "/ambiente/<int:ambiente_id>/excluir",
    methods=["POST"]
)
def excluir_ambiente(ambiente_id):

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        # Verifica se o ambiente pertence a um projeto
        # no qual o usuário é gestor ativo
        cursor.execute(
            """
            SELECT
                pr.id_propiedade AS propriedade_id
            FROM ambiente a

            INNER JOIN propriedade pr
                ON a.id_propiedade = pr.id_propiedade

            INNER JOIN vinculo_projeto_usuario v
                ON pr.id_projeto = v.id_projeto

            WHERE a.id_ambiente = %s
              AND v.id_user = %s
              AND v.papel_no_projeto = 'gestor'
              AND v.ativo = 1
            """,
            (ambiente_id, session["id_user"])
        )

        ambiente = cursor.fetchone()

        if not ambiente:
            abort(404)

        cursor.execute(
            """
            DELETE FROM ambiente
            WHERE id_ambiente = %s
            """,
            (ambiente_id,)
        )

        conexao.commit()

        return redirect(
            url_for(
                "dashboard.ambientes",
                propriedade_id=ambiente["propriedade_id"]
            )
        )

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()


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
