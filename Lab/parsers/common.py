"""Shared utilities for STS2 parsers.

All parsers (cards, relics, potions, etc.) import from here for:
- Path constants and version discovery
- DynamicVar extraction from decompiled C# source
- SmartFormat markup rendering (BBCode tags, diff, plural, etc.)
- Hover tip extraction (HoverTipFactory patterns)
- JSON serialisation of dataclasses
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, fields, is_dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
LAB_DIR = SCRIPT_PATH.parent.parent
DECOMPILED_DIR = LAB_DIR / "decompiled"
RESOURCES_DIR = LAB_DIR / "resources"
LOCALIZATION_DIR = RESOURCES_DIR / "localization"
IMAGE_DIR = RESOURCES_DIR / "images"
DEFAULT_LANGUAGE = "eng"


# ---------------------------------------------------------------------------
# Shared dataclasses
# ---------------------------------------------------------------------------


@dataclass
class HoverTip:
    kind: str
    target: str
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


# ---------------------------------------------------------------------------
# ID and version utilities
# ---------------------------------------------------------------------------


def class_name_to_id(class_name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).upper()


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


def infer_version_from_path(path: Path) -> str | None:
    parts = path.parts
    for index, part in enumerate(parts):
        if part == "decompiled" and index + 1 < len(parts):
            candidate = parts[index + 1]
            if candidate.startswith("v"):
                return candidate
    return None


def load_localization(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


# ---------------------------------------------------------------------------
# DynamicVar extraction
# ---------------------------------------------------------------------------


@lru_cache(maxsize=None)
def dynamic_var_type_names(version: str) -> dict[str, str]:
    """Return a map of *Var class name → canonical variable name for that version."""
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


def extract_numeric_symbols(content: str) -> dict[str, int]:
    symbols: dict[str, int] = {}
    for match in re.finditer(r"\b(?:public|private|protected)?\s*const\s+int\s+(\w+)\s*=\s*(-?\d+)", content):
        symbols[match.group(1)] = int(match.group(2))
    for match in re.finditer(r"\b(?:private|public|protected)?\s*int\s+(\w+)\s*=\s*(-?\d+)", content):
        symbols[match.group(1)] = int(match.group(2))
    for match in re.finditer(r"\bpublic\s+int\s+(\w+)\s*\{.*?\breturn\s+(\w+)\s*;.*?\bset\b", content, re.DOTALL):
        if match.group(2) in symbols:
            symbols[match.group(1)] = symbols[match.group(2)]
    return symbols


def parse_numeric_arg(value: str, symbols: dict[str, int]) -> int | None:
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return symbols.get(value)


def extract_vars(content: str, type_names: dict[str, str] | None = None) -> dict[str, int]:
    vars_found: dict[str, int] = {}
    type_names = type_names or {}
    symbols = extract_numeric_symbols(content)

    for match in re.finditer(
        r'new (?P<type>\w+Var|DynamicVar)(?:<(?P<generic>\w+)>)?\(\s*(?:"(?P<name>\w+)"\s*,\s*)?(?P<value>-?\d+|\w+)(?:m)?',
        content,
    ):
        var_type = match.group("type")
        var_name = match.group("name") or (match.group("generic") if var_type == "PowerVar" else type_names.get(var_type))
        var_value = parse_numeric_arg(match.group("value"), symbols)
        if var_name and var_value is not None:
            vars_found[var_name] = var_value

    calculated_base = vars_found.get("CalculationBase", 0)
    for match in re.finditer(r'new (?P<type>Calculated\w*Var)(?:<[^>]+>)?\(\s*(?:"(?P<name>\w+)"|[^),]+)', content):
        var_type = match.group("type")
        var_name = match.group("name") or type_names.get(var_type)
        if var_name and var_name not in vars_found:
            vars_found[var_name] = calculated_base

    return vars_found


# ---------------------------------------------------------------------------
# SmartFormat markup renderer
# ---------------------------------------------------------------------------


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


def parse_placeholder_parts(placeholder: str) -> tuple[str, str | None, str]:
    parts = split_top_level(placeholder, ":")
    name = parts[0] if parts else ""
    formatter = parts[1] if len(parts) > 1 else None
    formatter_arg = ":".join(parts[2:]) if len(parts) > 2 else ""
    return name, formatter, formatter_arg


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
    vars_by_name: dict[str, Any],
    changed_vars: set[str],
    upgraded: bool,
    style_stack: list[str],
    current_var: str | None = None,
) -> list[TextRun]:
    raw_name, formatter, formatter_arg = parse_placeholder_parts(placeholder)
    name = raw_name or current_var or ""
    if formatter and formatter.endswith("()"):
        formatter = formatter[:-2]
    formatter_args = ""
    formatter_match = re.fullmatch(r"(\w+)\((.*)\)", formatter or "")
    if formatter_match:
        formatter = formatter_match.group(1)
        formatter_args = formatter_match.group(2)
    style = style_stack[-1] if style_stack else None

    if name == "IfUpgraded" and formatter == "show":
        options = split_top_level(formatter_arg)
        selected = options[0] if upgraded else (options[1] if len(options) > 1 else "")
        return render_text_runs(selected, vars_by_name, changed_vars, upgraded, style_stack, current_var)

    if name == "InCombat":
        return []

    if name == "energyPrefix":
        return []

    if name == "singleStarIcon":
        return [TextRun(text="*", style=style)]

    # cond can resolve a fallback even when the var isn't a known numeric var —
    # handle it before the vars_by_name guard so dynamic string vars get the fallback branch.
    if formatter == "cond":
        if "?" in formatter_arg:
            # Format: {var:cond:condition?option1|option2}
            condition, _, options_markup = formatter_arg.partition("?")
            options = split_top_level(options_markup)
            value = vars_by_name.get(name)
            selected = ""
            if condition.startswith(">") and isinstance(value, int):
                threshold = parse_numeric_arg(condition[1:], {})
                if threshold is not None and value > threshold:
                    selected = options[0] if options else ""
                elif len(options) > 1:
                    selected = options[1]
        else:
            # Format: {var:cond:option1|option2} — use option1 if var is known, else fallback
            options = split_top_level(formatter_arg)
            value = vars_by_name.get(name)
            if value is not None and options:
                selected = options[0]
            else:
                selected = options[1] if len(options) > 1 else (options[0] if options else "")
        return render_text_runs(selected, vars_by_name, changed_vars, upgraded, style_stack, name)

    if name not in vars_by_name:
        return [TextRun(text="{" + placeholder + "}", style=style)]

    value = vars_by_name[name]

    if formatter == "percentMore":
        return [TextRun(text=format_value(value), source_var=name, style=style)]

    if formatter and formatter not in {"plural", "choose", "diff", "inverseDiff", "energyIcons", "starIcons"}:
        options = split_top_level(formatter)
        if isinstance(value, bool):
            selected = options[0] if value else (options[1] if len(options) > 1 else "")
            return render_text_runs(selected, vars_by_name, changed_vars, upgraded, style_stack, name)
        return [TextRun(text="{" + placeholder + "}", style=style)]

    if formatter == "plural":
        options = split_top_level(formatter_arg)
        selected = options[0] if isinstance(value, int) and abs(value) == 1 else (options[1] if len(options) > 1 else options[0])
        return render_text_runs(selected, vars_by_name, changed_vars, upgraded, style_stack, name)

    if formatter == "choose":
        choices = split_top_level(formatter_args)
        options = split_top_level(formatter_arg)
        if choices and str(value) in choices:
            choice_index = choices.index(str(value))
            selected = options[choice_index] if choice_index < len(options) else ""
        else:
            selected = options[-1] if len(options) > len(choices) else ""
        return render_text_runs(selected, vars_by_name, changed_vars, upgraded, style_stack, name)

    if formatter in (None, "diff", "inverseDiff", "energyIcons", "starIcons"):
        value_style = style
        if formatter in {"diff", "inverseDiff"} and upgraded and name in changed_vars:
            value_style = "green" if value >= 0 else "red"
        return [TextRun(text=format_value(value), source_var=name, style=value_style)]

    return [TextRun(text=format_value(value), source_var=name, style=style)]


def render_text_runs(
    markup: str,
    vars_by_name: dict[str, Any],
    changed_vars: set[str],
    upgraded: bool,
    style_stack: list[str] | None = None,
    current_var: str | None = None,
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
            for run in resolve_placeholder(markup[index + 1 : end], vars_by_name, changed_vars, upgraded, style_stack, current_var):
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


def resolve_text(markup: str, vars_by_name: dict[str, Any], changed_vars: set[str], upgraded: bool) -> ResolvedText:
    runs = render_text_runs(markup, vars_by_name, changed_vars, upgraded)
    return ResolvedText(plain=text_plain(runs), runs=runs)


# ---------------------------------------------------------------------------
# Hover tip extraction
# ---------------------------------------------------------------------------


def extract_tips(content: str) -> list[HoverTip]:
    tips: list[HoverTip] = []

    for match in re.finditer(r"HoverTipFactory\.Static\(StaticHoverTip\.(\w+)\)", content):
        tips.append(HoverTip(kind="hover_tip_static", target=match.group(1), source="HoverTipFactory.Static"))

    for match in re.finditer(r"HoverTipFactory\.FromCard(?:WithCardHoverTips)?<(\w+)>", content):
        tips.append(HoverTip(kind="hover_tip_card", target=class_name_to_id(match.group(1)), source="HoverTipFactory.FromCard"))

    for match in re.finditer(r"HoverTipFactory\.FromPower<(\w+)>", content):
        tips.append(HoverTip(kind="hover_tip_power", target=match.group(1), source="HoverTipFactory.FromPower"))

    for match in re.finditer(r"HoverTipFactory\.FromOrb<(\w+)>", content):
        tips.append(HoverTip(kind="hover_tip_orb", target=match.group(1), source="HoverTipFactory.FromOrb"))

    for _ in re.finditer(r"HoverTipFactory\.ForEnergy\(", content):
        tips.append(HoverTip(kind="hover_tip_energy", target="Energy", source="HoverTipFactory.ForEnergy"))

    for match in re.finditer(r"HoverTipFactory\.FromKeyword\(CardKeyword\.(\w+)\)", content):
        tips.append(HoverTip(kind="hover_tip_keyword", target=match.group(1), source="HoverTipFactory.FromKeyword"))

    for _ in re.finditer(r"HoverTipFactory\.FromForge\(\)", content):
        tips.append(HoverTip(kind="hover_tip_forge", target="Forge", source="HoverTipFactory.FromForge"))

    return _dedupe_tips(tips)


def _dedupe_tips(tips: list[HoverTip]) -> list[HoverTip]:
    deduped: list[HoverTip] = []
    seen: set[tuple[str, str, str]] = set()
    for tip in tips:
        key = (tip.kind, tip.target, tip.source)
        if key not in seen:
            seen.add(key)
            deduped.append(tip)
    return deduped


# ---------------------------------------------------------------------------
# JSON serialisation
# ---------------------------------------------------------------------------


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
