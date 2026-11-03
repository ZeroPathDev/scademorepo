package com.northbeam.templates.client;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import org.apache.commons.text.StringSubstitutor;

public final class TemplateClient {
    public String render(Path template, Map<String, String> fields) throws IOException {
        StringSubstitutor substitutor = new StringSubstitutor(fields);
        substitutor.setDisableSubstitutionInValues(true);
        substitutor.setEnableUndefinedVariableException(true);
        return substitutor.replace(Files.readString(template, StandardCharsets.UTF_8));
    }
}
