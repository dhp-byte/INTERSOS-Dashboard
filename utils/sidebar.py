"""
utils/sidebar.py — Contrôles globaux partagés (thème, seuils d'alerte),
à instancier sur CHAQUE page (et pas seulement l'accueil) pour que le
sélecteur de thème reste toujours visible et applique bien son choix
partout, quelle que soit la page depuis laquelle il est actionné.
"""

from __future__ import annotations

import streamlit as st

from utils import theme


def render_global_controls() -> None:
    """Affiche, dans la barre latérale, le sélecteur de thème et les seuils
    d'alerte configurables. Le widget de thème étant instancié sur chaque
    page avec la même clé de session ("theme_mode"), Streamlit y reflète et
    y applique systématiquement la valeur actuellement sélectionnée."""
    st.sidebar.selectbox("Thème", ["Aurora", "Mission Control"], key="theme_mode")

    with st.sidebar.expander("⚙️ Seuils d'alerte"):
        current = theme.get_thresholds()
        on_track_min = st.slider(
            "Seuil « En bonne voie » (%)", min_value=50, max_value=120,
            value=int(current["on_track_min"]), key="th_on_track",
        )
        watch_min = st.slider(
            "Seuil « À surveiller » (%)", min_value=0, max_value=on_track_min,
            value=min(int(current["watch_min"]), on_track_min), key="th_watch",
        )
        st.session_state["achievement_thresholds"] = {
            "on_track_min": float(on_track_min),
            "watch_min": float(watch_min),
        }
        st.caption("Ajuste en direct les badges et le moteur d'alertes sur toutes les pages.")
