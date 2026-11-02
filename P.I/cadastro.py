from validacao import (
    validar_nome,
    validar_cpf,
    validar_telefone,
    validar_email,
    validar_cidade,
    validar_sensores,
    validar_ambientes,
    cpf_existe,
    mascarar_cpf,
)

from senha import classificar_senha

# Cada cliente é uma lista nesta ordem:
# [0] nome  
# [1] cpf  
# [2] telefone  
# [3] email  
# [4] cidade
# [5] senha  
# [6] projeto aprovado (sim/não)  
# [7] sensores por ambiente  
# [8] ambientes
# [9] valor aprovado (fica 0 até o orçamento ser aceito)


def ler_nome():
    nome = input("Nome completo do cliente: ")

    while not validar_nome(nome):
        print("Nome inválido! Digite apenas letras e espaços.")
        nome = input("Nome completo do cliente: ")

    return nome.strip().upper()


def ler_cpf(clientes):
    cpf = input("CPF (11 números, com ou sem pontuação): ")

    while (not validar_cpf(cpf)) or cpf_existe(clientes, cpf):
        if not validar_cpf(cpf):
            print("CPF inválido!")

        else:
            print("Já existe um cliente cadastrado com esse CPF!")

        cpf = input("CPF (11 números, com ou sem pontuação): ")

    return cpf.replace(".", "").replace("-", "")


def ler_telefone():
    telefone = input("Telefone com DDD: ")

    while not validar_telefone(telefone):
        print("Telefone inválido! Digite de 10 a 11 números, com DDD.")
        telefone = input("Telefone com DDD: ")

    return telefone


def ler_email():
    email = input("E-mail: ")

    while not validar_email(email):
        print("E-mail inválido! Use o formato nome@dominio.com")
        email = input("E-mail: ")

    return email.strip().lower()


def ler_cidade():
    cidade = input("Cidade: ")

    while not validar_cidade(cidade):
        print("Cidade não pode ficar em branco!")
        cidade = input("Cidade: ")

    return cidade.strip().upper()


def ler_senha():
    print("Senha: minimo 8 caracteres, com maiuscula, minuscula, numero e simbolo (! @ # $ % & * ?)")
    senha = input("Crie uma senha: ")

    while classificar_senha(senha) == "fraca":
        print("Senha fraca! Tente novamente.")
        senha = input("Crie uma senha: ")

    return senha


def ler_ambientes():
    ambientes = input("Ambientes do imóvel (separados por vírgula): ")

    while not validar_ambientes(ambientes):
        print("Informe os ambientes corretamente, sem itens em branco (ex.: Sala, Quarto).")
        ambientes = input("Ambientes do imóvel (separados por vírgula): ")

    return ambientes.strip().upper()


def ler_sensores_por_ambiente(ambientes):
    lista_ambientes = ambientes.split(",")
    sensores_completo = ""

    for ambiente in lista_ambientes:
        ambiente = ambiente.strip()
        pergunta = "Sensores/dispositivos para o ambiente " + ambiente + " (separados por vírgula): "
        sensores_ambiente = input(pergunta)

        while not validar_sensores(sensores_ambiente):
            print("Informe os sensores corretamente, sem itens em branco.")
            sensores_ambiente = input(pergunta)

        sensores_ambiente = sensores_ambiente.strip().upper()

        if sensores_completo == "":
            sensores_completo = ambiente + ": " + sensores_ambiente

        else:
            sensores_completo = sensores_completo + " | " + ambiente + ": " + sensores_ambiente

    return sensores_completo


def cadastrar_cliente(clientes):
    print()
    print("--- CADASTRO DE NOVO CLIENTE (ARQUITETO) ---")
    nome = ler_nome()
    cpf = ler_cpf(clientes)
    telefone = ler_telefone()
    email = ler_email()
    cidade = ler_cidade()
    senha = ler_senha()
    ambientes = ler_ambientes()
    sensores = ler_sensores_por_ambiente(ambientes)

    novo_cliente = [nome, cpf, telefone, email, cidade, senha, False, sensores, ambientes, 0]
    clientes.append(novo_cliente)
    print("Cliente cadastrado com sucesso!")
    print()


def contar_sensores(sensores):
    total = 0

    for bloco in sensores.split("|"):
        partes_bloco = bloco.split(":")
        lista_sensores = partes_bloco[1].split(",")

        for sensor in lista_sensores:
            if sensor.strip() != "":
                total += 1

    return total


