package com.northbeam.settlement;

import java.time.LocalDate;

public record SettlementBatch(String processor, LocalDate businessDate) {}
