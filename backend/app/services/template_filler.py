"""
Utilitários de escrita sobre o template oficial polonês.

Os handlers recebem o `fitz.Page`, os dados a escrever, e a referência da
fileira de caixinhas (BoxRow) ou as coordenadas livres (y, x_start, max_w).

FONTE: registramos DejaVu Sans / DejaVu Sans Bold em cada página antes do
primeiro `insert_text`. A Helvetica nativa do PDF não cobre os diacríticos
poloneses (Ł, Ó, Ś, Ż, Ę, Ą, Ć, Ń, etc.).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import fitz

from .box_detector import BoxRow

# ---------------------------------------------------------------------------
# Fontes — DejaVu Sans cobre todos os diacríticos poloneses
# ---------------------------------------------------------------------------
_FONTS_DIR = Path(__file__).parent.parent / "fonts"
FONT_REGULAR_PATH = _FONTS_DIR / "DejaVuSans.ttf"
FONT_BOLD_PATH = _FONTS_DIR / "DejaVuSans-Bold.ttf"

# Aliases que registramos em cada página
FONT_REGULAR = "djv"
FONT_BOLD = "djvb"

# Tamanhos padrão
CHAR_FONT_SIZE = 8.5    # Letra dentro de caixinha (DejaVu é mais larga que Helv)
TEXT_FONT_SIZE = 9      # Texto livre em linhas pontilhadas
SMALL_TEXT_FONT_SIZE = 8


def ensure_fonts(page: fitz.Page) -> None:
    """
    Registra as fontes DejaVu na página (idempotente).
    Chame ANTES do primeiro `insert_text` em cada página nova.
    """
    page.insert_font(fontname=FONT_REGULAR, fontfile=str(FONT_REGULAR_PATH))
    page.insert_font(fontname=FONT_BOLD, fontfile=str(FONT_BOLD_PATH))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize(text: Optional[str]) -> str:
    """Converte para MAIÚSCULAS e remove espaços extras."""
    if text is None:
        return ""
    return str(text).strip().upper()


# Cache de fontes para medição (carregadas uma vez)
_FONT_CACHE: dict[str, fitz.Font] = {}


def _get_font(path: Path) -> fitz.Font:
    key = str(path)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = fitz.Font("djv", key)
    return _FONT_CACHE[key]


def _measure(text: str, fontfile: Path, size: float) -> float:
    """Mede a largura de um texto na fonte/tamanho informados."""
    return _get_font(fontfile).text_length(text, fontsize=size)


# ---------------------------------------------------------------------------
# Handlers — char-boxes (caixinhas de caractere)
# ---------------------------------------------------------------------------

def write_char_boxes(
    page: fitz.Page,
    text: Optional[str],
    row: BoxRow,
    start_index: int = 0,
    end_index: Optional[int] = None,
    font_size: float = CHAR_FONT_SIZE,
) -> None:
    """
    Escreve uma letra em cada caixinha da fileira, centralizada.

    Args:
        page: página do PyMuPDF onde escrever
        text: string a distribuir (será uppercased automaticamente)
        row: BoxRow com as caixinhas detectadas
        start_index: começar a partir da caixinha N (para sub-fileiras)
        end_index: parar na caixinha N (exclusivo)
    """
    text = _normalize(text)
    if not text:
        return

    end_index = end_index if end_index is not None else row.n
    available = row.boxes[start_index:end_index]

    for i, char in enumerate(text):
        if i >= len(available):
            break
        box = available[i]
        char_width = _measure(char, FONT_REGULAR_PATH, font_size)
        x = box.cx - char_width / 2
        # Baseline no fundo da caixa, com leve margem
        y = box.y1 - 1.5
        page.insert_text((x, y), char, fontname=FONT_REGULAR,
                         fontsize=font_size, color=(0, 0, 0))


def write_date_boxes(
    page: fitz.Page,
    iso_date: Optional[str],
    row: BoxRow,
) -> None:
    """
    Escreve uma data 'YYYY-MM-DD' nas caixinhas no padrão ano(4)/mês(2)/dia(2).

    O template normalmente tem 10 slots na fileira de data:
        [Y][Y][Y][Y] / [M][M] / [D][D]
    com separadores '/' como pseudo-caixas nas posições 4 e 7.
    """
    if not iso_date or len(iso_date) < 10:
        return
    try:
        y, m, d = iso_date.split("-")
    except ValueError:
        return

    digits = y + m + d  # 8 chars: YYYYMMDD

    if row.n >= 10:
        # 4 ano + skip + 2 mês + skip + 2 dia
        positions = [0, 1, 2, 3, 5, 6, 8, 9]
    elif row.n == 8:
        positions = [0, 1, 2, 3, 4, 5, 6, 7]
    else:
        positions = list(range(min(len(digits), row.n)))

    for i, digit in enumerate(digits):
        if i >= len(positions):
            break
        idx = positions[i]
        if idx >= row.n:
            break
        box = row.boxes[idx]
        w = _measure(digit, FONT_REGULAR_PATH, CHAR_FONT_SIZE)
        x = box.cx - w / 2
        y_pos = box.y1 - 1.5
        page.insert_text((x, y_pos), digit, fontname=FONT_REGULAR,
                         fontsize=CHAR_FONT_SIZE, color=(0, 0, 0))


def write_two_field_row(
    page: fitz.Page,
    row: BoxRow,
    text_left: Optional[str],
    text_right: Optional[str],
    split_gap_threshold: float = 25.0,
) -> None:
    """
    Escreve DOIS textos numa fileira que contém duas sub-fileiras separadas
    por gap (ex: "Numer domu" + "Numer mieszkania").
    """
    split_idx = len(row.boxes)
    for i in range(1, len(row.boxes)):
        gap = row.boxes[i].x0 - row.boxes[i - 1].x1
        if gap > split_gap_threshold:
            split_idx = i
            break

    write_char_boxes(page, text_left, row, start_index=0, end_index=split_idx)
    write_char_boxes(page, text_right, row, start_index=split_idx)


# ---------------------------------------------------------------------------
# Handlers — texto livre
# ---------------------------------------------------------------------------

def write_text_on_line(
    page: fitz.Page,
    text: Optional[str],
    x: float,
    y: float,
    max_width: float,
    font_size: float = TEXT_FONT_SIZE,
    bold: bool = False,
    uppercase: bool = True,
) -> None:
    """Escreve uma única linha de texto, truncando se ultrapassar max_width."""
    if not text:
        return
    text = _normalize(text) if uppercase else str(text).strip()
    if not text:
        return

    fontname = FONT_BOLD if bold else FONT_REGULAR
    fontfile = FONT_BOLD_PATH if bold else FONT_REGULAR_PATH

    while _measure(text, fontfile, font_size) > max_width and len(text) > 3:
        text = text[:-1]

    page.insert_text((x, y), text, fontname=fontname,
                     fontsize=font_size, color=(0, 0, 0))


def write_text_block(
    page: fitz.Page,
    text: Optional[str],
    x: float,
    y: float,
    max_width: float,
    line_height: float = 11,
    max_lines: int = 12,
    font_size: float = TEXT_FONT_SIZE,
    uppercase: bool = True,
) -> float:
    """
    Escreve texto com word-wrap em bloco livre (em cima das linhas pontilhadas).
    Retorna o Y da última linha escrita.
    """
    if not text:
        return y
    text = (str(text).strip().upper() if uppercase else str(text).strip())
    if not text:
        return y

    paragraphs = text.split("\n")
    cur_y = y
    lines_written = 0

    for para in paragraphs:
        if lines_written >= max_lines:
            break
        words = para.split()
        if not words:
            cur_y += line_height
            lines_written += 1
            continue

        current_line = ""
        for word in words:
            candidate = word if not current_line else f"{current_line} {word}"
            if _measure(candidate, FONT_REGULAR_PATH, font_size) <= max_width:
                current_line = candidate
            else:
                if current_line:
                    page.insert_text((x, cur_y), current_line, fontname=FONT_REGULAR,
                                     fontsize=font_size, color=(0, 0, 0))
                    cur_y += line_height
                    lines_written += 1
                    if lines_written >= max_lines:
                        break
                current_line = word
        if current_line and lines_written < max_lines:
            page.insert_text((x, cur_y), current_line, fontname=FONT_REGULAR,
                             fontsize=font_size, color=(0, 0, 0))
            cur_y += line_height
            lines_written += 1

    return cur_y


# ---------------------------------------------------------------------------
# Handlers — checkboxes
# ---------------------------------------------------------------------------

def draw_checkbox_cross(
    page: fitz.Page,
    x: float,
    y: float,
    size: float = 9,
) -> None:
    """Desenha um X dentro de um checkbox quadrado centrado em (x, y)."""
    half = size / 2
    page.draw_line(
        fitz.Point(x - half, y - half), fitz.Point(x + half, y + half),
        color=(0, 0, 0), width=1.0,
    )
    page.draw_line(
        fitz.Point(x + half, y - half), fitz.Point(x - half, y + half),
        color=(0, 0, 0), width=1.0,
    )
