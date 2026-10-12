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

def stampa(overlay, base, pos, nome_team_casa, nome_team_ospiti, serie, data,font_data, font_nomi_bold, font_ris_match_bold,font_number, TEXT_COLOR, punteggio=None):
    serie = serie[0]+serie[1]
    W, H = base.size # Dimensioni totali immagine
    draw = ImageDraw.Draw(base)
    seriepos = W/2 - 40    
    nome_team_casa_wrapped = wrap_text(nome_team_casa, 17)
    nome_team_ospiti_wrapped = wrap_text(nome_team_ospiti, 17)
    base.paste(overlay[0], (40, pos), mask=overlay[0])
    base.paste(overlay[1], (525, pos+30), mask=overlay[1])
    base.paste(overlay[2], (610, pos), mask=overlay[2])
    # Giocatore Casa (Allineato a DESTRA verso il centro -> anchor="rm")
    # X = W/2 - un po' di spazio (es. 100px dal centro)
    if punteggio is not None:
          punt = list(punteggio)
          punteggi = punt[0]
          draw.text((W/2-100, pos+70), punteggi, font=font_number, fill=TEXT_COLOR, anchor="mm")
          punteggi = punt[4]
          draw.text((W/2+100, pos+70), punteggi, font=font_number, fill=TEXT_COLOR, anchor="mm")
          draw.text((265, pos+70), nome_team_casa_wrapped, font=font_nomi_bold, fill=TEXT_COLOR, anchor="mm", align= "center")

    else:
          draw.text((W/2, pos-10), data, font=font_data, fill=TEXT_COLOR, anchor="mm")
          draw.text((280, pos+70), nome_team_casa_wrapped, font=font_nomi_bold, fill=TEXT_COLOR, anchor="mm", align= "center")
    # Risultato (Perfettamente centrato -> anchor="mm")
    draw.text((W/2, pos+70), serie, font=font_ris_match_bold, fill=TEXT_COLOR, anchor="mm")

    # Giocatore Ospiti (Allineato a SINISTRA dal centro -> anchor="lm")
    # X = W/2 + un po' di spazio
    draw.text((855, pos+70), nome_team_ospiti_wrapped, font=font_nomi_bold, fill=TEXT_COLOR, anchor="mm", align= "center")



def stampa_riga_match(nomi_societa, base, win, casa, derby, nome_team_casa, nome_team_ospiti, pos, serie,data,punteggio = None):
    base = base
    W, H = base.size # Dimensioni totali immagine
    draw = ImageDraw.Draw(base)
    try:
        overlay_wins = Image.open("assets/overlays/wins.png").convert("RGBA")
        overlay_winr = Image.open("assets/overlays/winr.png").convert("RGBA")
        overlay_loses = Image.open("assets/overlays/loses.png").convert("RGBA")
        overlay_loser = Image.open("assets/overlays/loser.png").convert("RGBA")
        overlay_grays = Image.open("assets/overlays/grays.png").convert("RGBA")
        overlay_grayr = Image.open("assets/overlays/grayr.png").convert("RGBA")
        overlay_derbys	= Image.open("assets/overlays/derbys.png").convert("RGBA")
        overlay_derbyr = Image.open("assets/overlays/derbyr.png").convert("RGBA")
        overlay_serie = Image.open("assets/overlays/serie.png").convert("RGBA")
        overlay_casas = Image.open("assets/overlays/casas.png").convert("RGBA")
        overlay_casar = Image.open("assets/overlays/casar.png").convert("RGBA")
        overlay_avvs = Image.open("assets/overlays/avvs.png").convert("RGBA")
        overlay_avvr = Image.open("assets/overlays/avvr.png").convert("RGBA")
                                
    except FileNotFoundError:
        print("ERRORE FATALE: Mancano match_win.png o match_lose.png in assets/overlays/")
        return
    TEXT_COLOR = "white" # Tutti i testi sono bianchi

    # Usiamo i percorsi e le dimensioni esatte richieste
    # N.B. Se non hai i file .ttf, il programma userà un font di default.
    font_nomi_bold = load_font("assets/fonts/Montserrat-ExtraBold.ttf", 30)
    font_number = load_font("assets/fonts/Montserrat-ExtraBold.ttf", 60)
    font_ris_match_bold = load_font("assets/fonts/Montserrat-ExtraBold.ttf", 30)
    font_data = load_font("assets/fonts/Montserrat-ExtraBold.ttf", 25)

    if punteggio is None:
        if nome_team_casa in nomi_societa and nome_team_ospiti in nomi_societa:
                stampa([overlay_casas, overlay_serie, overlay_casar], base, pos, nome_team_casa, nome_team_ospiti, serie, data, font_data, font_nomi_bold, font_ris_match_bold, font_number, TEXT_COLOR)
        elif nome_team_casa in nomi_societa:
            stampa([overlay_casas, overlay_serie, overlay_avvr], base, pos, nome_team_casa, nome_team_ospiti, serie, data, font_data, font_nomi_bold, font_ris_match_bold, font_number, TEXT_COLOR)
        else:
            stampa([overlay_avvs, overlay_serie, overlay_casar], base, pos, nome_team_casa, nome_team_ospiti, serie, data, font_data, font_nomi_bold, font_ris_match_bold, font_number, TEXT_COLOR)
    else:
        if win:
            if casa:
                if derby:
                    stampa([overlay_derbys, overlay_serie, overlay_grayr], base, pos, nome_team_casa, nome_team_ospiti, serie, data, font_data, font_nomi_bold, font_ris_match_bold, font_number, TEXT_COLOR, punteggio)
                else:
                    stampa([overlay_wins, overlay_serie, overlay_grayr], base, pos, nome_team_casa, nome_team_ospiti, serie, data, font_data, font_nomi_bold, font_ris_match_bold, font_number, TEXT_COLOR, punteggio)
            else:
                if derby:
                    stampa([overlay_grays, overlay_serie, overlay_derbyr], base, pos, nome_team_casa, nome_team_ospiti, serie, data, font_data, font_nomi_bold, font_ris_match_bold, font_number, TEXT_COLOR, punteggio)
                else:
                    stampa([overlay_grays, overlay_serie, overlay_winr], base, pos, nome_team_casa, nome_team_ospiti, serie, data, font_data, font_nomi_bold, font_ris_match_bold, font_number, TEXT_COLOR, punteggio)
        else:
            if casa:
                if derby:
                    stampa([overlay_grays, overlay_serie, overlay_derbyr], base, pos, nome_team_casa, nome_team_ospiti, serie, data, font_data, font_nomi_bold, font_ris_match_bold, font_number, TEXT_COLOR, punteggio)
                else:
                    stampa([overlay_grays, overlay_serie, overlay_loser], base, pos, nome_team_casa, nome_team_ospiti, serie, data, font_data, font_nomi_bold, font_ris_match_bold, font_number, TEXT_COLOR, punteggio)
            else:
                if derby:
                    stampa([overlay_derbys, overlay_serie, overlay_grayr], base, pos, nome_team_casa, nome_team_ospiti, serie, data, font_data, font_nomi_bold, font_ris_match_bold, font_number, TEXT_COLOR, punteggio)
                else:
                    stampa([overlay_loses, overlay_serie, overlay_grayr], base, pos, nome_team_casa, nome_team_ospiti, serie, data, font_data, font_nomi_bold, font_ris_match_bold, font_number, TEXT_COLOR, punteggio)


