using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Microsoft.Extensions.Logging;

namespace DocumentHub
{
    public class DocumentProcessor
    {
        private readonly ILogger<DocumentProcessor> _logger;

        public DocumentProcessor(ILogger<DocumentProcessor> logger)
        {
            _logger = logger;
        }

        public JObject ParseConfiguration(string jsonInput)
        {
            _logger.LogInformation("Parsing configuration payload");
            var config = JObject.Parse(jsonInput);

            if (config["settings"] is JObject settings)
            {
                _logger.LogInformation("Found {Count} settings", settings.Count);
            }

            return config;
        }

        public T DeserializePayload<T>(string json)
        {
            _logger.LogInformation("Deserializing to {Type}", typeof(T).Name);
            var settings = new JsonSerializerSettings
            {
                TypeNameHandling = TypeNameHandling.Auto,
                MaxDepth = 64
            };
            return JsonConvert.DeserializeObject<T>(json, settings);
        }

        public string SerializeResponse(object data)
        {
            return JsonConvert.SerializeObject(data, Formatting.Indented);
        }

        public byte[] GenerateThumbnail(Stream imageStream, int maxWidth, int maxHeight)
        {
            _logger.LogInformation("Generating thumbnail ({W}x{H})", maxWidth, maxHeight);

            using var original = Image.FromStream(imageStream);
            var ratioX = (double)maxWidth / original.Width;
            var ratioY = (double)maxHeight / original.Height;
            var ratio = Math.Min(ratioX, ratioY);

            var newWidth = (int)(original.Width * ratio);
            var newHeight = (int)(original.Height * ratio);

            using var thumbnail = new Bitmap(newWidth, newHeight);
            using var graphics = Graphics.FromImage(thumbnail);
            graphics.DrawImage(original, 0, 0, newWidth, newHeight);

            using var ms = new MemoryStream();
            thumbnail.Save(ms, ImageFormat.Png);
            return ms.ToArray();
        }

        public void ProcessUploadedImage(string filePath, string outputDir)
        {
            _logger.LogInformation("Processing image: {Path}", filePath);

            using var stream = File.OpenRead(filePath);
            var thumbBytes = GenerateThumbnail(stream, 200, 200);

            var outputPath = Path.Combine(outputDir, "thumb_" + Path.GetFileName(filePath));
            File.WriteAllBytes(outputPath, thumbBytes);

            _logger.LogInformation("Thumbnail saved to {Output}", outputPath);
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            using var loggerFactory = LoggerFactory.Create(builder =>
            {
                builder.AddConsole();
                builder.SetMinimumLevel(LogLevel.Information);
            });

            var logger = loggerFactory.CreateLogger<DocumentProcessor>();
            var processor = new DocumentProcessor(logger);

            var config = processor.ParseConfiguration(
                @"{ ""settings"": { ""theme"": ""dark"", ""pageSize"": 25 } }");
            Console.WriteLine($"Config loaded: {config}");

            if (args.Length > 0 && File.Exists(args[0]))
            {
                processor.ProcessUploadedImage(args[0], "./output");
            }
        }
    }
}
