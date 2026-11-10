
from flask import Blueprint, render_template

dashboard_bp = Blueprint("dashboard", __name__)


# Tela principal do gestor
@dashboard_bp.get("/gestor")
def gestor():
    return render_template("dashboard/gestor.html")


# Projetos
@dashboard_bp.get("/projeto")
def projeto():
    return render_template("dashboard/projeto.html")


@dashboard_bp.get("/novo-projeto")
def novo_projeto():
    return render_template("dashboard/novo-projeto.html")


@dashboard_bp.get("/editar-projeto")
def editar_projeto():
    return render_template("dashboard/editar-projeto.html")


# Participantes
@dashboard_bp.get("/participantes")
def participantes():
    return render_template("dashboard/participantes.html")


@dashboard_bp.get("/adicionar-participante")
def adicionar_participante():
    return render_template("dashboard/adicionar-participante.html")


@dashboard_bp.get("/alterar-papel")
def alterar_papel():
    return render_template("dashboard/alterar-papel.html")


@dashboard_bp.get("/desativar-participante")
def desativar_participante():
    return render_template("dashboard/desativar-participante.html")


# Clientes
@dashboard_bp.get("/clientes")
def clientes():
    return render_template("dashboard/clientes.html")


@dashboard_bp.get("/novo-cliente")
def novo_cliente():
    return render_template("dashboard/novo-cliente.html")


@dashboard_bp.get("/info-cliente")
def info_cliente():
    return render_template("dashboard/info-cliente.html")


@dashboard_bp.get("/editar-cliente")
def editar_cliente():
    return render_template("dashboard/editar-cliente.html")
