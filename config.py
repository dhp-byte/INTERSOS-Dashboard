"""
config.py — Configuration centrale du dashboard MEAL/IM INTERSOS Tchad.

Règle absolue du projet : ce module ne code JAMAIS en dur les secteurs, régions,
donateurs ou partenaires. Les seules constantes autorisées ici sont des chemins
de fichiers, des paramètres d'affichage et la charte graphique.
Toute donnée métier (secteurs, provinces, etc.) est dérivée dynamiquement des
fichiers de référence via utils/data_loader.py.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data"
EXPORTS_DIR: Path = BASE_DIR / "exports"
LOGS_DIR: Path = BASE_DIR / "logs"
ASSETS_DIR: Path = BASE_DIR / "assets"

EXCEL_PATH: Path = DATA_DIR / "INTERSOS_Chad_Program_Database.xlsx"
GEOJSON_PATH: Path = DATA_DIR / "chad_admin1.geojson"

for _d in (EXPORTS_DIR, LOGS_DIR, ASSETS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Feuilles Excel — noms de référence, ne jamais renommer (règle absolue)
# ---------------------------------------------------------------------------
SHEET_COVER = "Cover"
SHEET_BENEFICIARIES = "Beneficiary_Registration"
SHEET_INDICATORS = "Indicator_Tracker"

# Feuilles sectorielles d'activités (tout le reste, hors Cover/Bénéficiaires/Indicateurs)
SECTOR_SHEETS_EXCLUDED = {SHEET_COVER, SHEET_BENEFICIARIES, SHEET_INDICATORS}

# ---------------------------------------------------------------------------
# Identité visuelle — "Mission Control" (thème sombre) / "Aurora" (thème clair)
# Reprise du système graphique développé pour les dashboards MEAL INTERSOS/SI
# ---------------------------------------------------------------------------
THEME_MISSION_CONTROL = {
    "name": "Mission Control",
    "bg": "#0B1220",
    "bg_secondary": "#111A2E",
    "surface": "#16213A",
    "text": "#E8ECF4",
    "text_muted": "#8B95AB",
    "primary": "#3D6FE0",       # bleu INTERSOS (logo), éclairci pour contraste sur fond sombre
    "primary_dark": "#1B3A6B",
    "secondary": "#F4924A",     # orange, couleur secondaire d'accent
    "accent": "#F4C542",        # jaune alerte/achievement
    "success": "#33C481",
    "warning": "#F4A93B",
    "danger": "#E5484D",
    "border": "#233052",
}

THEME_AURORA = {
    "name": "Aurora",
    "bg": "#F7F8FB",
    "bg_secondary": "#FFFFFF",
    "surface": "#FFFFFF",
    "text": "#111A2E",
    "text_muted": "#5B6478",
    "primary": "#1B3A6B",       # bleu marine INTERSOS (logo), adapté fond clair
    "primary_dark": "#122647",
    "secondary": "#C97A16",
    "accent": "#C98A0F",
    "success": "#1F9D63",
    "warning": "#C97A16",
    "danger": "#C0353A",
    "border": "#E1E4EC",
}

# ---------------------------------------------------------------------------
# Couleurs par secteur, alignées sur les conventions de couleurs des clusters
# humanitaires (IASC) pour une lecture immédiate et cohérente dans les
# graphiques (Overview, pages sectorielles, cartographie).
# ---------------------------------------------------------------------------
SECTOR_COLORS = {
    "Protection": "#6C5CE7",             # indigo protection (distinct du bleu de marque)
    "Sante": "#E64980",                  # rose/rouge santé
    "Nutrition": "#F76707",              # orange nutrition
    "WASH": "#15AABF",                   # cyan eau/assainissement
    "Securite_Alimentaire": "#40C057",   # vert sécurité alimentaire
    "Abri_NFI": "#AE8C5A",               # brun/beige abris
}

# ---------------------------------------------------------------------------
# Repères officiels de la mission INTERSOS Tchad, tels que publiés sur
# https://www.intersos.org/en/what-we-do/chad/ (dernier rapport disponible).
# Utilisés uniquement à titre de contexte informatif (page Overview) ;
# n'alimentent jamais les calculs, qui restent basés à 100% sur le classeur
# Excel de référence.
# ---------------------------------------------------------------------------
ORG_CONTEXT = {
    "source_url": "https://www.intersos.org/en/what-we-do/chad/",
    "first_intervention": 2004,
    "people_reached": 626_000,
    "projects": 20,
    "budget_spent_eur": 13_308_521,
    "official_sectors": [
        "Protection",
        "Santé et Nutrition",
        "Sécurité alimentaire",
        "Eau, hygiène et assainissement",
        "Abris et sites",
    ],
}

APP_TITLE = "INTERSOS Tchad — Plateforme MEAL / IM"
APP_ICON = "🧭"

# ---------------------------------------------------------------------------
# Seuils d'alerte sur l'atteinte des indicateurs (Achievement_%)
# Ces seuils sont des paramètres de configuration de l'application (non issus
# des fichiers de référence) et peuvent être ajustés sans toucher aux données.
# ---------------------------------------------------------------------------
ACHIEVEMENT_THRESHOLDS = {
    "on_track_min": 90.0,   # >= 90% : en bonne voie
    "watch_min": 60.0,      # 60-90% : à surveiller
    # < 60% : en retard critique
}

# ---------------------------------------------------------------------------
# Comptes de démonstration (à remplacer par un backend d'authentification réel
# en production — cf. .streamlit/secrets.toml.example)
# ---------------------------------------------------------------------------
DEMO_USERS = {
    "im_manager": {"password": "intersos2026", "role": "IM Manager", "name": "Djaoyang Habekreo Pelandi"},
}

CACHE_TTL_SECONDS = 3600

# ---------------------------------------------------------------------------
# Images d'illustration (hero + carrousel de la page d'accueil), à contexte
# humanitaire générique. Photos libres de droits (licence Unsplash — usage
# commercial libre, sans attribution requise), hotlinkées depuis leur CDN
# d'origine, à l'identique de la pratique déjà en place dans les autres
# dashboards MEAL de l'utilisateur.
# ---------------------------------------------------------------------------
ILLUSTRATION_IMAGES = [
    "https://images.unsplash.com/photo-1727475807045-cac6e292e2b6?w=900&q=80",
    "https://images.unsplash.com/photo-1727473704300-1308ed6c1f78?w=900&q=80",
    "https://images.unsplash.com/photo-1624638764471-cffef5035746?w=900&q=80",
    "https://images.unsplash.com/photo-1637034132661-4f015591b84a?w=900&q=80",
    "https://images.unsplash.com/photo-1507427100689-2bf8574e32d4?w=900&q=80",
    "https://images.unsplash.com/photo-1727552889524-e1159fc95498?w=900&q=80",
    "https://images.unsplash.com/photo-1624638742121-32c6214bddd8?w=900&q=80",
    "https://images.unsplash.com/photo-1635931181100-1bd04e84c5c6?w=900&q=80",
]
HERO_BACKGROUND_IMAGE = "https://images.unsplash.com/photo-1727475807045-cac6e292e2b6?w=1400&q=80"

# Logo officiel INTERSOS (Wikimedia Commons — fichier libre de droits,
# hotlinké via le point d'accès stable Special:FilePath).
LOGO_URL = "https://commons.wikimedia.org/wiki/Special:FilePath/INTERSOS_Humanitarian_Aid_Organization_Logo.png"

# ---------------------------------------------------------------------------
# Configuration des pages sectorielles.
# Ce mapping ne fait que DÉCRIRE la structure déjà présente dans les colonnes
# du classeur Excel (quelle colonne est la cible, laquelle est l'atteint,
# quelles colonnes afficher en métriques complémentaires) : il ne fabrique
# aucune donnée et reste sans effet si une colonne venait à manquer (les
# pages vérifient la présence de chaque colonne avant affichage).
# ---------------------------------------------------------------------------
SECTOR_CONFIG = {
    "Protection": {
        "icon": "🛡️",
        "color": SECTOR_COLORS["Protection"],
        "target_col": "Target",
        "reached_col": "Reached",
        "breakdown_dims": ["Activity_Type", "Vulnerability_Type"],
        "extra_metrics": [],
    },
    "Sante": {
        "icon": "🩺",
        "color": SECTOR_COLORS["Sante"],
        "target_col": "Target_Consultations",
        "reached_col": "Reached_Consultations",
        "breakdown_dims": ["Activity_Type", "Health_Facility"],
        "extra_metrics": [{"col": "Quality_Score", "agg": "mean", "label": "Score qualité moyen"}],
    },
    "Nutrition": {
        "icon": "🍲",
        "color": SECTOR_COLORS["Nutrition"],
        "target_col": "Target_Screened",
        "reached_col": "Reached_Screened",
        "breakdown_dims": ["Activity_Type"],
        "extra_metrics": [
            {"col": "SAM_Cases", "agg": "sum", "label": "Cas MAS (SAM) dépistés"},
            {"col": "MAM_Cases", "agg": "sum", "label": "Cas MAM dépistés"},
            {"col": "Cure_Rate_SAM", "agg": "mean", "label": "Taux de guérison MAS"},
            {"col": "Cure_Rate_MAM", "agg": "mean", "label": "Taux de guérison MAM"},
        ],
    },
    "WASH": {
        "icon": "💧",
        "color": SECTOR_COLORS["WASH"],
        "target_col": "Target_Beneficiaries",
        "reached_col": "Reached_Beneficiaries",
        "breakdown_dims": ["Activity_Type", "Water_Source_Type"],
        "extra_metrics": [
            {"col": "Latrines_Built", "agg": "sum", "label": "Latrines construites"},
            {"col": "Soap_Distributed_kg", "agg": "sum", "label": "Savon distribué (kg)"},
        ],
    },
    "Securite_Alimentaire": {
        "icon": "🌾",
        "color": SECTOR_COLORS["Securite_Alimentaire"],
        "target_col": "Target_Households",
        "reached_col": "Reached_Households",
        "breakdown_dims": ["Activity_Type", "IPC_Phase"],
        "extra_metrics": [{"col": "Reached_Individuals", "agg": "sum", "label": "Individus atteints"}],
    },
    "Abri_NFI": {
        "icon": "🏠",
        "color": SECTOR_COLORS["Abri_NFI"],
        "target_col": "Target_Households",
        "reached_col": "Reached_Households",
        "breakdown_dims": ["Activity_Type", "Shelter_Type"],
        "extra_metrics": [
            {"col": "NFI_Kits_Distributed", "agg": "sum", "label": "Kits NFI distribués"},
            {"col": "Mosquito_Nets", "agg": "sum", "label": "Moustiquaires distribuées"},
        ],
    },
}
