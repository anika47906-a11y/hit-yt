import streamlit as st
import pandas as pd
import urllib.parse
from streamlit_qr_scanner import streamlit_qr_scanner

# 1. DEIN LINK ZU GOOGLE SHEETS
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRc6H9CTr8f_H1LxYyh073DgcjjlwZzHxtcY1aTjS7YSErz0sGzni6PYKbk9lJhN66hUdplPKn1f1a-/pub?output=csv"

st.set_page_config(page_title="Hitster Live Scanner", page_icon="🎥", layout="centered")

@st.cache_data(ttl=300)
def load_data():
    try:
        # Lädt die kombinierten Songdaten aus deinen CSVs
        return pd.read_csv(SHEET_CSV_URL, dtype={'qr_id': str})
    except Exception as e:
        st.error(f"Fehler beim Laden der Tabelle: {e}")
        return pd.DataFrame(columns=['qr_id', 'artist', 'title'])

def play_song(card_id, df):
    # Abgleich mit deiner Master-Liste
    song_info = df[df['qr_id'] == str(card_id)]
    
    if not song_info.empty:
        artist = song_info.iloc[0]['artist']
        title = song_info.iloc[0]['title']
        search_term = f"{artist} {title}"
        encoded_query = urllib.parse.quote(search_term)
        
        # Premium-optimierter Link
        ytm_url = f"https://music.youtube.com/search?q={encoded_query}"

        st.balloons() # Kleiner Effekt bei Erfolg
        st.success("🎯 Karte erkannt!")
        
        st.link_button("▶️ SONG STARTEN", ytm_url, type="primary", use_container_width=True)
        
        with st.expander("🔎 Lösung anzeigen"):
            st.write(f"**{artist}** — *{title}*")
    else:
        st.warning(f"ID {card_id} nicht in deiner Liste gefunden.")

# --- UI ---
st.title("🎧 Hitster Live-Scanner")
df = load_data()

tab1, tab2 = st.tabs(["🎥 Live-Scan", "⌨️ Manuelle ID"])

with tab1:
    st.write("Halte die Karte einfach vor die Kamera.")
    # Der Live-Scanner: Erzeugt einen Videostream im Browser
    qr_code = streamlit_qr_scanner(key='qrcode_scanner')

    if qr_code:
        # Extrahiert die ID (letzter Teil des Links)
        card_id = qr_code.split('/')[-1]
        play_song(card_id, df)

with tab2:
    manual_id = st.text_input("ID eingeben (z.B. DE01143):")
    if manual_id:
        play_song(manual_id, df)

st.divider()
if st.button("🔄 Liste aktualisieren"):
    st.cache_data.clear()
    st.rerun()
