def validar_nome(nome):
    nome = nome.strip()

    if nome == "":
        return False
    
    palavras = nome.split()

    for palavra in palavras:
        if not palavra.isalpha():

            return False
        
    return True


def calcular_digito_verificador(numeros):
    tamanho = len(numeros)
    peso = tamanho + 1
    soma = 0

    for i in range(tamanho):
        soma += int(numeros[i]) * peso
        peso -= 1

    resto = soma % 11

    if resto < 2:
        digito = 0

    else:
        digito = 11 - resto

    return digito


def cpf_todos_digitos_iguais(cpf):
    for i in range(1, len(cpf)):
        if cpf[i] != cpf[0]:

            return False
        
    return True

def validar_cpf(cpf):
    cpf = cpf.strip()
    cpf_numeros = cpf.replace(".", "").replace("-", "")

    if len(cpf_numeros) != 11:
        return False
    
    if not cpf_numeros.isdigit():
        return False
    
    if cpf_todos_digitos_iguais(cpf_numeros):
        return False

    primeiros_nove = cpf_numeros[0:9]
    digito1 = calcular_digito_verificador(primeiros_nove)

    if digito1 != int(cpf_numeros[9]):
        return False

    primeiros_dez = primeiros_nove + str(digito1)
    digito2 = calcular_digito_verificador(primeiros_dez)

    if digito2 != int(cpf_numeros[10]):
        return False

    return True

def mascarar_cpf(cpf):
    inicio = cpf[0:3]
    fim = cpf[9:11]

    return inicio + ".***.***-" + fim

def validar_telefone(telefone):
    telefone = telefone.strip()
    telefone_numeros = telefone.replace("(", "").replace(")", "")
    telefone_numeros = telefone_numeros.replace("-", "").replace(" ", "")

    if not telefone_numeros.isdigit():
        return False
    
    if len(telefone_numeros) < 10 or len(telefone_numeros) > 11:
        return False
    
    return True

def validar_email(email):
    email = email.strip()

    if email.count("@") != 1:
        return False

    partes = email.split("@")
    parte_antes = partes[0]
    parte_depois = partes[1]

    if parte_antes == "" or parte_depois == "":
        return False

    if len(parte_depois) <= 4:
        return False

    if parte_depois[-4:] != ".com":
        return False

    return True


def validar_cidade(cidade):
    cidade = cidade.strip()
    return cidade != ""

def lista_tem_item_vazio(texto):
    # verdadeiro se o espaçp entre as vírgulas estiver em branco (ex: "sala,,quarto")
    itens = texto.split(",")

    for item in itens:
        if item.strip() == "":
            return True
        
    return False


def validar_sensores(sensores):
    sensores = sensores.strip()

    if sensores == "":
        return False
    
    if lista_tem_item_vazio(sensores):
        return False
    
    return True

def validar_ambientes(ambientes):
    ambientes = ambientes.strip()

    if ambientes == "":
        return False
    
    if lista_tem_item_vazio(ambientes):
        return False
    
    return True

def cpf_existe(clientes, cpf):
    cpf_numeros = cpf.replace(".", "").replace("-", "")

    for cliente in clientes:
        if cliente[1] == cpf_numeros:  # posição 1 da lista = cpf
            return True
        
    return False
