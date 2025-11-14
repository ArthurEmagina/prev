from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import pandas as pd


@dataclass(frozen=True)
class TierDefinition:
	pattern: str  # regex with one capturing group for quantity

	def compile(self) -> re.Pattern[str]:
		return re.compile(self.pattern)


def find_tier_columns(columns: List[str], regex_pattern: str) -> Dict[int, str]:
	if not regex_pattern:
		return {}
	compiled = re.compile(regex_pattern)
	result: Dict[int, str] = {}
	for col in columns:
		col_str = str(col).strip()
		# Try both match and search for flexibility
		m = compiled.search(col_str)
		if not m:
			continue
		# Quantity is assumed to be in the last capturing group
		qty_str: Optional[str] = None
		if m.groups():
			# Get the last group (the quantity)
			qty_str = m.group(len(m.groups()))
		try:
			qty = int(float(str(qty_str).replace(",", "."))) if qty_str else None
		except Exception:  # noqa: BLE001
			qty = None
		if qty is None:
			continue
		result[qty] = col_str  # Use the trimmed column name
	return dict(sorted(result.items(), key=lambda kv: kv[0]))


def pick_tier_value(row: pd.Series, tiers: Dict[int, str], requested_qty: int, to_float) -> float:
	if not tiers:
		return 0.0
	# choose the largest tier <= requested_qty (tranche inférieure)
	sorted_qtys = sorted(tiers.keys())
	selected_tier = None
	for q in sorted_qtys:
		if q <= requested_qty:
			selected_tier = q
		else:
			break
	# If no tier <= requested_qty, use the smallest tier
	if selected_tier is None:
		selected_tier = sorted_qtys[0]
	return to_float(row.get(tiers[selected_tier], 0))

