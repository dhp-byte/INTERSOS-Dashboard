"""
pages/2_Cartographie.py — Carte choroplèthe des provinces (GeoJSON admin1)
avec marqueurs de bénéficiaires et couche de population 2023.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium

import config
from utils import data_loader as dl
from utils import theme
from utils import topbar

st.set_page_config(page_title="Cartographie — INTERSOS Tchad", page_icon="🗺️", layout="wide")

if "auth_user" not in st.session_state:
    st.warning("Veuillez vous connecter depuis la page d'accueil.")
    st.stop()

theme.inject_theme_css()
topbar.render_topbar("Cartographie")
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
col1, col2, col3 = st.columns(3)
sector_filter = col1.selectbox("Secteur", ["Tous"] + dl.get_sector_sheet_names(sheets), key="map_sector")
status_filter = col2.selectbox("Statut de déplacement", ["Tous"] + dl.get_displacement_statuses(sheets), key="map_status")
layer_choice = col3.radio(
    "Couche cartographique", ["Choroplèthe + clusters", "Carte de chaleur (densité)"],
    key="map_layer", horizontal=False,
)

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

if layer_choice == "Choroplèthe + clusters":
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
else:
    heat_points = df.dropna(subset=["GPS_Lat", "GPS_Lon"])[["GPS_Lat", "GPS_Lon"]].values.tolist()
    if heat_points:
        HeatMap(heat_points, radius=16, blur=22, name="Densité").add_to(m)
    else:
        st.info("Aucun point GPS disponible pour ces filtres.")

folium.LayerControl().add_to(m)

st_data = st_folium(m, use_container_width=True, height=560)

st.divider()
c1, c2 = st.columns(2)
with c1:
    st.markdown("#### Bénéficiaires par province (filtre appliqué)")
    sorted_counts = counts_by_province.sort_values("Beneficiaires", ascending=False)
    st.dataframe(sorted_counts, use_container_width=True, hide_index=True)
    top5 = sorted_counts.head(5)
    fig_top = px.bar(
        top5, x="Beneficiaires", y="Province", orientation="h", color="Province",
        color_discrete_sequence=["#3D6FE0", "#40C057", "#15AABF", "#F76707", "#6C5CE7"],
    )
    fig_top.update_layout(showlegend=False, height=240, yaxis={"categoryorder": "total ascending"},
                          xaxis_title="Bénéficiaires", title="Top 5 provinces")
    st.plotly_chart(fig_top, use_container_width=True)
with c2:
    st.markdown("#### Population 2023 (référence GeoJSON)")
    pop_df = pd.DataFrame(
        [{"Province": k, "Population 2023": v} for k, v in pop_by_province.items() if k in counts_by_province["Province"].values]
    ).sort_values("Population 2023", ascending=False)
    st.dataframe(pop_df, use_container_width=True, hide_index=True)
