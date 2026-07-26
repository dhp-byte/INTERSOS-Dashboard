"""
utils/trends.py — Comparaison de périodes (mois courant vs mois précédent)
pour afficher un delta sur les cartes KPI, à partir d'une colonne de date
réellement présente dans les données (aucune période n'est inventée).
"""

from __future__ import annotations

import pandas as pd


def month_over_month_delta(df: pd.DataFrame, date_col: str) -> str | None:
    """Compare le nombre de lignes du dernier mois disponible dans les
    données au mois précédent. Retourne None si moins de deux mois de
    données sont disponibles (rien à comparer)."""
    if date_col not in df.columns:
        return None
    dates = df[date_col].dropna()
    if dates.empty:
        return None
    months = dates.dt.to_period("M")
    counts = months.value_counts().sort_index()
    if len(counts) < 2:
        return None
    current, previous = counts.iloc[-1], counts.iloc[-2]
    diff = int(current - previous)
    sign = "+" if diff >= 0 else ""
    return f"{sign}{diff} vs mois précédent"
