from flask import Blueprint, render_template, request, redirect, url_for

auth_bp = Blueprint("auth", __name__)


# LOGIN
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        # Dados temporários para teste
        usuario_correto = "teste"
        senha_correta = "123456"

        if usuario == usuario_correto and senha == senha_correta:
            return redirect(url_for("dashboard.gestor"))

        else:
            mensagem = "Usuário ou senha incorretos."

            return render_template("auth/login.html", mensagem=mensagem)

    return render_template("auth/login.html")


# CADASTRO
@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form.get("nome")
        email = request.form.get("email")
        telefone = request.form.get("telefone")
        senha = request.form.get("senha")
        confirmar_senha = request.form.get("confirmar-senha")
        funcao = request.form.get("funcao")
        termos = request.form.get("termos")

        if not nome or not email or not telefone or not senha or not confirmar_senha or not funcao:
            mensagem = "Preencha todos os campos."

        elif senha != confirmar_senha:
            mensagem = "As senhas não são iguais."

        elif not termos:
            mensagem = "Você precisa aceitar os termos de uso."

        else:
            mensagem = f"Cadastro recebido para {nome}! Os dados ainda não foram salvos."

        return render_template("auth/cadastro.html", mensagem=mensagem)

    return render_template("auth/cadastro.html")


# RECUPERAÇÃO DE SENHA
@auth_bp.route("/recuperar-senha", methods=["GET", "POST"])
def recuperar_senha():

    if request.method == "POST":

        email = request.form.get("email")

        if email:
            return redirect(url_for("auth.recuperar_senha_codigo", email=email))

        mensagem = "Informe seu e-mail."

        return render_template("auth/recuperar-senha.html", mensagem=mensagem)

    return render_template("auth/recuperar-senha.html")


@auth_bp.route("/recuperar-senha/codigo", methods=["GET", "POST"])
def recuperar_senha_codigo():

    if request.method == "POST":

        codigo1 = request.form.get("codigo1")
        codigo2 = request.form.get("codigo2")
        codigo3 = request.form.get("codigo3")
        codigo4 = request.form.get("codigo4")
        codigo5 = request.form.get("codigo5")

        codigo = codigo1 + codigo2 + codigo3 + codigo4 + codigo5

        codigo_correto = "12345"

        if codigo == codigo_correto:
            return redirect(url_for("auth.nova_senha"))

        else:
            mensagem = "Código incorreto. Tente novamente."

            return render_template("auth/recuperar-senha-codigo.html", mensagem=mensagem)

    return render_template("auth/recuperar-senha-codigo.html")

# NOVA SENHA
@auth_bp.route("/nova-senha", methods=["GET", "POST"])
def nova_senha():

    if request.method == "POST":

        senha = request.form.get("senha")
        confirmar_senha = request.form.get("confirmar-senha")

        if senha != confirmar_senha:

            mensagem = "As senhas não são iguais."

            return render_template(
                "auth/new-senha.html",
                mensagem=mensagem
            )

        else:

            mensagem = "Senha validada com sucesso! (Alteração ainda não salva.)"

            return render_template(
                "auth/new-senha.html",
                mensagem=mensagem,
                sucesso=True
            )

    return render_template("auth/new-senha.html")