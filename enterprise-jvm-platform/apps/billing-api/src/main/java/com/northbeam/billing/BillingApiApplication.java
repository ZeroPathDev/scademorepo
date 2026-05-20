package com.northbeam.billing;

public final class BillingApiApplication {
    private BillingApiApplication() {}

    public static String invoiceTopic() {
        return "billing.invoice.created";
    }
}
