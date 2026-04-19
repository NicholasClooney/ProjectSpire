using Godot;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Cards.Holders;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Screens.CardSelection;
using MegaCrit.Sts2.Core.Nodes.Screens.Overlays;
using MegaCrit.Sts2.Core.Nodes.Screens.ScreenContext;
using MegaCrit.Sts2.addons.mega_text;

namespace SpireAPI.SpireAPICode;

public static class CombatApi
{
    public record CardInfo(
        uint CombatCardIndex,
        string Id,
        string Name,
        int EnergyCost,
        string TargetType,
        bool CanPlay,
        bool IsUpgraded);
    public record CreatureInfo(uint CombatId, string Name, int Hp, int MaxHp, int Block, bool IsAlive);
    public record PlayCardRequest(uint CombatCardIndex, uint? TargetCombatId);
    public record PlayCardResult(bool Success, string Message);
    public record UiSelectableCardInfo(int ChoiceIndex, uint? CombatCardIndex, string Id, string Name, bool IsUpgraded);
    public record UiStateInfo(
        bool HasActiveUi,
        string? CurrentScreenClass,
        string? CurrentScreenType,
        string? InteractionKind,
        string? Prompt,
        string? HandSelectionMode,
        List<UiSelectableCardInfo> SelectableCards,
        string? Message = null);
    public record SelectHandCardRequest(uint CombatCardIndex);
    public record SelectHandCardResult(bool Success, string Message);
    public record SelectUiCardRequest(int ChoiceIndex);
    public record SelectUiCardResult(bool Success, string Message);
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
                NetCombatCard.FromModel(c).CombatCardIndex,
                c.Id.Entry,
                c.Title,
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

