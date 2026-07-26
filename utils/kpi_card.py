"""
utils/kpi_card.py — Cartes KPI en HTML/CSS (icône colorée, valeur, delta),
et bandeau "hero" pour la page d'accueil — inspirés du dashboard SI Sudan.
"""

from __future__ import annotations

from utils import theme


def kpi_card(label: str, value: str, sub: str = "", color: str = "#3D6FE0", icon: str = "", delta: str | None = None) -> str:
    """Retourne le HTML d'une carte KPI. `delta` est une chaîne déjà formatée
    (ex. "+12 vs mois dernier") ; couleur du delta déduite du signe."""
    t = theme.get_active_theme()
    delta_html = ""
    if delta:
        is_negative = delta.strip().startswith("-")
        delta_color = t["danger"] if is_negative else t["success"]
        delta_html = f'<div class="im-kpi-delta" style="color:{delta_color};">{delta}</div>'
    return f"""
    <div class="im-kpi">
        <div class="im-kpi-icon" style="background:{color}22;color:{color};">{icon}</div>
        <div class="im-kpi-value">{value}</div>
        <div class="im-kpi-label">{label}{f' · {sub}' if sub else ''}</div>
        {delta_html}
    </div>
    """


def hero(tag: str, title: str, subtitle: str, bg_image: str | None = None) -> str:
    """Retourne le HTML du bandeau hero affiché en tête de la page d'accueil,
    avec une image de fond optionnelle (comme le dashboard SI Sudan)."""
    img_html = f"<img src='{bg_image}' alt='INTERSOS Tchad'>" if bg_image else ""
    return f"""
    <div class="im-hero">
        {img_html}
        <div class="im-hero-content">
            <span class="im-hero-tag">{tag}</span>
            <div class="im-hero-title">{title}</div>
            <p class="im-hero-sub">{subtitle}</p>
        </div>
        <div class="im-hero-bar"></div>
    </div>
    """


def image_slider(image_urls: list[str], repeat: int = 2) -> str:
    """Retourne le HTML d'un carrousel d'images à défilement horizontal
    infini (bande dupliquée pour une boucle continue sans à-coup), à
    l'identique du mécanisme du dashboard SI Sudan."""
    imgs_html = "".join(f"<img src='{u}' alt='INTERSOS Tchad'>" for u in image_urls * repeat)
    return f"""
    <div class="im-img-slider">
        <div class="im-img-track">{imgs_html}</div>
    </div>
    """
