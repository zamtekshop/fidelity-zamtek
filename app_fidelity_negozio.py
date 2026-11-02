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
                """,
                language="text",
            )

            # 1. TABELLA RIASSUNTIVA SCONTI DI QUESTO MESE
            st.markdown(
                f"#### 🛍️ Tabella Sconti Disponibili Oggi per Te ({mese_attuale_nome})"
            )

            dati_sconto_oggi = {
                "Categoria Prodotto": [
                    "Carte Singole ≤ 30€",
                    "Carte Singole > 30€",
                    "Sealed Definiti (Bustine/Mazzi)",
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
                    if livello_attuale in ["🥇 CHAMPION", "🥈 CHALLENGER"]
                    else "Prezzo Pieno",
                    "5% di Sconto"
                    if livello_attuale == "🥇 CHAMPION"
                    else "Prezzo Pieno",
                ],
            }
            st.table(pd.DataFrame(dati_sconto_oggi))

            # 2. TABELLA RIASSUNTIVA SCONTI DEL MESE PROSSIMO
            st.markdown(
                f"#### 🚀 Tabella Sconti Disponibili Prossimo Mese ({mese_prossimo_nome})"
            )
            st.caption(
                f"In base ai `{timbri_attuali}` timbri accumulati oggi, nel mese di {mese_prossimo_nome} avrai diritto a:"
            )

            dati_sconto_prossimo = {
                "Categoria Prodotto": [
                    "Carte Singole ≤ 30€",
                    "Carte Singole > 30€",
                    "Sealed Definiti (Bustine/Mazzi)",
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
                    if livello_futuro in ["🥇 CHAMPION", "🥈 CHALLENGER"]
                    else "Prezzo Pieno",
                    "5% di Sconto"
                    if livello_futuro == "🥇 CHAMPION"
                    else "Prezzo Pieno",
                ],
            }
            st.table(pd.DataFrame(dati_sconto_prossimo))
            st.caption(
                "⚠️ Gli sconti si applicano sul totale degli acquisti effettuati nella singola giornata. Esclusi Box display interi e preordini."
            )

            # GRAFICO VISIVO DI PROGRESSIONE VERSO IL MESE SUCCESSIVO
            st.markdown(
                f"#### 🪙 Grafico Avanzamento Livello per {mese_prossimo_nome}"
            )

            dati_grafico = pd.DataFrame(
                {
                    "Traguardi": [
                        "Livello Challenger",
                        "Livello Champion",
                        "I Tuoi Timbri",
                    ],
                    "Timbri": [5, 10, timbri_attuali],
                }
            )
            st.bar_chart(
                data=dati_grafico,
                x="Traguardi",
                y="Timbri",
                horizontal=True,
                color=["#ff4b4b"],
            )

            if timbri_attuali < 5:
                mancanti_challenger = 5 - timbri_attuali
                st.warning(
                    f"💡 Ti mancano ancora **{mancanti_challenger} timbri** entro fine mese per sbloccare il livello **Challenger** a {mese_prossimo_nome}!"
                )
            elif timbri_attuali < 10:
                mancanti_champion = 10 - timbri_attuali
                st.info(
                    f"🚀 Livello Challenger sicuro! Ti mancano **{mancanti_champion} timbri** entro fine mese per fare l'upgrade a **Champion**!"
                )
            else:
                st.success(
                    f"🥇 Massimo Livello Raggiunto! Sei un Champion confermato anche per il mese di {mese_prossimo_nome}!"
                )

        else:
            st.error("❌ Password errata per questo ID.")
    else:
        st.error("❌ ID o Email non trovato nel sistema.")
