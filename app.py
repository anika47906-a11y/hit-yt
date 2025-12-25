import streamlit as st
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import pandas as pd
import urllib.parse

# 1. DEIN LINK ZU GOOGLE SHEETS
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRc6H9CTr8f_H1LxYyh073DgcjjlwZzHxtcY1aTjS7YSErz0sGzni6PYKbk9lJhN66hUdplPKn1f1a-/pub?output=csv"

st.set_page_config(page_title="Hitster YT Pro", page_icon="🎵")

# Funktion zum Laden der Daten
@st.cache_data(ttl=300)
def load_data():
    try:
        return pd.read_csv(SHEET_CSV_URL, dtype={'qr_id': str})
    except Exception as e:
        st.error(f"Fehler beim Laden der Tabelle: {e}")
        return pd.DataFrame(columns=['qr_id', 'artist', 'title'])

def search_and_play(card_id, df):
    """Sucht Song in DF und zeigt Button an"""
    song_info = df[df['qr_id'] == str(card_id)]
    if not song_info.empty:
        artist = song_info.iloc[0]['artist']
        title = song_info.iloc[0]['title']
        search_term = f"{artist} {title}"
        st.success(f"✅ Gefunden: {artist} - {title}")
        encoded_search = urllib.parse.quote(search_term)
        ytm_url = f"https://music.youtube.com/search?q={encoded_search}"
        st.link_button("🚀 In YouTube Music abspielen", ytm_url)
    else:
        st.warning(f"⚠️ ID erkannt: {card_id}")
        st.info("Diese ID ist noch nicht in deiner Google Tabelle.")

# --- UI START ---
st.title("🎵 Hitster 2 YouTube Pro")

df = load_data()

# TAB-System für bessere Übersicht
tab1, tab2 = st.tabs(["📸 Scanner", "⌨️ Manuelle Eingabe"])

with tab1:
    st.write("Halte die Karte leicht gekippt (gegen Glanz).")
    img_file_buffer = st.camera_input("Scanner")

    if img_file_buffer:
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        # TURBO-SCAN: Verschiedene Bildvarianten testen
        gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
        enhanced = cv2.equalizeHist(gray)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        variants = [cv2_img, gray, enhanced, thresh]
        
        detected_codes = None
        for v in variants:
            detected_codes = decode(v)
            if detected_codes:
                break
        
        if detected_codes:
            card_id = detected_codes[0].data.decode("utf-8").split('/')[-1]
            search_and_play(card_id, df)
        else:
            st.error("🔍 Kein Code gefunden. Tipp: Karte leicht neigen oder weiter weg halten.")

with tab2:
    manual_id = st.text_input("QR-ID hier eintippen (z.B. vom Bildschirm ablesen):")
    if manual_id:
        search_and_play(manual_id, df)

st.write("---")
if st.button("🔄 Songliste neu laden"):
    st.cache_data.clear()
    st.rerun()
