"""
Detecta automaticamente as "fileiras de caixinhas" (char-boxes) em cada
página do template oficial polonês.

Uma fileira é um conjunto de pequenos retângulos retangulares contíguos
(≈17.2pt de largura, ≈8pt de altura) onde cada caixa recebe UMA letra/dígito.

O resultado é uma lista ordenada de `BoxRow` por página, onde cada BoxRow
tem {y0, y1, boxes=[(x0, x1, y0, y1), ...]}. Os campos do formulário
são mapeados para essas fileiras por POSIÇÃO ORDINAL (1ª fileira da
página, 2ª, etc.) no módulo `template_layout.py`.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List

import fitz  # PyMuPDF


# Largura típica de uma caixinha no template (em pontos PDF)
BOX_WIDTH_MIN = 15.5
BOX_WIDTH_MAX = 20.0

# Altura típica (corresponde à altura visual do "quadradinho")
BOX_HEIGHT_MIN = 7.5
BOX_HEIGHT_MAX = 16.0


@dataclass
class CharBox:
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def cy(self) -> float:
        return (self.y0 + self.y1) / 2


@dataclass
class BoxRow:
    """Uma fileira horizontal de caixinhas alinhadas no mesmo Y."""
    y0: float
    y1: float
    boxes: List[CharBox]

    @property
    def n(self) -> int:
        return len(self.boxes)

    @property
    def x_start(self) -> float:
        return self.boxes[0].x0 if self.boxes else 0.0

    @property
    def x_end(self) -> float:
        return self.boxes[-1].x1 if self.boxes else 0.0


def detect_box_rows(page: fitz.Page) -> List[BoxRow]:
    """Extrai todas as fileiras de caixinhas da página, ordenadas por Y (de cima para baixo)."""
    drawings = page.get_drawings()

    # Extrair todas as "linhas verticais" (retângulos finos altos que formam bordas das caixinhas)
    v_lines = []
    for d in drawings:
        r = d.get("rect")
        if r is None:
            continue
        w = r.width
        h = r.height
        if w < 1.0 and BOX_HEIGHT_MIN < h < BOX_HEIGHT_MAX:
            v_lines.append((round(r.x0, 1), round(r.y0, 1), round(r.y1, 1)))

    # Agrupar linhas verticais por (y0, y1) — mesma fileira de caixas
    by_y = defaultdict(set)
    for x, y0, y1 in v_lines:
        by_y[(y0, y1)].add(x)

    rows: List[BoxRow] = []
    for (y0, y1), xs in by_y.items():
        xs_sorted = sorted(xs)
        if len(xs_sorted) < 2:
            continue

        # Formar caixas a partir de pares consecutivos de X; ignorar gaps fora do range
        boxes: List[CharBox] = []
        for i in range(len(xs_sorted) - 1):
            dx = xs_sorted[i + 1] - xs_sorted[i]
            if BOX_WIDTH_MIN < dx < BOX_WIDTH_MAX:
                boxes.append(CharBox(
                    x0=xs_sorted[i], y0=y0,
                    x1=xs_sorted[i + 1], y1=y1,
                ))
        if boxes:
            rows.append(BoxRow(y0=y0, y1=y1, boxes=boxes))

    rows.sort(key=lambda r: r.y0)
    return rows


@lru_cache(maxsize=1)
def detect_all_rows(pdf_path: str) -> dict[int, List[BoxRow]]:
    """
    Detecta todas as fileiras em todas as páginas do template.
    Resultado cacheado (só roda uma vez).
    """
    doc = fitz.open(pdf_path)
    result = {}
    for i in range(len(doc)):
        result[i] = detect_box_rows(doc[i])
    doc.close()
    return result
