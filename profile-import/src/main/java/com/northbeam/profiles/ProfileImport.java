package com.northbeam.profiles;

import java.lang.reflect.InvocationTargetException;
import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;
import org.apache.commons.beanutils.BeanUtils;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.CSVRecord;

public final class ProfileImport {
    private static final String[] FIELDS = {"customerId", "email", "displayName", "department"};

    public void importProfiles(Path source, Path destination)
            throws IOException, IllegalAccessException, InvocationTargetException {
        try (Reader reader = Files.newBufferedReader(source, StandardCharsets.UTF_8);
                CSVParser rows = CSVFormat.DEFAULT.withFirstRecordAsHeader().parse(reader);
                Writer writer = Files.newBufferedWriter(destination, StandardCharsets.UTF_8);
                CSVPrinter output = new CSVPrinter(writer, CSVFormat.DEFAULT.withHeader(FIELDS))) {
            for (CSVRecord row : rows) {
                Map<String, String> fields = new LinkedHashMap<>();
                for (String name : FIELDS) {
                    fields.put(name, row.get(name).trim());
                }
                CustomerProfile profile = new CustomerProfile();
                BeanUtils.populate(profile, fields);
                profile.validate();
                output.printRecord(profile.getCustomerId(), profile.getEmail(),
                        profile.getDisplayName(), profile.getDepartment());
            }
        }
    }

    public static final class CustomerProfile {
        private String customerId;
        private String email;
        private String displayName;
        private String department;

        public String getCustomerId() { return customerId; }
        public void setCustomerId(String customerId) { this.customerId = customerId; }
        public String getEmail() { return email; }
        public void setEmail(String email) { this.email = email; }
        public String getDisplayName() { return displayName; }
        public void setDisplayName(String displayName) { this.displayName = displayName; }
        public String getDepartment() { return department; }
        public void setDepartment(String department) { this.department = department; }

        private void validate() {
            if (customerId.isEmpty() || !email.contains("@") || displayName.isEmpty()) {
                throw new IllegalArgumentException("A profile requires a customer ID, email and display name");
            }
        }
    }

    public static void main(String[] args)
            throws IOException, IllegalAccessException, InvocationTargetException {
        if (args.length != 2) {
            throw new IllegalArgumentException("Usage: ProfileImport source.csv normalized.csv");
        }
        new ProfileImport().importProfiles(Path.of(args[0]), Path.of(args[1]));
    }
}
