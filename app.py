import streamlit as st
import pypdf
import sqlite3
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Importăm modulele create anterior
from database import init_db, salveaza_utilizator, extrage_istoric
from pdf_generator import genereaza_pdf_raport

# Pornim baza de date SQLite locală
init_db()

# Inițializăm starea sesiunii
if "raport_final" not in st.session_state:
    st.session_state.raport_final = None

def trimite_email_mostra(email_destinatar, nume_client, text_mostra):
    """Trimite automat e-mailul DOAR cu mostra gratuită și instrucțiunile de plată."""
    try:
        email_sursa = st.secrets["EMAIL_EXPEDITOR"]
        parola_sursa = st.secrets["EMAIL_PAROLA"]
        
        msg = MIMEMultipart()
        msg['From'] = email_sursa
        msg['To'] = email_destinatar
        msg['Subject'] = f"🎓 Confirmare Profil Vocațional AI - {nume_client}"
        
        corp_mesaj = f"""Bună ziua, {nume_client},

Îți mulțumim că ai folosit Orientatorul Profesional Inteligent! Datele tale au fost procesate cu succes.

Iată prima parte a analizei tale (Mostra Gratuită):
--------------------------------------------------
{text_mostra}
--------------------------------------------------

🔒 RESTUL RAPORTULUI TĂU ESTE SALVAT ȘI BLOCAT ÎN SISTEM

Pentru a debloca secțiunile „Top 3 Meserii de Viitor Sigure”, „Planul de Acțiune pe 6 luni” și pentru a primi Raportul Oficial complet în format PDF direct pe email/WhatsApp, trimite o contribuție de doar 25 RON:

• Varianta 1 (Revolut): Trimite 25 RON în contul Revolut la numărul 07XX-XXX-XXX. La detalii plată scrie obligatoriu numele tău din aplicație.
• Varianta 2 (PayPal): Trimite echivalentul în contul PayPal la adresa: email_sotie@gmail.com.

Imediat ce plata este recepționată, un psihosociolog din echipa noastră îți va trimite documentul PDF complet în maximum 15-30 de minute!

Cu respect,
Echipa Orientare AI
"""
        msg.attach(MIMEText(corp_mesaj, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_sursa, parola_sursa)
        server.sendmail(email_sursa, email_destinatar, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Eroare la trimiterea e-mailului de confirmare: {e}")
        return False

# Configurația Interfeței Grafice
st.set_page_config(page_title="Orientare Profesională AI", page_icon="🎓", layout="centered")

st.title("🎓 Orientator Profesional Inteligent")
st.subheader("Descoperă-ți vocația pentru era viitorului (AI & AGI)")
st.write("Încarcă diplomele tale, iar AI-ul nostru te va ghida spre cariera ideală.")

nume = st.text_input("Numele tău complet:")
email = st.text_input("Adresa ta de Email (pentru livrarea PDF-ului):")
telefon = st.text_input("Numărul tău de Telefon / WhatsApp (pentru livrare rapidă):")
varsta = st.number_input("Vârsta:", min_value=10, max_value=100, value=18)
descriere = st.text_area("Povestește-ne despre tine (ce pasiuni ai, ce îți place să faci, ce urăști):")

diploma_file = st.file_uploader("Încarcă o diplomă sau eseu (PDF, TXT):", type=["pdf", "txt"])
desen_file = st.file_uploader("Încarcă un desen, schiță sau proiect vizual (JPG, PNG):", type=["jpg", "jpeg", "png"])

if st.button("Generează Profilul de Carieră 🚀"):
    if not nume or not email or not telefon or not descriere:
        st.warning("Te rog să completezi toate câmpurile obligatorii.")
    else:
        with st.spinner("Psihosociologul AI DeepSeek îți analizează datele..."):
            try:
                # Construim contextul text pentru DeepSeek
                text_complet = f"PROFIL UTILIZATOR:\nNume: {nume}\nVârstă: {varsta} ani\nDescriere: {descriere}"
                
                if diploma_file:
                    if diploma_file.name.endswith(".pdf"):
                        reader = pypdf.PdfReader(diploma_file)
                        text_diploma = ""
                        for page in reader.pages:
                            text_diploma += page.extract_text() + "\n"
                    else:
                        text_diploma = diploma_file.read().decode("utf-8", errors="ignore")
                    text_complet += f"\n\nDOCUMENT TEXT ATAȘAT:\n{text_diploma}"
                
                if desen_file:
                    # DeepSeek fiind text-only, îi dăm o notă modelului că utilizatorul s-a exprimat și vizual
                    text_complet += f"\n\n[Notă Sistem: Utilizatorul a atașat și o schiță/desen cu numele '{desen_file.name}'. Concentrează-te pe interpretarea psihosociologică intensă a textului din descriere.]"
                
                # Pregătire apel API DeepSeek securizat
                api_key_ascunsa = st.secrets["DEEPSEEK_API_KEY"]
                url_deepseek = "https://api.deepseek.com/v1/chat/completions"
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key_ascunsa}"
                }
                
                prompt_sistem = """
                Comportă-te ca un psihosociolog de elită și expert în orientare vocațională pentru era AGI.
                Analizează profilul și fișierele atașate. Generază un raport structurat în limba română, fără diacritice speciale:
                1. Analiza Psihosociologică a Profilului (Personalitate, puncte forte reflectate în text)
                2. Top 3 Meserii de Viitor Sigure (Explicații clare de ce i se potrivesc în era AI)
                3. Plan de Acțiune pe 6 luni (Pași practici de dezvoltare de abilități umane și tehnice)
                """
                
                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": prompt_sistem},
                        {"role": "user", "content": text_complet}
                    ],
                    "temperature": 0.7
                }

                response = requests.post(url_deepseek, json=payload, headers=headers)
                
                if response.status_code == 200:
                    raport_text = response.json()['choices'][0]['message']['content']
                    st.session_state.raport_final = raport_text
                    salveaza_utilizator(nume, email, telefon, varsta, descriere, raport_text)
                    
                    # Extragem mostra text pentru e-mail
                    linii = raport_text.split('\n')
                    mostra_text = []
                    for l in linii:
                        mostra_text.append(l)
                        if "2." in l or "Top 3" in l:
                            mostra_text.pop()
                            break
                    text_pentru_email = "\n".join(mostra_text)
                    
                    # Trimitem mostra pe email
                    trimite_email_mostra(email, nume, text_pentru_email)
                    st.success("✅ Analiza inițială a fost finalizată, iar mostra gratuită a fost trimisă pe email!")
                else:
                    st.error(f"Eroare la API-ul DeepSeek ({response.status_code}): {response.text}")
                
            except Exception as e:
                st.error(f"Eroare tehnică la procesarea AI: {e}")

