"""Cerca tutti i derby tra le squadre della lista e genera le locandine.

Un derby viene identificato quando due squadre appartengono alla stessa serie.
Ogni coppia viene elaborata una sola volta, anche se compare in entrambe le
posizioni della lista. Per ogni coppia vengono cercate e generate la locandina
dell'andata e quella del ritorno.
"""

from itertools import combinations
from pathlib import Path
import re

import matplotlib.pyplot as plt

from derby import naviga_e_scarica_dati_derby
from derby_pre import derby_pre


OUTPUT_DIR = Path("output")


def _normalizza_testo(valore):
    """Normalizza nomi e serie per i confronti, senza modificarne la grafica."""
    return " ".join(str(valore).split()).casefold()


def _nome_file_sicuro(valore):
    """Rende un nome adatto a essere usato come nome di file."""
    nome = re.sub(r"[^A-Za-z0-9._-]+", "_", str(valore).strip())
    return nome.strip("._") or "squadra"


def _coppie_per_serie(nomi_societa, serie):
    """Restituisce le coppie di squadre che condividono la stessa serie."""
    if len(nomi_societa) != len(serie):
        raise ValueError("nomi_societa e serie devono avere la stessa lunghezza")

    gruppi = {}
    for nome_squadra, nome_serie in zip(nomi_societa, serie):
        chiave_serie = _normalizza_testo(nome_serie)
        gruppi.setdefault(chiave_serie, []).append((nome_squadra, nome_serie))

    coppie = []
    for squadre in gruppi.values():
        coppie.extend(combinations(squadre, 2))
    return coppie


def _genera_locandine_derby(coppia, dati_derby):
    """Genera e salva le due locandine restituite dalla logica di derby."""
    squadra_a, squadra_b = coppia
    OUTPUT_DIR.mkdir(exist_ok=True)

    immagini = []
    fasi = ("andata", "ritorno")
    for indice, fase in enumerate(fasi):
        base = derby_pre(
            nome_team_casa=dati_derby["nome_casa"][indice],
            nome_team_ospiti=dati_derby["nome_ospiti"][indice],
            nome_serie=dati_derby["nome_serie"][indice],
            data=dati_derby["data"][indice],
            luogo=dati_derby["luogo"][indice],
            giornata=indice + 1,
        )

        nome_file = (
            f"derby_{_nome_file_sicuro(squadra_a)}_"
            f"{_nome_file_sicuro(squadra_b)}_"
            f"{_nome_file_sicuro(dati_derby['nome_serie'][indice])}_{fase}.png"
        )
        percorso = OUTPUT_DIR / nome_file
        base.save(percorso)
        immagini.append((percorso, base))

    return immagini


def get_all_derby(nomi_societa, serie, giornate=7, mostra_debug=True):
    """Genera le locandine di andata e ritorno per tutti i derby trovati.

    Args:
        nomi_societa: lista dei nomi delle squadre.
        serie: lista parallela con la serie di ogni squadra.
        giornate: numero massimo di giornate da controllare per ciascuna fase.
        mostra_debug: se True, mostra ogni immagine con matplotlib.

    Returns:
        Lista di immagini PIL per tutte le locandine create.
    """
    if giornate < 1:
        raise ValueError("giornate deve essere maggiore di zero")

    risultati = []
    coppie = _coppie_per_serie(nomi_societa, serie)
    print(f"Trovate {len(coppie)} coppie candidate al derby.")

    for (squadra_a, serie_a), (squadra_b, _) in coppie:
        coppia = (squadra_a, squadra_b)
        print(f"\nDerby candidato: {squadra_a} vs {squadra_b} ({serie_a})")

        dati_derby = naviga_e_scarica_dati_derby(
            nomi_societa=[squadra_a, squadra_b],
            nome_serie=serie_a,
            nome_squadra=squadra_a,
            giornate=giornate,
        )
        if not dati_derby or len(dati_derby["nome_casa"]) < 2:
            print("  Andata e ritorno non trovati.")
            continue

        immagini_derby = _genera_locandine_derby(
                coppia=coppia,
                dati_derby=dati_derby,
            )
        risultati.extend(immagine for _, immagine in immagini_derby)
        for percorso, immagine in immagini_derby:
            plt.figure(figsize=(immagine.width / 100, immagine.height / 100))
            plt.imshow(immagine)
            plt.axis("off")
            if mostra_debug:
                plt.show()
            else:
                plt.close()
            print(f"  Locandina salvata in: {percorso}")

    print(f"\nCreate {len(risultati)} locandine.")
    return risultati


if __name__ == "__main__":
    nomi_squadre = [
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
        "TT ACLI D3 ALFA LUGO",
    ]
    serie_squadra = [
        "C1/H", "D1/D", "D2/F", "D2/F", "D3/H", "D3/G",
        "D3/E", "D1/C", "D1/D", "D2/E", "D3/H", "D3/E",
    ]

    get_all_derby(nomi_squadre, serie_squadra, giornate=7)
