import streamlit as st
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import pandas as pd
import urllib.parse

# 1. DEIN LINK ZU GOOGLE SHEETS
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRc6H9CTr8f_H1LxYyh073DgcjjlwZzHxtcY1aTjS7YSErz0sGzni6PYKbk9lJhN66hUdplPKn1f1a-/pub?output=csv"

st.set_page_config(page_title="Hitster Silent Player", page_icon="🎵")

@st.cache_data(ttl=300)
def load_data():
    try:
        # Laden der kombinierten Liste
        return pd.read_csv(SHEET_CSV_URL, dtype={'qr_id': str})
    except Exception as e:
        st.error(f"Fehler beim Laden der Tabelle: {e}")
        return pd.DataFrame(columns=['qr_id', 'artist', 'title'])

def search_and_play(card_id, df):
    # Abgleich der extrahierten ID mit deiner Master-Liste
    song_info = df[df['qr_id'] == str(card_id)]
    
    if not song_info.empty:
        artist = song_info.iloc[0]['artist']
        title = song_info.iloc[0]['title']
        search_term = f"{artist} {title}"
        
        # Spoiler-Schutz: Keine Namen anzeigen!
        st.success("✅ Karte erkannt! Musik bereit.")
        
        # YouTube Music Link mit Autoplay-Parameter
        encoded_search = urllib.parse.quote(search_term)
        ytm_url = f"https://music.youtube.com/search?q={encoded_search}"
        
        st.link_button("▶️ SONG STARTEN", ytm_url, type="primary", use_container_width=True)
        
        # Optional: Ein versteckter Bereich für die Auflösung
        with st.expander("Lösung anzeigen (nur wenn keiner draufkommt)"):
            st.write(f"**{artist} - {title}**")
    else:
        st.warning(f"⚠️ ID {card_id} nicht gefunden.")
        st.info("Suche in deiner Liste nach dem Song und trage die ID ein.")

st.title("🎵 Hitster Silent Player")
df = load_data()

tab1, tab2 = st.tabs(["📸 Scan", "⌨️ Manuelle ID"])

with tab1:
    img_file_buffer = st.camera_input("Kamera")
    if img_file_buffer:
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        # --- SONGSEEKER INSPIRATION: MULTI-STEP SCAN ---
        # Wir wandeln das Bild in verschiedene Kontraststufen um
        gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
        
        # 1. Normaler Scan
        # 2. Adaptive Threshold (hilft extrem bei Schatten und bunten Ringen)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        detected_codes = decode(gray) or decode(thresh) or decode(cv2_img)
            
        if detected_codes:
            # Extrahiert ID aus dem Hitster-Link (z.B. .../play/DE01143)
            card_id = detected_codes[0].data.decode("utf-8").split('/')[-1]
            search_and_play(card_id, df)
        else:
            st.error("🔍 Kein Code gefunden. Versuche es mit etwas mehr Abstand.")

with tab2:
    manual_id = st.text_input("ID von Karte eingeben (z.B. DE01143):")
    if manual_id:
        search_and_play(manual_id, df)
        

