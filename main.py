import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import html

# 🔗 Replace this with your actual GitHub CSV raw URL
CSV_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/liberalita_edh.csv"

# 🟥 List of CIL/IL reference numbers from the PDF
pdf_refs = [
    "CILA 03-01", "CIL VIII 937", "CIL VIII 1223", "CIL VIII 1495", "CIL VIII 5142",
    "CIL VIII 5365", "CIL VIII 5366", "CIL VIII 10523", "CIL VIII 12058",
    "CIL VIII 26273", "IL Alg 02-03 10120", "IL Afr 511", "CIL X 6529", "AE 1955 151"
]

# Load the CSV
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    coords_col = 'coordinates (lat,lng)'
    if pd.isna(df.loc[29, coords_col]):
        df.loc[29, coords_col] = df.loc[29, coords_col]
    if pd.isna(df.loc[67, coords_col]):
        df.loc[67, coords_col] = df.loc[67, coords_col]
    return df

# Helper: parse coordinates
def extract_coordinates(loc_str):
    try:
        lat, lon = map(float, loc_str.strip().split(","))
        return lat, lon
    except:
        return None, None

# Helper: check if transcription contains any of the PDF refs
def matches_pdf_refs(transcription):
    return any(ref in transcription for ref in pdf_refs)

# Streamlit UI setup
st.set_page_config(page_title="Liberalitas Map", layout="wide")
st.title("📍 Inscriptions of *Liberalitas*")
st.markdown("Explore all known inscriptions, with those from the attached PDF highlighted in red.")

df = load_data()
all_regions = df['province / Italic region'].dropna().unique()
selected_region = st.sidebar.selectbox("🗺️ Filter by Region", ["All"] + sorted(all_regions.tolist()))

if selected_region != "All":
    df = df[df['province / Italic region'] == selected_region]

# 🗺️ Create Folium map
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

    # 🧼 Clean transcription: keep only content after last colon
    if ":" in transcription_raw:
        transcription_clean = transcription_raw.split(":")[-1].strip()
    else:
        transcription_clean = transcription_raw

    # Check if this matches one of the PDF-listed inscriptions
    is_highlighted = matches_pdf_refs(transcription_raw)

    popup_html = f"""
    <div style="width: 300px; max-height: 250px; overflow-y: auto; font-size: 13px;">
        <strong><u>Province:</u></strong> {html.escape(str(province))}<br>
        <strong><u>Modern Findspot:</u></strong> {html.escape(str(findspot))}<br><br>
        <strong>Transcription:</strong><br>
        <pre style="white-space: pre-wrap;">{html.escape(transcription_clean)}</pre>
    </div>
    """

    marker_color = "red" if is_highlighted else "blue"
    folium.Marker(
        location=(lat, lon),
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color=marker_color)
    ).add_to(marker_cluster)

# Show the map
st_folium(m, width=900, height=600)
