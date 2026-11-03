package com.northbeam.collections;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.Reader;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.apache.commons.collections.CollectionUtils;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.apache.commons.text.StringSubstitutor;

public final class CollectionIntake {
    private static final int BATCH_SIZE = 500;
    private static final String PAYMENT_LINE = "${invoiceId}\t${customerId}\t${amount}";

    public void exportReadyInvoices(Path input, Path output) throws IOException {
        try (Reader reader = Files.newBufferedReader(input, StandardCharsets.UTF_8);
                CSVParser rows = CSVFormat.DEFAULT.withFirstRecordAsHeader().parse(reader);
                BufferedWriter writer = Files.newBufferedWriter(output, StandardCharsets.UTF_8)) {
            List<Invoice> batch = new ArrayList<>();
            for (CSVRecord row : rows) {
                batch.add(new Invoice(row.get("invoiceId"), row.get("customerId"),
                        new BigDecimal(row.get("amount")), row.get("status")));
                if (batch.size() == BATCH_SIZE) {
                    writeBatch(batch, writer);
                    batch.clear();
                }
            }
            writeBatch(batch, writer);
        }
    }

    private void writeBatch(List<Invoice> batch, BufferedWriter writer) throws IOException {
        List<Invoice> ready = new ArrayList<>();
        CollectionUtils.select(batch, value -> ((Invoice) value).isReady(), ready);
        for (Invoice invoice : ready) {
            StringSubstitutor fields = new StringSubstitutor(Map.of(
                    "invoiceId", invoice.invoiceId, "customerId", invoice.customerId,
                    "amount", invoice.amount.toPlainString()));
            fields.setDisableSubstitutionInValues(true);
            writer.write(fields.replace(PAYMENT_LINE));
            writer.newLine();
        }
    }

    private static final class Invoice {
        private final String invoiceId;
        private final String customerId;
        private final BigDecimal amount;
        private final String status;

        private Invoice(String invoiceId, String customerId, BigDecimal amount, String status) {
            if (!invoiceId.matches("[A-Za-z0-9_-]+") || !customerId.matches("[A-Za-z0-9_-]+")) {
                throw new IllegalArgumentException("Invoice and customer identifiers must be alphanumeric");
            }
            this.invoiceId = invoiceId;
            this.customerId = customerId;
            this.amount = amount;
            this.status = status;
        }

        private boolean isReady() {
            return "ready".equals(status) && amount.signum() > 0;
        }
    }

    public static void main(String[] args) throws IOException {
        if (args.length != 2) {
            throw new IllegalArgumentException("Usage: CollectionIntake invoices.csv payments.tsv");
        }
        new CollectionIntake().exportReadyInvoices(Path.of(args[0]), Path.of(args[1]));
    }
}
