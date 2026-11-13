
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
# AGUARDANDO VÍNCULO
# ==================================================

@dashboard_bp.get("/aguardando-vinculo")
def aguardando_vinculo():

    if session.get("papel_global") != "padrao":
        abort(403)

    return render_template("dashboard/aguardando-vinculo.html")


# ==================================================
# PROJETO
# ==================================================

@dashboard_bp.get("/projeto/<int:projeto_id>")
def projeto(projeto_id):

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
                c.id_cliente AS cliente_id,
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

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_cliente AS id,
                nm_cliente AS nome
            FROM cliente
            ORDER BY nm_cliente ASC
        """)

        clientes = cursor.fetchall()

        if request.method == "POST":

            dados = request.form

            cliente = request.form.get("cliente", "").strip()
            nome = request.form.get("nome", "").strip()
            descricao = request.form.get("descricao", "").strip()
            inicio = request.form.get("inicio", "").strip()
            termino = request.form.get("termino", "").strip()

            if not cliente or not nome or not descricao:

                erro = "Preencha todos os campos obrigatórios."

            elif not cliente.isdigit():

                erro = "Selecione um cliente válido."

            elif inicio and termino and termino < inicio:

                erro = "A data de término não pode ser anterior à data de início."

            else:

                cursor.execute("""
                    SELECT id_cliente
                    FROM cliente
                    WHERE id_cliente = %s
                """, (int(cliente),))

                cliente_bd = cursor.fetchone()

                if not cliente_bd:

                    erro = "Cliente não encontrado."

                else:

                    cursor.execute("""
                        INSERT INTO projeto (
                            id_cliente,
                            nm_projeto,
                            desc_projeto,
                            inicio_previsto,
                            fim_previsto
                        )
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        int(cliente),
                        nome,
                        descricao,
                        inicio or None,
                        termino or None
                    ))

                    id_projeto = cursor.lastrowid

                    cursor.execute("""
                        INSERT INTO vinculo_projeto_usuario (
                            id_projeto,
                            id_user,
                            papel_no_projeto,
                            ativo
                        )
                        VALUES (%s, %s, 'gestor', 1)
                    """, (
                        id_projeto,
                        session["id_user"]
                    ))

                    conexao.commit()

                    return redirect(
                        url_for(
                            "dashboard.projeto",
                            projeto_id=id_projeto
                        )
                    )

        return render_template(
            "dashboard/novo-projeto.html",
            clientes=clientes,
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

@dashboard_bp.get("/projeto/<int:projeto_id>/participantes")
def participantes(projeto_id):

    verificar_gestor_no_projeto(projeto_id)

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                id_projeto,
                nm_projeto
            FROM projeto
            WHERE id_projeto = %s
            """,
            (projeto_id,)
        )

        projeto_atual = cursor.fetchone()

        if not projeto_atual:
            abort(404)

        cursor.execute(
            """
            SELECT
                v.id_vinculo,
                u.id_user,
                u.nm_user AS nome,
                u.email_user AS email,
                v.papel_no_projeto AS papel,
                v.ativo
            FROM vinculo_projeto_usuario v

            INNER JOIN usuario u
                ON v.id_user = u.id_user

            WHERE v.id_projeto = %s

            ORDER BY v.ativo DESC, u.nm_user ASC
            """,
            (projeto_id,)
        )

        participantes_lista = cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()

    return render_template(
        "dashboard/participantes.html",
        projeto=projeto_atual,
        participantes=participantes_lista
    )


# ==================================================
# ADICIONAR PARTICIPANTE
# ==================================================

@dashboard_bp.route(
    "/projeto/<int:projeto_id>/adicionar-participante",
    methods=["GET", "POST"]
)
def adicionar_participante(projeto_id):

    verificar_gestor_no_projeto(projeto_id)

    mensagem = None
    erro = None
    dados = {}

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT id_projeto, nm_projeto
            FROM projeto
            WHERE id_projeto = %s
        """, (projeto_id,))

        projeto_atual = cursor.fetchone()

        if not projeto_atual:
            abort(404)

        if request.method == "POST":

            dados = request.form

            usuario = request.form.get("usuario", "").strip()
            papel = request.form.get("papel", "").strip()

            papeis_validos = [
                "gestor",
                "tecnico",
                "arquiteto",
                "comercial"
            ]

            if not usuario or not papel:
                erro = "Preencha todos os campos obrigatórios."

            elif not usuario.isdigit():
                erro = "Selecione um usuário válido."

            elif papel not in papeis_validos:
                erro = "Selecione um papel válido."

            else:

                cursor.execute("""
                    SELECT id_user
                    FROM usuario
                    WHERE id_user = %s
                    AND ativo = 1
                """, (int(usuario),))

                usuario_bd = cursor.fetchone()

                if not usuario_bd:
                    erro = "Usuário não encontrado ou inativo."

                else:

                    cursor.execute("""
                        SELECT id_vinculo
                        FROM vinculo_projeto_usuario
                        WHERE id_projeto = %s
                        AND id_user = %s
                    """, (projeto_id, int(usuario)))

                    vinculo = cursor.fetchone()

                    if vinculo:

                        cursor.execute("""
                            UPDATE vinculo_projeto_usuario
                            SET papel_no_projeto = %s,
                                ativo = 1
                            WHERE id_vinculo = %s
                        """, (papel, vinculo["id_vinculo"]))

                    else:

                        cursor.execute("""
                            INSERT INTO vinculo_projeto_usuario (
                                id_projeto,
                                id_user,
                                papel_no_projeto,
                                ativo
                            )
                            VALUES (%s, %s, %s, 1)
                        """, (projeto_id, int(usuario), papel))

                    conexao.commit()

                    return redirect(
                        url_for(
                            "dashboard.participantes",
                            projeto_id=projeto_id
                        )
                    )

        cursor.execute("""
            SELECT
                u.id_user AS id,
                u.nm_user AS nome,
                u.email_user AS email
            FROM usuario u
            WHERE u.ativo = 1
            AND NOT EXISTS (
                SELECT 1
                FROM vinculo_projeto_usuario v
                WHERE v.id_projeto = %s
                AND v.id_user = u.id_user
                AND v.ativo = 1
            )
            ORDER BY u.nm_user ASC
        """, (projeto_id,))

        usuarios = cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()

    return render_template(
        "dashboard/adicionar-participante.html",
        projeto=projeto_atual,
        usuarios=usuarios,
        mensagem=mensagem,
        erro=erro,
        dados=dados
    )


