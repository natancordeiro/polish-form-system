"""
Gerador de PDF via INJEÇÃO DE TEXTO no template oficial polonês.

Fluxo:
  1. Abre o template `official_form.pdf` (11 páginas).
  2. Detecta as fileiras de caixinhas de cada página (uma vez, cacheado).
  3. Para cada campo do FormData, escreve nas caixinhas ou em áreas de
     texto livre, usando os handlers de `template_filler`.
  4. Devolve os bytes do PDF final.

O resultado fica visualmente idêntico ao modelo preenchido à mão
(Luiz_Ricardo.pdf), pois apenas escreve por cima do template — sem
recriar o layout.
"""
from __future__ import annotations

import logging
from pathlib import Path

import fitz

from app.schemas import FormData, DadosPessoais, DadosProgenitor, Endereco
from app.services import field_mapper as fm
from app.services.translator import translator
from app.services.box_detector import detect_all_rows, BoxRow
from app.services.template_filler import (
    ensure_fonts,
    write_char_boxes, write_date_boxes, write_two_field_row,
    write_text_on_line, write_text_block, draw_checkbox_cross,
)

logger = logging.getLogger(__name__)

TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "official_form.pdf"


# ---------------------------------------------------------------------------
# Helpers de valor
# ---------------------------------------------------------------------------

def _pais_voivodia(e: Endereco) -> str:
    pais = fm.traduzir_pais(e.pais)
    estado = (e.estado or "").upper().strip()
    return f"{pais} / {estado}" if estado else pais


def _local_format(pais: str, cidade: str) -> str:
    """Formato 'PAÍS / CIDADE' usado em vários campos."""
    pais_pl = fm.traduzir_pais(pais) if pais else ""
    return f"{pais_pl} / {(cidade or '').upper()}"


def _full_name(nome: str, sobrenome: str) -> str:
    nome = (nome or "").upper().strip()
    sobrenome = (sobrenome or "").upper().strip()
    return f"{nome} {sobrenome}".strip()


def _data_pl(d) -> str:
    return d.isoformat() if d else ""


# ---------------------------------------------------------------------------
# PÁGINA 1 — Cabeçalho, requerente, endereço, tipo
# ---------------------------------------------------------------------------

def _fill_page_1(page: fitz.Page, rows: list[BoxRow], data: FormData) -> None:
    ensure_fonts(page)

    # Cabeçalho — local + data
    write_char_boxes(page, data.local_submissao, rows[0])
    write_date_boxes(page, _data_pl(data.data_submissao), rows[1])

    # WOJEWODA (texto livre sobre linha pontilhada, à direita da palavra)
    write_text_on_line(page, data.wojewoda,
                       x=345, y=296, max_width=195,
                       font_size=11, bold=True)

    # Nome do requerente — pode ocupar 2 fileiras
    nome = (data.requerente_nome_completo or "").upper()
    write_char_boxes(page, nome[:20], rows[2])
    if len(nome) > 20:
        write_char_boxes(page, nome[20:40], rows[3])

    # Endereço
    e = data.requerente_endereco
    write_char_boxes(page, _pais_voivodia(e), rows[4])
    write_char_boxes(page, e.cidade, rows[5])
    write_char_boxes(page, f"UL. {e.rua}" if e.rua else "", rows[6])
    write_two_field_row(page, rows[7],
                        text_left=e.numero_casa,
                        text_right=e.numero_apartamento)
    _write_cep_row(page, rows[8], e.cep or "", e.cidade or "")
    write_char_boxes(page, e.telefone, rows[9])

    # Checkbox tipo de decisão + nome sobre linha pontilhada
    # Régua visual: checkbox centro em x=112, linha pontilhada (posiadanie) x=385-510
    if data.tipo_decisao == "posiadanie":
        draw_checkbox_cross(page, x=112, y=619, size=8)
        write_text_on_line(page, data.nome_titular_confirmacao,
                           x=382, y=623, max_width=145, font_size=9, bold=True)
    else:
        draw_checkbox_cross(page, x=112, y=644, size=8)
        write_text_on_line(page, data.nome_titular_confirmacao,
                           x=358, y=649, max_width=170, font_size=9, bold=True)

    # Info adicional (texto livre — 3 linhas pontilhadas, ~y=702..735)
    info_pl = translator.translate(data.info_adicional_pedido)
    write_text_block(page, info_pl,
                     x=70, y=712, max_width=470,
                     line_height=12, max_lines=4, font_size=9)


