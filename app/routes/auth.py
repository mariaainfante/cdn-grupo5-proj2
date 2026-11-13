
from flask import Blueprint, render_template, request, redirect, url_for, session
from app.database import conectar_banco
import bcrypt
import secrets

auth_bp = Blueprint("auth", __name__)


# ==================================================
# LOGIN
# ==================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")

        if not usuario or not senha:
            mensagem = "Informe seu e-mail e sua senha."
            return render_template("auth/login.html", mensagem=mensagem)

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    id_user,
                    nm_user,
                    email_user,
                    password_hash,
                    papel_global,
                    ativo
                FROM usuario
                WHERE email_user = %s
                """,
                (usuario,)
            )

            usuario_bd = cursor.fetchone()

            if usuario_bd and usuario_bd["ativo"] == 1:

                senha_hash = usuario_bd["password_hash"].encode("utf-8")

                if bcrypt.checkpw(senha.encode("utf-8"), senha_hash):

                    session.clear()

                    session["id_user"] = usuario_bd["id_user"]
                    session["nm_user"] = usuario_bd["nm_user"]
                    session["papel_global"] = usuario_bd["papel_global"]

                    return redirect(url_for("dashboard.gestor"))

            mensagem = "Usuário ou senha incorretos."

            return render_template("auth/login.html", mensagem=mensagem)

        finally:
            cursor.close()
            conexao.close()

    return render_template("auth/login.html")


# ==================================================
# LOGOUT
# ==================================================

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.login"))


# ==================================================
# CADASTRO
# ==================================================

@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefone = request.form.get("telefone", "").strip()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar-senha", "")
        funcao = request.form.get("funcao", "").strip()
        termos = request.form.get("termos")

        if not nome or not email or not telefone or not senha or not confirmar_senha or not funcao:
            mensagem = "Preencha todos os campos."
            return render_template("auth/cadastro.html", mensagem=mensagem)

        if senha != confirmar_senha:
            mensagem = "As senhas não são iguais."
            return render_template("auth/cadastro.html", mensagem=mensagem)

        if not termos:
            mensagem = "Você precisa aceitar os termos de uso."
            return render_template("auth/cadastro.html", mensagem=mensagem)

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT id_user
                FROM usuario
                WHERE email_user = %s
                """,
                (email,)
            )

            usuario_existente = cursor.fetchone()

            if usuario_existente:
                mensagem = "Este e-mail já está cadastrado."
                return render_template("auth/cadastro.html", mensagem=mensagem)

            senha_hash = bcrypt.hashpw(
                senha.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            cursor.execute(
                """
                INSERT INTO usuario (
                    nm_user,
                    email_user,
                    telefone_user,
                    password_hash,
                    papel_global,
                    ativo
                )
                VALUES (%s, %s, %s, %s, 'padrao', 1)
                """,
                (nome, email, telefone, senha_hash)
            )

            conexao.commit()

            return redirect(url_for("auth.login"))

        except Exception:
            conexao.rollback()
            raise

        finally:
            cursor.close()
            conexao.close()

    return render_template("auth/cadastro.html")


# ==================================================
# SOLICITAR RECUPERAÇÃO DE SENHA
# ==================================================

@auth_bp.route("/recuperar-senha", methods=["GET", "POST"])
def recuperar_senha():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()

        if not email:
            mensagem = "Informe seu e-mail."

            return render_template(
                "auth/recuperar-senha.html",
                mensagem=mensagem
            )

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT id_user, nm_user, email_user
                FROM usuario
                WHERE email_user = %s
                  AND ativo = 1
                """,
                (email,)
            )

            usuario = cursor.fetchone()

            session.pop("recuperacao_email", None)
            session.pop("recuperacao_user_id", None)

            session["recuperacao_email"] = email

            if usuario:

                # Gera código aleatório de cinco dígitos
                codigo = str(secrets.randbelow(90000) + 10000)

                # Criptografa o código
                codigo_hash = bcrypt.hashpw(
                    codigo.encode("utf-8"),
                    bcrypt.gensalt()
                ).decode("utf-8")

                # Remove códigos anteriores não utilizados
                cursor.execute(
                    """
                    DELETE FROM recuperacao_senha
                    WHERE id_user = %s
                      AND utilizado = 0
                    """,
                    (usuario["id_user"],)
                )

                # Salva o novo código com validade de 10 minutos
                cursor.execute(
                    """
                    INSERT INTO recuperacao_senha (
                        id_user,
                        codigo_hash,
                        expiracao,
                        utilizado
                    )
                    VALUES (
                        %s,
                        %s,
                        DATE_ADD(NOW(), INTERVAL 10 MINUTE),
                        0
                    )
                    """,
                    (usuario["id_user"], codigo_hash)
                )

                # Envia o e-mail
                from app import mail
                from flask_mail import Message

                mensagem = Message(
                    subject="Recuperação de senha - Conatus",
                    recipients=[email],
                    body=f"""
Olá, {usuario['nm_user']}!

Recebemos uma solicitação para recuperar sua senha no Conatus.

Seu código de verificação é:

{codigo}

Esse código é válido por 10 minutos.

Se você não solicitou essa recuperação, ignore este e-mail.

Equipe Conatus.
"""
                )

                mail.send(mensagem)

                conexao.commit()

            return redirect(url_for("auth.recuperar_senha_codigo"))

        except Exception:
            conexao.rollback()
            raise

        finally:
            cursor.close()
            conexao.close()

    return render_template("auth/recuperar-senha.html")


# ==================================================
# VALIDAR CÓDIGO DE RECUPERAÇÃO
# ==================================================

@auth_bp.route("/recuperar-senha/codigo", methods=["GET", "POST"])
def recuperar_senha_codigo():

    if "recuperacao_email" not in session:
        return redirect(url_for("auth.recuperar_senha"))

    if request.method == "POST":

        codigo1 = request.form.get("codigo1") or ""
        codigo2 = request.form.get("codigo2") or ""
        codigo3 = request.form.get("codigo3") or ""
        codigo4 = request.form.get("codigo4") or ""
        codigo5 = request.form.get("codigo5") or ""

        codigo = codigo1 + codigo2 + codigo3 + codigo4 + codigo5

        if len(codigo) != 5 or not codigo.isdigit():
            mensagem = "Informe os cinco dígitos do código."

            return render_template(
                "auth/recuperar-senha-codigo.html",
                mensagem=mensagem
            )

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT
                    r.id_recuperacao,
                    r.codigo_hash,
                    r.id_user
                FROM recuperacao_senha r
                INNER JOIN usuario u
                    ON r.id_user = u.id_user
                WHERE u.email_user = %s
                  AND u.ativo = 1
                  AND r.utilizado = 0
                  AND r.expiracao > NOW()
                ORDER BY r.id_recuperacao DESC
                LIMIT 1
                """,
                (session["recuperacao_email"],)
            )

            recuperacao = cursor.fetchone()

            if not recuperacao:
                mensagem = "Código inválido ou expirado."

                return render_template(
                    "auth/recuperar-senha-codigo.html",
                    mensagem=mensagem
                )

            codigo_hash = recuperacao["codigo_hash"].encode("utf-8")

            if not bcrypt.checkpw(codigo.encode("utf-8"), codigo_hash):
                mensagem = "Código incorreto. Tente novamente."

                return render_template(
                    "auth/recuperar-senha-codigo.html",
                    mensagem=mensagem
                )

            # Marca o código como utilizado
            cursor.execute(
                """
                UPDATE recuperacao_senha
                SET utilizado = 1
                WHERE id_recuperacao = %s
                """,
                (recuperacao["id_recuperacao"],)
            )

            conexao.commit()

            session["recuperacao_user_id"] = recuperacao["id_user"]

            return redirect(url_for("auth.nova_senha"))

        except Exception:
            conexao.rollback()
            raise

        finally:
            cursor.close()
            conexao.close()

    return render_template("auth/recuperar-senha-codigo.html")


