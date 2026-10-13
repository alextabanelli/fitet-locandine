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


def derby_pre(
                nome_team_casa, 
                nome_team_ospiti,
                nome_serie,
                data,
                luogo,
                giornata=1,
):
                print("--- Inizio creazione locandina ---")

                # Preserve original names for file naming (avoid embedded newlines)

                nome_team_casa = nome_team_casa
                nome_team_ospiti = nome_team_ospiti
                bg_path1 = "assets/templates/derby.png" # Sfondo principale

                base = Image.open(bg_path1).convert("RGBA")
                W, H = base.size # Dimensioni totali immagine
                TEXT_COLOR = "white" # Tutti i testi sono bianchi
                font_serie = load_font("assets/fonts/Outfit-Bold.ttf", 60)
                font_luogo = load_font("assets/fonts/Outfit-Bold.ttf", 40)
                font_nomi = load_font("assets/fonts/Outfit-Bold.ttf", 30)
                font_data = load_font("assets/fonts/Outfit-Bold.ttf", 55)
                draw = ImageDraw.Draw(base)
                draw.text((W/2, 100),data, font=font_data, fill=TEXT_COLOR, anchor="mm", align="center")
                draw.text((W/2-5, 620),nome_serie, font=font_serie, fill=TEXT_COLOR, anchor="mm", align="center")
                nomi_team_casa_wrapped = wrap_text(nome_team_casa, font_nomi, 350)
                nomi_team_ospiti_wrapped = wrap_text(nome_team_ospiti, font_nomi, 350)
                draw.text((305, 720),nomi_team_casa_wrapped, font=font_nomi, fill=TEXT_COLOR, anchor="mm", align="center")
                draw.text((W-305, 720),nomi_team_ospiti_wrapped, font=font_nomi, fill=TEXT_COLOR, anchor="mm", align="center")
                diff = 70
                step = 1050 # Altezza di ogni riga di match
                draw.text((W/2, step),luogo['campo_principale'], font=font_luogo, fill=TEXT_COLOR, anchor="mm", align="center")
                draw.text((W/2, step + diff),luogo['indirizzo'], font=font_luogo, fill=TEXT_COLOR, anchor="mm", align="center")
                draw.text((W/2, step + 2*diff),luogo['cap'], font=font_luogo, fill=TEXT_COLOR, anchor="mm", align="center")                

                                

                

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
                derby_pre(
                                nome_team_casa="TT ACLI C2 LUGO",
                                nome_team_ospiti="USD Apuania Carrara Tennistavolo 'B'",
                                nome_serie="C2",
                                data="Domenica 24 Ottobre 15:00",
                                luogo={'campo_principale': 'PALESTRA SCUOLA MEDIA GHERARDI', 'indirizzo': 'VIA TARONI, 4-Lugo', 'cap': '48022 RA'},
                                giornata=1
                                )