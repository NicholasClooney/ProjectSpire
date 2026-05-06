# Release Tags and Pages

Read this before creating or reviewing release tags or GitHub Release pages.

Release tags mark a finished feature, app, mod, package, or workflow within this monorepo.

Use annotated tags named:

```text
release/<component-or-feature-slug>/vX.Y.Z
```

Use lowercase kebab-case for the slug and SemVer for the version, for example:

```text
release/asset-recovery-team/v0.1.0
```

Create a GitHub Release page for each release tag. Use this title format:

```text
Project Spire - <feature name> v<version> - <short summary>
```

Use mostly bullet points in the release description. Include what finished, important workflow or interface changes, and any follow-up notes that matter for the next person using the release.

Example:

```text
Project Spire - Asset Recovery Team v0.1.0 - Initial STS2 Resource Recovery Workflow
```

`snapshot/*` tags are repo-wide point-in-time checkpoints and are not stable releases. `release/*/vX.Y.Z` tags identify a completed monorepo unit. A release tag and a snapshot tag may point to the same commit when the release completion and repo checkpoint are intentionally the same point in history.
