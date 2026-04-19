using System.Net;
using System.Text;
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
    private static int _nextRequestId;

    private const string IndexHtml = """
        <!DOCTYPE html>
        <html>
        <head><title>SpireRestAPI</title></head>
        <body>
        <h1>SpireRestAPI</h1>
        <table border="1" cellpadding="6">
          <tr><th>Method</th><th>Path</th><th>Description</th></tr>
          <tr><td>GET</td><td><a href="/combat/state">/combat/state</a></td><td>Current combat state: hand, enemies, energy, round. Returns isInProgress=false when not in combat.</td></tr>
          <tr><td>POST</td><td>/combat/play-card</td><td>Queue a straightforward hand card play using combatCardIndex and optional targetCombatId.</td></tr>
          <tr><td>GET</td><td><a href="/ui/state">/ui/state</a></td><td>Describe the current active screen and any supported hand card selection UI.</td></tr>
          <tr><td>POST</td><td>/combat/select-hand-card</td><td>Answer the active supported hand card selection by combatCardIndex.</td></tr>
          <tr><td>POST</td><td>/ui/select-card</td><td>Answer a supported overlay card selection screen by choiceIndex.</td></tr>
        </table>
        </body>
        </html>
        """;

    private sealed record ErrorResponse(string Message);

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
            while (listener.IsListening)
            {
                HttpListenerContext ctx;
                try { ctx = listener.GetContext(); }
                catch (Exception ex)
                {
                    Logger.Error($"SpireRestAPI: failed to get context: {ex.Message}");
                    break;
                }

                // Handle each request in its own try-catch so one bad request can't kill the thread.
                try
                {
                    Handle(ctx);
                }
                catch (Exception ex)
                {
                    Logger.Error($"SpireRestAPI: unhandled error on {ctx.Request.HttpMethod} {ctx.Request.Url?.AbsolutePath}: {ex}");
                    try
                    {
                        ctx.Response.StatusCode = 500;
                        ctx.Response.OutputStream.Close();
                    }
                    catch { /* best effort */ }
                }
            }
        }) { IsBackground = true }.Start();
    }

    private static void Handle(HttpListenerContext ctx)
    {
        var req = ctx.Request;
        var res = ctx.Response;
        var requestId = Interlocked.Increment(ref _nextRequestId);
        var logContext = $"play-card req={requestId}";
        Logger.Info($"[{logContext}] request: {req.HttpMethod} {req.Url?.AbsolutePath}");

        byte[] body;
        if (req.HttpMethod == "GET" && req.Url?.AbsolutePath == "/")
        {
            body = Encoding.UTF8.GetBytes(IndexHtml);
            res.ContentType = "text/html; charset=utf-8";
        }
        else if (req.HttpMethod == "GET" && req.Url?.AbsolutePath == "/combat/state")
        {
            var data = CombatApi.GetCombatState();
            body = JsonSerializer.SerializeToUtf8Bytes(data, JsonOptions);
            res.ContentType = "application/json";
        }
        else if (req.HttpMethod == "GET" && req.Url?.AbsolutePath == "/ui/state")
        {
            var data = SpireAPI.SpireAPICode.MainFile.RunOnMainThread(CombatApi.GetUiState, logContext)
                .GetAwaiter()
                .GetResult();
            body = JsonSerializer.SerializeToUtf8Bytes(data, JsonOptions);
            res.ContentType = "application/json";
        }
        else if (req.HttpMethod == "POST" && req.Url?.AbsolutePath == "/combat/play-card")
        {
            using var reader = new StreamReader(req.InputStream, req.ContentEncoding ?? Encoding.UTF8);
            var rawBody = reader.ReadToEnd();
            Logger.Info($"[{logContext}] received play-card body: {rawBody}");

            CombatApi.PlayCardRequest? request;
            try
            {
                request = JsonSerializer.Deserialize<CombatApi.PlayCardRequest>(rawBody, JsonOptions);
            }
            catch (JsonException ex)
            {
                Logger.Error($"[{logContext}] invalid play-card JSON: {ex.Message}");
                body = JsonSerializer.SerializeToUtf8Bytes(new ErrorResponse("Invalid JSON body"), JsonOptions);
                res.StatusCode = 400;
                res.ContentType = "application/json";
                WriteResponse(res, body, logContext);
                return;
            }

            if (request is null)
            {
                Logger.Info($"[{logContext}] play-card request body was empty or null after deserialization");
                body = JsonSerializer.SerializeToUtf8Bytes(new ErrorResponse("Request body is required"), JsonOptions);
                res.StatusCode = 400;
                res.ContentType = "application/json";
            }
            else
            {
                Logger.Info(
                    $"[{logContext}] dispatching play-card request to main thread. combatCardIndex={request.CombatCardIndex}, targetCombatId={request.TargetCombatId?.ToString() ?? "null"}");
                var result = SpireAPI.SpireAPICode.MainFile.RunOnMainThread(() => CombatApi.PlayCard(request, logContext), logContext)
                    .GetAwaiter()
                    .GetResult();

                Logger.Info($"[{logContext}] play-card result success={result.Success} message=\"{result.Message}\"");
                body = JsonSerializer.SerializeToUtf8Bytes(result, JsonOptions);
                res.StatusCode = result.Success ? 200 : 400;
                res.ContentType = "application/json";
            }
        }
        else if (req.HttpMethod == "POST" && req.Url?.AbsolutePath == "/combat/select-hand-card")
        {
            using var reader = new StreamReader(req.InputStream, req.ContentEncoding ?? Encoding.UTF8);
            var rawBody = reader.ReadToEnd();
            Logger.Info($"[{logContext}] received select-hand-card body: {rawBody}");

            CombatApi.SelectHandCardRequest? request;
            try
            {
                request = JsonSerializer.Deserialize<CombatApi.SelectHandCardRequest>(rawBody, JsonOptions);
            }
            catch (JsonException ex)
            {
                Logger.Error($"[{logContext}] invalid select-hand-card JSON: {ex.Message}");
                body = JsonSerializer.SerializeToUtf8Bytes(new ErrorResponse("Invalid JSON body"), JsonOptions);
                res.StatusCode = 400;
                res.ContentType = "application/json";
                WriteResponse(res, body, logContext);
                return;
            }

            if (request is null)
            {
                Logger.Info($"[{logContext}] select-hand-card request body was empty or null after deserialization");
                body = JsonSerializer.SerializeToUtf8Bytes(new ErrorResponse("Request body is required"), JsonOptions);
                res.StatusCode = 400;
                res.ContentType = "application/json";
            }
            else
            {
                Logger.Info($"[{logContext}] dispatching select-hand-card request to main thread. combatCardIndex={request.CombatCardIndex}");
                var result = SpireAPI.SpireAPICode.MainFile.RunOnMainThread(() => CombatApi.SelectHandCard(request, logContext), logContext)
                    .GetAwaiter()
                    .GetResult();

                Logger.Info($"[{logContext}] select-hand-card result success={result.Success} message=\"{result.Message}\"");
                body = JsonSerializer.SerializeToUtf8Bytes(result, JsonOptions);
                res.StatusCode = result.Success ? 200 : 400;
                res.ContentType = "application/json";
            }
        }
        else if (req.HttpMethod == "POST" && req.Url?.AbsolutePath == "/ui/select-card")
        {
            using var reader = new StreamReader(req.InputStream, req.ContentEncoding ?? Encoding.UTF8);
            var rawBody = reader.ReadToEnd();
            Logger.Info($"[{logContext}] received ui/select-card body: {rawBody}");

            CombatApi.SelectUiCardRequest? request;
            try
            {
                request = JsonSerializer.Deserialize<CombatApi.SelectUiCardRequest>(rawBody, JsonOptions);
            }
            catch (JsonException ex)
            {
                Logger.Error($"[{logContext}] invalid ui/select-card JSON: {ex.Message}");
                body = JsonSerializer.SerializeToUtf8Bytes(new ErrorResponse("Invalid JSON body"), JsonOptions);
                res.StatusCode = 400;
                res.ContentType = "application/json";
                WriteResponse(res, body, logContext);
                return;
            }

            if (request is null)
            {
                Logger.Info($"[{logContext}] ui/select-card request body was empty or null after deserialization");
                body = JsonSerializer.SerializeToUtf8Bytes(new ErrorResponse("Request body is required"), JsonOptions);
                res.StatusCode = 400;
                res.ContentType = "application/json";
            }
            else
            {
                Logger.Info($"[{logContext}] dispatching ui/select-card request to main thread. choiceIndex={request.ChoiceIndex}");
                var result = SpireAPI.SpireAPICode.MainFile.RunOnMainThread(() => CombatApi.SelectUiCard(request, logContext), logContext)
                    .GetAwaiter()
                    .GetResult();

                Logger.Info($"[{logContext}] ui/select-card result success={result.Success} message=\"{result.Message}\"");
                body = JsonSerializer.SerializeToUtf8Bytes(result, JsonOptions);
                res.StatusCode = result.Success ? 200 : 400;
                res.ContentType = "application/json";
            }
        }
        else
        {
            body = "Not Found"u8.ToArray();
            res.StatusCode = 404;
            res.ContentType = "text/plain";
        }

        WriteResponse(res, body, logContext);
    }

    private static void WriteResponse(HttpListenerResponse res, byte[] body, string logContext)
    {
        Logger.Info($"[{logContext}] responding with status={res.StatusCode} contentType={res.ContentType} bytes={body.Length}");
        res.ContentLength64 = body.Length;
        res.OutputStream.Write(body);
        res.OutputStream.Close();
    }
}
