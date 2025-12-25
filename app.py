import streamlit as st
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import pandas as pd
import urllib.parse

# 1. DEIN LINK ZU GOOGLE SHEETS
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRc6H9CTr8f_H1LxYyh073DgcjjlwZzHxtcY1aTjS7YSErz0sGzni6PYKbk9lJhN66hUdplPKn1f1a-/pub?output=csv"

st.set_page_config(page_title="Hitster YT Music", page_icon="🎵")

# Funktion zum Laden der Daten
@st.cache_data(ttl=300)
def load_data():
    try:
        return pd.read_csv(SHEET_CSV_URL, dtype={'qr_id': str})
    except Exception as e:
        st.error(f"Fehler beim Laden der Tabelle: {e}")
        return pd.DataFrame(columns=['qr_id', 'artist', 'title'])

st.title("🎵 Hitster 2 YouTube Music")
st.write("Halte die Karte ruhig und hell ins Bild.")

# Kamera-Eingabe
img_file_buffer = st.camera_input("Scanner")

if img_file_buffer:
    # Bild in OpenCV-Format umwandeln
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    # --- BILDOPTIMIERUNG ---
    # 1. In Graustufen umwandeln
    gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
    
    # 2. Kontrast erhöhen (Histogramm-Egalisierung)
    enhanced = cv2.equalizeHist(gray)
    
    # 3. Leichtes Schärfen
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    # Versuche den Scan mit dem optimierten Bild
    detected_codes = decode(sharpened)
    
    # Falls nichts gefunden wurde, versuche es mit dem Originalbild
    if not detected_codes:
        detected_codes = decode(cv2_img)

    if detected_codes:
        for code in detected_codes:
            raw_url = code.data.decode("utf-8")
            # Extrahiert die ID nach dem letzten Slash (z.B. aus hitstergame.com/play/1234)
            card_id = raw_url.split('/')[-1] 
            
            df = load_data()
            song_info = df[df['qr_id'] == card_id]

            if not song_info.empty:
                artist = song_info.iloc[0]['artist']
                title = song_info.iloc[0]['title']
                search_term = f"{artist} {title}"
                
                st.success(f"✅ Gefunden: {artist} - {title}")
                
                # YouTube Music Link generieren
                encoded_search = urllib.parse.quote(search_term)
                ytm_url = f"https://music.youtube.com/search?q={encoded_search}"
                
                st.link_button("🚀 In YouTube Music abspielen", ytm_url)
            else:
                st.warning(f"⚠️ ID erkannt: {card_id}")
                st.info("Diese ID ist noch nicht in deiner Google Tabelle eingetragen.")
    else:
        st.info("🔍 Kein QR-Code erkannt. Versuche es mit mehr Licht oder variiere den Abstand.")
