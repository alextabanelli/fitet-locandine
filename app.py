import streamlit as st
import time
import zipfile
from io import BytesIO

# --- IMPORT DAI TUOI FILE ---
try:
    from data_reader import naviga_e_scarica_dati
    from template_generator import crea_locandina_v2
except ImportError as e:
    st.error(f"Errore nell'importazione dei file: {e}. Assicurati che data_reader.py e template_generator.py siano nella stessa cartella.")
    st.stop()
    
def set_pwa_icon(icon_path):
    """Inietta i meta tag necessari per l'icona sul telefono (Android/iOS)"""
    try:
        with open(icon_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        
        icon_html = f"""
            <link rel="apple-touch-icon" href="data:image/png;base64,{data}">
            <link rel="icon" sizes="192x192" href="data:image/png;base64,{data}">
            <link rel="shortcut icon" href="data:image/png;base64,{data}">
        """
        st.markdown(icon_html, unsafe_allow_html=True)
    except Exception:
        # Se il file non esiste ancora, l'app non crasha
        pass
# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="FITET Locandine Generator",
    page_icon="assets/logo_app.png", # Icona della scheda del browser
    layout="centered"
)

# Applichiamo l'icona per la schermata del telefono
set_pwa_icon("assets/logo_app.png")

st.set_page_config(
    page_title="FITET Locandine Generator",
    layout="centered"
)

# Inizializzazione Database Squadre
if 'teams_db' not in st.session_state:
    st.session_state['teams_db'] = {
        "TT ACLI C2 LUGO": "C2/B",
        "TT ACLI D1 JUNIOR RAVENNA": "D1/B",
        "TT ACLI D1 ALFA LUGO": "D1/C",
        "TT ACLI D1 BETA LUGO": "D1/B",
        "TT ACLI D1 OVER LUGO": "D1/C",
        "TT ACLI D2 LUGO": "D2/E",
        "TT ACLI D3 JUNIOR LUGO": "D3/E",
        "TT ACLI D3 ALCHIMIA RAVENNA": "D3/F",
        "TT ACLI D3 DECOWARM RAVENNA": "D3/G"
    }

