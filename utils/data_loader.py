"""
utils/data_loader.py — Chargement et préparation des données de référence.

Toutes les fonctions publiques sont mises en cache (`st.cache_data`) et
renvoient des structures pandas/geopandas prêtes à l'emploi pour les pages
du dashboard. Aucune valeur métier (secteur, province, donateur...) n'est
codée en dur : tout est extrait dynamiquement des fichiers sources.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

logger = logging.getLogger("intersos_dashboard")
if not logger.handlers:
    handler = logging.FileHandler(config.LOGS_DIR / "system.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


@st.cache_data(ttl=config.CACHE_TTL_SECONDS, show_spinner=False)
def load_excel_sheets(excel_path: str = str(config.EXCEL_PATH)) -> dict[str, pd.DataFrame]:
    """Charge toutes les feuilles du classeur Excel de référence.

    Parameters
    ----------
    excel_path : str
        Chemin vers le fichier INTERSOS_Chad_Program_Database.xlsx.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionnaire {nom_feuille: DataFrame}, clés identiques aux noms de
        feuilles du classeur (jamais renommées, règle absolue du projet).

    Raises
    ------
    FileNotFoundError
        Si le fichier Excel de référence est introuvable.
    """
    path = Path(excel_path)
    if not path.exists():
        logger.error("Fichier Excel introuvable : %s", path)
        raise FileNotFoundError(
            f"Le fichier de référence '{path.name}' est introuvable dans data/. "
            "Vérifiez que INTERSOS_Chad_Program_Database.xlsx a bien été déposé."
        )
    try:
        xl = pd.ExcelFile(path)
        sheets = {name: xl.parse(name) for name in xl.sheet_names}
        for name, df in sheets.items():
            for col in df.columns:
                if "Date" in col:
                    sheets[name][col] = pd.to_datetime(df[col], errors="coerce")
        logger.info("Excel chargé : %d feuilles.", len(sheets))
        return sheets
    except Exception as exc:  # noqa: BLE001
        logger.exception("Erreur de chargement Excel")
        raise RuntimeError(f"Impossible de lire le fichier Excel : {exc}") from exc


@st.cache_data(ttl=config.CACHE_TTL_SECONDS, show_spinner=False)
def load_geojson(geojson_path: str = str(config.GEOJSON_PATH)) -> dict[str, Any]:
    """Charge le GeoJSON des régions administratives (admin1) du Tchad.

    Returns
    -------
    dict
        Objet GeoJSON brut (FeatureCollection).
    """
    import json

    path = Path(geojson_path)
    if not path.exists():
        logger.error("GeoJSON introuvable : %s", path)
        raise FileNotFoundError(f"Le fichier '{path.name}' est introuvable dans data/.")
    with open(path, encoding="utf-8") as f:
        gj = json.load(f)
    logger.info("GeoJSON chargé : %d régions.", len(gj.get("features", [])))
    return gj


@st.cache_data(ttl=config.CACHE_TTL_SECONDS, show_spinner=False)
def get_admin_centroids(geojson_path: str = str(config.GEOJSON_PATH)) -> dict[str, tuple[float, float]]:
    """Calcule le centroïde (lat, lon) de chaque région admin1 pour Folium.

    Utilise le centroïde du polygone (moyenne simple des anneaux extérieurs),
    suffisant pour le positionnement de marqueurs et libellés cartographiques.

    Returns
    -------
    dict[str, tuple[float, float]]
        {nom_region: (latitude, longitude)}
    """
    gj = load_geojson(geojson_path)
    centroids: dict[str, tuple[float, float]] = {}
    for feat in gj["features"]:
        name = feat["properties"]["name"]
        geom = feat["geometry"]
        coords = geom["coordinates"][0] if geom["type"] == "Polygon" else geom["coordinates"][0][0]
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        centroids[name] = (sum(lats) / len(lats), sum(lons) / len(lons))
    return centroids


def get_cover_info(sheets: dict[str, pd.DataFrame]) -> dict[str, str]:
    """Extrait les métadonnées de la feuille Cover sous forme de dictionnaire."""
    cover = sheets.get(config.SHEET_COVER)
    if cover is None:
        return {}
    return dict(zip(cover["Champ"], cover["Valeur"].astype(str)))


def get_sector_sheet_names(sheets: dict[str, pd.DataFrame]) -> list[str]:
    """Retourne dynamiquement la liste des feuilles sectorielles d'activités
    (toutes les feuilles hors Cover, Beneficiary_Registration, Indicator_Tracker)."""
    return [s for s in sheets if s not in config.SECTOR_SHEETS_EXCLUDED]


def get_provinces(sheets: dict[str, pd.DataFrame]) -> list[str]:
    """Liste dynamique des provinces réellement présentes dans les données
    opérationnelles (union sur toutes les feuilles sectorielles + bénéficiaires),
    et non celle — potentiellement obsolète — annoncée en page Cover."""
    provinces: set[str] = set()
    for name, df in sheets.items():
        if "Province" in df.columns:
            provinces.update(df["Province"].dropna().unique().tolist())
    return sorted(provinces)


def get_donors(sheets: dict[str, pd.DataFrame]) -> list[str]:
    """Liste dynamique des donateurs présents dans les données."""
    donors: set[str] = set()
    for df in sheets.values():
        if "Donor" in df.columns:
            donors.update(df["Donor"].dropna().unique().tolist())
    return sorted(donors)


def get_partners(sheets: dict[str, pd.DataFrame]) -> list[str]:
    """Liste dynamique des partenaires présents dans les données."""
    partners: set[str] = set()
    for df in sheets.values():
        if "Partner" in df.columns:
            partners.update(df["Partner"].dropna().unique().tolist())
    return sorted(partners)


def get_displacement_statuses(sheets: dict[str, pd.DataFrame]) -> list[str]:
    """Liste dynamique des statuts de déplacement (IDP, Réfugié, Retourné...)."""
    statuses: set[str] = set()
    for df in sheets.values():
        if "Displacement_Status" in df.columns:
            statuses.update(df["Displacement_Status"].dropna().unique().tolist())
    return sorted(statuses)


def compute_data_quality_report(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Construit un tableau de qualité des données (lignes, colonnes, valeurs
    manquantes, doublons) pour chaque feuille — utilisé en page Overview/Admin.
    """
    rows = []
    for name, df in sheets.items():
        rows.append(
            {
                "Feuille": name,
                "Lignes": len(df),
                "Colonnes": df.shape[1],
                "Valeurs manquantes": int(df.isna().sum().sum()),
                "Doublons": int(df.duplicated().sum()),
                "Colonnes GPS": "Oui" if {"GPS_Lat", "GPS_Lon"}.issubset(df.columns) else "Non",
            }
        )
    return pd.DataFrame(rows)


def province_name_mismatches(sheets: dict[str, pd.DataFrame], geojson_path: str = str(config.GEOJSON_PATH)) -> dict[str, list[str]]:
    """Compare les noms de provinces des données Excel à ceux du GeoJSON afin
    de signaler toute incohérence de nommage avant l'affichage cartographique.
    """
    gj = load_geojson(geojson_path)
    geo_names = {f["properties"]["name"] for f in gj["features"]}
    data_names = set(get_provinces(sheets))
    return {
        "provinces_sans_geometrie": sorted(data_names - geo_names),
        "regions_geojson_non_utilisees": sorted(geo_names - data_names),
    }
