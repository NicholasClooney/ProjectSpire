---
name: decompile-sts2
description: Decompile the local Slay the Spire 2 DLL into C# source. Use when the user wants to decompile the game, regenerate decompiled source, or update to a new game version.
---

# Decompile STS2

Run the decompile script:

```bash
scripts/decompile-sts2.sh
```

Requires `ilspycmd` on PATH (`dotnet tool install --global ilspycmd`). The script auto-detects the game version from `release_info.json` and outputs to `decompiled/<version>/`.

## Options

- `--dll PATH` — override the DLL path (default: Steam macOS ARM64 install)
- `--out DIR` — override output directory
- `--clean` — wipe the output directory before decompiling
- `STS2_DLL_PATH` / `STS2_DECOMPILED_DIR` — env var equivalents

## Known failure modes

- **`ilspycmd` not found**: run `dotnet tool install --global ilspycmd` and ensure `~/.dotnet/tools` is on PATH
- **DLL not found**: pass `--dll PATH` or set `STS2_DLL_PATH` if Steam library is in a non-default location
- **Output directory not empty**: pass `--clean` to wipe and re-decompile
- **Version shows `unknown`**: `release_info.json` not found — verify the DLL path points to the real Steam install, not a copy
