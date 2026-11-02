import streamlit as st
import pandas as pd
import os
from datetime import datetime
import calendar

# Configurazione della pagina ottimizzata per Mobile e Desktop
st.set_page_config(page_title="ZAMTEK SHOP - Fidelity", layout="centered")

DB_FILE = "fidelity_database.csv"
LOG_FILE = "fidelity_cronologia.csv"
LOGO_FILE = "logo.png"
PASSWORD_CASSA = "zamtek2026"  # Password segreta per te alla cassa

# Funzione per calcolare le date di validità in italiano
def ottieni_date_validita():
    ora = datetime.now()
    anno_corrente = ora.year
    mese_corrente = ora.month
    
    ultimo_giorno = calendar.monthrange(anno_corrente, mese_corrente)
    data_inizio_attivita = f"01/{mese_corrente:02d}/{anno_corrente}"
    data_fine_attivita = f"{ultimo_giorno:02d}/{mese_corrente:02d}/{anno_corrente}"
    nome_mese_corrente = calendar.month_name[mese_corrente].capitalize()
    
    if mese_corrente == 12:
        mese_succ = 1
        anno_succ = anno_corrente + 1
    else:
        mese_succ = mese_corrente + 1
        anno_succ = anno_corrente
    nome_mese_succ = calendar.month_name[mese_succ].capitalize()
    
    return data_inizio_attivita, data_fine_attivita, nome_mese_corrente, nome_mese_succ

# Imposta i mesi in italiano nel sistema
import locale
try:
    locale.setlocale(locale.LC_TIME, "it_IT.UTF-8")
except:
    try:
        locale.setlocale(locale.LC_TIME, "it_IT")
    except:
        pass

data_inizio, data_fine, mese_attuale_nome, mese_prossimo_nome = ottieni_date_validita()

# Funzione per calcolare il livello futuro in base ai timbri attuali
def calcola_livello_futuro(timbri):
    if timbri >= 10:
        return "🥇 CHAMPION"
    elif timbri >= 5:
        return "🥈 CHALLENGER"
    else:
        return "🥉 Nessun Livello"

# Funzione per mappare gli sconti descrittivi
def descrivi_sconto(livello):
    if livello == "🥇 CHAMPION":
        return "7% Singole ≤30€ | 5% Singole >30€ | 5% Sealed (Bustine/Mazzi)"
    elif livello == "🥈 CHALLENGER":
        return "5% su Tutte le Carte Singole | No Sealed"
    else:
        return "Prezzo pieno su tutto"

# Funzione per registrare un evento nella cronologia
def scrivi_log(giocatore, operazione, timbri_variati):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nuovo_log = {
        "Data/Ora": timestamp,
        "Giocatore": giocatore,
        "Operazione": operazione,
        "Variazione Timbri": timbri_variati
    }
    if os.path.exists(LOG_FILE):
        log_df = pd.read_csv(LOG_FILE)
        log_df = pd.concat([pd.DataFrame([nuovo_log]), log_df], ignore_index=True)
    else:
        log_df = pd.DataFrame([nuovo_log])
    log_df.to_csv(LOG_FILE, index=False)

# Funzione per caricare il database
def carica_db():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if 'Timbri_Mese' not in df.columns:
            df['Timbri_Mese'] = 0
        if 'Livello_Attuale' not in df.columns:
            df['Livello_Attuale'] = "🥉 Nessun Livello"
        if 'Ultimo_Aggiornamento_Mese' not in df.columns:
            df['Ultimo_Aggiornamento_Mese'] = datetime.now().strftime("%Y-%m")
        if 'Password_Utente' not in df.columns:
            df['Password_Utente'] = df['Nome'].str.lower().str[:3] + "123"
        return df
    else:
        return pd.DataFrame(columns=["Nome", "Cognome", "Email_ID", "Password_Utente", "Timbri_Mese", "Livello_Attuale", "Ultimo_Aggiornamento_Mese"])

# Funzione per salvare il database
def salva_db(df):
    df.to_csv(DB_FILE, index=False)

# Funzione per il ricalcolo automatico dei livelli al cambio del mese
def controllo_cambio_mese_automatico(df):
    if df.empty:
        return df
    mese_corrente = datetime.now().strftime("%Y-%m")
    modificato = False
    for idx, row in df.iterrows():
        if str(row['Ultimo_Aggiornamento_Mese']) != mese_corrente:
            timbri = row['Timbri_Mese']
            vecchio_livello = row['Livello_Attuale']
            nuovo_livello = calcola_livello_futuro(timbri)
            
            df.at[idx, 'Livello_Attuale'] = nuovo_livello
            df.at[idx, 'Timbri_Mese'] = 0  
            df.at[idx, 'Ultimo_Aggiornamento_Mese'] = mese_corrente
            modificato = True
            
            # Registra il reset automatico nel log
            scrivi_log(f"{row['Nome']} {row['Cognome']}", f"Reset Mensile Autom. (Nuovo Livello: {nuovo_livello} basato su {timbri} timbri)", 0)
            
    if modificato:
        salva_db(df)
    return df

# Inizializzazione database
df = carica_db()
df = controllo_cambio_mese_automatico(df)

# Mostra il logo centrato
if os.path.exists(LOGO_FILE):
    st.image(LOGO_FILE, use_container_width=True)

st.markdown("<h1 style='text-align: center;'>🏆 card</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: gray;'>Resoconto Digitale Personale Giocatori • ZAMTEK SHOP</p>", unsafe_allow_html=True)

st.markdown("---")

