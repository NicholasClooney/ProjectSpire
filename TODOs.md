# TODOs

## Card Parser Localization

- [ ] #medium Add localized card data versions so generated cards can coexist per l11n language instead of overwriting the default English output.
- [ ] #medium Update `Lab/parsers/card_parser.py` to walk every available l11n folder, produce card data for each language, and make `cards` a symlink to the `eng` l11n output.

## DONE

## Card Parser v0.2.0

- [x] #easy Add card pool to the parsed card models
- [x] #easy Fix parsed card models have duplicated power dynamic vars
- [x] #easy Fix card parser handling upgrade energy cost reduction

### Asset Recovery Team v0.1.0

Tasks related to recovering assets from sts2.pck file.

1. [x] #medium set up gdre tools in path & set up recover script & git ignore so we don't import all assets / data into the repo. only import necessary ones.
2. [x] Let's start with localization data first.

- [x] #hard Find a solution to include necessary assets (images / ui elements) recovered from sts2.pck file in the repo... (also need to be not duped by the app project...) while keeping the size relatively small...
