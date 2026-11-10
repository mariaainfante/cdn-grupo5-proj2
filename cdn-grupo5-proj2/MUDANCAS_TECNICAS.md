# Mudanças técnicas do projeto Conatus

Este documento explica as alterações realizadas para conectar o frontend existente ao backend Flask e ao banco de dados MySQL. O trabalho foi mantido dentro do escopo atual do projeto: landing page, login e visualização dos dados de um projeto.

## Resumo das alterações

Antes das alterações, as páginas eram apenas visuais. O formulário de login não processava dados, a tela de projeto exibia informações fixas e não havia conexão entre Flask e MySQL.

Após as alterações, o sistema possui o seguinte fluxo:

```text
Landing page
    ↓
Login com e-mail e senha
    ↓
Consulta do usuário no MySQL
    ↓
Criação da sessão
    ↓
Consulta de projeto com vínculo ativo
    ↓
Exibição dos dados reais no frontend
    ↓
Logout e encerramento da sessão
```

## Backend Flask

### Conexão com o MySQL

O arquivo `app/db.py` centraliza a conexão com o banco de dados.

A conexão usa as seguintes variáveis de ambiente:

- `DB_HOST`: endereço do servidor MySQL;
- `DB_PORT`: porta do MySQL;
- `DB_USER`: usuário do banco;
- `DB_PASSWORD`: senha do banco;
- `DB_NAME`: nome do schema;
- `SECRET_KEY`: chave usada para proteger a sessão Flask.

Essas informações não ficam diretamente no código. O arquivo `.env.example` serve como modelo para criar um arquivo `.env` local.

O `.env` não deve ser enviado ao Git, pois pode conter senhas e outras informações privadas.

### Login

A rota `/login` passou a aceitar os métodos `GET` e `POST`.

No envio do formulário, o backend:

1. Recebe o e-mail e a senha;
2. Consulta o usuário na tabela `usuario`;
3. Compara a senha informada com o hash armazenado em `password_hash`;
4. Cria uma sessão quando as credenciais estão corretas;
5. Redireciona o usuário para `/projeto`.

As senhas não são armazenadas em texto puro. A validação utiliza as funções de segurança do Werkzeug, biblioteca incluída no Flask.

### Sessão e logout

Após o login, a sessão guarda:

- ID do usuário;
- nome do usuário;
- papel global.

A rota `/logout` limpa a sessão e retorna para a tela de login.

A página de projeto é protegida. Se alguém tentar acessar `/projeto` sem estar autenticado, será redirecionado para `/login`.

### Consulta do projeto

As rotas disponíveis são:

```text
/projeto
/projeto/<id>
```

A consulta relaciona as tabelas:

```text
usuario
    ↓
vinculo_projeto_usuario
    ↓
projeto
    ↓
cliente
```

O backend somente retorna um projeto quando o usuário possui um vínculo ativo. Dessa forma, não basta conhecer o ID do projeto para acessá-lo.

Quando nenhum projeto autorizado é encontrado, o frontend exibe uma mensagem informativa. Se houver falha na conexão com o MySQL, a página mostra uma mensagem de erro em vez de interromper a aplicação sem explicação.

### Comando para criar usuários

Foi adicionado o comando:

```powershell
python -m flask --app livingmodel create-user
```

O comando solicita nome, e-mail, papel e senha. A senha é convertida em hash antes de ser salva no banco.

## Banco de dados

### Modelo importado

O modelo original do MySQL Workbench contém as seguintes tabelas:

- `ambiente`;
- `cliente`;
- `comentario`;
- `evento_historico`;
- `projeto`;
- `projeto_sensor`;
- `propriedade`;
- `sensor`;
- `usuario`;
- `vinculo_projeto_usuario`.

O fluxo implementado atualmente utiliza diretamente:

- `usuario`;
- `cliente`;
- `projeto`;
- `vinculo_projeto_usuario`.

