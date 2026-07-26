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
    stocké dans st.session_state (par défaut : Aurora)."""
    mode = st.session_state.get("theme_mode", "Aurora")
    return config.THEME_AURORA if mode == "Aurora" else config.THEME_MISSION_CONTROL


def get_thresholds() -> dict:
    """Seuils d'alerte actifs : ceux ajustés par l'utilisateur dans la barre
    latérale (session) prévalent sur les valeurs par défaut de config.py."""
    return st.session_state.get("achievement_thresholds", config.ACHIEVEMENT_THRESHOLDS)


def inject_theme_css() -> None:
    """Injecte le CSS du thème actif dans la page Streamlit courante."""
    t = get_active_theme()
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');
        html, body, .stApp {{ font-family: 'Outfit', sans-serif; }}
        .stApp {{
            background-color: {t['bg']};
            color: {t['text']};
        }}
        /* Masquer la navigation multipage native : remplacée par la barre
           de navigation personnalisée (utils/topbar.py) */
        [data-testid="stSidebarNav"] {{ display: none; }}
        [data-testid="stHeader"] {{
            background-color: {t['bg_secondary']};
            border-bottom: 3px solid {t['primary']};
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

        /* ---- Topbar ---------------------------------------------------- */
        .im-topbar {{
            background: {t['bg_secondary']};
            border-bottom: 3px solid {t['primary']};
            border-radius: 12px;
            padding: 10px 18px;
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 14px;
        }}
        .im-logo-box {{
            width: 44px; height: 44px; border-radius: 8px;
            background: #FFFFFF;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.2rem; flex-shrink: 0; padding: 4px;
            border: 1px solid {t['border']};
        }}
        .im-logo-box img {{ width: 100%; height: 100%; object-fit: contain; }}
        .im-brand {{ font-size: 0.98rem; font-weight: 800; color: {t['text']}; line-height: 1.15; }}
        .im-brand small {{
            display: block; font-size: 0.62rem; color: {t['text_muted']};
            font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase;
        }}

        /* ---- Hero ------------------------------------------------------- */
        .im-hero {{
            position: relative; overflow: hidden; border-radius: 14px;
            margin-bottom: 1rem; padding: 1.8rem 2.2rem; min-height: 190px;
            background: linear-gradient(135deg, {t['primary_dark']} 0%, {t['bg']} 85%);
            border: 1px solid {t['border']};
            display: flex; flex-direction: column; justify-content: flex-end;
        }}
        .im-hero img {{
            position: absolute; inset: 0; width: 100%; height: 100%;
            object-fit: cover; opacity: 0.32;
            filter: brightness(0.7) saturate(1.15);
        }}
        .im-hero-content {{ position: relative; z-index: 2; }}
        .im-hero-tag {{
            display: inline-block; background: {t['accent']}; color: #16213A;
            font-size: 0.66rem; font-weight: 800; letter-spacing: 0.1em;
            text-transform: uppercase; padding: 3px 10px; border-radius: 4px;
            margin-bottom: 0.6rem;
        }}
        .im-hero-title {{ font-size: 1.7rem; font-weight: 800; color: #fff; margin: 0 0 4px;
            text-shadow: 0 2px 16px rgba(0,0,0,0.5); }}
        .im-hero-sub {{ font-size: 0.85rem; color: rgba(255,255,255,0.8); margin: 0; max-width: 760px; }}
        .im-hero-bar {{
            position: absolute; bottom: 0; left: 0; right: 0; height: 4px; z-index: 2;
            background: linear-gradient(90deg, {t['primary']}, {t['accent']}, {t['primary']});
            animation: im-pulse 3s ease-in-out infinite;
        }}
        @keyframes im-pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.55; }} }}

        /* ---- Carrousel d'images (défilement horizontal infini) ---------- */
        .im-img-slider {{ overflow: hidden; border-radius: 10px; margin: 0 0 1.4rem 0; }}
        .im-img-track {{
            display: flex; gap: 10px; width: max-content;
            animation: im-slide 34s linear infinite;
        }}
        .im-img-track img {{
            height: 130px; width: 210px; object-fit: cover; border-radius: 8px;
            flex-shrink: 0; border: 1px solid {t['border']};
            filter: brightness(0.85) saturate(1.05);
            transition: filter .25s;
        }}
        .im-img-track img:hover {{ filter: brightness(1) saturate(1.25); }}
        @keyframes im-slide {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}

        /* ---- KPI cards --------------------------------------------------- */
        .im-kpi {{
            background: {t['surface']}; border: 1px solid {t['border']};
            border-radius: 12px; padding: 14px 16px; height: 100%;
        }}
        .im-kpi-icon {{
            width: 30px; height: 30px; border-radius: 7px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1rem; margin-bottom: 8px;
        }}
        .im-kpi-value {{ font-size: 1.5rem; font-weight: 800; color: {t['text']}; line-height: 1.1; }}
        .im-kpi-label {{ font-size: 0.75rem; color: {t['text_muted']}; margin-top: 2px; }}
        .im-kpi-delta {{ font-size: 0.72rem; font-weight: 700; margin-top: 6px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def badge_for_achievement(pct: float) -> str:
    """Retourne le HTML d'un badge coloré selon le seuil d'atteinte de l'indicateur."""
    th = get_thresholds()
    if pct >= th["on_track_min"]:
        cls, label = "im-badge-ontrack", "En bonne voie"
    elif pct >= th["watch_min"]:
        cls, label = "im-badge-watch", "À surveiller"
    else:
        cls, label = "im-badge-critical", "Retard critique"
    return f'<span class="im-badge {cls}">{label}</span>'
