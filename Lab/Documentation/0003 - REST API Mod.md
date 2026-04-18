# 0003 - REST API Mod: Controlling Combat via HTTP

> **Note:** This document was written against a previous game version. Logic may have changed.

This doc covers the concrete classes, access paths, and action patterns needed to build a REST API mod for STS2 that can read game state and execute player actions (play card, use potion, end turn).

---

## Mod Entry Point

Mods are `.pck` files dropped in `./mods/` next to the game binary. `ModManager.Initialize()` scans for them at startup.

If the assembly contains a class decorated with `[ModInitializer("MethodName")]`, that static method is called. Otherwise `Harmony.PatchAll()` runs automatically.

```csharp
[ModInitializer("Initialize")]
public class StsApiMod
{
    public static void Initialize()
    {
        // Called once at game startup — start your HttpListener here
    }
}
```

`ModInitializerAttribute` lives in `MegaCrit.Sts2.Core.Modding`.

---

## Reaching the Action Queue

All game actions (card play, potion use, end turn) are enqueued through:

```csharp
RunManager.Instance.ActionQueueSynchronizer.RequestEnqueue(action);
```

- `RunManager.Instance` — static singleton (`MegaCrit.Sts2.Core.Runs.RunManager`)
- `ActionQueueSynchronizer` — property on `RunManager`, type `ActionQueueSynchronizer` (`MegaCrit.Sts2.Core.GameActions.Multiplayer`)
- `RequestEnqueue(GameAction)` — queues the action; handles multiplayer sync and play-phase gating automatically. Actions typed `CombatPlayPhaseOnly` are deferred if the player isn't in their play phase.

---

## Getting the Local Player

```csharp
// All players in the current run
IReadOnlyList<Player> players = RunManager.Instance.State.Players;

// In singleplayer there is exactly one player
Player player = players[0];
```

`Player` is in `MegaCrit.Sts2.Core.Entities.Players`. Key members used in action construction:

| Member | Type | Notes |
|--------|------|-------|
| `NetId` | `ulong` | Used as `OwnerId` in all actions |
| `Creature` | `Creature` | The player's combat creature |
| `Creature.CombatState` | `PlayerCombatState?` | Null outside combat |
| `PotionSlots` | `IReadOnlyList<PotionModel?>` | Indexed slots; null = empty slot |
| `Potions` | `IEnumerable<PotionModel>` | Non-null potions only |
| `GetPotionAtSlotIndex(int)` | `PotionModel?` | Used internally by `UsePotionAction` |
| `GetPotionSlotIndex(PotionModel)` | `int` | Reverse lookup |

---

## Reading Combat State

```csharp
CombatManager cm = CombatManager.Instance; // MegaCrit.Sts2.Core.Combat

bool active       = cm.IsInProgress;
bool playerPhase  = cm.IsPlayPhase;
CombatState state = cm.State;             // null outside combat
```

### CombatState members

| Member | Type | Notes |
|--------|------|-------|
| `Enemies` | `IReadOnlyList<Creature>` | All enemies |
| `HittableEnemies` | `IReadOnlyList<Creature>` | Valid targets |
| `Allies` | `IReadOnlyList<Creature>` | Player-side creatures |
| `Players` | `IReadOnlyList<Player>` | All players in combat |
| `RoundNumber` | `int` | 1-indexed; required for end-turn action |
| `GetCreature(uint? combatId)` | `Creature?` | Resolve target by ID |

### Creature members (enemies and player creature alike)

| Member | Type | Notes |
|--------|------|-------|
| `CombatId` | `uint?` | Assigned when spawned into combat |
| `CurrentHp` | `int` | |
| `MaxHp` | `int` | |
| `Block` | `int` | |
| `Name` | `string` | Localized display name |
| `Side` | `CombatSide` | `Enemy` or `Player` |
| `IsAlive` | `bool` | `CurrentHp > 0` |
| `IsMonster` | `bool` | |
| `IsPlayer` | `bool` | |
| `Powers` | (via `_powers`) | List of active `PowerModel` |

### PlayerCombatState members

Access via `player.Creature.CombatState` (type `PlayerCombatState`):

