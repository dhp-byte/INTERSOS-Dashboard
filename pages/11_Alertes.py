"""
pages/11_Alertes.py — Moteur d'alertes : agrège, sur l'ensemble des
secteurs et des indicateurs, tout ce qui est "À surveiller" ou en
"Retard critique" par rapport aux seuils actifs (configurables dans la
barre latérale via theme.get_thresholds(), sinon config.ACHIEVEMENT_THRESHOLDS).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st

import config
from utils import data_loader as dl
from utils import theme
from utils import topbar

st.set_page_config(page_title="Alertes — INTERSOS Tchad", page_icon="🚨", layout="wide")

if "auth_user" not in st.session_state:
    st.warning("Veuillez vous connecter depuis la page d'accueil.")
    st.stop()

theme.inject_theme_css()
topbar.render_topbar("Alertes")

try:
    sheets = dl.load_excel_sheets()
except (FileNotFoundError, RuntimeError) as exc:
    st.error(str(exc))
    st.stop()

st.markdown("## 🚨 Alertes — indicateurs et activités à risque")
th = theme.get_thresholds()
st.caption(
    f"Seuils actifs (ajustables dans la barre latérale) : ≥ {th['on_track_min']:.0f}% en bonne voie · "
    f"{th['watch_min']:.0f}–{th['on_track_min']:.0f}% à surveiller · "
    f"< {th['watch_min']:.0f}% retard critique."
)

indicators = sheets[config.SHEET_INDICATORS]

critical = indicators[indicators["Achievement_%"] < th["watch_min"]].sort_values("Achievement_%")
watch = indicators[
    (indicators["Achievement_%"] >= th["watch_min"]) & (indicators["Achievement_%"] < th["on_track_min"])
].sort_values("Achievement_%")

st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("🔴 Retard critique", len(critical))
c2.metric("🟠 À surveiller", len(watch))
c3.metric("🟢 En bonne voie", len(indicators) - len(critical) - len(watch))

st.divider()
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("#### Taux moyen de réalisation par secteur")
    avg_by_sector = indicators.groupby("Sector")["Achievement_%"].mean().round(1).reset_index()
    avg_by_sector.columns = ["Secteur", "Atteint moyen (%)"]
    avg_by_sector = avg_by_sector.sort_values("Atteint moyen (%)")
    fig_sect = px.bar(
        avg_by_sector, x="Atteint moyen (%)", y="Secteur", orientation="h", color="Secteur",
        color_discrete_map=config.SECTOR_COLORS,
    )
    fig_sect.add_vline(x=th["on_track_min"], line_dash="dash", line_color="#33C481")
    fig_sect.add_vline(x=th["watch_min"], line_dash="dash", line_color="#F4A93B")
    fig_sect.update_layout(showlegend=False, height=320)
    st.plotly_chart(fig_sect, use_container_width=True)

with col_b:
    st.markdown("#### Répartition globale des indicateurs")
    dist = pd.DataFrame({
        "Statut": ["En bonne voie", "À surveiller", "Retard critique"],
        "Nombre": [len(indicators) - len(critical) - len(watch), len(watch), len(critical)],
    })
    fig_dist = px.pie(
        dist, names="Statut", values="Nombre", hole=0.5,
        color="Statut", color_discrete_map={
            "En bonne voie": "#33C481", "À surveiller": "#F4A93B", "Retard critique": "#E5484D",
        },
    )
    fig_dist.update_layout(height=320)
    st.plotly_chart(fig_dist, use_container_width=True)

st.divider()

if not critical.empty:
    st.markdown("### 🔴 Indicateurs en retard critique")
    for _, r in critical.iterrows():
        st.error(f"**{r['Indicator']}** ({r['Sector']}) — {r['Achievement_%']:.1f}% de l'objectif atteint")
else:
    st.success("Aucun indicateur en retard critique.")

st.divider()

if not watch.empty:
    st.markdown("### 🟠 Indicateurs à surveiller")
    for _, r in watch.iterrows():
        st.warning(f"**{r['Indicator']}** ({r['Sector']}) — {r['Achievement_%']:.1f}% de l'objectif atteint")
else:
    st.info("Aucun indicateur à surveiller.")

st.divider()
st.markdown("### 📋 Activités sectorielles sous le seuil d'alerte")
st.caption(
    "Pour chaque secteur disposant de colonnes Cible/Atteint, activités dont le taux de réalisation "
    "individuel est inférieur au seuil de surveillance."
)

rows = []
for sheet_name, cfg in config.SECTOR_CONFIG.items():
    if sheet_name not in sheets:
        continue
    df = sheets[sheet_name]
    target_col, reached_col = cfg["target_col"], cfg["reached_col"]
    if not {target_col, reached_col}.issubset(df.columns):
        continue
    tmp = df.copy()
    tmp = tmp[tmp[target_col] > 0]
    tmp["Taux"] = 100 * tmp[reached_col] / tmp[target_col]
    at_risk = tmp[tmp["Taux"] < th["watch_min"]]
    for _, r in at_risk.iterrows():
        rows.append(
            {
                "Secteur": sheet_name.replace("_", " "),
                "Province": r.get("Province", "—"),
                "Activité": r.get("Activity_Type", "—"),
                "Cible": r[target_col],
                "Atteint": r[reached_col],
                "Taux": f"{r['Taux']:.1f}%",
            }
        )

if rows:
    st.dataframe(pd.DataFrame(rows).sort_values("Taux"), use_container_width=True, hide_index=True)
else:
    st.success("Aucune activité sectorielle sous le seuil de surveillance.")
