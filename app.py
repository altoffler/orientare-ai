import streamlit as st
from google import genai
from google.genai import types
import pypdf
import sqlite3

# Importăm modulele create de noi anterior
from database import init_db, salveaza_utilizator, extrage_istoric
from pdf_generator import genereaza_pdf_raport

# Pornim baza de date SQLite locală
init_db()

# Inițializăm starea sesiunii
if "raport_final" not in st.session_state:
    st.session_state.raport_final = None

# Configurația Interfeței Grafice
st.set_page_config(page_title="Orientare Profesională AI", page_icon="🎓", layout="centered")

st.title("🎓 Orientator Profesional Inteligent")
st.subheader("Descoperă-ți vocația pentru era viitorului (AI & AGI)")
st.write("Încarcă diplomele sau desenele tale, iar AI-ul nostru te va ghida spre cariera ideală.")

# 1. Datele utilizatorului
nume = st.text_input("Numele tău complet:")
varsta = st.number_input("Vârsta:", min_value=10, max_value=100, value=18)
descriere = st.text_area("Povestește-ne despre tine (ce pasiuni ai, ce îți place să faci, ce urăști):")

diploma_file = st.file_uploader("Încarcă o diploma sau eseu (PDF, TXT):", type=["pdf", "txt"])
desen_file = st.file_uploader("Încarcă un desen, schiță sau proiect vizual (JPG, PNG):", type=["jpg", "jpeg", "png"])

# 2. Logica la apăsarea butonului de generare
if st.button("Generează Profilul de Carieră 🚀"):
    if not nume or not descriere:
        st.warning("Te rog să completezi cel puțin numele și descrierea personală.")
    else:
        with st.spinner("Psihosociologul AI îți analizează portofoliul..."):
            try:
                # Citim cheia API direct din seiful serverului (Streamlit Secrets)
                api_key_ascunsa = st.secrets["GEMINI_API_KEY"]
                client = genai.Client(api_key=api_key_ascunsa)
                
                continut_prompt = []
                date_text = f"PROFIL UTILIZATOR:\nNume: {nume}\nVârstă: {varsta}\nDescriere: {descriere}"
                continut_prompt.append(date_text)
                
                if diploma_file:
                    if diploma_file.name.endswith(".pdf"):
                        reader = pypdf.PdfReader(diploma_file)
                        text_diploma = ""
                        for page in reader.pages:
                            text_diploma += page.extract_text() + "\n"
                    else:
                        text_diploma = diploma_file.read().decode("utf-8", errors="ignore")
                    continut_prompt.append(f"\nDOCUMENT TEXT ATAȘAT:\n{text_diploma}")
                
                if desen_file:
                    bytes_imagine = desen_file.read()
                    part_imagine = types.Part.from_bytes(data=bytes_imagine, mime_type=desen_file.type)
                    continut_prompt.append(part_imagine)
                
                prompt_sistem = """
                Comportă-te ca un psihosociolog de elită și expert în orientare vocațională pentru era AGI.
                Analizează profilul și fișierele atașate. Generază un raport structurat în limba română, fără diacritice speciale:
                1. Analiza Psihosociologică a Profilului (Personalitate, puncte forte reflectate în desene/text)
                2. Top 3 Meserii de Viitor Sigure (Explicații clare de ce i se potrivesc în era AI)
                3. Plan de Acțiune pe 6 luni (Pași practici de dezvoltare de abilități umane și tehnice)
                """
                continut_prompt.append(f"\nINSTRUCTIUNE CRITICĂ: {prompt_sistem}")

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=continut_prompt
                )
                
                st.session_state.raport_final = response.text
                # Salvăm automat totul în baza de date locală
                salveaza_utilizator(nume, varsta, descriere, response.text)
                
            except Exception as e:
                st.error(f"Eroare tehnică la procesarea AI: {e}")

# 3. STRATEGIA DE MONETIZARE (Nativă și stabilă)
if st.session_state.raport_final:
    st.markdown("---")
    st.success("Analiza inițială a fost finalizată cu succes!")
    
    # Împărțim textul primit de la AI pentru a-i arăta doar prima parte (Mostra gratuită)
    linii_raport = st.session_state.raport_final.split('\n')
    mostra_gratuita = []
    
    # Extragem doar liniile care aparțin primei secțiuni (Analiza Psihosociologică)
    for linie in linii_raport:
        mostra_gratuita.append(linie)
        if "2." in linie or "Top 3" in linie or "Meserii" in linie:
            mostra_gratuita.pop() # Ne oprim exact înainte de secțiunea 2
            break
            
    # Afișăm pe ecran DOAR mostra gratuită
    st.markdown("### 🧠 Mostră Gratuită: Analiza Psihologică a Profilului Tău")
    st.write("\n".join(mostra_gratuita))
    
    # BLOCAJUL VIZUAL NATIV (Fără riscuri de sintaxă)
    st.markdown("---")
    st.warning("🔒 RESTUL RAPORTULUI ESTE BLOCAT")
    st.info(
        "Pentru a debloca Top 3 Meserii de Viitor Sigure adaptate profilului tău, "
        "Planul de Acțiune pe 6 luni și pentru a descărca Raportul Oficial complet în format PDF, "
        "trimite o contribuție de doar 25 RON prin una dintre metodele de mai jos:\n\n"
        "• Varianta 1 (Revolut): Trimite 25 RON în contul Revolut la numărul 0736-932-363.\n"
        "• Varianta 2 (PayPal): Trimite echivalentul în contul PayPal la adresa: anadanieladobre@gmail.com.\n\n"
        "Cum primești PDF-ul: Imediat ce plata este recepționată, îți vom trimite Raportul PDF complet "
        "direct pe adresa ta de email sau WhatsApp în maximum 15-30 de minute! Datele tale sunt salvate în siguranță în sistem."
    )

# 4. Zona Admin: Pentru ca TU să poți extrage PDF-urile plătite
st.markdown("---")
st.markdown("### 🗄️ Panou Administrativ (Doar pentru tine)")
if st.checkbox("Accesează baza de date pentru a trimite PDF-urile plătite"):
    cod_acces = st.text_input("Introdu codul tău de administrator:", type="password")
    if cod_acces == "orientareAI26": # Modifică parola cu una proprie
        st.write("Istoricul complet al rapoartelor generate:")
        
        conn = sqlite3.connect("orientare_cariera.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nume, varsta, descriere, raport_ai, data_creare FROM utilizatori ORDER BY id DESC")
        randuri = cursor.fetchall()
        conn.close()
        
        if randuri:
            for r in randuri:
                with st.expander(f"Candidat: {r[1]} ({r[2]} ani) - Data: {r[5]}"):
                    st.text("Descriere utilizator:")
                    st.write(r[3])
                    st.text("Raport Complet generat de AI:")
                    st.write(r[4])
                    
                    # Generăm PDF-ul pe loc în panoul tău de admin
                    pdf_bytes_admin = genereaza_pdf_raport(r[1], r[2], r[4])
                    st.download_button(
                        label=f"📥 Descarcă PDF-ul pentru {r[1]}",
                        data=bytes(pdf_bytes_admin),
                        file_name=f"Raport_{r[1].replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key=f"btn_{r[0]}"
                    )
        else:
            st.info("Baza de date este goală momentan.")
