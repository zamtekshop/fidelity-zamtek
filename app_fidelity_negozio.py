import os
import calendar
from datetime import datetime

import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURAZIONE
# ============================================================

st.set_page_config(
    page_title="ZAMTEK SHOP - Fidelity",
    page_icon="🏆",
    layout="centered",
)

DB_FILE = "fidelity_database.csv"
LOG_FILE = "fidelity_cronologia.csv"
LOGO_FILE = "logo.png"

# Password dell'area amministratore/cassa
PASSWORD_CASSA = "zamtek2026"

MESI_ITALIANI = [
    "",
    "Gennaio",
    "Febbraio",
    "Marzo",
    "Aprile",
    "Maggio",
    "Giugno",
    "Luglio",
    "Agosto",
    "Settembre",
    "Ottobre",
    "Novembre",
    "Dicembre",
]

COLONNE_DB = [
    "Nome",
    "Cognome",
    "Email_ID",
    "Password_Utente",
    "Timbri_Mese",
    "Livello_Attuale",
    "Ultimo_Aggiornamento_Mese",
]

COLONNE_LOG = [
    "Data/Ora",
    "Giocatore",
    "Operazione",
    "Variazione Timbri",
]


# ============================================================
# FUNZIONI GENERALI
# ============================================================

def mese_corrente_id():
    return datetime.now().strftime("%Y-%m")


def ottieni_date_validita():
    ora = datetime.now()
    anno = ora.year
    mese = ora.month

    # calendar.monthrange restituisce una tupla:
    # [0] = giorno della settimana; [1] = ultimo giorno del mese.
    ultimo_giorno = calendar.monthrange(anno, mese)[1]

    data_inizio = f"01/{mese:02d}/{anno}"
    data_fine = f"{ultimo_giorno:02d}/{mese:02d}/{anno}"

    nome_mese_corrente = MESI_ITALIANI[mese]
    mese_successivo = 1 if mese == 12 else mese + 1
    nome_mese_successivo = MESI_ITALIANI[mese_successivo]

    return (
        data_inizio,
        data_fine,
        nome_mese_corrente,
        nome_mese_successivo,
    )


def calcola_livello_futuro(timbri):
    timbri = int(timbri)

    if timbri >= 10:
        return "🥇 CHAMPION"