# ==================================================
# CADASTRAR NOVA SENHA
# ==================================================

@auth_bp.route("/nova-senha", methods=["GET", "POST"])
def nova_senha():

    if "recuperacao_user_id" not in session:
        return redirect(url_for("auth.recuperar_senha"))

    if request.method == "POST":

        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar-senha", "")

        if not senha or not confirmar_senha:
            mensagem = "Preencha os dois campos de senha."

            return render_template(
                "auth/new-senha.html",
                mensagem=mensagem
            )

        if senha != confirmar_senha:
            mensagem = "As senhas não são iguais."

            return render_template(
                "auth/new-senha.html",
                mensagem=mensagem
            )

        # Criptografa a nova senha
        senha_hash = bcrypt.hashpw(
            senha.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        conexao = conectar_banco()
        cursor = conexao.cursor()

        try:
            cursor.execute(
                """
                UPDATE usuario
                SET password_hash = %s
                WHERE id_user = %s
                  AND ativo = 1
                """,
                (senha_hash, session["recuperacao_user_id"])
            )

            if cursor.rowcount == 0:
                mensagem = "Não foi possível atualizar a senha."

                return render_template(
                    "auth/new-senha.html",
                    mensagem=mensagem
                )

            conexao.commit()

            session.pop("recuperacao_user_id", None)
            session.pop("recuperacao_email", None)

            return redirect(url_for("auth.login"))

        except Exception:
            conexao.rollback()
            raise

        finally:
            cursor.close()
            conexao.close()

    return render_template("auth/new-senha.html")
