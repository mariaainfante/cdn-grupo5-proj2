
from flask import Flask, render_template
from flask_mail import Mail
from dotenv import load_dotenv
import os

# ==================================================
# CONFIGURAÇÕES INICIAIS
# ==================================================

load_dotenv()

app = Flask(__name__)

app.secret_key = "conatus-chave-temporaria-2026"


# ==================================================
# CONFIGURAÇÃO DE E-MAIL
# ==================================================

app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]

mail = Mail(app)


# ==================================================
# PÁGINA INICIAL
# ==================================================

@app.route("/")
@app.route("/index")
def index():
    return render_template("auth/landing-page.html")


# ==================================================
# BLUEPRINTS
# ==================================================

from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.orcamento import orcamento_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(orcamento_bp)
