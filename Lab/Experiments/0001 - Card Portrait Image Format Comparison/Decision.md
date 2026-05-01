# Resource Image Conversion Decision

Date: 2026-05-01

Project areas: `Lab/`, recovered STS2 resources, Git LFS

## Decision

Tracked recovered card portrait images will be converted from PNG to WebP using `cwebp` quality 85.

The initial extraction workflow applies this profile to:

```text
Lab/unpacked/images/packed/card_portraits/**/*.png
```

and writes the converted assets under:

```text
Lab/resources/images/packed/card_portraits/**/*.webp
```

## Context

The comparison experiment in `Lab/Experiments/0001 - Card Portrait Image Format Comparison/` tested original PNG, lossless WebP, and lossy WebP at qualities 95, 85, 75, and 60 across large, medium, and small card portrait samples.

Across the sampled set, WebP q85 reduced logical file size to about 12.2% of the original PNG total while preserving enough visual quality for current research and UI import experiments. Lossless WebP was materially larger at about 63.1% of the original PNG total.

## Consequences

- `Lab/resources/**/*.webp` assets are tracked through Git LFS via the repository `*.webp` rule.
- The tracked resource subset is optimized for practical repo size and visual inspection, not archival byte-for-byte preservation.
- The ignored `Lab/unpacked/` directory remains the source of truth for original recovered PNGs when exact originals are needed.

## Open Questions

- Whether future app/runtime consumers need a different quality profile for specific asset categories.
- Whether non-card-portrait assets should use the same q85 profile or have separate profiles.
