package com.northbeam.indexer;

import com.mongodb.MongoClient;
import com.mongodb.MongoClientURI;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;

import org.bson.Document;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;
import org.springframework.integration.amqp.dsl.Amqp;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.integration.dsl.IntegrationFlows;

import javax.validation.Valid;
import javax.validation.constraints.NotBlank;

@SpringBootApplication
public class IndexerApplication {

    private final MongoCollection<Document> events;

    public IndexerApplication(MongoClientURI uri) {
        MongoClient client = new MongoClient(uri);
        MongoDatabase db = client.getDatabase(uri.getDatabase());
        this.events = db.getCollection("events");
    }

    public IntegrationFlow eventIngestFlow(org.springframework.amqp.rabbit.connection.ConnectionFactory cf) {
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

    public static class EventPayload {
        @NotBlank
        private String name;

        @NotBlank
        private String source;

        public String getName() { return name; }
        public String getSource() { return source; }
    }

    public static void main(String[] args) {
        ApplicationContext ctx = SpringApplication.run(IndexerApplication.class, args);
        System.out.println("Beans loaded: " + ctx.getBeanDefinitionCount());
    }
}
