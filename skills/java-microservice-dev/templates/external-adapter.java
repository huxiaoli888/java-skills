package {{basePackage}}.adapter;

import org.springframework.stereotype.Component;
import {{basePackage}}.client.{{clientClass}};

@Component
public class {{adapterClass}} {
    private final {{clientClass}} client;

    public {{adapterClass}}({{clientClass}} client) {
        this.client = client;
    }

    public {{responseClass}} {{methodName}}({{requestClass}} request) {
        // Convert project-level request to provider request here when contracts differ.
        return client.{{methodName}}(request);
    }
}
