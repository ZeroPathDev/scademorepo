package com.northbeam.templates;

import java.io.IOException;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Properties;
import com.northbeam.templates.client.TemplateClient;

public final class TemplateService {
    public String render(Path template, Path recipient) throws IOException {
        Properties properties = new Properties();
        try (Reader reader = Files.newBufferedReader(recipient, StandardCharsets.UTF_8)) {
            properties.load(reader);
        }
        Map<String, String> fields = new LinkedHashMap<>();
        for (String name : properties.stringPropertyNames()) {
            fields.put(name, properties.getProperty(name));
        }
        return new TemplateClient().render(template, fields);
    }

    public static void main(String[] args) throws IOException {
        if (args.length != 2) {
            throw new IllegalArgumentException("Usage: TemplateService template.txt recipient.properties");
        }
        System.out.print(new TemplateService().render(Path.of(args[0]), Path.of(args[1])));
    }
}
