package com.northbeam.risk;

public final class RiskDecisionService {
    public boolean approve(long merchantId, int riskScore) {
        return merchantId > 0 && riskScore < 700;
    }
}
