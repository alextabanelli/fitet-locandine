from PIL import Image, ImageDraw, ImageFont
import os
import difflib 
# --- FUNZIONE HELPER PER CARICARE I FONT IN SICUREZZA ---
def load_font(path, size, default_font=None):
    try:
        # Pillow supporta dimensioni float nelle versioni recenti
        return ImageFont.truetype(path, size)
    except OSError:
        print(f"ATTENZIONE: Font non trovato in '{path}'. Uso un default brutto.")
        return default_font if default_font else ImageFont.load_default()
    
def wrap_text(text, max_chars):
    """Divide il testo in più righe senza spezzare le parole."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        # Se aggiungendo la parola superiamo il limite, chiudiamo la riga attuale
        if current_length + len(word) + 1 > max_chars and current_line:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word) + 1
            
    if current_line:
        lines.append(" ".join(current_line))
        
    return "\n".join(lines)


import os

def trova_percorso_logo(nome_squadra, cartella_loghi="assets/logos/"):
    """
    Cerca il logo migliore confrontando tutti i file e scegliendo quello
    con la somiglianza più alta col nome della squadra.
    """
    if not nome_squadra:
        return None

    # Normalizziamo il nome squadra
    nome_squadra = nome_squadra.lower()
    
    # Parole da ignorare per il matching
    parole_inutili = {"asd", "tt", "tennistavolo", "team", "ponente", "levante", "c2", "c1", "d1", "d2", "d3", "b2"}

    try:
        if not os.path.exists(cartella_loghi):
            print(f"⚠️ Cartella loghi non trovata: {cartella_loghi}")
            return None

        file_loghi = os.listdir(cartella_loghi)
        
        # Puliamo il nome squadra rimuovendo le parole inutili
        parole_squadra = [p for p in nome_squadra.split() if p not in parole_inutili and len(p) > 2]
        nome_squadra_clean = " ".join(parole_squadra)

        best_match = None
        best_score = 0.0

        for file in file_loghi:
            # Puliamo il nome del file (via estensione e minuscolo)
            nome_file_pulito = os.path.splitext(file)[0].lower()
            
            # Calcoliamo la somiglianza tra il nome del file e il nome pulito della squadra
            # ratio() restituisce un float tra 0.0 (diverso) e 1.0 (identico)
            score = difflib.SequenceMatcher(None, nome_file_pulito, nome_squadra_clean).ratio()
            
            # BONUS: Se il nome del file è CONTENUTO interamente nel nome squadra (o viceversa)
            # diamo un boost al punteggio, ma preferiamo le stringhe più lunghe.
            # Esempio: "cesena" in "cesenatico" -> Match parziale
            # Esempio: "cesenatico" in "cesenatico" -> Match totale (vince questo)
            if nome_file_pulito in nome_squadra_clean:
                # Normalizziamo sulla lunghezza per favorire match più lunghi ("cesenatico" > "cesena")
                score = 0.8 + (len(nome_file_pulito) / len(nome_squadra_clean)) * 0.2
            
            # Teniamo traccia del vincitore attuale
            if score > best_score and score > 0.6: # Soglia minima di somiglianza
                best_score = score
                best_match = file

        if best_match:
            percorso_completo = os.path.join(cartella_loghi, best_match)
            print(f"✅ Logo trovato per '{nome_squadra}': {best_match} (Score: {best_score:.2f})")
            return percorso_completo

    except Exception as e:
        print(f"Errore ricerca logo: {e}")
        return None

    print(f"❌ Nessun logo trovato per: {nome_squadra}")
    return None

def crea_locandina_v2(
    punteggio_casa, 
    punteggio_ospiti, 
    nome_team_casa, 
    nome_team_ospiti,
    nome_serie,             # Nuovo: es. "C2/B"
    giocatori_casa,         # Lista nomi
    giocatori_ospiti,       # Lista nomi
    risultati_match         # Lista risultati (es: "3-0", "1-3")
):
    print("--- Inizio creazione locandina ---")

    # Preserve original names for file naming (avoid embedded newlines)
    nome_team_casa_raw = nome_team_casa
    nome_team_ospiti_raw = nome_team_ospiti

    # 1. SCELTA DEL TEMPLATE PRINCIPALE (Vittoria vs Sconfitta)
    # Logica: Se punteggio casa > ospiti, vinciamo noi.
    if punteggio_casa > punteggio_ospiti:
        bg_path = "assets/templates/vittoria.png"
        print(f"Risultato {punteggio_casa}-{punteggio_ospiti}: VITTORIA. Carico sfondo verde.")
    else:
        bg_path = "assets/templates/sconfitta.png"
        print(f"Risultato {punteggio_casa}-{punteggio_ospiti}: SCONFITTA. Carico sfondo rosso.")

    try:
        base = Image.open(bg_path).convert("RGBA")
        W, H = base.size # Dimensioni totali immagine
    except FileNotFoundError:
        print(f"ERRORE FATALE: Non trovo lo sfondo principale: {bg_path}")
        return

    # 2. SETUP COLORI E FONT (Specifiche utente)
    TEXT_COLOR = "white" # Tutti i testi sono bianchi

    # Usiamo i percorsi e le dimensioni esatte richieste
    # N.B. Se non hai i file .ttf, il programma userà un font di default.
    font_nomi_bold = load_font("assets/fonts/Montserrat-ExtraBold.ttf", 27)
    font_serie_bold = load_font("assets/fonts/Montserrat-ExtraBold.ttf", 30)
    font_ris_match_bold = load_font("assets/fonts/Montserrat-ExtraBold.ttf", 40)
    font_ris_finale_anton = load_font("assets/fonts/Anton-Regular.ttf", 136)
    
    draw = ImageDraw.Draw(base)

    # --- INIZIO POSIZIONAMENTO ELEMENTI ---
    # NOTA SULLE COORDINATE: Uso ancore centrali (mm, lm, rm) per facilitare l'allineamento.
    # Modifica i valori X, Y per spostare gli elementi.

    # 3. SEZIONE HEADER (Nomi squadre, Serie, Punteggioone)
    # Ho stimato le coordinate Y guardando l'esempio, aggiustale tu.
    serie_pos = (W/2, 757)
    res_pos = (W/2, 897)
    squad1_pos = (221,759) # A sinistra del centro
    squad2_pos = (830,759) # A destra del centro
    # Nome Serie (es. C2/B) - Centrato in alto
    draw.text((serie_pos[0], serie_pos[1]), nome_serie, font=font_serie_bold, fill=TEXT_COLOR, anchor="mm")

    # Nomi Squadre
    # Casa (a sinistra del centro)
    #Controllo sulla lunghezza dei nomi delle squadre per evitare overflow (opzionale, dipende dal font)
    max_name_length = 20 # Puoi regolare questo valore in base alla dimensione del font e alla larghezza disponibile
    nome_team_casa = wrap_text(nome_team_casa_raw, max_name_length)
    nome_team_ospiti = wrap_text(nome_team_ospiti_raw, max_name_length)

    #Se il nome va a capo, voglio l'allineamento orizzontale centrato 
    if "\n" in nome_team_casa:
        draw.text((squad1_pos[0], squad1_pos[1]), nome_team_casa, font=font_serie_bold, fill=TEXT_COLOR, anchor="mm", align="center")
    else : draw.text((squad1_pos[0], squad1_pos[1]), nome_team_casa, font=font_serie_bold, fill=TEXT_COLOR, anchor="mm")
    # Ospiti (a destra del centro)
    if "\n" in nome_team_ospiti: 
        draw.text((squad2_pos[0], squad2_pos[1]), nome_team_ospiti, font=font_serie_bold, fill=TEXT_COLOR, anchor="mm", align="center")
    else : draw.text((squad2_pos[0], squad2_pos[1]), nome_team_ospiti, font=font_serie_bold, fill=TEXT_COLOR, anchor="mm")

    # Punteggio Finale Gigante (es. 6 - 1) - Perfettamente centrato
    final_score_text = f"{punteggio_casa} - {punteggio_ospiti}"
    draw.text((res_pos[0], res_pos[1]), final_score_text, font=font_ris_finale_anton, fill=TEXT_COLOR, anchor="mm")

    # 4. LOGHI SOCIETÀ
    # Definisci centro e dimensione dei loghi
    size_logo = (180, 180) # Dimensione target
    pos_logo_ospiti_center = (754, 815)

    # Funzione helper per piazzare i loghi centrati
    def piazza_logo(path, pos, size, base_img):
        try:
            img = Image.open(path).convert("RGBA")            
            base_img.paste(img, (pos[0], pos[1]), mask=img)
        except FileNotFoundError:
            print(f"Logo non trovato: {path}")

    # Trova e piazza i loghi usando la funzione helper
    logo_ospiti_path = trova_percorso_logo(nome_team_ospiti_raw)
    if logo_ospiti_path is not None:
        piazza_logo(logo_ospiti_path, pos_logo_ospiti_center, size_logo, base)

    # 5. SEZIONE INCONTRI INDIVIDUALI (Loop con Overlay Dinamici)
    print("--- Inizio elaborazione righe match ---")
    
    # Carica le immagini dei parallelepipedi
    try:
        overlay_win = Image.open("assets/overlays/win.png").convert("RGBA")
        overlay_lose = Image.open("assets/overlays/lose.png").convert("RGBA")
        overlay_dwin = Image.open("assets/overlays/dwin.png").convert("RGBA")
        overlay_dlose = Image.open("assets/overlays/dlose.png").convert("RGBA")
        # Assumiamo che win e lose abbiano le stesse dimensioni
        ow_w, ow_h = overlay_win.size
        ow_wd, ow_hd = overlay_dwin.size
    except FileNotFoundError:
        print("ERRORE FATALE: Mancano match_win.png o match_lose.png in assets/overlays/")
        return

    num_match = min(len(risultati_match), len(giocatori_casa), len(giocatori_ospiti))
    pos_overlay = [(142,990), (142,1034), (142,1081), (142,1125), (142,1209), (142,1254), (142,1301)]
    for i in range(num_match):

        risultato_str = risultati_match[i] # es. "3-0"

        # 5a. ANALISI VINCITORE DEL SINGOLO MATCH
        try:
            # Splitta "3-1" in ["3", "1"] e converte in numeri
            punti_casa_match, punti_ospiti_match = map(int, risultato_str.split("-"))
            # Se punti casa > punti ospiti, è vittoria per noi
            match_vinto_da_casa = punti_casa_match > punti_ospiti_match
        except ValueError:
            print(f"Errore formato risultato '{risultato_str}' alla riga {i}. Salto.")
            continue

        # 5b. SCEGLI E INCOLLA L'OVERLAY (Verde o Rosso)
        if i != 3: # Se non è il doppio, usa win/lose
            if match_vinto_da_casa:
                overlay_to_use = overlay_win
            else:
                overlay_to_use = overlay_lose
        
        else: # Se è il doppio, usa dwin/dlose
            if match_vinto_da_casa:
                overlay_to_use = overlay_dwin
            else:
                overlay_to_use = overlay_dlose
        
        # Calcola dove incollare (l'immagine overlay va centrata orizzontalmente e verticalmente rispetto alla riga)
        paste_x = pos_overlay[i][0]
        paste_y = pos_overlay[i][1]
        current_y_center = paste_y + (ow_h/2 if i != 3 else ow_hd/2) # Centro verticale dell'overlay
        # Incolla la striscia colorata
        base.paste(overlay_to_use, (paste_x, paste_y), mask=overlay_to_use)


        # Giocatore Casa (Allineato a DESTRA verso il centro -> anchor="rm")
        # X = W/2 - un po' di spazio (es. 100px dal centro)
        draw.text((W/2 - 200, current_y_center), giocatori_casa[i], font=font_nomi_bold, fill=TEXT_COLOR, anchor="mm", align= "center")

        # Risultato (Perfettamente centrato -> anchor="mm")
        y_rerult = pos_overlay[i][1] + ow_h/2 if i != 3 else pos_overlay[i][1] + ow_hd/2
        draw.text((W/2, y_rerult), risultato_str, font=font_ris_match_bold, fill=TEXT_COLOR, anchor="mm")

        # Giocatore Ospiti (Allineato a SINISTRA dal centro -> anchor="lm")
        # X = W/2 + un po' di spazio
        draw.text((W/2 + 200, current_y_center), giocatori_ospiti[i], font=font_nomi_bold, fill=TEXT_COLOR, anchor="mm", align= "center")


    # 6. SALVATAGGIO FINALE
    os.makedirs("output", exist_ok=True)
    # Crea un nome file pulito
    clean_casa = nome_team_casa_raw.replace("\n", " ").replace(" ", "_").replace(".", "")
    clean_ospiti = nome_team_ospiti_raw.replace("\n", " ").replace(" ", "_").replace(".", "")
    nome_file_output = f"output/match_{clean_casa}_vs_{clean_ospiti}.png"
    
    #base.save(nome_file_output)
    print(f"--- FINITO! Locandina salvata in: {nome_file_output} ---")
    return base

# --- BLOCCO DI TEST CON I DATI DELLA TUA IMMAGINE ---
if __name__ == "__main__":
    # Dati presi esattamente dalla tua immagine di esempio
    crea_locandina_v2(
        punteggio_casa=3,
        punteggio_ospiti=4,
        nome_team_casa="TT ACLI C2 LUGO",
        nome_team_ospiti="EVERPING CESENATICO PONENTE",
        nome_serie="C2/B",
        giocatori_casa=["Loboda D.", "Tabanelli A.", "Loboda J.", "Loboda J.\nPollino F.", "Loboda D.", "Loboda J.", "Tabanelli A."],
        # Nota: Ho aggiunto \n per il doppio per farlo andare a capo se il font lo supporta, altrimenti uscirà su una riga
        giocatori_ospiti=["Godio L.", "Castelvetro C.", "Montanari L.", "Castelvetro C.\nGodio L.", "Castelvetro C.", "Godio L.", "Montanari L."],
        risultati_match=["0-3", "0-3", "0-3", "3-0", "0-3", "3-1", "3-2"]
    )