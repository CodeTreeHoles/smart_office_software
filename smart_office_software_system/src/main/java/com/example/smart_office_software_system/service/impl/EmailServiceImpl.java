package com.example.smart_office_software_system.service.impl;

import com.example.smart_office_software_system.configs.RabbitMQConfig;
import com.example.smart_office_software_system.mapper.ScheduleMapper;
import com.example.smart_office_software_system.service.EmailService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.rabbit.connection.CorrelationData;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSenderImpl;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import static com.example.smart_office_software_system.utils.EmailUtils.isEmailValid;

@Service
@Slf4j
public class EmailServiceImpl implements EmailService {
    @Value("${spring.mail.username}")
    private String username;
    @Autowired
    private JavaMailSenderImpl mailSender;
    @Autowired
    private ScheduleMapper scheduleMapper;
    @Autowired
    private RabbitTemplate rabbitTemplate;
    @Autowired
    private RedisTemplate<String,Object> redisTemplate;
    @Override
    public String sendEmail(String content, String subject, LocalDateTime sendTime, String email) {
        if (!isEmailValid(email)) {
            return "邮箱号不存在";
        }

        try {
            // 1. 封装邮件任务
            String taskId = UUID.randomUUID().toString();
            Map<String, Object> messageBody = new HashMap<>();
            messageBody.put("content", content);
            messageBody.put("subject", subject);
            messageBody.put("email", email);
            messageBody.put("sendTime", sendTime.toString());
            messageBody.put("taskId", taskId); // 生成唯一任务ID

            // 2. 计算延迟时间（毫秒）
            long delayMillis = calculateDelayMillis(sendTime);

            // 3. 发送延迟消息到 RabbitMQ 延迟交换机
            CorrelationData correlationData = new CorrelationData((String) messageBody.get("taskId"));
            rabbitTemplate.convertAndSend(
                    RabbitMQConfig.DELAYED_EMAIL_EXCHANGE, // 延迟交换机
                    RabbitMQConfig.DELAYED_ROUTING_KEY,   // 路由键
                    messageBody,                           // 消息体
                    msg -> {
                        msg.getMessageProperties().setHeader("x-delay", delayMillis); // 设置延迟头
                        return msg;
                    },
                    correlationData
            );

            log.info("延迟邮件已调度，TaskID: {}，计划发送时间: {}", messageBody.get("taskId"), sendTime);
            redisTemplate.opsForValue().set(taskId,subject);
            return taskId;
        } catch (Exception e) {
            log.error("调度邮件失败: {}", e.getMessage());
            return e.getMessage();
        }
    }

    @Override
    public void cancelEmail(String taskId) {
        redisTemplate.delete(taskId);
    }

    // 计算延迟时间（当前时间到目标时间的毫秒差）
    private long calculateDelayMillis(LocalDateTime targetTime) {
        LocalDateTime now = LocalDateTime.now();
        if (targetTime.isBefore(now)) {
            return 0; // 时间已过，立即发送
        }
        return (targetTime.toEpochSecond(ZoneOffset.UTC) - now.toEpochSecond(ZoneOffset.UTC)) * 1000;
    }

    // 监听延迟队列，消费到期消息
    @RabbitListener(queues = RabbitMQConfig.DELAYED_EMAIL_QUEUE)
    public void handleDelayedEmail(Map<String, Object> messageBody) {
        try {
            String taskId = (String) messageBody.get("taskId");
            String subject = (String) redisTemplate.opsForValue().get(taskId);
            if(subject == null || subject.isEmpty()){
                return;
            }
            String email = (String) messageBody.get("email");
            String content = (String) messageBody.get("content");
            log.info("触发邮件发送，TaskID: {}，目标邮箱: {}", taskId, email);
            sendImmediateEmail(subject, content, email);
            redisTemplate.delete(taskId);
        } catch (Exception e) {
            log.error("处理邮件失败，TaskID: {}，原因: {}", messageBody.get("taskId"), e.getMessage());
            // 可添加死信队列逻辑，将失败消息存入死信队列
        }
    }

    // 立即发送邮件
    private void sendImmediateEmail(String subject, String content, String toEmail) {
        SimpleMailMessage mailMessage = new SimpleMailMessage();
        mailMessage.setFrom(username);
        mailMessage.setTo(toEmail);
        mailMessage.setSubject(subject);
        mailMessage.setText(content);

        try {
            mailSender.send(mailMessage);
            log.info("邮件已发送，收件人: {}", toEmail);
        } catch (Exception e) {
            log.error("邮件发送失败，收件人: {}, 原因: {}", toEmail, e.getMessage());
        }
    }
}