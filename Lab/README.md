# ProjectSpire - Lab

This is where we research and document findings from Slay the Spire 2.

## Audits

Audit scripts live in:

```text
Lab/audits/
```

For example, check whether generated card JSON still covers source patterns
recognized by the card parser:

```sh
python3 Lab/audits/card_parser_coverage.py --version v0.103.2
```

The audit exits non-zero for hard source-vs-JSON mismatches. Warnings identify
source API patterns that may deserve parser support.

## Asset recovery

The asset recovery workflow keeps the full recovered game dump out of Git while
tracking a curated subset that ProjectSpire uses for research and app work.

The ignored local source tree is:

```text
Lab/unpacked/
```

The tracked curated output is:

```text
Lab/resources/
```

The allowlist that controls what gets copied or converted is:

```text
Lab/resources.allowlist.yaml
```

### Prerequisites

- Slay the Spire 2 installed through Steam at the default macOS location, or a
  custom PCK path supplied with `--pck` or `STS2_PCK_PATH`.
- Godot RE Tools CLI available as `gdretools` on `PATH`, or supplied with
  `--gdretools` or `GDRETOOLS`.
- WebP tools available as `cwebp` on `PATH`.
- PyYAML available to Python 3 for reading the allowlist.

### Recover the local PCK

Run this from the repository root:

```sh
Lab/scripts/recover-sts2-pck.py --clean
```

By default, this recovers:

```text
~/Library/Application Support/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.app/Contents/Resources/Slay the Spire 2.pck
```

into:

```text
Lab/unpacked/
```

Useful overrides:

```sh
Lab/scripts/recover-sts2-pck.py --pck /path/to/Slay\ the\ Spire\ 2.pck --out Lab/unpacked --clean
GDRETOOLS=/path/to/gdretools Lab/scripts/recover-sts2-pck.py --clean
STS2_PCK_PATH=/path/to/Slay\ the\ Spire\ 2.pck Lab/scripts/recover-sts2-pck.py --clean
```

Without `--clean`, the script refuses to write into a non-empty output
directory.

### Extract tracked resources

After `Lab/unpacked/` exists, run:

```sh
Lab/scripts/extract-sts2-resources.py --clean
```

The extractor reads `Lab/resources.allowlist.yaml` and writes:

```text
Lab/resources/
Lab/resources/manifest.json
```

The current allowlist copies localization files and converts card portrait PNGs
to WebP q85. Add new tracked resources by editing the allowlist, then rerun the
extractor.

Useful overrides:

```sh
Lab/scripts/extract-sts2-resources.py --source Lab/unpacked --out Lab/resources --clean
Lab/scripts/extract-sts2-resources.py --allowlist Lab/resources.allowlist.yaml --clean
```

### Git tracking

`Lab/unpacked/` is ignored and should stay local. `Lab/resources/` is tracked
when the curated output is intentionally updated.

WebP resources are tracked through Git LFS. After regenerating resources, review
the manifest and changed files before committing:

```sh
git status --short Lab/resources Lab/resources.allowlist.yaml
git diff -- Lab/resources/manifest.json Lab/resources.allowlist.yaml
```

More context is documented in:

```text
Documentation/0002 - STS2 Resource Recovery Workflow.md
```
