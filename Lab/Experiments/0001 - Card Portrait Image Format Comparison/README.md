# Card Portrait Image Format Comparison

Compares original STS2 card portrait PNGs against lossless WebP and lossy WebP at qualities 95, 85, 75, and 60.

Samples are selected from `Lab/unpacked/images/packed/card_portraits`: 4 large files, 4 medium files, and 4 small files by source PNG byte size.

Sizes in this report are logical file sizes from `stat`, shown as decimal KB plus exact bytes. Disk usage tools may report slightly larger allocated size because APFS rounds storage to filesystem blocks.

Open `index.html` to visually compare the variants. Raw measurements are in `report.json`.

## Summary Table

| Bucket | Source | Dimensions | PNG | Lossless | Q95 | Q85 | Q75 | Q60 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| large | `Lab/unpacked/images/packed/card_portraits/curse/beta/spore_mind.png` | 1000x760 | 859.9 KB (859,863 B) (100.0%) | 520.4 KB (520,444 B) (60.5%) | 121.0 KB (121,026 B) (14.1%) | 57.5 KB (57,458 B) (6.7%) | 38.7 KB (38,706 B) (4.5%) | 32.0 KB (31,980 B) (3.7%) |
| large | `Lab/unpacked/images/packed/card_portraits/curse/beta/greed.png` | 1000x760 | 850.1 KB (850,149 B) (100.0%) | 497.2 KB (497,242 B) (58.5%) | 113.3 KB (113,288 B) (13.3%) | 55.3 KB (55,322 B) (6.5%) | 35.7 KB (35,706 B) (4.2%) | 29.7 KB (29,692 B) (3.5%) |
| large | `Lab/unpacked/images/packed/card_portraits/defect/white_noise.png` | 1000x760 | 841.5 KB (841,454 B) (100.0%) | 477.2 KB (477,228 B) (56.7%) | 193.5 KB (193,538 B) (23.0%) | 122.6 KB (122,558 B) (14.6%) | 89.1 KB (89,120 B) (10.6%) | 75.5 KB (75,458 B) (9.0%) |
| large | `Lab/unpacked/images/packed/card_portraits/token/beta/giant_rock.png` | 668x508 | 820.3 KB (820,289 B) (100.0%) | 625.8 KB (625,766 B) (76.3%) | 159.4 KB (159,414 B) (19.4%) | 86.1 KB (86,062 B) (10.5%) | 47.2 KB (47,250 B) (5.8%) | 33.8 KB (33,820 B) (4.1%) |
| medium | `Lab/unpacked/images/packed/card_portraits/colorless/tag_team.png` | 1000x760 | 388.4 KB (388,396 B) (100.0%) | 251.8 KB (251,822 B) (64.8%) | 133.0 KB (133,026 B) (34.3%) | 81.7 KB (81,728 B) (21.0%) | 58.4 KB (58,426 B) (15.0%) | 50.5 KB (50,522 B) (13.0%) |
| medium | `Lab/unpacked/images/packed/card_portraits/defect/skim.png` | 1000x760 | 354.3 KB (354,262 B) (100.0%) | 216.6 KB (216,600 B) (61.1%) | 85.6 KB (85,554 B) (24.1%) | 48.4 KB (48,418 B) (13.7%) | 33.6 KB (33,620 B) (9.5%) | 28.4 KB (28,392 B) (8.0%) |
| medium | `Lab/unpacked/images/packed/card_portraits/status/dazed.png` | 1000x760 | 321.2 KB (321,152 B) (100.0%) | 221.4 KB (221,362 B) (68.9%) | 84.6 KB (84,620 B) (26.3%) | 52.2 KB (52,194 B) (16.3%) | 37.8 KB (37,828 B) (11.8%) | 32.8 KB (32,822 B) (10.2%) |
| medium | `Lab/unpacked/images/packed/card_portraits/defect/rocket_punch.png` | 1000x760 | 276.1 KB (276,146 B) (100.0%) | 173.5 KB (173,518 B) (62.8%) | 81.3 KB (81,262 B) (29.4%) | 49.4 KB (49,400 B) (17.9%) | 35.4 KB (35,354 B) (12.8%) | 30.3 KB (30,328 B) (11.0%) |
| small | `Lab/unpacked/images/packed/card_portraits/necrobinder/beta/reap.png` | 668x508 | 4.3 KB (4,312 B) (100.0%) | 978 B (978 B) (22.7%) | 6.8 KB (6,804 B) (157.8%) | 4.3 KB (4,328 B) (100.4%) | 3.4 KB (3,404 B) (78.9%) | 3.0 KB (3,028 B) (70.2%) |
| small | `Lab/unpacked/images/packed/card_portraits/regent/beta/pale_blue_dot.png` | 1000x760 | 4.8 KB (4,805 B) (100.0%) | 132 B (132 B) (2.7%) | 1.5 KB (1,472 B) (30.6%) | 1.5 KB (1,458 B) (30.3%) | 1.5 KB (1,452 B) (30.2%) | 1.5 KB (1,452 B) (30.2%) |
| small | `Lab/unpacked/images/packed/card_portraits/colorless/beta/ultimate_defend.png` | 668x508 | 5.1 KB (5,091 B) (100.0%) | 1.4 KB (1,384 B) (27.2%) | 10.8 KB (10,794 B) (212.0%) | 7.1 KB (7,132 B) (140.1%) | 5.3 KB (5,336 B) (104.8%) | 4.7 KB (4,684 B) (92.0%) |
| small | `Lab/unpacked/images/packed/card_portraits/colorless/beta/rend.png` | 668x508 | 5.9 KB (5,875 B) (100.0%) | 1.6 KB (1,560 B) (26.6%) | 13.6 KB (13,578 B) (231.1%) | 9.4 KB (9,392 B) (159.9%) | 7.3 KB (7,256 B) (123.5%) | 6.3 KB (6,330 B) (107.7%) |
