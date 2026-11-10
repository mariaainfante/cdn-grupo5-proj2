import click
from flask.cli import with_appcontext
from mysql.connector import Error
from werkzeug.security import generate_password_hash

from app.db import get_db


@click.command("create-user")
@click.option("--name", prompt="Nome")
@click.option("--email", prompt="E-mail")
@click.option(
    "--role",
    type=click.Choice(["gestor", "padrao"], case_sensitive=False),
    default="gestor",
    show_default=True,
)
@click.password_option("--password", confirmation_prompt=True)
@with_appcontext
def create_user_command(name, email, role, password):
    """Cria um usuário com a senha armazenada de forma segura."""
    if len(password) < 8:
        raise click.ClickException("A senha deve ter pelo menos 8 caracteres.")

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO usuario (nm_user, email_user, password_hash, papel_global)
            VALUES (%s, %s, %s, %s)
            """,
            (
                name.strip(),
                email.strip().lower(),
                generate_password_hash(password),
                role.lower(),
            ),
        )
        db.commit()
    except Error as error:
        db.rollback()
        raise click.ClickException(f"Não foi possível criar o usuário: {error}") from error
    finally:
        cursor.close()

    click.echo("Usuário criado com sucesso.")


def init_app(app):
    app.cli.add_command(create_user_command)
