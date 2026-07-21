import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether,
    HRFlowable, ListFlowable, ListItem, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Don't draw header/footer on cover page (page 1)
        if self._pageNumber > 1:
            # Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawString(54, A4[1] - 36, "VISUALIZADOR DE CIFRAS INTERATIVO — MANUAL DE INSTRUÇÕES")
            
            self.setFont("Helvetica", 8)
            self.drawRightString(A4[0] - 54, A4[1] - 36, "Versão 2.5")
            
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(54, A4[1] - 42, A4[0] - 54, A4[1] - 42)
            
            # Footer
            self.line(54, 45, A4[0] - 54, 45)
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(54, 32, "Plataforma Multi-instrumento (Cavaquinho, Violão e Teclado)")
            
            page_str = f"Página {self._pageNumber} de {page_count}"
            self.drawRightString(A4[0] - 54, 32, page_str)
            
        self.restoreState()

def create_manual():
    output_pdf = os.path.join(os.path.dirname(__file__), "..", "Manual_Visualizador_de_Cifras.pdf")
    output_pdf = os.path.abspath(output_pdf)
    
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0F172A")    # Deep Slate / Dark Navy
    c_secondary = colors.HexColor("#1E3A8A")  # Indigo
    c_accent = colors.HexColor("#D97706")     # Warm Gold / Amber
    c_text = colors.HexColor("#1E293B")       # Dark Grey
    c_bg_light = colors.HexColor("#F8FAFC")   # Light Slate Tint
    c_bg_card = colors.HexColor("#F1F5F9")    # Card Background
    
    # Custom Styles
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=c_primary,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    style_cover_subtitle = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=c_secondary,
        alignment=TA_CENTER,
        spaceAfter=25
    )
    
    style_h1 = ParagraphStyle(
        'Heading1Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_primary,
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )
    
    style_h2 = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    style_body = ParagraphStyle(
        'BodyCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=c_text,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )
    
    style_body_bold = ParagraphStyle(
        'BodyBoldCustom',
        parent=style_body,
        fontName='Helvetica-Bold'
    )
    
    style_bullet = ParagraphStyle(
        'BulletCustom',
        parent=style_body,
        alignment=TA_LEFT,
        spaceAfter=4
    )
    
    style_callout = ParagraphStyle(
        'CalloutText',
        parent=style_body,
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155")
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=c_text,
        alignment=TA_LEFT
    )

    story = []
    
    # ==========================================
    # COVER PAGE
    # ==========================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("VISUALIZADOR DE CIFRAS INTERATIVO", style_cover_title))
    story.append(Paragraph("Manual Completo de Instruções, Guia de Estudo e Referência Prática para Cavaquinho, Violão e Teclado", style_cover_subtitle))
    story.append(HRFlowable(width="100%", thickness=3, color=c_accent, spaceBefore=10, spaceAfter=25))
    
    cover_box_content = [
        Paragraph("<b>Sobre este Manual:</b> Este documento apresenta todos os recursos da plataforma de estudo musical e visualização dinâmica de cifras. Desenvolvido com foco no músico prático, arranjador e estudante, o aplicativo integra diagramas interativos em tempo real, transposição harmônica e navegação inteligente por acordes.", style_body),
        Spacer(1, 8),
        Paragraph("<b>Destaques da Versão 2.5:</b>", style_body_bold),
        ListFlowable([
            ListItem(Paragraph("<b>Duplo Painel de Acordes:</b> Visualização simultânea do <i>Acorde Atual</i> e do <i>Próximo Acorde</i> com trecho da letra para antecipação de digitação.", style_bullet), bulletColor=c_accent),
            ListItem(Paragraph("<b>Variação de Posições Independente:</b> Navegue por inversões, tríades e aberturas no braço separadamente para o acorde em execução e o seguinte.", style_bullet), bulletColor=c_accent),
            ListItem(Paragraph("<b>Suporte a 3 Instrumentos:</b> Alternância instantânea entre Cavaquinho, Violão e Teclado preservando o tom e o compasso da música.", style_bullet), bulletColor=c_accent),
            ListItem(Paragraph("<b>Acervo Expandido:</b> Catálogo pré-carregado com mais de 150 grandes sucessos de Noel Rosa, Ney Matogrosso, Tom Jobim, Cartola e muito mais.", style_bullet), bulletColor=c_accent)
        ], bulletType='bullet', start='square', leftIndent=15)
    ]
    
    cover_table = Table([[cover_box_content]], colWidths=[A4[0] - 108])
    cover_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_card),
        ('BOX', (0,0), (-1,-1), 1.5, c_secondary),
        ('PADDING', (0,0), (-1,-1), 16),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 40))
    
    info_data = [
        [Paragraph("<b>Plataforma:</b> Web HTML5 / JS Vanilla (Zero-Dependency)", style_table_cell),
         Paragraph("<b>Arquitetura:</b> 100% Offline-capable / Modular", style_table_cell)],
        [Paragraph("<b>Instrumentos Suportados:</b> Cavaquinho, Violão, Teclado", style_table_cell),
         Paragraph("<b>Automação:</b> Python Scraper & Catalog Generator", style_table_cell)],
        [Paragraph("<b>Licença do Projeto:</b> Uso Pessoal e Educacional", style_table_cell),
         Paragraph("<b>Data de Emissão:</b> Julho de 2026", style_table_cell)]
    ]
    info_table = Table(info_data, colWidths=[(A4[0] - 108)/2.0]*2)
    info_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(PageBreak())
    
    # ==========================================
    # SECTION 1: INTRODUÇÃO E VISÃO GERAL
    # ==========================================
    story.append(Paragraph("1. Introdução e Visão Geral", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=12))
    story.append(Paragraph(
        "O <b>Visualizador de Cifras</b> nasceu da necessidade de transformar a experiência de leitura de cifras no computador, tablet e celular. Diferente de sites tradicionais onde a cifra é apenas um texto estático que precisa ser rolado continuamente, nosso aplicativo transforma cada música em uma <b>interface visual interativa</b>.",
        style_body
    ))
    story.append(Paragraph(
        "Ao tocar uma música na plataforma, você tem acesso instantâneo ao desenho exato dos acordes no braço do seu instrumento favorito ou nas teclas do piano. Mais importante: a interface foi pensada para eliminar surpresas na hora das transições complexas, apresentando sempre o próximo acorde com antecedência.",
        style_body
    ))
    
    story.append(Paragraph("A Estrutura da Plataforma", style_h2))
    story.append(Paragraph("O sistema é composto pelos seguintes módulos principais:", style_body))
    
    mod_data = [
        [Paragraph("<b>Módulo / Página</b>", style_table_header), Paragraph("<b>Função Principal e Características</b>", style_table_header)],
        [Paragraph("<code>index.html</code><br/>(Hub Central)", style_table_cell), Paragraph("Página inicial que lista o acervo completo em ordem alfabética, exibindo títulos e compositores, com busca instantânea.", style_table_cell)],
        [Paragraph("<code>viewer-cavaquinho.html</code><br/>(Visualizador de Cavaquinho)", style_table_cell), Paragraph("Ambiente dedicado ao cavaquinho (afinação Ré-Sol-Si-Ré), com diagramas vetoriais SVG de alta precisão, numeração de casas e variação de tríades.", style_table_cell)],
        [Paragraph("<code>viewer-violao.html</code><br/>(Visualizador de Violão)", style_table_cell), Paragraph("Ambiente para violão de 6 cordas (afinação padrão), com representação de pestanas, cordas abertas e abafadas e posições ergonômicas.", style_table_cell)],
        [Paragraph("<code>viewer-piano.html</code><br/>(Visualizador de Teclado)", style_table_cell), Paragraph("Teclado virtual interativo de 2 oitavas que ilumina as notas de cada acorde e destaca a nota fundamental (Root) em cor diferenciada.", style_table_cell)],
        [Paragraph("<code>tools/gerar_musica.py</code><br/>(Automação CLI)", style_table_cell), Paragraph("Ferramenta de linha de comando em Python que importa cifras automaticamente de sites como Cifra Club, extrai acordes e atualiza o catálogo.", style_table_cell)]
    ]
    mod_table = Table(mod_data, colWidths=[140, A4[0] - 108 - 140])
    mod_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light])
    ]))
    story.append(mod_table)
    story.append(Spacer(1, 14))
    
    # ==========================================
    # SECTION 2: COMO USAR OS INSTRUMENTOS
    # ==========================================
    story.append(Paragraph("2. Conhecendo os Instrumentos e Diagramas", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=12))
    story.append(Paragraph(
        "Cada visualizador foi projetado respeitando as especificidades de dedilhado e afinação do respectivo instrumento, garantindo que as notas geradas estejam sempre em conformidade com a harmonia correta da música.",
        style_body
    ))
    
    story.append(Paragraph("2.1. Cavaquinho (Ré - Sol - Si - Ré)", style_h2))
    story.append(Paragraph(
        "O visualizador de cavaquinho desenha os 4 tramos verticais representando as cordas (da 4ª corda mais grave à esquerda para a 1ª corda mais aguda à direita). Os pontos circulares indicam onde pressionar os dedos:",
        style_body
    ))
    story.append(ListFlowable([
        ListItem(Paragraph("<b>Bolinhas Coloridas:</b> Indicam a casa e a corda exata onde o dedo deve ser posicionado.", style_bullet), bulletColor=c_accent),
        ListItem(Paragraph("<b>Indicador de Casa (`Nª casa`):</b> Quando um acorde é montado em regiões mais altas do braço (ex: na 5ª casa), o número da casa inicial é exibido na lateral do diagrama.", style_bullet), bulletColor=c_accent),
        ListItem(Paragraph("<b>Cordas Soltas (`O`) e Abafadas (`X`):</b> No topo do diagrama, círculos abertos (`O`) indicam cordas que devem soar livres, enquanto um `X` indica cordas que não devem ser tocadas.", style_bullet), bulletColor=c_accent)
    ], bulletType='bullet', start='circle', leftIndent=15))
    story.append(Spacer(1, 6))

    story.append(Paragraph("2.2. Violão de 6 Cordas (Mi - Lá - Ré - Sol - Si - Mi)", style_h2))
    story.append(Paragraph(
        "No violão, o diagrama exibe as 6 cordas verticais e os tramos do braço. O diferencial do módulo de violão é o suporte a <b>pestanas dinâmicas</b>:",
        style_body
    ))
    story.append(ListFlowable([
        ListItem(Paragraph("<b>Barra de Pestana:</b> Uma barra horizontal grossa unindo várias cordas indica quando o dedo indicador deve pressionar todas (ou parte) das cordas na mesma casa.", style_bullet), bulletColor=c_secondary),
        ListItem(Paragraph("<b>Aberturas Clássicas e Modernas:</b> O dicionário de violão contempla tanto as posições tradicionais com cordas soltas quanto inversões sofisticadas usadas na Bossa Nova e Jazz.", style_bullet), bulletColor=c_secondary)
    ], bulletType='bullet', start='circle', leftIndent=15))
    story.append(Spacer(1, 6))

    story.append(Paragraph("2.3. Teclado e Piano Virtual", style_h2))
    story.append(Paragraph(
        "Para os tecladistas, o app apresenta um teclado de duas oitavas com as teclas brancas e pretas (acidentes). Ao selecionar um acorde:",
        style_body
    ))
    story.append(ListFlowable([
        ListItem(Paragraph("<b>Destaque da Fundamental (Root):</b> A nota tônica do acorde (por exemplo, o Dó num acorde de C7M) é iluminada em uma cor de destaque especial (ouro/âmbar), facilitando a identificação da base do acorde.", style_bullet), bulletColor=c_primary),
        ListItem(Paragraph("<b>Tríades e Tétrades:</b> Todas as notas que compõem o acorde (3ª, 5ª, 7ª, 9ª, etc.) são iluminadas simultaneamente no teclado em tom azul/turquesa vibrante.", style_bullet), bulletColor=c_primary)
    ], bulletType='bullet', start='circle', leftIndent=15))
    story.append(Spacer(1, 14))

    # ==========================================
    # SECTION 3: RECURSOS AVANÇADOS DO PAINEL
    # ==========================================
    story.append(PageBreak())
    story.append(Paragraph("3. Recursos Interativos e Painel de Controle", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=12))
    story.append(Paragraph(
        "O painel lateral (ou topo flutuante em dispositivos móveis) é o coração da experiência prática da plataforma. Ele foi projetado para dar controle total ao músico durante o estudo ou execução na roda de música.",
        style_body
    ))

    # Callout box for Double View
    callout_box = [
        [Paragraph("<b>💡 INOVAÇÃO: DUPLO DIAGRAMA (ACORDE ATUAL + PRÓXIMO ACORDE)</b><br/>"
                   "Um dos maiores desafios ao tocar uma música nova é preparar os dedos para a próxima troca de acorde. Nosso visualizador exibe <b>dois cards simultâneos</b>: o card superior mostra o acorde exato que está sendo tocado agora. O card inferior exibe antecipadamente o <b>próximo acorde</b> da música junto com o trecho da letra correspondente, permitindo um planejamento mental e visual perfeito da digitação!", style_callout)]
    ]
    t_callout = Table(callout_box, colWidths=[A4[0] - 108])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF3C7")), # Light yellow/amber
        ('BOX', (0,0), (-1,-1), 1, c_accent),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_callout)
    story.append(Spacer(1, 12))

    story.append(Paragraph("3.1. Navegação Sincronizada pela Letra", style_h2))
    story.append(Paragraph(
        "A letra da música é exibida na tela principal com os acordes perfeitamente posicionados acima das sílabas correspondentes. Todos os acordes são elementos interativos:",
        style_body
    ))
    story.append(ListFlowable([
        ListItem(Paragraph("<b>Clique em qualquer acorde:</b> Ao clicar ou tocar em um acorde na letra, o painel lateral é imediatamente atualizado para exibir aquele acorde como o <i>Acorde Atual</i>.", style_bullet), bulletColor=c_secondary),
        ListItem(Paragraph("<b>Destaque na Frase:</b> O acorde selecionado recebe um destaque luminoso dourado (`#fbbf24`) na própria letra, e a linha inteira de letra correspondente aparece reproduzida no topo do painel lateral.", style_bullet), bulletColor=c_secondary),
        ListItem(Paragraph("<b>Sequência de Transição (`→`):</b> Se houver vários acordes na mesma linha de letra, o visualizador exibe uma barra de sequência logo acima do diagrama, indicando o caminho harmônico do compasso.", style_bullet), bulletColor=c_secondary)
    ], bulletType='bullet', start='square', leftIndent=15))
    story.append(Spacer(1, 8))

    story.append(Paragraph("3.2. Botão de Variação de Posição (`🔄 Variar Posição`)", style_h2))
    story.append(Paragraph(
        "Um mesmo acorde pode ser montado de dezenas de formas diferentes no braço do instrumento — seja na região mais grave (aberto), no meio do braço ou com inversões agudas. Para dar máxima flexibilidade de arranjo, implementamos o controle de posições alternativas:",
        style_body
    ))
    story.append(Paragraph(
        "Sempre que o acorde selecionado possuir alternativas mapeadas, um botão **`🔄 Variar Posição`** aparecerá automaticamente abaixo do diagrama junto com um badge indicador de contagem (`1/3`, `2/3`, `3/3`).",
        style_body
    ))
    
    # Table illustrating independent position controls
    pos_data = [
        [Paragraph("<b>Controle no Card Superior<br/>(Acorde Atual)</b>", style_table_header),
         Paragraph("<b>Controle no Card Inferior<br/>(Próximo Acorde)</b>", style_table_header)],
        [Paragraph("O botão de variação superior altera exclusivamente o desenho do acorde que você está tocando no momento. Permite testar se uma digitação na 5ª casa soa melhor para o trecho atual.", style_table_cell),
         Paragraph("O botão de variação inferior altera <b>exclusivamente</b> o desenho do próximo acorde! Com isso, você pode escolher a inversão do próximo acorde que fique fisicamente mais próxima dos seus dedos.", style_table_cell)]
    ]
    t_pos = Table(pos_data, colWidths=[(A4[0] - 108)/2.0]*2)
    t_pos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [c_bg_light])
    ]))
    story.append(t_pos)
    story.append(Spacer(1, 10))

    story.append(Paragraph("3.3. Transposição de Tom em Tempo Real (`- Tom +`)", style_h2))
    story.append(Paragraph(
        "Precisa adequar a música ao alcance vocal do cantor ou facilitar a digitação eliminando pestanas? Utilize os controles de transposição (`-` e `+`) situados na barra superior da tela.",
        style_body
    ))
    story.append(Paragraph(
        "Ao clicar em `+` (aumentar meio tom) ou `-` (diminuir meio tom), o sistema recalcula matematicamente **todos os acordes** da música simultaneamente — preservando extensões complexas como `m7(b5)`, `/F#` ou `(9+)`. Os diagramas visuais do cavaquinho, violão ou teclado são redesenhados instantaneamente no novo tom escolhido!",
        style_body
    ))
    story.append(Spacer(1, 14))

    # ==========================================
    # SECTION 4: COMO ADICIONAR MÚSICAS (CLI)
    # ==========================================
    story.append(KeepTogether([
        Paragraph("4. Guia de Automação e Expansão do Catálogo", style_h1),
        HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=12),
        Paragraph(
            "A plataforma foi construída com um ecossistema aberto que permite adicionar infinitas músicas de forma automatizada sem precisar digitar notas manualmente ou criar arquivos HTML individuais.",
            style_body
        ),
        Paragraph("4.1. Importando Músicas com `gerar_musica.py`", style_h2),
        Paragraph(
            "No diretório `tools/` do projeto, reside o script Python `gerar_musica.py`. Ele é capaz de ler qualquer URL de cifra (por exemplo, do portal Cifra Club), extrair a letra, limpar anotações desnecessárias, identificar todos os acordes, calcular as notas componentes e salvar tudo automaticamente no acervo.",
            style_body
        ),
        Paragraph("<b>Sintaxe de Uso no Terminal:</b>", style_body_bold),
        Table([
            [Paragraph("<code>python tools/gerar_musica.py \"https://www.cifraclub.com.br/artista/nome-da-musica/#tabs=false\"</code>", style_table_cell)]
        ], colWidths=[A4[0] - 108], style=[
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E2E8F0")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94A3B8")),
            ('PADDING', (0,0), (-1,-1), 10)
        ]),
        Spacer(1, 8),
        Paragraph("<b>O que o comando faz automaticamente:</b>", style_body_bold),
        ListFlowable([
            ListItem(Paragraph("Faz o download limpo do HTML ou markdown da música.", style_bullet), bulletColor=c_accent),
            ListItem(Paragraph("Envolve cada acorde detectado em tags interativas <code>&lt;span class=\"chord\" data-chord=\"...\"&gt;</code>.", style_bullet), bulletColor=c_accent),
            ListItem(Paragraph("Calcula as notas musicais e intervalos de cada acorde através do analisador harmônico `chord_parser.py`.", style_bullet), bulletColor=c_accent),
            ListItem(Paragraph("Gera os arquivos <code>data/songs/NomeDaMusica.json</code> e <code>.js</code>.", style_bullet), bulletColor=c_accent),
            ListItem(Paragraph("Atualiza o índice principal (<code>index.html</code>) em ordem alfabética e reconstrói o catálogo unificado (<code>catalog.json</code> e <code>catalog.js</code>).", style_bullet), bulletColor=c_accent)
        ], bulletType='bullet', start='circle', leftIndent=15)
    ]))
    story.append(Spacer(1, 14))

    # ==========================================
    # SECTION 5: DICAS PRÁTICAS E ATALHOS
    # ==========================================
    story.append(KeepTogether([
        Paragraph("5. Dicas Práticas para o Dia a Dia Musical", style_h1),
        HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=12),
        Paragraph("<b>• Modo Palco / Estúdio:</b> Se você estiver tocando ao vivo com um celular ou tablet em um estante de partitura e quiser focar apenas na letra e nos acordes em texto, clique no botão <b><code>👁️ Ocultar / Mostrar Diagrama</code></b> na barra superior. Isso recolhe o painel de braço e expande a letra para 100% da largura da tela.", style_body),
        Spacer(1, 4),
        Paragraph("<b>• Estudo de Tríades e Inversões no Cavaquinho:</b> Ao estudar sambas de raiz e choros (como os de Noel Rosa ou Cartola), experimente tocar a música inteira utilizando o botão <b><code>🔄 Variar Posição</code></b> para escolher apenas digitações a partir da 5ª casa. Isso desenvolve o domínio de todo o braço do instrumento e enriquece a sonoridade da roda!", style_body),
        Spacer(1, 4),
        Paragraph("<b>• Alternando entre Violão e Cavaquinho na mesma roda:</b> Os três links no cabeçalho (<code>🪕 Cavaquinho</code>, <code>🎸 Violão</code>, <code>🎹 Piano</code>) preservam o parâmetro da música na URL. Se um violonista e um cavaquinista estiverem estudando juntos, basta abrir a mesma música e alternar a visualização para conferir a harmonia em ambos os instrumentos perfeitamente sincronizados.", style_body),
        Spacer(1, 25),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceBefore=10, spaceAfter=15),
        Paragraph("<b>Projeto Visualizador de Cifras Interativo — Desenvolvido com carinho para a comunidade musical brasileira.</b><br/>Acervo de Músicas, Módulos JS Vetoriais e Scrapers Python sob licença aberta de uso pessoal.", style_callout)
    ]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Manual em PDF gerado com sucesso em: {output_pdf}")

if __name__ == "__main__":
    create_manual()