def _write_cep_row(page: fitz.Page, row: BoxRow, cep: str, cidade: str) -> None:
    """Escreve 'XX-XXX' (pulando a caixa do hífen) + cidade após o gap."""
    cep_digits = (cep or "").replace("-", "")

    for i, digit in enumerate(cep_digits[:5]):
        idx = i if i < 2 else i + 1
        if idx < row.n:
            box = row.boxes[idx]
            from app.services.template_filler import _measure, FONT_REGULAR_PATH, FONT_REGULAR, CHAR_FONT_SIZE
            w = _measure(digit, FONT_REGULAR_PATH, CHAR_FONT_SIZE)
            page.insert_text((box.cx - w / 2, box.y1 - 1.5), digit,
                             fontname=FONT_REGULAR, fontsize=CHAR_FONT_SIZE, color=(0, 0, 0))

    split_idx = row.n
    for i in range(1, row.n):
        if row.boxes[i].x0 - row.boxes[i - 1].x1 > 25:
            split_idx = i
            break
    write_char_boxes(page, cidade, row, start_index=split_idx)


# ---------------------------------------------------------------------------
# PÁGINA 2 — Procuração + CZĘŚĆ I A. Dados solicitante + B.
# ---------------------------------------------------------------------------

def _fill_page_2(page: fitz.Page, rows: list[BoxRow], data: FormData) -> None:
    ensure_fonts(page)

    # Justificativa de procuração (texto livre no topo da página, y≈115-260)
    if data.justificativa_procuracao:
        proc_pl = translator.translate(data.justificativa_procuracao)
        write_text_block(page, proc_pl,
                         x=70, y=140, max_width=460,
                         line_height=12, max_lines=10, font_size=9)
    else:
        write_text_block(page, "NIE DOTYCZY.",
                         x=70, y=140, max_width=460,
                         line_height=12, max_lines=1, font_size=9)

    # CZĘŚĆ I — A. Dados do solicitante
    # Fileiras reais detectadas na pág 2 (15 fileiras):
    #   [0] y=312 Nazwisko linha 1
    #   [1] y=329 Nazwisko linha 2
    #   [2] y=344 Nazwisko rodowe
    #   [3] y=360 Imię (imiona)
    #   [4] y=377 Imię i nazwisko ojca
    #   [5] y=393 Imię i nazwisko rodowe matki
    #   [6] y=417 Używane nazwiska linha 1
    #   [7] y=432 Używane nazwiska linha 2 (para data de mudança)
    #   [8] y=448 (n=11) Data urodzenia + Płeć
    #   [9] y=472 Miejsce urodzenia (państwo/miejscowość)
    #   [10] y=496 Posiadane obce obywatelstwa linha 1
    #   [11] y=513 Posiadane obce obywatelstwa linha 2
    #   [12] y=529 Posiadane obce obywatelstwa linha 3
    #   [13] y=545 Stan cywilny
    #   [14] y=561 (n=11) PESEL
    s = data.solicitante
    write_char_boxes(page, s.sobrenome, rows[0])
    write_char_boxes(page, s.sobrenome_solteiro or s.sobrenome, rows[2])
    write_char_boxes(page, s.nome, rows[3])
    write_char_boxes(page, _full_name(s.nome_pai, s.sobrenome_pai), rows[4])
    write_char_boxes(page, _full_name(s.nome_mae, s.sobrenome_solteiro_mae), rows[5])
    write_char_boxes(page, s.nomes_usados or "NIE DOTYCZY", rows[6])
    if s.data_mudanca_nome:
        write_date_boxes(page, _data_pl(s.data_mudanca_nome), rows[7])

    # Data de nascimento + sexo na mesma fileira (rows[8], n=11)
    _write_data_plus_sexo(page, rows[8], _data_pl(s.data_nascimento), fm.traduzir_sexo(s.sexo))

    # Miejsce urodzenia
    write_char_boxes(page, _local_format(s.pais_nascimento, s.cidade_nascimento), rows[9])

    # Cidadania: nome em linha 1, data na linha 2 (linha 3 normalmente vazia)
    write_char_boxes(page, translator.translate(s.cidadania) if s.cidadania else "", rows[10])
    write_char_boxes(page, translator.translate(s.data_aquisicao_cidadania) if s.data_aquisicao_cidadania else "", rows[11])

    # Stan cywilny
    write_char_boxes(page, fm.traduzir_estado_civil(s.estado_civil, s.sexo), rows[13])

    # PESEL
    if s.pesel:
        write_char_boxes(page, s.pesel, rows[14])

    # B. Decisão anterior — texto livre (~y=720-790)
    secao_b = (translator.translate(data.detalhes_decisao_anterior)
               if (data.houve_decisao_anterior and data.detalhes_decisao_anterior)
               else "NIE.")
    write_text_block(page, secao_b,
                     x=70, y=720, max_width=460,
                     line_height=12, max_lines=4, font_size=9)


