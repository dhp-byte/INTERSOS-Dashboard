"""
utils/theme.py — Application des thèmes visuels "Mission Control" (sombre)
et "Aurora" (clair) via injection CSS dans Streamlit.
"""

from __future__ import annotations

import streamlit as st

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config


def get_active_theme() -> dict:
    """Retourne le dictionnaire de thème actif selon le choix utilisateur
    stocké dans st.session_state (par défaut : Mission Control)."""
    mode = st.session_state.get("theme_mode", "Mission Control")
    return config.THEME_AURORA if mode == "Aurora" else config.THEME_MISSION_CONTROL


def inject_theme_css() -> None:
    """Injecte le CSS du thème actif dans la page Streamlit courante."""
    t = get_active_theme()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {t['bg']};
            color: {t['text']};
        }}
        section[data-testid="stSidebar"] {{
            background-color: {t['bg_secondary']};
            border-right: 1px solid {t['border']};
        }}
        div[data-testid="stMetric"] {{
            background-color: {t['surface']};
            border: 1px solid {t['border']};
            border-radius: 10px;
            padding: 14px 16px;
        }}
        div[data-testid="stMetricValue"] {{
            color: {t['primary']};
        }}
        .im-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 0 18px 0;
            border-bottom: 1px solid {t['border']};
            margin-bottom: 18px;
        }}
        .im-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }}
        .im-badge-ontrack {{ background-color: {t['success']}22; color: {t['success']}; }}
        .im-badge-watch {{ background-color: {t['warning']}22; color: {t['warning']}; }}
        .im-badge-critical {{ background-color: {t['danger']}22; color: {t['danger']}; }}
        .stButton>button {{
            background-color: {t['primary']};
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def badge_for_achievement(pct: float) -> str:
    """Retourne le HTML d'un badge coloré selon le seuil d'atteinte de l'indicateur."""
    th = config.ACHIEVEMENT_THRESHOLDS
    if pct >= th["on_track_min"]:
        cls, label = "im-badge-ontrack", "En bonne voie"
    elif pct >= th["watch_min"]:
        cls, label = "im-badge-watch", "À surveiller"
    else:
        cls, label = "im-badge-critical", "Retard critique"
    return f'<span class="im-badge {cls}">{label}</span>'
