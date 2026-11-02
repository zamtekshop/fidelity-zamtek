import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configurazione della pagina ottimizzata per Mobile
st.set_page_config(page_title="ZAMTEK SHOP - Fidelity", layout="centered")

DB_FILE = "fidelity_database.csv"
LOGO_FILE = "logo.png"
PASSWORD_CASSA = "zamtek2026"  # Password segreta per te alla cassa

# Funzione per caricare il database
def carica_db():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # Controllo e standardizzazione delle colonne necessarie
        if 'Timbri_Mese' not in df.columns:
            df['Timbri_Mese'] = 0
        if 'Livello_Attuale' not in df.columns:
            df['Livello_Attuale'] = "🥉 Nessun Livello"
        if 'Ultimo_Aggiornamento_Mese' not in df.columns:
            df['Ultimo_Aggiornamento_Mese'] = datetime.now().strftime("%Y-%m")
        if 'Password_Utente' not in df.columns:
            # Se mancano le password nel vecchio DB, genera una password di default basata sul nome
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
st.markdown("<p style='text-align: center; color: gray;'>Accedi per verificare il tuo livello personale</p>", unsafe_allow_html=True)


st.markdown("---")

# INTERFACCIA DI LOGIN PER IL GIOCATORE
st.subheader("🔑 Accesso Giocatore")
login_id = st.text_input("Inserisci la tua Email o ID Gioco:")
login_pass = st.text_input("Inserisci la tua Password personale:", type="password")

if login_id and login_pass:
    # Cerchiamo l'utente nel database
    utente_filtrato = df[df['Email_ID'].str.lower() == login_id.lower()]
    
    if not utente_filtrato.empty:
        idx_cliente = utente_filtrato.index[0]
        password_corretta = str(df.at[idx_cliente, 'Password_Utente'])
        
        if login_pass == password_corretta:
            st.success(f"🔓 Accesso effettuato! Benvenuto, {df.at[idx_cliente, 'Nome']} {df.at[idx_cliente, 'Cognome']}")
            st.markdown("---")
            
            # 1. VISUALIZZAZIONE ESCLUSIVA DEL PROFILO PERSONALE
            st.markdown("#### 🛍️ I tuoi sconti validi OGGI in cassa:")
            livello = df.at[idx_cliente, 'Livello_Attuale']
            if livello == "🥈 CHALLENGER":
                st.warning("""
                **🥈 LIVELLO CHALLENGER ATTIVO**
                * 🔮 **Carte Singole:** **5% di SCONTO** giornaliero su tutte le carte.
                * 📦 **Prodotti Sealed:** Prezzo pieno.
                """)
            elif livello == "🥇 CHAMPION":
                st.success("""
                **🥇 LIVELLO CHAMPION ATTIVO**
                * 🔮 **Carte Singole FINO a 30€:** **7% di SCONTO** giornaliero.
                * 💎 **Carte Singole OLTRE i 30€:** **5% di SCONTO** giornaliero.
                * 📦 **Prodotti Sealed Selezionati:** **5% di SCONTO** giornaliero (Bustine sfuse, Mazzi, Bundle).
                """)
            else:
                st.info("🔹 **NESSUN LIVELLO ATTIVO:** Partecipa ai tornei o fai acquisti per sbloccare i prossimi sconti!")
                
            # 2. BARRA DI AVANZAMENTO GRAFICA
            st.markdown("#### 🪙 I tuoi progressi questo mese:")
            timbri_attuali = int(df.at[idx_cliente, 'Timbri_Mese'])
            
            if timbri_attuali < 5:
                mancanti_challenger = 5 - timbri_attuali
                st.write(f"🔹 Timbri attuali: `{timbri_attuali} / 5` per il livello **Challenger**.")
                st.progress(timbri_attuali / 5)
                st.write(f"💡 *Ti mancano {mancanti_challenger} timbri questo mese per diventare Challenger il mese prossimo!*")
            elif timbri_attuali < 10:
                mancanti_champion = 10 - timbri_attuali
                st.write(f"🥈 **Sei Challenger!** Progressi verso il livello **Champion**: `{timbri_attuali} / 10`")
                progresso_relativo = (timbri_attuali - 5) / 5
                st.progress(progresso_relativo)
                st.write(f"🚀 *Ti mancano {mancanti_champion} timbri questo mese per fare l'upgrade a Champion il mese prossimo!*")
            else:
                st.write(f"🥇 **Grandioso! Livello Champion confermato per il prossimo mese!**")
                st.progress(1.0)
        else:
            st.error("❌ Password errata per questo ID.")
    else:
        st.error("❌ ID o Email non trovato nel sistema.")