def _write_data_plus_sexo(page: fitz.Page, row: BoxRow, iso_date: str, sexo: str) -> None:
    """Linha de data (8 dígitos nas 10 caixas) + caixa de sexo no fim."""
    if iso_date:
        write_date_boxes(page, iso_date, row)
    if sexo and row.n >= 11:
        # A última caixa fica isolada (depois do label "8. Płeć")
        box = row.boxes[-1]
        from app.services.template_filler import _measure, FONT_REGULAR_PATH, FONT_REGULAR, CHAR_FONT_SIZE
        w = _measure(sexo, FONT_REGULAR_PATH, CHAR_FONT_SIZE)
        page.insert_text((box.cx - w / 2, box.y1 - 1.5), sexo,
                         fontname=FONT_REGULAR, fontsize=CHAR_FONT_SIZE, color=(0, 0, 0))


# ---------------------------------------------------------------------------
# PÁGINA 3 — Seções C, D + Mãe + início do Pai
# ---------------------------------------------------------------------------

def _fill_page_3(page: fitz.Page, rows: list[BoxRow], data: FormData) -> None:
    ensure_fonts(page)

    # C. (texto livre ~y=190-300)
    secao_c = (translator.translate(data.detalhes_mudanca_cidadania)
               if (data.houve_mudanca_cidadania and data.detalhes_mudanca_cidadania)
               else "NIE.")
    write_text_block(page, secao_c,
                     x=70, y=200, max_width=460,
                     line_height=12, max_lines=5, font_size=9)

    # D. Endereços de vida (texto livre ~y=320-380)
    enderecos_pl = translator.translate(data.enderecos_vida)
    write_text_block(page, enderecos_pl,
                     x=70, y=315, max_width=460,
                     line_height=12, max_lines=3, font_size=9)

    # E.I. Dados da mãe — começa em rows[0..]
    # Layout esperado das ~19 fileiras detectadas:
    #   [0] Nazwisko (linha 1)
    #   [1] Nazwisko (linha 2)
    #   [2] Nazwisko rodowe
    #   [3] Imię (imiona)
    #   [4] Imię i nazwisko ojca
    #   [5] Imię i nazwisko rodowe matki
    #   [6] Używane nazwiska linha 1
    #   [7] Używane nazwiska linha 2 (data)
    #   [8] Data urodzenia (n=10)
    #   [9] Miejsce urodzenia
    #   [10] Stan cywilny
    #   [11] Data zawarcia związku małżeńskiego (n=10)
    #   [12] Miejsce zawarcia związku małżeńskiego
    #   [13] Obywatelstwa — linha 1
    #   [14] Obywatelstwa — linha 2
    #   [15] PESEL
    #   [16] Pai - Nazwisko linha 1
    #   [17] Pai - Nazwisko linha 2
    #   [18] Pai - Nazwisko rodowe
    m = data.mae
    write_char_boxes(page, m.sobrenome, rows[0])
    write_char_boxes(page, m.sobrenome_solteiro or m.sobrenome, rows[2])
    write_char_boxes(page, m.nome, rows[3])
    write_char_boxes(page, _full_name(m.nome_pai, m.sobrenome_pai), rows[4])
    write_char_boxes(page, _full_name(m.nome_mae, m.sobrenome_solteiro_mae), rows[5])
    if m.nomes_usados:
        write_char_boxes(page, m.nomes_usados, rows[6])
    if m.data_mudanca_nome:
        # data combinada na linha "usados" (mesma estrutura do solicitante)
        write_date_boxes(page, _data_pl(m.data_mudanca_nome), rows[7])

    if m.data_nascimento and not m.data_nascimento_desconhecida:
        write_date_boxes(page, _data_pl(m.data_nascimento), rows[8])
    write_char_boxes(page, _local_format(m.pais_nascimento, m.cidade_nascimento), rows[9])
    write_char_boxes(page, fm.traduzir_estado_civil(m.estado_civil, m.sexo), rows[10])
    if m.data_casamento:
        write_date_boxes(page, _data_pl(m.data_casamento), rows[11])
    write_char_boxes(page, _local_format(m.pais_casamento, m.cidade_casamento), rows[12])
    write_char_boxes(page, translator.translate(m.cidadania) if m.cidadania else "", rows[13])
    write_char_boxes(page, translator.translate(m.data_aquisicao_cidadania) if m.data_aquisicao_cidadania else "", rows[14])
    if m.pesel:
        write_char_boxes(page, m.pesel, rows[15])

    # E.II. Pai — só os dois primeiros (Nazwisko + Nazwisko rodowe)
    p = data.pai
    if len(rows) > 16:
        write_char_boxes(page, p.sobrenome, rows[16])
        write_char_boxes(page, p.sobrenome_solteiro or p.sobrenome, rows[18])


