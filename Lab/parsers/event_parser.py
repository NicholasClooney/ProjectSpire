#!/usr/bin/env python3
"""Parse decompiled STS2 event C# into structured JSON.

Conservative approach:
- Only emits facts explicit in the event source or localization.
- Page and option structure is derived from localization keys, not the C#
  state machine (which is too dynamic to parse reliably).
- Ancient events (AncientEventModel subclasses) are emitted with kind=ancient
  and no pages — they use a different dialogue system with no standard loc keys.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from common import (
    DEFAULT_LANGUAGE,
    DECOMPILED_DIR,
    IMAGE_DIR,
    LAB_DIR,
    LOCALIZATION_DIR,
    ResolvedText,
    class_name_to_id,
    dynamic_var_type_names,
    extract_vars,
    infer_version_from_path,
    latest_decompiled_version,
    list_decompiled_versions,
    load_localization,
    resolve_text,
    source_version,
    to_jsonable,
)


EVENTS_SUBDIR = "MegaCrit.Sts2.Core.Models.Events"
PARSER_VERSION = "0.1.0"
SCHEMA_VERSION = "0.1.0"

EVENT_IMAGE_DIR = IMAGE_DIR / "events"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class EventLocalization:
    table: str
    title_key: str


@dataclass
class EventAsset:
    kind: str
    path: str
    source: str


@dataclass
class ResolvedOption:
    title: str
    description: ResolvedText | None = None


@dataclass
class ResolvedPage:
    description: ResolvedText | None = None
    options: dict[str, ResolvedOption] = field(default_factory=dict)


@dataclass
class ResolvedEvent:
    title: str
    loss: ResolvedText | None = None
    pages: dict[str, ResolvedPage] = field(default_factory=dict)


@dataclass
class RawEventInfo:
    parser_version: str
    class_name: str
    file: str
    kind: str
    localization: EventLocalization
    vars: dict[str, int] = field(default_factory=dict)
    assets: list[EventAsset] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class EventInfo:
    schema_version: str
    id: str
    raw: RawEventInfo
    resolved: ResolvedEvent | dict[str, Any]


# ---------------------------------------------------------------------------
# Model detection
# ---------------------------------------------------------------------------


def is_event_model(content: str) -> bool:
    return bool(re.search(r":\s*(?:Ancient)?EventModel\b", content))


def is_ancient_event(content: str) -> bool:
    return bool(re.search(r":\s*AncientEventModel\b", content))


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------


def event_image_path(event_id: str) -> Path:
    return EVENT_IMAGE_DIR / f"{event_id.lower()}.webp"


def extract_event_assets(event_id: str) -> list[EventAsset]:
    path = event_image_path(event_id)
    if not path.exists():
        return []
    return [
        EventAsset(
            kind="portrait",
            path=str(path.relative_to(LAB_DIR.parent)),
            source="Lab.resources.images.events",
        )
    ]


# ---------------------------------------------------------------------------
# Localization resolution
# ---------------------------------------------------------------------------


def _page_id(event_id: str, key: str) -> str | None:
    """Extract page ID from a full localization key, or None if not a pages key."""
    prefix = f"{event_id}.pages."
    if not key.startswith(prefix):
        return None
    rest = key[len(prefix):]
    return rest.split(".")[0]


def build_resolved_event(
    event_id: str,
    vars_by_name: dict[str, int],
    localization: dict[str, str],
    title_key: str | None = None,
) -> ResolvedEvent:
    title_key = title_key or f"{event_id}.title"
    if title_key not in localization:
        raise ValueError(f"Missing title key for {event_id}")

    display_vars: dict[str, Any] = dict(vars_by_name)

    loss: ResolvedText | None = None
    loss_key = f"{event_id}.loss"
    if loss_key in localization and localization[loss_key]:
        loss = resolve_text(localization[loss_key], display_vars, set(), upgraded=False)

    # Collect all page IDs from localization keys
    page_ids: list[str] = []
    for key in localization:
        pid = _page_id(event_id, key)
        if pid and pid not in page_ids:
            page_ids.append(pid)
    page_ids.sort()

    pages: dict[str, ResolvedPage] = {}
    for page_id in page_ids:
        page_prefix = f"{event_id}.pages.{page_id}"
        desc_key = f"{page_prefix}.description"

        description: ResolvedText | None = None
        if desc_key in localization and localization[desc_key]:
            description = resolve_text(localization[desc_key], display_vars, set(), upgraded=False)

        # Collect options for this page
        option_prefix = f"{page_prefix}.options."
        option_ids: list[str] = []
        for key in localization:
            if key.startswith(option_prefix):
                rest = key[len(option_prefix):]
                opt_id = rest.split(".")[0]
                if opt_id not in option_ids:
                    option_ids.append(opt_id)
        option_ids.sort()

        options: dict[str, ResolvedOption] = {}
        for opt_id in option_ids:
            opt_prefix = f"{option_prefix}{opt_id}"
            title_val = localization.get(f"{opt_prefix}.title", "")
            desc_val = localization.get(f"{opt_prefix}.description", "")

            opt_description: ResolvedText | None = None
            if desc_val:
                opt_description = resolve_text(desc_val, display_vars, set(), upgraded=False)

            options[opt_id] = ResolvedOption(title=title_val, description=opt_description)

        page = ResolvedPage(description=description, options=options)
        if page.description is not None or page.options:
            pages[page_id] = page

    return ResolvedEvent(
        title=localization[title_key],
        loss=loss,
        pages=pages,
    )


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def default_localization_path(language: str) -> Path:
    return LOCALIZATION_DIR / language / "events.json"


def default_ancients_localization_path(language: str) -> Path:
    return LOCALIZATION_DIR / language / "ancients.json"


def parse_event(
    filepath: Path,
    localization: dict[str, str] | None = None,
    ancients_localization: dict[str, str] | None = None,
) -> EventInfo:
    content = filepath.read_text(encoding="utf-8")
    class_name = filepath.stem
    event_id = class_name_to_id(class_name)
    display_path = str(filepath.relative_to(LAB_DIR.parent))

    localization = localization or {}
    ancients_localization = ancients_localization or {}
    version = source_version(filepath)

    kind = "ancient" if is_ancient_event(content) else "event"
    vars_by_name = extract_vars(content, dynamic_var_type_names(version) if version else {})
    assets = extract_event_assets(event_id)

    title_key = f"{event_id}.title"
    epithet_key = f"{event_id}.epithet"
    notes: list[str] = []

    resolved: ResolvedEvent | dict[str, Any] = {}
    if kind == "event":
        if localization and title_key in localization:
            resolved = build_resolved_event(event_id, vars_by_name, localization)
        elif localization:
            notes.append("Localization keys not found; event may be deprecated or unreleased.")
    elif kind == "ancient":
        if ancients_localization and epithet_key in ancients_localization:
            resolved = build_resolved_event(
                event_id, vars_by_name, ancients_localization, title_key=epithet_key
            )

    return EventInfo(
        schema_version=SCHEMA_VERSION,
        id=event_id,
        raw=RawEventInfo(
            parser_version=PARSER_VERSION,
            class_name=class_name,
            file=display_path,
            kind=kind,
            localization=EventLocalization(
                table="events",
                title_key=title_key,
            ),
            vars=vars_by_name,
            assets=assets,
            notes=notes,
        ),
        resolved=resolved,
    )


def parse_many(
    event_dir: Path,
    localization: dict[str, str] | None = None,
    ancients_localization: dict[str, str] | None = None,
) -> list[EventInfo]:
    events = []
    for path in sorted(event_dir.glob("*.cs")):
        content = path.read_text(encoding="utf-8")
        if not is_event_model(content):
            continue
        events.append(parse_event(path, localization, ancients_localization))
    return events


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def write_event_output(event: EventInfo, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{event.id.lower()}.json"
    output_path.write_text(
        json.dumps(to_jsonable(event), indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def write_many_events(events: list[EventInfo], output_dir: Path) -> list[Path]:
    return [write_event_output(event, output_dir) for event in events]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


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


def resolve_events_dir(path_arg: str | None, version: str | None) -> tuple[Path, str | None]:
    if path_arg:
        path = Path(path_arg).resolve()
        return path, infer_version_from_path(path)

    available_versions = list_decompiled_versions()
    selected_version = version
    if selected_version is None:
        latest = latest_decompiled_version()
        selected_version = prompt_for_version(available_versions, latest) if sys.stdin.isatty() else latest
    return DECOMPILED_DIR / selected_version / EVENTS_SUBDIR, selected_version


def default_output_dir(version: str | None) -> Path:
    return LAB_DIR / "data" / version / "events" if version else LAB_DIR / "data" / "events"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="Event .cs file or events directory")
    parser.add_argument("--version", help="Decompiler version, e.g. v0.103.2")
    parser.add_argument(
        "--language",
        default=DEFAULT_LANGUAGE,
        help=f"Localization language (default: {DEFAULT_LANGUAGE})",
    )
    parser.add_argument("--localization", type=Path, help="Path to events.json (overrides default)")
    parser.add_argument("--raw-only", action="store_true", help="Skip localization resolution")
    parser.add_argument("--output-dir", type=Path, help="Directory for per-event JSON output")
    parser.add_argument("--stdout", action="store_true", help="Print JSON to stdout instead of writing files")
    args = parser.parse_args()

    input_path, inferred_version = resolve_events_dir(args.path, args.version)
    version = args.version or inferred_version
    localization_path = args.localization or default_localization_path(args.language)
    ancients_localization_path = default_ancients_localization_path(args.language)
    localization = {} if args.raw_only else load_localization(localization_path)
    ancients_localization = {} if args.raw_only else load_localization(ancients_localization_path)
    output_dir = args.output_dir.resolve() if args.output_dir else default_output_dir(version)

    if input_path.is_file():
        event = parse_event(input_path, localization, ancients_localization)
        if args.stdout:
            print(json.dumps(to_jsonable(event), indent=2, sort_keys=False))
            return
        output_path = write_event_output(event, output_dir)
        print(output_path)
    else:
        started_at = time.perf_counter()
        events = parse_many(input_path, localization, ancients_localization)
        if args.stdout:
            print(json.dumps(to_jsonable(events), indent=2, sort_keys=False))
            return
        paths = write_many_events(events, output_dir)
        elapsed = time.perf_counter() - started_at
        print(f"Wrote {len(paths)} event files to {output_dir} in {elapsed:.3f}s")


if __name__ == "__main__":
    main()
