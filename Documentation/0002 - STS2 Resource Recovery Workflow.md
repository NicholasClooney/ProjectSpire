# STS2 Resource Recovery Workflow

Date: 2026-05-01

Project areas: `Lab/`, recovered STS2 resources, Git LFS

## Purpose

ProjectSpire keeps a reproducible workflow for recovering selected Slay the Spire 2 package resources without committing the full recovered game dump.

The full recovered resource tree lives locally at:

```text
Lab/unpacked/
```

That directory is ignored by Git. The curated, tracked subset lives at:

```text
Lab/resources/
```

## Working Principles

- Keep the full recovered game dump local and ignored. `Lab/unpacked/` is the local source of truth, not repo history.
- Track only curated resources that have a current use. Start small and expand the allowlist when a concrete research or app need appears.
- Make extraction reproducible. Tracked resources should be generated from scripts and config, not manual copy state.
- Prefer readable tooling. Use Python for the recovery/extraction scripts because it is easier to maintain and understand in this repo.
- Keep binary assets repo-friendly. Use WebP for practical image size reduction and Git LFS for tracked binary resources.
- Preserve original assets locally. Lossy tracked resources are acceptable because original PNGs remain available in ignored `Lab/unpacked/`.
- Make decisions discoverable. Root decisions stay short in `Documentation/0000 - Project Decisions.md`; detailed rationale should live near supporting experiments.
- Separate workflow, evidence, and generated output. Scripts/config, experiments/docs, and generated resources should be committed separately.

## Implemented Workflow

Godot RE Tools is installed at:

```text
/Applications/Godot RE Tools.app/Contents/MacOS/Godot RE Tools
```

A local PATH symlink points to it:

```text
~/.bin/gdretools
```

Recover the installed PCK into the ignored local source tree:

```text
Lab/scripts/recover-sts2-pck.py --clean
```

Extract the tracked subset:

```text
Lab/scripts/extract-sts2-resources.py --clean
```

The extractor reads:

```text
Lab/resources.allowlist.yaml
```

and writes:

```text
Lab/resources/
Lab/resources/manifest.json
```

## Initial Allowlist

The first tracked subset is intentionally small:

- `localization/**`
- `images/packed/card_portraits/**/*.png`, converted to WebP q85

The workflow currently avoids broad recovered resource categories such as root JSON, Godot scenes, materials, themes, shaders, and sidecar files like `.import` until there is a concrete need for them.

## Image Conversion Decision

Card portrait PNGs are converted to WebP q85.

This decision is recorded in:

```text
Documentation/0000 - Project Decisions.md
Lab/Experiments/0001 - Card Portrait Image Format Comparison/
```

The experiment compared PNG, lossless WebP, and lossy WebP at multiple quality levels. WebP q85 was selected because it gave a large size reduction while preserving enough visual quality for current research and UI import work.

## Git Tracking

`Lab/unpacked/` is ignored.

Generated WebP files are tracked through Git LFS via:

```text
*.webp filter=lfs diff=lfs merge=lfs -text
```

Existing PNG and TTF LFS rules remain in place.

## Current Output

The first generated `Lab/resources/` output contains:

- copied localization files
- q85 WebP card portraits
- `manifest.json` describing copied and converted files

At generation time, the resource folder was about `54M`, with card portrait WebP output about `43M` and localization about `11M`.

## Future Additions

Add new resources by editing `Lab/resources.allowlist.yaml`, then regenerating `Lab/resources/`.

Likely future allowlist candidates:

- card frames and templates
- relic images
- power icons
- potion images
- atlas metadata if packed sprite coordinates become necessary
