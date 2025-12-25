import streamlit as st
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import pandas as pd
import urllib.parse

# 1. HIER den Link als Variable definieren (in Anführungszeichen!)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRc6H9CTr8f_H1LxYyh073DgcjjlwZzHxtcY1aTjS7YSErz0sGzni6PYKbk9lJhN66hUdplPKn1f1a-/pub?output=csv"

# 2. Die Funktion nutzt dann diese Variable
@st.cache_data(ttl=600)
def load_data():
    try:
        return pd.read_csv(SHEET_CSV_URL, dtype={'qr_id': str})
    except Exception as e:
        st.error(f"Fehler beim Laden der Tabelle: {e}")
        return pd.DataFrame(columns=['qr_id', 'artist', 'title'])

df = load_data()

st.title("Hitster 2 YouTube Music 🎵")

img_file_buffer = st.camera_input("Scanne deine Hitster-Karte")

if img_file_buffer:
    # Bild verarbeiten
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    detected_codes = decode(cv2_img)

    if detected_codes:
        for code in detected_codes:
            # Die ID aus der URL extrahieren (z.B. von "hitstergame.com/play/1001")
            raw_url = code.data.decode("utf-8")
            # Wir nehmen nur den letzten Teil der URL als ID
            card_id = raw_url.split('/')[-1] 
            
            st.info(f"ID erkannt: {card_id}")

            # 2. In der CSV nach der ID suchen
            song_info = df[df['qr_id'] == card_id]

            if not song_info.empty:
                artist = song_info.iloc[0]['artist']
                title = song_info.iloc[0]['title']

                search_term = f"{artist} {title}"
                
                st.success(f"Gefunden: {artist} - {title}")
                
                # YouTube Music Link generieren
                encoded_search = urllib.parse.quote(search_term)
                ytm_url = f"https://music.youtube.com/search?q={encoded_search}"
                
                # Button zur Weiterleitung
                st.link_button("In YouTube Music abspielen", ytm_url)
            else:
                st.error("Diese Karte ist leider noch nicht in der Datenbank.")


