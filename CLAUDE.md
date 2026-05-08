# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo structure

See `README.md`.

When making structural changes to the repository, update the repo structure section in `README.md` in the same change.

## Plans

Implementation-ready plans live in `Documentation/Plans/`.

Use this folder for agreed plans that should be executable by another engineer or agent without rediscovering the intent, target commit, naming convention, verification steps, or important assumptions.

## Captain Logs

At the end of each meaningful user-agent conversation, add or update the appropriate Captain Log in `Documentation/Captain Logs/`.

Follow the detailed local workflow in `Documentation/Captain Logs/AGENTS.md`. Claude-compatible local instructions are available through the symlink `Documentation/Captain Logs/CLAUDE.md`.

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

See `Documentation/Agent Workflows/Snapshot Tags.md` before creating or reviewing snapshot tags.

## Release tags and pages

See `Documentation/Agent Workflows/Release Tags and Pages.md` before creating or reviewing release tags or GitHub Release pages.

## Today's work timeline summaries

See `Documentation/Agent Workflows/Todays Work Timeline Summary.md` when summarizing today's commits and today's changed documentation for a timeline entry or thread-style update. Keep the result prose-led, with a few blended Eleventy GitHub shortcode snippets or regular GitHub links instead of a formal source-reference section.

## Commits

Conventional commits with a short, stable area scope are required. Prefer concise shorthand scopes that identify the product area, app, workflow, or documentation family over long module names. Examples: `feat(app/cafe): centralize tab navigation style`, `docs(logs): refine Captain Log guidance`, `docs(doc): update repo structure notes`, `fix(api): handle missing catalog payload`, `chore(lab): refresh generated fixtures`.
