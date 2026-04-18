# 0001 - Map Markers

> **Note:** This document was written against a previous game version. Logic may have changed.

## Data Model

**`MapPoint`** is the logical node. It stores:
- `MapCoord` (column 0-6, row 0-N)
- `MapPointType` enum: `Monster`, `Elite`, `Boss`, `Shop`, `Treasure`, `RestSite`, `Unknown`, `Ancient`
- Parent/child relationships defining the branching path graph
- A `MapPointState`: `None`, `Travelable`, `Traveled`, or `Untravelable`

## Map Generation (`StandardActMap.cs`)

1. A 7-column grid is built. Start is col 3 row 0, boss is col 3 bottom row.
2. `PathGenerate()` walks downward from the start, randomly choosing columns and creating children to form branching paths.
3. `AssignPointTypes()` fills in room types based on per-act `MapPointTypeCounts`, with placement restrictions (e.g. no elites adjacent to each other, no elites in the first rows, etc.).
4. Post-processing: `MapPathPruning`, `CenterGrid`, `SpreadAdjacentMapPoints`, `StraightenPaths`.

## Visual Nodes (`NMapPoint`, `NNormalMapPoint`, `NBossMapPoint`)

Each `MapPoint` gets a Godot scene node counterpart. The nodes handle:
- **Input** via `OnRelease()` - checks `IsTravelable` before forwarding to `NMapScreen.OnMapPointSelectedLocally()`
- **Color state** - transitions between travelable (colored), traveled (white), and untravelable (half-transparent) using tweens
- A multiplayer vote container overlay for co-op voting on destinations

## Traversal (`TravelToMapCoord()` in `NMapScreen.cs`)

When a node is selected:
1. The player animates along the path to the destination.
2. Intermediate nodes get "tick" marks and flip to `MapPointState.Traveled`.
3. `RecalculateTravelability()` runs after each move, marking only the children of the new current position as `Travelable`.
4. The destination room is loaded and the encounter begins.

The key invariant: only nodes that are direct children of your current position can ever be `Travelable`, enforcing movement along the pre-generated paths.
