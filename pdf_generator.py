from fpdf import FPDF
import datetime

def genereaza_pdf_raport(nume, varsta, text_raport):
    """
    Transforma textul raportului AI intr-un fisier PDF salvat in memorie.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Antetul Raportului
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Raport de Orientare Vocationala AI", ln=True, align="C")
    pdf.ln(5)
    
    # 2. Informații despre utilizator
    pdf.set_font("Helvetica", "I", 12)
    data_curenta = datetime.date.today().strftime('%d.%m.%Y')
    pdf.cell(0, 10, f"Candidat: {nume} | Varsta: {varsta} ani", ln=True, align="C")
    pdf.cell(0, 10, f"Data generarii: {data_curenta}", ln=True, align="C")
    
    # Linie de separare
    pdf.line(10, 42, 200, 42)
    pdf.ln(12)
    
    # 3. Conținutul Raportului
    pdf.set_font("Helvetica", "", 11)
    
    # Curățăm formatările Markdown simple pentru a evita caracterele ciudate în PDF
    text_curat = text_raport.replace("**", "").replace("###", "").replace("##", "-")
    
    # Scriem textul cu aliniere automată la capăt de rând (multi_cell)
    # Folosim encode/decode 'latin-1' ca soluție de bază pentru caracterele standard
    pdf.multi_cell(0, 6, text_curat.encode('latin-1', 'replace').decode('latin-1'))
    
    # Returnăm PDF-ul sub formă de bytes (în memorie), gata pentru descărcare
    return pdf.output()
