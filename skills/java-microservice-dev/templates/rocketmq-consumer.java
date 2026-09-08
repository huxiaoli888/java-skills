package {{basePackage}}.consumer;

import org.apache.rocketmq.spring.annotation.RocketMQMessageListener;
import org.apache.rocketmq.spring.core.RocketMQListener;
import org.springframework.stereotype.Component;
import {{basePackage}}.message.{{messageClass}};

@Component
@RocketMQMessageListener(
        topic = "${{{mqConfigPrefix}}.topic}",
        consumerGroup = "${{{mqConfigPrefix}}.consumer-group}"
)
public class {{consumerClass}} implements RocketMQListener<{{messageClass}}> {

    @Override
    public void onMessage({{messageClass}} message) {
        // Validate payload, enforce idempotency, then call service layer.
    }
}
