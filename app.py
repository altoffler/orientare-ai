import streamlit as st
from google import genai
from google.genai import types
import pypdf

# Importăm modulele create de noi în sarcinile anterioare
from database import init_db, salveaza_utilizator, extrage_istoric
from pdf_generator import genereaza_pdf_raport

# Pornim baza de date SQLite locală
init_db()

# Inițializăm starea sesiunii pentru a păstra raportul pe ecran
if "raport_final" not in st.session_state:
    st.session_state.raport_final = None

# 1. Configurația Interfeței Grafice
st.set_page_config(page_title="Orientare Profesională AI", page_icon="🎓", layout="centered")

st.title("🎓 Orientator Profesional Inteligent")
st.subheader("Descoperă-ți vocația pentru era viitorului (AI & AGI)")
st.write("Încarcă diplomele sau desenele tale, iar AI-ul nostru te va ghida spre cariera ideală.")

# 2. Căsuța pentru Cheia API Google Gemini
api_key = st.text_input("Introdu Cheia ta Google Gemini API:", type="password", 
                       help="Obține o cheie gratuită din Google AI Studio.")

# 3. Formularul de date al utilizatorului
nume = st.text_input("Numele tău complet:")
varsta = st.number_input("Vârsta:", min_value=10, max_value=100, value=18)
descriere = st.text_area("Povestește-ne despre tine (ce pasiuni ai, ce îți place să faci, ce urăști):")

# Căsuțele de încărcare fișiere (Multimodal)
diploma_file = st.file_uploader("Încarcă o diplomă sau eseu (PDF, TXT):", type=["pdf", "txt"])
desen_file = st.file_uploader("Încarcă un desen, schiță sau proiect vizual (JPG, PNG):", type=["jpg", "jpeg", "png"])

# 4. Logica la apăsarea butonului de generare
if st.button("Generează Profilul de Carieră 🚀"):
    if not api_key:
        st.error("Te rog să introduci cheia API pentru a porni creierul AI.")
    elif not nume or not descriere:
        st.warning("Te rog să completezi cel puțin numele și descrierea personală.")
    else:
        with st.spinner("Psihosociologul AI îți analizează portofoliul și salvează datele..."):
            try:
                # Conectarea oficială la noul API Google GenAI
                client = genai.Client(api_key=api_key)
                continut_prompt = []
                
                # Adăugăm datele text în lista trimisă la AI
                date_text = f"PROFIL UTILIZATOR:\nNume: {nume}\nVârstă: {varsta}\nDescriere: {descriere}"
                continut_prompt.append(date_text)
                
                # Dacă există un fișier încărcat, extragem textul inteligent
                if diploma_file:
                    if diploma_file.name.endswith(".pdf"):
                        reader = pypdf.PdfReader(diploma_file)
                        text_diploma = ""
                        for page in reader.pages:
                            text_diploma += page.extract_text() + "\n"
                    else:
                        text_diploma = diploma_file.read().decode("utf-8", errors="ignore")
                    
                    continut_prompt.append(f"\nDOCUMENT TEXT ATAȘAT:\n{text_diploma}")
                
                # Dacă există o imagine (desen), o trimitem ca Part brut către Gemini
                if desen_file:
                    bytes_imagine = desen_file.read()
                    part_imagine = types.Part.from_bytes(
                        data=bytes_imagine,
                        mime_type=desen_file.type
                    )
                    continut_prompt.append(part_imagine)
                
                # Promptul tău de sistem ca psihosociolog, optimizat pentru PDF (fără diacritice speciale)
                prompt_sistem = """
                Comportă-te ca un psihosociolog de elită și expert în orientare vocațională pentru era AGI.
                Analizează profilul și fișierele atașate. Generază un raport structurat în limba română (folosește formatare curată):
                1. Analiza Psihosociologică a Profilului (Personalitate, puncte forte reflectate în desene/text)
                2. Top 3 Meserii de Viitor Sigure (Explicații clare de ce i se potrivesc în era AI)
                3. Plan de Acțiune pe 6 luni (Pași practici de dezvoltare de abilități umane și tehnice)
                
                Notă importantă pentru compatibilitatea PDF: Înlocuiește diacriticele speciale (ș, ț, ă, î, â) cu litere standard (s, t, a, i, a) sau combinații clare în textul final pentru a evita erorile de compilare.
                """
                continut_prompt.append(f"\nINSTRUCTIUNE CRITICĂ: {prompt_sistem}")

                # Apelăm modelul stabil de înaltă performanță Gemini 2.5 Flash
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=continut_prompt
                )
                
                # Salvăm rezultatul în sesiune și în baza de date locală SQLite
                st.session_state.raport_final = response.text
                salveaza_utilizator(nume, varsta, descriere, response.text)
                st.success("Raportul a fost generat și salvat local în baza de date!")
                
            except Exception as e:
                st.error(f"Eroare tehnică la procesarea AI: {e}")

# 5. Afișarea raportului și activarea butonului de descărcare PDF
if st.session_state.raport_final:
    st.markdown("---")
    st.markdown(st.session_state.raport_final)
    st.markdown("---")
    
    # Generăm PDF-ul folosind modulul nostru secundar
    pdf_bytes = genereaza_pdf_raport(nume, varsta, st.session_state.raport_final)
    
    # Butonul de descărcare
    st.download_button(
        label="📥 Descarcă Raportul în format PDF",
        data=bytes(pdf_bytes),
        file_name=f"Raport_Carieră_{nume.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

# 6. Zona Admin: Vizualizarea istoricului din baza de date
st.markdown("---")
st.markdown("### 🗄️ Panou Administrativ (Local)")
if st.checkbox("Afișează istoricul utilizatorilor salvați"):
    randuri = extrage_istoric()
    if randuri:
        for r in randuri:
            st.write(f"**ID: {r[0]}** | Nume: {r[1]} ({r[2]} ani) | Data: {r[3]}")
    else:
        st.info("Baza de date este goală momentan.")
