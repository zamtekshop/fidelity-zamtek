import streamlit as st
import pandas as pd
import os
from datetime import datetime
import calendar

# CONFIGURAZIONE PAGINA
st.set_page_config(
    page_title="ZAMTEK SHOP - Fidelity",
    layout="centered"
)

DB_FILE = "fidelity_database.csv"
LOG_FILE = "fidelity_cronologia.csv"
LOGO_FILE = "logo.png"
PASSWORD_CASSA = "zamtek2026"

MESI_ITALIANI = [
    "",
    "Gennaio", "Febbraio", "Marzo", "Aprile",
    "Maggio", "Giugno", "Luglio", "Agosto",
    "Settembre", "Ottobre", "Novembre", "Dicembre"
]


# CALCOLO DATE DI VALIDITA'
def ottieni_date_validita():

    ora = datetime.now()
    anno_corrente = ora.year
    mese_corrente = ora.month

    # CORREZIONE: estraiamo il secondo elemento della tupla
    ultimo_giorno = calendar.monthrange(
        anno_corrente,
        mese_corrente
    )[1]

    data_inizio_attivita = (
        f"01/{mese_corrente:02d}/{anno_corrente}"
    )

    data_fine_attivita = (
        f"{ultimo_giorno:02d}/{mese_corrente:02d}/{anno_corrente}"
    )

    nome_mese_corrente = MESI_ITALIANI[mese_corrente]

    if mese_corrente == 12:
        mese_succ = 1
    else:
        mese_succ = mese_corrente + 1

    nome_mese_succ = MESI_ITALIANI[mese_succ]

    return (
        data_inizio_attivita,
        data_fine_attivita,
        nome_mese_corrente,
        nome_mese_succ
    )


data_inizio, data_fine, mese_attuale_nome, mese_prossimo_nome = (
    ottieni_date_validita()
)


# CALCOLO LIVELLO FUTURO
def calcola_livello_futuro(timbri):

    timbri = int(timbri)

    if timbri >= 10:
        return "🥇 CHAMPION"

    elif timbri >= 5:
        return "🥈 CHALLENGER"

    else:
        return "🥉 Nessun Livello"


# DESCRIZIONE SCONTI
def descrivi_sconto(livello):

    if livello == "🥇 CHAMPION":
        return "7% Singole ≤30€ | 5% Singole >30€ | 5% Sealed (Bustine/Mazzi)"

    elif livello == "🥈 CHALLENGER":
        return "5% su Tutte le Carte Singole | No Sealed"

    else:
        return "Prezzo pieno su tutto"


# REGISTRAZIONE CRONOLOGIA
def scrivi_log(giocatore, operazione, timbri_variati):

    timestamp = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    nuovo_log = {
        "Data/Ora": timestamp,
        "Giocatore": giocatore,
        "Operazione": operazione,
        "Variazione Timbri": timbri_variati
    }

    if os.path.exists(LOG_FILE):

        log_df = pd.read_csv(LOG_FILE)

        log_df = pd.concat(
            [pd.DataFrame([nuovo_log]), log_df],
            ignore_index=True
        )

    else:
        log_df = pd.DataFrame([nuovo_log])

    log_df.to_csv(LOG_FILE, index=False)


