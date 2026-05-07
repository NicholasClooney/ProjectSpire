# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo structure

See `README.md`.

When making structural changes to the repository, update the repo structure section in `README.md` in the same change.

## Plans

Implementation-ready plans live in `Documentation/Plans/`.

Use this folder for agreed plans that should be executable by another engineer or agent without rediscovering the intent, target commit, naming convention, verification steps, or important assumptions.

## Captain Logs

Agent/user collaboration notes live in `Documentation/Captain Logs/`.

Each conversation gets its own numbered markdown file in this folder, using the filename pattern `NNNN - Short Conversation Title.md`. For example, `0001 - The Beginning of Captain Logs.md`.

If the current conversation does not already have a Captain Log file, create the next numbered file and add it to the top of `Documentation/Captain Logs/README.md` with a short summary.

At the end of every meaningful user-agent interaction, add a concise entry to the top of the current conversation's log file, directly below the introductory text, so newest entries appear first and oldest entries remain at the bottom. Do not add entries for purely appreciative or acknowledgement-only replies, such as "nice", "good", or "well done", unless they include a decision, correction, new constraint, or requested change. Do not add entries for routine operational steps, such as git status checks, staging, committing, pushing, or splitting commits, when the user provides no feedback, decision, correction, or reusable process guidance. This is not a transcript and it is not a replacement for full devlogs in `Documentation/Devlogs/`. Capture the collaboration shape: what the user asked for, how the agent responded, how the agent acted, how the user steered or corrected the work, the outcome, and what future agents should carry forward.

Confirmed user taste, craft standards, and durable working preferences live in `Documentation/Captain Logs/User Preferences.md`. When the user provides feedback on completed work, corrects the agent's approach, pauses or redirects the work, or otherwise reveals a possible durable preference, infer the likely preference and ask whether the user wants it recorded there before editing the file. Keep that file short, one-line oriented, confirmed-only, and avoid duplicating instructions already captured elsewhere.

Keep `Documentation/Captain Logs/README.md` as an index of conversation log files. Add new log links at the top of the index, with a short summary, so newest conversations appear first and oldest conversations remain at the bottom.

After updating the file, explicitly report back to the user with the prefix `I have updated Captain Log` followed by a short summary of the latest topic, implementation, feedback, or outcome. For example: `I have updated Captain Log on the latest documentation-flow feedback: the confirmation now includes a concise summary.`

When writing `Carry Forward`, prefer durable engineering guidance over narrow restatement. Capture the reusable lesson future agents should preserve, especially where the work revealed a need to encode consistency into code structure. If a behavior, style, naming pattern, workflow, or policy should stay unified, favor shared helpers, wrappers, types, configuration, tests, or documentation that make drift harder instead of relying on individual call sites to remember the convention.

Use this entry shape:

```md
## YYYY-MM-DD - Short Session Title

**Context:** Why this interaction happened.

**User Direction:** What the user asked for, valued, constrained, or clarified.

**Agent Response:** What the agent did or proposed at a high level.

**User Feedback:** Pushback, corrections, preferences, or observations from the user.

**Outcome:** What changed, what was decided, or what remains pending.

**Carry Forward:** What future agents should preserve, avoid, or remember.
```

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
