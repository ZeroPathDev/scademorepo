package com.northbeam.domain;

public record MerchantId(String value) {
    public MerchantId {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("merchant id is required");
        }
    }
}
