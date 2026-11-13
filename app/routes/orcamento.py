
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, abort, flash, send_file, current_app
)
from app.database import conectar_banco
from decimal import Decimal, InvalidOperation
from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, Image, HRFlowable
)


orcamento_bp = Blueprint("orcamento", __name__)


# ==================================================
# PROTEÇÃO DE ACESSO
# ==================================================

@orcamento_bp.before_request
def verificar_login():
    if "id_user" not in session:
        return redirect(url_for("auth.login"))


# ==================================================
# VERIFICAR ACESSO À PROPRIEDADE
# ==================================================

def verificar_acesso_propriedade(id_propiedade):

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.id_projeto
        FROM propriedade p
        INNER JOIN vinculo_projeto_usuario v
            ON v.id_projeto = p.id_projeto
        WHERE p.id_propiedade = %s
          AND v.id_user = %s
          AND v.ativo = 1
    """, (id_propiedade, session["id_user"]))

    acesso = cursor.fetchone()

    cursor.close()
    conexao.close()

    if not acesso:
        abort(403)

    return acesso["id_projeto"]

def verificar_permissao_gestor(id_propiedade):

    id_projeto = verificar_acesso_propriedade(id_propiedade)

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT papel_no_projeto
        FROM vinculo_projeto_usuario
        WHERE id_projeto = %s
          AND id_user = %s
          AND ativo = 1
    """, (id_projeto, session["id_user"]))

    vinculo = cursor.fetchone()

    cursor.close()
    conexao.close()

    if not vinculo or vinculo["papel_no_projeto"] != "gestor":
        abort(403)

    return id_projeto


# ==================================================
# LISTAR ORÇAMENTOS DA PROPRIEDADE
# ==================================================