| Member | Type | Notes |
|--------|------|-------|
| `Hand` | `CardPile` | Playable cards |
| `DrawPile` | `CardPile` | Cards to draw |
| `DiscardPile` | `CardPile` | Discarded |
| `ExhaustPile` | `CardPile` | Exhausted |
| `Energy` | `int` | Current energy |
| `MaxEnergy` | `int` | Max for this turn |
| `Stars` | `int` | Star resource |
| `HasCardsToPlay()` | `bool` | Any playable card in hand |

Each `CardPile` exposes `IReadOnlyList<CardModel> Cards`.

### CardModel identification

| Member | Type | Notes |
|--------|------|-------|
| `Id` | `ModelId` | Has `.Entry` string — the stable card key |
| `EnergyCost` | `CardEnergyCost` | |
| `TargetType` | `TargetType` | `TargetedNoCreature`, `AnyEnemy`, `AnyAlly` |
| `IsUpgraded` | `bool` | |
| `CurrentUpgradeLevel` | `int` | |
| `CanPlay()` | `bool` | Full playability check |
| `IsValidTarget(Creature?)` | `bool` | Check before passing target |
| `Pile` | `CardPile?` | Which pile the card is in right now |

---

## Playing a Card

```csharp
// Simplest constructor — resolves owner from cardModel.Owner internally
var action = new PlayCardAction(cardModel, target); // target = null for no-target cards
RunManager.Instance.ActionQueueSynchronizer.RequestEnqueue(action);
```

**`PlayCardAction`** (`MegaCrit.Sts2.Core.GameActions`)

- `ActionType` = `CombatPlayPhaseOnly` — queued, not executed, outside player phase
- Internally validates `CanPlay()` and `IsValidTarget()` during `ExecuteAction()`
- Calls `SpendResources()` then `CardModel.OnPlayWrapper()`

To find a card to play:

```csharp
CardPile hand = player.Creature.CombatState!.Hand;

// By Id.Entry string
CardModel? card = hand.Cards.FirstOrDefault(c => c.Id.Entry == "Strike");

// Pass a target enemy
Creature? target = CombatManager.Instance.State!.HittableEnemies.FirstOrDefault();
```

---

## Using a Potion

```csharp
// Simplest constructor
var action = new UsePotionAction(potionModel, target, isCombatInProgress: true);
RunManager.Instance.ActionQueueSynchronizer.RequestEnqueue(action);
```

**`UsePotionAction`** (`MegaCrit.Sts2.Core.GameActions`)

- `ActionType` = `CombatPlayPhaseOnly` when `isCombatInProgress = true`, else `NonCombat`
- Resolves potion from `player.GetPotionAtSlotIndex(PotionIndex)` during execution

To find a potion:

```csharp
// Iterate non-null slots
foreach (var potion in player.Potions)
{
    // potion.Id.Entry  — stable potion key
    // potion.Owner     — the Player
}
```

---

## Ending the Turn

```csharp
int round = player.Creature.CombatState!.RoundNumber;
var action = new EndPlayerTurnAction(player, round);
RunManager.Instance.ActionQueueSynchronizer.RequestEnqueue(action);
```

**`EndPlayerTurnAction`** (`MegaCrit.Sts2.Core.GameActions`)

- `ActionType` = `CombatPlayPhaseOnly`
- Internally calls `PlayerCmd.EndTurn(player, canBackOut: true)` only if the stored round number still matches the current round (prevents stale queued end-turns from firing in the wrong round)

The `UndoEndPlayerTurnAction` exists with the same constructor signature if undo is needed.

---

## Thread Safety: HTTP Thread -> Godot Main Thread

The HTTP server runs on a background thread. All game state mutations must happen on the Godot main thread. The safe pattern:

```csharp
// From the HTTP handler thread:
Godot.Engine.GetMainLoop().CallDeferred(
    Godot.Node.MethodName._Process,
    Godot.Callable.From(() =>
    {
        RunManager.Instance.ActionQueueSynchronizer.RequestEnqueue(action);
    })
);
```

Reading state (querying `Hand.Cards`, `CombatState`, etc.) is generally safe from a background thread as long as no mutation occurs concurrently, but enqueuing actions must go through `CallDeferred` or an equivalent main-thread dispatch.

