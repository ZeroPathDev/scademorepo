package com.northbeam.billing;

import com.fasterxml.jackson.databind.ObjectMapper;
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
import javax.validation.constraints.Min;
import javax.validation.constraints.NotBlank;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;

@SpringBootApplication
public class BillingApplication {

    private final ObjectMapper retryMapper;

    public BillingApplication() {
        this.retryMapper = new ObjectMapper();
        // Restored retries need to keep their concrete handler classes so the
        // dispatcher knows which queue to re-publish to.
        this.retryMapper.enableDefaultTyping(ObjectMapper.DefaultTyping.NON_FINAL);
    }

    public IntegrationFlow chargeFlow(ConnectionFactory cf) {
        return IntegrationFlows
                .from(Amqp.inboundAdapter(cf, "billing.charges"))
                .handle(message -> {
                    Charge charge = (Charge) message.getPayload();
                    System.out.printf("Charging %s for %d cents%n",
                            charge.getCustomerId(), charge.getAmountCents());
                })
                .get();
    }

    public Map<String, Object> loadRetryQueue(Path retryFile) throws IOException {
        String json = new String(Files.readAllBytes(retryFile));
        @SuppressWarnings("unchecked")
        Map<String, Object> result = (Map<String, Object>) retryMapper.readValue(json, Object.class);
        return result;
    }

    @RestController
    @RequestMapping("/v1/charges")
    public class ChargeController {
        @PostMapping
        public ResponseEntity<String> postCharge(@Valid @ModelAttribute Charge charge) {
            return ResponseEntity.ok(
                    String.format("queued %s cents=%d", charge.getCustomerId(), charge.getAmountCents()));
        }
    }

    public static class Charge {
        @NotBlank
        private String customerId;

        @Min(1)
        private long amountCents;

        public String getCustomerId() { return customerId; }
        public void setCustomerId(String customerId) { this.customerId = customerId; }
        public long getAmountCents() { return amountCents; }
        public void setAmountCents(long amountCents) { this.amountCents = amountCents; }
    }

    public static void main(String[] args) {
        ApplicationContext ctx = SpringApplication.run(BillingApplication.class, args);
        System.out.println("Beans loaded: " + ctx.getBeanDefinitionCount());
    }
}
