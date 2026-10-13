import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def avvia_browser():
    """Configura e avvia il browser Chrome in modalità headless (silenziosa)."""
    chrome_options = Options()

    # Browser in modalità headless (silenziosa)
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Selenium Manager downloads/selects the compatible driver automatically.
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def get_luogo(nome_serie, nome_squadra):
    driver = avvia_browser()
    wait = WebDriverWait(driver, 15)
    base_url = "https://portale.fitet.org/risultati/regioni/default_reg.asp?REG=9"  # Emilia Romagna

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

        riga_trovata = None
        for indice, riga in enumerate(righe):
            celle = riga.find_elements(By.XPATH, "./td")
            if len(celle) < 2:
                continue

            squadra = celle[1].text.strip()
            print(f"Controllo la squadra {squadra} nella riga {indice}.")
            if squadra == nome_squadra.strip():
                riga_trovata = riga
                print(f"Trovata la squadra: {nome_squadra}")
                break

        if riga_trovata is None:
            print(f"Squadra {nome_squadra} non trovata.")
            return None

        link_squadra = riga_trovata.find_element(By.XPATH, "./td[1]//a[.//img]")
        print(f"Seleziono la squadra {nome_squadra}.")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_squadra)
        link_squadra.click()
        print(f"Squadra {nome_squadra} selezionata, attendo il caricamento della pagina dei dettagli.")
        time.sleep(1)
        driver.switch_to.default_content()

        # 4. LETTURA DEI DATI DELLA SQUADRA
        wait.until(EC.frame_to_be_available_and_switch_to_it("principale3"))
        print("Entrato nel frame 'principale3' per leggere i dettagli.")
        wait.until(EC.frame_to_be_available_and_switch_to_it("corpo"))
        print("Entrato nel frame 'corpo' per leggere i dettagli.")
        fieldset = wait.until(
            EC.presence_of_element_located((By.XPATH, "//fieldset[@name='squadra']"))
        )
        print("Entrato nel fieldset per trovare la squadra.")
        tabella = fieldset.find_element(By.XPATH, ".//table[2]")
        print("Trovata la tabella dei dettagli della squadra.")

        righe_dettaglio = tabella.find_elements(By.XPATH, ".//tr")
        if len(righe_dettaglio) < 2:
            raise ValueError("La tabella non contiene una seconda riga.")

        riga = righe_dettaglio[1]
        celle_dettaglio = riga.find_elements(By.XPATH, "./td")
        if len(celle_dettaglio) < 4:
            raise ValueError(
                f"La seconda riga contiene {len(celle_dettaglio)} celle, "
                "ma ne servono almeno 4."
            )
        print("Trovata la seconda riga dei dettagli della squadra.")

        campo_principale = celle_dettaglio[0].text.strip()
        indirizzo = celle_dettaglio[1].text.strip()
        cap = celle_dettaglio[2].text.strip()
        prov = celle_dettaglio[3].text.strip()

        print(f"Campo principale della squadra: {campo_principale}")
        print(f"Indirizzo della squadra: {indirizzo}")
        print(f"CAP della squadra: {cap}")
        print(f"Provincia della squadra: {prov}")
        cap_prov = f"{cap} {prov}"
        return {
            "campo_principale": campo_principale,
            "indirizzo": indirizzo,
            "cap": cap_prov,
        }
    finally:
        driver.quit()


if __name__ == "__main__":
    dati = get_luogo(
        nome_serie="D3/E",
        nome_squadra="TT ACLI D3 ALFA LUGO",
    )
    print("Dati Scaricati:", dati)