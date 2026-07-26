"""
utils/topbar.py — Barre de navigation supérieure personnalisée.

Remplace la liste de pages native de Streamlit (masquée via CSS dans
utils.theme) par une barre brandée avec le logo officiel INTERSOS et des
raccourcis vers l'ensemble des pages de l'application — inspirée de la
topbar du dashboard SI Sudan.
"""

from __future__ import annotations

import streamlit as st

import config
from utils import theme

# (label affiché, chemin de fichier, icône)
NAV_ITEMS: list[tuple[str, str, str]] = [
    ("Accueil", "app.py", "🏠"),
    ("Cartographie", "pages/2_Cartographie.py", "🗺️"),
    ("Protection", "pages/3_Protection.py", "🛡️"),
    ("Santé", "pages/4_Sante.py", "🩺"),
    ("Nutrition", "pages/5_Nutrition.py", "🍲"),
    ("WASH", "pages/6_WASH.py", "💧"),
    ("Sécurité Alim.", "pages/7_Securite_Alimentaire.py", "🌾"),
    ("Abri/NFI", "pages/8_Abri_NFI.py", "🏠"),
    ("Bénéficiaires", "pages/9_Beneficiaires.py", "👥"),
    ("Rapports", "pages/10_Rapports.py", "📄"),
    ("Alertes", "pages/11_Alertes.py", "🚨"),
]

# Répartition sur deux rangées pour rester lisible avec 11 pages
NAV_ROW_1 = ["Accueil", "Cartographie", "Protection", "Santé", "Nutrition", "WASH"]
NAV_ROW_2 = ["Sécurité Alim.", "Abri/NFI", "Bénéficiaires", "Alertes", "Rapports"]


def _nav_row(labels: list[str], active: str, lookup: dict) -> None:
    cols = st.columns(len(labels))
    for col, label in zip(cols, labels):
        path, icon = lookup[label]
        marker = "▸ " if label == active else ""
        col.page_link(path, label=f"{marker}{icon} {label}", use_container_width=True)


def render_topbar(active: str = "Accueil") -> None:
    """Affiche la barre supérieure de marque (logo officiel INTERSOS), puis
    deux rangées de raccourcis vers l'ensemble des pages de l'application."""
    st.markdown(
        f"""<div class="im-topbar">
            <div class="im-logo-box"><img src="{config.LOGO_URL}" alt="INTERSOS"></div>
            <div class="im-brand">{config.APP_TITLE}
                <small>MEAL / Information Management — Tchad</small>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    lookup = {label: (path, icon) for label, path, icon in NAV_ITEMS}
    _nav_row(NAV_ROW_1, active, lookup)
    _nav_row(NAV_ROW_2, active, lookup)