# --- 2. CSS CUSTOM (STILE FORNITO + ANIMAZIONE PALLINA) ---
st.markdown("""
    <style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:ital,wght@0,300;0,700;1,900&family=Poppins:wght@300;400;600&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

    /* --- VARIABILI COLORI --- */
    :root {
        --primary-blue: #00f2ff;
        --primary-red: #ff2a2a;
        --dark-bg: #0a0e17;
        --card-bg: rgba(16, 24, 40, 0.85);
        --glass-border: rgba(255, 255, 255, 0.1);
        --text-main: #ffffff;
        --text-muted: #a0a0a0;
    }

    /* --- SFONDO GENERALE --- */
    .stApp {
        background-color: var(--dark-bg);
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(0, 242, 255, 0.2) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(255, 42, 42, 0.2) 0%, transparent 40%),
            url('https://images.unsplash.com/photo-1534158914592-062992bbe79e?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(10, 14, 23, 0.85);
        z-index: -1;
        pointer-events: none;
    }

    /* --- HEADER STYLES --- */
    h1 {
        font-family: 'Exo 2', sans-serif !important;
        font-weight: 900 !important;
        font-size: 3rem !important;
        letter-spacing: 2px !important;
        text-transform: uppercase;
        background: linear-gradient(to right, var(--primary-blue), #ffffff, var(--primary-red));
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-shadow: 0 0 20px rgba(0, 242, 255, 0.5);
        text-align: center;
        margin-bottom: 5px !important;
        padding-top: 0 !important;
    }
    
    .header-subtitle {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.9rem;
        letter-spacing: 1px;
        margin-bottom: 30px;
        font-family: 'Poppins', sans-serif;
    }

    .header-icon-container {
        text-align: center;
        margin-bottom: 10px;
    }
    
    .header-icon-main {
        font-size: 2.5rem;
        color: #fff;
        animation: float 3s ease-in-out infinite;
        text-shadow: 0 0 15px var(--primary-blue);
    }

    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    /* --- CARD CONTAINER --- */
    div[data-testid="stVerticalBlock"] > div:has(div.custom-card-start) {
        background: var(--card-bg);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 0 40px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(255, 255, 255, 0.05);
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
    }

    /* Bordo Neon Superiore */
    div[data-testid="stVerticalBlock"] > div:has(div.custom-card-start)::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--primary-blue), transparent, var(--primary-red));
        z-index: 2;
    }

    /* --- ANIMAZIONE PALLINA PING PONG --- */
    .pong-container {
        width: 100%;
        height: 60px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 12px;
        position: relative;
        overflow: hidden;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
    }
            
    


    .pong-ball {
        width: 14px;
        height: 14px;
        background-color: #fff;
        border-radius: 50%;
        position: absolute;
        
        /* Ombra neon */
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.9), 0 0 20px var(--primary-blue);
        
        /* DUE ANIMAZIONI INDIPENDENTI:
        1. bounceX: Sposta la palla da Sinistra a Destra
        2. bounceY: Sposta la palla da Sopra a Sotto
        
        Uso due durate "prime" (es. 4.1s e 3.3s) per evitare che si sincronizzino,
        creando un movimento che sembra casuale e tocca tutti i bordi.
        */
        animation: 
            bounceX 2.1s linear infinite alternate,
            bounceY 3.2s linear infinite alternate;
    }

    /* Movimento Orizzontale (Lato Sinistro <-> Lato Destro) */
    @keyframes bounceX {
        0% { left: 0; }
        100% { left: calc(100% - 14px); } /* 100% meno la larghezza della palla per non uscire */
    }

    /* Movimento Verticale (Lato Alto <-> Lato Basso) */
    @keyframes bounceY {
        0% { top: 0; }
        100% { top: calc(100% - 14px); } /* 100% meno l'altezza della palla */
    }

    /* --- WIDGET STYLING --- */
    label {
        color: var(--text-muted) !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        font-family: 'Poppins', sans-serif !important;
    }

    div[data-baseweb="select"] > div {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid #333 !important;
        color: #fff !important;
        border-radius: 10px !important;
        font-family: 'Poppins', sans-serif !important;
        padding: 8px 12px !important;
        height: auto !important;
        align-items: center;
    }

    .stNumberInput input, .stTextInput input {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid #333 !important;
        color: #fff !important;
        border-radius: 10px !important;
        font-family: 'Poppins', sans-serif !important;
        padding: 10px 12px !important;
    }
    
    div[data-baseweb="select"] > div:focus-within, .stTextInput input:focus, .stNumberInput input:focus-within {
        border-color: var(--primary-blue) !important;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.2) !important;
    }

    label[data-testid="stCheckbox"] span {
        color: #fff !important;
    }

    /* --- BOTTONI --- */
    div[data-testid="column"]:nth-of-type(1) button {
        background: linear-gradient(135deg, #0061ff, #00f2ff) !important;
        box-shadow: 0 4px 15px rgba(0, 242, 255, 0.3) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Exo 2', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        padding: 20px !important;
        transition: transform 0.2s !important;
    }
    
    div[data-testid="column"]:nth-of-type(2) button {
        background: linear-gradient(135deg, #ff9900, #ff2a2a) !important;
        box-shadow: 0 4px 15px rgba(255, 42, 42, 0.3) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Exo 2', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        padding: 20px !important;
        transition: transform 0.2s !important;
    }

    button:hover {
        transform: translateY(-3px);
        filter: brightness(1.1);
    }

    .reset-container button {
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: var(--text-muted) !important;
        width: 100%;
        margin-top: 20px;
    }
    .reset-container button:hover {
        border-color: var(--primary-red) !important;
        color: var(--primary-red) !important;
        background: rgba(255, 42, 42, 0.05) !important;
    }

    .custom-badge {
        background: rgba(255, 255, 255, 0.1);
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        color: var(--primary-blue);
        display: inline-block;
        margin-top: 5px;
    }

    .card-title {
        font-family: 'Exo 2', sans-serif;
        font-size: 1.2rem;
        color: #fff;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 10px;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
            
    /* Stile per il link dell'icona */
    a.icon-home-link {
        text-decoration: none; /* Toglie la sottolineatura */
        display: inline-block; /* Necessario per l'animazione */
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Rimbalzo elastico */
    }

    /* Effetto Hover: ingrandisce e ruota leggermente la racchetta */
    a.icon-home-link:hover {
        transform: scale(1.2);
        cursor: pointer;
    }
    
    </style>
    """, unsafe_allow_html=True)

# --- 3. DIALOG GESTIONE SQUADRE ---
@st.dialog("Gestione Squadre")
def manage_teams_dialog():
    st.markdown("### ⚙️ Database Squadre")
    
    c1, c2 = st.columns([2, 1])
    new_name = c1.text_input("Nome", placeholder="Es. TT ACLI LUGO")
    new_series = c2.text_input("Serie", placeholder="C2/B")
    
    if st.button("➕ Aggiungi", type="primary"):
        if new_name and new_series:
            st.session_state['teams_db'][new_name] = new_series
            st.rerun()
            
    st.markdown("---")
    for team, series in list(st.session_state['teams_db'].items()):
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.text(team)
        c2.caption(series)
        if c3.button("🗑️", key=f"del_{team}"):
            del st.session_state['teams_db'][team]
            st.rerun()

# --- 4. LAYOUT HEADER ---
st.markdown("""
    <div class="header-icon-container">
        <a href="/" target="_self" class="icon-home-link" title="Torna alla Home">
            <div class="header-icon-main">🏓</div>
        </a>
    </div>
    
    <h1>FITET Locandine</h1>
    <div class="header-subtitle">GENERATORE AUTOMATICO PER PARTITE DI TENNISTAVOLO</div>
""", unsafe_allow_html=True)

