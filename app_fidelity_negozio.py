import streamlit as st
import pandas as pd
import os
from datetime import datetime
import calendar

# Configurazione della pagina ottimizzata per Mobile
st.set_page_config(page_title="ZAMTEK SHOP - Fidelity", layout="centered")

DB_FILE = "fidelity_database.csv"
LOGO_FILE = "logo.png"
PASSWORD_CASSA = "zamtek2026"  # Password segreta per te alla cassa

# Funzione per calcolare le date di validità in italiano
def ottieni_date_validita():
    ora = datetime.now()
    anno_corrente = ora.year
    mese_corrente = ora.month
    
    # Mese corrente (Utilizzo Sconti)
    ultimo_giorno = calendar.monthrange(anno_corrente, mese_corrente)[1]
    data_inizio_attivita = f"01/{mese_corrente:02d}/{anno_corrente}"
    data_fine_attivita = f"{ultimo_giorno:02d}/{mese_corrente:02d}/{anno_corrente}"
    nome_mese_corrente = calendar.month_name[mese_corrente].capitalize()
    
    # Mese successivo (Accumulo Timbri)
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
        pass # Fallback se il sistema non ha la lingua installata

data_inizio, data_fine, mese_attuale_nome, mese_prossimo_nome = ottieni_date_validita()

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
            if timbri >= 10:
                nuovo_livello = "🥇 CHAMPION"
            elif timbri >= 5:
                nuovo_livello = "🥈 CHALLENGER"
            else:
                nuovo_livello = "🥉 Nessun Livello"
            df.at[idx, 'Livello_Attuale'] = nuovo_livello
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
st.markdown(f"<p style='text-align: center; color: gray;'>Periodo di Validità Sconti Attuali: <b>{data_inizio}</b> fino al <b>{data_fine}</b></p>", unsafe_allow_html=True)

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
            st.success(f"🔓 Accesso effettuato! Benvenuto, {df.at[idx_cliente, 'Nome']} {df.at[idx_cliente, 'Cognome']}")
            st.markdown("---")
            
            # RESOCONTO DETTAGLIATO PER IL CLIENTE
            st.markdown("### 📊 Il tuo Riepilogo Fidelity")
            st.info(f"""
            * **Il tuo Livello Attuale:** {df.at[idx_cliente, 'Livello_Attuale']}
            * **Periodo utilizzo sconti:** Valido dal **{data_inizio}** al **{data_fine}** (Mese di {mese_attuale_nome})
            * **Timbri accumulati in questo mese:** `{df.at[idx_cliente, 'Timbri_Mese']}` timbri inseriti.
            * **Obiettivo:** I timbri che raccogli ora determineranno lo sconto per il mese di **{mese_prossimo_nome}**.
            """)
            
            # VISUALIZZAZIONE SCONTI DISPONIBILI
            st.markdown("#### 🛍️ Gli sconti a tua disposizione OGGI alla cassa:")
            livello = df.at[idx_cliente, 'Livello_Attuale']
            if livello == "🥈 CHALLENGER":
                st.warning(f"""
                **🥈 AGEVOLAZIONI LIVELLO CHALLENGER (Valido oggi per scontrino unico giornaliero):**
                * 🔮 **Carte Singole:** **5% di SCONTO** su tutte le carte (sia sotto che sopra i 30€).
                * 📦 **Prodotti Sealed (Sigillati):** Prezzo pieno (Nessuno sconto).
                * *Esclusioni:* Box Display interi, Iscrizioni tornei, Preordini, Accessori.
                """)
            elif livello == "🥇 CHAMPION":
                st.success(f"""
                **🥇 AGEVOLAZIONI LIVELLO CHAMPION (Valido oggi per scontrino unico giornaliero):**
                * 🔮 **Carte Singole FINO a 30€:** **7% di SCONTO**
                * 💎 **Carte Singole OLTRE i 30€:** **5% di SCONTO**
                * 📦 **Prodotti Sealed Selezionati:** **5% di SCONTO** applicabile esclusivamente su: *Bustine sfuse, Mazzi Commander, Mazzi Starter e Bundle*.
                * *Esclusioni:* Box Display interi (sigillati), Iscrizioni tornei, Preordini, Accessori.
                """)
            else:
                st.error("❌ **NESSUN LIVELLO ATTIVO QUESTO MESE:** Paghi il prezzo pieno su tutti i prodotti. Partecipa ai tornei serali o effettua acquisti per sbloccare i tuoi sconti per il mese prossimo!")
                
            # BARRA DI AVANZAMENTO GRAFICA
            st.markdown(f"#### 🪙 Il tuo percorso accumulo nel mese di {mese_attuale_nome}:")
            timbri_attuali = int(df.at[idx_cliente, 'Timbri_Mese'])
            
            if timbri_attuali < 5:
                mancanti_challenger = 5 - timbri_attuali
                st.write(f"🔹 Progressi per livello **Challenger**: `{timbri_attuali} / 5` timbri.")
                st.progress(timbri_attuali / 5)
                st.write(f"💡 *Raggiungi quota 5 timbri entro il {data_fine} per sbloccare il 5% sulle singole a {mese_prossimo_nome}!*")
            elif timbri_attuali < 10:
                mancanti_champion = 10 - timbri_attuali
                st.write(f"🥈 **Sei Challenger!** Progressi verso il livello **Champion**: `{timbri_attuali} / 10` timbri.")
                progresso_relativo = (timbri_attuali - 5) / 5
                st.progress(progresso_relativo)
                st.write(f"🚀 *Raggiungi quota 10 timbri entro il {data_fine} per fare il grande salto a Champion (Sconti su Singole + Sealed) a {mese_prossimo_nome}!*")
            else:
                st.write(f"🥇 **Grandioso! Livello Champion già confermato e bloccato per il mese di {mese_prossimo_nome}!**")
                st.progress(1.0)
        else:
            st.error("❌ Password errata per questo ID.")
    else:
        st.error("❌ ID o Email non trovato nel sistema.")

# AREA RISERVATA ALLA CASSA (COMPRESA LA TABELLA DETTAGLIATA CON TUTTE LE INFO)
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
                idx_cassa = df[df['Nome_Completo'] == scelta_cassa].index
                
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
                        st.toast("+1 Timbro Spesa assegnato!")