@orcamento_bp.route("/propriedade/<int:id_propiedade>/orcamentos")
def listar_orcamentos(id_propiedade):

    verificar_acesso_propriedade(id_propiedade)

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            o.id_orcamento,
            o.versao,
            o.status_orcamento,
            o.validade,
            o.valor_total,
            o.criado_em,
            o.atualizado_em,
            p.id_projeto,
            p.nm_projeto,
            pr.id_propiedade,
            pr.nm_propriedade,
            c.nm_cliente
        FROM orcamento o
        INNER JOIN propriedade pr
            ON pr.id_propiedade = o.id_propiedade
        INNER JOIN projeto p
            ON p.id_projeto = pr.id_projeto
        INNER JOIN cliente c
            ON c.id_cliente = p.id_cliente
        WHERE o.id_propiedade = %s
        ORDER BY o.versao DESC
    """, (id_propiedade,))

    orcamentos = cursor.fetchall()

    cursor.execute("""
        SELECT
            p.id_projeto,
            p.nm_projeto,
            c.nm_cliente,
            pr.id_propiedade,
            pr.nm_propriedade
        FROM propriedade pr
        INNER JOIN projeto p
            ON p.id_projeto = pr.id_projeto
        INNER JOIN cliente c
            ON c.id_cliente = p.id_cliente
        WHERE pr.id_propiedade = %s
    """, (id_propiedade,))

    propriedade = cursor.fetchone()

    cursor.close()
    conexao.close()

    if not propriedade:
        abort(404)

    return render_template(
        "dashboard/orcamentos.html",
        orcamentos=orcamentos,
        projeto=propriedade,
        propriedade=propriedade
    )



# ==================================================
# CRIAR NOVO ORÇAMENTO OU NOVA VERSÃO
# ==================================================


@orcamento_bp.route(
    "/propriedade/<int:id_propiedade>/orcamento/novo",
    methods=["GET", "POST"]
)
def novo_orcamento(id_propiedade):

    id_projeto = verificar_permissao_gestor(id_propiedade)

    id_orcamento_base = request.values.get(
        "id_orcamento_base",
        type=int
    )

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        # --------------------------------------------------
        # BUSCAR PROPRIEDADE
        # --------------------------------------------------

        cursor.execute("""
            SELECT
                pr.id_propiedade,
                pr.nm_propriedade,
                p.id_projeto,
                p.nm_projeto,
                c.nm_cliente
            FROM propriedade pr
            INNER JOIN projeto p
                ON p.id_projeto = pr.id_projeto
            INNER JOIN cliente c
                ON c.id_cliente = p.id_cliente
            WHERE pr.id_propiedade = %s
        """, (id_propiedade,))

        propriedade = cursor.fetchone()

        if not propriedade:
            abort(404)

        validade_inicial = None
        observacoes_iniciais = ""

        # --------------------------------------------------
        # VERIFICAR SE EXISTE UMA VERSÃO ANTERIOR
        # --------------------------------------------------

        if id_orcamento_base:

            cursor.execute("""
                SELECT
                    id_orcamento,
                    validade,
                    observacoes
                FROM orcamento
                WHERE id_orcamento = %s
                  AND id_propiedade = %s
            """, (
                id_orcamento_base,
                id_propiedade
            ))

            orcamento_base = cursor.fetchone()

            if not orcamento_base:
                abort(404)

            validade_inicial = orcamento_base["validade"]
            observacoes_iniciais = (
                orcamento_base["observacoes"] or ""
            )

            # Copiar os itens da versão anterior
            cursor.execute("""
                SELECT
                    descricao_item AS nm_sensor,
                    quantidade,
                    preco_unitario
                FROM item_orcamento
                WHERE id_orcamento = %s
                ORDER BY id_item_orcamento
            """, (id_orcamento_base,))

            sensores = cursor.fetchall()

        else:

            # --------------------------------------------------
            # NOVO ORÇAMENTO: BUSCAR SENSORES DA PROPRIEDADE
            # --------------------------------------------------

            cursor.execute("""
                SELECT
                    CONCAT(
                        s.nm_sensor,
                        ' - ',
                        a.nm_ambiente
                    ) AS nm_sensor,
                    aus.quantidade,
                    aus.preco_unitario
                FROM ambiente_sensor aus
                INNER JOIN ambiente a
                    ON a.id_ambiente = aus.id_ambiente
                INNER JOIN propriedade pr
                    ON pr.id_propiedade = a.id_propiedade
                INNER JOIN sensor s
                    ON s.id_sensor = aus.id_sensor
                WHERE pr.id_propiedade = %s
                ORDER BY a.nm_ambiente, s.nm_sensor
            """, (id_propiedade,))

            sensores = cursor.fetchall()

        # --------------------------------------------------
        # SALVAR ORÇAMENTO
        # --------------------------------------------------

        if request.method == "POST":

            validade = request.form.get("validade") or None

            observacoes = request.form.get(
                "observacoes",
                ""
            ).strip()

            descricoes = request.form.getlist("descricao_item[]")
            quantidades = request.form.getlist("quantidade[]")
            precos = request.form.getlist("preco_unitario[]")

            itens = []
            valor_total = Decimal("0.00")

            try:

                if not (
                    len(descricoes) ==
                    len(quantidades) ==
                    len(precos)
                ):
                    raise ValueError("Dados dos itens incompletos.")

                for descricao, quantidade, preco in zip(
                    descricoes,
                    quantidades,
                    precos
                ):

                    descricao = descricao.strip()

                    if not descricao:
                        continue

                    quantidade = Decimal(
                        quantidade.replace(",", ".")
                    )

                    preco = Decimal(
                        preco.replace(",", ".")
                    )

                    if (
                        not quantidade.is_finite()
                        or not preco.is_finite()
                        or quantidade <= 0
                        or preco < 0
                    ):
                        raise InvalidOperation

                    subtotal = (
                        quantidade * preco
                    ).quantize(Decimal("0.01"))

                    itens.append({
                        "descricao": descricao,
                        "quantidade": quantidade,
                        "preco": preco,
                        "subtotal": subtotal
                    })

                    valor_total += subtotal

                if not itens:
                    raise ValueError(
                        "Adicione pelo menos um item."
                    )

                if validade:
                    datetime.strptime(validade, "%Y-%m-%d")

               
                # --------------------------------------------------
                # BLOQUEAR PROPRIEDADE PARA EVITAR CONFLITO DE VERSÃO
                # --------------------------------------------------

                cursor.execute("""
                    SELECT id_propiedade
                    FROM propriedade
                    WHERE id_propiedade = %s
                    FOR UPDATE
                """, (id_propiedade,))

                # Consumir o resultado da consulta
                # O bloqueio continua ativo até o commit ou rollback
                cursor.fetchone()

                # --------------------------------------------------
                # CALCULAR PRÓXIMA VERSÃO
                # --------------------------------------------------

                cursor.execute("""
                    SELECT
                        COALESCE(MAX(versao), 0) + 1
                        AS proxima_versao
                    FROM orcamento
                    WHERE id_propiedade = %s
                """, (id_propiedade,))

                versao = cursor.fetchone()["proxima_versao"]

                # --------------------------------------------------
                # CRIAR NOVO ORÇAMENTO
                # --------------------------------------------------

                cursor.execute("""
                    INSERT INTO orcamento (
                        id_projeto,
                        id_propiedade,
                        versao,
                        status_orcamento,
                        validade,
                        valor_total,
                        observacoes
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        'em_elaboracao',
                        %s,
                        %s,
                        %s
                    )
                """, (
                    id_projeto,
                    id_propiedade,
                    versao,
                    validade,
                    valor_total,
                    observacoes
                ))

                id_orcamento = cursor.lastrowid

                # --------------------------------------------------
                # INSERIR ITENS NA NOVA VERSÃO
                # --------------------------------------------------

                for item in itens:

                    cursor.execute("""
                        INSERT INTO item_orcamento (
                            id_orcamento,
                            descricao_item,
                            quantidade,
                            preco_unitario,
                            subtotal
                        )
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        id_orcamento,
                        item["descricao"],
                        item["quantidade"],
                        item["preco"],
                        item["subtotal"]
                    ))

                # --------------------------------------------------
                # REGISTRAR HISTÓRICO
                # --------------------------------------------------

                if id_orcamento_base:

                    mensagem = (
                        f"Nova versão {versao} criada "
                        f"a partir do orçamento "
                        f"{id_orcamento_base}."
                    )

                    acao = "Criação de nova versão"

                else:

                    mensagem = (
                        f"Orçamento versão {versao} criado."
                    )

                    acao = "Criação do orçamento"

                cursor.execute("""
                    INSERT INTO historico_orcamento (
                        id_orcamento,
                        acao,
                        status_novo,
                        observacao
                    )
                    VALUES (%s, %s, 'em_elaboracao', %s)
                """, (
                    id_orcamento,
                    acao,
                    mensagem
                ))

                conexao.commit()

                flash(
                    "Orçamento criado com sucesso!",
                    "success"
                )

                return redirect(url_for(
                    "orcamento.listar_orcamentos",
                    id_propiedade=id_propiedade
                ))

            except (InvalidOperation, ValueError):
                conexao.rollback()

                flash(
                    "Verifique os itens, quantidades e preços informados.",
                    "danger"
                )

                # Preservar os itens digitados se houver erro
                sensores = []

                for descricao, quantidade, preco in zip(
                    descricoes,
                    quantidades,
                    precos
                ):
                    sensores.append({
                        "nm_sensor": descricao,
                        "quantidade": quantidade,
                        "preco_unitario": preco
                    })

        return render_template(
            "dashboard/novo_orcamento.html",
            projeto=propriedade,
            propriedade=propriedade,
            sensores=sensores,
            validade_inicial=validade_inicial,
            observacoes_iniciais=observacoes_iniciais,
            id_orcamento_base=id_orcamento_base
        )

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()