# CARICAMENTO DATABASE
def carica_db():

    if os.path.exists(DB_FILE):

        df = pd.read_csv(DB_FILE)

        if "Timbri_Mese" not in df.columns:
            df["Timbri_Mese"] = 0

        if "Livello_Attuale" not in df.columns:
            df["Livello_Attuale"] = "🥉 Nessun Livello"

        if "Ultimo_Aggiornamento_Mese" not in df.columns:
            df["Ultimo_Aggiornamento_Mese"] = (
                datetime.now().strftime("%Y-%m")
            )

        if "Password_Utente" not in df.columns:
            df["Password_Utente"] = (
                df["Nome"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str[:3] + "123"
            )

        df["Timbri_Mese"] = pd.to_numeric(
            df["Timbri_Mese"],
            errors="coerce"
        ).fillna(0).astype(int)

        return df

    else:

        return pd.DataFrame(
            columns=[
                "Nome",
                "Cognome",
                "Email_ID",
                "Password_Utente",
                "Timbri_Mese",
                "Livello_Attuale",
                "Ultimo_Aggiornamento_Mese"
            ]
        )


# SALVATAGGIO DATABASE
def salva_db(df):

    df.to_csv(DB_FILE, index=False)


# CONTROLLO CAMBIO MESE AUTOMATICO
def controllo_cambio_mese_automatico(df):

    if df.empty:
        return df

    mese_corrente = datetime.now().strftime("%Y-%m")

    modificato = False

    for idx, row in df.iterrows():

        if str(row["Ultimo_Aggiornamento_Mese"]) != mese_corrente:

            timbri = int(row["Timbri_Mese"])

            nuovo_livello = calcola_livello_futuro(timbri)

            df.at[idx, "Livello_Attuale"] = nuovo_livello

            df.at[idx, "Timbri_Mese"] = 0

            df.at[idx, "Ultimo_Aggiornamento_Mese"] = mese_corrente

            modificato = True

            scrivi_log(
                f"{row['Nome']} {row['Cognome']}",
                f"Reset Mensile Autom. (Nuovo Livello: {nuovo_livello} basato su {timbri} timbri)",
                0
            )

    if modificato:
        salva_db(df)

    return df


# INIZIALIZZAZIONE DATABASE
df = carica_db()

df = controllo_cambio_mese_automatico(df)


# LOGO
if os.path.exists(LOGO_FILE):

    st.image(
        LOGO_FILE,
        use_container_width=True
    )


# INTESTAZIONE
st.markdown(
    "<h1 style='text-align: center;'>🏆 card</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center; color: gray;'>Resoconto Digitale Personale Giocatori • ZAMTEK SHOP</p>",
    unsafe_allow_html=True
)

st.markdown("---")


# LOGIN GIOCATORE
st.subheader("🔑 Accesso Giocatore")

login_id = st.text_input(
    "Inserisci la tua Email o ID Gioco:"
)

login_pass = st.text_input(
    "Inserisci la tua Password personale:",
    type="password"
)


if login_id and login_pass:

    utente_filtrato = df[
        df["Email_ID"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.casefold()
        == login_id.strip().casefold()
    ]

    if not utente_filtrato.empty:

        # CORREZIONE INDICE PANDAS
        idx_cliente = utente_filtrato.index[0]

        password_corretta = str(
            df.at[idx_cliente, "Password_Utente"]
        )

        if login_pass == password_corretta:

            nome_giocatore = str(
                df.at[idx_cliente, "Nome"]
            )

            cognome_giocatore = str(
                df.at[idx_cliente, "Cognome"]
            )

            livello_attuale = str(
                df.at[idx_cliente, "Livello_Attuale"]
            )

            timbri_attuali = int(
                df.at[idx_cliente, "Timbri_Mese"]
            )

            livello_futuro = calcola_livello_futuro(
                timbri_attuali
            )

            st.success(
                f"🔓 Accesso effettuato! Benvenuto nella tua Area Personale, {nome_giocatore}!"
            )

            st.markdown("---")

            # PROFILO PERSONALIZZATO
            st.markdown(
                "### 📋 Il Tuo Profilo Personalizzato"
            )

            # IMPORTANTE:
            # Tutto il testo dello scontrino è racchiuso
            # correttamente tra virgolette triple.

            scontrino = f"""
==================================================
              ZAMTEK SHOP FIDELITY
==================================================
 GIOCATORE:      {nome_giocatore.upper()} {cognome_giocatore.upper()}
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
"""

            st.code(
                scontrino,
                language="text"
            )


            # TABELLA SCONTI MESE ATTUALE
            st.markdown(
                f"#### 🛍️ Tabella Sconti Disponibili Oggi per Te ({mese_attuale_nome})"
            )

            dati_sconto_oggi = {

                "Categoria Prodotto": [
                    "Carte Singole ≤ 30€",
                    "Carte Singole > 30€",
                    "Sealed Definiti (Bustine/Mazzi)"
                ],

                "Il tuo Sconto Attivo": [

                    "7% di Sconto"
                    if livello_attuale == "🥇 CHAMPION"
                    else (
                        "5% di Sconto"
                        if livello_attuale == "🥈 CHALLENGER"
                        else "Prezzo Pieno"
                    ),

                    "5% di Sconto"
                    if livello_attuale in [
                        "🥇 CHAMPION",
                        "🥈 CHALLENGER"
                    ]
                    else "Prezzo Pieno",

                    "5% di Sconto"
                    if livello_attuale == "🥇 CHAMPION"
                    else "Prezzo Pieno"
                ]
            }

            st.table(
                pd.DataFrame(dati_sconto_oggi)
            )


            # TABELLA SCONTI MESE PROSSIMO
            st.markdown(
                f"#### 🚀 Tabella Sconti Disponibili Prossimo Mese ({mese_prossimo_nome})"
            )

            st.caption(
                f"In base ai {timbri_attuali} timbri accumulati oggi, nel mese di {mese_prossimo_nome} avrai diritto a:"
            )

            dati_sconto_prossimo = {

                "Categoria Prodotto": [
                    "Carte Singole ≤ 30€",
                    "Carte Singole > 30€",
                    "Sealed Definiti (Bustine/Mazzi)"
                ],

                "Sconto Futuro Garantito": [

                    "7% di Sconto"
                    if livello_futuro == "🥇 CHAMPION"
                    else (
                        "5% di Sconto"
                        if livello_futuro == "🥈 CHALLENGER"
                        else "Prezzo Pieno"
                    ),

                    "5% di Sconto"
                    if livello_futuro in [
                        "🥇 CHAMPION",
                        "🥈 CHALLENGER"
                    ]
                    else "Prezzo Pieno",

                    "5% di Sconto"
                    if livello_futuro == "🥇 CHAMPION"
                    else "Prezzo Pieno"
                ]
            }

            st.table(
                pd.DataFrame(dati_sconto_prossimo)
            )

            st.caption(
                "⚠️ Gli sconti si applicano sul totale degli acquisti effettuati nella singola giornata. Esclusi Box display interi e preordini."
            )


            # GRAFICO AVANZAMENTO
            st.markdown(
                f"#### 🪙 Grafico Avanzamento Livello per {mese_prossimo_nome}"
            )

            dati_grafico = pd.DataFrame({

                "Traguardi": [
                    "Livello Challenger",
                    "Livello Champion",
                    "I Tuoi Timbri"
                ],

                "Timbri": [
                    5,
                    10,
                    timbri_attuali
                ]
            })

            st.bar_chart(
                data=dati_grafico,
                x="Traguardi",
                y="Timbri",
                horizontal=True,
                color=["#ff4b4b"]
            )


            # MESSAGGI PROGRESSIONE
            if timbri_attuali < 5:

                mancanti_challenger = 5 - timbri_attuali

                st.warning(
                    f"💡 Ti mancano ancora {mancanti_challenger} timbri entro fine mese per sbloccare il livello Challenger a {mese_prossimo_nome}!"
                )

            elif timbri_attuali < 10:

                mancanti_champion = 10 - timbri_attuali

                st.info(
                    f"🚀 Livello Challenger sicuro! Ti mancano {mancanti_champion} timbri entro fine mese per fare l'upgrade a Champion!"
                )

            else:

                st.success(
                    f"🥇 Massimo Livello Raggiunto! Sei un Champion confermato anche per il mese di {mese_prossimo_nome}!"
                )

        else:

            st.error(
                "❌ Password errata per questo ID."
            )

    else:

        st.error(
            "❌ ID o Email non trovato nel sistema."
        )