# ==================================================
# ALTERAR PAPEL DO PARTICIPANTE
# ==================================================

@dashboard_bp.route(
    "/projeto/<int:projeto_id>/participante/<int:participante_id>/alterar-papel",
    methods=["GET", "POST"]
)
def alterar_papel(projeto_id, participante_id):

    verificar_gestor_no_projeto(projeto_id)

    mensagem = None
    erro = None

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT id_projeto, nm_projeto
            FROM projeto
            WHERE id_projeto = %s
        """, (projeto_id,))

        projeto_atual = cursor.fetchone()

        if not projeto_atual:
            abort(404)

        cursor.execute("""
            SELECT
                v.id_vinculo,
                v.id_user,
                v.papel_no_projeto AS papel,
                u.nm_user AS nome,
                u.email_user AS email
            FROM vinculo_projeto_usuario v

            INNER JOIN usuario u
                ON v.id_user = u.id_user

            WHERE v.id_projeto = %s
              AND v.id_user = %s
            ORDER BY v.ativo DESC, v.id_vinculo DESC
            LIMIT 1
        """, (projeto_id, participante_id))

        participante = cursor.fetchone()

        if not participante:
            abort(404)

        dados = {
            "papel": participante["papel"]
        }

        if request.method == "POST":

            papel = request.form.get("papel", "").strip()

            dados = {
                "papel": papel
            }

            papeis_validos = [
                "gestor",
                "tecnico",
                "arquiteto",
                "comercial"
            ]

            if participante_id == session["id_user"]:
                erro = "Você não pode alterar seu próprio papel."

            elif papel not in papeis_validos:
                erro = "Selecione um papel válido."

            else:

                cursor.execute("""
                    UPDATE vinculo_projeto_usuario
                    SET papel_no_projeto = %s
                    WHERE id_vinculo = %s
                      AND id_projeto = %s
                """, (
                    papel,
                    participante["id_vinculo"],
                    projeto_id
                ))

                conexao.commit()

                return redirect(
                    url_for(
                        "dashboard.participantes",
                        projeto_id=projeto_id
                    )
                )

        return render_template(
            "dashboard/alterar-papel.html",
            projeto=projeto_atual,
            participante=participante,
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
# DESATIVAR PARTICIPANTE
# ==================================================

@dashboard_bp.route(
    "/projeto/<int:projeto_id>/participante/<int:participante_id>/desativar",
    methods=["GET", "POST"]
)
def desativar_participante(projeto_id, participante_id):

    verificar_gestor_no_projeto(projeto_id)

    mensagem = None
    erro = None

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT id_projeto, nm_projeto
            FROM projeto
            WHERE id_projeto = %s
        """, (projeto_id,))

        projeto_atual = cursor.fetchone()

        if not projeto_atual:
            abort(404)

        cursor.execute("""
            SELECT
                v.id_vinculo,
                v.id_user,
                v.papel_no_projeto AS papel,
                v.ativo,
                u.nm_user AS nome,
                u.email_user AS email
            FROM vinculo_projeto_usuario v

            INNER JOIN usuario u
                ON v.id_user = u.id_user

            WHERE v.id_projeto = %s
              AND v.id_user = %s
              AND v.ativo = 1
            LIMIT 1
        """, (projeto_id, participante_id))

        participante = cursor.fetchone()

        if not participante:
            abort(404)

        if request.method == "POST":

            if participante_id == session["id_user"]:

                erro = "Você não pode desativar sua própria participação."

            else:

                if participante["papel"] == "gestor":

                    cursor.execute("""
                        SELECT COUNT(*) AS total
                        FROM vinculo_projeto_usuario
                        WHERE id_projeto = %s
                          AND papel_no_projeto = 'gestor'
                          AND ativo = 1
                    """, (projeto_id,))

                    total_gestores = cursor.fetchone()["total"]

                    if total_gestores <= 1:
                        erro = "Não é possível desativar o último gestor do projeto."

                if not erro:

                    cursor.execute("""
                        UPDATE vinculo_projeto_usuario
                        SET ativo = 0
                        WHERE id_vinculo = %s
                          AND id_projeto = %s
                    """, (
                        participante["id_vinculo"],
                        projeto_id
                    ))

                    conexao.commit()

                    return redirect(
                        url_for(
                            "dashboard.participantes",
                            projeto_id=projeto_id
                        )
                    )

        return render_template(
            "dashboard/desativar-participante.html",
            projeto=projeto_atual,
            participante=participante,
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
# REATIVAR PARTICIPANTE
# ==================================================

@dashboard_bp.route(
    "/projeto/<int:projeto_id>/participante/<int:participante_id>/reativar",
    methods=["POST"]
)
def reativar_participante(projeto_id, participante_id):

    verificar_gestor_no_projeto(projeto_id)

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT id_projeto
            FROM projeto
            WHERE id_projeto = %s
        """, (projeto_id,))

        projeto_atual = cursor.fetchone()

        if not projeto_atual:
            abort(404)

        cursor.execute("""
            SELECT id_vinculo
            FROM vinculo_projeto_usuario
            WHERE id_projeto = %s
              AND id_user = %s
              AND ativo = 0
            LIMIT 1
        """, (projeto_id, participante_id))

        vinculo = cursor.fetchone()

        if not vinculo:
            abort(404)

        cursor.execute("""
            UPDATE vinculo_projeto_usuario
            SET ativo = 1
            WHERE id_vinculo = %s
        """, (vinculo["id_vinculo"],))

        conexao.commit()

        return redirect(
            url_for(
                "dashboard.participantes",
                projeto_id=projeto_id
            )
        )

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()


# ==================================================
# CLIENTES
# ==================================================

@dashboard_bp.get("/clientes")
def clientes():

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_cliente AS id,
                nm_cliente AS nome,
                contato_cliente AS contato,
                email_cliente AS email
            FROM cliente
            ORDER BY nm_cliente ASC
        """)

        clientes = cursor.fetchall()

        return render_template(
            "dashboard/clientes.html",
            clientes=clientes
        )

    finally:
        cursor.close()
        conexao.close()


