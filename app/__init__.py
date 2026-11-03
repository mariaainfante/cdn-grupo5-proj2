from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

from app.routes.auth import auth_bp

app.register_blueprint(auth_bp)