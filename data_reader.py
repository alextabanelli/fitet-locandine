import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def avvia_browser():
    """Configura e avvia il browser Chrome in modalità headless (silenziosa)."""
    chrome_options = Options()
    
    # Browser in modalità headless (silenziosa)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Selenium Manager downloads/selects the compatible driver automatically.
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def formatta_nome_giocatore(nome_grezzo, deve_skippare=False):
    if not nome_grezzo: return ""
    
    # --- GESTIONE DOPPIO ---
    if "-" in nome_grezzo:
        parti_doppio = nome_grezzo.split("-")
        nomi_formattati = []
        
        for p in parti_doppio:
            nome_singolo = p.strip()
            parole = nome_singolo.split()
            
            if deve_skippare and len(parole) >= 3:
                cognome = f"{parole[0].capitalize()} {parole[1].capitalize()}"
                iniziale = parole[2][0].upper()
                nomi_formattati.append(f"{cognome} {iniziale}.")
            else:
                if len(parole) >= 2:
                    cognome = parole[0].capitalize()
                    iniziale = parole[1][0].upper()
                    nomi_formattati.append(f"{cognome} {iniziale}.")
                else:
                    nomi_formattati.append(nome_singolo.capitalize())
        
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

def parse_serie_girone(nome_serie):
    """
    Esempio input: "B2/C" -> macro: "Serie B", sotto_serie: "B/2", girone: "Gir.C"
    Esempio input: "C1/A" -> macro: "Serie C", sotto_serie: "C/1", girone: "Gir.A"
    """
    match = re.match(r"([A-Za-z])(\d)/([A-Za-z])", nome_serie.strip())
    if match:
        lettera, num, girone = match.groups()
        macro_serie = f"Serie {lettera.upper()}"
        sotto_serie = f"{lettera.upper()}/{num}"
        girone_str = f"Gir.{girone.upper()}"
        return macro_serie, sotto_serie, girone_str
    
    return f"Serie {nome_serie[0].upper()}", "", ""

