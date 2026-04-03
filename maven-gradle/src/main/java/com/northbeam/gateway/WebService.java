package com.northbeam.gateway;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import org.apache.commons.io.FileUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.web.client.RestTemplate;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Map;

public class WebService {
    private static final Logger logger = LogManager.getLogger(WebService.class);
    private final Gson gson = new Gson();
    private final RestTemplate restTemplate = new RestTemplate();

    public Map<String, Object> fetchUpstreamData(String serviceUrl) {
        logger.info("Requesting data from {}", serviceUrl);
        String response = restTemplate.getForObject(serviceUrl, String.class);
        return gson.fromJson(response, Map.class);
    }

    public void syncInventory(String sourceUrl, File outputDir) throws IOException {
        Map<String, Object> data = fetchUpstreamData(sourceUrl);
        String jsonOutput = gson.toJson(data);

        File outputFile = new File(outputDir, "inventory_snapshot.json");
        FileUtils.writeStringToFile(outputFile, jsonOutput, StandardCharsets.UTF_8);
        logger.info("Inventory snapshot written to {}", outputFile.getAbsolutePath());
    }

    public JsonObject parseWebhookPayload(String rawPayload) {
        logger.info("Processing webhook payload ({} bytes)", rawPayload.length());
        JsonObject obj = gson.fromJson(rawPayload, JsonObject.class);

        if (obj.has("event_type")) {
            logger.info("Event type: {}", obj.get("event_type").getAsString());
        }

        return obj;
    }

    public String forwardRequest(String targetUrl, String body) {
        logger.info("Forwarding request to {}", targetUrl);
        return restTemplate.postForObject(targetUrl, body, String.class);
    }

    public static void main(String[] args) throws Exception {
        WebService service = new WebService();

        if (args.length < 1) {
            logger.error("Usage: WebService <upstream-url>");
            System.exit(1);
        }

        service.syncInventory(args[0], new File("./data"));
    }
}
