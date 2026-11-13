
from flask import Blueprint, render_template, abort, redirect, url_for, session

from app.database import conectar_banco


consultor_bp = Blueprint(
    "consultor",
    __name__,
    url_prefix="/consultor"
)


# ==================================================
# PROTEÇÃO DE ACESSO
# ==================================================

@consultor_bp.before_request
def verificar_login():

    if "id_user" not in session:
        return redirect(url_for("auth.login"))

    if session.get("papel_global") != "padrao":
        abort(403)


# ==================================================
# VERIFICAÇÃO DE PERMISSÃO DO CONSULTOR NO PROJETO
# ==================================================

def verificar_consultor_no_projeto(projeto_id):

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        print("USUÁRIO DA SESSÃO:", session.get("id_user"))
        print("PROJETO SOLICITADO:", projeto_id)

        cursor.execute(
            """
            SELECT id_vinculo
            FROM vinculo_projeto_usuario
            WHERE id_projeto = %s
              AND id_user = %s
              AND papel_no_projeto = 'comercial'
              AND ativo = 1
            """,
            (projeto_id, session["id_user"])
        )

        vinculo = cursor.fetchone()

        print("VÍNCULO ENCONTRADO:", vinculo)

        if not vinculo:
            abort(403)

        return vinculo

    finally:
        cursor.close()
        conexao.close()


# ==================================================
# TELA PRINCIPAL DO CONSULTOR
# ==================================================

@consultor_bp.get("/")
def inicio():

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        # ------------------------------------------
        # PROJETOS VINCULADOS AO CONSULTOR
        # ------------------------------------------

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
              AND v.papel_no_projeto = 'comercial'
              AND v.ativo = 1

            ORDER BY p.criado_em DESC
            """,
            (session["id_user"],)
        )

        projetos = cursor.fetchall()

        # ------------------------------------------
        # INDICADORES DO PAINEL
        # ------------------------------------------

        total_projetos = len(projetos)

        projetos_andamento = sum(
            1 for projeto in projetos
            if projeto["estado"] == "em_andamento"
        )

        projetos_concluidos = sum(
            1 for projeto in projetos
            if projeto["estado"] == "concluido"
        )

        # ------------------------------------------
        # ATIVIDADES RECENTES
        # ------------------------------------------

        cursor.execute(
            """
            SELECT
                e.id_evento,
                e.acao_evento,
                e.desc_evento,
                e.criado_em,
                p.nm_projeto AS projeto

            FROM evento_historico e

            INNER JOIN projeto p
                ON e.id_projeto = p.id_projeto

            WHERE EXISTS (
                SELECT 1
                FROM vinculo_projeto_usuario v

                WHERE v.id_projeto = e.id_projeto
                  AND v.id_user = %s
                  AND v.papel_no_projeto = 'comercial'
                  AND v.ativo = 1
            )

            ORDER BY e.criado_em DESC

            LIMIT 5
            """,
            (session["id_user"],)
        )

        atividades = cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()

    return render_template(
        "consultor/consultor.html",
        projetos=projetos,
        total_projetos=total_projetos,
        projetos_andamento=projetos_andamento,
        projetos_concluidos=projetos_concluidos,
        atividades=atividades
    )


# ==================================================
# DETALHES DO PROJETO
# ==================================================

@consultor_bp.get("/projeto/<int:projeto_id>")
def projeto(projeto_id):

    verificar_consultor_no_projeto(projeto_id)

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                p.id_projeto,
                p.nm_projeto,
                p.desc_projeto,
                p.estado_projeto,
                p.criado_em,
                p.inicio_previsto,
                p.fim_previsto,

                c.nm_cliente,
                c.contato_cliente,
                c.email_cliente

            FROM projeto p

            INNER JOIN cliente c
                ON p.id_cliente = c.id_cliente

            WHERE p.id_projeto = %s
            """,
            (projeto_id,)
        )

        projeto = cursor.fetchone()

        if not projeto:
            abort(404)

    finally:
        cursor.close()
        conexao.close()

    return render_template(
        "consultor/projeto.html",
        projeto=projeto
    )