def naviga_e_scarica_dati_regionale(nome_serie, nome_squadra_casa, giornata_numero, is_ritorno=False, skip_casa=[], skip_ospiti=[]):
    """
    Funzione principale che orchestra tutta la navigazione.
    """
    driver = avvia_browser()
    wait = WebDriverWait(driver, 15)
    base_url = "https://portale.fitet.org/risultati/regioni/default_reg.asp?REG=9" # Emilia Romagna

    print(f"--- Avvio Scraping: {nome_serie} - Giornata {giornata_numero} ---")

    try:
        # 1. ACCESSO AL SITO
        driver.get(base_url)

        # 2. SELEZIONE SERIE
        print(f"Seleziono la serie...{nome_serie}")
        wait.until(EC.frame_to_be_available_and_switch_to_it("sommario2"))
        serie_link = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, nome_serie)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", serie_link)
        time.sleep(1)
        serie_link.click()
        driver.switch_to.default_content()

        # 3. SELEZIONE CALENDARIO
        print("Apro il calendario...")
        wait.until(EC.frame_to_be_available_and_switch_to_it("principale3"))
        wait.until(EC.frame_to_be_available_and_switch_to_it("header"))
        calendario = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Calendario incontri")))
        time.sleep(1)
        calendario.click()
        driver.switch_to.default_content()

        # 4. RICERCA MATCH NEL CALENDARIO
        print(f"Cerco il match della giornata {giornata_numero}...")
        wait.until(EC.frame_to_be_available_and_switch_to_it("principale3"))
        wait.until(EC.frame_to_be_available_and_switch_to_it("corpo"))
        
        righe = driver.find_elements(By.XPATH, f"//div/table[{giornata_numero+1}]/tbody/tr")
        match_found = False
        
        for riga in righe:
            testo = riga.text
            if nome_squadra_casa in testo:
                colonne = riga.find_elements(By.TAG_NAME, "td")
                if len(colonne) > 5:
                    idx = 5 if is_ritorno else 2
                    try:
                        link_punteggio = colonne[idx].find_element(By.TAG_NAME, "a")
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
        wait.until(EC.frame_to_be_available_and_switch_to_it("principale3"))
        wait.until(EC.frame_to_be_available_and_switch_to_it("corpo"))
        wait.until(EC.frame_to_be_available_and_switch_to_it("header"))
        
        div1 = driver.find_element(By.XPATH, "//div[1]")
        n1 = div1.find_element(By.XPATH, ".//table/tbody/tr[1]/td[1]/table/tbody/tr[1]/td[1]").text.strip()
        n2 = div1.find_element(By.XPATH, ".//table/tbody/tr[1]/td[1]/table/tbody/tr[1]/td[3]").text.strip()
        
        tab_punti = div1.find_element(By.XPATH, ".//table/tbody/tr[1]/td[2]/table/tbody")
        p1 = tab_punti.find_element(By.XPATH, ".//tr[1]/td[1]").text.strip()
        p2 = tab_punti.find_element(By.XPATH, ".//tr[1]/td[3]").text.strip()

        if nome_squadra_casa.upper() in n1.upper():
            nome_avversario, p_casa, p_ospiti = n2, p1, p2
            siamo_squadra_1 = True
        else:
            nome_avversario, p_casa, p_ospiti = n1, p2, p1
            siamo_squadra_1 = False

        giocatori_casa = []
        giocatori_ospiti = []
        risultati_match = []
        
        righe_match = driver.find_elements(By.XPATH, "//div[2]/table/tbody/tr")[1:]
        i = 1
        for riga in righe_match:
            cols = riga.find_elements(By.TAG_NAME, "td")
            if len(cols) < 15: continue
            
            s1_raw = cols[1].text.strip()
            s2_raw = cols[2].text.strip()
            sv = cols[13].text.strip() 
            sp = cols[14].text.strip()

            if siamo_squadra_1:
                deve_skippare_casa = i in skip_casa
                deve_skippare_ospiti = i in skip_ospiti
                s1_player = formatta_nome_giocatore(s1_raw, deve_skippare_casa)
                s2_player = formatta_nome_giocatore(s2_raw, deve_skippare_ospiti)
                giocatori_casa.append(s1_player)
                giocatori_ospiti.append(s2_player)
                risultati_match.append(f"{sv}-{sp}")
            else:
                deve_skippare_casa = i in skip_casa
                deve_skippare_ospiti = i in skip_ospiti
                s1_player = formatta_nome_giocatore(s1_raw, deve_skippare_ospiti)
                s2_player = formatta_nome_giocatore(s2_raw, deve_skippare_casa)
                giocatori_casa.append(s2_player)
                giocatori_ospiti.append(s1_player)
                risultati_match.append(f"{sp}-{sv}")
            i += 1

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


