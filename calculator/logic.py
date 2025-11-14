from __future__ import annotations

import datetime as dt
from typing import Dict, Any

import pandas as pd

from .tiered_columns import pick_tier_value
import re


def _extract_number_token(value: Any) -> str | None:
	if value is None:
		return None
	if isinstance(value, (int, float)):
		return str(value)
	text = str(value)
	match = re.search(r"[-+]?\d+(?:[\.,]\d+)?", text)
	return match.group(0) if match else None


def _to_float(value: Any, default: float = 0.0) -> float:
	try:
		num = _extract_number_token(value)
		if num is None:
			return default
		return float(num.replace(",", "."))
	except Exception:  # noqa: BLE001
		return default


def _to_int(value: Any, default: int = 0) -> int:
	try:
		num = _extract_number_token(value)
		if num is None:
			return default
		return int(float(num.replace(",", ".")))
	except Exception:  # noqa: BLE001
		return default


def _ceil_to_lot(quantity: int, lot_size: int) -> int:
	if lot_size <= 1:
		return quantity
	return ((quantity + lot_size - 1) // lot_size) * lot_size


def _apply_pricing_overheads(amount: float, pricing_cfg: Dict[str, float]) -> float:
	handling_flat = float(pricing_cfg.get("handling_flat", 0) or 0)
	handling_percent = float(pricing_cfg.get("handling_percent", 0) or 0)
	total = amount + handling_flat
	total *= (1 + handling_percent / 100.0)
	return total


def _prepare_fields(row: pd.Series, mapping: Dict[str, str], requested_qty: int) -> Dict[str, Any]:
	f: Dict[str, Any] = {}
	# Tiered prices: prod + transport
	prod_tiers = mapping.get("tiers_production", {})
	air_tr_tiers = mapping.get("tiers_air_transport", {})
	sea_tr_tiers = mapping.get("tiers_sea_transport", {})

	prod_cost = pick_tier_value(row, prod_tiers, requested_qty, _to_float)
	air_tr_cost = pick_tier_value(row, air_tr_tiers, requested_qty, _to_float)
	sea_tr_cost = pick_tier_value(row, sea_tr_tiers, requested_qty, _to_float)

	# Missing transport is allowed (treated as 0)
	f["production_unit_cost"] = float(prod_cost)
	f["air_transport_unit_cost"] = float(air_tr_cost)
	f["sea_transport_unit_cost"] = float(sea_tr_cost)
	f["unit_price_air"] = float(prod_cost) + float(air_tr_cost)
	f["unit_price_sea"] = float(prod_cost) + float(sea_tr_cost)

	# MOQ, lot, currency
	f["moq"] = max(1, _to_int(row.get(mapping.get("moq", ""), 1)) or 1)
	f["lot_size"] = max(1, _to_int(row.get(mapping.get("lot_size", ""), 1)) or 1)
	f["currency"] = str(row.get(mapping.get("currency", ""), "")).strip() or "EUR"

	# Lead times: production time (tiered) + transport time (fixed column)
	prod_time_tiers = mapping.get("tiers_production_time", {})
	prod_time_weeks = pick_tier_value(row, prod_time_tiers, requested_qty, _to_int) if prod_time_tiers else 0
	air_tr_time_col = mapping.get("air_transport_time_column", "")
	sea_tr_time_col = mapping.get("sea_transport_time_column", "")
	
	# Read transport times from specific columns (no fallback)
	air_tr_time_weeks = 0
	if air_tr_time_col and air_tr_time_col in row.index:
		air_tr_time_weeks = _to_int(row.get(air_tr_time_col, 0))
	
	sea_tr_time_weeks = 0
	if sea_tr_time_col and sea_tr_time_col in row.index:
		sea_tr_time_weeks = _to_int(row.get(sea_tr_time_col, 0))
	
	# Total lead time = production time + transport time (all in weeks, convert to days)
	f["lead_time_air_days"] = (prod_time_weeks + air_tr_time_weeks) * 7
	f["lead_time_sea_days"] = (prod_time_weeks + sea_tr_time_weeks) * 7
	return f


def compute_offer(row: pd.Series, requested_qty: int, target_date: dt.date, mapping: Dict[str, str], config: Dict[str, Any]) -> Dict[str, Any]:
	fields = _prepare_fields(row, mapping, requested_qty)
	pricing_cfg = config.get("pricing", {})

	# Respect MOQ and lot size
	qty_after_moq = max(requested_qty, fields["moq"])
	qty_ordered = _ceil_to_lot(qty_after_moq, fields["lot_size"])

	# Costs per mode
	air_cost = _apply_pricing_overheads(qty_ordered * fields["unit_price_air"], pricing_cfg)
	sea_cost = _apply_pricing_overheads(qty_ordered * fields["unit_price_sea"], pricing_cfg)

	# Pre-overhead breakdown totals
	prod_total = qty_ordered * fields["production_unit_cost"]
	air_tr_total = qty_ordered * fields["air_transport_unit_cost"]
	sea_tr_total = qty_ordered * fields["sea_transport_unit_cost"]

	# Order-by dates
	air_order_by = target_date - dt.timedelta(days=fields["lead_time_air_days"])
	sea_order_by = target_date - dt.timedelta(days=fields["lead_time_sea_days"])

	return {
		"requested_qty": requested_qty,
		"qty_ordered": qty_ordered,
		"currency": fields["currency"],
		"air": {
			"unit_price": fields["unit_price_air"],
			"production_unit_cost": fields["production_unit_cost"],
			"transport_unit_cost": fields["air_transport_unit_cost"],
			"production_total_pre_overhead": prod_total,
			"transport_total_pre_overhead": air_tr_total,
			"lead_time_days": fields["lead_time_air_days"],
			"total_cost": air_cost,
			"order_by": air_order_by,
		},
		"sea": {
			"unit_price": fields["unit_price_sea"],
			"production_unit_cost": fields["production_unit_cost"],
			"transport_unit_cost": fields["sea_transport_unit_cost"],
			"production_total_pre_overhead": prod_total,
			"transport_total_pre_overhead": sea_tr_total,
			"lead_time_days": fields["lead_time_sea_days"],
			"total_cost": sea_cost,
			"order_by": sea_order_by,
		},
	}

