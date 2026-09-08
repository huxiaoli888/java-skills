package com.chaken.ai.test.cms.sampleitem.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class SampleItemCreateRequest {
    @NotBlank(message = "{common.required}")
    @Size(max = 64, message = "{common.size.invalid}")
    private String name;

    @NotBlank(message = "{common.required}")
    @Size(max = 64, message = "{common.size.invalid}")
    private String code;

    @Size(max = 256, message = "{common.size.invalid}")
    private String description;

    private Boolean enabled = true;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Boolean getEnabled() {
        return enabled;
    }

    public void setEnabled(Boolean enabled) {
        this.enabled = enabled;
    }
}
