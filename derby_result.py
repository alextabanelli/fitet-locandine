from PIL import Image, ImageDraw, ImageFont
import os
import difflib 
#import matplotlib.pyplot as plt
# --- FUNZIONE HELPER PER CARICARE I FONT IN SICUREZZA ---

def load_font(path, size, default_font=None):
                try:
                                # Pillow supporta dimensioni float nelle versioni recenti
                                return ImageFont.truetype(path, size)
                except OSError:
                                print(f"ATTENZIONE: Font non trovato in '{path}'. Uso un default brutto.")
                                return default_font if default_font else ImageFont.load_default()

def wrap_text(text, font, max_width):
                """Divide il testo in righe usando la larghezza reale del font."""
                words = text.split()
                lines = []
                current_line = []

                for word in words:
                                candidate = " ".join(current_line + [word])
                                if current_line and font.getlength(candidate) > max_width:
                                                lines.append(" ".join(current_line))
                                                current_line = [word]
                                else:
                                                current_line.append(word)

                if current_line:
                                lines.append(" ".join(current_line))

                return "\n".join(lines)


def derby_result(
                nome_team_casa, 
                nome_team_ospiti,
                nome_serie,
                giocatori_casa,
                giocatori_ospiti,
                punteggio,
                punteggi_partite,
                giornata=1
):
                print("--- Inizio creazione locandina ---")

                # Preserve original names for file naming (avoid embedded newlines)

                nome_team_casa = nome_team_casa
                nome_team_ospiti = nome_team_ospiti
                bg_path1 = "assets/templates/Derby_Result_2.png" # Sfondo principale

                base = Image.open(bg_path1).convert("RGBA")
                W, H = base.size # Dimensioni totali immagine
                TEXT_COLOR = "white" # Tutti i testi sono bianchi
                font_serie = load_font("assets/fonts/Montserrat-ExtraBold.ttf", 55)
                font_nomi = load_font("assets/fonts/Montserrat-ExtraBold.ttf", 25)
                font_squadre = load_font("assets/fonts/Montserrat-ExtraBold.ttf", 30)
                font_punteggi = load_font("assets/fonts/Montserrat-ExtraBold.ttf", 40)

                font_punteggio = load_font("assets/fonts/Anton-Regular.ttf", 120)
                draw = ImageDraw.Draw(base)
                draw.text((W/2-5, 775),nome_serie, font=font_serie, fill=TEXT_COLOR, anchor="mm", align="center")
                draw.text((W/2-5, 900),punteggio, font=font_punteggio, fill=TEXT_COLOR, anchor="mm", align="center")
                nomi_team_casa_wrapped = wrap_text(nome_team_casa, font_squadre, 350)
                nomi_team_ospiti_wrapped = wrap_text(nome_team_ospiti, font_squadre , 350)

                posx_casa = 290
                posy_casa = 750
                draw.text((posx_casa, posy_casa),nomi_team_casa_wrapped, font=font_squadre, fill=TEXT_COLOR, anchor="mm", align="center")
                draw.text((W-posx_casa, posy_casa),nomi_team_ospiti_wrapped, font=font_squadre, fill=TEXT_COLOR, anchor="mm", align="center")
                center_x1 = 335
                center_x2 = W-center_x1
                altezza_iniziale = 1003
                step = [50, 50, 65, 63, 50, 50, 50]  # Passo per ogni riga di giocatori
                for i in range(0, len(giocatori_casa)):
                                draw.text((W/2-10, altezza_iniziale + sum(step[:i])), punteggi_partite[i], font=font_punteggi, fill=TEXT_COLOR, anchor="mm", align="center")
                                draw.text((center_x1, altezza_iniziale +sum(step[:i])),giocatori_casa[i], font=font_nomi, fill=TEXT_COLOR, anchor="mm", align="center")
                                draw.text((center_x2, altezza_iniziale + sum(step[:i])),giocatori_ospiti[i], font=font_nomi, fill=TEXT_COLOR, anchor="mm", align="center")   


                # 6. SALVATAGGIO FINALE
                os.makedirs("output", exist_ok=True)
                nome_file_output1 = f"derby_{giornata}.png"
                base.save(nome_file_output1)
                # base2.save(nome_file_output2)
                # plt.figure(figsize=(W/100, H/100), dpi=100)
                # plt.imshow(base)
                # plt.axis('off')  # Disattiva gli assi
                print(f"--- FINITO! Locandina salvata ---")
                return base

# --- BLOCCO DI TEST CON I DATI DELLA TUA IMMAGINE ---
#punteggio=["5-2", "3-4", "4-3", "2-5", "1-6", "3-4"],
if __name__ == "__main__":
                # Dati presi esattamente dalla tua immagine di esempio
                derby_result(
                                nome_team_casa="TT ACLI C2 LUGO",
                                nome_team_ospiti="USD Apuania Carrara Tennistavolo 'B'",
                                nome_serie="C2",
                                giocatori_casa=["Loboda D.", "Tabanelli A.", "Loboda J.", "Loboda J.\nPollino F.", "Loboda D.", "Loboda J.", "Tabanelli A."],
                                # Nota: Ho aggiunto \n per il doppio per farlo andare a capo se il font lo supporta, altrimenti uscirà su una riga
                                giocatori_ospiti=["Godio L.", "Castelvetro C.", "Montanari L.", "Castelvetro C.\nGodio L.", "Castelvetro C.", "Godio L.", "Montanari L."],
                                punteggio="5 - 2",
                                punteggi_partite =["0-3", "0-3", "0-3", "3-0", "0-3", "3-1", "3-2"],
                                )