# Afișarea pe ecran (Paywall-ul comercial)
if st.session_state.raport_final:
    st.markdown("---")
    linii_raport = st.session_state.raport_final.split('\n')
    mostra_gratuita = []
    for linie in linii_raport:
        mostra_gratuita.append(linie)
        if "2." in linie or "Top 3" in linie or "Meserii" in linie:
            mostra_gratuita.pop()
            break
            
    st.markdown("### 🧠 Mostră Gratuită: Analiza Psihologică a Profilului Tău")
    st.write("\n".join(mostra_gratuita))
    
    st.markdown("---")
    st.warning("🔒 RESTUL RAPORTULUI ESTE BLOCAT")
    st.info(
        "For deblocking Top 3 Meserii de Viitor Sigure adaptate profilului tău, "
        "Planul de Acțiune pe 6 luni și pentru a descărca Raportul Oficial complet în format PDF, "
        "trimite o contribuție de doar 25 RON prin:\n\n"
        "• Varianta 1 (Revolut): Trimite 25 RON în contul Revolut la numărul 0736-932-363.\n"
        "• Varianta 2 (PayPal): Trimite echivalentul în contul PayPal la adresa: anadanieladobre@gmail.com.\n\n"
        "Cum primești PDF-ul: Imediat ce vedem notificarea de plată, îți vom trimite Raportul PDF complet "
        "direct pe Email sau WhatsApp în maximum 15-30 de minute!"
    )

# Panoul Admin
st.markdown("---")
st.markdown("### 🗄️ Panou Administrativ (Doar pentru tine)")
if st.checkbox("Accesează baza de date pentru a trimite PDF-urile plătite"):
    cod_acces = st.text_input("Introdu codul tău de administrator:", type="password")
    if cod_acces == "orientareAI26":
        st.write("Istoricul complet al rapoartelor generate de clienți:")
        randuri = extrage_istoric()
        if randuri:
            for r in randuri:
                with st.expander(f"Candidat: {r[1]} | Email: {r[2]} | Tel: {r[3]} | Data: {r[5]}"):
                    conn = sqlite3.connect("orientare_cariera.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT descriere, raport_ai FROM utilizatori WHERE id = ?", (r[0],))
                    date_detaliate = cursor.fetchone()
                    conn.close()
                    
                    if date_detaliate:
                        st.text("Raport Complet existent în baza de date:")
                        st.write(date_detaliate[1])
                        
                        pdf_bytes_admin = genereaza_pdf_raport(r[1], r[4], date_detaliate[1])
                        st.download_button(
                            label=f"📥 Descarcă PDF complet pentru {r[1]}",
                            data=bytes(pdf_bytes_admin),
                            file_name=f"Raport_Complet_{r[1].replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            key=f"btn_{r[0]}"
                        )