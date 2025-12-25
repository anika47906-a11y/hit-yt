import streamlit as st
import pandas as pd
import urllib.parse
import cv2
import numpy as np
from pyzbar.pyzbar import decode

# URL deines veröffentlichten Google Sheets (CSV-Link)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/DEINE_ID/pub?output=csv"

st.set_page_config(page_title="Hitster Scan Fix", layout="centered")

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(SHEET_CSV_URL, dtype={'qr_id': str})

st.title("🎧 Hitster Scanner Fix")
df = load_data()

# Einfaches Kamera-Eingabefeld
img_file = st.camera_input("Karte scannen")

if img_file:
    # Bild verarbeiten
    bytes_data = img_file.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    # QR-Code suchen
    detected_codes = decode(cv2_img)
    
    if detected_codes:
        raw_content = detected_codes[0].data.decode("utf-8")
        # ID extrahieren (nimmt das Ende des Links)
        card_id = raw_content.split('/')[-1].strip()
        
        st.write(f"Gefundene ID: **{card_id}**") # Zur Kontrolle anzeigen
        
        # Abgleich mit Tabelle
        song = df[df['qr_id'] == card_id]
        
        if not song.empty:
            artist = song.iloc[0]['artist']
            title = song.iloc[0]['title']
            search = urllib.parse.quote(f"{artist} {title}")
            yt_link = f"https://music.youtube.com/search?q={search}"
            
            st.success(f"🎯 Treffer!")
            st.link_button("▶️ SONG ABSPIELEN", yt_link, type="primary", use_container_width=True)
        else:
            st.warning(f"ID {card_id} nicht in der Liste gefunden.")
    else:
        st.error("Kein QR-Code erkannt. Bitte näher ran oder Licht verbessern.")
