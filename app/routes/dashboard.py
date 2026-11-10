
from flask import Blueprint, render_template

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/gestor")
def gestor():
    return render_template("dashboard/gestor.html")


@dashboard_bp.get("/projeto")
def projeto():
    return render_template("dashboard/projeto.html")


@dashboard_bp.get("/participantes")
def participantes():
    return render_template("dashboard/participantes.html")


@dashboard_bp.get("/info-cliente")
def info_cliente():
    return render_template("dashboard/info-cliente.html")


@dashboard_bp.get("/novo-cliente")
def novo_cliente():
    return render_template("dashboard/novo-cliente.html")


@dashboard_bp.get("/novo-projeto")
def novo_projeto():
    return render_template("dashboard/novo-projeto.html")
