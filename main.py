from data_reader import naviga_e_scarica_dati
from template_generator import crea_locandina_v2

# --- CONFIGURAZIONE UTENTE ---
# Modifica questi parametri prima di lanciare il programma
GIORNATA = 2           # Inserisci il numero della giornata
RITORNO = True         # False = Andata, True = Ritorno

def main(serie, squadra, giornata, ritorno, skip_casa=[], skip_ospiti=[]):
    print("==========================================")
    print(f"🏓  GENERATORE AUTOMATICO LOCANDINE FITET")
    print("==========================================")
    print(f"Squadra: {squadra}")
    print(f"Campionato: {serie} - Giornata {giornata} ({'Ritorno' if ritorno else 'Andata'})")
    print("------------------------------------------")

    # 1. AVVIO LO SCRAPER
    print("⏳ 1. Avvio il browser e cerco i risultati...")
    try:
        # Nota: Convertiamo GIORNATA in int per sicurezza
        dati_partita = naviga_e_scarica_dati(serie, squadra, int(giornata), is_ritorno=ritorno, skip_casa=skip_casa, skip_ospiti=skip_ospiti)
    except Exception as e:
        print(f"❌ Errore imprevisto durante lo scaricamento: {e}")
        dati_partita = None

    # 2. CONTROLLO E GENERAZIONE GRAFICA
    if dati_partita:
        print("\n✅ Dati scaricati con successo!")
        print(f"   Match: {dati_partita['nome_team_casa']} vs {dati_partita['nome_team_ospiti']}")
        print(f"   Risultato: {dati_partita['punteggio_casa']} - {dati_partita['punteggio_ospiti']}")
        
        print("\n🎨 2. Creazione della locandina in corso...")
        try:
            crea_locandina_v2(
                punteggio_casa=dati_partita["punteggio_casa"],
                punteggio_ospiti=dati_partita["punteggio_ospiti"],
                nome_team_casa=dati_partita["nome_team_casa"],
                nome_team_ospiti=dati_partita["nome_team_ospiti"],
                nome_serie=dati_partita["nome_serie"],
                giocatori_casa=dati_partita["giocatori_casa"],
                giocatori_ospiti=dati_partita["giocatori_ospiti"],
                risultati_match=dati_partita["risultati_match"]
            )
            print("\n🎉 TUTTO FATTO! Controlla la cartella 'output'.")
        except Exception as e:
             print(f"❌ Errore durante la generazione grafica: {e}")
    else:
        print("\n❌ ERRORE: Non sono stati trovati dati validi per questa giornata.")
        print("   Suggerimenti:")
        print("   - Controlla che il risultato sia già stato caricato sul portale.")
        print("   - Verifica se è una giornata di Andata (RITORNO = False) o Ritorno.")
        print("   - Controlla il numero della giornata.")

if __name__ == "__main__":
    nomi_squadre = [
        "TT ACLI C2 LUGO",
        "TT ACLI D1 JUNIOR RAVENNA",
        "TT ACLI D1 ALFA LUGO",
        "TT ACLI D1 BETA LUGO",
        "TT ACLI D1 OVER LUGO",
        "TT ACLI D2 LUGO",
        "TT ACLI D3 JUNIOR LUGO",
        "TT ACLI D3 ALCHIMIA RAVENNA",
        "TT ACLI D3 DECOWARM RAVENNA"
    ]
    serie_squadra = ["C2/B", "D1/B", "D1/C", "D1/B", "D1/C", "D2/E", "D3/E", "D3/F", "D3/G"] 

    main("C2/B", "TT ACLI C2 LUGO", GIORNATA, RITORNO, skip_casa=[], skip_ospiti=[1,5])
    main("D1/B", "TT ACLI D1 JUNIOR RAVENNA", GIORNATA, RITORNO)
    main("D1/C", "TT ACLI D1 ALFA LUGO", GIORNATA, RITORNO)
    main("D1/B", "TT ACLI D1 BETA LUGO", GIORNATA, RITORNO)
    main("D1/C", "TT ACLI D1 OVER LUGO", GIORNATA, RITORNO)
    main("D2/E", "TT ACLI D2 LUGO", GIORNATA, RITORNO)
    main("D3/E", "TT ACLI D3 JUNIOR LUGO", GIORNATA, RITORNO)
    main("D3/F", "TT ACLI D3 ALCHIMIA RAVENNA", GIORNATA, RITORNO)
    main("D3/G", "TT ACLI D3 DECOWARM RAVENNA", GIORNATA, RITORNO)