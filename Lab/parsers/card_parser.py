#!/usr/bin/env python3
"""Parse decompiled STS2 card C# into a safer JSON shape.

This parser is intentionally conservative:
- It only emits facts that are explicit in the card source.
- It separates hover-tip references from actual card creation.
- It resolves descriptions from localization as a second pass.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field, fields, is_dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
LAB_DIR = SCRIPT_PATH.parent.parent
DECOMPILED_DIR = LAB_DIR / "decompiled"
CARDS_SUBDIR = "MegaCrit.Sts2.Core.Models.Cards"
PARSER_VERSION = "0.2.2"
SCHEMA_VERSION = "0.2.2"
DEFAULT_LANGUAGE = "eng"
RESOURCES_DIR = LAB_DIR / "resources"
LOCALIZATION_DIR = RESOURCES_DIR / "localization"
IMAGE_DIR = RESOURCES_DIR / "images"
PACKED_CARD_PORTRAITS_DIR = IMAGE_DIR / "packed" / "card_portraits"
CARD_POOLS_SUBDIR = "MegaCrit.Sts2.Core.Models.CardPools"

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
class TextRun:
    text: str
    source_var: str | None = None
    style: str | None = None


@dataclass
class ResolvedText:
    plain: str
    runs: list[TextRun]


@dataclass
class ResolvedCardState:
    title: str
    cost: int
    description: ResolvedText
    changed: list[str] | None = None


@dataclass
class ResolvedCard:
    base: ResolvedCardState
    upgraded: ResolvedCardState | None = None


@dataclass
class RawCardInfo:
    parser_version: str
    class_name: str
    file: str
    cost: int
    type: str
    rarity: str
    target: str
    localization: LocalizationInfo
    vars: dict[str, int] = field(default_factory=dict)
    assets: list[CardAsset] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    upgrades: list[UpgradeDelta] = field(default_factory=list)
    cost_upgrades: list[CostUpgradeDelta] = field(default_factory=list)
    tips: list[CardRelation] = field(default_factory=list)
    applies_powers: list[AppliedPower] = field(default_factory=list)
    relations: list[CardRelation] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class CardInfo:
    schema_version: str
    id: str
    raw: RawCardInfo
    resolved: ResolvedCard | dict[str, Any]


def class_name_to_id(class_name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).upper()


def default_localization_path(language: str) -> Path:
    return LOCALIZATION_DIR / language / "cards.json"


def load_localization(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_version_key(name: str) -> tuple[int, ...]:
    if not name.startswith("v"):
        return (-1,)
    parts = re.findall(r"\d+", name[1:])
    if not parts:
        return (-1,)
    return tuple(int(part) for part in parts)


def list_decompiled_versions() -> list[str]:
    if not DECOMPILED_DIR.exists():
        return []
    versions = [path.name for path in DECOMPILED_DIR.iterdir() if path.is_dir() and path.name.startswith("v")]
    return sorted(versions, key=parse_version_key)


def latest_decompiled_version() -> str:
    versions = list_decompiled_versions()
    if not versions:
        raise ValueError(f"No decompiled versions found under {DECOMPILED_DIR}")
    return versions[-1]


def source_version(filepath: Path) -> str | None:
    try:
        relative = filepath.resolve().relative_to(DECOMPILED_DIR.resolve())
    except ValueError:
        return None
    return relative.parts[0] if relative.parts else None


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


def infer_version_from_path(path: Path) -> str | None:
    parts = path.parts
    for index, part in enumerate(parts):
        if part == "decompiled" and index + 1 < len(parts):
            candidate = parts[index + 1]
            if candidate.startswith("v"):
                return candidate
    return None


def default_output_dir(version: str | None) -> Path:
    if version:
        return LAB_DIR / "data" / version / "cards"
    return LAB_DIR / "data" / "cards"


def load_card_pool_map(version: str | None) -> dict[str, str]:
    if version is None:
        return {}
    pool_dir = DECOMPILED_DIR / version / CARD_POOLS_SUBDIR
    if not pool_dir.exists():
        return {}

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


def extract_vars(content: str, type_names: dict[str, str] | None = None) -> dict[str, int]:
    vars_found: dict[str, int] = {}
    type_names = type_names or {}

    for match in re.finditer(
        r'new (?P<type>\w+Var)(?:<(?P<generic>\w+)>)?\(\s*(?:"(?P<name>\w+)"\s*,\s*)?(?P<value>-?\d+)(?:m)?',
        content,
    ):
        var_type = match.group("type")
        var_name = match.group("name") or (match.group("generic") if var_type == "PowerVar" else type_names.get(var_type))
        if var_name:
            vars_found[var_name] = int(match.group("value"))

    return vars_found


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
    keyword_names = [
        "Exhaust",
        "Innate",
        "Ethereal",
        "Retain",
        "Unplayable",
        "Sly",
        "Eternal",
    ]
    for keyword in keyword_names:
        if re.search(rf"CardKeyword\.{keyword}", content):
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


def extract_tips(content: str) -> list[CardRelation]:
    tips: list[CardRelation] = []

    for match in re.finditer(r"HoverTipFactory\.Static\(StaticHoverTip\.(\w+)\)", content):
        tips.append(CardRelation(kind="hover_tip_static", target=match.group(1), source="HoverTipFactory.Static"))

    for match in re.finditer(r"HoverTipFactory\.FromCard(?:WithCardHoverTips)?<(\w+)>", content):
        tips.append(CardRelation(kind="hover_tip_card", target=class_name_to_id(match.group(1)), source="HoverTipFactory.FromCard"))

    for match in re.finditer(r"HoverTipFactory\.FromPower<(\w+)>", content):
        tips.append(CardRelation(kind="hover_tip_power", target=match.group(1), source="HoverTipFactory.FromPower"))

    for match in re.finditer(r"HoverTipFactory\.FromOrb<(\w+)>", content):
        tips.append(CardRelation(kind="hover_tip_orb", target=match.group(1), source="HoverTipFactory.FromOrb"))

    return dedupe_relations(tips)


def extract_relations(content: str) -> list[CardRelation]:
    relations: list[CardRelation] = []

    for match in re.finditer(r"CreateCard<(\w+)>", content):
        relations.append(CardRelation(kind="creates_card", target=class_name_to_id(match.group(1)), source="CreateCard"))

    for match in re.finditer(r"(\w+)\.CreateInHand\(", content):
        relations.append(CardRelation(kind="creates_card", target=class_name_to_id(match.group(1)), source="CreateInHand"))

    for match in re.finditer(r"AddToCombatAndPreview<(\w+)>", content):
        relations.append(CardRelation(kind="creates_card", target=class_name_to_id(match.group(1)), source="AddToCombatAndPreview"))

    return dedupe_relations(relations)


def dedupe_relations(relations: list[CardRelation]) -> list[CardRelation]:
    deduped: list[CardRelation] = []
    seen: set[tuple[str, str, str]] = set()
    for relation in relations:
        key = (relation.kind, relation.target, relation.source)
        if key not in seen:
            seen.add(key)
            deduped.append(relation)
    return deduped


def append_run(runs: list[TextRun], text: str, source_var: str | None = None, style: str | None = None) -> None:
    if text == "":
        return
    if runs and runs[-1].source_var == source_var and runs[-1].style == style:
        runs[-1].text += text
        return
    runs.append(TextRun(text=text, source_var=source_var, style=style))


def text_plain(runs: list[TextRun]) -> str:
    return "".join(run.text for run in runs)


def split_top_level(value: str, separator: str = "|") -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    for index, char in enumerate(value):
        if char == "{":
            depth += 1
        elif char == "}" and depth > 0:
            depth -= 1
        elif char == separator and depth == 0:
            parts.append(value[start:index])
            start = index + 1
    parts.append(value[start:])
    return parts


def find_matching_brace(markup: str, start: int) -> int:
    depth = 0
    for index in range(start, len(markup)):
        if markup[index] == "{":
            depth += 1
        elif markup[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    return -1


def format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def resolve_placeholder(
    placeholder: str,
    vars_by_name: dict[str, int],
    changed_vars: set[str],
    upgraded: bool,
    style_stack: list[str],
) -> list[TextRun]:
    parts = placeholder.split(":", 2)
    name = parts[0]
    formatter = parts[1] if len(parts) > 1 else None
    if formatter and formatter.endswith("()"):
        formatter = formatter[:-2]
    formatter_arg = parts[2] if len(parts) > 2 else ""
    style = style_stack[-1] if style_stack else None

    if name == "IfUpgraded" and formatter == "show":
        options = split_top_level(formatter_arg)
        selected = options[0] if upgraded else (options[1] if len(options) > 1 else "")
        return render_text_runs(selected, vars_by_name, changed_vars, upgraded, style_stack)

    if name == "InCombat":
        return []

    if name == "energyPrefix":
        return []

    if name == "singleStarIcon":
        return [TextRun(text="*", style=style)]

    if name not in vars_by_name:
        return [TextRun(text="{" + placeholder + "}", style=style)]

    value = vars_by_name[name]
    if formatter == "plural":
        options = split_top_level(formatter_arg)
        selected = options[0] if abs(value) == 1 else (options[1] if len(options) > 1 else options[0])
        return render_text_runs(selected, vars_by_name, changed_vars, upgraded, style_stack)

    if formatter in (None, "diff", "energyIcons", "starIcons"):
        value_style = style
        if formatter == "diff" and upgraded and name in changed_vars:
            value_style = "green" if value >= 0 else "red"
        return [TextRun(text=format_value(value), source_var=name, style=value_style)]

    return [TextRun(text=format_value(value), source_var=name, style=style)]


def render_text_runs(
    markup: str,
    vars_by_name: dict[str, int],
    changed_vars: set[str],
    upgraded: bool,
    style_stack: list[str] | None = None,
) -> list[TextRun]:
    style_stack = list(style_stack or [])
    runs: list[TextRun] = []
    index = 0
    tag_pattern = re.compile(r"\[(/?)([A-Za-z][A-Za-z0-9_]*)\]")

    while index < len(markup):
        if markup[index] == "{":
            end = find_matching_brace(markup, index)
            if end == -1:
                append_run(runs, markup[index], style=style_stack[-1] if style_stack else None)
                index += 1
                continue
            for run in resolve_placeholder(markup[index + 1 : end], vars_by_name, changed_vars, upgraded, style_stack):
                append_run(runs, run.text, run.source_var, run.style)
            index = end + 1
            continue

        tag_match = tag_pattern.match(markup, index)
        if tag_match:
            is_closing = tag_match.group(1) == "/"
            tag_name = tag_match.group(2)
            if is_closing:
                if tag_name in style_stack:
                    style_stack.remove(tag_name)
            else:
                style_stack.append(tag_name)
            index = tag_match.end()
            continue

        next_special = len(markup)
        for char in ("{", "["):
            found = markup.find(char, index + 1)
            if found != -1:
                next_special = min(next_special, found)
        append_run(runs, markup[index:next_special], style=style_stack[-1] if style_stack else None)
        index = next_special

    return runs


def resolve_text(markup: str, vars_by_name: dict[str, int], changed_vars: set[str], upgraded: bool) -> ResolvedText:
    runs = render_text_runs(markup, vars_by_name, changed_vars, upgraded)
    return ResolvedText(plain=text_plain(runs), runs=runs)


def build_resolved_card(
    card_id: str,
    cost: int,
    vars_by_name: dict[str, int],
    upgrades: list[UpgradeDelta],
    cost_upgrades: list[CostUpgradeDelta],
    localization: dict[str, str],
) -> ResolvedCard:
    title_key = f"{card_id}.title"
    description_key = f"{card_id}.description"
    missing_keys = [key for key in (title_key, description_key) if key not in localization]
    if missing_keys:
        raise ValueError(f"Missing required localization keys for {card_id}: {', '.join(missing_keys)}")

    base_description = resolve_text(localization[description_key], vars_by_name, set(), upgraded=False)
    base = ResolvedCardState(
        title=localization[title_key],
        cost=cost,
        description=base_description,
    )

    upgraded_vars = dict(vars_by_name)
    changed_vars: set[str] = set()
    for upgrade in upgrades:
        if upgrade.var in upgraded_vars:
            upgraded_vars[upgrade.var] += upgrade.delta
            changed_vars.add(upgrade.var)

    upgraded_cost = cost
    for cost_upgrade in cost_upgrades:
        if cost_upgrade.target == "cost":
            upgraded_cost = max(upgraded_cost + cost_upgrade.delta, 0)

    upgraded_description = resolve_text(localization[description_key], upgraded_vars, changed_vars, upgraded=True)
    changed: list[str] = []
    if upgraded_cost != cost:
        changed.append("cost")
    if upgraded_description.plain != base_description.plain:
        changed.append("description")
    upgraded_state = ResolvedCardState(
        title=f"{localization[title_key]}+",
        cost=upgraded_cost,
        changed=changed,
        description=upgraded_description,
    )
    return ResolvedCard(base=base, upgraded=upgraded_state)


def parse_card(
    filepath: Path,
    localization: dict[str, str] | None = None,
    card_pools: dict[str, str] | None = None,
) -> CardInfo:
    content = filepath.read_text(encoding="utf-8")
    class_name = filepath.stem
    card_id = class_name_to_id(class_name)
    cost, card_type, rarity, target = extract_constructor_fields(content)
    display_path = str(filepath.relative_to(LAB_DIR.parent))

    localization = localization or {}
    card_pools = card_pools or {}
    title_key = f"{card_id}.title"
    description_key = f"{card_id}.description"
    version = source_version(filepath)
    vars_by_name = extract_vars(content, dynamic_var_type_names(version) if version else {})
    upgrades = extract_upgrades(content, dynamic_var_accessor_keys(version) if version else {})
    cost_upgrades = extract_cost_upgrades(content)

    notes: list[str] = []
    if localization and description_key not in localization:
        notes.append("Description is not present in the C# file; supply localization data to populate it.")

    resolved: ResolvedCard | dict[str, Any] = {}
    if localization:
        resolved = build_resolved_card(card_id, cost, vars_by_name, upgrades, cost_upgrades, localization)

    return CardInfo(
        schema_version=SCHEMA_VERSION,
        id=card_id,
        raw=RawCardInfo(
            parser_version=PARSER_VERSION,
            class_name=class_name,
            file=display_path,
            cost=cost,
            type=card_type,
            rarity=rarity,
            target=target,
            localization=LocalizationInfo(
                table="cards",
                title_key=title_key,
                description_key=description_key,
            ),
            vars=vars_by_name,
            assets=extract_assets(card_id, card_pools.get(card_id)),
            keywords=extract_keywords(content),
            tags=extract_tags(content),
            upgrades=upgrades,
            cost_upgrades=cost_upgrades,
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
    card_pools: dict[str, str] | None = None,
) -> list[CardInfo]:
    return [parse_card(path, localization, card_pools) for path in sorted(card_dir.glob("*.cs"))]


def to_jsonable(value: Any) -> Any:
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: to_jsonable(val) for key, val in value.items() if val is not None and val != [] and val != {}}
    if is_dataclass(value):
        return {
            item.name: to_jsonable(val)
            for item in fields(value)
            for val in [getattr(value, item.name)]
            if val is not None and val != [] and (val != {} or item.name == "resolved")
        }
    return value


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
    card_pools = load_card_pool_map(args.version or inferred_version)
    output_dir = args.output_dir.resolve() if args.output_dir else default_output_dir(args.version or inferred_version)

    if input_path.is_file():
        card = parse_card(input_path, localization, card_pools)
        if args.stdout:
            print(json.dumps(to_jsonable(card), indent=2, sort_keys=False))
            return
        output_path = write_card_output(card, output_dir)
        print(output_path)
    else:
        started_at = time.perf_counter()
        cards = parse_many(input_path, localization, card_pools)
        if args.stdout:
            print(json.dumps(to_jsonable(cards), indent=2, sort_keys=False))
            return
        paths = write_many_cards(cards, output_dir)
        elapsed_seconds = time.perf_counter() - started_at
        print(
            f"Wrote {len(paths)} card files to {output_dir} "
            f"in {elapsed_seconds:.3f}s"
        )


if __name__ == "__main__":
    main()
