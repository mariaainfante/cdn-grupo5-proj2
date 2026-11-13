from app.database import conectar_banco

try:
    conexao = conectar_banco()

    if conexao.is_connected():
        print("Conexão com o banco Conatus realizada com sucesso!")

    conexao.close()

except Exception as erro:
    print("Erro ao conectar:", erro)