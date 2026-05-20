package com.northbeam.email;

public record EmailDeliveryRequest(String recipient, String templateKey) {}
