import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import html

# 🔗 Replace this with your real raw CSV URL from GitHub
CSV_URL = "https://raw.githubusercontent.com/lapis82/liberalita-edh-20250714/refs/heads/main/liberalita_edh.csv"

# Load data from GitHub
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    coords_col = 'coordinates (lat,lng)'
    
    # Fallback handling for rows 30 and 68 (index 29, 67)
    if pd.isna(df.loc[29, coords_col]):
        df.loc[29, coords_col] = df.loc[29, coords_col]
    if pd.isna(df.loc[67, coords_col]):
        df.loc[67, coords_col] = df.loc[67, coords_col]
    
    return df

# Parse coordinates from string
def extract_coordinates(loc_str):
    try:
        lat, lon = map(float, loc_str.strip().split(","))
        return lat, lon
    except:
        return None, None

# 🌍 App layout
st.set_page_config(page_title="Liberalitas Map", layout="wide")
st.title("📍 Inscriptions of *Liberalitas*")
st.markdown("Explore locations and transcriptions of Roman inscriptions mentioning *liberalitas*.")

# 📊 Load data
df = load_data()

# Sidebar filter
all_regions = df['province / Italic region'].dropna().unique()
selected_region = st.sidebar.selectbox("🗺️ Filter by Region", ["All"] + sorted(all_regions.tolist()))

if selected_region != "All":
    df = df[df['province / Italic region'] == selected_region]

# 🌍 Initialize map
m = folium.Map(location=(41.9, 12.5), zoom_start=5)
marker_cluster = MarkerCluster().add_to(m)

for _, row in df.iterrows():
    coords = row['coordinates (lat,lng)']
    transcription_raw = str(row['transcription']).strip()
    province = row.get('province / Italic region', 'Unknown')
    findspot = row.get('modern find spot', 'Unknown')

    if pd.isna(coords):
        continue

    lat, lon = extract_coordinates(coords)
    if lat is None or lon is None:
        continue

    # ✂️ Clean transcription: remove all metadata before last colon
    if ":" in transcription_raw:
        transcription_clean = transcription_raw.split(":")[-1].strip()
    else:
        transcription_clean = transcription_raw

    # 📜 HTML popup
    popup_html = f"""
    <div style="width: 300px; max-height: 250px; overflow-y: auto; font-size: 13px;">
        <strong><u>Province:</u></strong> {html.escape(str(province))}<br>
        <strong><u>Modern Findspot:</u></strong> {html.escape(str(findspot))}<br><br>
        <strong>Transcription:</strong><br>
        <pre style="white-space: pre-wrap;">{html.escape(transcription_clean)}</pre>
    </div>
    """
    folium.Marker(
        location=(lat, lon),
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(marker_cluster)

# Show the map
st_folium(m, width=900, height=600)
