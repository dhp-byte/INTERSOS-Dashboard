"""
pages/10_Rapports.py — Génération à la demande d'un rapport de synthèse
exécutive (Word ou PDF), à partir des données réelles du classeur.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st

import config
from utils import data_loader as dl
from utils import report_generator as rg
from utils import theme
from utils import topbar

st.set_page_config(page_title="Rapports — INTERSOS Tchad", page_icon="📄", layout="wide")

if "auth_user" not in st.session_state:
    st.warning("Veuillez vous connecter depuis la page d'accueil.")
    st.stop()

theme.inject_theme_css()
topbar.render_topbar("Rapports")

try:
    sheets = dl.load_excel_sheets()
    cover = dl.get_cover_info(sheets)
except (FileNotFoundError, RuntimeError) as exc:
    st.error(str(exc))
    st.stop()

st.markdown("## 📄 Rapports de synthèse")
st.caption(
    "Génère un rapport exécutif (KPI globaux, performance par secteur, suivi des indicateurs, "
    "qualité des données) directement à partir du classeur de référence."
)

st.divider()
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### 📝 Rapport Word (.docx)")
    st.write("Format éditable, adapté à la relecture et à l'annotation par l'équipe MEAL.")
    if st.button("Générer le rapport Word", use_container_width=True, key="gen_docx"):
        with st.spinner("Génération du document Word en cours..."):
            docx_bytes = rg.build_docx_report(sheets, cover, theme.get_thresholds())
        st.success("Rapport Word généré.")
        st.download_button(
            "⬇️ Télécharger le rapport (.docx)",
            data=docx_bytes,
            file_name=f"INTERSOS_Tchad_Rapport_{datetime.now():%Y%m%d}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )

with c2:
    st.markdown("#### 📕 Rapport PDF")
    st.write("Format figé, adapté à la diffusion aux bailleurs et partenaires.")
    if st.button("Générer le rapport PDF", use_container_width=True, key="gen_pdf"):
        with st.spinner("Génération du document PDF en cours..."):
            pdf_bytes = rg.build_pdf_report(sheets, cover, theme.get_thresholds())
        st.success("Rapport PDF généré.")
        st.download_button(
            "⬇️ Télécharger le rapport (.pdf)",
            data=pdf_bytes,
            file_name=f"INTERSOS_Tchad_Rapport_{datetime.now():%Y%m%d}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

st.divider()
with st.expander("Contenu du rapport"):
    st.markdown(
        """
        1. **Indicateurs clés** — bénéficiaires, ménages, provinces, secteurs, indicateurs en bonne voie
        2. **Performance par secteur** — activités, cible cumulée, atteint cumulé, taux de réalisation, **graphique en barres**
        3. **Suivi des indicateurs** — statut (En bonne voie / À surveiller / Retard critique) pour chacun des 24 indicateurs, **graphique de synthèse**
        4. **Qualité des données** — lignes, colonnes, valeurs manquantes, doublons par feuille, cohérence géographique
        """
    )
