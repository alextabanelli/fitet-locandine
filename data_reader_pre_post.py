#datareader_pre_post
from data_reader_pre_post_n import naviga_e_scarica_dati_n
from data_reader_pre_post_r import naviga_e_scarica_dati_r

def naviga_e_scarica_dati(nome_serie, nome_squadra_casa, giornata_numero, is_ritorno, post):
    if nome_serie.startswith("C1") or nome_serie.startswith("B2"):
        return naviga_e_scarica_dati_n(nome_serie, nome_squadra_casa, giornata_numero, is_ritorno, post)
    else:
        return naviga_e_scarica_dati_r(nome_serie, nome_squadra_casa, giornata_numero, is_ritorno, post)