import streamlit as st
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import pandas as pd
import urllib.parse

# 1. DEIN LINK ZU GOOGLE SHEETS
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRc6H9CTr8f_H1LxYyh073DgcjjlwZzHxtcY1aTjS7YSErz0sGzni6PYKbk9lJhN66hUdplPKn1f1a-/pub?output=csv"

st.set_page_config(page_title="Hitster YT Silent", page_icon="🎵")

@st.cache_data(ttl=300)
def load_data():
    try:
        # Wir laden die Daten aus deiner Master-Liste
        return pd.read_csv(SHEET_CSV_URL, dtype={'qr_id': str})
    except Exception as e:
        st.error(f"Fehler beim Laden der Tabelle: {e}")
        return pd.DataFrame(columns=['qr_id', 'artist', 'title'])

def search_and_play(card_id, df):
    # Abgleich der ID mit deiner Liste
    song_info = df[df['qr_id'] == str(card_id)]
    
    if not song_info.empty:
        # Daten werden im Hintergrund geladen, aber nicht per st.write angezeigt!
        artist = song_info.iloc[0]['artist']
        title = song_info.iloc[0]['title']
        search_term = f"{artist} {title}"
        
        st.success("✅ Song erkannt! Bereit zum Abspielen.")
        
        # Link-Generierung mit Autoplay-Befehl
        encoded_search = urllib.parse.quote(search_term)
        # Wir nutzen die Suche und hängen Autoplay an
        ytm_url = f"https://music.youtube.com/search?q={encoded_search}&autoplay=1"
        
        # Ein großer, prominenter Button
        st.link_button("▶️ JETZT ABSPIELEN", ytm_url, type="primary", use_container_width=True)
    else:
        st.warning(f"⚠️ ID {card_id} unbekannt. Bitte in Google Sheets nachtragen.")

# --- UI ---
st.title("🎵 Hitster Silent Player")

df = load_data()
tab1, tab2 = st.tabs(["📸 Scan", "⌨️ ID Tippen"])

with tab1:
    img_file_buffer = st.camera_input("Scanner")
    if img_file_buffer:
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        # Optimierter Scan-Vorgang
        gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
        detected_codes = decode(gray)
        if not detected_codes:
            detected_codes = decode(cv2_img)
            
        if detected_codes:
            card_id = detected_codes[0].data.decode("utf-8").split('/')[-1]
            search_and_play(card_id, df)
        else:
            st.info("Suche QR-Code...")

with tab2:
    manual_id = st.text_input("ID eingeben:")
    if manual_id:
        search_and_play(manual_id, df)
        
