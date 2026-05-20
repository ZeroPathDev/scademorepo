package com.northbeam.audit;

import java.time.Instant;

public record AuditEvent(String actor, String action, Instant observedAt) {}