# ---------------------------------------------------------------------------
# PÁGINA 4 — Continuação Pai + F.I. Avô materno + F.II. Avó materna (parcial)
# ---------------------------------------------------------------------------

def _fill_page_4(page: fitz.Page, rows: list[BoxRow], data: FormData) -> None:
    ensure_fonts(page)
    p = data.pai

    # Continuação dos dados do pai
    # Layout esperado das ~27 fileiras:
    #   [0] Imię (imiona)
    #   [1] Imię i nazwisko ojca
    #   [2] Imię i nazwisko rodowe matki
    #   [3] Używane nazwiska linha 1
    #   [4] Używane nazwiska linha 2 (data)
    #   [5] Data urodzenia (n=10)
    #   [6] Miejsce urodzenia
    #   [7] Stan cywilny (n=11)
    #   [8] Data zawarcia związku (n=10)
    #   [9] Miejsce zawarcia
    #   [10] Obywatelstwa - linha 1
    #   [11] Obywatelstwa - linha 2
    #   [12] PESEL pai (n=11)
    #   [13..] Avô materno (Nazwisko, Nazwisko rodowe, Imię, Imię ojca, Imię matki, Data, Miejsce, PESEL)
    write_char_boxes(page, p.nome, rows[0])
    write_char_boxes(page, _full_name(p.nome_pai, p.sobrenome_pai), rows[1])
    write_char_boxes(page, _full_name(p.nome_mae, p.sobrenome_solteiro_mae), rows[2])
    if p.nomes_usados:
        write_char_boxes(page, p.nomes_usados, rows[3])
    if p.data_mudanca_nome:
        write_date_boxes(page, _data_pl(p.data_mudanca_nome), rows[4])
    if p.data_nascimento and not p.data_nascimento_desconhecida:
        write_date_boxes(page, _data_pl(p.data_nascimento), rows[5])
    write_char_boxes(page, _local_format(p.pais_nascimento, p.cidade_nascimento), rows[6])
    write_char_boxes(page, fm.traduzir_estado_civil(p.estado_civil, p.sexo), rows[7])
    if p.data_casamento:
        write_date_boxes(page, _data_pl(p.data_casamento), rows[8])
    write_char_boxes(page, _local_format(p.pais_casamento, p.cidade_casamento), rows[9])
    write_char_boxes(page, translator.translate(p.cidadania) if p.cidadania else "", rows[10])
    write_char_boxes(page, translator.translate(p.data_aquisicao_cidadania) if p.data_aquisicao_cidadania else "", rows[11])
    if p.pesel:
        write_char_boxes(page, p.pesel, rows[12])

    # F.I. Avô materno — começa em rows[13]
    a = data.avo_materno
    base = 13
    if len(rows) > base + 7:
        write_char_boxes(page, a.sobrenome, rows[base])
        # Próxima fileira = nazwisko 2ª linha (skip)
        write_char_boxes(page, a.sobrenome_solteiro or a.sobrenome, rows[base + 2])
        write_char_boxes(page, a.nome, rows[base + 3])
        write_char_boxes(page, _full_name(a.nome_pai, a.sobrenome_pai), rows[base + 4])
        write_char_boxes(page, _full_name(a.nome_mae, a.sobrenome_solteiro_mae), rows[base + 5])
        # Data: se desconhecida, não escreve (template já tem "NIEZNANE" implícito? Não — escrevemos sobre)
        if a.data_nascimento and not a.data_nascimento_desconhecida:
            write_date_boxes(page, _data_pl(a.data_nascimento), rows[base + 6])
        write_char_boxes(page, _local_format(a.pais_nascimento, a.cidade_nascimento), rows[base + 7])
        if a.pesel and len(rows) > base + 8:
            write_char_boxes(page, a.pesel, rows[base + 8])

    # F.II. Avó materna — Nazwisko + Nazwisko rodowe + Imię + Imię ojca
    av = data.avo_materna
    base2 = 22
    if len(rows) > base2 + 4:
        write_char_boxes(page, av.sobrenome, rows[base2])
        write_char_boxes(page, av.sobrenome_solteiro or av.sobrenome, rows[base2 + 2])
        write_char_boxes(page, av.nome, rows[base2 + 3])
        write_char_boxes(page, _full_name(av.nome_pai, av.sobrenome_pai), rows[base2 + 4])


