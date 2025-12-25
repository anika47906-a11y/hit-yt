import streamlit as st
import pandas as pd
import urllib.parse
import cv2
import numpy as np
from pyzbar.pyzbar import decode

# DEIN CSV-LINK
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRc6H9CTr8f_H1LxYyh073DgcjjlwZzHxtcY1aTjS7YSErz0sGzni6PYKbk9lJhN66hUdplPKn1f1a-/pub?output=csv"

st.set_page_config(page_title="Hitster Pro", layout="centered")

# CSS für echtes Vollbild-Vorschaubild und bessere Sichtbarkeit
st.markdown("""
    <style>
    /* Erzwingt das korrekte Seitenverhältnis der Kamera-Vorschau */
    [data-testid="stCameraInput"] video {
        height: auto !important;
        width: 100% !important;
        max-height: 80vh !important; /* Nutzt 80% der Bildschirmhöhe */
        object-fit: contain !important; /* Zeigt das ganze Bild ohne Abschneiden */
        background: black;
        border: 2px solid #333;
        border-radius: 10px;
    }
    /* Button-Styling */
    .stButton>button {
        width: 100%;
        height: 4em;
        font-weight: bold;
        font-size: 1.2rem !important;
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
    
    # EXPLIZITER RADIO-START (Beste Option für Premium)
    # Wir nutzen 'watch' statt 'search', was YouTube Music signalisiert, 
    # dass es direkt mit der Wiedergabe (oder einem Radio) beginnen soll.
    search_query = f"{artist} {title}"
    encoded_query = urllib.parse.quote(search_query)
    
    # Dieser Link-Typ versucht direkt in den Player-Modus zu springen
    yt_link = f"https://music.youtube.com/search?q={encoded_query}" 
    # Alternativer Radio-Link (falls unterstützt):
    # yt_link = f"https://music.youtube.com/watch?q={encoded_query}"

    st.divider()
    st.balloons()
    
    # Großer Button für blinde Bedienung
    st.link_button(f"🚀 RADIO STARTEN: {artist}", yt_link, type="primary", use_container_width=True)
    
    with st.expander("🔎 Lösung anzeigen"):
        st.subheader(f"{artist} - {title}")

st.title("🎧 Hitster Radio-Scanner")

df, error = load_data()
if error:
    st.error("Google Sheets Verbindung fehlgeschlagen!")
    st.stop()

# Kamera mit besserem Viewport
img_file = st.camera_input("Kamera")

if img_file:
    bytes_data = img_file.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    detected = decode(cv2_img)
    
    if detected:
        # Extrahiert ID aus Link
        raw_url = detected[0].data.decode("utf-8")
        card_id = raw_url.split('/')[-1].strip()
        
        match = df[df['qr_id'] == card_id]
        if not match.empty:
            show_play_ui(match.iloc[0])
        else:
            st.warning(f"ID {card_id} erkannt, aber nicht im Google Sheet gefunden.")
            st.info(f"Inhalt des Scans: {raw_url}")
    else:
        st.error("QR-Code nicht erkannt. Bitte halte die Karte ruhiger oder weiter weg.")

# Manuelle Eingabe
with st.expander("⌨️ Manuelle ID"):
    m_id = st.text_input("ID:")
    if m_id:
        match_manual = df[df['qr_id'] == m_id]
        if not match_manual.empty:
            show_play_ui(match_manual.iloc[0])
