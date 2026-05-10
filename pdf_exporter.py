"""
pdf_exporter.py — Addım 5: Startup hesabatını PDF-ə çevirir (fpdf2)
"""
from pathlib import Path
import datetime

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


def export_to_pdf(startup_idea: str, results: dict, agents_map: dict) -> bytes:
    """
    Startup hesabatını PDF formatında qaytarır.
    Returns: PDF bytes (st.download_button üçün)
    """
    if not FPDF_AVAILABLE:
        raise RuntimeError("fpdf2 qurulmayıb. Terminal: pip install fpdf2")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Başlıq ───────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_fill_color(15, 15, 40)
    pdf.set_text_color(255, 255, 255)
    pdf.rect(0, 0, 210, 40, "F")
    pdf.set_y(12)
    pdf.cell(0, 10, "AI Startup Team Report", align="C", ln=True)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(200, 200, 255)
    pdf.cell(0, 7, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C", ln=True)

    pdf.set_y(45)

    # ── İdeya ────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 30, 80)
    pdf.set_fill_color(230, 235, 255)
    pdf.cell(0, 9, "Startup Idea", fill=True, ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 7, startup_idea)
    pdf.ln(5)

    # ── Agent nəticələri ──────────────────────────────────────
    for key, content in results.items():
        agent = agents_map.get(key)
        name = f"{agent.emoji} {agent.name} — {agent.role}" if agent else key

        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_fill_color(20, 20, 60)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, _safe_str(name), fill=True, ln=True)
        pdf.ln(3)

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(20, 20, 20)

        # Uzun mətnləri parçala (FPDF çox uzun sətirləri sevmir)
        clean = _clean_markdown(content)
        for paragraph in clean.split("\n"):
            paragraph = _safe_str(paragraph)
            if paragraph.strip():
                try:
                    pdf.multi_cell(0, 6, paragraph)
                except Exception:
                    pdf.multi_cell(0, 6, paragraph.encode("latin-1", "replace").decode("latin-1"))
            else:
                pdf.ln(3)

    return bytes(pdf.output())


def _safe_str(text: str) -> str:
    """Latin-1 uyğunluğu üçün xüsusi simvolları təmizlər."""
    return text.encode("latin-1", "replace").decode("latin-1")


def _clean_markdown(text: str) -> str:
    """Əsas Markdown işarələrini sadə mətndə çevirir."""
    import re
    text = re.sub(r"#{1,6}\s*", "", text)      # Başlıqlar
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # Bold
    text = re.sub(r"\*(.+?)\*", r"\1", text)      # İtalik
    text = re.sub(r"`(.+?)`", r"\1", text)         # Kod
    text = re.sub(r"<[^>]+>", "", text)            # XML/HTML tagları
    return text