# ---------------------------------------------------------------------------
# PÁGINA 5 — Avó materna (resto) + Avô paterno + Avó paterna
# ---------------------------------------------------------------------------

def _fill_page_5(page: fitz.Page, rows: list[BoxRow], data: FormData) -> None:
    ensure_fonts(page)

    # Continuação avó materna: Imię matki, Data, Miejsce, PESEL
    av = data.avo_materna
    # rows[0] = nazwisko rodowe matki, [1] = Data, [2] = Miejsce, [3] = PESEL
    write_char_boxes(page, _full_name(av.nome_mae, av.sobrenome_solteiro_mae), rows[0])
    if av.data_nascimento and not av.data_nascimento_desconhecida:
        write_date_boxes(page, _data_pl(av.data_nascimento), rows[1])
    write_char_boxes(page, _local_format(av.pais_nascimento, av.cidade_nascimento), rows[2])
    if av.pesel:
        write_char_boxes(page, av.pesel, rows[3])

    # F.III. Avô paterno (~rows[4..11])
    ap = data.avo_paterno
    base = 4
    if len(rows) > base + 7:
        write_char_boxes(page, ap.sobrenome, rows[base])
        write_char_boxes(page, ap.sobrenome_solteiro or ap.sobrenome, rows[base + 2])
        write_char_boxes(page, ap.nome, rows[base + 3])
        write_char_boxes(page, _full_name(ap.nome_pai, ap.sobrenome_pai), rows[base + 4])
        write_char_boxes(page, _full_name(ap.nome_mae, ap.sobrenome_solteiro_mae), rows[base + 5])
        if ap.data_nascimento and not ap.data_nascimento_desconhecida:
            write_date_boxes(page, _data_pl(ap.data_nascimento), rows[base + 6])
        write_char_boxes(page, _local_format(ap.pais_nascimento, ap.cidade_nascimento), rows[base + 7])
        if ap.pesel and len(rows) > base + 8:
            write_char_boxes(page, ap.pesel, rows[base + 8])

    # F.IV. Avó paterna (~rows[13..20])
    apt = data.avo_paterna
    base2 = 13
    if len(rows) > base2 + 7:
        write_char_boxes(page, apt.sobrenome, rows[base2])
        write_char_boxes(page, apt.sobrenome_solteiro or apt.sobrenome, rows[base2 + 2])
        write_char_boxes(page, apt.nome, rows[base2 + 3])
        write_char_boxes(page, _full_name(apt.nome_pai, apt.sobrenome_pai), rows[base2 + 4])
        write_char_boxes(page, _full_name(apt.nome_mae, apt.sobrenome_solteiro_mae), rows[base2 + 5])
        if apt.data_nascimento and not apt.data_nascimento_desconhecida:
            write_date_boxes(page, _data_pl(apt.data_nascimento), rows[base2 + 6])
        write_char_boxes(page, _local_format(apt.pais_nascimento, apt.cidade_nascimento), rows[base2 + 7])
        if apt.pesel and len(rows) > base2 + 8:
            write_char_boxes(page, apt.pesel, rows[base2 + 8])


# ---------------------------------------------------------------------------
# PÁGINA 6 — CZĘŚĆ II A. Biografia solicitante + B. Escolha cidadania
# ---------------------------------------------------------------------------

CHECKBOX_TAK_X = 148
CHECKBOX_NIE_X = 202
CHECKBOX_NIE_WIEM_X = 248
CHECKBOX_NIE_DOTYCZY_X = 312
CHECKBOX_Y = 506


