"""
tests/test_data_loader.py — Tests unitaires sur le chargement et la
préparation des données réelles (data/INTERSOS_Chad_Program_Database.xlsx
et data/chad_admin1.geojson). Exécuter avec : pytest tests/ -v
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

import config
from utils import data_loader as dl
from utils import report_generator as rg


@pytest.fixture(scope="module")
def sheets():
    return dl.load_excel_sheets()


def test_all_expected_sheets_present(sheets):
    expected = {
        "Cover", "Beneficiary_Registration", "Protection", "Sante",
        "Nutrition", "WASH", "Securite_Alimentaire", "Abri_NFI", "Indicator_Tracker",
    }
    assert expected.issubset(sheets.keys())


def test_beneficiary_ids_are_unique(sheets):
    ben = sheets[config.SHEET_BENEFICIARIES]
    assert ben["Beneficiary_ID"].is_unique


def test_no_duplicate_rows(sheets):
    for name, df in sheets.items():
        assert df.duplicated().sum() == 0, f"Doublons détectés dans {name}"


def test_provinces_have_geojson_geometry(sheets):
    mismatches = dl.province_name_mismatches(sheets)
    assert mismatches["provinces_sans_geometrie"] == []


def test_sector_config_columns_exist(sheets):
    """Vérifie que chaque colonne cible/atteint/métrique déclarée dans
    config.SECTOR_CONFIG existe réellement dans la feuille correspondante."""
    for sheet_name, cfg in config.SECTOR_CONFIG.items():
        df = sheets[sheet_name]
        assert cfg["target_col"] in df.columns
        assert cfg["reached_col"] in df.columns
        for extra in cfg["extra_metrics"]:
            assert extra["col"] in df.columns


def test_get_provinces_returns_sorted_unique_list(sheets):
    provinces = dl.get_provinces(sheets)
    assert provinces == sorted(set(provinces))
    assert len(provinces) > 0


def test_geojson_loads(sheets):
    gj = dl.load_geojson()
    assert gj["type"] == "FeatureCollection"
    assert len(gj["features"]) > 0


def test_data_quality_report_shape(sheets):
    report = dl.compute_data_quality_report(sheets)
    assert set(report.columns) == {"Feuille", "Lignes", "Colonnes", "Valeurs manquantes", "Doublons", "Colonnes GPS"}
    assert len(report) == len(sheets)


def test_missing_excel_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        dl.load_excel_sheets(str(tmp_path / "does_not_exist.xlsx"))


def test_docx_report_generates_valid_bytes(sheets):
    cover = dl.get_cover_info(sheets)
    content = rg.build_docx_report(sheets, cover)
    assert isinstance(content, bytes)
    assert content[:2] == b"PK"  # signature ZIP (.docx est un zip)
    assert len(content) > 1000


def test_pdf_report_generates_valid_bytes(sheets):
    cover = dl.get_cover_info(sheets)
    content = rg.build_pdf_report(sheets, cover)
    assert isinstance(content, bytes)
    assert content[:5] == b"%PDF-"
    assert len(content) > 1000