def crea_locandina_v2(
                giornata,
                nomi_societa,
                nome_team_casa, 
                nome_team_ospiti,
                nome_serie,
                data,
                punteggio =	None        
):
                print("--- Inizio creazione locandina ---")
                #elimino eventuali duplicati tra casa e ospiti

                nome_team_casa_filtrati = []
                nome_team_ospiti_filtrati = []
                nome_serie_filtrati = []
                data_filtrati = []
                punteggio_filtrati = [] if punteggio is not None else None
                coppie_gia_viste = set()

                for i, team_casa in enumerate(nome_team_casa):
                      team_ospite = nome_team_ospiti[i]
                      coppia = frozenset((team_casa, team_ospite))
                      if coppia in coppie_gia_viste:
                            print(f"ATTENZIONE: La coppia '{team_casa} - {team_ospite}' è già presente. Salto il match duplicato.")
                            continue
                      coppie_gia_viste.add(coppia)

                      nome_team_casa_filtrati.append(team_casa)
                      nome_team_ospiti_filtrati.append(team_ospite)
                      nome_serie_filtrati.append(nome_serie[i])
                      data_filtrati.append(data[i])
                      if punteggio is not None:
                            punteggio_filtrati.append(punteggio[i])

                nome_team_casa = nome_team_casa_filtrati
                nome_team_ospiti = nome_team_ospiti_filtrati
                nome_serie = nome_serie_filtrati
                data = data_filtrati
                punteggio = punteggio_filtrati
                # Preserve original names for file naming (avoid embedded newlines)
                nomi_societa = nomi_societa
                nome_team_casa = nome_team_casa
                nome_team_ospiti = nome_team_ospiti
                pos1 = 250 # Posizione verticale iniziale per la prima riga di match
                pos2 = 30
                bg_path1 = "assets/templates/first.png" # Sfondo principale
                bg_path2 = "assets/templates/second.png" # Sfondo secondario (per eventuali altre versioni)

                base1 = Image.open(bg_path1).convert("RGBA")
                base2	= Image.open(bg_path2).convert("RGBA")
                W, H = base1.size # Dimensioni totali immagine
                TEXT_COLOR = "white" # Tutti i testi sono bianchi
                font_giornata = load_font("assets/fonts/Montserrat-ExtraBold.ttf", 50)
                font_titolo	= load_font("assets/fonts/Montserrat-ExtraBold.ttf", 90)
                draw = ImageDraw.Draw(base1)
                draw.text((W/2, 70), f"DAY {giornata}", font=font_giornata, fill=TEXT_COLOR, anchor="mm")
                pos = pos1
                base = base1
                todiff = 0
                step = 165 # Altezza di ogni riga di match
                if punteggio is None or len(punteggio) == 0:
                    draw.text((W/2, 160), f"SCHEDULE", font=font_titolo, fill=TEXT_COLOR, anchor="mm")
                    print(f"--- Creazione locandina per {len(nome_team_casa)} match ---")
                    for i in range(len(nome_team_casa)):
                        if (pos+(i*step)-todiff)+130 > H:
                            pos = pos2
                            base = base2
                            todiff = i*160
                        if (nome_team_casa[i] in nomi_societa) and (nome_team_ospiti[i] in nomi_societa):
                            derby = True
                        else:
                            derby = False
                        if (nome_team_casa[i] in nomi_societa):
                            casa = True
                        else:
                            casa = False
                        win = False
                        stampa_riga_match(nomi_societa, base, win, casa, derby, nome_team_casa[i], nome_team_ospiti[i], (pos + i*step)-todiff, nome_serie[i], data[i])
                else:
                    for i in range(len(punteggio)):
                        if (pos+(i*step)-todiff)+130 > H:
                            pos = pos2
                            base = base2
                            todiff = i*160
                        draw.text((W/2, 160), f"MATCHES RESULT", font=font_titolo, fill=TEXT_COLOR,anchor="mm")
                        if punteggio[i] == "7 - 0" or	punteggio[i] == "6 - 1" or punteggio[i] == "5 - 2" or punteggio[i] == "4 - 3":
                            if nome_team_casa[i] in nomi_societa:
                                casa = True
                                win = True
                            else:
                                casa = False
                                win = False
                        else:
                            if nome_team_casa[i] in nomi_societa:
                                casa = True
                                win = False
                            else:
                                casa = False
                                win = True
                        if (nome_team_casa[i] in nomi_societa) and (nome_team_ospiti[i] in nomi_societa):
                            derby = True
                        else:
                            derby = False
                        stampa_riga_match(nomi_societa, base, win, casa, derby, nome_team_casa[i], nome_team_ospiti[i], (pos + i*step)-todiff, nome_serie[i],data[i], punteggio[i])

                                

                

                # 6. Ritorno immagini
                print(f"--- FINITO! Locandina generata ---")
                return base1, base2

