"""Export table data to CSV / JSON / PDF."""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import Any

from smf_types.core import Column

# Simplified transliteration of Polish characters — built-in fpdf2 fonts (Helvetica)
# support only WinAnsi/Latin-1, so for PDF we map diacritics to the nearest
# ASCII equivalent (CSV/JSON keep full UTF-8).
_PL_MAP = str.maketrans({
    'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
    'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z',
    '—': '-', '–': '-', '„': '"', '”': '"', '↔': '<->', '→': '->',
})


def _ascii_safe(value: Any) -> str:
    text = _cell_text(value)
    return text.translate(_PL_MAP)


def _cell_text(value: Any) -> str:
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    return str(value)


def visible_columns(columns: list[Column], visible_keys: set[str]) -> list[Column]:
    return [c for c in columns if c.key in visible_keys]


def rows_to_csv_bytes(columns: list[Column], rows: list[dict]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=';')
    writer.writerow([c.label for c in columns])
    for row in rows:
        writer.writerow([_cell_text(row.get(c.key)) for c in columns])
    return buf.getvalue().encode('utf-8-sig')  # BOM => correct Polish characters in Excel


def rows_to_json_bytes(columns: list[Column], rows: list[dict]) -> bytes:
    keys = [c.key for c in columns]
    payload = [{k: row.get(k) for k in keys} for row in rows]
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str).encode('utf-8')


def rows_to_pdf_bytes(title: str, subtitle: str, columns: list[Column], rows: list[dict]) -> bytes:
    from fpdf import FPDF  # local import — fpdf2 is an optional dependency for PDF export only

    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 8, _ascii_safe(title), ln=1)
    pdf.set_font('helvetica', '', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, _ascii_safe(subtitle), ln=1)
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Rows: {len(rows)}", ln=1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

    usable_width = pdf.w - pdf.l_margin - pdf.r_margin
    col_width = usable_width / max(1, len(columns))
    row_height = 6

    def header_row():
        pdf.set_font('helvetica', 'B', 8)
        pdf.set_fill_color(28, 36, 56)
        pdf.set_text_color(255, 255, 255)
        for c in columns:
            pdf.cell(col_width, row_height, _ascii_safe(c.label)[:40], border=1, fill=True)
        pdf.ln(row_height)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('helvetica', '', 7.5)

    header_row()
    for i, row in enumerate(rows):
        if pdf.get_y() + row_height > pdf.h - pdf.b_margin:
            pdf.add_page()
            header_row()
        fill = i % 2 == 1
        if fill:
            pdf.set_fill_color(240, 240, 245)
        for c in columns:
            text = _ascii_safe(row.get(c.key))
            if len(text) > 28:
                text = text[:27] + '...'
            pdf.cell(col_width, row_height, text, border=1, fill=fill)
        pdf.ln(row_height)

    out = pdf.output()
    return bytes(out)
