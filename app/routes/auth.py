
from flask import Blueprint, render_template

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login():
    return render_template("auth/login.html")


@auth_bp.get("/cadastro")
def cadastro():
    return render_template("auth/cadastro.html")


@auth_bp.get("/recuperar-senha")
def recuperar_senha():
    return render_template("auth/recuperar-senha.html")


@auth_bp.get("/recuperar-senha/codigo")
def recuperar_senha_codigo():
    return render_template("auth/recuperar-senha-codigo.html")


@auth_bp.get("/nova-senha")
def nova_senha():
    return render_template("auth/new-senha.html")
