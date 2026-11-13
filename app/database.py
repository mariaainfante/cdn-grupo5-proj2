
import mysql.connector


def conectar_banco():
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="conatus"
    )

    return conexao
