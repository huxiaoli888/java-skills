package {{basePackage}}.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

@FeignClient(name = "{{serviceName}}", url = "${{{configPrefix}}.url}")
public interface {{clientClass}} {

    @PostMapping("{{path}}")
    {{responseClass}} {{methodName}}(@RequestBody {{requestClass}} request);
}
