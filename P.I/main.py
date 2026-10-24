from cadastro import (
    cadastrar_cliente,
    gerar_orcamento,
    listar_clientes,
    buscar_cliente,
    listar_projetos_tecnico,
    listar_projetos_arquiteto,
    area_cliente,
)

from funcionario import acesso_funcionario

def exibir_menu_login():
    print("-" * 40)
    print(" CONATUS - ACESSO AO SISTEMA ")
    print("-" * 40)
    print("1 - Consultor ")
    print("2 - Técnico ")
    print("3 - Arquiteto ")
    print("4 - Cliente ")
    print("5 - Sair ")
    print("-" * 40)

def exibir_menu_flex():
    print("-" * 40)
    print(" MENU CONSULTOR ")
    print("-" * 40)
    print("1 - Gerar orçamento / aprovar projeto ")
    print("2 - Listar todos os clientes ")
    print("3 - Buscar cliente por nome ")
    print("4 - Voltar ")
    print("-" * 40)

def menu_flex(clientes):
    opcao = ""

    while opcao != "4":
        exibir_menu_flex()
        opcao = input("Escolha uma opção: ")
        opcao = opcao.strip()

        if opcao == "1":
            gerar_orcamento(clientes)

        elif opcao == "2":
            listar_clientes(clientes)

        elif opcao == "3":
            buscar_cliente(clientes)

        elif opcao == "4":
            print()

        else:
            print()
            print("Opção inválida! Tente novamente. ")
            print()


def exibir_menu_arquiteto():
    print("-" * 40)
    print(" MENU ARQUITETO ")
    print("-" * 40)
    print("1 - Cadastrar novo cliente ")
    print("2 - Listar projetos aprovados ")
    print("3 - Voltar ")
    print("-" * 40)

def menu_arquiteto(clientes):
    opcao = ""

    while opcao != "3":
        exibir_menu_arquiteto()
        opcao = input("Escolha uma opção: ")
        opcao = opcao.strip()

        if opcao == "1":
            cadastrar_cliente(clientes)

        elif opcao == "2":
            listar_projetos_arquiteto(clientes)

        elif opcao == "3":
            print()
            
        else:
            print()
            print("Opção inválida! Tente novamente. ")
            print()

def main():
    clientes = [] 
    funcionarios = []  
    opcao = ""

    while opcao != "5":
        exibir_menu_login()
        opcao = input("Escolha uma opção: ")
        opcao = opcao.strip()

        if opcao == "1":
            if acesso_funcionario(funcionarios, "CONSULTOR "):
                menu_flex(clientes)

        elif opcao == "2":
            if acesso_funcionario(funcionarios, "TÉCNICO "):
                listar_projetos_tecnico(clientes)

        elif opcao == "3":
            if acesso_funcionario(funcionarios, "ARQUITETO "):
                menu_arquiteto(clientes)

        elif opcao == "4":
            area_cliente(clientes)

        elif opcao == "5":
            print()
            print("Encerrando o sistema. Até logo! ")

        else:
            print()
            print("Opção inválida! Tente novamente. ")
            print()

if __name__ == "__main__":
    main()