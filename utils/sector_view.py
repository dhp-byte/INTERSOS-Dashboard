"""
utils/sector_view.py — Moteur générique de rendu d'une page sectorielle.

Une seule fonction `render_sector_page(sheet_name, sheets)` est appelée par
chacune des 6 pages sectorielles (pages/3 à 8). Elle s'appuie uniquement sur :
  - les données réelles de la feuille Excel correspondante ;
  - la configuration déclarative `config.SECTOR_CONFIG[sheet_name]`.
Aucune donnée métier n'est fabriquée : toute colonne absente est simplement
ignorée (garde `if col in df.columns`).
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

import config
from utils import data_loader as dl
from utils import theme
from utils import topbar


def _kpi_row(df: pd.DataFrame, cfg: dict) -> None:
    """Affiche la ligne de KPI : cible, atteint, taux de réalisation, activités."""
    target_col, reached_col = cfg["target_col"], cfg["reached_col"]
    cols = st.columns(4 + len(cfg.get("extra_metrics", [])))

    target_total = df[target_col].sum() if target_col in df.columns else None
    reached_total = df[reached_col].sum() if reached_col in df.columns else None

    cols[0].metric("Activités", len(df))
    if target_total is not None:
        cols[1].metric("Cible cumulée", f"{target_total:,.0f}".replace(",", " "))
    if reached_total is not None:
        cols[2].metric("Atteint cumulé", f"{reached_total:,.0f}".replace(",", " "))
    if target_total and reached_total is not None:
        pct = 100 * reached_total / target_total if target_total else 0
        cols[3].metric("Taux de réalisation", f"{pct:.1f}%")

    for i, extra in enumerate(cfg.get("extra_metrics", []), start=4):
        col_name = extra["col"]
        if col_name in df.columns:
            value = df[col_name].agg(extra["agg"])
            fmt = f"{value:.1%}" if "Rate" in col_name else f"{value:,.0f}".replace(",", " ")
            cols[i].metric(extra["label"], fmt)


def _status_and_gender(df: pd.DataFrame) -> None:
    """Répartition par statut d'activité et par genre (Reached_Male/Female)."""
    c1, c2 = st.columns(2)
    with c1:
        if "Status" in df.columns:
            st.markdown("#### Statut des activités")
            counts = df["Status"].value_counts().reset_index()
            counts.columns = ["Statut", "Nombre"]
            fig = px.pie(counts, names="Statut", values="Nombre", hole=0.45)
            fig.update_layout(height=320)
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        if {"Reached_Male", "Reached_Female"}.issubset(df.columns):
            st.markdown("#### Répartition par genre")
            gender = pd.DataFrame(
                {"Genre": ["Hommes", "Femmes"], "Atteint": [df["Reached_Male"].sum(), df["Reached_Female"].sum()]}
            )
            fig2 = px.bar(gender, x="Genre", y="Atteint", color="Genre")
            fig2.update_layout(showlegend=False, height=320)
            st.plotly_chart(fig2, use_container_width=True)


def _shades(hex_color: str, n: int) -> list[str]:
    """Génère n nuances (claire → foncée) d'une couleur de secteur, pour que
    chaque page sectorielle garde une identité visuelle cohérente plutôt que
    la palette qualitative générique de Plotly."""
    import colorsys

    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    n = max(n, 1)
    lightness_range = [0.35 + 0.4 * (i / max(n - 1, 1)) for i in range(n)]
    shades = []
    for lval in lightness_range:
        rr, gg, bb = colorsys.hls_to_rgb(h, lval, min(s + 0.1, 1.0))
        shades.append(f"#{int(rr*255):02x}{int(gg*255):02x}{int(bb*255):02x}")
    return shades


def _breakdowns(df: pd.DataFrame, dims: list[str], sector_color: str = "#4C6EF5") -> None:
    """Graphiques en barres pour chaque dimension de ventilation configurée,
    dans les nuances de la couleur du secteur (identité visuelle cohérente)."""
    present = [d for d in dims if d in df.columns]
    if not present:
        return
    cols = st.columns(len(present))
    for col_widget, dim in zip(cols, present):
        with col_widget:
            st.markdown(f"#### Par {dim.replace('_', ' ')}")
            counts = df[dim].value_counts().reset_index()
            counts.columns = [dim, "Nombre"]
            palette = _shades(sector_color, len(counts))
            fig = px.bar(counts, x=dim, y="Nombre", color=dim, color_discrete_sequence=palette)
            fig.update_layout(showlegend=False, height=340, xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)