def _fill_page_6(page: fitz.Page, rows: list[BoxRow], data: FormData) -> None:
    ensure_fonts(page)

    # A. Biografia (texto livre grande, ~y=200..440)
    bio_pl = translator.translate(data.biografia_solicitante)
    write_text_block(page, bio_pl,
                     x=70, y=200, max_width=460,
                     line_height=12, max_lines=20, font_size=9)

    # B. Checkbox da escolha de cidadania estrangeira
    choice_map = {
        "TAK": CHECKBOX_TAK_X,
        "NIE": CHECKBOX_NIE_X,
        "NIE_WIEM": CHECKBOX_NIE_WIEM_X,
        "NIE_DOTYCZY": CHECKBOX_NIE_DOTYCZY_X,
    }
    cx = choice_map.get(data.escolheu_cidadania_estrangeira, CHECKBOX_NIE_X)
    draw_checkbox_cross(page, x=cx, y=CHECKBOX_Y, size=8)

    # Nazwa organu (texto livre, ~y=531)
    if data.orgao_escolha_cidadania:
        organ_pl = translator.translate(data.orgao_escolha_cidadania)
        write_text_on_line(page, organ_pl, x=130, y=534, max_width=410, font_size=9)


# ---------------------------------------------------------------------------
# PÁGINA 7 — CZĘŚĆ III A.I. Biografia mãe + A.II. pai + B.I. avô materno
# ---------------------------------------------------------------------------

def _fill_page_7(page: fitz.Page, rows: list[BoxRow], data: FormData) -> None:
    ensure_fonts(page)

    # A.I. Biografia mãe (~y=200..340)
    bio_mae = (translator.translate(data.biografia_mae)
               if data.biografia_mae else "NIE DOTYCZY.")
    write_text_block(page, bio_mae,
                     x=70, y=200, max_width=460,
                     line_height=12, max_lines=11, font_size=9)

    # A.II. Biografia pai (~y=420..585)
    bio_pai = (translator.translate(data.biografia_pai)
               if data.biografia_pai else "NIE DOTYCZY.")
    write_text_block(page, bio_pai,
                     x=70, y=425, max_width=460,
                     line_height=12, max_lines=13, font_size=9)

    # B.I. Biografia avô materno (~y=685..755)
    bio_avo_m = (translator.translate(data.biografia_avo_materno)
                 if data.biografia_avo_materno else "NIE DOTYCZY.")
    write_text_block(page, bio_avo_m,
                     x=70, y=688, max_width=460,
                     line_height=12, max_lines=6, font_size=9)


# ---------------------------------------------------------------------------
# PÁGINA 8 — B.I (cont.) + B.II avó materna + B.III avô paterno
# ---------------------------------------------------------------------------

def _fill_page_8(page: fitz.Page, rows: list[BoxRow], data: FormData) -> None:
    ensure_fonts(page)

    # Continuação B.I avô materno (~y=85..230) — só se a bio for grande
    # Pulamos por enquanto, considerando que cabe na pág 7

    # B.II avó materna (~y=300..460)
    bio_avo_mn = (translator.translate(data.biografia_avo_materna)
                  if data.biografia_avo_materna else "NIE DOTYCZY.")
    write_text_block(page, bio_avo_mn,
                     x=70, y=300, max_width=460,
                     line_height=12, max_lines=14, font_size=9)

    # B.III avô paterno (~y=540..760)
    bio_avo_p = (translator.translate(data.biografia_avo_paterno)
                 if data.biografia_avo_paterno else "NIE DOTYCZY.")
    write_text_block(page, bio_avo_p,
                     x=70, y=545, max_width=460,
                     line_height=12, max_lines=18, font_size=9)


# ---------------------------------------------------------------------------
# PÁGINA 9 — B.IV avó paterna + C. Ancestral polonês + D.I (cabeçalho)
# ---------------------------------------------------------------------------

def _fill_page_9(page: fitz.Page, rows: list[BoxRow], data: FormData) -> None:
    ensure_fonts(page)

    # B.IV avó paterna (~y=170..340)
    bio_avo_pn = (translator.translate(data.biografia_avo_paterna)
                  if data.biografia_avo_paterna else "NIE DOTYCZY.")
    write_text_block(page, bio_avo_pn,
                     x=70, y=170, max_width=460,
                     line_height=12, max_lines=14, font_size=9)

    # C. Ancestral polonês — biografia que justifica o pedido (~y=430..640)
    bio_anc = (translator.translate(data.biografia_ancestral_polones)
               if data.biografia_ancestral_polones else "NIE DOTYCZY.")
    write_text_block(page, bio_anc,
                     x=70, y=435, max_width=460,
                     line_height=12, max_lines=17, font_size=9)