def naviga_e_scarica_dati_nazionale(nome_serie, nome_squadra_casa, giornata_numero, is_ritorno=False, skip_casa=[], skip_ospiti=[]):
    driver = avvia_browser()
    wait = WebDriverWait(driver, 15)
    base_url = "https://portale.fitet.org/"

    macro_serie, sotto_serie, girone_str = parse_serie_girone(nome_serie)
    print(f"--- Avvio Scraping Nazionale: {nome_serie} ({macro_serie} -> {sotto_serie} {girone_str}) - Giornata {giornata_numero} ---")

    try:
        # 1. ACCESSO AL PORTALE
        driver.get(base_url)

        # 2. SELEZIONE MACRO SERIE NEL FRAME "sinistra"
        print(f"Entro nel frame 'sinistra' e cerco '{macro_serie}'...")
        wait.until(EC.frame_to_be_available_and_switch_to_it("sinistra"))
        
        xpath_macro = f"//body//table//tbody//tr//td//p[contains(@class, 'testa')]//a[contains(text(), '{macro_serie}')]"
        try:
            link_macro = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_macro)))
        except:
            link_macro = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{macro_serie}')]")))
            
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_macro)
        time.sleep(1)
        link_macro.click()
        
        driver.switch_to.default_content()

        # 3. SELEZIONE GIRONE NEL TARGET FRAME (inferioredx / elenco)
        print(f"Passo al frame di destra e seleziono il girone ({sotto_serie} {girone_str})...")
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it("inferioredx"))
            wait.until(EC.frame_to_be_available_and_switch_to_it("elenco"))
        except:
            try:
                wait.until(EC.frame_to_be_available_and_switch_to_it("principale3"))
            except:
                pass

        xpath_girone = f"//div[@align='center']//table//tbody//tr[contains(., 'Maschile')]//td[contains(., '{sotto_serie}') and contains(., '{girone_str}')]//a"
        try:
            link_girone = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_girone)))
        except:
            xpath_fallback = f"//table//tr[contains(., 'Maschile')]//td[contains(., '{sotto_serie}') and contains(., '{girone_str}')]//a | //a[contains(., '{girone_str}')]"
            link_girone = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_fallback)))

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_girone)
        time.sleep(1)
        link_girone.click()

        driver.switch_to.default_content()

        # 4. SELEZIONE CALENDARIO
        print("Apro il Calendario Incontri...")
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it("inferioredx"))
            wait.until(EC.frame_to_be_available_and_switch_to_it("main"))
            wait.until(EC.frame_to_be_available_and_switch_to_it("header"))
        except:
            try:
                wait.until(EC.frame_to_be_available_and_switch_to_it("principale3"))
                wait.until(EC.frame_to_be_available_and_switch_to_it("header"))
            except:
                pass
                
        calendario = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Calendario incontri")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", calendario)
        time.sleep(1)
        calendario.click()

        driver.switch_to.default_content()

        # 5. RICERCA MATCH NEL CALENDARIO
        print(f"Cerco il match della giornata {giornata_numero}...")
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it("inferioredx"))
            wait.until(EC.frame_to_be_available_and_switch_to_it("main"))
            wait.until(EC.frame_to_be_available_and_switch_to_it("corpo"))
        except:
            try:
                wait.until(EC.frame_to_be_available_and_switch_to_it("principale3"))
                wait.until(EC.frame_to_be_available_and_switch_to_it("corpo"))
            except:
                pass

        righe = driver.find_elements(By.XPATH, f"//div/table[{giornata_numero+1}]/tbody/tr")
        if not righe:
            righe = driver.find_elements(By.XPATH, f"//table[{giornata_numero+1}]//tr")

        match_row_found = False
        punteggio_link_found = False
        link_punteggio_elem = None

        for riga in righe:
            testo = riga.text
            if nome_squadra_casa.upper() in testo.upper():
                colonne = riga.find_elements(By.TAG_NAME, "td")
                if len(colonne) >= 5:
                    match_row_found = True
                    sq_casa_tab = colonne[3].text.strip()
                    sq_ospiti_tab = colonne[4].text.strip()
                    print(f"\n==========================================")
                    print(f">>> MATCH TROVATO: {sq_casa_tab} vs {sq_ospiti_tab}")
                    print(f"==========================================\n")

                    idx = 5 if is_ritorno else 2
                    try:
                        link_punteggio = colonne[idx].find_element(By.TAG_NAME, "a")
                        if "-" in link_punteggio.text:
                            punteggio_link_found = True
                            link_punteggio_elem = link_punteggio
                            break
                    except:
                        pass

        if not match_row_found:
            print(f"\n[AVVISO]: Squadra '{nome_squadra_casa}' non trovata in calendario alla giornata {giornata_numero}.")
            return None
        
        if not punteggio_link_found:
            print(f"\n[INFO]: I punteggi non sono ancora presenti per la partita di '{nome_squadra_casa}' (Giornata {giornata_numero}).")
            return None

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_punteggio_elem)
        link_punteggio_elem.click()

        # 6. ESTRAZIONE DATI REFERTO
        print("Leggo i dati del referto...")
        driver.switch_to.default_content()
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it("inferioredx"))
            wait.until(EC.frame_to_be_available_and_switch_to_it("main"))
            wait.until(EC.frame_to_be_available_and_switch_to_it("corpo"))
            wait.until(EC.frame_to_be_available_and_switch_to_it("mainer"))
        except:
            try:
                wait.until(EC.frame_to_be_available_and_switch_to_it("principale3"))
                wait.until(EC.frame_to_be_available_and_switch_to_it("corpo"))
                wait.until(EC.frame_to_be_available_and_switch_to_it("header"))
            except:
                pass

        try:
            div1 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[1]")))
            n1 = div1.find_element(By.XPATH, ".//table/tbody/tr[1]/td[1]/table/tbody/tr[1]/td[1]").text.strip()
            n2 = div1.find_element(By.XPATH, ".//table/tbody/tr[1]/td[1]/table/tbody/tr[1]/td[3]").text.strip()
            
            tab_punti = div1.find_element(By.XPATH, ".//table/tbody/tr[1]/td[2]/table/tbody")
            p1 = tab_punti.find_element(By.XPATH, ".//tr[1]/td[1]").text.strip()
            p2 = tab_punti.find_element(By.XPATH, ".//tr[1]/td[3]").text.strip()

            righe_match = driver.find_elements(By.XPATH, "//div[2]/table/tbody/tr")[1:]
            if not righe_match:
                raise ValueError("Nessun match individuale trovato nel referto.")

        except Exception:
            print("\n[INFO]: I punteggi non sono ancora presenti o il referto non è compilato.")
            return None

        if nome_squadra_casa.upper() in n1.upper():
            nome_avversario, p_casa, p_ospiti = n2, p1, p2
            siamo_squadra_1 = True
        else:
            nome_avversario, p_casa, p_ospiti = n1, p2, p1
            siamo_squadra_1 = False

        giocatori_casa = []
        giocatori_ospiti = []
        risultati_match = []
        
        i = 1
        for riga in righe_match:
            cols = riga.find_elements(By.TAG_NAME, "td")
            s1_raw = cols[1].text.strip()
            s2_raw = cols[2].text.strip()
            sv = cols[13].text.strip() 
            sp = cols[14].text.strip()

            if siamo_squadra_1:
                deve_skippare_casa = i in skip_casa
                deve_skippare_ospiti = i in skip_ospiti
                s1_player = formatta_nome_giocatore(s1_raw, deve_skippare_casa)
                s2_player = formatta_nome_giocatore(s2_raw, deve_skippare_ospiti)
                giocatori_casa.append(s1_player)
                giocatori_ospiti.append(s2_player)
                risultati_match.append(f"{sv}-{sp}")
            else:
                deve_skippare_casa = i in skip_casa
                deve_skippare_ospiti = i in skip_ospiti
                s1_player = formatta_nome_giocatore(s1_raw, deve_skippare_ospiti)
                s2_player = formatta_nome_giocatore(s2_raw, deve_skippare_casa)
                giocatori_casa.append(s2_player)
                giocatori_ospiti.append(s1_player)
                risultati_match.append(f"{sp}-{sv}")
            i += 1

        print(f"Estrazione completata con successo: {nome_squadra_casa} vs {nome_avversario} ({p_casa}-{p_ospiti})")
        
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
        print(f"\n[ERRORE]: {e}")
        return None
    finally:
        driver.quit()

def naviga_e_scarica_dati(nome_serie, nome_squadra_casa, giornata_numero, is_ritorno=False, skip_casa=[], skip_ospiti=[]):
    """
    Funzione principale che orchestra tutta la navigazione.
    """
    if nome_serie.startswith("C2") or nome_serie.startswith("D"):
        return naviga_e_scarica_dati_regionale(nome_serie, nome_squadra_casa, giornata_numero, is_ritorno, skip_casa, skip_ospiti)
    else:
        return naviga_e_scarica_dati_nazionale(nome_serie, nome_squadra_casa, giornata_numero, is_ritorno, skip_casa, skip_ospiti)

if __name__ == "__main__":
    dati = naviga_e_scarica_dati_regionale(
        nome_serie="C1/H", 
        nome_squadra_casa="TT ACLI DOMUS NOVA RAVENNA", 
        giornata_numero=1,
        is_ritorno=False
    )
    print("Dati Scaricati:", dati)