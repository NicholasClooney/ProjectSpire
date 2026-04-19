using System;
using System.Threading.Tasks;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Modding;

namespace SpireAPI.SpireAPICode;

//You're recommended but not required to keep all your code in this package and all your assets in the SpireAPI folder.
[ModInitializer(nameof(Initialize))]
public partial class MainFile : Node
{
    public const string ModId = "SpireAPI"; //At the moment, this is used only for the Logger and harmony names.

    public static MegaCrit.Sts2.Core.Logging.Logger Logger { get; } =
        new(ModId, MegaCrit.Sts2.Core.Logging.LogType.Generic);

    public static Task<T> RunOnMainThread<T>(Func<T> action, string? logContext = null)
    {
        var tcs = new TaskCompletionSource<T>(TaskCreationOptions.RunContinuationsAsynchronously);
        Logger.Info($"{FormatLogContext(logContext)}scheduling work onto the Godot main thread");

        Callable.From(() =>
        {
            try
            {
                Logger.Info($"{FormatLogContext(logContext)}running scheduled work on the Godot main thread");
                tcs.SetResult(action());
            }
            catch (Exception ex)
            {
                Logger.Error($"{FormatLogContext(logContext)}scheduled main-thread work failed: {ex}");
                tcs.SetException(ex);
            }
        }).CallDeferred();

        return tcs.Task;
    }

    private static string FormatLogContext(string? logContext)
    {
        return string.IsNullOrWhiteSpace(logContext) ? string.Empty : $"[{logContext}] ";
    }

    public static void Initialize()
    {
        Harmony harmony = new(ModId);
        harmony.PatchAll();
    }
}