---

## Reading Relics

```csharp
IReadOnlyList<RelicModel> relics = player.Relics;

// Lookup helpers on Player
RelicModel? r  = player.GetRelicById(id);
T?          r2 = player.GetRelic<BurningBlood>(); // by concrete type
```

### RelicModel members

| Member | Type | Notes |
|--------|------|-------|
| `Id.Entry` | `string` | Stable relic key (e.g. `"BurningBlood"`) |
| `Title` | `LocString` | Localized display name; call `.GetFormattedText()` |
| `Description` | `LocString` | Static description text |
| `DynamicDescription` | `LocString` | Description with current variable values filled in |
| `Rarity` | `RelicRarity` | `Common`, `Uncommon`, `Rare`, `Shop`, `Ancient`, `Starter`, `Event`, `None` |
| `Status` | `RelicStatus` | See below |
| `ShowCounter` | `bool` | Whether this relic displays a numeric counter |
| `DisplayAmount` | `int` | The counter value (e.g. charges, turns remaining) |
| `StackCount` | `int` | Stack count for stackable relics; default 1 |
| `IsWax` | `bool` | Wax Seal variant |
| `IsMelted` | `bool` | Melted state — relic is inert |
| `IsUsedUp` | `bool` | Virtual; true when the relic has been fully consumed |
| `IsTradable` | `bool` | Whether it can be traded at merchant |
| `FloorAddedToDeck` | `int` | Which floor the player picked this up |
| `HasBeenRemovedFromState` | `bool` | True if relic was removed during the current run |
| `Owner` | `Player` | Owning player |

### RelicStatus enum

`MegaCrit.Sts2.Core.Entities.Relics.RelicStatus`

| Value | Shader effect | Meaning |
|-------|---------------|---------|
| `Normal` | No effect | Idle, ready |
| `Active` | Pulse glow | Currently triggering / activated this turn |
| `Disabled` | Greyed out ("used") | Spent for this turn / unavailable |

The `StatusChanged` event fires whenever `Status` changes — useful for reactive state snapshots.

### DynamicVars (per-relic counters)

Some relics store named numeric variables used in their description text (e.g. `"chargesLeft"`, `"turnsRemaining"`). These are exposed through `DynamicVarSet DynamicVars`. For a simple counter relic, `DisplayAmount` is the cleaner read.

### RelicRarity enum

`Common` < `Uncommon` < `Rare` < `Shop` < `Event` < `Ancient` < `Starter`

---

## Suggested Endpoints

| Method | Path | Action |
|--------|------|--------|
| `GET` | `/combat/state` | Energy, hand (id + name), enemies (id + hp + block), round |
| `GET` | `/combat/hand` | Full card list with CanPlay, TargetType, EnergyCost |
| `GET` | `/combat/potions` | Player's potion slots with id, name, index |
| `GET` | `/player/relics` | All relics: id, name, status, counter, rarity |
| `POST` | `/combat/play-card` | Body: `{ "cardId": "Strike", "targetCombatId": 1 }` |
| `POST` | `/combat/use-potion` | Body: `{ "slotIndex": 0, "targetCombatId": 1 }` |
| `POST` | `/combat/end-turn` | No body needed |

---

## Key Namespaces

| Namespace | Contents |
|-----------|----------|
| `MegaCrit.Sts2.Core.Runs` | `RunManager`, `RunState` |
| `MegaCrit.Sts2.Core.Combat` | `CombatManager`, `CombatState` |
| `MegaCrit.Sts2.Core.Entities.Players` | `Player`, `PlayerCombatState` |
| `MegaCrit.Sts2.Core.Entities.Creatures` | `Creature` |
| `MegaCrit.Sts2.Core.Models` | `CardModel`, `PotionModel`, `RelicModel` |
| `MegaCrit.Sts2.Core.GameActions` | `PlayCardAction`, `UsePotionAction`, `EndPlayerTurnAction` |
| `MegaCrit.Sts2.Core.GameActions.Multiplayer` | `ActionQueueSynchronizer` |
| `MegaCrit.Sts2.Core.Modding` | `ModManager`, `ModInitializerAttribute` |