As demais tabelas permanecem disponíveis para funcionalidades futuras.

### Scripts SQL

O diretório `database` contém:

- `schema.sql`: estrutura mínima necessária para executar o sistema atual;
- `demo.sql`: contas, cliente, projeto e vínculos para testes.

Se o modelo completo já foi importado pelo Forward Engineer do MySQL Workbench, não é necessário executar `schema.sql`. Nesse caso, basta executar `demo.sql` para inserir os dados de demonstração.

O `demo.sql` pode ser executado novamente sem duplicar usuários ou vínculos.

### Contas de demonstração

As contas abaixo são exclusivas para desenvolvimento e apresentação:

| Perfil | E-mail | Senha |
|---|---|---|
| Gestor | `gestor@conatus.com` | `Gestor@123` |
| Técnico | `tecnico@conatus.com` | `Tecnico@123` |
| Arquiteto | `arquiteto@conatus.com` | `Arquiteto@123` |
| Comercial | `comercial@conatus.com` | `Comercial@123` |

Essas senhas não devem ser reutilizadas em produção.

## Frontend

As telas existentes foram conectadas às rotas Flask:

- Os botões da landing page direcionam para a rota de login;
- O formulário de login envia e-mail e senha ao backend;
- A tela de projeto usa os dados retornados pelo MySQL;
- O nome do usuário autenticado aparece no cabeçalho;
- O botão de logout encerra a sessão;
- Links para páginas que ainda não existem foram removidos para evitar erros 404.

Os seguintes dados deixaram de ser fixos no HTML:

- nome do projeto;
- descrição;
- cliente;
- estado;
- data de criação;
- início previsto;
- término previsto.

## Dependências

As dependências foram registradas em `requirements.txt`:

```text
Flask
mysql-connector-python
python-dotenv
```

Para instalá-las:

```powershell
python -m pip install -r requirements.txt
```

## Como executar

### 1. Configurar o ambiente

Copie `.env.example` para `.env` e informe as credenciais do MySQL:

```env
SECRET_KEY=uma-chave-segura
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=senha-do-mysql
DB_NAME=conatus
```

### 2. Preparar os dados

No MySQL Workbench, execute `database/demo.sql`.

### 3. Iniciar o Flask

```powershell
python -m flask --app livingmodel run
```

### 4. Abrir o sistema

```text
http://127.0.0.1:5000
```

## Roteiro de teste manual

1. Abra a landing page;
2. Clique em **Entrar**;
3. Faça login com uma das contas de demonstração;
4. Confirme o redirecionamento para `/projeto`;
5. Verifique se o projeto e o cliente aparecem com dados do banco;
6. Clique em **Sair**;
7. Tente abrir `/projeto` novamente;
8. Confirme que o sistema redireciona para o login;
9. Tente uma senha incorreta e confirme a mensagem de credenciais inválidas.

## Testes automatizados

Os testes estão no diretório `tests` e verificam:

- redirecionamento de usuário não autenticado;
- links da landing page;
- criação de sessão após login válido;
- renderização dos dados do projeto;
- registro do comando de criação de usuário.

Para executar:

```powershell
python -m unittest discover -s tests -v
```

## Organização e Git

O `.gitignore` foi atualizado para impedir o versionamento de:

- arquivo `.env`;
- diretórios `__pycache__`;
- arquivos compilados `.pyc`.

Os arquivos `__pycache__` que já estavam no repositório foram removidos do índice do Git. Eles podem continuar existindo no computador, mas não aparecerão em commits futuros.

## Limites da implementação atual

Esta entrega conecta somente as telas já existentes. Ainda não foram implementados:

- cadastro de clientes pela interface;
- criação e edição de projetos pela interface;
- lista de projetos;
- propriedades e ambientes;
- participantes;
- eventos e comentários;
- linha do tempo;
- indicadores.

Essas funcionalidades podem utilizar as tabelas existentes em etapas futuras, mas não fazem parte da integração atual.