    public static PlayCardResult PlayCard(PlayCardRequest request, string? logContext = null)
    {
        var cm = CombatManager.Instance;
        var state = cm.DebugOnlyGetState();

        MainFile.Logger.Info(
            $"{FormatLogContext(logContext)}play-card request received. combatCardIndex={request.CombatCardIndex}, targetCombatId={request.TargetCombatId?.ToString() ?? "null"}");

        if (!cm.IsInProgress || state is null)
        {
            MainFile.Logger.Info($"{FormatLogContext(logContext)}rejecting play-card request because combat is not in progress");
            return new PlayCardResult(false, "Not in combat");
        }

        if (!cm.IsPlayPhase)
        {
            MainFile.Logger.Info($"{FormatLogContext(logContext)}rejecting play-card request because combat is not in play phase");
            return new PlayCardResult(false, "Not in play phase");
        }

        var player = state.Players[0];
        var combatState = player.PlayerCombatState;
        var hand = combatState?.Hand.Cards;

        if (hand is null)
        {
            MainFile.Logger.Info($"{FormatLogContext(logContext)}rejecting play-card request because the local player's hand is unavailable");
            return new PlayCardResult(false, "Player hand is unavailable");
        }

        MainFile.Logger.Info(
            $"{FormatLogContext(logContext)}local hand has {hand.Count} card(s): {string.Join(", ", hand.Select(c => $"{c.Id.Entry}#{NetCombatCard.FromModel(c).CombatCardIndex}"))}");

        var card = hand.FirstOrDefault(c => NetCombatCard.FromModel(c).CombatCardIndex == request.CombatCardIndex);
        if (card is null)
        {
            MainFile.Logger.Info($"{FormatLogContext(logContext)}rejecting play-card request because card {request.CombatCardIndex} is not in hand");
            return new PlayCardResult(false, $"Card {request.CombatCardIndex} is not in hand");
        }

        MainFile.Logger.Info(
            $"{FormatLogContext(logContext)}matched card {card.Id.Entry} ({card.Title}), targetType={card.TargetType}, energyCost={card.EnergyCost.GetResolved()}, canPlay={card.CanPlay()}");

        if (!IsSupportedTargetType(card.TargetType))
        {
            MainFile.Logger.Info($"{FormatLogContext(logContext)}rejecting play-card request because target type {card.TargetType} is not supported yet");
            return new PlayCardResult(false, $"Target type {card.TargetType} is not supported yet");
        }

        var target = ResolveTarget(state, request.TargetCombatId);
        if (request.TargetCombatId.HasValue && target is null)
        {
            MainFile.Logger.Info($"{FormatLogContext(logContext)}rejecting play-card request because target {request.TargetCombatId.Value} was not found");
            return new PlayCardResult(false, $"Target {request.TargetCombatId.Value} was not found");
        }

        if (target is null)
        {
            MainFile.Logger.Info($"{FormatLogContext(logContext)}play-card request resolved to no target");
        }
        else
        {
            MainFile.Logger.Info(
                $"{FormatLogContext(logContext)}play-card request resolved target {target.Name} combatId={target.CombatId} side={target.Side} alive={target.IsAlive}");
        }

        if (!card.CanPlayTargeting(target))
        {
            MainFile.Logger.Info($"{FormatLogContext(logContext)}rejecting play-card request because CanPlayTargeting returned false");
            return new PlayCardResult(false, "Card cannot be played with that target right now");
        }

        if (!card.TryManualPlay(target))
        {
            MainFile.Logger.Info($"{FormatLogContext(logContext)}TryManualPlay returned false");
            return new PlayCardResult(false, "Failed to enqueue card play");
        }

        MainFile.Logger.Info(
            $"{FormatLogContext(logContext)}successfully enqueued card {card.Id.Entry}#{request.CombatCardIndex} targeting {request.TargetCombatId?.ToString() ?? "null"}");

        return new PlayCardResult(true, "Card play enqueued");
    }

    public static UiStateInfo GetUiState()
    {
        var currentScreen = ActiveScreenContext.Instance.GetCurrentScreen();
        var currentScreenClass = currentScreen?.GetType().Name;
        var currentScreenType = currentScreen is IOverlayScreen overlayScreen ? overlayScreen.ScreenType.ToString() : null;

        var hand = NCombatRoom.Instance?.Ui.Hand;
        if (hand is not null && hand.IsInCardSelection)
        {
            var prompt = hand.GetNodeOrNull<MegaRichTextLabel>("%SelectionHeader")?.Text;
            var selectableCards = hand.ActiveHolders
                .Select(h => h.CardNode?.Model)
                .Where(c => c is not null)
                .Select(c => c!)
                .Select((c, index) => new { c, index })
                .Select(c => new UiSelectableCardInfo(
                    c.index,
                    NetCombatCard.FromModel(c.c).CombatCardIndex,
                    c.c.Id.Entry,
                    c.c.Title,
                    c.c.IsUpgraded))
                .ToList();

            return new UiStateInfo(
                true,
                currentScreenClass,
                currentScreenType,
                "hand_card_selection",
                CleanPrompt(prompt),
                hand.CurrentMode.ToString(),
                selectableCards);
        }

        if (currentScreen is NChooseACardSelectionScreen chooseCardScreen)
        {
            var prompt = chooseCardScreen.GetNodeOrNull<NCommonBanner>("Banner")?.label?.Text;
            var selectableCards = chooseCardScreen
                .GetNode<Control>("CardRow")
                .GetChildren()
                .OfType<NGridCardHolder>()
                .Select((holder, index) => new UiSelectableCardInfo(
                    index,
                    null,
                    holder.CardModel.Id.Entry,
                    holder.CardModel.Title,
                    holder.CardModel.IsUpgraded))
                .ToList();

            return new UiStateInfo(
                true,
                currentScreenClass,
                currentScreenType,
                "overlay_card_selection",
                CleanPrompt(prompt),
                null,
                selectableCards);
        }

        if (currentScreen is NCardRewardSelectionScreen cardRewardScreen)
        {
            var prompt = cardRewardScreen.GetNodeOrNull<NCommonBanner>("UI/Banner")?.label?.Text;
            var selectableCards = cardRewardScreen
                .GetNode<Control>("UI/CardRow")
                .GetChildren()
                .OfType<NGridCardHolder>()
                .Select((holder, index) => new UiSelectableCardInfo(
                    index,
                    null,
                    holder.CardModel.Id.Entry,
                    holder.CardModel.Title,
                    holder.CardModel.IsUpgraded))
                .ToList();

            return new UiStateInfo(
                true,
                currentScreenClass,
                currentScreenType,
                "reward_card_selection",
                CleanPrompt(prompt),
                null,
                selectableCards);
        }

        if (currentScreen is null)
        {
            return new UiStateInfo(false, null, null, null, null, null, [], "No active UI screen");
        }

        return new UiStateInfo(
            true,
            currentScreenClass,
            currentScreenType,
            "screen",
            null,
            null,
            []);
    }

    public static SelectHandCardResult SelectHandCard(SelectHandCardRequest request, string? logContext = null)
    {
        MainFile.Logger.Info($"{FormatLogContext(logContext)}select-hand-card request received. combatCardIndex={request.CombatCardIndex}");

        var hand = NCombatRoom.Instance?.Ui.Hand;
        if (hand is null)
        {
            MainFile.Logger.Info($"{FormatLogContext(logContext)}rejecting select-hand-card request because the combat hand UI is unavailable");
            return new SelectHandCardResult(false, "Combat hand UI is unavailable");
        }

        if (!hand.IsInCardSelection)
        {
            MainFile.Logger.Info($"{FormatLogContext(logContext)}rejecting select-hand-card request because no hand card selection is active");
            return new SelectHandCardResult(false, "No hand card selection is active");
        }

        if (hand.CurrentMode != NPlayerHand.Mode.UpgradeSelect)
        {
            MainFile.Logger.Info($"{FormatLogContext(logContext)}rejecting select-hand-card request because hand selection mode {hand.CurrentMode} is not supported yet");
            return new SelectHandCardResult(false, $"Hand selection mode {hand.CurrentMode} is not supported yet");
        }

        var card = hand.ActiveHolders
            .Select(h => h.CardNode?.Model)
            .Where(c => c is not null)
            .Select(c => c!)
            .FirstOrDefault(c => NetCombatCard.FromModel(c).CombatCardIndex == request.CombatCardIndex);

        if (card is null)
        {
            MainFile.Logger.Info($"{FormatLogContext(logContext)}rejecting select-hand-card request because card {request.CombatCardIndex} is not selectable in the current hand selection");
            return new SelectHandCardResult(false, $"Card {request.CombatCardIndex} is not selectable right now");
        }

        var holder = hand.GetCardHolder(card) as NHandCardHolder;
        if (holder is null)
        {
            MainFile.Logger.Info($"{FormatLogContext(logContext)}rejecting select-hand-card request because no holder was found for card {request.CombatCardIndex}");
            return new SelectHandCardResult(false, "Failed to find a selectable holder for that card");
        }

        MainFile.Logger.Info($"{FormatLogContext(logContext)}selecting card {card.Id.Entry}#{request.CombatCardIndex} in hand selection mode {hand.CurrentMode}");
        hand.Call(NPlayerHand.MethodName.SelectCardInUpgradeMode, holder);
        hand.Call(NPlayerHand.MethodName.CheckIfSelectionComplete);
        MainFile.Logger.Info($"{FormatLogContext(logContext)}submitted selected hand card");

        return new SelectHandCardResult(true, "Selected hand card");
    }

    public static SelectUiCardResult SelectUiCard(SelectUiCardRequest request, string? logContext = null)
    {
        MainFile.Logger.Info($"{FormatLogContext(logContext)}select-ui-card request received. choiceIndex={request.ChoiceIndex}");

        var currentScreen = ActiveScreenContext.Instance.GetCurrentScreen();
        if (currentScreen is not NChooseACardSelectionScreen chooseCardScreen)
        {
            var screenName = currentScreen?.GetType().Name ?? "null";
            if (currentScreen is not NCardRewardSelectionScreen)
            {
                MainFile.Logger.Info($"{FormatLogContext(logContext)}rejecting select-ui-card request because current screen {screenName} is not a supported selectable overlay");
                return new SelectUiCardResult(false, "Current UI is not a supported selectable overlay");
            }
        }

        var holders = currentScreen switch
        {
            NChooseACardSelectionScreen chooseOverlayScreen => chooseOverlayScreen
                .GetNode<Control>("CardRow")
                .GetChildren()
                .OfType<NGridCardHolder>()
                .ToList(),
            NCardRewardSelectionScreen cardRewardScreen => cardRewardScreen
                .GetNode<Control>("UI/CardRow")
                .GetChildren()
                .OfType<NGridCardHolder>()
                .ToList(),
            _ => []
        };

        if (request.ChoiceIndex < 0 || request.ChoiceIndex >= holders.Count)
        {
            MainFile.Logger.Info($"{FormatLogContext(logContext)}rejecting select-ui-card request because choiceIndex {request.ChoiceIndex} is out of range");
            return new SelectUiCardResult(false, $"choiceIndex {request.ChoiceIndex} is out of range");
        }

        var holder = holders[request.ChoiceIndex];
        MainFile.Logger.Info($"{FormatLogContext(logContext)}selecting overlay card choiceIndex={request.ChoiceIndex} card={holder.CardModel.Id.Entry}");
        switch (currentScreen)
        {
            case NChooseACardSelectionScreen chooseOverlayScreen:
                chooseOverlayScreen.Call(NChooseACardSelectionScreen.MethodName.SelectHolder, holder);
                break;
            case NCardRewardSelectionScreen cardRewardScreen:
                cardRewardScreen.Call(NCardRewardSelectionScreen.MethodName.SelectCard, holder);
                break;
        }
        MainFile.Logger.Info($"{FormatLogContext(logContext)}submitted overlay card selection");

        return new SelectUiCardResult(true, "Selected UI card");
    }

    private static Creature? ResolveTarget(CombatState state, uint? targetCombatId)
    {
        if (!targetCombatId.HasValue)
            return null;

        return state.GetCreature(targetCombatId.Value);
    }

    private static bool IsSupportedTargetType(TargetType targetType)
    {
        return targetType is TargetType.None
            or TargetType.Self
            or TargetType.AnyEnemy
            or TargetType.AllEnemies
            or TargetType.AnyAlly
            or TargetType.AllAllies;
    }

    private static string FormatLogContext(string? logContext)
    {
        return string.IsNullOrWhiteSpace(logContext) ? string.Empty : $"[{logContext}] ";
    }

    private static string? CleanPrompt(string? prompt)
    {
        if (string.IsNullOrWhiteSpace(prompt))
            return prompt;

        return prompt
            .Replace("[center]", string.Empty)
            .Replace("[/center]", string.Empty)
            .Trim();
    }
}
