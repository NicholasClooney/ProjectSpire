#!/usr/bin/env python3
"""Parse decompiled STS2 card C# into a safer JSON shape.

This parser is intentionally conservative:
- It only emits facts that are explicit in the card source.
- It separates hover-tip references from actual card creation.
- It resolves descriptions from localization as a second pass.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from common import (
    DEFAULT_LANGUAGE,
    DECOMPILED_DIR,
    HoverTip,
    LAB_DIR,
    IMAGE_DIR,
    LOCALIZATION_DIR,
    ResolvedText,
    TextRun,
    class_name_to_id,
    dynamic_var_type_names,
    extract_tips,
    extract_vars,
    infer_version_from_path,
    latest_decompiled_version,
    list_decompiled_versions,
    load_localization,
    parse_version_key,
    render_text_runs,
    resolve_text,
    source_version,
    to_jsonable,
)


CARDS_SUBDIR = "MegaCrit.Sts2.Core.Models.Cards"
CARD_POOLS_SUBDIR = "MegaCrit.Sts2.Core.Models.CardPools"
CARD_ENTITIES_SUBDIR = "MegaCrit.Sts2.Core.Entities.Cards"
PARSER_VERSION = "0.2.4"
SCHEMA_VERSION = "0.2.4"

PACKED_CARD_PORTRAITS_DIR = IMAGE_DIR / "packed" / "card_portraits"

CARD_TYPE_NAME = {
    "Attack": "Attack",
    "Skill": "Skill",
    "Power": "Power",
    "Status": "Status",
    "Curse": "Curse",
}

CARD_RARITY_NAME = {
    "Basic": "Basic",
    "Common": "Common",
    "Uncommon": "Uncommon",
    "Rare": "Rare",
    "Special": "Special",
    "Token": "Token",
}

TARGET_TYPE_NAME = {
    "Self": "Self",
    "AnyEnemy": "AnyEnemy",
    "AllEnemies": "AllEnemies",
    "NoTarget": "NoTarget",
    "None": "None",
}


@dataclass
class CardRelation:
    kind: str
    target: str
    source: str


@dataclass
class AppliedPower:
    power: str
    target_expr: str
    amount_expr: str


@dataclass
class UpgradeDelta:
    var: str
    delta: int


@dataclass
class CostUpgradeDelta:
    target: str
    delta: int
    source: str


@dataclass
class KeywordUpgrade:
    operation: str
    keyword: str
    source: str


@dataclass
class EnergyCostInfo:
    kind: str
    value: int


@dataclass
class LocalizationInfo:
    table: str
    title_key: str
    description_key: str


@dataclass
class CardAsset:
    kind: str
    path: str
    source: str


@dataclass
class ResolvedKeyword:
    id: str
    placement: str
    title: str
    description: ResolvedText


@dataclass
class ResolvedCardState:
    title: str
    cost: int
    energy_cost: EnergyCostInfo
    description: ResolvedText
    keywords: list[ResolvedKeyword] = field(default_factory=list)
    changed: list[str] | None = None


@dataclass
class ResolvedCard:
    keyword_period: str
    base: ResolvedCardState
    upgraded: ResolvedCardState | None = None


@dataclass
class RawCardInfo:
    parser_version: str
    class_name: str
    file: str
    cost: int
    energy_cost: EnergyCostInfo
    type: str
    rarity: str
    target: str
    card_pool: str
    localization: LocalizationInfo
    vars: dict[str, int] = field(default_factory=dict)
    assets: list[CardAsset] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    upgrades: list[UpgradeDelta] = field(default_factory=list)
    cost_upgrades: list[CostUpgradeDelta] = field(default_factory=list)
    keyword_upgrades: list[KeywordUpgrade] = field(default_factory=list)
    tips: list[HoverTip] = field(default_factory=list)
    applies_powers: list[AppliedPower] = field(default_factory=list)
    relations: list[CardRelation] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class CardInfo:
    schema_version: str
    id: str
    raw: RawCardInfo
    resolved: ResolvedCard | dict[str, Any]


def default_localization_path(language: str) -> Path:
    return LOCALIZATION_DIR / language / "cards.json"


def default_keyword_localization_path(language: str) -> Path:
    return LOCALIZATION_DIR / language / "card_keywords.json"


def prompt_for_version(versions: list[str], default_version: str) -> str:
    print("Available decompiled versions:", file=sys.stderr)
    for index, version in enumerate(versions, start=1):
        default_marker = " (default)" if version == default_version else ""
        print(f"  {index}. {version}{default_marker}", file=sys.stderr)

    response = input(f"Choose a version [default: {default_version}]: ").strip()
    if not response:
        return default_version
    if response.isdigit():
        selected_index = int(response) - 1
        if 0 <= selected_index < len(versions):
            return versions[selected_index]
    if response in versions:
        return response
    raise ValueError(f"Unknown version selection: {response}")


def resolve_cards_dir(path_arg: str | None, version: str | None) -> tuple[Path, str | None]:
    if path_arg:
        path = Path(path_arg).resolve()
        inferred_version = infer_version_from_path(path)
        if path.is_dir():
            return path, inferred_version
        return path, inferred_version

    available_versions = list_decompiled_versions()
    selected_version = version
    if selected_version is None:
        latest = latest_decompiled_version()
        if sys.stdin.isatty():
            selected_version = prompt_for_version(available_versions, latest)
        else:
            selected_version = latest
    cards_dir = DECOMPILED_DIR / selected_version / CARDS_SUBDIR
    return cards_dir, selected_version


def default_output_dir(version: str | None) -> Path:
    if version:
        return LAB_DIR / "data" / version / "cards"
    return LAB_DIR / "data" / "cards"


def default_audit_output_dir(version: str | None, card_output_dir: Path) -> Path:
    if version:
        return LAB_DIR / "data" / version
    if card_output_dir.name == "cards":
        return card_output_dir.parent
    return card_output_dir


def load_card_pool_map(version: str | None) -> dict[str, str]:
    if version is None:
        return {}
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
def card_keyword_order(version: str) -> tuple[list[str], list[str], dict[str, str]]:
    keyword_dir = DECOMPILED_DIR / version / CARD_ENTITIES_SUBDIR
    enum_path = keyword_dir / "CardKeyword.cs"
    order_path = keyword_dir / "CardKeywordOrder.cs"
    if not enum_path.exists():
        raise FileNotFoundError(f"Missing CardKeyword source for {version}: {enum_path}")
    if not order_path.exists():
        raise FileNotFoundError(f"Missing CardKeywordOrder source for {version}: {order_path}")

    enum_content = enum_path.read_text(encoding="utf-8")
    order_content = order_path.read_text(encoding="utf-8")
    enum_match = re.search(r"public enum CardKeyword\s*\{(?P<body>.*?)\}", enum_content, re.DOTALL)
    if not enum_match:
        raise ValueError(f"Could not parse CardKeyword enum for {version}: {enum_path}")

    keyword_names = [
        line.strip().rstrip(",")
        for line in enum_match.group("body").splitlines()
        if line.strip() and not line.strip().startswith("//")
    ]

    def extract_order_array(name: str) -> list[str]:
        match = re.search(
            rf"{name}\s*=\s*new CardKeyword\[\d+\]\s*\{{(?P<body>.*?)\}};",
            order_content,
            re.DOTALL,
        )
        if not match:
            raise ValueError(f"Could not parse CardKeywordOrder.{name} for {version}: {order_path}")
        return re.findall(r"CardKeyword\.([A-Za-z0-9_]+)", match.group("body"))

    before = extract_order_array("beforeDescription")
    after = extract_order_array("afterDescription")
    before_set = set(before)
    after_set = set(after)
    overlap = sorted(before_set & after_set)
    if overlap:
        raise ValueError(f"Card keywords appear in both display placement arrays for {version}: {', '.join(overlap)}")

    displayed_keywords = [keyword for keyword in keyword_names if keyword != "None"]
    missing = sorted(keyword for keyword in displayed_keywords if keyword not in before_set and keyword not in after_set)
    if missing:
        raise ValueError(f"Card keywords are missing display placement for {version}: {', '.join(missing)}")

    placement = {keyword: "beforeDescription" for keyword in before}
    placement.update({keyword: "afterDescription" for keyword in after})
    return before, after, placement


def energy_cost_info(cost: int, costs_x: bool) -> EnergyCostInfo:
    return EnergyCostInfo(kind="x" if costs_x else "int", value=cost)


def extract_constructor_fields(content: str) -> tuple[int, str, str, str]:
    match = re.search(
        r":\s*base\(\s*(-?\d+)\s*,\s*CardType\.(\w+)\s*,\s*CardRarity\.(\w+)\s*,\s*TargetType\.(\w+)",
        content,
    )
    if not match:
        raise ValueError("Could not locate card base constructor")
    cost = int(match.group(1))
    card_type = CARD_TYPE_NAME.get(match.group(2), match.group(2))
    rarity = CARD_RARITY_NAME.get(match.group(3), match.group(3))
    target = TARGET_TYPE_NAME.get(match.group(4), match.group(4))
    return cost, card_type, rarity, target


def extract_costs_x(content: str) -> bool:
    return bool(re.search(r"HasEnergyCostX\s*=>\s*true", content))


def packed_portrait_path(pool: str, card_id: str, is_beta: bool) -> Path:
    parts = [pool]
    if is_beta:
        parts.append("beta")
    parts.append(f"{card_id.lower()}.webp")
    return PACKED_CARD_PORTRAITS_DIR.joinpath(*parts)


def extract_assets(card_id: str, pool: str | None) -> list[CardAsset]:
    if pool is None:
        return []

    assets: list[CardAsset] = []
    for kind, is_beta in (("portrait", False), ("beta_portrait", True)):
        path = packed_portrait_path(pool, card_id, is_beta)
        if path.exists():
            assets.append(
                CardAsset(
                    kind=kind,
                    path=str(path.relative_to(LAB_DIR.parent)),
                    source="Lab.resources.images.packed.card_portraits",
                )
            )
    return assets


def extract_keywords(content: str) -> list[str]:
    found: list[str] = []
    canonical_match = re.search(r"CanonicalKeywords\s*=>\s*(.*?);", content, re.DOTALL)
    if canonical_match:
        for keyword in re.findall(r"CardKeyword\.(\w+)", canonical_match.group(1)):
            found.append(keyword)

    for keyword, pattern in [
        ("Ethereal", r"IsEthereal\s*=>\s*true"),
        ("Innate", r"IsInnate\s*=>\s*true"),
        ("Retain", r"IsRetain(?:able)?\s*=>\s*true"),
        ("Unplayable", r"IsUnplayable\s*=>\s*true"),
    ]:
        if keyword not in found and re.search(pattern, content):
            found.append(keyword)
    return found


def extract_method_body(content: str, method_name: str) -> str:
    match = re.search(rf"\b{method_name}\s*\([^)]*\)\s*\{{", content)
    if not match:
        return ""

    body_start = match.end()
    depth = 1
    index = body_start
    while index < len(content):
        char = content[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return content[body_start:index]
        index += 1
    return ""


def extract_keyword_upgrades(content: str) -> list[KeywordUpgrade]:
    body = extract_method_body(content, "OnUpgrade")
    if not body:
        return []

    upgrades: list[KeywordUpgrade] = []
    for match in re.finditer(r"\b(AddKeyword|RemoveKeyword)\(\s*CardKeyword\.(\w+)\s*\)", body):
        operation = "add" if match.group(1) == "AddKeyword" else "remove"
        upgrades.append(KeywordUpgrade(operation=operation, keyword=match.group(2), source="OnUpgrade"))
    return upgrades


def apply_keyword_upgrades(keywords: list[str], keyword_upgrades: list[KeywordUpgrade]) -> list[str]:
    upgraded_keywords = list(keywords)
    for upgrade in keyword_upgrades:
        if upgrade.operation == "add" and upgrade.keyword not in upgraded_keywords:
            upgraded_keywords.append(upgrade.keyword)
        elif upgrade.operation == "remove" and upgrade.keyword in upgraded_keywords:
            upgraded_keywords.remove(upgrade.keyword)
    return upgraded_keywords


def extract_tags(content: str) -> list[str]:
    tags: list[str] = []
    for tag in ("Strike", "Defend", "Minion", "OstyAttack", "Shiv"):
        if re.search(rf"CardTag\.{tag}", content):
            tags.append(tag)
    return tags


def extract_upgrades(content: str, accessor_keys: dict[str, str] | None = None) -> list[UpgradeDelta]:
    upgrades: dict[str, int] = {}
    accessor_keys = accessor_keys or {}

    for match in re.finditer(r"(?<!\w)(\w+)\.UpgradeValueBy\((-?\d+)m\)", content):
        var_name = accessor_keys.get(match.group(1), match.group(1))
        upgrades[var_name] = int(match.group(2))

    for match in re.finditer(r'\["(\w+)"\]\.UpgradeValueBy\((-?\d+)m\)', content):
        upgrades.setdefault(match.group(1), int(match.group(2)))

    return [UpgradeDelta(var=var_name, delta=delta) for var_name, delta in sorted(upgrades.items())]


def extract_cost_upgrades(content: str) -> list[CostUpgradeDelta]:
    upgrades: list[CostUpgradeDelta] = []
    for match in re.finditer(r"base\.EnergyCost\.UpgradeBy\((-?\d+)\)", content):
        delta = int(match.group(1))
        if delta != 0:
            upgrades.append(
                CostUpgradeDelta(
                    target="cost",
                    delta=delta,
                    source="EnergyCost.UpgradeBy",
                )
            )
    return upgrades


def extract_applied_powers(content: str) -> list[AppliedPower]:
    applied: list[AppliedPower] = []
    for match in re.finditer(
        r"PowerCmd\.Apply<(\w+)>\(([^,]+),\s*([^,]+),\s*[^,]+,\s*this\)",
        content,
    ):
        power_name = match.group(1)
        applied.append(
            AppliedPower(
                power=power_name[:-5] if power_name.endswith("Power") else power_name,
                target_expr=match.group(2).strip(),
                amount_expr=match.group(3).strip(),
            )
        )
    return applied


def extract_relations(content: str) -> list[CardRelation]:
    relations: list[CardRelation] = []

    for match in re.finditer(r"CreateCard<(\w+)>", content):
        relations.append(CardRelation(kind="creates_card", target=class_name_to_id(match.group(1)), source="CreateCard"))

    for match in re.finditer(r"(\w+)\.CreateInHand\(", content):
        relations.append(CardRelation(kind="creates_card", target=class_name_to_id(match.group(1)), source="CreateInHand"))

    for match in re.finditer(r"AddToCombatAndPreview<(\w+)>", content):
        relations.append(CardRelation(kind="creates_card", target=class_name_to_id(match.group(1)), source="AddToCombatAndPreview"))

    return _dedupe_relations(relations)


def _dedupe_relations(relations: list[CardRelation]) -> list[CardRelation]:
    deduped: list[CardRelation] = []
    seen: set[tuple[str, str, str]] = set()
    for relation in relations:
        key = (relation.kind, relation.target, relation.source)
        if key not in seen:
            seen.add(key)
            deduped.append(relation)
    return deduped


def keyword_loc_key(keyword: str, suffix: str) -> str:
    return f"{re.sub(r'(?<!^)(?=[A-Z])', '_', keyword).upper()}.{suffix}"


def ordered_keywords(keywords: list[str], before_keywords: list[str], after_keywords: list[str]) -> list[str]:
    keyword_set = set(keywords)
    before_visible = [keyword for keyword in reversed(before_keywords) if keyword in keyword_set]
    after_visible = [keyword for keyword in after_keywords if keyword in keyword_set]
    return before_visible + after_visible


def resolve_keywords(
    keywords: list[str],
    keyword_localization: dict[str, str],
    before_keywords: list[str],
    after_keywords: list[str],
    keyword_placements: dict[str, str],
) -> list[ResolvedKeyword]:
    resolved: list[ResolvedKeyword] = []
    missing_keys: list[str] = []
    for keyword in ordered_keywords(keywords, before_keywords, after_keywords):
        title_key = keyword_loc_key(keyword, "title")
        description_key = keyword_loc_key(keyword, "description")
        for key in (title_key, description_key):
            if key not in keyword_localization:
                missing_keys.append(key)
        if missing_keys:
            continue
        resolved.append(
            ResolvedKeyword(
                id=keyword,
                placement=keyword_placements[keyword],
                title=keyword_localization[title_key],
                description=resolve_text(keyword_localization[description_key], {}, set(), upgraded=False),
            )
        )

    if missing_keys:
        raise ValueError(f"Missing required card keyword localization keys: {', '.join(sorted(set(missing_keys)))}")
    return resolved


def build_resolved_card(
    card_id: str,
    cost: int,
    costs_x: bool,
    card_type: str,
    target: str,
    vars_by_name: dict[str, int],
    upgrades: list[UpgradeDelta],
    cost_upgrades: list[CostUpgradeDelta],
    keywords: list[str],
    keyword_upgrades: list[KeywordUpgrade],
    localization: dict[str, str],
    keyword_localization: dict[str, str],
    keyword_version: str,
) -> ResolvedCard:
    title_key = f"{card_id}.title"
    description_key = f"{card_id}.description"
    missing_keys = [key for key in (title_key, description_key) if key not in localization]
    if "PERIOD" not in keyword_localization:
        missing_keys.append("card_keywords.PERIOD")
    if missing_keys:
        raise ValueError(f"Missing required localization keys for {card_id}: {', '.join(missing_keys)}")

    before_keywords, after_keywords, keyword_placements = card_keyword_order(keyword_version)
    base_keywords = resolve_keywords(keywords, keyword_localization, before_keywords, after_keywords, keyword_placements)
    base_display_vars: dict[str, Any] = {
        **vars_by_name,
        "CardType": card_type,
        "TargetType": target,
        "HasRider": False,
        "IsTargeting": False,
        "Sapping": False,
        "Choking": False,
        "Energized": False,
        "Wisdom": False,
        "Chaos": False,
        "Expertise": False,
        "Curious": False,
        "Improvement": False,
        "Violence": False,
    }
    base_description = resolve_text(localization[description_key], base_display_vars, set(), upgraded=False)
    base = ResolvedCardState(
        title=localization[title_key],
        cost=cost,
        energy_cost=energy_cost_info(cost, costs_x),
        description=base_description,
        keywords=base_keywords,
    )

    upgraded_vars = dict(vars_by_name)
    changed_vars: set[str] = set()
    for upgrade in upgrades:
        if upgrade.var in upgraded_vars:
            upgraded_vars[upgrade.var] += upgrade.delta
            changed_vars.add(upgrade.var)
            if upgrade.var == "CalculationBase":
                for var_name in upgraded_vars:
                    if var_name.startswith("Calculated"):
                        upgraded_vars[var_name] = upgraded_vars["CalculationBase"]
                        changed_vars.add(var_name)

    upgraded_cost = cost
    for cost_upgrade in cost_upgrades:
        if cost_upgrade.target == "cost":
            upgraded_cost = max(upgraded_cost + cost_upgrade.delta, 0)

    upgraded_display_vars: dict[str, Any] = {
        **upgraded_vars,
        "CardType": card_type,
        "TargetType": target,
        "HasRider": False,
        "IsTargeting": False,
        "Sapping": False,
        "Choking": False,
        "Energized": False,
        "Wisdom": False,
        "Chaos": False,
        "Expertise": False,
        "Curious": False,
        "Improvement": False,
        "Violence": False,
    }
    upgraded_description = resolve_text(localization[description_key], upgraded_display_vars, changed_vars, upgraded=True)
    upgraded_keywords = resolve_keywords(
        apply_keyword_upgrades(keywords, keyword_upgrades),
        keyword_localization,
        before_keywords,
        after_keywords,
        keyword_placements,
    )
    changed: list[str] = []
    if upgraded_cost != cost:
        changed.append("cost")
    if upgraded_description.plain != base_description.plain:
        changed.append("description")
    if [keyword.id for keyword in upgraded_keywords] != [keyword.id for keyword in base_keywords]:
        changed.append("keywords")
    upgraded_state = ResolvedCardState(
        title=f"{localization[title_key]}+",
        cost=upgraded_cost,
        energy_cost=energy_cost_info(upgraded_cost, costs_x),
        changed=changed,
        description=upgraded_description,
        keywords=upgraded_keywords,
    )
    return ResolvedCard(keyword_period=keyword_localization["PERIOD"], base=base, upgraded=upgraded_state)


def parse_card(
    filepath: Path,
    localization: dict[str, str] | None = None,
    keyword_localization: dict[str, str] | None = None,
    card_pools: dict[str, str] | None = None,
) -> CardInfo:
    content = filepath.read_text(encoding="utf-8")
    class_name = filepath.stem
    card_id = class_name_to_id(class_name)
    cost, card_type, rarity, target = extract_constructor_fields(content)
    costs_x = extract_costs_x(content)
    display_path = str(filepath.relative_to(LAB_DIR.parent))

    localization = localization or {}
    keyword_localization = keyword_localization or {}
    card_pools = card_pools or {}
    card_pool = card_pools.get(card_id)
    if card_pool is None:
        raise ValueError(f"Could not resolve card pool for {card_id}")
    title_key = f"{card_id}.title"
    description_key = f"{card_id}.description"
    version = source_version(filepath)
    vars_by_name = extract_vars(content, dynamic_var_type_names(version) if version else {})
    upgrades = extract_upgrades(content, dynamic_var_accessor_keys(version) if version else {})
    cost_upgrades = extract_cost_upgrades(content)
    keywords = extract_keywords(content)
    keyword_upgrades = extract_keyword_upgrades(content)

    notes: list[str] = []
    if localization and description_key not in localization:
        notes.append("Description is not present in the C# file; supply localization data to populate it.")

    resolved: ResolvedCard | dict[str, Any] = {}
    if localization:
        resolved = build_resolved_card(
            card_id,
            cost,
            costs_x,
            card_type,
            target,
            vars_by_name,
            upgrades,
            cost_upgrades,
            keywords,
            keyword_upgrades,
            localization,
            keyword_localization,
            version or latest_decompiled_version(),
        )

    return CardInfo(
        schema_version=SCHEMA_VERSION,
        id=card_id,
        raw=RawCardInfo(
            parser_version=PARSER_VERSION,
            class_name=class_name,
            file=display_path,
            cost=cost,
            energy_cost=energy_cost_info(cost, costs_x),
            type=card_type,
            rarity=rarity,
            target=target,
            card_pool=card_pool,
            localization=LocalizationInfo(
                table="cards",
                title_key=title_key,
                description_key=description_key,
            ),
            vars=vars_by_name,
            assets=extract_assets(card_id, card_pools.get(card_id)),
            keywords=keywords,
            tags=extract_tags(content),
            upgrades=upgrades,
            cost_upgrades=cost_upgrades,
            keyword_upgrades=keyword_upgrades,
            tips=extract_tips(content),
            applies_powers=extract_applied_powers(content),
            relations=extract_relations(content),
            notes=notes,
        ),
        resolved=resolved,
    )


def parse_many(
    card_dir: Path,
    localization: dict[str, str] | None = None,
    keyword_localization: dict[str, str] | None = None,
    card_pools: dict[str, str] | None = None,
) -> list[CardInfo]:
    return [parse_card(path, localization, keyword_localization, card_pools) for path in sorted(card_dir.glob("*.cs"))]


def write_card_output(card: CardInfo, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{card.id.lower()}.json"
    output_path.write_text(
        json.dumps(to_jsonable(card), indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def write_many_cards(cards: list[CardInfo], output_dir: Path) -> list[Path]:
    return [write_card_output(card, output_dir) for card in cards]


def unresolved_placeholder_log_path(output_dir: Path) -> Path:
    return output_dir / "unresolved_placeholders.csv"


def unresolved_placeholder_catalog_path(output_dir: Path) -> Path:
    return output_dir / "unresolved_placeholder_catalog.json"


def unresolved_placeholders_for_card(card: CardInfo) -> list[dict[str, str]]:
    if not isinstance(card.resolved, ResolvedCard):
        return []

    rows: list[dict[str, str]] = []
    states = [("base", card.resolved.base)]
    if card.resolved.upgraded is not None:
        states.append(("upgraded", card.resolved.upgraded))

    for state_name, state in states:
        for match in re.finditer(r"\{[^{}]+\}", state.description.plain):
            rows.append(
                {
                    "card_id": card.id,
                    "state": state_name,
                    "placeholder": match.group(0),
                    "resolved_text": state.description.plain,
                }
            )
    return rows


def unresolved_placeholder_catalog(rows: list[dict[str, str]]) -> dict[str, Any]:
    by_placeholder: dict[str, dict[str, Any]] = {}
    for row in rows:
        entry = by_placeholder.setdefault(
            row["placeholder"],
            {
                "placeholder": row["placeholder"],
                "count": 0,
                "cards": set(),
                "states": set(),
            },
        )
        entry["count"] += 1
        entry["cards"].add(row["card_id"])
        entry["states"].add(row["state"])

    placeholders = []
    for entry in by_placeholder.values():
        placeholders.append(
            {
                "placeholder": entry["placeholder"],
                "count": entry["count"],
                "cards": sorted(entry["cards"]),
                "states": sorted(entry["states"]),
            }
        )
    placeholders.sort(key=lambda entry: (-entry["count"], entry["placeholder"]))

    return {
        "generated_from": unresolved_placeholder_log_path(Path(".")).name,
        "total_occurrences": len(rows),
        "total_placeholders": len(placeholders),
        "placeholders": placeholders,
    }


def write_unresolved_placeholder_log(cards: list[CardInfo], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = unresolved_placeholder_log_path(output_dir)
    catalog_path = unresolved_placeholder_catalog_path(output_dir)
    rows = [row for card in cards for row in unresolved_placeholders_for_card(card)]
    with log_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["card_id", "state", "placeholder", "resolved_text"])
        writer.writeheader()
        writer.writerows(rows)
    catalog_path.write_text(
        json.dumps(unresolved_placeholder_catalog(rows), indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return log_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="Card .cs file or card directory")
    parser.add_argument("--version", help="Decompiler version under Lab/decompiled/, for example v0.103.2")
    parser.add_argument(
        "--language",
        default=DEFAULT_LANGUAGE,
        help=f"Localization language under Lab/resources/localization/ (default: {DEFAULT_LANGUAGE})",
    )
    parser.add_argument(
        "--localization",
        type=Path,
        help="JSON map of card localization keys to strings (default: Lab/resources/localization/<language>/cards.json)",
    )
    parser.add_argument(
        "--raw-only",
        action="store_true",
        help="Skip localization resolution and leave resolved empty",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for per-card JSON output",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing per-card files",
    )
    args = parser.parse_args()

    input_path, inferred_version = resolve_cards_dir(args.path, args.version)
    localization_path = args.localization or default_localization_path(args.language)
    localization = {} if args.raw_only else load_localization(localization_path)
    keyword_localization = {} if args.raw_only else load_localization(default_keyword_localization_path(args.language))
    card_pools = load_card_pool_map(args.version or inferred_version)
    output_dir = args.output_dir.resolve() if args.output_dir else default_output_dir(args.version or inferred_version)
    audit_output_dir = default_audit_output_dir(args.version or inferred_version, output_dir)

    if input_path.is_file():
        card = parse_card(input_path, localization, keyword_localization, card_pools)
        if args.stdout:
            print(json.dumps(to_jsonable(card), indent=2, sort_keys=False))
            return
        output_path = write_card_output(card, output_dir)
        write_unresolved_placeholder_log([card], audit_output_dir)
        print(output_path)
    else:
        started_at = time.perf_counter()
        cards = parse_many(input_path, localization, keyword_localization, card_pools)
        if args.stdout:
            print(json.dumps(to_jsonable(cards), indent=2, sort_keys=False))
            return
        paths = write_many_cards(cards, output_dir)
        unresolved_log_path = write_unresolved_placeholder_log(cards, audit_output_dir)
        elapsed_seconds = time.perf_counter() - started_at
        print(
            f"Wrote {len(paths)} card files to {output_dir} "
            f"in {elapsed_seconds:.3f}s; unresolved placeholder log: {unresolved_log_path}"
        )


if __name__ == "__main__":
    main()
