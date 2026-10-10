import time
import re
from datetime import datetime
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
    
    # Usa Selenium Manager (automatico da Selenium 4.6+)
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



def naviga_e_scarica_dati_n(nome_serie, nome_squadra_casa, giornata_numero, is_ritorno, post):
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
            print(f"\n[AVVISO]: Squadra '{nome_squadra_casa}' non trovata in calendario alla giornata {giornata_numero}.")
            return None

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
        print(f"\n[ERRORE]: {e}")
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    dati = naviga_e_scarica_dati_n(
        nome_serie="C1/H", 
        nome_squadra_casa="TT ACLI DOMUS NOVA RAVENNA", 
        giornata_numero=1,
        is_ritorno=False,
        post = False
    )
    print("Dati Scaricati:", dati)  