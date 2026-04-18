using System.Net;
using System.Text.Json;
using System.Threading;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Modding;
using SpireAPI.SpireAPICode;

namespace SpireRestAPI.SpireRestAPICode;

//You're recommended but not required to keep all your code in this package and all your assets in the SpireRestAPI folder.
[ModInitializer(nameof(Initialize))]
public partial class MainFile : Node
{
    public const string ModId = "SpireRestAPI"; //At the moment, this is used only for the Logger and harmony names.
    // macOS resolves localhost to IPv6 (::1); adding the explicit IPv4 address ensures
    // both http://localhost:7777/ and http://127.0.0.1:7777/ work in the browser.
    private const string ListenPrefix = "http://localhost:7777/";
    private const string ListenPrefixIpv4 = "http://127.0.0.1:7777/";

    public static MegaCrit.Sts2.Core.Logging.Logger Logger { get; } =
        new(ModId, MegaCrit.Sts2.Core.Logging.LogType.Generic);

    private static readonly JsonSerializerOptions JsonOptions = new() { PropertyNamingPolicy = JsonNamingPolicy.CamelCase };

    private const string IndexHtml = """
        <!DOCTYPE html>
        <html>
        <head><title>SpireRestAPI</title></head>
        <body>
        <h1>SpireRestAPI</h1>
        <table border="1" cellpadding="6">
          <tr><th>Method</th><th>Path</th><th>Description</th></tr>
          <tr><td>GET</td><td><a href="/combat/state">/combat/state</a></td><td>Current combat state: hand, enemies, energy, round. Returns isInProgress=false when not in combat.</td></tr>
        </table>
        </body>
        </html>
        """;

    public static void Initialize()
    {
        Harmony harmony = new(ModId);
        harmony.PatchAll();

        var listener = new HttpListener();
        listener.Prefixes.Add(ListenPrefix);
        listener.Prefixes.Add(ListenPrefixIpv4);
        listener.Start();
        Logger.Info($"SpireRestAPI listening on {ListenPrefix} and {ListenPrefixIpv4}");

        new Thread(() =>
        {
            try
            {
                while (listener.IsListening)
                {
                    var ctx = listener.GetContext();
                    var req = ctx.Request;
                    var res = ctx.Response;
                    Logger.Info($"SpireRestAPI request: {req.HttpMethod} {req.Url?.AbsolutePath}");

                    byte[] body;
                    if (req.HttpMethod == "GET" && req.Url?.AbsolutePath == "/")
                    {
                        body = System.Text.Encoding.UTF8.GetBytes(IndexHtml);
                        res.ContentType = "text/html; charset=utf-8";
                    }
                    else if (req.HttpMethod == "GET" && req.Url?.AbsolutePath == "/combat/state")
                    {
                        var data = CombatApi.GetCombatState();
                        body = JsonSerializer.SerializeToUtf8Bytes(data, JsonOptions);
                        res.ContentType = "application/json";
                    }
                    else
                    {
                        body = "Not Found"u8.ToArray();
                        res.StatusCode = 404;
                        res.ContentType = "text/plain";
                    }

                    res.ContentLength64 = body.Length;
                    res.OutputStream.Write(body);
                    res.OutputStream.Close();
                }
            }
            catch (Exception ex)
            {
                Logger.Error($"SpireRestAPI listener error: {ex}");
            }
        }) { IsBackground = true }.Start();
    }
}
