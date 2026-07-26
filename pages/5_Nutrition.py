"""
pages/5_Nutrition.py — Page sectorielle Nutrition (rendu via utils.sector_view, moteur
générique piloté par config.SECTOR_CONFIG["Nutrition"]).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st

from utils import data_loader as dl
from utils.sector_view import render_sector_page

st.set_page_config(page_title="Nutrition — INTERSOS Tchad", page_icon="🍲", layout="wide")

if "auth_user" not in st.session_state:
    st.warning("Veuillez vous connecter depuis la page d'accueil.")
    st.stop()

try:
    sheets = dl.load_excel_sheets()
except (FileNotFoundError, RuntimeError) as exc:
    st.error(str(exc))
    st.stop()

render_sector_page("Nutrition", sheets)
