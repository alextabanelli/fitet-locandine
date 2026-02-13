import os
import time  # Necessario per time.sleep()
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# Importazioni fondamentali per far funzionare WebDriverWait, By e EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    is_streamlit_cloud = os.path.exists("/usr/bin/chromium")
    
    if is_streamlit_cloud:
        chrome_options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
    else:
        service = Service() 

    driver = webdriver.Chrome(service=service, options=chrome_options)
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

def naviga_e_scarica_dati(nome_serie, nome_squadra_casa, giornata_numero, is_ritorno=False, skip_casa=[], skip_ospiti=[]):
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
        print("Seleziono la serie...")
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