# MARCATORE INIZIO CARD (Per il CSS)
st.markdown("""<div class="custom-card-start">
                <div class="pong-ball"></div>
            </div>""", unsafe_allow_html=True)

# --- CONTENUTO CARD ---

st.markdown("""
    <div class="card-title">
        ✨ Configurazione Partita
    </div>
""", unsafe_allow_html=True)

# RIGA 1: SQUADRA e SETTINGS
col_team, col_settings = st.columns([6, 1])
with col_team:
    teams_list = list(st.session_state['teams_db'].keys())
    squadra_scelta = st.selectbox("Squadra", teams_list)
    serie_auto = st.session_state['teams_db'][squadra_scelta]
    
    # Badge Serie Custom HTML
    st.markdown(f'<span class="custom-badge">Serie associata: {serie_auto}</span>', unsafe_allow_html=True)

with col_settings:
    st.write("") 
    st.write("") 
    if st.button("⚙️", help="Gestisci"):
        manage_teams_dialog()

st.write("") # Spaziatore

# RIGA 2: GIORNATA e RITORNO
col_day, col_return = st.columns([3, 2])
with col_day:
    giornata = st.number_input("Giornata", min_value=1, max_value=20, value=1, step=1)

with col_return:
    st.write("")
    st.write("")
    is_ritorno = st.toggle("Girone di Ritorno", value=False)

st.write("") # Spaziatore

# RIGA 3: OPZIONI AVANZATE (Nascoste nell'expander stilizzato di default)
with st.expander("🔧 Opzioni Avanzate (Nomi Doppi)"):
    st.caption("Seleziona i match dove applicare la formattazione speciale per cognomi doppi.")
    ec1, ec2 = st.columns(2)
    skip_casa = ec1.multiselect("Noi (Match #)", range(1, 10))
    skip_ospiti = ec2.multiselect("Loro (Match #)", range(1, 10))

st.markdown("<br>", unsafe_allow_html=True)

# RIGA 4: BOTTONI AZIONE (CSS targeting via nth-of-type)
col_act1, col_act2 = st.columns(2)

with col_act1:
    # Bottone GENERA (Blu)
    if st.button("📷 GENERA LOCANDINA"):
        status = st.status("Elaborazione in corso...", expanded=True)
        try:
            status.write("📡 Connessione al portale FITET...")
            dati = naviga_e_scarica_dati(
                serie_auto, squadra_scelta, giornata, 
                is_ritorno, skip_casa, skip_ospiti
            )
            
            if dati:
                status.write("🎨 Creazione grafica...")
                img = crea_locandina_v2(**dati)
                status.update(label="✅ Fatto!", state="complete", expanded=False)
                
                # Visualizza
                st.image(img, caption=f"{dati['punteggio_casa']} - {dati['punteggio_ospiti']}")
                
                # Download
                buf = BytesIO()
                img.save(buf, format="PNG")
                st.download_button(
                    "📥 Salva Immagine", 
                    data=buf.getvalue(), 
                    file_name=f"{squadra_scelta}_G{giornata}.png", 
                    mime="image/png",
                    use_container_width=True
                )
            else:
                status.update(label="❌ Errore", state="error")
                st.error("Dati non trovati.")
        except Exception as e:
            status.update(label="⚠️ Errore critico", state="error")
            st.error(f"{e}")

with col_act2:
    # Bottone DOWNLOAD ALL (Rosso/Arancio)
    if st.button("📦 GENERA TUTTE (ZIP)"):
        status = st.status("Batch Download...", expanded=True)
        zip_buf = BytesIO()
        cnt = 0
        tot = len(st.session_state['teams_db'])
        
        try:
            with zipfile.ZipFile(zip_buf, "w") as zf:
                for i, (tm, ser) in enumerate(st.session_state['teams_db'].items()):
                    status.write(f"[{i+1}/{tot}] {tm}...")
                    try:
                        d = naviga_e_scarica_dati(ser, tm, giornata, is_ritorno)
                        if d:
                            img = crea_locandina_v2(**d)
                            ib = BytesIO()
                            img.save(ib, format="PNG")
                            zf.writestr(f"{tm.replace(' ','_')}_G{giornata}.png", ib.getvalue())
                            cnt += 1
                    except: pass 
            
            status.update(label=f"✅ Completato ({cnt} locandine)", state="complete", expanded=False)
            if cnt > 0:
                st.download_button(
                    "📥 SCARICA ZIP", 
                    data=zip_buf.getvalue(), 
                    file_name=f"Giornata_{giornata}.zip", 
                    mime="application/zip",
                    use_container_width=True
                )
        except Exception as e:
            st.error(str(e))

# MARCATORE FINE CARD
st.markdown('<div class="custom-card-end"></div>', unsafe_allow_html=True)

# FOOTER RESET (Contenitore specifico per targeting CSS)
st.markdown('<div class="reset-container">', unsafe_allow_html=True)
if st.button("🧹 Pulisci Schermata / Nuova Ricerca"):
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
