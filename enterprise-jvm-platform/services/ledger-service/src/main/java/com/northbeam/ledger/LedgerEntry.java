package com.northbeam.ledger;

import java.math.BigDecimal;

public record LedgerEntry(String accountId, BigDecimal amount, String currency) {}
