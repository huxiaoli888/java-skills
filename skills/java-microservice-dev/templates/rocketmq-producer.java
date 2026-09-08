package {{basePackage}}.producer;

import org.apache.rocketmq.spring.core.RocketMQTemplate;
import org.springframework.stereotype.Component;
import {{basePackage}}.message.{{messageClass}};

@Component
public class {{producerClass}} {
    private final RocketMQTemplate rocketMQTemplate;

    public {{producerClass}}(RocketMQTemplate rocketMQTemplate) {
        this.rocketMQTemplate = rocketMQTemplate;
    }

    public void send(String topic, {{messageClass}} message) {
        rocketMQTemplate.convertAndSend(topic, message);
    }
}