# ==================================================
# VISUALIZAR DETALHES DO ORÇAMENTO
# ==================================================

@orcamento_bp.route("/orcamento/<int:id_orcamento>")
def detalhes_orcamento(id_orcamento):

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            o.*,
            p.id_projeto,
            p.nm_projeto,
            pr.id_propiedade,
            pr.nm_propriedade,
            c.nm_cliente
        FROM orcamento o
        INNER JOIN propriedade pr
            ON pr.id_propiedade = o.id_propiedade
        INNER JOIN projeto p
            ON p.id_projeto = pr.id_projeto
        INNER JOIN cliente c
            ON c.id_cliente = p.id_cliente
        WHERE o.id_orcamento = %s
    """, (id_orcamento,))

    orcamento = cursor.fetchone()

    cursor.close()
    conexao.close()

    if not orcamento:
        abort(404)

    verificar_acesso_propriedade(orcamento["id_propiedade"])

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM item_orcamento
        WHERE id_orcamento = %s
        ORDER BY id_item_orcamento
    """, (id_orcamento,))

    itens = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM historico_orcamento
        WHERE id_orcamento = %s
        ORDER BY realizado_em DESC
    """, (id_orcamento,))

    historico = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template(
        "dashboard/detalhes_orcamento.html",
        orcamento=orcamento,
        itens=itens,
        historico=historico
    )


# ==================================================
# GERAR PDF DO ORÇAMENTO
# ==================================================

@orcamento_bp.route("/orcamento/<int:id_orcamento>/pdf")
def gerar_pdf(id_orcamento):

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            o.*,
            p.id_projeto,
            p.nm_projeto,
            pr.id_propiedade,
            pr.nm_propriedade,
            c.nm_cliente
        FROM orcamento o
        INNER JOIN propriedade pr
            ON pr.id_propiedade = o.id_propiedade
        INNER JOIN projeto p
            ON p.id_projeto = pr.id_projeto
        INNER JOIN cliente c
            ON c.id_cliente = p.id_cliente
        WHERE o.id_orcamento = %s
    """, (id_orcamento,))

    orcamento = cursor.fetchone()

    if not orcamento:
        cursor.close()
        conexao.close()
        abort(404)

    cursor.execute("""
        SELECT
            descricao_item,
            quantidade,
            preco_unitario,
            subtotal
        FROM item_orcamento
        WHERE id_orcamento = %s
        ORDER BY id_item_orcamento
    """, (id_orcamento,))

    itens = cursor.fetchall()

    cursor.close()
    conexao.close()

    verificar_acesso_propriedade(orcamento["id_propiedade"])

    arquivo = BytesIO()

    documento = SimpleDocTemplate(
        arquivo,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=15 * mm,
        bottomMargin=20 * mm,
        title=f"Orçamento Conatus - {orcamento['id_orcamento']}",
        author="Conatus"
    )

    azul = colors.HexColor("#2f5f9a")
    azul_claro = colors.HexColor("#eaf1f8")
    texto = colors.HexColor("#252d35")
    cinza = colors.HexColor("#687580")
    borda = colors.HexColor("#dce3eb")

    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "TituloConatus",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=19,
        textColor=azul,
        alignment=TA_RIGHT,
        spaceAfter=2
    )

    estilo_subtitulo = ParagraphStyle(
        "SubtituloConatus",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=cinza,
        alignment=TA_RIGHT
    )

    estilo_secao = ParagraphStyle(
        "SecaoConatus",
        parent=estilos["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=azul,
        spaceBefore=8,
        spaceAfter=7
    )

    estilo_normal = ParagraphStyle(
        "NormalConatus",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=texto
    )

    estilo_pequeno = ParagraphStyle(
        "PequenoConatus",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=cinza
    )

    estilo_total = ParagraphStyle(
        "TotalConatus",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=azul,
        alignment=TA_RIGHT
    )

    estilo_cabecalho_tabela = ParagraphStyle(
        "CabecalhoTabela",
        parent=estilo_normal,
        fontName="Helvetica-Bold",
        fontSize=8,
        textColor=texto
    )

    def formatar_moeda(valor):

        valor = Decimal(str(valor or 0))

        valor_formatado = f"{valor:,.2f}"
        valor_formatado = valor_formatado.replace(",", "X")
        valor_formatado = valor_formatado.replace(".", ",")
        valor_formatado = valor_formatado.replace("X", ".")

        return f"R$ {valor_formatado}"

    def formatar_data(data):

        if not data:
            return "Não informada"

        return data.strftime("%d/%m/%Y")

    def texto_seguro(valor):

        if valor is None or valor == "":
            return "-"

        return escape(str(valor))

    status_legiveis = {
        "em_elaboracao": "Em elaboração",
        "em_revisao": "Em revisão",
        "enviado_ao_cliente": "Enviado ao cliente",
        "aprovado": "Aprovado",
        "rejeitado": "Rejeitado"
    }

    status = status_legiveis.get(
        orcamento["status_orcamento"],
        orcamento["status_orcamento"]
    )

    elementos = []

    # --------------------------------------------------
    # CABEÇALHO COM A LOGO
    # --------------------------------------------------

    caminho_logo = os.path.join(
        current_app.root_path,
        "static",
        "img",
        "Logoconatus.png"
    )

    if os.path.exists(caminho_logo):

        logo = Image(
            caminho_logo,
            width=38 * mm,
            height=18 * mm,
            kind="proportional"
        )

        cabecalho_texto = [
            Paragraph("ORÇAMENTO", estilo_titulo),
            Paragraph("AUTOMAÇÃO INTELIGENTE", estilo_subtitulo),
            Paragraph(
                f"Nº {orcamento['id_orcamento']} "
                f"• Versão {orcamento['versao']}",
                estilo_subtitulo
            )
        ]

        cabecalho = Table(
            [[logo, cabecalho_texto]],
            colWidths=[75 * mm, 95 * mm]
        )

    else:

        cabecalho = Table(
            [[
                Paragraph("CONATUS", estilo_titulo),
                [
                    Paragraph("ORÇAMENTO", estilo_titulo),
                    Paragraph(
                        f"Nº {orcamento['id_orcamento']} "
                        f"• Versão {orcamento['versao']}",
                        estilo_subtitulo
                    )
                ]
            ]],
            colWidths=[75 * mm, 95 * mm]
        )

    cabecalho.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4)
    ]))

    elementos.append(cabecalho)
    elementos.append(Spacer(1, 1.5 * mm))

    elementos.append(HRFlowable(
        width="100%",
        thickness=1.5,
        color=azul,
        spaceAfter=3.5 * mm
    ))

    # --------------------------------------------------
    # INFORMAÇÕES DO ORÇAMENTO
    # --------------------------------------------------

    elementos.append(Paragraph(
        "INFORMAÇÕES DO ORÇAMENTO",
        estilo_secao
    ))

    dados_orcamento = [
        [
            Paragraph("<b>Cliente</b>", estilo_normal),
            Paragraph(texto_seguro(orcamento["nm_cliente"]), estilo_normal)
        ],
        [
            Paragraph("<b>Projeto</b>", estilo_normal),
            Paragraph(texto_seguro(orcamento["nm_projeto"]), estilo_normal)
        ],
        [
            Paragraph("<b>Propriedade</b>", estilo_normal),
            Paragraph(texto_seguro(orcamento["nm_propriedade"]), estilo_normal)
        ],
        [
            Paragraph("<b>Status</b>", estilo_normal),
            Paragraph(texto_seguro(status), estilo_normal)
        ],
        [
            Paragraph("<b>Data de criação</b>", estilo_normal),
            Paragraph(formatar_data(orcamento["criado_em"]), estilo_normal)
        ],
        [
            Paragraph("<b>Validade</b>", estilo_normal),
            Paragraph(formatar_data(orcamento["validade"]), estilo_normal)
        ]
    ]

    tabela_dados = Table(
        dados_orcamento,
        colWidths=[40 * mm, 130 * mm]
    )

    tabela_dados.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), azul_claro),
        ("BOX", (0, 0), (-1, -1), 0.5, borda),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, borda),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
    ]))

    elementos.append(tabela_dados)
    elementos.append(Spacer(1, 5 * mm))

    # --------------------------------------------------
    # ITENS DO ORÇAMENTO
    # --------------------------------------------------

    elementos.append(Paragraph(
        "ITENS DO ORÇAMENTO",
        estilo_secao
    ))

    dados_itens = [[
        Paragraph("Descrição", estilo_cabecalho_tabela),
        Paragraph("Qtd.", estilo_cabecalho_tabela),
        Paragraph("Valor unitário", estilo_cabecalho_tabela),
        Paragraph("Subtotal", estilo_cabecalho_tabela)
    ]]

    for item in itens:

        dados_itens.append([
            Paragraph(texto_seguro(item["descricao_item"]), estilo_normal),
            Paragraph(str(item["quantidade"]).replace(".", ","), estilo_normal),
            Paragraph(formatar_moeda(item["preco_unitario"]), estilo_normal),
            Paragraph(formatar_moeda(item["subtotal"]), estilo_normal)
        ])

    if not itens:
        dados_itens.append([
            Paragraph("Nenhum item cadastrado.", estilo_normal),
            "",
            "",
            ""
        ])

    tabela_itens = Table(
        dados_itens,
        colWidths=[75 * mm, 20 * mm, 37 * mm, 38 * mm],
        repeatRows=1
    )

    tabela_itens.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), azul_claro),
        ("BOX", (0, 0), (-1, -1), 0.5, borda),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, borda),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9)
    ]))

    elementos.append(tabela_itens)
    elementos.append(Spacer(1, 5 * mm))

    # --------------------------------------------------
    # VALOR TOTAL
    # --------------------------------------------------

    total = Paragraph(
        f"VALOR TOTAL: {formatar_moeda(orcamento['valor_total'])}",
        estilo_total
    )

    tabela_total = Table(
        [[total]],
        colWidths=[170 * mm]
    )

    tabela_total.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), azul_claro),
        ("BOX", (0, 0), (-1, -1), 0.7, azul),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12)
    ]))

    elementos.append(tabela_total)
    elementos.append(Spacer(1, 5 * mm))

    # --------------------------------------------------
    # OBSERVAÇÕES
    # --------------------------------------------------

    if orcamento["observacoes"]:

        elementos.append(Paragraph(
            "OBSERVAÇÕES",
            estilo_secao
        ))

        observacoes = texto_seguro(
            orcamento["observacoes"]
        ).replace("\n", "<br/>")

        elementos.append(Paragraph(
            observacoes,
            estilo_normal
        ))

        elementos.append(Spacer(1, 8 * mm))

    else:
        elementos.append(Spacer(1, 5 * mm))

    # --------------------------------------------------
    # APROVAÇÃO E ASSINATURA
    # --------------------------------------------------

    elementos.append(Paragraph(
        "APROVAÇÃO DO CLIENTE",
        estilo_secao
    ))

    elementos.append(Paragraph(
        "Ao assinar, o cliente declara estar de acordo com os "
        "itens e valores apresentados neste orçamento.",
        estilo_pequeno
    ))

    elementos.append(Spacer(1, 17 * mm))

    assinatura = Table(
        [
            ["________________________________", "________________________________"],
            [
                Paragraph("Assinatura do cliente", estilo_pequeno),
                Paragraph("Data da aprovação", estilo_pequeno)
            ]
        ],
        colWidths=[85 * mm, 85 * mm]
    )

    assinatura.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4)
    ]))

    elementos.append(assinatura)
    elementos.append(Spacer(1, 10 * mm))

    elementos.append(HRFlowable(
        width="100%",
        thickness=0.5,
        color=borda
    ))

    elementos.append(Spacer(1, 3 * mm))

    elementos.append(Paragraph(
        "Conatus | Documento gerado automaticamente pelo sistema.",
        ParagraphStyle(
            "RodapeConatus",
            parent=estilo_pequeno,
            alignment=TA_CENTER
        )
    ))

    documento.build(elementos)

    arquivo.seek(0)

    return send_file(
        arquivo,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=(
            f"orcamento_conatus_{id_orcamento}_"
            f"v{orcamento['versao']}.pdf"
        )
    )


