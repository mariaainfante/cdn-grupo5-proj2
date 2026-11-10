from functools import wraps

from flask import Blueprint, redirect, render_template, session, url_for
from mysql.connector import Error

from app.db import get_db

dashboard_bp = Blueprint("dashboard", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


@dashboard_bp.get("/projeto")
@dashboard_bp.get("/projeto/<int:projeto_id>")
@login_required
def projeto(projeto_id=None):
    parametros = [session["user_id"]]
    filtro_projeto = ""
    if projeto_id is not None:
        filtro_projeto = "AND p.id_projeto = %s"
        parametros.append(projeto_id)

    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            f"""
            SELECT
                p.id_projeto,
                p.nm_projeto,
                p.desc_projeto,
                p.estado_projeto,
                p.criado_em,
                p.inicio_previsto,
                p.fim_previsto,
                c.id_cliente,
                c.nm_cliente
            FROM projeto AS p
            INNER JOIN cliente AS c ON c.id_cliente = p.id_cliente
            INNER JOIN vinculo_projeto_usuario AS v
                ON v.id_projeto = p.id_projeto
            WHERE v.id_user = %s
              AND v.ativo = 1
              {filtro_projeto}
            ORDER BY p.criado_em DESC
            LIMIT 1
            """,
            tuple(parametros),
        )
        dados_projeto = cursor.fetchone()
        cursor.close()
    except Error:
        return render_template(
            "dashboard/projeto.html",
            projeto=None,
            erro_banco=True,
            user_role=session.get("user_role", "Usuário"),
            user_name=session.get("user_name", "Usuário"),
        ), 503

    status = 200 if dados_projeto else 404
    return render_template(
        "dashboard/projeto.html",
        projeto=dados_projeto,
        erro_banco=False,
        user_role=session.get("user_role", "Usuário"),
        user_name=session.get("user_name", "Usuário"),
    ), status
