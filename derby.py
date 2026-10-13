import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from luogo import get_luogo

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


def formatta_data_italiana(data):
    """Converte una data nel formato gg/mm/aaaa in una stringa italiana estesa."""
    data_convertita = datetime.strptime(data.strip(), "%d/%m/%Y")
    giorni = [
        "Lunedì", "Martedì", "Mercoledì", "Giovedì",
        "Venerdì", "Sabato", "Domenica"
    ]
    mesi = [
        "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
        "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
    ]
    return (
        f"{giorni[data_convertita.weekday()]} "
        f"{data_convertita.day} {mesi[data_convertita.month - 1]}"
    )

def naviga_e_scarica_dati_derby(nomi_societa, nome_serie, nome_squadra, giornate = 7):
    """
    Funzione principale che orchestra tutta la navigazione.
    Restituisce un dizionario con i dati pronti per la grafica.
    """
    driver = avvia_browser()
    wait = WebDriverWait(driver, 15)
    base_url = "https://portale.fitet.org/risultati/regioni/default_reg.asp?REG=9" # Emilia Romagna

    nomserie = nome_serie[0]+nome_serie[1]
    try:
        # 1. ACCESSO AL SITO
        driver.get(base_url)

        # 2. SELEZIONE SERIE
        msg = f"Seleziono la serie...{nome_serie}"
        print(msg)
        wait.until(EC.frame_to_be_available_and_switch_to_it("sommario2"))
        serie_link = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, nome_serie)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", serie_link)
        time.sleep(1)
        serie_link.click()
        driver.switch_to.default_content()

        # 3. SELEZIONE SQUADRA
        msg = f"Seleziono la squadra...{nome_squadra}"
        print(msg)
        wait.until(EC.frame_to_be_available_and_switch_to_it("principale3"))
        print("Entrato nel frame 'principale3' per trovare la squadra.")
        wait.until(EC.frame_to_be_available_and_switch_to_it("corpo"))
        print("Entrato nel frame 'corpo' per trovare la squadra.")
        div1 = driver.find_element(By.XPATH, "//div[1]")
        righe = div1.find_elements(By.XPATH, ".//table/tbody/tr")
        print(f"Trovate {len(righe)} righe nella tabella delle squadre.")

        nome_casa = []
        nome_ospiti = []
        serie = []
        datar = []
        orari = []
        luogo = []


        riga_trovata = None
        for indice, riga in enumerate(righe):
            celle = riga.find_elements(By.XPATH, "./td")
            if len(celle) < 2:
                continue
            squadra = celle[1].text.strip()
            if squadra != nome_squadra.strip() and squadra in nomi_societa:
                riga_trovata = riga
                print(f"Trovato derby tra le squadre: {squadra} e {nome_squadra}")
                break

        if not riga_trovata:
            print(f"Derby non trovato tra {nome_squadra} e le squadre: {nomi_societa}")
            return None
        else:
            driver.switch_to.default_content()
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
            driver.switch_to.default_content()
            wait.until(EC.frame_to_be_available_and_switch_to_it("principale3"))
            wait.until(EC.frame_to_be_available_and_switch_to_it("corpo"))
            for i in range(1, giornate + 1):
                xpath_giornata = f"//div/table[{i+1}]/tbody/tr"
                righe_giornata = driver.find_elements(By.XPATH, xpath_giornata)
                if not righe_giornata:
                    righe_giornata = driver.find_elements(
                        By.XPATH, f"//table[{i+1}]//tbody/tr"
                    )
                print(f"Trovate {len(righe_giornata)} righe nella giornata {i}.")
                for riga in righe_giornata:
                    celle = riga.find_elements(By.XPATH, "./td")
                    if len(celle) < 5:
                        continue
                    sq_casa = celle[3].text.strip()
                    sq_ospiti = celle[4].text.strip()
                    if sq_casa == nome_squadra.strip() and sq_ospiti == squadra.strip():
                        nome_casa.append(sq_casa)
                        nome_ospiti.append(sq_ospiti)
                        serie.append(nomserie)
                        datar.append(celle[0].text.strip())
                        orari.append(celle[1].text.strip())
                        luogo.append(get_luogo(nome_serie, sq_casa))
                        nome_casa.append(sq_ospiti)
                        nome_ospiti.append(sq_casa)
                        serie.append(nomserie)
                        datar.append(celle[7].text.strip())
                        orari.append(celle[6].text.strip())
                        luogo.append(get_luogo(nome_serie, sq_ospiti))
                    elif sq_casa == squadra.strip() and sq_ospiti == nome_squadra.strip():
                        nome_casa.append(sq_casa)
                        nome_ospiti.append(sq_ospiti)
                        serie.append(nomserie)
                        datar.append(celle[0].text.strip())
                        orari.append(celle[1].text.strip())
                        luogo.append(get_luogo(nome_serie, sq_casa))
                        nome_casa.append(sq_ospiti)
                        nome_ospiti.append(sq_casa)
                        serie.append(nomserie)
                        datar.append(celle[7].text.strip())
                        orari.append(celle[6].text.strip())
                        luogo.append(get_luogo(nome_serie, sq_ospiti))

        if not datar:
            print(f"Nessun match trovato per {nome_squadra} contro {squadra}.")
            return None

        data = [
            f"{formatta_data_italiana(giorno)} alle {orario}"
            for giorno, orario in zip(datar, orari)
        ]
        print(f"Estrazione completata con successo: {len(data)} match trovati.")

        return {
            "nome_casa": nome_casa,
            "nome_ospiti": nome_ospiti,
            "nome_serie": serie,
            "data": data,
            "luogo": luogo
        }

    except Exception as e:
        print(f"ERRORE CRITICO: {e}")
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    dati = naviga_e_scarica_dati_derby( nomi_societa = [
                "TT ACLI DOMUS NOVA RAVENNA",
                "TT ACLI D1 JUNIOR RAVENNA",
                "TT ACLI D2 ALCHIMIA RAVENNA",
                "TT ACLI D2 DECOWARM RAVENNA",
                "TT ACLI D3 DECOWARM RAVENNA",
                "TT ACLI D3 ALCHIMIA RAVENNA",
                "TT ACLI D3 BETA RAVENNA",
                "TT ACLI D1 BETA LUGO",
                "TT ACLI D1 ALFA LUGO",
                "TT ACLI D2 OVER LUGO",
                "TT ACLI D3 JUNIOR LUGO",
                "TT ACLI D3 ALFA LUGO"
            ],
        nome_serie="D3/E", 
        nome_squadra="TT ACLI D3 ALFA LUGO", 
    )
    print("Dati Scaricati:", dati)