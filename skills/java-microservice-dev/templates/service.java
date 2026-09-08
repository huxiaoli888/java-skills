package {{basePackage}}.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import {{basePackage}}.dto.{{requestClass}};
import {{basePackage}}.dto.{{responseClass}};

@Service
public class {{serviceClass}} {

    @Transactional
    public {{responseClass}} {{methodName}}({{requestClass}} request) {
        // 只保留业务编排；持久化放 repository/mapper，外部调用放 adapter/client。
        throw new UnsupportedOperationException("请根据业务规则实现服务编排逻辑");
    }
}
