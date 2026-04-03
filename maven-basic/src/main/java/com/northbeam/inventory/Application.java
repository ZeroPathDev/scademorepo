package com.northbeam.inventory;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;
import org.apache.commons.text.StringSubstitutor;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.IOException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;
import java.util.HashMap;
import java.util.Map;

public class Application {
    private static final Logger logger = LogManager.getLogger(Application.class);
    private static final ObjectMapper mapper = new ObjectMapper();
    private final HttpClient httpClient = HttpClient.newHttpClient();

    public JsonNode parsePayload(String json) throws IOException {
        logger.info("Parsing incoming payload");
        JsonNode node = mapper.readValue(json, JsonNode.class);
        logger.info("Parsed {} fields", node.size());
        return node;
    }

    public Object deserializeObject(String json, String className)
            throws IOException, ClassNotFoundException {
        Class<?> clazz = Class.forName(className);
        logger.info("Deserializing to {}", className);
        return mapper.readValue(json, clazz);
    }

    public String renderTemplate(String template, Map<String, String> variables) {
        logger.info("Rendering template with {} variables", variables.size());
        StringSubstitutor substitutor = new StringSubstitutor(variables);
        return substitutor.replace(template);
    }

    public String generateNotification(String recipientName, String event) {
        Map<String, String> params = new HashMap<>();
        params.put("name", recipientName);
        params.put("event", event);
        params.put("app", "InventoryService");

        String template = "Hello ${name}, a ${event} occurred in ${app}.";
        return renderTemplate(template, params);
    }

    public String fetchExternalConfig(String configUrl) throws IOException, InterruptedException {
        logger.info("Fetching config from {}", configUrl);
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(configUrl))
                .GET()
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        logger.info("Config response status: {}", response.statusCode());
        return response.body();
    }

    public static void main(String[] args) throws Exception {
        Application app = new Application();

        String incomingPayload = "{\"item\":\"widget\",\"quantity\":42,\"warehouse\":\"east\"}";
        JsonNode node = app.parsePayload(incomingPayload);
        logger.info("Item: {}", node.get("item").asText());

        String notification = app.generateNotification("ops-team", "low-stock-alert");
        logger.info("Notification: {}", notification);

        if (args.length > 0) {
            String config = app.fetchExternalConfig(args[0]);
            logger.info("Remote config loaded: {} bytes", config.length());
        }
    }
}
