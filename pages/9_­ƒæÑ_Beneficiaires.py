"""
pages/9_👥_Beneficiaires.py — Registre des bénéficiaires enregistrés
(feuille Beneficiary_Registration), avec filtres, profils démographiques,
carte de densité et export du registre filtré.
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

st.set_page_config(page_title="Bénéficiaires — INTERSOS Tchad", page_icon="👥", layout="wide")

if "auth_user" not in st.session_state:
    st.warning("Veuillez vous connecter depuis la page d'accueil.")
    st.stop()

theme.inject_theme_css()

try:
    sheets = dl.load_excel_sheets()
except (FileNotFoundError, RuntimeError) as exc:
    st.error(str(exc))
    st.stop()

ben_full = sheets[config.SHEET_BENEFICIARIES]

st.markdown("## 👥 Registre des bénéficiaires")

# --- Filtres -----------------------------------------------------------
f1, f2, f3, f4 = st.columns(4)
province = f1.selectbox("Province", ["Toutes"] + sorted(ben_full["Province"].dropna().unique().tolist()))
sector = f2.selectbox("Secteur", ["Tous"] + sorted(ben_full["Sector"].dropna().unique().tolist())) if "Sector" in ben_full.columns else "Tous"
disp_status = f3.selectbox("Statut de déplacement", ["Tous"] + sorted(ben_full["Displacement_Status"].dropna().unique().tolist()))
vuln_col = "Vulnerability" if "Vulnerability" in ben_full.columns else None
vuln = f4.selectbox("Vulnérabilité", ["Toutes"] + sorted(ben_full[vuln_col].dropna().unique().tolist())) if vuln_col else "Toutes"

ben = ben_full.copy()
if province != "Toutes":
    ben = ben[ben["Province"] == province]
if sector != "Tous" and "Sector" in ben.columns:
    ben = ben[ben["Sector"] == sector]
if disp_status != "Tous":
    ben = ben[ben["Displacement_Status"] == disp_status]
if vuln_col and vuln != "Toutes":
    ben = ben[ben[vuln_col] == vuln]

if ben.empty:
    st.info("Aucun bénéficiaire ne correspond aux filtres sélectionnés.")
    st.stop()

st.divider()

# --- KPI -----------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Bénéficiaires", f"{len(ben):,}".replace(",", " "))
c2.metric("Ménages", ben["Household_ID"].nunique())
if "Sex" in ben.columns:
    pct_f = 100 * (ben["Sex"] == "F").mean()
    c3.metric("Part féminine", f"{pct_f:.0f}%")
if "Age" in ben.columns:
    c4.metric("Âge médian", f"{ben['Age'].median():.0f} ans")

st.divider()

col_a, col_b = st.columns(2)
with col_a:
    if "Age" in ben.columns:
        st.markdown("#### Pyramide des âges")
        bins = [0, 5, 12, 18, 60, 120]
        labels = ["0-4", "5-11", "12-17", "18-59", "60+"]
        ben["Tranche_age"] = pd.cut(ben["Age"], bins=bins, labels=labels, right=False)
        age_counts = ben["Tranche_age"].value_counts().reindex(labels).reset_index()
        age_counts.columns = ["Tranche d'âge", "Nombre"]
        fig = px.bar(age_counts, x="Tranche d'âge", y="Nombre")
        fig.update_layout(height=340)
        st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown("#### Statut de déplacement")
    disp_counts = ben["Displacement_Status"].value_counts().reset_index()
    disp_counts.columns = ["Statut", "Nombre"]
    fig2 = px.pie(disp_counts, names="Statut", values="Nombre", hole=0.45)
    fig2.update_layout(height=340)
    st.plotly_chart(fig2, use_container_width=True)

if vuln_col:
    st.divider()
    st.markdown("#### Types de vulnérabilité")
    vc = ben[vuln_col].value_counts().reset_index()
    vc.columns = ["Vulnérabilité", "Nombre"]
    fig3 = px.bar(vc, x="Vulnérabilité", y="Nombre", color="Vulnérabilité")
    fig3.update_layout(showlegend=False, height=320, xaxis_tickangle=-20)
    st.plotly_chart(fig3, use_container_width=True)

st.divider()
with st.expander(f"📋 Registre détaillé ({len(ben)} bénéficiaires)"):
    st.dataframe(ben.drop(columns=["Tranche_age"], errors="ignore"), use_container_width=True, hide_index=True)
    st.download_button(
        "Télécharger le registre filtré (CSV)",
        ben.drop(columns=["Tranche_age"], errors="ignore").to_csv(index=False).encode("utf-8"),
        file_name="Beneficiaires_export.csv",
        mime="text/csv",
    )
