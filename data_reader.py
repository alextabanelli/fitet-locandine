import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# Rimuoviamo webdriver_manager perché su Streamlit Cloud crea conflitti di versione
# from webdriver_manager.chrome import ChromeDriverManager 

def avvia_browser():
    """Configura e avvia il browser in modalità headless compatibile con Streamlit Cloud."""
    chrome_options = Options()
    
    # Impostazioni obbligatorie per server Linux/Streamlit Cloud
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Rileviamo se siamo su Streamlit Cloud o in locale
    # Streamlit Cloud installa chromium in /usr/bin/chromium
    is_streamlit_cloud = os.path.exists("/usr/bin/chromium")
    
    if is_streamlit_cloud:
        # Percorsi fissi per Streamlit Cloud (installati via packages.txt)
        chrome_options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
    else:
        # In locale (Windows/Mac) usiamo le impostazioni standard
        # Se hai ancora errori in locale, qui potresti riutilizzare ChromeDriverManager
        service = Service() 

    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# ... resto delle tue funzioni (naviga_e_scarica_dati, ecc.) ...

def formatta_nome_giocatore(nome_grezzo, deve_skippare=False):
    if not nome_grezzo: return ""
    
    # --- GESTIONE DOPPIO ---
    if "-" in nome_grezzo:
        parti_doppio = nome_grezzo.split("-")
        nomi_formattati = []
        
        for p in parti_doppio:
            nome_singolo = p.strip()
            parole = nome_singolo.split()
            
            # Se è richiesto lo skip per questo match E ci sono abbastanza parole
            if deve_skippare and len(parole) >= 3:
                # Esempio: "DE GIUSEPPE MARIO" -> "De Giuseppe M."
                cognome = f"{parole[0].capitalize()} {parole[1].capitalize()}"
                iniziale = parole[2][0].upper()
                nomi_formattati.append(f"{cognome} {iniziale}.")
            else:
                # Formattazione standard: "LOBODA JOVAN" -> "Loboda J."
                if len(parole) >= 2:
                    cognome = parole[0].capitalize()
                    iniziale = parole[1][0].upper()
                    nomi_formattati.append(f"{cognome} {iniziale}.")
                else:
                    nomi_formattati.append(nome_singolo.capitalize())
        
        # Uniamo i due nomi del doppio con l'andata a capo per la locandina
        return "\n".join(nomi_formattati)

    # --- GESTIONE SINGOLO ---
    parole = nome_grezzo.strip().split()
    if deve_skippare and len(parole) >= 3:
        cognome = f"{parole[0].capitalize()} {parole[1].capitalize()}"
        iniziale = parole[2][0].upper()
        return f"{cognome} {iniziale}."
    
    if len(parole) >= 2:
        return f"{parole[0].capitalize()} {parole[1][0].upper()}."
    
    return nome_grezzo.capitalize()