# AREA RISERVATA ALLA CASSA (GESTIONE STAFF)
st.markdown("---")
with st.expander("🔒 Area Riservata Staff Zamtek (Aggiunta Timbri / Nuovi Clienti)"):
    pass_inserita = st.text_input("Inserisci la Password di Cassa:", type="password", key="pass_staff")
    
    if pass_inserita == PASSWORD_CASSA:
        st.success("🔓 Accesso Cassa Consentito")
        tab1, tab2 = st.tabs(["⚙️ Gestione Timbri Giocatore", "👤 Registra Nuovo Giocatore"])
        
        with tab1:
            if not df.empty:
                df['Nome_Completo'] = df['Nome'] + " " + df['Cognome'] + " (" + df['Email_ID'] + ")"
                scelta_cassa = st.selectbox("Seleziona il giocatore al bancone:", df['Nome_Completo'].values, key="cassa_select")
                idx_cassa = df[df['Nome_Completo'] == scelta_cassa].index[0]
                
                st.write(f"Password attuale del cliente da comunicargli: `{df.at[idx_cassa, 'Password_Utente']}`")
                
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
                        st.rerun()
                with c3:
                    if st.button("📦 +4 Acquisto Box Display"):
                        df.at[idx_cassa, 'Timbri_Mese'] += 4
                        df.at[idx_cassa, 'Ultimo_Aggiornamento_Mese'] = datetime.now().strftime("%Y-%m")
                        salva_db(df.drop(columns=['Nome_Completo'], errors='ignore'))
                        st.toast("+4 Timbri Box assegnati!")
                        st.rerun()
        
        with tab2:
            nuovo_nome = st.text_input("Nome", key="reg_nome")
            nuovo_cognome = st.text_input("Cognome", key="reg_cogn")
            nuovo_id = st.text_input("Email o ID Gioco (Melee / Riftbound)", key="reg_id")
            
            if st.button("Salva Nuovo Giocatore"):
                if nuovo_nome and nuovo_cognome and nuovo_id:
                    if nuovo_id.lower() in df['Email_ID'].str.lower().values:
                        st.error("Questo ID è già registrato!")
                    else:
                        # Generazione automatica password iniziale (3 lettere nome + 3 lettere cognome)
                        pass_automatica = (nuovo_nome.strip().lower()[:3] + nuovo_cognome.strip().lower()[:3]).replace(" ", "")
                        if len(pass_automatica) < 4:
                            pass_automatica += "123"
                            
                        nuovo_utente = {
                            "Nome": nuovo_nome.strip(),
                            "Cognome": nuovo_cognome.strip(),
                            "Email_ID": nuovo_id.strip(),
                            "Password_Utente": pass_automatica,
                            "Timbri_Mese": 0,
                            "Livello_Attuale": "🥉 Nessun Livello",
                            "Ultimo_Aggiornamento_Mese": datetime.now().strftime("%Y-%m")
                        }
                        
                        df_salva = df.drop(columns=['Nome_Completo'], errors='ignore')
                        df_nuovo = pd.concat([df_salva, pd.DataFrame([nuovo_utente])], ignore_index=True)
                        salva_db(df_nuovo)
                        st.success(f"Giocatore registrato! Password temporanea: {pass_automatica}")
                        st.rerun()
                else:
                    st.warning("Riempi tutti i campi.")
