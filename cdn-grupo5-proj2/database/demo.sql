USE conatus;

-- Contas exclusivas para desenvolvimento e demonstração.

START TRANSACTION;

INSERT INTO usuario (nm_user, email_user, password_hash, papel_global)
VALUES
    ('Gestor Demonstração', 'gestor@conatus.com', 'scrypt:32768:8:1$4bFlTmpG5jAAiJoX$348582cb857b2733ba268cea7738a9ed51cacf7b1bc13ce15e9c34619cc8f5cfe5ecaa2cdd690f6c56d835d6516f9a0f20dcbefc69ed3543f6a70c89ddf5b34a', 'gestor'),
    ('Técnico Demonstração', 'tecnico@conatus.com', 'scrypt:32768:8:1$8JSqmROBgFf09i13$eb09fd173d3c047a59ac6ae0f2bbd165e46860762d336cec2414c55b86f9251bd8c308bba8dca4c32c0e3936c860bd33b22556e140d7767003b54b5148ce52eb', 'padrao'),
    ('Arquiteto Demonstração', 'arquiteto@conatus.com', 'scrypt:32768:8:1$JHabQxnVUIUfeFjG$4863a53be35389a3f18baa4383b277e39081abd7ac9037c5dd9167a7e38c0e125b6c04c60b9083f392967fed31da8575a67e87c3084ff2a8e8c7a1d2baf2b29d', 'padrao'),
    ('Comercial Demonstração', 'comercial@conatus.com', 'scrypt:32768:8:1$4PwBdFYgqFhUM81L$ee0481cd498eb370eca863c1688ccdbb5fe0662ef105c63e8e319077bb5e43ca95ed784e298cf306ff34525f1d976dc3f5ce032b68008711aa87d3962b88cf5e', 'padrao')
ON DUPLICATE KEY UPDATE
    nm_user = VALUES(nm_user),
    password_hash = VALUES(password_hash),
    papel_global = VALUES(papel_global);

INSERT INTO cliente (nm_cliente, contato_cliente)
SELECT 'Cliente demonstração', 'cliente@exemplo.com'
WHERE NOT EXISTS (
    SELECT 1 FROM cliente WHERE nm_cliente = 'Cliente demonstração'
);

SET @cliente_id = (
    SELECT id_cliente FROM cliente
    WHERE nm_cliente = 'Cliente demonstração'
    ORDER BY id_cliente LIMIT 1
);

INSERT INTO projeto (
    id_cliente, nm_projeto, desc_projeto, estado_projeto,
    inicio_previsto, fim_previsto
)
SELECT
    @cliente_id,
    'Automação residencial',
    'Projeto de demonstração integrado ao Flask e ao MySQL.',
    'em_andamento',
    CURRENT_DATE,
    DATE_ADD(CURRENT_DATE, INTERVAL 60 DAY)
WHERE NOT EXISTS (
    SELECT 1 FROM projeto WHERE nm_projeto = 'Automação residencial'
);

SET @projeto_id = (
    SELECT id_projeto FROM projeto
    WHERE nm_projeto = 'Automação residencial'
    ORDER BY id_projeto LIMIT 1
);

INSERT INTO vinculo_projeto_usuario
    (id_projeto, id_user, papel_no_projeto, ativo)
SELECT @projeto_id, id_user, 'manager', 1 FROM usuario
WHERE email_user = 'gestor@conatus.com'
ON DUPLICATE KEY UPDATE papel_no_projeto = 'manager', ativo = 1;

INSERT INTO vinculo_projeto_usuario
    (id_projeto, id_user, papel_no_projeto, ativo)
SELECT @projeto_id, id_user, 'technician', 1 FROM usuario
WHERE email_user = 'tecnico@conatus.com'
ON DUPLICATE KEY UPDATE papel_no_projeto = 'technician', ativo = 1;

INSERT INTO vinculo_projeto_usuario
    (id_projeto, id_user, papel_no_projeto, ativo)
SELECT @projeto_id, id_user, 'architect', 1 FROM usuario
WHERE email_user = 'arquiteto@conatus.com'
ON DUPLICATE KEY UPDATE papel_no_projeto = 'architect', ativo = 1;

INSERT INTO vinculo_projeto_usuario
    (id_projeto, id_user, papel_no_projeto, ativo)
SELECT @projeto_id, id_user, 'commercial', 1 FROM usuario
WHERE email_user = 'comercial@conatus.com'
ON DUPLICATE KEY UPDATE papel_no_projeto = 'commercial', ativo = 1;

COMMIT;
