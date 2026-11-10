from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from mysql.connector import Error
from werkzeug.security import check_password_hash

from app.db import get_db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        try:
            cursor = get_db().cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id_user, nm_user, email_user, password_hash, papel_global
                FROM usuario
                WHERE LOWER(email_user) = %s
                """,
                (email,),
            )
            usuario = cursor.fetchone()
            cursor.close()
        except Error:
            flash("Não foi possível acessar o banco de dados.", "danger")
            return render_template("auth/login.html"), 503

        if usuario is None or not check_password_hash(usuario["password_hash"], senha):
            flash("E-mail ou senha inválidos.", "danger")
        else:
            session.clear()
            session["user_id"] = usuario["id_user"]
            session["user_name"] = usuario["nm_user"]
            session["user_role"] = usuario["papel_global"]
            return redirect(url_for("dashboard.projeto"))

    return render_template("auth/login.html")


@auth_bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
