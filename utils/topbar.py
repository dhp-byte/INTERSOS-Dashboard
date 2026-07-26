"""
utils/topbar.py — Barre de navigation supérieure personnalisée.

Remplace la liste de pages native de Streamlit (masquée via CSS dans
utils.theme) par une barre brandée avec logo, titre et raccourcis vers les
pages principales — inspirée de la topbar du dashboard SI Sudan.
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


def render_topbar(active: str = "Accueil") -> None:
    """Affiche la barre supérieure de marque, puis une rangée de raccourcis
    de navigation vers les pages principales (les plus consultées)."""
    t = theme.get_active_theme()
    st.markdown(
        f"""<div class="im-topbar">
            <div class="im-logo-box">{config.APP_ICON}</div>
            <div class="im-brand">{config.APP_TITLE}
                <small>MEAL / Information Management — Tchad</small>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    quick = ["Accueil", "Cartographie", "Bénéficiaires", "Alertes", "Rapports"]
    cols = st.columns(len(quick))
    lookup = {label: (path, icon) for label, path, icon in NAV_ITEMS}
    for col, label in zip(cols, quick):
        path, icon = lookup[label]
        marker = "▸ " if label == active else ""
        col.page_link(path, label=f"{marker}{icon} {label}", use_container_width=True)
