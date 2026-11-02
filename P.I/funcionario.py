from validacao import validar_email

def email_funcionario_existe(funcionarios, email, perfil):
    for funcionario in funcionarios:
        if funcionario[0] == email and funcionario[2] == perfil:

            return True

    return False

def ler_email_funcionario(funcionarios, perfil):
    email = input("E-mail: ")

    while (not validar_email(email)) or email_funcionario_existe(funcionarios, email, perfil):
        if not validar_email(email):
            print("E-mail inválido! Use o formato nome@dominio.com ")

        else:
            print("Já existe um cadastro com esse e-mail para este perfil. ")
            
        email = input("E-mail: ")

    return email.strip().lower()

def ler_senha_funcionario():
    senha = input("Crie uma senha: ")

    while senha.strip() == "":
        print("A senha não pode ficar em branco! ")
        senha = input("Crie uma senha: ")

    return senha

def cadastrar_funcionario(funcionarios, perfil):
    print()
    print("--- CADASTRO DE ACESSO -", perfil.upper(), "---")
    email = ler_email_funcionario(funcionarios, perfil)
    senha = ler_senha_funcionario()

    novo_funcionario = [email, senha, perfil]
    funcionarios.append(novo_funcionario)
    print("Cadastro realizado com sucesso! ")
    print()

def login_funcionario(funcionarios, perfil):
    email = input("E-mail: ")
    email = email.strip().lower()
    senha = input("Senha: ")

    for funcionario in funcionarios:
        if funcionario[0] == email and funcionario[1] == senha and funcionario[2] == perfil:
            print()
            print("Login realizado com sucesso! ")
            print()

            return True

    print()
    print("E-mail ou senha incorretos. ")
    print()

    return False

def acesso_funcionario(funcionarios, perfil):
    print()
    print("--- ACESSO", perfil.upper(), "---")
    print("1 - Entrar ")
    print("2 - Cadastrar novo acesso ")
    opcao = input("Escolha uma opção: ")
    opcao = opcao.strip()

    if opcao == "1":
        return login_funcionario(funcionarios, perfil)
    
    elif opcao == "2":
        cadastrar_funcionario(funcionarios, perfil)

        return True
    
    
    else:
        print()
        print("Opção inválida!")
        print()

        return False