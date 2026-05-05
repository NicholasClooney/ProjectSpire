# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo structure

See `README.md`.

When making structural changes to the repository, update the repo structure section in `README.md` in the same change.

## Plans

Implementation-ready plans live in `Documentation/Plans/`.

Use this folder for agreed plans that should be executable by another engineer or agent without rediscovering the intent, target commit, naming convention, verification steps, or important assumptions.

## Builds

When compiling with `xcodebuild`, pipe through `xcbeautify` to keep output compact and readable:

```
xcodebuild ... | xcbeautify
```

Use raw `xcodebuild` output only when diagnosing a specific issue that needs the full log.

## Game logs

```
~/Library/Application Support/SlayTheSpire2/logs/godot.log
```

`godot.log` is the current session. Tail it live with `tail -f`.

## Snapshot tags

See `Documentation/Snapshot Tags.md` before creating or reviewing snapshot tags.

## Release tags and pages

See `Documentation/Release Tags and Pages.md` before creating or reviewing release tags or GitHub Release pages.

## Commits

Conventional commits with a scope are required, e.g. `feat(SpireAPI):`, `feat(SpireRestAPI):`, `docs(Lab):`, `chore:`.
