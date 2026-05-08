# 0011 - Card Keyword Text Investigation

## 2026-05-08 - Keyword Pipeline Devlog

**Context:** The user asked for a devlog covering work from the session that had not yet been documented in the devlog history.

**User Direction:** The user wanted durable documentation for anything worked on but not documented elsewhere yet.

**Agent Response:** The agent reviewed existing devlogs and added a new devlog for the card keyword pipeline from source/parser through catalog, Swift rendering, text fitting, and keyword search.

**User Feedback:** No correction during this step.

**Outcome:** `Documentation/Devlogs/0005 - Card Keyword Pipeline And Neows Cafe Rendering.md` now records the source findings, parser/catalog/app commits, verification, and future work notes for keyword rendering.

**Carry Forward:** When a feature spans parser output, generated catalog data, and app rendering, keep a human-readable devlog that ties source findings, schema shape, app paths, commits, and verification together.

## 2026-05-08 - Card Text Scaling And Keyword Search

**Context:** The user showed a Bombardment render where long rules text was truncated and asked to include keywords in card search.

**User Direction:** The user wanted long descriptions to fit better in the fixed card text box and wanted `CardFilter` to match keyword text.

**Agent Response:** The agent changed the card rules render to one styled, scalable `AttributedString` text block and extended search matching to keyword `id` and `title`.

**User Feedback:** No correction during this step.

**Outcome:** Longer card rules can shrink within the card text area while preserving keyword coloring, and searching for a keyword such as `exhaust` matches cards that carry that keyword. Build and tests pass.

**Carry Forward:** Keep rules text as a single scalable rendered block when fitting within the in-game card frame; splitting description and keywords into independent text views makes truncation harder to control.

## 2026-05-08 - Neow's Cafe Keyword Rendering

**Context:** The user asked to add parsed card keywords to Neow's Cafe's Swift card model and card UI.

**User Direction:** The user wanted keyword data carried through `Card.swift` and rendered in `CardView.swift`, with the existing parser work already providing before/after placement.

**Agent Response:** The agent added `Card.Keyword` with placement metadata, decoded keyword summaries from the app catalog, regenerated the tracked catalog index with keyword fields, and rendered before-description and after-description keyword lines around the rules text.

**User Feedback:** No correction during this step.

**Outcome:** Neow's Cafe now receives `keywords` and `keywordPeriod` from `cards.index.json`, preserves keyword placement in the model, and displays localized keyword titles with the period in the card text box. The app build and catalog decoder test pass.

**Carry Forward:** Keep the app-facing catalog summary aligned with the parser's resolved display schema; SwiftUI should render keyword title lines from structured placement metadata instead of concatenating them into the card description upstream.

## 2026-05-08 - Keyword Parser Schema Implementation

**Context:** The user asked to save the keyword parser schema plan under `Documentation/Plans/` and then implement it.

**User Direction:** The user wanted the parser updated to extract keywords with before/after placement and emit localized keyword data in `resolved`.

**Agent Response:** The agent created `Documentation/Plans/0004 - Card Keyword Parser Schema.md`, implemented parser schema `0.2.4`, regenerated `Lab/data/v0.103.2/cards`, updated the coverage audit, and refreshed Lab documentation.

**User Feedback:** The user clarified that `displayText` was unnecessary when title and period are available, and asked whether upgrades can add or remove keywords; source inspection showed direct `OnUpgrade()` keyword mutations exist.

**Outcome:** `raw.keyword_upgrades` now records direct `OnUpgrade()` keyword adds/removes, `resolved.keyword_period` carries localized period text, and `resolved.base/upgraded.keywords` carries localized keyword objects with `id`, `placement`, `title`, and `description`. The audit now checks base keyword membership and keyword upgrade deltas; targeted examples and the audit pass with zero errors.

**Carry Forward:** Keep base keyword membership and upgrade keyword mutations separate. For rendering, compose visible keyword lines from structured `resolved.*.keywords` plus `resolved.keyword_period`, not from `resolved.description.plain`.

## 2026-05-08 - Keyword Placement Extraction

**Context:** The user asked whether after-description keywords follow a heuristic and whether a keyword can appear both before and after the card description.

**User Direction:** The user wanted a one-off Python extraction to list all card keywords and classify each as before-description or after-description.

**Agent Response:** The agent inspected `CardKeyword.cs`, `CardKeywordOrder.cs`, and `card_keywords.json`, then ran a Python parser over the decompiled constants.

**User Feedback:** The user asked to document the findings in `Lab/Documentation`.

**Outcome:** The game uses explicit arrays: `Ethereal`, `Sly`, `Retain`, `Innate`, and `Unplayable` are before-description keywords; `Exhaust` and `Eternal` are after-description keywords. There is no overlap and no displayed keyword enum is missing from the arrays. The findings are now documented in `Lab/Documentation/0014 - Card Keywords.md`, with a cross-reference from `Lab/Documentation/0006 - Card Parser.md`.

**Carry Forward:** Model keyword placement as source-derived enum metadata from `CardKeywordOrder`, not as a heuristic based on keyword meaning or localization text.

## 2026-05-08 - Card Keyword Text Investigation

**Context:** The user compared Neow's Cafe card renders against in-game screenshots for `Ascender's Bane` and `Dazed`, where the app showed blank rules text while the game showed keyword text.

**User Direction:** The user asked how the game represents those card keywords and whether ProjectSpire's card parser captures them today.

**Agent Response:** The agent inspected decompiled card models, keyword ordering code, parser output, catalog generation, and the Swift app model/render path.

**User Feedback:** The user noted up front that the app does not yet have UI logic to support keyword rendering.

**Outcome:** The game represents keyword-only text through `CardModel.CanonicalKeywords`/`Keywords`, then composes keyword lines in `GetDescriptionForPile`; ProjectSpire's parser captures the keyword set in raw card JSON, but the app-facing catalog and Swift model drop it and only render `description`.

**Carry Forward:** Treat keyword text as structured card display data, not fallback description text. Preserve keyword identity and game display ordering in the catalog/app model before adding SwiftUI rendering.
