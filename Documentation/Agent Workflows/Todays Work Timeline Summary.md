# Today's Work Timeline Summary

Date: 2026-05-06

Project areas: `Documentation/`, Git history, timeline publishing notes

Use this workflow when the user asks for a high-level timeline entry, Twitter-style post, or thread-style summary of what happened today, grounded in commits and documentation changes.

The target is not a formal blog report. Treat it like a concise public timeline update with no strict length limit: readable prose first, source snippets and links blended in only where they add useful texture.

Use `Todays Work Timeline Summary Example.md` as the style reference for tone, flow, embedded snippets, and regular GitHub links.

## Goal

Produce a timeline-ready summary of today's work that covers:

- commits made today
- plans, devlogs, Captain Logs, and other files changed under `Documentation/`
- key technical details worth preserving
- a small number of source references or snippets that fit naturally into the text

Keep the narrative high level and personal enough to read like a timeline entry, not release notes. Prefer one clear arc over a raw changelog.

## Source Window

Use the user's current date and timezone unless they specify another day.

For the current day, gather commits from local midnight through now:

```sh
git log --since="$(date +%F) 00:00" --date=iso-strict --pretty=format:'%H%x09%ad%x09%s'
```

Then gather today's documentation changes:

```sh
git log --since="$(date +%F) 00:00" --name-status -- Documentation
```

If the user asks for a committed-only summary, ignore uncommitted changes. If they ask for "what we have been doing" and the working tree is dirty, mention uncommitted documentation changes separately rather than blending them into committed work.

## What To Read

Read today's changed documentation files at the relevant commit, especially:

- `Documentation/Plans/`
- `Documentation/Devlogs/`
- `Documentation/Captain Logs/`
- `Documentation/Issues/`
- project-wide decision or workflow notes under `Documentation/`

Also inspect the commit subjects and file lists for non-documentation changes so the summary captures what the docs were describing.

Prefer commit hashes, plan names, durable file paths, and verification commands over implementation minutiae. Preserve specific technical details when they explain architecture, data flow, tooling, risk, or a future maintenance decision.

## Source References And Snippets

Use this site's Eleventy GitHub shortcode when an embedded snippet should appear inside the timeline entry:

```njk
{% github "https://github.com/OWNER/REPO/blob/COMMIT_OR_BRANCH/path/to/file.ext#L10-L42" %}
```

Rules:

- Pass a normal GitHub `blob` URL.
- Include `#Lx-Ly` for the exact line range; omit it only when embedding the whole file.
- Prefer pinned commit SHAs over `main` so timeline entries do not drift over time.
- Optional second arg controls chrome theme: `"auto"` default, `"light"`, or `"dark"`.
- Use only a few embedded snippets. They should be sprinkled into the prose near the sentence they support, not collected in a dense "source references" section.
- Use regular Markdown links for supporting implementation files, commits, or secondary details that do not need to be visually embedded.

Example:

```njk
{% github "https://github.com/TheClooneyCollection/11ty-subspace-builder/blob/5e7ae27a30f04c1d6c2bf281de97b29cdccd602d/eleventy.config.js#L19-L46" %}
```

To build the URL:

1. Get the GitHub remote and normalize it to `https://github.com/OWNER/REPO`.
2. Use the commit SHA that introduced or best represents the referenced detail.
3. Resolve line numbers at that commit, not only in the working tree.

Useful commands:

```sh
git config --get remote.origin.url
git show COMMIT:path/to/file.md | nl -ba
```

## Summary Shape

Use this output shape unless the user asks for a different format. Keep it prose-led:

```md
I spent today...

{% github "https://github.com/OWNER/REPO/blob/COMMIT/path/to/planning-file.md#Lx-Ly" %}

That gave the app...

{% github "https://github.com/OWNER/REPO/blob/COMMIT/path/to/planning-file.md#Lx-Ly" %}

On the implementation side, [FileName.swift](https://github.com/OWNER/REPO/blob/COMMIT/path/FileName.swift) now...
```

Avoid formal sections such as `Key Work`, `Source References`, and `Notes` unless the user explicitly asks for a report. Do not paste long code blocks from the repo into the timeline entry. Use short prose plus a few `{% github ... %}` snippets or normal links for exact source evidence.

For a complete example, read `Documentation/Agent Workflows/Todays Work Timeline Summary Example.md`.

## Quality Bar

Before handing back the summary:

- confirm the commit window and exact date used
- verify every shortcode URL points at a real path and pinned commit
- verify every line range matches the quoted claim
- separate committed history from uncommitted local changes
- keep the summary readable as a timeline post or thread-style update, not a raw changelog or release note
