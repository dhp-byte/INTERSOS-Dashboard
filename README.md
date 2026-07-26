# INTERSOS Tchad — Plateforme MEAL / Information Management

Application Streamlit de suivi MEAL (Monitoring, Evaluation, Accountability & Learning)
et de gestion de l'information pour la mission INTERSOS au Tchad : cartographie
opérationnelle, suivi sectoriel, registre des bénéficiaires, moteur d'alertes et
génération de rapports Word/PDF — piloté à 100% par les données réelles du classeur
de référence.

## Démarrage rapide

```bash
pip install -r requirements.txt
streamlit run app.py
```

Identifiants de démonstration : `im_manager` / `intersos2026`

## Avec Docker

```bash
docker build -t intersos-meal .
docker run -p 8501:8501 intersos-meal
```

## Architecture

```
app.py                      Point d'entrée : login + page Overview
config.py                   Configuration centrale (thèmes, seuils, mapping sectoriel)
utils/
  data_loader.py            Chargement en cache du classeur Excel et du GeoJSON,
                             dérivation dynamique des secteurs/provinces/donateurs
  sector_view.py             Moteur générique de rendu des pages sectorielles
  theme.py                   Thèmes "Mission Control" (sombre) / "Aurora" (clair)
  report_generator.py         Génération de rapports Word (.docx) et PDF
pages/
  2_🗺️_Cartographie.py        Choroplèthe Folium + clusters de bénéficiaires
  3 à 8 (secteurs)            Protection, Santé, Nutrition, WASH, Sécurité
                               Alimentaire, Abri/NFI
  9_👥_Beneficiaires.py         Registre individuel des bénéficiaires
  10_📄_Rapports.py             Génération de rapports Word/PDF à la demande
  11_🚨_Alertes.py              Moteur d'alertes multi-secteurs
data/                        Classeur Excel de référence + GeoJSON admin1
tests/                       Suite de tests pytest (11 tests)
```

## Principe fondamental : 100% piloté par les données

Aucune valeur métier (secteur, province, donateur, partenaire, statut de
déplacement...) n'est codée en dur dans l'application. Tout est dérivé
dynamiquement du classeur `data/INTERSOS_Chad_Program_Database.xlsx` et du
fichier `data/chad_admin1.geojson` au chargement (`utils/data_loader.py`).
Le fichier `config.py` ne contient que des paramètres d'affichage
(thèmes, seuils d'alerte, icônes/couleurs par secteur) — jamais de données.

## Tests

```bash
pip install pytest
pytest tests/ -v
```

11 tests couvrent : présence des feuilles attendues, unicité des identifiants
bénéficiaires, absence de doublons, cohérence des noms de provinces avec le
GeoJSON, validité des colonnes déclarées dans `SECTOR_CONFIG`, et génération
effective de rapports Word/PDF.

## Qualité des données

Un contrôle qualité automatique (lignes, colonnes, valeurs manquantes,
doublons, cohérence géographique) est visible dans la page Overview et
inclus dans les rapports générés.

## Auteur

Djaoyang Habekreo Pelandi — Ingénieur Statisticien Économiste (ISE), MEAL / IM
