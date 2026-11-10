# Conatus

Aplicação Flask conectada ao banco MySQL do projeto Conatus.

## Configuração

1. Crie e ative um ambiente virtual Python.
2. Instale as dependências com `pip install -r requirements.txt`.
3. No MySQL Workbench, abra e execute `database/schema.sql`.
4. Copie `.env.example` para `.env` e informe as credenciais do MySQL.
5. Para desenvolvimento, execute `database/demo.sql` no Workbench. O script
   cria quatro contas de teste, um cliente, um projeto e seus vínculos.
6. Execute a aplicação com `python -m flask --app livingmodel run`.

Para criar outra conta sem manter uma senha conhecida no SQL, use
`python -m flask --app livingmodel create-user`.

O login consulta a tabela `usuario`. A página `/projeto` mostra o projeto mais
recente ao qual o usuário autenticado possui vínculo ativo. Um projeto específico
pode ser consultado em `/projeto/<id>`, desde que o usuário tenha vínculo ativo.

As senhas da tabela `usuario` devem ser armazenadas com um hash compatível com
`werkzeug.security.generate_password_hash`.
