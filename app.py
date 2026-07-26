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
from utils import sidebar
from utils import theme
from utils import topbar
from utils.kpi_card import hero, image_slider, kpi_card
from utils.trends import month_over_month_delta

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
        logo_url = getattr(config, "LOGO_URL", "")
        logo_html = (
            f'<img src="{logo_url}" alt="INTERSOS" style="max-width:100%; max-height:100%; object-fit:contain;">'
            if logo_url else config.APP_ICON
        )
        st.markdown(
            f"""<div style="text-align:center; margin-top:40px; margin-bottom:10px;">
            <div style="display:inline-flex; align-items:center; justify-content:center;
                        width:120px; height:80px; border-radius:12px;
                        background:#FFFFFF; border:1px solid {t['border']}; padding:10px; font-size:32px;">
                {logo_html}
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
    """Barre latérale : identité, thème, filtres globaux et seuils d'alerte
    configurables (persistés en session)."""
    user = st.session_state["auth_user"]
    st.sidebar.markdown(f"**{user['name']}**")
    st.sidebar.caption(user["role"])
    sidebar.render_global_controls()

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
    """Page Overview : hero, cartes KPI, répartition sectorielle, alertes indicateurs."""
    theme.inject_theme_css()
    topbar.render_topbar("Accueil")

    ben = sheets[config.SHEET_BENEFICIARIES]
    indicators = sheets[config.SHEET_INDICATORS]
    sector_sheets = dl.get_sector_sheet_names(sheets)
    th = theme.get_thresholds()

    oc = config.ORG_CONTEXT
    st.markdown(
        hero(
            tag="Mission Tchad",
            title=cover.get("Mission", config.APP_TITLE),
            subtitle=(
                f"Présente depuis {oc['first_intervention']} · {len(dl.get_provinces(sheets))} provinces couvertes "
                f"dans le périmètre suivi · {len(sector_sheets)} secteurs actifs : "
                + ", ".join(s.replace("_", " ") for s in sector_sheets)
            ),
            bg_image=getattr(config, "HERO_BACKGROUND_IMAGE", None),
        ),
        unsafe_allow_html=True,
    )
    illustration_images = getattr(config, "ILLUSTRATION_IMAGES", [])
    if illustration_images:
        st.markdown(image_slider(illustration_images), unsafe_allow_html=True)

    # --- Cartes KPI ------------------------------------------------------
    ben_delta = month_over_month_delta(ben, "Date_Registration")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(
        kpi_card("Bénéficiaires enregistrés", f"{len(ben):,}".replace(",", " "), icon="👤",
                 color=config.THEME_MISSION_CONTROL["primary"], delta=ben_delta),
        unsafe_allow_html=True,
    )
    c2.markdown(
        kpi_card("Ménages", f"{ben['Household_ID'].nunique():,}".replace(",", " "), icon="🏘️", color="#40C057"),
        unsafe_allow_html=True,
    )
    c3.markdown(
        kpi_card("Provinces couvertes", str(len(dl.get_provinces(sheets))), icon="📍", color="#15AABF"),
        unsafe_allow_html=True,
    )
    c4.markdown(
        kpi_card("Secteurs actifs", str(len(sector_sheets)), icon="🧩", color="#F76707"),
        unsafe_allow_html=True,
    )
    on_track = (indicators["Achievement_%"] >= th["on_track_min"]).sum()
    c5.markdown(
        kpi_card("Indicateurs en bonne voie", f"{on_track}/{len(indicators)}", icon="🎯", color="#6C5CE7"),
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("ℹ️ Contexte de la mission INTERSOS Tchad (source : site officiel)"):
        oc1, oc2, oc3, oc4 = st.columns(4)
        oc1.metric("Présence depuis", oc["first_intervention"])
        oc2.metric("Personnes atteintes (mission)", f"{oc['people_reached']:,}".replace(",", " "))
        oc3.metric("Projets en cours", oc["projects"])
        oc4.metric("Budget dépensé", f"{oc['budget_spent_eur']:,} €".replace(",", " "))
        st.caption(
            "Chiffres au niveau de la mission Tchad dans son ensemble (dernier rapport public), "
            "à ne pas confondre avec les totaux du projet MEAL suivis ci-dessus, qui portent sur "
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
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("#### Évolution mensuelle des enregistrements")
        monthly = ben.dropna(subset=["Date_Registration"]).copy()
        monthly["Mois"] = monthly["Date_Registration"].dt.to_period("M").astype(str)
        monthly_counts = monthly.groupby("Mois").size().reset_index(name="Bénéficiaires")
        fig3 = px.line(monthly_counts, x="Mois", y="Bénéficiaires", markers=True)
        fig3.update_traces(line_color=config.THEME_MISSION_CONTROL["primary"])
        fig3.update_layout(height=320)
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        st.markdown("#### Top 5 provinces par bénéficiaires")
        top_provinces = ben["Province"].value_counts().head(5).reset_index()
        top_provinces.columns = ["Province", "Bénéficiaires"]
        st.dataframe(top_provinces, use_container_width=True, hide_index=True)
        fig4 = px.bar(top_provinces, x="Bénéficiaires", y="Province", orientation="h", color="Province",
                      color_discrete_sequence=["#3D6FE0", "#40C057", "#15AABF", "#F76707", "#6C5CE7"])
        fig4.update_layout(showlegend=False, height=220, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()
    st.markdown("#### Suivi des indicateurs (Achievement_%)")
    indicators_sorted = indicators.sort_values("Achievement_%")
    for _, row in indicators_sorted.iterrows():
        cols = st.columns([3, 1, 1, 2])
        cols[0].write(row["Indicator"])
        cols[1].write(row["Sector"])
        cols[2].write(f"{row['Achievement_%']:.1f}%")
        cols[3].markdown(theme.badge_for_achievement(row["Achievement_%"]), unsafe_allow_html=True)
    st.page_link("pages/11_Alertes.py", label="Voir le détail des alertes →")

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
