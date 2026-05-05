#!/usr/bin/env python3
"""Audit generated card JSON against decompiled card source.

This script is intentionally separate from the exporter. It scans source for
card facts the parser should represent, compares them to generated JSON, and
prints suspicious source patterns that may deserve parser support.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
LAB_DIR = SCRIPT_PATH.parent.parent
DECOMPILED_DIR = LAB_DIR / "decompiled"
CARDS_SUBDIR = "MegaCrit.Sts2.Core.Models.Cards"
CARD_POOLS_SUBDIR = "MegaCrit.Sts2.Core.Models.CardPools"
DATA_DIR = LAB_DIR / "data"
LOCALIZATION_DIR = LAB_DIR / "resources" / "localization"
DEFAULT_LANGUAGE = "eng"


@dataclass(frozen=True)
class Finding:
    level: str
    card_id: str
    message: str

    def format(self) -> str:
        return f"{self.level}: {self.card_id}: {self.message}"


def class_name_to_id(class_name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).upper()


def parse_version_key(name: str) -> tuple[int, ...]:
    if not name.startswith("v"):
        return (-1,)
    parts = re.findall(r"\d+", name[1:])
    if not parts:
        return (-1,)
    return tuple(int(part) for part in parts)


def latest_decompiled_version() -> str:
    versions = [path.name for path in DECOMPILED_DIR.iterdir() if path.is_dir() and path.name.startswith("v")]
    if not versions:
        raise ValueError(f"No decompiled versions found under {DECOMPILED_DIR}")
    return sorted(versions, key=parse_version_key)[-1]


@lru_cache(maxsize=None)
def dynamic_var_accessor_keys(version: str) -> dict[str, str]:
    dynamic_var_set = DECOMPILED_DIR / version / "MegaCrit.Sts2.Core.Localization.DynamicVars" / "DynamicVarSet.cs"
    if not dynamic_var_set.exists():
        raise FileNotFoundError(f"Missing DynamicVarSet source for {version}: {dynamic_var_set}")

    content = dynamic_var_set.read_text(encoding="utf-8")
    return {
        match.group(1): match.group(2)
        for match in re.finditer(r"public [^;\n]+? (\w+) => [^;\n]*_vars\[\s*\"(\w+)\"\s*\]", content)
    }


@lru_cache(maxsize=None)
def dynamic_var_type_names(version: str) -> dict[str, str]:
    dynamic_vars_dir = DECOMPILED_DIR / version / "MegaCrit.Sts2.Core.Localization.DynamicVars"
    if not dynamic_vars_dir.exists():
        raise FileNotFoundError(f"Missing DynamicVars source directory for {version}: {dynamic_vars_dir}")

    type_names: dict[str, str] = {}
    for path in sorted(dynamic_vars_dir.glob("*Var.cs")):
        content = path.read_text(encoding="utf-8")
        class_match = re.search(r"public class (\w+Var)(?:<[^>]+>)?\s*:", content)
        if not class_match:
            continue

        default_name_match = re.search(r'public const string defaultName = "(\w+)"', content)
        base_name_match = re.search(r':\s*(?:base|this)\("(\w+)"[,)]', content)
        var_name_match = default_name_match or base_name_match
        if var_name_match:
            type_names[class_match.group(1)] = var_name_match.group(1)

    if not type_names:
        raise ValueError(f"No DynamicVar type names found under {dynamic_vars_dir}")
    return type_names


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_card_pool_map(version: str) -> dict[str, str]:
    pool_dir = DECOMPILED_DIR / version / CARD_POOLS_SUBDIR
    if not pool_dir.exists():
        raise FileNotFoundError(f"Missing card pool source directory for {version}: {pool_dir}")

    card_pools: dict[str, str] = {}
    for path in sorted(pool_dir.glob("*CardPool.cs")):
        content = path.read_text(encoding="utf-8")
        title_match = re.search(r'public override string Title => "([^"]+)"', content)
        if not title_match:
            continue
        pool_title = title_match.group(1)
        for card_match in re.finditer(r"ModelDb\.Card<(\w+)>\(\)", content):
            card_pools[class_name_to_id(card_match.group(1))] = pool_title
    return card_pools


def extract_constructor_cost(content: str) -> int:
    match = re.search(r":\s*base\(\s*(-?\d+)\s*,", content)
    if not match:
        raise ValueError("Could not locate card base constructor cost")
    return int(match.group(1))


def extract_costs_x(content: str) -> bool:
    return bool(re.search(r"HasEnergyCostX\s*=>\s*true", content))


def extract_source_vars(content: str, type_names: dict[str, str]) -> dict[str, int]:
    vars_found: dict[str, int] = {}
    for match in re.finditer(
        r'new (?P<type>\w+Var)(?:<(?P<generic>\w+)>)?\(\s*(?:"(?P<name>\w+)"\s*,\s*)?(?P<value>-?\d+)(?:m)?',
        content,
    ):
        var_type = match.group("type")
        var_name = match.group("name") or (match.group("generic") if var_type == "PowerVar" else type_names.get(var_type))
        if var_name:
            vars_found[var_name] = int(match.group("value"))

    return vars_found


def extract_source_upgrades(content: str, accessor_keys: dict[str, str]) -> list[dict[str, Any]]:
    upgrades: dict[str, int] = {}
    for match in re.finditer(r"(?<!\w)(\w+)\.UpgradeValueBy\((-?\d+)m\)", content):
        var_name = accessor_keys.get(match.group(1), match.group(1))
        upgrades[var_name] = int(match.group(2))
    for match in re.finditer(r'\["(\w+)"\]\.UpgradeValueBy\((-?\d+)m\)', content):
        upgrades.setdefault(match.group(1), int(match.group(2)))
    return [{"var": var_name, "delta": delta} for var_name, delta in sorted(upgrades.items())]


def extract_source_cost_upgrades(content: str) -> list[dict[str, Any]]:
    return [
        {"target": "cost", "delta": int(match.group(1)), "source": "EnergyCost.UpgradeBy"}
        for match in re.finditer(r"base\.EnergyCost\.UpgradeBy\((-?\d+)\)", content)
        if int(match.group(1)) != 0
    ]


def extract_source_tips(content: str) -> list[dict[str, str]]:
    tips: list[dict[str, str]] = []
    for match in re.finditer(r"HoverTipFactory\.Static\(StaticHoverTip\.(\w+)\)", content):
        tips.append({"kind": "hover_tip_static", "target": match.group(1), "source": "HoverTipFactory.Static"})
    for match in re.finditer(r"HoverTipFactory\.FromCard(?:WithCardHoverTips)?<(\w+)>", content):
        tips.append({"kind": "hover_tip_card", "target": class_name_to_id(match.group(1)), "source": "HoverTipFactory.FromCard"})
    for match in re.finditer(r"HoverTipFactory\.FromPower<(\w+)>", content):
        tips.append({"kind": "hover_tip_power", "target": match.group(1), "source": "HoverTipFactory.FromPower"})
    for match in re.finditer(r"HoverTipFactory\.FromOrb<(\w+)>", content):
        tips.append({"kind": "hover_tip_orb", "target": match.group(1), "source": "HoverTipFactory.FromOrb"})
    return dedupe_dicts(tips)


def extract_source_relations(content: str) -> list[dict[str, str]]:
    relations: list[dict[str, str]] = []
    for match in re.finditer(r"CreateCard<(\w+)>", content):
        relations.append({"kind": "creates_card", "target": class_name_to_id(match.group(1)), "source": "CreateCard"})
    for match in re.finditer(r"(\w+)\.CreateInHand\(", content):
        relations.append({"kind": "creates_card", "target": class_name_to_id(match.group(1)), "source": "CreateInHand"})
    for match in re.finditer(r"AddToCombatAndPreview<(\w+)>", content):
        relations.append({"kind": "creates_card", "target": class_name_to_id(match.group(1)), "source": "AddToCombatAndPreview"})
    return dedupe_dicts(relations)


def dedupe_dicts(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[tuple[str, Any], ...]] = set()
    for item in items:
        key = tuple(sorted(item.items()))
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped


def normalize_dict_list(items: list[dict[str, Any]]) -> set[tuple[tuple[str, Any], ...]]:
    return {tuple(sorted(item.items())) for item in items}


def compare_dicts(card_id: str, label: str, source_value: dict[str, Any], json_value: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    for key, expected_value in sorted(source_value.items()):
        actual_value = json_value.get(key)
        if actual_value != expected_value:
            findings.append(Finding("ERROR", card_id, f"{label}.{key} expected {expected_value!r}, found {actual_value!r}"))
    extra_keys = sorted(set(json_value) - set(source_value))
    for key in extra_keys:
        findings.append(Finding("WARN", card_id, f"{label}.{key} appears in JSON but was not detected in source"))
    return findings


def compare_list(card_id: str, label: str, source_items: list[dict[str, Any]], json_items: list[dict[str, Any]]) -> list[Finding]:
    findings: list[Finding] = []
    source_set = normalize_dict_list(source_items)
    json_set = normalize_dict_list(json_items)
    for missing in sorted(source_set - json_set):
        findings.append(Finding("ERROR", card_id, f"missing {label} {dict(missing)!r}"))
    for extra in sorted(json_set - source_set):
        findings.append(Finding("WARN", card_id, f"extra {label} {dict(extra)!r}"))
    return findings


def extract_placeholders(markup: str) -> set[str]:
    placeholders: set[str] = set()
    depth = 0
    start: int | None = None
    for index, char in enumerate(markup):
        if char == "{":
            if depth == 0:
                start = index + 1
            depth += 1
        elif char == "}" and depth > 0:
            depth -= 1
            if depth == 0 and start is not None:
                placeholders.add(markup[start:index])
    return placeholders


def suspicious_source_patterns(
    card_id: str,
    content: str,
    raw_vars: dict[str, Any],
    localization_text: str | None,
    include_dynamic_var_warnings: bool,
    include_localization_placeholder_warnings: bool,
) -> list[Finding]:
    findings: list[Finding] = []

    for match in re.finditer(r"base\.EnergyCost\.(\w+)\(", content):
        method = match.group(1)
        if method not in {"UpgradeBy", "SetThisCombat", "SetThisTurnOrUntilPlayed", "AddThisTurn", "AddThisCombat"}:
            findings.append(Finding("WARN", card_id, f"unsupported EnergyCost method base.EnergyCost.{method}()"))

    raw_var_names = set(raw_vars)
    if include_dynamic_var_warnings:
        for match in re.finditer(r"base\.DynamicVars(?:\.(\w+)|\[\s*\"(\w+)\"\s*\])", content):
            name = match.group(1) or match.group(2)
            if name and name not in raw_var_names and name not in {"Keys", "Values"}:
                findings.append(Finding("WARN", card_id, f"DynamicVars access {name!r} is not in raw.vars"))

    for match in re.finditer(r"HoverTipFactory\.(\w+)", content):
        method = match.group(1)
        if method not in {"Static", "FromCard", "FromCardWithCardHoverTips", "FromPower", "FromOrb"}:
            findings.append(Finding("WARN", card_id, f"unsupported HoverTipFactory.{method}"))

    if include_localization_placeholder_warnings and localization_text is not None:
        known_non_var_placeholders = {"IfUpgraded", "InCombat", "energyPrefix", "singleStarIcon"}
        for placeholder in sorted(extract_placeholders(localization_text)):
            name = placeholder.split(":", 1)[0]
            if name not in raw_var_names and name not in known_non_var_placeholders:
                findings.append(Finding("WARN", card_id, f"localization placeholder {name!r} is not in raw.vars"))

    return findings


def audit_card(
    source_path: Path,
    data_dir: Path,
    localization: dict[str, str],
    type_names: dict[str, str],
    accessor_keys: dict[str, str],
    card_pools: dict[str, str],
    include_dynamic_var_warnings: bool,
    include_localization_placeholder_warnings: bool,
) -> list[Finding]:
    content = source_path.read_text(encoding="utf-8")
    card_id = class_name_to_id(source_path.stem)
    data_path = data_dir / f"{card_id.lower()}.json"
    if not data_path.exists():
        return [Finding("ERROR", card_id, f"missing generated JSON {data_path}")]

    card_json = load_json(data_path)
    raw = card_json.get("raw", {})
    findings: list[Finding] = []

    if card_json.get("id") != card_id:
        findings.append(Finding("ERROR", card_id, f"id expected {card_id!r}, found {card_json.get('id')!r}"))

    cost = extract_constructor_cost(content)
    costs_x = extract_costs_x(content)
    expected_energy_cost = {"kind": "x" if costs_x else "int", "value": cost}
    expected_card_pool = card_pools.get(card_id)
    if expected_card_pool is None:
        findings.append(Finding("ERROR", card_id, "missing source card pool"))
    elif raw.get("card_pool") != expected_card_pool:
        findings.append(Finding("ERROR", card_id, f"raw.card_pool expected {expected_card_pool!r}, found {raw.get('card_pool')!r}"))
    if raw.get("energy_cost") != expected_energy_cost:
        findings.append(Finding("ERROR", card_id, f"raw.energy_cost expected {expected_energy_cost!r}, found {raw.get('energy_cost')!r}"))

    findings.extend(compare_dicts(card_id, "raw.vars", extract_source_vars(content, type_names), raw.get("vars", {})))
    findings.extend(compare_list(card_id, "raw.upgrades", extract_source_upgrades(content, accessor_keys), raw.get("upgrades", [])))
    findings.extend(compare_list(card_id, "raw.cost_upgrades", extract_source_cost_upgrades(content), raw.get("cost_upgrades", [])))
    findings.extend(compare_list(card_id, "raw.tips", extract_source_tips(content), raw.get("tips", [])))
    findings.extend(compare_list(card_id, "raw.relations", extract_source_relations(content), raw.get("relations", [])))

    localization_text = localization.get(f"{card_id}.description")
    findings.extend(
        suspicious_source_patterns(
            card_id,
            content,
            raw.get("vars", {}),
            localization_text,
            include_dynamic_var_warnings,
            include_localization_placeholder_warnings,
        )
    )
    return dedupe_findings(findings)


def dedupe_findings(findings: list[Finding]) -> list[Finding]:
    deduped: list[Finding] = []
    seen: set[tuple[str, str, str]] = set()
    for finding in findings:
        key = (finding.level, finding.card_id, finding.message)
        if key not in seen:
            seen.add(key)
            deduped.append(finding)
    return deduped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default=latest_decompiled_version(), help="Decompiler/data version to audit")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE, help=f"Localization language to inspect (default: {DEFAULT_LANGUAGE})")
    parser.add_argument("--warnings-as-errors", action="store_true", help="Exit non-zero when warnings are present")
    parser.add_argument(
        "--include-dynamic-var-warnings",
        action="store_true",
        help="Warn when source DynamicVars accesses are not present in raw.vars",
    )
    parser.add_argument(
        "--include-localization-placeholder-warnings",
        action="store_true",
        help="Warn when localization placeholders are not present in raw.vars",
    )
    args = parser.parse_args()

    cards_dir = DECOMPILED_DIR / args.version / CARDS_SUBDIR
    data_dir = DATA_DIR / args.version / "cards"
    localization_path = LOCALIZATION_DIR / args.language / "cards.json"
    localization = load_json(localization_path) if localization_path.exists() else {}
    type_names = dynamic_var_type_names(args.version)
    accessor_keys = dynamic_var_accessor_keys(args.version)
    card_pools = load_card_pool_map(args.version)

    findings: list[Finding] = []
    for source_path in sorted(cards_dir.glob("*.cs")):
        findings.extend(
            audit_card(
                source_path,
                data_dir,
                localization,
                type_names,
                accessor_keys,
                card_pools,
                args.include_dynamic_var_warnings,
                args.include_localization_placeholder_warnings,
            )
        )
    findings = dedupe_findings(findings)

    errors = [finding for finding in findings if finding.level == "ERROR"]
    warnings = [finding for finding in findings if finding.level == "WARN"]

    for finding in errors + warnings:
        print(finding.format())

    print(f"Audited {len(list(cards_dir.glob('*.cs')))} cards: {len(errors)} errors, {len(warnings)} warnings")

    if errors or (args.warnings_as_errors and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