# INTERFACCIA DI LOGIN PER IL GIOCATORE
st.subheader("🔑 Accesso Giocatore")
login_id = st.text_input("Inserisci la tua Email o ID Gioco:")
login_pass = st.text_input("Inserisci la tua Password personale:", type="password")

if login_id and login_pass:
    utente_filtrato = df[df['Email_ID'].str.lower() == login_id.lower()]
    
    if not utente_filtrato.empty:
        idx_cliente = utente_filtrato.index
        password_corretta = str(df.at[idx_cliente, 'Password_Utente'])
        
        if login_pass == password_corretta:
            st.success(f"🔓 Accesso effettuato! Benvenuto nella tua Area Personale, {df.at[idx_cliente, 'Nome']}!")
            st.markdown("---")
            
            # RICEVUTA PRESTAZIONI "SCONTRINO STYLE"
            st.markdown("### 📋 Il Tuo Profilo Personalizzato")
            livello_attuale = df.at[idx_cliente, 'Livello_Attuale']
            timbri_attuali = int(df.at[idx_cliente, 'Timbri_Mese'])
            livello_futuro = calcola_livello_futuro(timbri_attuali)
            
            st.code(f"""
==================================================
              ZAMTEK SHOP FIDELITY               
==================================================
 GIOCATORE:      {df.at[idx_cliente, 'Nome'].upper()} {df.at[idx_cliente, 'Cognome'].upper()}
 ID ACCOUNT:     {df.at[idx_cliente, 'Email_ID']}
--------------------------------------------------
 STATO ATTUALE ({mese_attuale_nome.upper()}):
 🔹 Livello Attivo:      {livello_attuale}
 🔹 Validità Sconti:     dal {data_inizio} al {data_fine}
--------------------------------------------------
 ANDAMENTO RACCOLTA ATTUALE:
 🔹 Timbri Accumulati:   {timbri_attuali} Timbri
 🚀 STATO MESE PROSSIMO ({mese_prossimo_nome.upper()}): {livello_futuro}
==================================================
            """, language="text")
            
            # 1. TABELLA RIASSUNTIVA SCONTI DI QUESTO MESE
            st.markdown(f"#### 🛍️ Tabella Sconti Disponibili Oggi per Te ({mese_attuale_nome})")
            
            dati_sconto_oggi = {
                "Categoria Prodotto": ["Carte Singole ≤ 30€", "Carte Singole > 30€", "Sealed Definiti (Bustine/Mazzi)"],
                "Il tuo Sconto Attivo": [
                    "7% di Sconto" if livello_attuale == "🥇 CHAMPION" else ("5% di Sconto" if livello_attuale == "🥈 CHALLENGER" else "Prezzo Pieno"),
                    "5% di Sconto" if livello_attuale in ["🥇 CHAMPION", "🥈 CHALLENGER"] else "Prezzo Pieno",
                    "5% di Sconto" if livello_attuale == "🥇 CHAMPION" else "Prezzo Pieno"
                ]
            }
            st.table(pd.DataFrame(dati_sconto_oggi))
            
            # 2. TABELLA RIASSUNTIVA SCONTI DEL MESE PROSSIMO
            st.markdown(f"#### 🚀 Tabella Sconti Disponibili Prossimo Mese ({mese_prossimo_nome})")
            st.caption(f"In base ai `{timbri_attuali}` timbri accumulati oggi, nel mese di {mese_prossimo_nome} avrai diritto a:")
            
            dati_sconto_prossimo = {
                "Categoria Prodotto": ["Carte Singole ≤ 30€", "Carte Singole > 30€", "Sealed Definiti (Bustine/Mazzi)"],
                "Sconto Futuro Garantito": [
                    "7% di Sconto" if livello_futuro == "🥇 CHAMPION" else ("5% di Sconto" if livello_futuro == "🥈 CHALLENGER" else "Prezzo Pieno"),
                    "5% di Sconto" if livello_futuro in ["🥇 CHAMPION", "🥈 CHALLENGER"] else "Prezzo Pieno",
                    "5% di Sconto" if livello_futuro == "🥇 CHAMPION" else "Prezzo Pieno"
                ]
            }
            st.table(pd.DataFrame(dati_sconto_prossimo))
            st.caption("⚠️ Gli sconti si applicano sul totale degli acquisti effettuati nella singola giornata. Esclusi Box display interi e preordini.")
            
            # GRAFICO VISIVO DI PROGRESSIONE VERSO IL MESE SUCCESSIVO
            st.markdown(f"#### 🪙 Grafico Avanzamento Livello per {mese_prossimo_nome}")
            
            dati_grafico = pd.DataFrame({
                'Traguardi': ['Livello Challenger', 'Livello Champion', 'I Tuoi Timbri'],
                'Timbri': [5, 10, timbri_attuali]
            })
            st.bar_chart(data=dati_grafico, x='Traguardi', y='Timbri', horizontal=True, color=["#ff4b4b"])
            
            if timbri_attuali < 5:
                mancanti_challenger = 5 - timbri_attuali
                st.warning(f"💡 Ti mancano ancora **{5 - timbri_attuali} timbri** entro fine mese per sbloccare il livello **Challenger** a {mese_prossimo_nome}!")
            elif timbri_attuali < 10:
                mancanti_champion = 10 - timbri_attuali
                st.info(f"🚀 Livello Challenger sicuro! Ti mancano **{10 - timbri_attuali} timbri** entro fine mese per fare l'upgrade a **Champion**!")
            else:
                st.success(f"🥇 Massimo Livello Raggiunto! Sei un Champion confermato anche per il mese di {mese_prossimo_nome}!")
                
        else:
            st.error("❌ Password errata per questo ID.")
    else:
        st.error("❌ ID o Email non trovato nel sistema.")

