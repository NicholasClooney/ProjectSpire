# Asset Recovery Team v0.1.0 Release

Date: 2026-05-05

Project areas: `Lab/`, `Documentation/`, release tags, GitHub Releases

## Summary

Create a release tag and GitHub Release page for the completed Asset Recovery Team v0.1.0 work.

The release tag should point to the same commit as `snapshot/2026-05-01`:

```text
a1b6e9df7cf652533092cc4f8aa9196dbffd9c0a
```

That commit documents the initial STS2 resource recovery workflow.

## Tag

Use the monorepo release tag convention:

```text
release/<component-or-feature-slug>/vX.Y.Z
```

For this release:

```text
release/asset-recovery-team/v0.1.0
```

Create it as an annotated tag:

```sh
git tag -a release/asset-recovery-team/v0.1.0 a1b6e9df7cf652533092cc4f8aa9196dbffd9c0a \
  -m "Asset Recovery Team v0.1.0" \
  -m "Marks completion of the initial STS2 resource recovery workflow." \
  -m "Release contents:" \
  -m "- Added reproducible recovery and extraction workflow for selected STS2 resources." \
  -m "- Added curated tracked resources under Lab/resources from the ignored Lab/unpacked source tree." \
  -m "- Documented WebP q85 image conversion and Git LFS tracking decisions."
```

Push only the release tag:

```sh
git push origin release/asset-recovery-team/v0.1.0
```

## Release page

Create a GitHub Release page for the pushed tag.

Use this title:

```text
Project Spire - Asset Recovery Team v0.1.0 - Initial STS2 Resource Recovery Workflow
```

Use mostly bullet points in the description:

```markdown
- Marks completion of the initial STS2 resource recovery workflow.
- Adds reproducible recovery of the installed Slay the Spire 2 PCK into ignored local `Lab/unpacked/`.
- Adds allowlist-driven extraction into tracked `Lab/resources/`.
- Copies localization resources and converts card portrait PNGs to WebP q85.
- Records generated output in `Lab/resources/manifest.json`.
- Documents WebP q85 and Git LFS tracking decisions.

Notes:

- `Lab/unpacked/` remains local-only and ignored.
- Expand `Lab/resources.allowlist.yaml` when new app or research work needs additional recovered assets.
```

## Verification

Confirm the tag exists and points to the intended commit:

```sh
git show --no-patch --format=fuller release/asset-recovery-team/v0.1.0
```

Confirm the pushed tag is visible on origin:

```sh
git ls-remote --tags origin release/asset-recovery-team/v0.1.0
```

Confirm the GitHub Release page exists:

```sh
gh release view release/asset-recovery-team/v0.1.0
```

## Assumptions

- `asset-recovery-team` is the Git-safe slug for `Asset Recovery Team`.
- `v0.1.0` is the first functional release of the resource recovery workflow.
- The release and snapshot tags intentionally point to the same commit.