def naviga_e_scarica_dati(nome_serie, nome_squadra_casa, giornata_numero, is_ritorno=False, skip_casa=[], skip_ospiti=[]):
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
        match_found = False
        
        for riga in righe:
            testo = riga.text
            # Controlliamo se siamo nella sezione della giornata giusta (logica semplificata)
            # Qui cerchiamo direttamente la riga che ha la squadra e un punteggio
            if nome_squadra_casa in testo:
                colonne = riga.find_elements(By.TAG_NAME, "td")
                if len(colonne) > 5:
                    # Logica colonne (basata sulla tua analisi):
                    # Andata (is_ritorno=False) -> Punteggio in colonna index 2 (3° td)
                    # Ritorno (is_ritorno=True) -> Punteggio in colonna index 5 (6° td)
                    idx = 5 if is_ritorno else 2
                    
                    try:
                        link_punteggio = colonne[idx].find_element(By.TAG_NAME, "a")
                        # Verifica che il link contenga un punteggio (es "5-2")
                        if "-" in link_punteggio.text:
                            print(f"Match trovato")
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_punteggio)
                            link_punteggio.click()
                            match_found = True
                            break
                    except:
                        continue
        
        if not match_found:
            raise Exception("Match non trovato o punteggio non ancora inserito.")

        driver.switch_to.default_content()

        # 5. ESTRAZIONE DATI REFERTO
        print("Leggo i dettagli del referto...")
        
        # Navigazione profonda nei frame come descritto
        driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it("principale3"))
        wait.until(EC.frame_to_be_available_and_switch_to_it("corpo"))
        wait.until(EC.frame_to_be_available_and_switch_to_it("header"))
        
        # --- A. Nomi Squadre e Punteggio Totale (Dal primo DIV) ---
        # Percorso: Div 1 -> Tabella -> TR 1 -> TD 1 (Nomi) e TD 2 (Punti)
        div1 = driver.find_element(By.XPATH, "//div[1]")
        div2 = driver.find_element(By.XPATH, "//div[2]") # Per i dettagli dei match più avanti
        # Tabella Nomi (nella prima TD del Div 1)
        n1 = div1.find_element(By.XPATH, ".//table/tbody/tr[1]/td[1]/table/tbody/tr[1]/td[1]").text.strip() # Squadra 1
        n2 = div1.find_element(By.XPATH, ".//table/tbody/tr[1]/td[1]/table/tbody/tr[1]/td[3]").text.strip() # Simbolo "vs" o simile
        #n2 = div2.find_element(By.XPATH, ".//table/tbody/tr[1]/td[3]").text.strip() # Squadra 2
        # Tabella Punteggi (nella seconda TD del Div 1)
        tab_punti = div1.find_element(By.XPATH, ".//table/tbody/tr[1]/td[2]/table/tbody")
        p1 = tab_punti.find_element(By.XPATH, ".//tr[1]/td[1]").text.strip() # Punti Sq 1
        p2 = tab_punti.find_element(By.XPATH, ".//tr[1]/td[3]").text.strip() # Punti Sq 2

        # Identifichiamo chi siamo noi per assegnare correttamente Casa/Ospite sulla locandina
        if nome_squadra_casa.upper() in n1.upper():
            nome_avversario, p_casa, p_ospiti = n2, p1, p2
            siamo_squadra_1 = True
        else:
            nome_avversario, p_casa, p_ospiti = n1, p2, p1
            siamo_squadra_1 = False

        # --- B. Dettaglio Singoli Match (Dal secondo DIV) ---
        giocatori_casa = []
        giocatori_ospiti = []
        risultati_match = []
        
        # Prendiamo tutte le righe della tabella nel secondo DIV, saltando l'intestazione
        righe_match = driver.find_elements(By.XPATH, "//div[2]/table/tbody/tr")[1:]
        i = 1
        for riga in righe_match:
            print(f"Elaboro riga {i} dei match...")
            cols = riga.find_elements(By.TAG_NAME, "td")
            s1_raw = cols[1].text.strip()
            s2_raw = cols[2].text.strip()
            
            # SV = Set Vinti da Squadra 1 | SP = Set Persi da Sq 1 (quindi vinti da Sq 2)
            sv = cols[13].text.strip() 
            sp = cols[14].text.strip()

            # APPLICHIAMO IL FILTRO
            if siamo_squadra_1:
                deve_skippare_casa = i in skip_casa
                deve_skippare_ospiti = i in skip_ospiti
                
                s1_player = formatta_nome_giocatore(s1_raw, deve_skippare_casa)
                s2_player = formatta_nome_giocatore(s2_raw, deve_skippare_ospiti)
            else:
                deve_skippare_casa = i in skip_casa
                deve_skippare_ospiti = i in skip_ospiti
                
                # Attenzione: qui s1_raw è l'ospite e s2_raw è casa
                s1_player = formatta_nome_giocatore(s1_raw, deve_skippare_ospiti)
                s2_player = formatta_nome_giocatore(s2_raw, deve_skippare_casa)
                

            if siamo_squadra_1:
                giocatori_casa.append(s1_player)
                giocatori_ospiti.append(s2_player)
                risultati_match.append(f"{sv}-{sp}")
            else:
                giocatori_casa.append(s2_player)
                giocatori_ospiti.append(s1_player)
                risultati_match.append(f"{sp}-{sv}")
            
            i += 1
        

        print(f"Estrazione completata: {nome_squadra_casa} vs {nome_avversario} ({p_casa}-{p_ospiti})")
        
        return {
            "punteggio_casa": int(p_casa),
            "punteggio_ospiti": int(p_ospiti),
            "nome_team_casa": nome_squadra_casa,
            "nome_team_ospiti": nome_avversario,
            "nome_serie": nome_serie,
            "giocatori_casa": giocatori_casa,
            "giocatori_ospiti": giocatori_ospiti,
            "risultati_match": risultati_match
        }

    except Exception as e:
        print(f"ERRORE CRITICO: {e}")
        return None
    finally:
        driver.quit()

# --- BLOCCO DI TEST ---
if __name__ == "__main__":
    # Esempio di utilizzo
    dati = naviga_e_scarica_dati(
        nome_serie="D1/C", 
        nome_squadra_casa="TT ACLI D1 ALFA LUGO", 
        giornata_numero=3,   # Metti la giornata corretta che ha un risultato inserito
        is_ritorno=False       # False = Andata, True = Ritorno
    )
    print("Dati Scaricati:", dati)
