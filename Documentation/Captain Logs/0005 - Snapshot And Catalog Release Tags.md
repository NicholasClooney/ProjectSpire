# 0005 - Snapshot And Catalog Release Tags

This conversation records the snapshot and release tagging work for the May 6 repository checkpoint and card catalog release.

Entries are newest first. This is not a transcript and it is not a replacement for full devlogs in `Documentation/Devlogs/`. Each entry preserves the interaction shape: user direction, agent response, user steering, outcome, and what future agents should carry forward.

## 2026-05-07 - Tag May 6 Snapshot And Card Catalog Release

**Context:** The user wanted durable Git tags for the prior day's final documentation commit and for the completed card catalog work.

**User Direction:** The user asked to create a snapshot tag for commit `2b50e8c` and a release tag for the latest catalog changes, explicitly including both `Lab/scripts/serve-card-catalog.py` and the generated `Lab/catalog` content, with confirmation before tagging.

**Agent Response:** The agent reviewed the snapshot and release tag workflow docs, checked existing local and remote tags, inspected relevant commits, proposed `snapshot/2026-05-06` at `2b50e8c` and `release/card-catalog/v0.1.0` at `717c87d`, then waited for confirmation.

**User Feedback:** The user approved the proposed tags and release scope.

**Outcome:** Created and pushed annotated tags `snapshot/2026-05-06` and `release/card-catalog/v0.1.0`, and created the GitHub Release page for `release/card-catalog/v0.1.0`.

**Carry Forward:** When tagging catalog releases, include the generated `Lab/catalog` content and serving workflow changes together when they ship as one unit.
