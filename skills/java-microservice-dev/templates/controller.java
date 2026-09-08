package {{basePackage}}.controller;

import javax.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import {{basePackage}}.dto.{{requestClass}};
import {{basePackage}}.dto.{{responseClass}};
import {{basePackage}}.service.{{serviceClass}};
import {{basePackage}}.web.ApiResponse;

@RestController
@RequestMapping("{{basePath}}")
public class {{controllerClass}} {
    private final {{serviceClass}} service;

    public {{controllerClass}}({{serviceClass}} service) {
        this.service = service;
    }

    @PostMapping("{{operationPath}}")
    public ApiResponse<{{responseClass}}> {{methodName}}(
            @Valid @RequestBody {{requestClass}} request,
            @RequestHeader(value = "x-reqid", required = true) String reqid) {
        return ApiResponse.success(service.{{methodName}}(request), reqid);
    }
}
