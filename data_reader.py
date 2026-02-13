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
