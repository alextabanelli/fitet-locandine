from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def avvia_browser():
    """Configura e avvia il browser Chrome in modalità headless."""
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Usa Selenium Manager
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def formatta_data_italiana(data):
    """Converte una data nel formato gg/mm/aaaa in una stringa italiana estesa."""
    data_convertita = datetime.strptime(data.strip(), "%d/%m/%Y")
    giorni = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]
    mesi = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    return (
        f"{giorni[data_convertita.weekday()]} "
        f"{data_convertita.day} {mesi[data_convertita.month - 1]}"
    )

def naviga_e_scarica_dati_r(nome_serie, nome_squadra_casa, giornata_numero, is_ritorno, post=False):
    """
    Funzione principale che orchestra tutta la navigazione.
    Restituisce un dizionario con i dati pronti per la grafica.
    """
    driver = avvia_browser()
    wait = WebDriverWait(driver, 15)
    base_url = "https://portale.fitet.org/risultati/regioni/default_reg.asp?REG=9" # Emilia Romagna

    print(f"--- Avvio Scraping: {nome_serie} - Giornata {giornata_numero} ---")

    try:
        # 1. ACCESSO AL SITO
        driver.get(base_url)

        # 2. SELEZIONE SERIE (Frame: sommario2)
        print("Seleziono la serie...")
        wait.until(EC.frame_to_be_available_and_switch_to_it("sommario2"))
        print("Entrato nel frame 'sommario2' per la selezione serie.")
        
        # Cerca il link che contiene il nome della serie (es. "C2/B")
        serie_link = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, nome_serie)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", serie_link)
        time.sleep(1) # Piccola pausa per stabilizzare lo scroll
        serie_link.click()
        
        driver.switch_to.default_content() # Torna al livello base

        # 3. SELEZIONE CALENDARIO (Frame: header)
        print("Apro il calendario...")
        wait.until(EC.frame_to_be_available_and_switch_to_it("principale3"))
        print("Entrato nel frame 'principale3' per il calendario.")
        wait.until(EC.frame_to_be_available_and_switch_to_it("header"))
        print("Entrato nel frame 'header' per il calendario.")
        
        calendario = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Calendario incontri")))
        print("Trovato il link del calendario.")
        time.sleep(1) # Piccola pausa per stabilizzare lo scroll
        calendario.click()
        
        driver.switch_to.default_content()

        # 4. RICERCA MATCH NEL CALENDARIO (Frame: corpo)
        print(f"Cerco il match della giornata {giornata_numero}...")
        wait.until(EC.frame_to_be_available_and_switch_to_it("principale3"))
        print("Entrato nel frame 'principale3' per la ricerca del match.")
        wait.until(EC.frame_to_be_available_and_switch_to_it("corpo"))
        print("Entrato nel frame 'corpo' per la ricerca del match.")
        
        # XPATH Dinamico: Cerca la tabella che contiene "X^ Giornata"
        # Nota: Sul sito spesso scrivono "1^ Giornata", "2^ Giornata" etc.
        header_giornata = f"{giornata_numero}^ Giornata"
        
        # Trova la riga (TR) che contiene l'intestazione della giornata
        # Poi cerca la tabella padre o le righe successive
        #Voglio scegliere la tabella che è uguale al numero di giornata
        righe = driver.find_elements(By.XPATH, f"//div/table[{giornata_numero+1}]/tbody/tr")
        match_row_found = False
        punteggio_link_found = False
        link_punteggio_elem = None

        for riga in righe:
            testo = riga.text
            if nome_squadra_casa.upper() in testo.upper():
                colonne = riga.find_elements(By.TAG_NAME, "td")
                if len(colonne) >= 5:
                    match_row_found = True
                    id_casa = 4 if is_ritorno else 3
                    sq_casa = colonne[id_casa].text.strip()
                    sq_ospiti = colonne[7-id_casa].text.strip()
                    if is_ritorno:
                        datar = colonne[7].text.strip()
                        ora = colonne[6].text.strip()
                    else:
                        datar = colonne[0].text.strip()
                        ora = colonne[1].text.strip()
                    print(f"\n==========================================")
                    print(f">>> MATCH TROVATO: {sq_casa} vs {sq_ospiti}")
                    print(f"==========================================\n")

                    idx = 5 if is_ritorno else 2
                    link_punteggio = colonne[idx].find_element(By.TAG_NAME, "a")
                    if link_punteggio.text[0].isnumeric():  # Controlla se il link contiene un punteggio
                        punteggio = link_punteggio.text
                    else:   
                        punteggio = None
                    break  # Esci dal ciclo dopo aver trovato il match
        
        if not match_row_found:
            raise Exception("Match non trovato o punteggio non ancora inserito.")

        data = f"{formatta_data_italiana(datar)} {ora}"

        print(f"Estrazione completata con successo: {sq_casa} vs {sq_ospiti} ({punteggio})")
        
        return {
            "punteggio": punteggio,
            "nome_team_casa": sq_casa,
            "nome_team_ospiti": sq_ospiti,
            "nome_serie": nome_serie,
            "data": data
        }

    except Exception as e:
        print(f"ERRORE CRITICO: {e}")
        return None
    finally:
        driver.quit()

# --- BLOCCO DI TEST ---
if __name__ == "__main__":
    # Esempio di utilizzo
    dati = naviga_e_scarica_dati_r(
        nome_serie="D1/D", 
        nome_squadra_casa="TT ACLI D1 JUNIOR RAVENNA", 
        giornata_numero=1,   # Metti la giornata corretta che ha un risultato inserito
        is_ritorno=False,       # False = Andata, True = Ritorno
        post=False             # True = Scarica dati post-partita, False = Pre-partita
    )
    print("Dati Scaricati:", dati)