import os

import mysql.connector
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=current_app.config["DB_HOST"],
            port=current_app.config["DB_PORT"],
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASSWORD"],
            database=current_app.config["DB_NAME"],
        )
    return g.db


def close_db(_exception=None):
    db = g.pop("db", None)
    if db is not None and db.is_connected():
        db.close()


def init_app(app):
    app.config.from_mapping(
        DB_HOST=os.getenv("DB_HOST", "localhost"),
        DB_PORT=int(os.getenv("DB_PORT", "3306")),
        DB_USER=os.getenv("DB_USER", "root"),
        DB_PASSWORD=os.getenv("DB_PASSWORD", ""),
        DB_NAME=os.getenv("DB_NAME", "conatus"),
    )
    app.teardown_appcontext(close_db)
