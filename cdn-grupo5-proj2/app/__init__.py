import os

from flask import Flask, render_template

from app.db import init_app as init_db
from app.commands import init_app as init_commands

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-change-this-key")
init_db(app)
init_commands(app)

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
