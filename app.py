import streamlit as st
import pandas as pd
import urllib.parse
import cv2
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from pyzbar.pyzbar import decode
import numpy as np

# 1. DEIN LINK ZU GOOGLE SHEETS
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRc6H9CTr8f_H1LxYyh073DgcjjlwZzHxtcY1aTjS7YSErz0sGzni6PYKbk9lJhN66hUdplPKn1f1a-/pub?output=csv"

st.set_page_config(page_title="Hitster Live Pro", page_icon="🎥")

@st.cache_data(ttl=300)
def load_data():
    try:
        return pd.read_csv(SHEET_CSV_URL, dtype={'qr_id': str})
    except:
        return pd.DataFrame(columns=['qr_id', 'artist', 'title'])

# Diese Klasse verarbeitet das Live-Video
class QRScanner(VideoTransformerBase):
    def __init__(self):
        self.result = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        # QR-Code im aktuellen Bild suchen
        codes = decode(img)
        if codes:
            self.result = codes[0].data.decode("utf-8").split('/')[-1]
            # Einen grünen Rahmen um den Code zeichnen (visuelles Feedback)
            for code in codes:
                pts = np.array([code.polygon], np.int32)
                cv2.polylines(img, [pts], True, (0, 255, 0), 5)
        return img

st.title("🎧 Hitster Live-Scanner")
df = load_data()

# Live-Video Stream starten
ctx = webrtc_streamer(key="scanner", video_transformer_factory=QRScanner)

# Wenn ein Code im Live-Stream gefunden wurde
if ctx.video_transformer and ctx.video_transformer.result:
    card_id = ctx.video_transformer.result
    
    song_info = df[df['qr_id'] == str(card_id)]
    
    if not song_info.empty:
        artist = song_info.iloc[0]['artist']
        title = song_info.iloc[0]['title']
        st.success(f"🎯 Erkannt! ID: {card_id}")
        
        search_term = f"{artist} {title}"
        ytm_url = f"https://music.youtube.com/search?q={urllib.parse.quote(search_term)}"
        
        st.link_button("▶️ JETZT ABSPIELEN", ytm_url, type="primary", use_container_width=True)
        
        with st.expander("🔎 Lösung anzeigen"):
            st.write(f"**{artist}** — {title}")
    else:
        st.warning(f"ID {card_id} noch nicht in der Liste.")

# Fallback manuelle Eingabe
with st.expander("⌨️ Manuelle Eingabe"):
    manual_id = st.text_input("ID eingeben:")
    if manual_id:
        # (Hier die gleiche Logik wie oben für manual_id)
        pass
