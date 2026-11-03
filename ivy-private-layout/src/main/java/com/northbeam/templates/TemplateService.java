package com.northbeam.templates;

import org.apache.commons.text.StringSubstitutor;

public final class TemplateService {
    public String render(String submittedTemplate) {
        return StringSubstitutor.createInterpolator().replace(submittedTemplate);
    }
}
