import unittest
from datetime import date, datetime
from unittest.mock import Mock, patch

from werkzeug.security import generate_password_hash

from app import app
from app.commands import create_user_command


class RouteTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, SECRET_KEY="test-key")
        self.client = app.test_client()

    def test_projeto_exige_login(self):
        resposta = self.client.get("/projeto")
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/login", resposta.headers["Location"])

    def test_landing_page_aponta_para_login(self):
        resposta = self.client.get("/")
        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b'href="/login"', resposta.data)
        self.assertNotIn(b"cadastro.html", resposta.data)

    @patch("app.routes.auth.get_db")
    def test_login_valido_cria_sessao(self, get_db_mock):
        cursor = Mock()
        cursor.fetchone.return_value = {
            "id_user": 1,
            "nm_user": "Gestor",
            "email_user": "gestor@conatus.com",
            "password_hash": generate_password_hash("senha123"),
            "papel_global": "gestor",
        }
        get_db_mock.return_value.cursor.return_value = cursor

        resposta = self.client.post(
            "/login",
            data={"email": "gestor@conatus.com", "senha": "senha123"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/projeto", resposta.headers["Location"])

    @patch("app.routes.dashboard.get_db")
    def test_projeto_renderiza_dados_do_banco(self, get_db_mock):
        cursor = Mock()
        cursor.fetchone.return_value = {
            "id_projeto": 10,
            "nm_projeto": "Automação Residencial",
            "desc_projeto": "Projeto integrado ao banco.",
            "estado_projeto": "em_andamento",
            "criado_em": datetime(2026, 11, 9, 10, 30),
            "inicio_previsto": date(2026, 11, 10),
            "fim_previsto": date(2026, 12, 20),
            "id_cliente": 5,
            "nm_cliente": "Cliente Teste",
        }
        get_db_mock.return_value.cursor.return_value = cursor

        with self.client.session_transaction() as sessao:
            sessao["user_id"] = 1
            sessao["user_role"] = "gestor"
            sessao["user_name"] = "Gestor"

        resposta = self.client.get("/projeto/10")

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Automa\xc3\xa7\xc3\xa3o Residencial", resposta.data)
        self.assertIn(b"Cliente Teste", resposta.data)
        self.assertNotIn(b'href="/gestor"', resposta.data)

    def test_comando_create_user_esta_registrado(self):
        self.assertIn(create_user_command.name, app.cli.commands)


if __name__ == "__main__":
    unittest.main()
