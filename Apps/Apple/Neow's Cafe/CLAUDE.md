# Neow's Cafe

This folder contains the iOS SwiftUI app for experimenting with STS2 card rendering.

## Project Layout

- `Project.swift` - Tuist project definition.
- `Neow's Cafe/` - app sources and resources.
- `Neow's Cafe/Sources/` - Swift source files.
- `Neow's Cafe/Resources/Assets.xcassets/` - image assets.
- `Neow's Cafe/Resources/Fonts/` - bundled fonts.
- `Derived/` - generated Tuist/Xcode files. Do not hand-edit generated files.

## Tuist

After changing `Project.swift`, resources, generated-file inputs, or target configuration, regenerate the project:

```sh
tuist generate
```

## Building

When compiling with `xcodebuild`, pipe through `xcbeautify` to keep output compact and context-efficient:

```sh
xcodebuild \
  -workspace "Neow's Cafe.xcworkspace" \
  -scheme "Neow's Cafe" \
  -destination 'generic/platform=iOS Simulator' \
  build | xcbeautify
```

Run this from `Apps/Apple/Neow's Cafe`.

If raw build output is needed to diagnose a specific issue, use `xcodebuild` without `xcbeautify` only for that focused investigation.

## Implementation Notes

- Prefer SwiftUI for app UI.
- Keep card rendering constants close to the card view until there is enough repetition to justify extracting layout data.
- Use generated asset and font accessors where available instead of stringly-typed resource names.
- Do not edit generated Tuist files directly; update the source inputs and regenerate.
