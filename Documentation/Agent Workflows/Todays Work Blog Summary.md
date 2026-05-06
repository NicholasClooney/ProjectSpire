# Today's Work Blog Summary

Date: 2026-05-06

Project areas: `Documentation/`, Git history, blog publishing notes

Use this workflow when the user asks for a high-level summary of what happened today, grounded in commits and documentation changes, with source references suitable for the user's Eleventy blog.

## Goal

Produce a concise, blog-ready summary of today's work that covers:

- commits made today
- plans, devlogs, Captain Logs, and other files changed under `Documentation/`
- key technical details worth preserving
- exact source references using the Eleventy GitHub shortcode

Keep the narrative high level, but anchor important implementation details to pinned GitHub snippets instead of pasting code blocks.

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

## GitHub Shortcode References

Use this site's Eleventy GitHub shortcode for source references:

```njk
{% github "https://github.com/OWNER/REPO/blob/COMMIT_OR_BRANCH/path/to/file.ext#L10-L42" %}
```

Rules:

- Pass a normal GitHub `blob` URL.
- Include `#Lx-Ly` for the exact line range; omit it only when embedding the whole file.
- Prefer pinned commit SHAs over `main` so posts do not drift over time.
- Optional second arg controls chrome theme: `"auto"` default, `"light"`, or `"dark"`.

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

Use this output shape unless the user asks for a different format:

```md
## YYYY-MM-DD - Short Title

One or two paragraphs summarizing the day's main arc.

### Key Work

- High-level item with specific technical detail and why it mattered.
- High-level item with specific technical detail and why it mattered.

### Source References

{% github "https://github.com/OWNER/REPO/blob/COMMIT/path/to/file.md#Lx-Ly" %}

### Notes

- Mention uncommitted work, gaps, skipped verification, or open questions only when relevant.
```

Do not paste long code blocks from the repo into the blog summary. Use short prose plus `{% github ... %}` snippets for exact source evidence.

## Quality Bar

Before handing back the summary:

- confirm the commit window and exact date used
- verify every shortcode URL points at a real path and pinned commit
- verify every line range matches the quoted claim
- separate committed history from uncommitted local changes
- keep the summary readable enough for a blog post, not a raw changelog