# ---------------------------------------------------------------------------
# PÁGINA 10 — D.I, D.II, D.III + CZĘŚĆ IV
# ---------------------------------------------------------------------------

def _fill_page_10(page: fitz.Page, rows: list[BoxRow], data: FormData) -> None:
    ensure_fonts(page)

    # D.I. Decisões sobre parentes (~y=130..200)
    dec_par = (translator.translate(data.decisao_sobre_parentes)
               if data.decisao_sobre_parentes else "NIE.")
    write_text_block(page, dec_par,
                     x=70, y=140, max_width=460,
                     line_height=12, max_lines=5, font_size=9)

    # D.II. Documentos poloneses ascendentes (~y=240..310)
    docs = (translator.translate(data.docs_poloneses_ancestrais)
            if data.docs_poloneses_ancestrais else "NIE DOTYCZY.")
    write_text_block(page, docs,
                     x=70, y=245, max_width=460,
                     line_height=12, max_lines=5, font_size=9)

    # D.III. Renúncia cidadania ascendentes (~y=360..430)
    ren = (translator.translate(data.renuncia_cidadania_ancestrais)
           if data.renuncia_cidadania_ancestrais else "NIE.")
    write_text_block(page, ren,
                     x=70, y=370, max_width=460,
                     line_height=12, max_lines=5, font_size=9)

    # CZĘŚĆ IV — Outras informações (~y=505..795)
    parte_iv = (translator.translate(data.outras_informacoes)
                if data.outras_informacoes else "NIE DOTYCZY.")
    write_text_block(page, parte_iv,
                     x=70, y=510, max_width=460,
                     line_height=12, max_lines=22, font_size=9)


# ---------------------------------------------------------------------------
# PÁGINA 11 — Anexos + Data + Assinatura
# ---------------------------------------------------------------------------

def _fill_page_11(page: fitz.Page, rows: list[BoxRow], data: FormData) -> None:
    ensure_fonts(page)

    # Anexos — 20 linhas pontilhadas a partir de ~y=265
    # Cada item tem o número impresso à esquerda; escrevemos o texto à direita.
    anexos = data.anexos or []
    Y_INICIAL_ANEXO = 268
    LINE_HEIGHT_ANEXO = 17
    X_ANEXO = 100  # após o número "1.", "2.", etc

    for i, anexo in enumerate(anexos[:20]):
        if not anexo.strip():
            continue
        anexo_pl = translator.translate(anexo)
        y = Y_INICIAL_ANEXO + i * LINE_HEIGHT_ANEXO
        write_text_on_line(page, anexo_pl, x=X_ANEXO, y=y, max_width=440, font_size=9)

    # Data da submissão (boxes de data ~y=605)
    if rows:
        # A primeira fileira detectada na pág 11 é a data do solicitante
        write_date_boxes(page, _data_pl(data.data_submissao), rows[0])


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------

PAGE_FILLERS = [
    _fill_page_1, _fill_page_2, _fill_page_3, _fill_page_4,
    _fill_page_5, _fill_page_6, _fill_page_7, _fill_page_8,
    _fill_page_9, _fill_page_10, _fill_page_11,
]


def generate_pdf(data: FormData) -> bytes:
    """Carrega o template, injeta os dados em cada página e devolve os bytes do PDF."""
    logger.info("Gerando PDF para %s", data.nome_titular_confirmacao)

    doc = fitz.open(str(TEMPLATE_PATH))
    rows_by_page = detect_all_rows(str(TEMPLATE_PATH))

    for page_idx, filler in enumerate(PAGE_FILLERS):
        if page_idx >= len(doc):
            break
        try:
            filler(doc[page_idx], rows_by_page.get(page_idx, []), data)
        except Exception as e:
            logger.exception("Erro ao preencher página %d: %s", page_idx + 1, e)

    pdf_bytes = doc.tobytes()
    doc.close()

    logger.info("PDF gerado: %d bytes", len(pdf_bytes))
    return pdf_bytes
