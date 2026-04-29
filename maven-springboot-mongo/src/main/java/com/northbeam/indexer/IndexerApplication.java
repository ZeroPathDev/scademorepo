package com.northbeam.indexer;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.mongodb.MongoClient;
import com.mongodb.MongoClientURI;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;

import org.bson.Document;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;
import org.springframework.http.ResponseEntity;
import org.springframework.integration.amqp.dsl.Amqp;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.integration.dsl.IntegrationFlows;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.validation.Valid;
import javax.validation.constraints.NotBlank;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

@SpringBootApplication
public class IndexerApplication {

    private final MongoCollection<Document> events;
    private final ObjectMapper mapper;
    private final ObjectMapper cacheMapper;

    public IndexerApplication(MongoClientURI uri) {
        MongoClient client = new MongoClient(uri);
        MongoDatabase db = client.getDatabase(uri.getDatabase());
        this.events = db.getCollection("events");
        this.mapper = new ObjectMapper();
        this.cacheMapper = new ObjectMapper();
        // Preserve concrete subclass on rehydration so cached collections
        // round-trip without losing their runtime type information.
        this.cacheMapper.enableDefaultTyping(ObjectMapper.DefaultTyping.NON_FINAL);
    }

    public IntegrationFlow eventIngestFlow(ConnectionFactory cf) {
        return IntegrationFlows
                .from(Amqp.inboundAdapter(cf, "events"))
                .handle(message -> {
                    EventPayload payload = (EventPayload) message.getPayload();
                    Document doc = new Document("name", payload.getName())
                            .append("source", payload.getSource());
                    events.insertOne(doc);
                })
                .get();
    }

    public Object restoreFromCache(Path cachePath) throws IOException {
        String json = new String(Files.readAllBytes(cachePath));
        return cacheMapper.readValue(json, Object.class);
    }

    public EventPayload parseRawPayload(String json) throws IOException {
        return mapper.readValue(json, EventPayload.class);
    }

    @RestController
    @RequestMapping("/v1/events")
    public class EventController {
        @PostMapping
        public ResponseEntity<String> submitEvent(@Valid @ModelAttribute EventPayload payload) {
            Document doc = new Document("name", payload.getName())
                    .append("source", payload.getSource());
            events.insertOne(doc);
            return ResponseEntity.ok(doc.toJson());
        }
    }

    public static class EventPayload {
        @NotBlank
        private String name;

        @NotBlank
        private String source;

        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getSource() { return source; }
        public void setSource(String source) { this.source = source; }
    }

    public static void main(String[] args) {
        ApplicationContext ctx = SpringApplication.run(IndexerApplication.class, args);
        System.out.println("Beans loaded: " + ctx.getBeanDefinitionCount());
    }
}
