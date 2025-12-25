import streamlit as st
import pandas as pd
import urllib.parse
import cv2
import numpy as np
from pyzbar.pyzbar import decode

# DEIN CSV-LINK
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRc6H9CTr8f_H1LxYyh073DgcjjlwZzHxtcY1aTjS7YSErz0sGzni6PYKbk9lJhN66hUdplPKn1f1a-/pub?output=csv"

st.set_page_config(page_title="Hitster Pro", layout="centered")

# Aggressives CSS für ein großes Kamerafenster
st.markdown("""
    <style>
    /* Das umschließende Element des Kamera-Inputs */
    [data-testid="stCameraInput"] {
        max-width: 100% !important;
    }
    /* Das Video-Element selbst */
    [data-testid="stCameraInput"] video {
        height: 600px !important;
        object-fit: cover !important;
        border: 4px solid #FF4B4B !important;
        border-radius: 20px !important;
    }
    /* Den "Foto aufnehmen" Button vergrößern */
    [data-testid="stCameraInput"] button {
        background-color: #FF4B4B !important;
        color: white !important;
        font-weight: bold !important;
        height: 50px !important;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_data():
    try:
        return pd.read_csv(SHEET_CSV_URL, dtype={'qr_id': str}), None
    except Exception as e:
        return None, str(e)

def show_play_ui(song_row):
    artist = song_row['artist']
    title = song_row['title']
    
    # PREMIUM TRICK: Wir hängen "autoplay=1" an und nutzen den "search?q=" Pfad
    # YouTube Music spielt oft das erste Ergebnis direkt ab, wenn man Premium hat.
    search_term = urllib.parse.quote(f"{artist} {title}")
    yt_link = f"https://music.youtube.com/search?q={search_term}"
    
    st.divider()
    st.info("🎵 Song bereit!")
    
    # Großer Button für blindes Klicken
    st.link_button("🔥 SOFORT ABSPIELEN (PREMIUM)", yt_link, type="primary", use_container_width=True)
    
    # Die Lösung ist ganz weit unten oder eingeklappt
    with st.expander("🔎 Lösung erst nach dem Raten öffnen"):
        st.subheader(f"{artist}")
        st.write(f"Song: {title}")

st.title("🎧 Hitster Premium Player")

df, error = load_data()
if error:
    st.error("Google Sheets Verbindung fehlt!")
    st.stop()

# Kamera
img_file = st.camera_input("Scanner")

if img_file:
    bytes_data = img_file.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    detected = decode(cv2_img)
    
    if detected:
        card_id = detected[0].data.decode("utf-8").split('/')[-1].strip()
        match = df[df['qr_id'] == card_id]
        if not match.empty:
            show_play_ui(match.iloc[0])
        else:
            st.warning(f"ID {card_id} nicht im Sheet.")
    else:
        st.error("Kein Code erkannt – bitte näher ran.")

# Manuell
with st.expander("⌨️ Manuelle Eingabe"):
    m_id = st.text_input("ID:")
    if m_id:
        match_manual = df[df['qr_id'] == m_id]
        if not match_manual.empty:
            show_play_ui(match_manual.iloc[0])
