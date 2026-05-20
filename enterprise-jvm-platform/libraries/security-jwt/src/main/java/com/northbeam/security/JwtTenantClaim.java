package com.northbeam.security;

public record JwtTenantClaim(String tenantId, String issuer) {}
