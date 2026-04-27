package com.northbeam.billing;

import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;
import org.springframework.integration.amqp.dsl.Amqp;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.integration.dsl.IntegrationFlows;

import javax.validation.constraints.Min;
import javax.validation.constraints.NotBlank;

@SpringBootApplication
public class BillingApplication {

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

    public static class Charge {
        @NotBlank
        private String customerId;

        @Min(1)
        private long amountCents;

        public String getCustomerId() { return customerId; }
        public long getAmountCents() { return amountCents; }
    }

    public static void main(String[] args) {
        ApplicationContext ctx = SpringApplication.run(BillingApplication.class, args);
        System.out.println("Beans loaded: " + ctx.getBeanDefinitionCount());
    }
}
