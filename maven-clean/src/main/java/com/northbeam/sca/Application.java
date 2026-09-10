package com.northbeam.sca;

import java.util.Map;
import org.apache.commons.text.StringSubstitutor;

public final class Application {
    public static void main(String[] args) {
        StringSubstitutor template = new StringSubstitutor(Map.of("warehouse", "primary"));
        System.out.println(template.replace("Inventory export from ${warehouse}"));
    }
}
