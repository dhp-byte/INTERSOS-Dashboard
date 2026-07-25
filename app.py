"""
app.py — Point d'entrée de la plateforme MEAL/IM INTERSOS Tchad.

Gère l'authentification puis affiche la page Overview (vue d'ensemble
mission), point de départ vers les pages sectorielles listées dans pages/.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

import config
from utils import data_loader as dl
from utils import theme

st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


def _check_login(username: str, password: str) -> dict | None:
    """Vérifie les identifiants contre les comptes de démonstration.

    En production, remplacer par un backend d'authentification (secrets.toml
    + hash de mot de passe) — cf. .streamlit/secrets.toml.example.
    """
    user = config.DEMO_USERS.get(username)
    if user and user["password"] == password:
        return user
    return None


def render_login() -> None:
    """Affiche l'écran de connexion."""
    theme.inject_theme_css()
    t = theme.get_active_theme()
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown(
            f"""<div style="text-align:center; margin-top:40px; margin-bottom:10px;">
            <div style="display:inline-flex; align-items:center; justify-content:center;
                        width:64px; height:64px; border-radius:16px;
                        background:{t['primary']}; font-size:32px; margin-bottom:10px;">
                {config.APP_ICON}
            </div>
            </div>""",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<h2 style='text-align:center;margin:0;'>{config.APP_TITLE}</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align:center;opacity:.7;'>Gestion de l'Information Humanitaire — MEAL / IM</p>",
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            username = st.text_input("Identifiant")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter", use_container_width=True)
        if submitted:
            user = _check_login(username, password)
            if user:
                st.session_state["auth_user"] = user
                st.session_state["auth_username"] = username
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")
        st.caption("Démo : im_manager / intersos2026")


def render_sidebar(sheets: dict[str, pd.DataFrame], cover: dict[str, str]) -> None:
    """Barre latérale : identité, thème, filtres globaux persistés en session."""
    user = st.session_state["auth_user"]
    st.sidebar.markdown(f"**{user['name']}**")
    st.sidebar.caption(user["role"])
    st.sidebar.selectbox("Thème", ["Mission Control", "Aurora"], key="theme_mode")

    st.sidebar.divider()
    st.sidebar.markdown("### Filtres globaux")
    provinces = ["Toutes"] + dl.get_provinces(sheets)
    st.session_state["filter_province"] = st.sidebar.selectbox("Province", provinces)

    sectors = ["Tous"] + dl.get_sector_sheet_names(sheets)
    st.session_state["filter_sector"] = st.sidebar.selectbox("Secteur", sectors)

    donors = ["Tous"] + dl.get_donors(sheets)
    st.session_state["filter_donor"] = st.sidebar.selectbox("Donateur", donors)

    st.sidebar.divider()
    if st.sidebar.button("Se déconnecter", use_container_width=True):
        for k in ("auth_user", "auth_username"):
            st.session_state.pop(k, None)
        st.rerun()


def render_overview(sheets: dict[str, pd.DataFrame], cover: dict[str, str]) -> None:
    """Page Overview : KPI globaux, répartition sectorielle, alertes indicateurs."""
    theme.inject_theme_css()

    t = theme.get_active_theme()
    st.markdown(
        f"""<div class="im-header">
        <div><h2 style="margin:0;color:{t['primary']};">{config.APP_ICON} {config.APP_TITLE}</h2>
        <span style="opacity:.7;">{cover.get('Mission', '')}</span></div>
        </div>""",
        unsafe_allow_html=True,
    )

    nav1, nav2, nav3, nav4 = st.columns(4)
    nav1.page_link("pages/2_🗺️_Cartographie.py", label="🗺️ Cartographie", use_container_width=True)
    nav2.page_link("pages/9_👥_Beneficiaires.py", label="👥 Bénéficiaires", use_container_width=True)
    nav3.page_link("pages/11_🚨_Alertes.py", label="🚨 Alertes", use_container_width=True)
    nav4.page_link("pages/10_📄_Rapports.py", label="📄 Rapports", use_container_width=True)

    st.divider()

    ben = sheets[config.SHEET_BENEFICIARIES]
    indicators = sheets[config.SHEET_INDICATORS]
    sector_sheets = dl.get_sector_sheet_names(sheets)

    # --- KPI globaux ---------------------------------------------------
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Bénéficiaires enregistrés", f"{len(ben):,}".replace(",", " "))
    c2.metric("Ménages", f"{ben['Household_ID'].nunique():,}".replace(",", " "))
    c3.metric("Provinces couvertes", dl.get_provinces(sheets).__len__())
    c4.metric("Secteurs actifs", len(sector_sheets))
    on_track = (indicators["Achievement_%"] >= config.ACHIEVEMENT_THRESHOLDS["on_track_min"]).sum()
    c5.metric("Indicateurs en bonne voie", f"{on_track}/{len(indicators)}")

    st.divider()

    with st.expander("ℹ️ Contexte de la mission INTERSOS Tchad (source : site officiel)"):
        oc = config.ORG_CONTEXT
        oc1, oc2, oc3, oc4 = st.columns(4)
        oc1.metric("Présence depuis", oc["first_intervention"])
        oc2.metric("Personnes atteintes (mission)", f"{oc['people_reached']:,}".replace(",", " "))
        oc3.metric("Projets en cours", oc["projects"])
        oc4.metric("Budget dépensé", f"{oc['budget_spent_eur']:,} €".replace(",", " "))
        st.caption(
            "Chiffres au niveau de la mission Tchad dans son ensemble (dernier rapport public), "
            "à ne pas confondre avec les totaux du projet MEAL suivis ci-dessous, qui portent sur "
            "le périmètre du présent classeur de données. Secteurs officiels de la mission : "
            + ", ".join(oc["official_sectors"]) + f". Source : {oc['source_url']}"
        )

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Bénéficiaires par secteur")
        by_sector = ben["Sector"].value_counts().reset_index()
        by_sector.columns = ["Secteur", "Bénéficiaires"]
        fig = px.bar(
            by_sector, x="Secteur", y="Bénéficiaires", color="Secteur",
            color_discrete_map=config.SECTOR_COLORS,
        )
        fig.update_layout(showlegend=False, height=360)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### Bénéficiaires par statut de déplacement")
        by_status = ben["Displacement_Status"].value_counts().reset_index()
        by_status.columns = ["Statut", "Bénéficiaires"]
        fig2 = px.pie(by_status, names="Statut", values="Bénéficiaires", hole=0.45)
        fig2.update_layout(height=360)
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.markdown("#### Suivi des indicateurs (Achievement_%)")
    indicators_sorted = indicators.sort_values("Achievement_%")
    for _, row in indicators_sorted.iterrows():
        cols = st.columns([3, 1, 1, 2])
        cols[0].write(row["Indicator"])
        cols[1].write(row["Sector"])
        cols[2].write(f"{row['Achievement_%']:.1f}%")
        cols[3].markdown(theme.badge_for_achievement(row["Achievement_%"]), unsafe_allow_html=True)
    st.page_link("pages/11_🚨_Alertes.py", label="Voir le détail des alertes →")

    st.divider()
    with st.expander("🔍 Rapport de qualité des données (Étape 0 — analyse automatique)"):
        st.dataframe(dl.compute_data_quality_report(sheets), use_container_width=True, hide_index=True)
        mismatches = dl.province_name_mismatches(sheets)
        if mismatches["provinces_sans_geometrie"]:
            st.warning(f"Provinces sans géométrie GeoJSON : {mismatches['provinces_sans_geometrie']}")
        else:
            st.success("Toutes les provinces des données possèdent une géométrie GeoJSON correspondante.")

    st.markdown(
        f"""<p style="text-align:center; opacity:.5; font-size:0.8rem; margin-top:24px;">
        Plateforme MEAL / IM — INTERSOS Tchad · Développée par Djaoyang Habekreo Pelandi
        </p>""",
        unsafe_allow_html=True,
    )


def main() -> None:
    if "auth_user" not in st.session_state:
        render_login()
        return

    try:
        sheets = dl.load_excel_sheets()
        cover = dl.get_cover_info(sheets)
    except (FileNotFoundError, RuntimeError) as exc:
        st.error(str(exc))
        return

    render_sidebar(sheets, cover)
    render_overview(sheets, cover)


if __name__ == "__main__":
    main()