# ==================================================
# NOVO CLIENTE
# ==================================================

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

            conexao = conectar_banco()
            cursor = conexao.cursor()

            try:

                cursor.execute("""
                    INSERT INTO cliente (
                        nm_cliente,
                        contato_cliente
                    )
                    VALUES (%s, %s)
                """, (nome, contato or ""))

                conexao.commit()

                return redirect(url_for("dashboard.clientes"))

            except Exception:
                conexao.rollback()
                raise

            finally:
                cursor.close()
                conexao.close()

    return render_template(
        "dashboard/novo-cliente.html",
        mensagem=mensagem,
        erro=erro,
        dados=dados
    )


# ==================================================
# INFORMAÇÕES DO CLIENTE
# ==================================================

@dashboard_bp.get("/info-cliente/<int:cliente_id>")
def info_cliente(cliente_id):

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_cliente AS id,
                nm_cliente AS nome,
                contato_cliente AS contato,
                email_cliente AS email
            FROM cliente
            WHERE id_cliente = %s
        """, (cliente_id,))

        cliente = cursor.fetchone()

        if not cliente:
            abort(404)

        return render_template(
            "dashboard/info-cliente.html",
            cliente=cliente
        )

    finally:
        cursor.close()
        conexao.close()


# ==================================================
# EDITAR CLIENTE
# ==================================================

@dashboard_bp.route("/editar-cliente/<int:cliente_id>", methods=["GET", "POST"])
def editar_cliente(cliente_id):

    verificar_gestor_global()

    mensagem = None
    erro = None

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_cliente AS id,
                nm_cliente AS nome,
                contato_cliente AS contato,
                email_cliente AS email
            FROM cliente
            WHERE id_cliente = %s
        """, (cliente_id,))

        cliente = cursor.fetchone()

        if not cliente:
            abort(404)

        dados = cliente.copy()

        if request.method == "POST":

            dados = request.form

            nome = request.form.get("nome", "").strip()
            contato = request.form.get("contato", "").strip()

            if not nome:

                erro = "O nome do cliente é obrigatório."

            else:

                cursor.execute("""
                    UPDATE cliente
                    SET
                        nm_cliente = %s,
                        contato_cliente = %s
                    WHERE id_cliente = %s
                """, (nome, contato or "", cliente_id))

                conexao.commit()

                return redirect(
                    url_for(
                        "dashboard.info_cliente",
                        cliente_id=cliente_id
                    )
                )

        return render_template(
            "dashboard/editar-cliente.html",
            cliente=cliente,
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
# EXCLUIR CLIENTE
# ==================================================

@dashboard_bp.route("/excluir-cliente/<int:cliente_id>", methods=["POST"])
def excluir_cliente(cliente_id):

    verificar_gestor_global()

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_cliente AS id,
                nm_cliente AS nome,
                contato_cliente AS contato,
                email_cliente AS email
            FROM cliente
            WHERE id_cliente = %s
        """, (cliente_id,))

        cliente = cursor.fetchone()

        if not cliente:
            abort(404)

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM projeto
            WHERE id_cliente = %s
        """, (cliente_id,))

        resultado = cursor.fetchone()
        total_projetos = resultado["total"]

        if total_projetos > 0:

            erro = (
                "Não é possível excluir este cliente porque "
                "existem projetos vinculados a ele."
            )

            return render_template(
                "dashboard/info-cliente.html",
                cliente=cliente,
                erro=erro
            )

        cursor.execute("""
            DELETE FROM cliente
            WHERE id_cliente = %s
        """, (cliente_id,))

        conexao.commit()

        return redirect(url_for("dashboard.clientes"))

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()


