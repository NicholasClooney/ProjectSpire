# TODOs

## App UI

- [ ] #medium Add a relics tab.
- [ ] #medium Replace character names in the dropdown with icons from the game's card library screen.
- [ ] #hard Investigate which fonts Slay the Spire uses, whether they are all Koreon or include other fonts, and whether those fonts are free to use.

## Card Parser Localization

- [ ] #medium Add localized card data versions so generated cards can coexist per l11n language instead of overwriting the default English output.
- [ ] #medium Update `Lab/parsers/card_parser.py` to walk every available l11n folder, produce card data for each language, and make `cards` a symlink to the `eng` l11n output.

## DONE

## App UI

- [x] #medium Add a card details view with a `View Upgrades` button.
- [x] #medium Add card keyword rendering in the UI, including cases like Ascender's Bane.
- [x] #medium Register approved app fonts with SwiftUI so standard `.font(...)` usage can pick up the theme without specifying custom font names everywhere.
- [x] #hard Add light and dark app themes inspired by Slay the Spire, with shared semantic colors for app chrome and filter controls.

## Card Parser v0.2.0

- [x] #easy Add card pool to the parsed card models
- [x] #easy Fix parsed card models have duplicated power dynamic vars
- [x] #easy Fix card parser handling upgrade energy cost reduction

### Asset Recovery Team v0.1.0

Tasks related to recovering assets from sts2.pck file.

1. [x] #medium set up gdre tools in path & set up recover script & git ignore so we don't import all assets / data into the repo. only import necessary ones.
2. [x] Let's start with localization data first.

- [x] #hard Find a solution to include necessary assets (images / ui elements) recovered from sts2.pck file in the repo... (also need to be not duped by the app project...) while keeping the size relatively small...