def gerar_orcamento(clientes):
    if len(clientes) == 0:
        print()
        print("Nenhum cliente cadastrado ainda.")
        print()

        return

    cpf = input("Digite o CPF do cliente para gerar o orçamento: ")
    cpf = cpf.replace(".", "").replace("-", "")

    encontrou = False

    for cliente in clientes:
        if cliente[1] == cpf:
            encontrou = True

            if cliente[6]:
                print()
                print("Este cliente já teve o orçamento aceito anteriormente.")
                print("Valor fechado: R$ " + str(cliente[9]) + ",00")
                print()

                return

            quantidade_ambientes = len(cliente[8].split(","))
            total_sensores = contar_sensores(cliente[7])
            valor_total = (quantidade_ambientes * 300) + (total_sensores * 50)

            print()
            print("--- ORÇAMENTO (FLEX) ---")
            print("Ambientes do imóvel:", cliente[8])
            print("Sensores por ambiente:", cliente[7])
            print("Quantidade de ambientes:", quantidade_ambientes)
            print("Quantidade de sensores:", total_sensores)
            print("Valor estimado do projeto: R$ " + str(valor_total) + ",00")

            resposta = input("O cliente aceita o orçamento? (sim/nao): ")
            resposta = resposta.strip().lower()

            while resposta != "sim" and resposta != "nao":
                print("Resposta inválida! Digite 'sim' ou 'nao'.")
                resposta = input("O cliente aceita o orçamento? (sim/nao): ")
                resposta = resposta.strip().lower()

            if resposta == "sim":
                cliente[6] = True
                cliente[9] = valor_total
                print("Orçamento aceito! Projeto aprovado.")

            else:
                print("Orçamento recusado pelo cliente.")

            print()

    if not encontrou:
        print()
        print("Cliente não encontrado.")
        print()


def listar_clientes(clientes):
    print()
    print("--- LISTA DE CLIENTES CADASTRADOS ---")

    if len(clientes) == 0:
        print("Nenhum cliente cadastrado ainda.")
        print()

        return
    
    for i in range(len(clientes)):
        cliente = clientes[i]
        print(i + 1, ") Nome:", cliente[0])
        print("   CPF:", mascarar_cpf(cliente[1]))
        print("   Telefone:", cliente[2])
        print("   E-mail:", cliente[3])
        print("   Cidade:", cliente[4])
        print("   Senha: ", "*" * len(cliente[5]))

        if cliente[6]:
            print("   Projeto: aprovado - R$ " + str(cliente[9]) + ",00")

        else:
            print("   Projeto: aguardando orçamento/aprovação")

        print("-" * 40)

    print()


def buscar_cliente(clientes):
    if len(clientes) == 0:
        print()
        print("Nenhum cliente cadastrado ainda.")
        print()

        return
    
    termo = input("Digite o nome (ou parte dele) para buscar: ")
    termo = termo.strip().upper()
    encontrou = False

    for cliente in clientes:
        if termo in cliente[0]:
            print()
            print("Nome:", cliente[0])
            print("CPF:", mascarar_cpf(cliente[1]))
            print("Telefone:", cliente[2])
            print("E-mail:", cliente[3])
            print("Cidade:", cliente[4])
            print("Senha: ", "*" * len(cliente[5]))

            if cliente[6]:
                print("Projeto: aprovado - R$ " + str(cliente[9]) + ",00")

            else:
                print("Projeto: aguardando orçamento/aprovação")

            print("-" * 40)


            encontrou = True

    if not encontrou:
        print()
        print("Nenhum cliente encontrado com esse nome.")

def listar_projetos_tecnico(clientes):
    print()
    print("--- PROJETOS APROVADOS (TÉCNICO) ---")
    tem_projeto = False

    for i in range(len(clientes)):
        cliente = clientes[i]

        if cliente[6]:
            tem_projeto = True
            print("Projeto nº", i + 1)
            print("Sensores por ambiente:", cliente[7])
            print("-" * 40)

    if not tem_projeto:
        print("Nenhum projeto aprovado no momento.")

    print()


def listar_projetos_arquiteto(clientes):
    print()
    print("--- PROJETOS APROVADOS (ARQUITETO) ---")
    tem_projeto = False

    for i in range(len(clientes)):
        cliente = clientes[i]

        if cliente[6]:
            tem_projeto = True
            print("Projeto nº", i + 1)
            print("Ambientes do imóvel:", cliente[8])
            print("Sensores por ambiente:", cliente[7])
            print("-" * 40)

    if not tem_projeto:
        print("Nenhum projeto aprovado no momento.")

    print()

def area_cliente(clientes):
    if len(clientes) == 0:
        print()
        print("Nenhum cliente cadastrado ainda.")
        print()

        return

    print()
    print("--- ÁREA DO CLIENTE ---")
    cpf = input("Digite seu CPF: ")
    cpf = cpf.replace(".", "").replace("-", "")
    senha = input("Digite sua senha: ")

    encontrou = False

    for cliente in clientes:
        if cliente[1] == cpf and cliente[5] == senha:
            encontrou = True

            if not cliente[6]:
                print()
                print("Seu orçamento ainda não foi aprovado.")
                print("Assim que o orçamento for aceito, sua área ficará disponível.")
                print()
                
                return

            print()
            print("Bem-vindo(a),", cliente[0])
            print("CPF:", mascarar_cpf(cliente[1]))
            print("Telefone:", cliente[2])
            print("E-mail:", cliente[3])
            print("Cidade:", cliente[4])
            print("Status do projeto: aprovado")
            print("Valor do projeto: R$ " + str(cliente[9]) + ",00")
            print("Ambientes do imóvel:", cliente[8])
            print("Sensores por ambiente:", cliente[7])
            print()

    if not encontrou:
        print()
        print("CPF ou senha incorretos.")
        print()