"""
pdf_exporter.py — Addım 5: Startup hesabatını PDF-ə çevirir (fpdf2)
"""
from pathlib import Path
import datetime
import re

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


class StartupPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"AI Startup Team — Səhifə {self.page_no()}", align="C")


def export_to_pdf(startup_idea: str, results: dict, agents_map: dict) -> bytes:
    """
    Startup hesabatını PDF formatında qaytarır.
    Returns: PDF bytes (st.download_button üçün)
    """
    if not FPDF_AVAILABLE:
        raise RuntimeError("fpdf2 qurulmayıb. Terminal: pip install fpdf2")

    pdf = StartupPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(left=20, top=20, right=20)

    # ── Başlıq Səhifəsi ──────────────────────────────────────
    pdf.add_page()

    # Başlıq bloku
    pdf.set_fill_color(20, 20, 50)
    pdf.rect(0, 0, 210, 55, "F")

    pdf.set_y(12)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "AI Startup Team", align="C", ln=True)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(180, 190, 255)
    pdf.cell(0, 8, "Startup Hesabati", align="C", ln=True)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(140, 150, 200)
    pdf.cell(0, 7, f"Tarix: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", align="C", ln=True)

    # İdeya hissəsi
    pdf.set_y(65)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(20, 20, 60)
    pdf.set_fill_color(235, 238, 255)
    pdf.cell(0, 9, "Startup Ideyasi", fill=True, ln=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 6, _safe(startup_idea))

    # ── Agent Nəticələri ──────────────────────────────────────
    for key, content in results.items():
        pdf.add_page()

        agent = agents_map.get(key)
        if agent:
            header_text = _safe(f"{agent.name} — {agent.role}")
            sub_text = _safe(agent.goal)
        else:
            header_text = _safe(str(key).upper())
            sub_text = ""

        # Agent başlığı
        pdf.set_fill_color(25, 25, 60)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 11, header_text, fill=True, ln=True)

        if sub_text:
            pdf.set_fill_color(235, 238, 255)
            pdf.set_text_color(50, 50, 120)
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 7, sub_text[:90], fill=True, ln=True)

        pdf.ln(4)

        # Məzmun
        pdf.set_text_color(20, 20, 20)
        pdf.set_font("Helvetica", "", 9)

        clean = _clean_markdown(content)
        for line in clean.split("\n"):
            line = _safe(line.rstrip())
            if not line:
                pdf.ln(2)
                continue
            # Başlıq sətiri (böyük hərf çox, yaxud --- ilə başlayır)
            if line.startswith("===") or line.startswith("---"):
                pdf.ln(1)
                continue
            try:
                pdf.multi_cell(0, 5, line)
            except Exception:
                try:
                    pdf.multi_cell(0, 5, line[:100])
                except Exception:
                    pass

    return bytes(pdf.output())


def _safe(text: str) -> str:
    """Latin-1 uyğunluğu üçün xüsusi simvolları əvəzləyir."""
    replacements = {
        "\u0259": "e", "\u018f": "E",  # ə, Ə
        "\u011f": "g", "\u011e": "G",  # ğ, Ğ
        "\u0131": "i", "\u0130": "I",  # ı, İ
        "\u00f6": "o", "\u00d6": "O",  # ö, Ö
        "\u00fc": "u", "\u00dc": "U",  # ü, Ü
        "\u00e7": "c", "\u00c7": "C",  # ç, Ç
        "\u015f": "s", "\u015e": "S",  # ş, Ş
        "\u2019": "'", "\u2018": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "--",
        "\u2022": "*", "\u25cf": "*",
        "\u00b7": "*", "\u2026": "...",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text.encode("latin-1", "replace").decode("latin-1")


def _clean_markdown(text: str) -> str:
    """Markdown işarələrini sadə mətndə çevirir."""
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    return text