def _trend(df: pd.DataFrame, cfg: dict, sector_color: str = "#4C6EF5") -> None:
    """Courbe temporelle atteint vs cible si une colonne de date existe.
    L'atteint est tracé dans la couleur du secteur, la cible en gris pointillé
    de référence."""
    date_col = next((c for c in df.columns if c.startswith("Date")), None)
    if not date_col:
        return
    target_col, reached_col = cfg["target_col"], cfg["reached_col"]
    if not {target_col, reached_col}.issubset(df.columns):
        return
    st.markdown("#### Évolution mensuelle (cible vs atteint)")
    tmp = df.dropna(subset=[date_col]).copy()
    tmp["Mois"] = tmp[date_col].dt.to_period("M").astype(str)
    monthly = tmp.groupby("Mois")[[target_col, reached_col]].sum().reset_index()
    fig = px.line(
        monthly, x="Mois", y=[target_col, reached_col], markers=True,
        color_discrete_map={target_col: "#9AA3B5", reached_col: sector_color},
    )
    fig.update_traces(line=dict(dash="dash"), selector=dict(name=target_col))
    fig.update_layout(height=340, legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)


def _province_ranking(df: pd.DataFrame, cfg: dict, sector_color: str) -> None:
    """Tableau + graphique du taux de réalisation par province, pour situer
    rapidement les zones en avance ou en retard sur leurs cibles."""
    target_col, reached_col = cfg["target_col"], cfg["reached_col"]
    if not {target_col, reached_col, "Province"}.issubset(df.columns):
        return
    grouped = df.groupby("Province")[[target_col, reached_col]].sum().reset_index()
    grouped = grouped[grouped[target_col] > 0]
    if grouped.empty:
        return
    grouped["Taux (%)"] = (100 * grouped[reached_col] / grouped[target_col]).round(1)
    grouped = grouped.sort_values("Taux (%)", ascending=False)

    st.markdown("#### Classement des provinces par taux de réalisation")
    col_tbl, col_chart = st.columns([1, 1.2])
    with col_tbl:
        st.dataframe(
            grouped.rename(columns={target_col: "Cible", reached_col: "Atteint"}),
            use_container_width=True, hide_index=True,
        )
    with col_chart:
        palette = _shades(sector_color, len(grouped))
        fig = px.bar(grouped, x="Province", y="Taux (%)", color="Province", color_discrete_sequence=palette)
        fig.add_hline(y=100, line_dash="dash", line_color="#9AA3B5")
        fig.update_layout(showlegend=False, height=320, xaxis_tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)


def render_sector_page(sheet_name: str, sheets: dict[str, pd.DataFrame]) -> None:
    """Point d'entrée appelé par chaque page sectorielle."""
    theme.inject_theme_css()
    cfg = config.SECTOR_CONFIG.get(sheet_name, {})
    icon = cfg.get("icon", "📁")
    sector_color = cfg.get("color", "#4C6EF5")
    df_full = sheets[sheet_name]

    nav_label = {
        "Sante": "Santé", "Securite_Alimentaire": "Sécurité Alim.", "Abri_NFI": "Abri/NFI",
    }.get(sheet_name, sheet_name)
    topbar.render_topbar(nav_label)

    st.markdown(
        f"""<div style="border-left:5px solid {sector_color}; padding:4px 0 4px 14px; margin-bottom:6px;">
        <h2 style="margin:0;">{icon} {sheet_name.replace('_', ' ')}</h2></div>""",
        unsafe_allow_html=True,
    )

    # --- Filtres locaux --------------------------------------------------
    fcols = st.columns(4)
    provinces = ["Toutes"] + sorted(df_full["Province"].dropna().unique().tolist())
    province = fcols[0].selectbox("Province", provinces, key=f"{sheet_name}_prov")

    statuses = ["Tous"] + sorted(df_full["Status"].dropna().unique().tolist()) if "Status" in df_full.columns else ["Tous"]
    status = fcols[1].selectbox("Statut activité", statuses, key=f"{sheet_name}_status")

    donors = ["Tous"] + sorted(df_full["Donor"].dropna().unique().tolist()) if "Donor" in df_full.columns else ["Tous"]
    donor = fcols[2].selectbox("Donateur", donors, key=f"{sheet_name}_donor")

    disp_statuses = (
        ["Tous"] + sorted(df_full["Displacement_Status"].dropna().unique().tolist())
        if "Displacement_Status" in df_full.columns
        else ["Tous"]
    )
    disp_status = fcols[3].selectbox("Statut déplacement", disp_statuses, key=f"{sheet_name}_disp")

    df = df_full.copy()
    if province != "Toutes":
        df = df[df["Province"] == province]
    if status != "Tous":
        df = df[df["Status"] == status]
    if donor != "Tous":
        df = df[df["Donor"] == donor]
    if disp_status != "Tous":
        df = df[df["Displacement_Status"] == disp_status]

    if df.empty:
        st.info("Aucune activité ne correspond aux filtres sélectionnés.")
        return

    st.divider()
    _kpi_row(df, cfg)
    st.divider()
    _status_and_gender(df)
    st.divider()
    _breakdowns(df, cfg.get("breakdown_dims", []), sector_color)
    st.divider()
    _province_ranking(df, cfg, sector_color)
    st.divider()
    _trend(df, cfg, sector_color)

    st.divider()
    with st.expander(f"📋 Détail des activités ({len(df)} lignes)"):
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "Télécharger ce tableau (CSV)",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"{sheet_name}_export.csv",
            mime="text/csv",
        )
