"""
pages/2_🗺️_Cartographie.py — Carte choroplèthe des provinces (GeoJSON admin1)
avec marqueurs de bénéficiaires et couche de population 2023.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import folium
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

import config
from utils import data_loader as dl
from utils import theme

st.set_page_config(page_title="Cartographie — INTERSOS Tchad", page_icon="🗺️", layout="wide")

if "auth_user" not in st.session_state:
    st.warning("Veuillez vous connecter depuis la page d'accueil.")
    st.stop()

theme.inject_theme_css()
t = theme.get_active_theme()

st.markdown("## 🗺️ Cartographie opérationnelle")

try:
    sheets = dl.load_excel_sheets()
    gj = dl.load_geojson()
except (FileNotFoundError, RuntimeError) as exc:
    st.error(str(exc))
    st.stop()

ben = sheets[config.SHEET_BENEFICIARIES]

# --- Filtres locaux, cohérents avec les filtres globaux de la sidebar ------
col1, col2 = st.columns(2)
sector_filter = col1.selectbox("Secteur", ["Tous"] + dl.get_sector_sheet_names(sheets), key="map_sector")
status_filter = col2.selectbox("Statut de déplacement", ["Tous"] + dl.get_displacement_statuses(sheets), key="map_status")

df = ben.copy()
if sector_filter != "Tous" and "Sector" in df.columns:
    df = df[df["Sector"] == sector_filter]
if status_filter != "Tous":
    df = df[df["Displacement_Status"] == status_filter]

# --- Agrégation par province pour la choroplèthe ---------------------------
counts_by_province = df.groupby("Province").size().reset_index(name="Beneficiaires")

# Population 2023 par province, extraite du GeoJSON (source de vérité géo)
pop_by_province = {
    feat["properties"]["name"]: feat["properties"].get("population") or feat["properties"].get("population_2023")
    for feat in gj["features"]
}

m = folium.Map(location=[13.5, 18.7], zoom_start=6, tiles="CartoDB dark_matter" if t["name"] == "Mission Control" else "CartoDB positron")

folium.Choropleth(
    geo_data=gj,
    data=counts_by_province,
    columns=["Province", "Beneficiaires"],
    key_on="feature.properties.name",
    fill_color="YlOrRd",
    fill_opacity=0.75,
    line_opacity=0.4,
    legend_name="Bénéficiaires par province (filtre appliqué)",
    nan_fill_color="#444444",
).add_to(m)

cluster = MarkerCluster(name="Bénéficiaires").add_to(m)
for _, row in df.dropna(subset=["GPS_Lat", "GPS_Lon"]).iterrows():
    folium.CircleMarker(
        location=[row["GPS_Lat"], row["GPS_Lon"]],
        radius=3,
        color=t["primary"],
        fill=True,
        fill_opacity=0.7,
        popup=f"{row.get('Sector', '')} — {row.get('Displacement_Status', '')}",
    ).add_to(cluster)

folium.LayerControl().add_to(m)

st_data = st_folium(m, use_container_width=True, height=560)

st.divider()
c1, c2 = st.columns(2)
with c1:
    st.markdown("#### Bénéficiaires par province (filtre appliqué)")
    st.dataframe(
        counts_by_province.sort_values("Beneficiaires", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
with c2:
    st.markdown("#### Population 2023 (référence GeoJSON)")
    pop_df = pd.DataFrame(
        [{"Province": k, "Population 2023": v} for k, v in pop_by_province.items() if k in counts_by_province["Province"].values]
    ).sort_values("Population 2023", ascending=False)
    st.dataframe(pop_df, use_container_width=True, hide_index=True)
