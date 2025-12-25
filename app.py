import streamlit as st
import pandas as pd
import urllib.parse
import cv2
import numpy as np
from pyzbar.pyzbar import decode

# HIER DEINEN NEUEN CSV-LINK EINFÜGEN
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRc6H9CTr8f_H1LxYyh073DgcjjlwZzHxtcY1aTjS7YSErz0sGzni6PYKbk9lJhN66hUdplPKn1f1a-/pub?output=csv"

st.set_page_config(page_title="Hitster Scanner", layout="centered")

@st.cache_data(ttl=60)
def load_data():
    try:
        data = pd.read_csv(SHEET_CSV_URL, dtype={'qr_id': str})
        return data, None
    except Exception as e:
        return None, str(e)

st.title("🎧 Hitster Scanner")

df, error = load_data()

if error:
    st.error(f"⚠️ Verbindung zur Google-Tabelle fehlgeschlagen.")
    st.info("Bitte prüfe, ob die Tabelle im Web als CSV veröffentlicht wurde.")
    st.stop() # Stoppt die App hier, bis der Link korrigiert ist

# Kamera-Input
img_file = st.camera_input("QR-Code scannen")

if img_file:
    bytes_data = img_file.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    detected_codes = decode(cv2_img)
    
    if detected_codes:
        raw_content = detected_codes[0].data.decode("utf-8")
        card_id = raw_content.split('/')[-1].strip()
        
        st.write(f"Erkannte ID: **{card_id}**")
        
        # Suche in der Tabelle
        song = df[df['qr_id'] == card_id]
        
        if not song.empty:
            artist = song.iloc[0]['artist']
            title = song.iloc[0]['title']
            yt_link = f"https://music.youtube.com/search?q={urllib.parse.quote(f'{artist} {title}')}"
            
            st.success(f"🎯 Gefunden: {artist} - {title}")
            st.link_button("▶️ SONG STARTEN", yt_link, type="primary", use_container_width=True)
        else:
            st.warning(f"ID {card_id} ist noch nicht verknüpft.")
    else:
        st.warning("Kein Code erkannt. Achte auf gute Beleuchtung und keine Spiegelungen.")

# Manuelle Suche als Backup
with st.expander("⌨️ Manuelle ID-Suche"):
    m_id = st.text_input("ID eingeben:")
    if m_id and not df[df['qr_id'] == m_id].empty:
        # Gleiche Logik wie oben
        res = df[df['qr_id'] == m_id].iloc[0]
        st.write(f"Gefunden: {res['artist']} - {res['title']}")
