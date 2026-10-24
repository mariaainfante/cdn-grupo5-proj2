simbolos = "!@#$%&*?"
minimo = 8

def validar_tamanho(senha):
    return len(senha) >= minimo

def tem_minuscula(senha):
    for caractere in senha:
        if caractere.islower():

            return True
        
    return False

def tem_maiuscula(senha):
    for caractere in senha:
        if caractere.isupper():

            return True
        
    return False

def tem_digito(senha):
    for caractere in senha:
        if caractere.isdigit():

            return True
        
    return False

def tem_simbolo(senha):
    for caractere in senha:
        if caractere in simbolos:
            
            return True
        
    return False

def contar_criterios(senha):
    criterios = (
        validar_tamanho(senha),
        tem_minuscula(senha),
        tem_maiuscula(senha),
        tem_digito(senha),
        tem_simbolo(senha),
    )

    return sum(criterios)

def classificar_senha(senha):
    total = contar_criterios(senha)

    if total <= 2:
        return "fraca"
    
    elif total in (3, 4):
        return "media"
    
    else:
        return "forte"