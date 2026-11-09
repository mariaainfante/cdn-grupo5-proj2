from flask import Blueprint, render_template

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/projeto")
def projeto():
    return render_template("dashboard/projeto.html")