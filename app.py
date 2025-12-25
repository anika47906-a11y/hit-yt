import streamlit as st
import pandas as pd
import urllib.parse
import cv2
import numpy as np
from pyzbar.pyzbar import decode

# HIER DEINEN AKTUELLEN CSV-LINK EINFÜGEN
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRc6H9CTr8f_H1LxYyh073DgcjjlwZzHxtcY1aTjS7YSErz0sGzni6PYKbk9lJhN66hUdplPKn1f1a-/pub?output=csv"

st.set_page_config(page_title="Hitster Pro Scanner", layout="centered")

# CSS für ein riesiges Kamerafenster
st.markdown("""
    <style>
    /* Vergrößert das Kamera-Input Fenster */
    div[data-testid="stCameraInput"] {
        width: 100% !important;
    }
    video {
        border-radius: 15px;
        border: 3px solid #FF4B4B;
        height: 500px !important; /* Hier kannst du die Höhe anpassen */
        object-fit: cover;
    }
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_data():
    try:
        data = pd.read_csv(SHEET_CSV_URL, dtype={'qr_id': str})
        return data, None
    except Exception as e:
        return None, str(e)

def show_play_ui(song_row):
    """Zentralfunktion um den Play-Button anzuzeigen"""
    artist = song_row['artist']
    title = song_row['title']
    
    # YouTube Music Link generieren
    search_term = urllib.parse.quote(f"{artist} {title}")
    yt_link = f"https://music.youtube.com/search?q={search_term}"
    
    st.divider()
    st.success("🎯 Song in der Liste gefunden!")
    
    # Der Play-Button öffnet YT Music in einem neuen Tab
    st.link_button("▶️ JETZT AUF YT-MUSIC ABSPIELEN", yt_link, type="primary")
    
    # Lösung verstecken
    with st.expander("🔎 Lösung anzeigen (Spoiler!)"):
        st.subheader(f"{artist} - {title}")

# --- HAUPT APP ---
st.title("🎧 Hitster Pro-Scanner")

df, error = load_data()

if error:
    st.error("⚠️ Verbindung zur Google-Tabelle fehlt. Bitte CSV-Link prüfen.")
    st.stop()

# 1. Kamera-Scan (Jetzt viel größer durch CSS)
st.subheader("📸 QR-Code Scannen")
img_file = st.camera_input("Halte die Karte mittig ins Bild")

if img_file:
    bytes_data = img_file.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    detected = decode(cv2_img)
    
    if detected:
        card_id = detected[0].data.decode("utf-8").split('/')[-1].strip()
        st.info(f"Erkannte ID: {card_id}")
        
        match = df[df['qr_id'] == card_id]
        if not match.empty:
            show_play_ui(match.iloc[0])
        else:
            st.warning(f"ID {card_id} ist nicht in deinem Google Sheet hinterlegt.")
    else:
        st.error("Kein Code gefunden. Probiere es näher oder mit mehr Licht.")

# 2. Manuelle ID-Eingabe (Fix: Button erscheint jetzt!)
st.divider()
with st.expander("⌨️ Manuelle ID Eingabe (z.B. DE01301)"):
    m_id = st.text_input("ID eingeben:")
    if m_id:
        match_manual = df[df['qr_id'] == m_id]
        if not match_manual.empty:
            show_play_ui(match_manual.iloc[0])
        else:
            st.warning(f"ID {m_id} nicht gefunden.")