# ==================================================
# ALTERAR STATUS DO ORÇAMENTO
# ==================================================

@orcamento_bp.route(
    "/orcamento/<int:id_orcamento>/status",
    methods=["POST"]
)
def alterar_status(id_orcamento):

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_orcamento,
                id_propiedade,
                status_orcamento
            FROM orcamento
            WHERE id_orcamento = %s
        """, (id_orcamento,))

        orcamento = cursor.fetchone()

        if not orcamento:
            abort(404)

        verificar_permissao_gestor(orcamento["id_propiedade"])

        status_atual = orcamento["status_orcamento"]
        novo_status = request.form.get("status_novo")

        transicoes = {
            "em_elaboracao": ["em_revisao"],
            "em_revisao": ["enviado_ao_cliente"],
            "enviado_ao_cliente": ["aprovado", "rejeitado"],
            "aprovado": [],
            "rejeitado": []
        }

        if novo_status not in transicoes.get(status_atual, []):

            flash(
                "Essa alteração de status não é permitida.",
                "danger"
            )

            return redirect(url_for(
                "orcamento.detalhes_orcamento",
                id_orcamento=id_orcamento
            ))

        cursor.execute("""
            UPDATE orcamento
            SET status_orcamento = %s
            WHERE id_orcamento = %s
        """, (novo_status, id_orcamento))

        cursor.execute("""
            INSERT INTO historico_orcamento (
                id_orcamento,
                acao,
                status_anterior,
                status_novo,
                observacao
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            id_orcamento,
            "Alteração de status",
            status_atual,
            novo_status,
            f"Status alterado de {status_atual} para {novo_status}."
        ))

        conexao.commit()

        flash("Status atualizado com sucesso!", "success")

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()

    return redirect(url_for(
        "orcamento.detalhes_orcamento",
        id_orcamento=id_orcamento
    ))
