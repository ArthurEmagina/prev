from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple, Any

import pandas as pd

from .tiered_columns import find_tier_columns


def _require_basic_columns(df: pd.DataFrame, mapping: Dict[str, str]) -> None:
	required = ["product_code"]
	missing = [logical for logical in required if mapping.get(logical) not in df.columns]
	if missing:
		raise ValueError(
			"Colonnes essentielles manquantes (vérifiez config.yaml): " + ", ".join(missing)
		)


def load_dataset(config: dict) -> Tuple[pd.DataFrame, Dict[str, str]]:
	workbook_path_str = config["excel"]["workbook_path"]
	# Normaliser le chemin
	if isinstance(workbook_path_str, str):
		workbook_path = Path(workbook_path_str)
	else:
		workbook_path = workbook_path_str
	
	# Résoudre le chemin absolu
	try:
		workbook_path = workbook_path.resolve()
	except Exception as e:
		raise FileNotFoundError(f"Impossible de résoudre le chemin: {workbook_path_str} - {e}")
	
	sheet_name = config["excel"]["sheet_name"]
	mapping: Dict[str, str] = config["excel"].get("columns", {})
	tiers_cfg: Dict[str, str] = config["excel"].get("tiers", {})

	if not workbook_path.exists():
		raise FileNotFoundError(f"Fichier introuvable: {workbook_path}")
	
	# Vérifier que c'est bien un fichier
	if not workbook_path.is_file():
		raise PermissionError(f"Le chemin spécifié n'est pas un fichier (c'est peut-être un dossier): {workbook_path}")

	# Vérifier les permissions de lecture
	import os
	if not os.access(workbook_path, os.R_OK):
		raise PermissionError(
			f"Pas de permission de lecture sur le fichier. "
			f"Assurez-vous que le fichier n'est pas ouvert dans Excel: {workbook_path}"
		)

	try:
		df = pd.read_excel(
			workbook_path,
			sheet_name=sheet_name,
			engine="openpyxl",
			dtype=str,
		)
	except PermissionError as e:
		raise PermissionError(
			f"Impossible d'accéder au fichier Excel (fichier verrouillé). "
			f"Assurez-vous que le fichier n'est pas ouvert dans Excel ou un autre programme: {workbook_path}"
		) from e
	except Exception as e:
		raise Exception(f"Erreur lors de la lecture du fichier Excel '{workbook_path}': {e}") from e
	df.columns = [str(c).strip() for c in df.columns]

	_require_basic_columns(df, mapping)

	# Build tier maps to be used by logic layer (we store them inside mapping)
	columns_list = list(df.columns)
	if tiers_cfg:
		prod_map = find_tier_columns(columns_list, tiers_cfg.get("production_unit_cost_pattern", ""))
		air_map = find_tier_columns(columns_list, tiers_cfg.get("air_transport_unit_cost_pattern", ""))
		sea_map = find_tier_columns(columns_list, tiers_cfg.get("sea_transport_unit_cost_pattern", ""))
		prod_time_map = find_tier_columns(columns_list, tiers_cfg.get("production_time_pattern", ""))
		mapping = {
			**mapping,
			"tiers_production": prod_map,
			"tiers_air_transport": air_map,
			"tiers_sea_transport": sea_map,
			"tiers_production_time": prod_time_map,
			"air_transport_time_column": tiers_cfg.get("air_transport_time_column", ""),
			"sea_transport_time_column": tiers_cfg.get("sea_transport_time_column", ""),
		}

	return df, mapping

