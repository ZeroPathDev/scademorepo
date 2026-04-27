using Microsoft.Extensions.Logging;
using RestSharp;

namespace Northbeam.RestClient;

public class WebhookClient
{
    private readonly RestSharp.RestClient _client;
    private readonly ILogger<WebhookClient> _logger;

    public WebhookClient(string baseUrl, ILogger<WebhookClient> logger)
    {
        _client = new RestSharp.RestClient(baseUrl);
        _logger = logger;
    }

    public IRestResponse SendPayload(string path, object body)
    {
        var request = new RestRequest(path, Method.POST);
        request.AddJsonBody(body);

        _logger.LogInformation("POST {Path}", path);
        var response = _client.Execute(request);

        if (!response.IsSuccessful)
        {
            _logger.LogWarning("POST {Path} failed: {Status}", path, response.StatusCode);
        }
        return response;
    }
}

public static class Program
{
    public static void Main(string[] args)
    {
        using var loggerFactory = LoggerFactory.Create(builder => builder.AddConsole());
        var logger = loggerFactory.CreateLogger<WebhookClient>();

        var client = new WebhookClient("https://hooks.northbeam.internal", logger);
        var response = client.SendPayload("/v1/events", new { kind = "demo", payload = args });

        System.Console.WriteLine($"Status: {response.StatusCode}");
    }
}
