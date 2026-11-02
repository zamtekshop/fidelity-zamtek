import streamlit as st
import pandas as pd
import os
from datetime import datetime
import calendar

# Configurazione della pagina ottimizzata per Mobile e Desktop
st.set_page_config(page_title="ZAMTEK SHOP - Fidelity", layout="centered")

DB_FILE = "fidelity_database.csv"
LOGO_FILE = "logo.png"
PASSWORD_CASSA = "zamtek2026"  # Password segreta per te alla cassa

# Funzione per calcolare le date di validità in italiano
def ottieni_date_validita():
    ora = datetime.now()
    anno_corrente = ora.year
    mese_corrente = ora.month
    
    ultimo_giorno = calendar.monthrange(anno_corrente, mese_corrente)[1]
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
            df.at[idx, 'Livello_Attuale'] = calcola_livello_futuro(timbri)
            df.at[idx, 'Timbri_Mese'] = 0  
            df.at[idx, 'Ultimo_Aggiornamento_Mese'] = mese_corrente
            modificato = True
    if modificato:
        salva_db(df)
    return df

# Inizializzazione database
df = carica_db()
df = controllo_cambio_mese_automatico(df)

# Mostra il logo centrato
if os.path.exists(LOGO_FILE):
    st.image(LOGO_FILE, use_container_width=True)

st.markdown("<h1 style='text-align: center;'>🏆 ZAMTEK SHOP Fidelity</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: gray;'>Resoconto Digitale Personale Giocatori • Aggiornato in Tempo Reale</p>", unsafe_allow_html=True)

st.markdown("---")

# INTERFACCIA DI LOGIN PER IL GIOCATORE
st.subheader("🔑 Accesso Giocatore")
login_id = st.text_input("Inserisci la tua Email o ID Gioco:")
login_pass = st.text_input("Inserisci la tua Password personale:", type="password")

if login_id and login_pass:
    utente_filtrato = df[df['Email_ID'].str.lower() == login_id.lower()]
    
    if not utente_filtrato.empty:
        idx_cliente = utente_filtrato.index[0]
        password_corretta = str(df.at[idx_cliente, 'Password_Utente'])
        
        if login_pass == password_corretta:
            st.success(f"🔓 Accesso effettuato! Benvenuto nella tua Area Personale, {df.at[idx_cliente, 'Nome']}!")
            st.markdown("---")
            
            # 1. RICEVUTA PRESTAZIONI "SCONTRINO STYLE"
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
            
            # 2. TABELLA RIASSUNTIVA SCONTI DEL GIORNO
            st.markdown("#### 🛍️ Tabella Sconti Disponibili Oggi per Te")
            
            dati_sconto_tabella = {
                "Categoria Prodotto": ["Carte Singole ≤ 30€", "Carte Singole > 30€", "Sealed Definiti (Bustine/Mazzi)"],
                "Il tuo Sconto Attivo": [
                    "7% di Sconto" if livello_attuale == "🥇 CHAMPION" else ("5% di Sconto" if livello_attuale == "🥈 CHALLENGER" else "Prezzo Pieno"),
                    "5% di Sconto" if livello_attuale in ["🥇 CHAMPION", "🥈 CHALLENGER"] else "Prezzo Pieno",
                    "5% di Sconto" if livello_attuale == "🥇 CHAMPION" else "Prezzo Pieno"
                ]
            }
            st.table(pd.DataFrame(dati_sconto_tabella))
            st.caption("⚠️ Gli sconti si applicano sul totale degli acquisti effettuati nella singola giornata. Esclusi Box display interi e preordini.")
            
            # 3. GRAFICO VISIVO DI PROGRESSIONE VERSO IL MESE SUCCESSIVO
            st.markdown(f"#### 🪙 Grafico Avanzamento Livello per {mese_prossimo_nome}")
            
            # Creazione di un grafico a barre orizzontali pulito
            dati_grafico = pd.DataFrame({
                'Traguardi': ['Livello Challenger', 'Livello Champion', 'I Tuoi Timbri'],
                'Timbri': [5, 10, timbri_attuali]
            })
            st.bar_chart(data=dati_grafico, x='Traguardi', y='Timbri', horizontal=True, color=["#ff4b4b"])
            
            if timbri_attuali < 5:
                st.warning(f"💡 Ti mancano ancora **{5 - timbri_attuali} timbri** entro fine mese per sbloccare il livello **Challenger** a {mese_prossimo_nome}!")
            elif timbri_attuali < 10:
                st.info(f"🚀 Livello Challenger sicuro! Ti mancano **{10 - timbri_attuali} timbri** entro fine mese per fare l'upgrade a **Champion**!")
            else:
                st.success(f"🥇 Massimo Livello Raggiunto! Sei un Champion confermato anche per il mese di {mese_prossimo_nome}!")
                
        else:
            st.error("❌ Password errata per questo ID.")
    else:
        st.error("❌ ID o Email non trovato nel sistema.")

# AREA RISERVATA ALLA CASSA
st.markdown("---")
with st.expander("🔒 Area Riservata Staff Zamtek (Pannello di Controllo & Registro Completo)"):
    pass_inserita = st.text_input("Inserisci la Password di Cassa:", type="password", key="pass_staff")
    
    if pass_inserita == PASSWORD_CASSA:
        st.success("🔓 Accesso Amministratore Concesso")
        tab1, tab2, tab3 = st.tabs(["⚙️ Assegna Timbri Giocatore", "📊 Tabellone Generale Sconti", "👤 Registra Nuovo Giocatore"])
        
        with tab1:
            if not df.empty:
                df['Nome_Completo'] = df['Nome'] + " " + df['Cognome'] + " (" + df['Email_ID'] + ")"
                scelta_cassa = st.selectbox("Seleziona il giocatore al bancone:", df['Nome_Completo'].values, key="cassa_select")
                idx_cassa = df[df['Nome_Completo'] == scelta_cassa].index[0]
                
                st.write(f"ℹ️ **Stato attuale cliente:** Livello di questo mese: `{df.at[idx_cassa, 'Livello_Attuale']}` | Timbri correnti raccolti: `{df.at[idx_cassa, 'Timbri_Mese']}`")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("🕹️ +1 Torneo Serale"):
                        df.at[idx_cassa, 'Timbri_Mese'] += 1
                        df.at[idx_cassa, 'Ultimo_Aggiornamento_Mese'] = datetime.now().strftime("%Y-%m")
                        salva_db(df.drop(columns=['Nome_Completo'], errors='ignore'))
                        st.toast("+1 Timbro Torneo assegnato!")
                        st.rerun()
                with c2:
                    if st.button("🛍️ +1 Spesa ≥ 50€ Netta"):
                        df.at[idx_cassa, 'Timbri_Mese'] += 1
                        df.at[idx_cassa, 'Ultimo_Aggiornamento_Mese'] = datetime.now().strftime("%Y-%m")
                        salva_db(df.drop(columns=['Nome_Completo'], errors='ignore'))