# ==================================================
# NOVA PROPRIEDADE
# ==================================================

@dashboard_bp.route(
    "/projeto/<int:projeto_id>/nova-propriedade",
    methods=["GET", "POST"]
)
def nova_propriedade(projeto_id):

    verificar_gestor_no_projeto(projeto_id)

    mensagem = None
    erro = None
    dados = {}

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

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

@dashboard_bp.get("/projeto/<int:projeto_id>/historico")
def historico(projeto_id):

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                p.id_projeto AS id,
                p.nm_projeto AS nome
            FROM projeto p

            INNER JOIN vinculo_projeto_usuario v
                ON p.id_projeto = v.id_projeto

            WHERE p.id_projeto = %s
              AND v.id_user = %s
              AND v.ativo = 1
            LIMIT 1
        """, (projeto_id, session["id_user"]))

        projeto_atual = cursor.fetchone()

        if not projeto_atual:
            abort(404)

        cursor.execute("""
            SELECT
                historico.tipo,
                historico.data,
                historico.descricao,
                historico.responsavel
            FROM (
                SELECT
                    eh.acao_evento AS tipo,
                    COALESCE(
                        eh.data_evento,
                        DATE(eh.criado_em)
                    ) AS data,
                    eh.desc_evento AS descricao,
                    COALESCE(
                        u.nm_user,
                        'Usuário não identificado'
                    ) AS responsavel,
                    eh.criado_em AS ordem_data

                FROM evento_historico eh

                LEFT JOIN vinculo_projeto_usuario v
                    ON eh.id_vinculo = v.id_vinculo

                LEFT JOIN usuario u
                    ON v.id_user = u.id_user

                WHERE eh.id_projeto = %s

                UNION ALL

                SELECT
                    'Comentário' AS tipo,
                    DATE(c.criado_em) AS data,
                    c.texto_comentario AS descricao,
                    COALESCE(
                        u.nm_user,
                        'Usuário não identificado'
                    ) AS responsavel,
                    c.criado_em AS ordem_data

                FROM comentario c

                LEFT JOIN vinculo_projeto_usuario v
                    ON c.id_vinculo = v.id_vinculo

                LEFT JOIN usuario u
                    ON v.id_user = u.id_user

                WHERE c.id_projeto = %s
            ) AS historico

            ORDER BY historico.data DESC, historico.ordem_data DESC
        """, (projeto_id, projeto_id))

        historico_projeto = cursor.fetchall()

        return render_template(
            "dashboard/historico.html",
            projeto=projeto_atual,
            historico=historico_projeto
        )

    finally:
        cursor.close()
        conexao.close()


# ==================================================
# NOVO EVENTO
# ==================================================

@dashboard_bp.route(
    "/projeto/<int:projeto_id>/novo-evento",
    methods=["GET", "POST"]
)
def novo_evento(projeto_id):

    mensagem = None
    erro = None
    dados = {}

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                p.id_projeto AS id,
                p.nm_projeto AS nome,
                c.nm_cliente AS cliente,
                v.id_vinculo
            FROM projeto p

            INNER JOIN cliente c
                ON p.id_cliente = c.id_cliente

            INNER JOIN vinculo_projeto_usuario v
                ON p.id_projeto = v.id_projeto

            WHERE p.id_projeto = %s
              AND v.id_user = %s
              AND v.ativo = 1
            LIMIT 1
        """, (projeto_id, session["id_user"]))

        projeto_atual = cursor.fetchone()

        if not projeto_atual:
            abort(404)

        if request.method == "POST":

            dados = request.form

            titulo = request.form.get("titulo", "").strip()
            data = request.form.get("data", "").strip()
            descricao = request.form.get("descricao", "").strip()

            if not titulo or not data or not descricao:

                erro = "Preencha todos os campos obrigatórios."

            else:

                cursor.execute("""
                    INSERT INTO evento_historico (
                        id_projeto,
                        id_vinculo,
                        acao_evento,
                        desc_evento,
                        data_evento
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    projeto_id,
                    projeto_atual["id_vinculo"],
                    "Evento",
                    f"{titulo}: {descricao}",
                    data
                ))

                conexao.commit()

                return redirect(
                    url_for(
                        "dashboard.historico",
                        projeto_id=projeto_id
                    )
                )

        return render_template(
            "dashboard/novo-evento.html",
            projeto=projeto_atual,
            projeto_id=projeto_id,
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
# NOVO COMENTÁRIO
# ==================================================

@dashboard_bp.route(
    "/projeto/<int:projeto_id>/novo-comentario",
    methods=["GET", "POST"]
)
def novo_comentario(projeto_id):

    mensagem = None
    erro = None
    dados = {}

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                p.id_projeto AS id,
                p.nm_projeto AS nome,
                v.id_vinculo
            FROM projeto p

            INNER JOIN vinculo_projeto_usuario v
                ON p.id_projeto = v.id_projeto

            WHERE p.id_projeto = %s
              AND v.id_user = %s
              AND v.ativo = 1
            LIMIT 1
        """, (projeto_id, session["id_user"]))

        projeto_atual = cursor.fetchone()

        if not projeto_atual:
            abort(404)

        if request.method == "POST":

            dados = request.form

            comentario_texto = request.form.get(
                "comentario", ""
            ).strip()

            if not comentario_texto:

                erro = "Escreva um comentário antes de publicar."

            else:

                cursor.execute("""
                    INSERT INTO comentario (
                        id_projeto,
                        id_vinculo,
                        texto_comentario
                    )
                    VALUES (%s, %s, %s)
                """, (
                    projeto_id,
                    projeto_atual["id_vinculo"],
                    comentario_texto
                ))

                conexao.commit()

                return redirect(
                    url_for(
                        "dashboard.historico",
                        projeto_id=projeto_id
                    )
                )

        return render_template(
            "dashboard/novo-comentario.html",
            projeto=projeto_atual,
            projeto_id=projeto_id,
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
# NOVA DECISÃO
# ==================================================

@dashboard_bp.route(
    "/projeto/<int:projeto_id>/nova-decisao",
    methods=["GET", "POST"]
)
def nova_decisao(projeto_id):

    mensagem = None
    erro = None
    dados = {}

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                p.id_projeto AS id,
                p.nm_projeto AS nome,
                v.id_vinculo
            FROM projeto p

            INNER JOIN vinculo_projeto_usuario v
                ON p.id_projeto = v.id_projeto

            WHERE p.id_projeto = %s
              AND v.id_user = %s
              AND v.ativo = 1
            LIMIT 1
        """, (projeto_id, session["id_user"]))

        projeto_atual = cursor.fetchone()

        if not projeto_atual:
            abort(404)

        if request.method == "POST":

            dados = request.form

            titulo = request.form.get("titulo", "").strip()
            descricao = request.form.get("descricao", "").strip()
            data = request.form.get("data", "").strip()

            if not titulo or not descricao or not data:

                erro = "Preencha todos os campos obrigatórios."

            else:

                cursor.execute("""
                    INSERT INTO evento_historico (
                        id_projeto,
                        id_vinculo,
                        acao_evento,
                        desc_evento,
                        data_evento
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    projeto_id,
                    projeto_atual["id_vinculo"],
                    "Decisão",
                    f"{titulo}: {descricao}",
                    data
                ))

                conexao.commit()

                return redirect(
                    url_for(
                        "dashboard.historico",
                        projeto_id=projeto_id
                    )
                )

        return render_template(
            "dashboard/nova-decisao.html",
            projeto=projeto_atual,
            projeto_id=projeto_id,
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
