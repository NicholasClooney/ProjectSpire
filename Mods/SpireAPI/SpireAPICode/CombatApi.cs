// This class is the future SpireAPI layer: pure game-state access, no HTTP concerns.
// When SpireRESTAPI becomes a separate mod, this moves there as a dependency.

using MegaCrit.Sts2.Core.Combat;

namespace SpireAPI.SpireAPICode;

public static class CombatApi
{
    public record CardInfo(string Id, int EnergyCost, string TargetType, bool CanPlay, bool IsUpgraded);
    public record CreatureInfo(uint CombatId, string Name, int Hp, int MaxHp, int Block, bool IsAlive);
    public record CombatStateInfo(
        bool IsInProgress,
        bool IsPlayPhase,
        int Round,
        int Energy,
        int MaxEnergy,
        List<CardInfo> Hand,
        List<CreatureInfo> Enemies,
        string? Message = null
    );

    public static CombatStateInfo GetCombatState()
    {
        var cm = CombatManager.Instance;
        var state = cm.DebugOnlyGetState();

        if (!cm.IsInProgress || state is null)
            return new CombatStateInfo(false, false, 0, 0, 0, [], [], "Not in combat");

        var player = state.Players[0];
        var combatState = player.PlayerCombatState;

        var hand = combatState?.Hand.Cards
            .Select(c => new CardInfo(
                c.Id.Entry,
                c.EnergyCost.GetResolved(),
                c.TargetType.ToString(),
                c.CanPlay(),
                c.IsUpgraded))
            .ToList() ?? [];

        var enemies = state.Enemies
            .Where(e => e.CombatId.HasValue)
            .Select(e => new CreatureInfo(
                e.CombatId!.Value,
                e.Name,
                e.CurrentHp,
                e.MaxHp,
                e.Block,
                e.IsAlive))
            .ToList();

        return new CombatStateInfo(
            true,
            cm.IsPlayPhase,
            state.RoundNumber,
            combatState?.Energy ?? 0,
            combatState?.MaxEnergy ?? 0,
            hand,
            enemies
        );
    }
}