# --- BLOCCO DI TEST CON I DATI DELLA TUA IMMAGINE ---
#punteggio=["5-2", "3-4", "4-3", "2-5", "1-6", "3-4"],
if __name__ == "__main__":
                # Dati presi esattamente dalla tua immagine di esempio
                crea_locandina_v2(
                                giornata=1,
                                nomi_societa=["TT ACLI C2 LUGO", "TT ACLI D1	LUGO", "TT ACLI D2 LUGO", "TT ACLI D3 LUGO", "TT ACLI D4 LUGO", "TT ACLI D5 LUGO", "TT ACLI D6 LUGO", "TT ACLI 1", "TT ACLI 2", "TT ACLI 3", "TT ACLI 4", "TT ACLI 5", "TT ACLI 6"],
                                nome_team_casa=["TT ACLI C2 LUGO","OPPPPPPPPP OPPPOPOPO  OPPO PPOOPO 4", "EVERPING CESENATICO PONENTE B", "DINAMIS", "TT ACLI D3 LUGO", "TT ACLI D6 LUGO","TT ACLI 1", "TT ACLI 2", "TT ACLI 3", "TT ACLI 4",	"TT ACLI 5", "TT ACLI 6"],
                                nome_team_ospiti=["USD Apuania Carrara Tennistavolo 'B'","TT ACLI D2 LUGO", "TT ACLI D3 LUGO", "TT ACLI D4 LUGO", "IMOLA TT", "TT ACLI D5 LUGO", "OPPON 1", "OPPON 2", "OPPON 3", "OPPPPPPPPP OPPPOPOPO  OPPO PPOOPO 4", "OPPON 5", "OPPON 6"],
                                nome_serie=["C2", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11"],
                                data=["Domenica 24 ottobre 15:00", "Lunedì 25 ottobre 15:00", "Martedì 26 ottobre 15:00", "Mercoledì 27 ottobre 15:00", "Giovedì 28 ottobre 15:00", "Venerdì 29 ottobre 15:00", "Sabato 30 ottobre 15:00", "Domenica 31 ottobre 15:00", "Lunedì 1 novembre 15:00", "Martedì 2 novembre 15:00", "Giovedì 3 novembre 15:00", "Venerdì 4 novembre 15:00"],
                                punteggio=["5-2", "3-4", "4-3", "2-5", "1-6", "3-4", "7-0", "6-1", "5-2", "4-3", "3-4", "2-5"]
                                
                )
