package com.example.smart_office_software_system.configs;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.config.SimpleRabbitListenerContainerFactory;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.HashMap;
import java.util.Map;

@Configuration
public class RabbitMQConfig {

    // ===================== 延迟消息配置 =====================
    // 延迟交换机名称
    public static final String DELAYED_EMAIL_EXCHANGE = "delayed.email.exchange";
    // 延迟队列名称
    public static final String DELAYED_EMAIL_QUEUE = "delayed.email.queue";
    // 延迟路由键
    public static final String DELAYED_ROUTING_KEY = "delayed.email.send";

    // ===================== 普通消息配置 =====================
    // 普通交换机名称（使用direct类型）
    public static final String NORMAL_EXCHANGE = "normal.message.exchange";
    // 普通队列名称 - 示例1：任务通知队列
    public static final String TASK_NOTIFICATION_QUEUE = "task.notification.queue";
    // 普通队列名称 - 示例2：系统日志队列
    public static final String SYSTEM_LOG_QUEUE = "system.log.queue";
    // 普通路由键 - 任务通知
    public static final String TASK_NOTIFICATION_ROUTING_KEY = "task.notification";
    // 普通路由键 - 系统日志
    public static final String SYSTEM_LOG_ROUTING_KEY = "system.log";

    @Autowired
    private ConnectionFactory connectionFactory;

    // ===================== 延迟消息组件定义 =====================
    // 创建延迟交换机（需安装 rabbitmq-delayed-message-exchange 插件）
    @Bean
    public CustomExchange delayedEmailExchange() {
        Map<String, Object> args = new HashMap<>();
        args.put("x-delayed-type", "direct"); // 指定交换机类型为 direct 延迟交换机
        return new CustomExchange(DELAYED_EMAIL_EXCHANGE, "x-delayed-message", true, false, args);
    }

    // 创建延迟队列（持久化）
    @Bean
    public Queue delayedEmailQueue() {
        return new Queue(DELAYED_EMAIL_QUEUE, true); // durable = true
    }

    // 绑定延迟队列到交换机
    @Bean
    public Binding delayedEmailBinding() {
        return BindingBuilder.bind(delayedEmailQueue())
                .to(delayedEmailExchange())
                .with(DELAYED_ROUTING_KEY)
                .noargs();
    }

    // ===================== 普通消息组件定义 =====================
    // 创建普通direct交换机（持久化）
    @Bean
    public DirectExchange normalExchange() {
        return new DirectExchange(NORMAL_EXCHANGE, true, false);
    }

    // 创建任务通知队列（持久化）
    @Bean
    public Queue taskNotificationQueue() {
        return new Queue(TASK_NOTIFICATION_QUEUE, true);
    }

    // 创建系统日志队列（持久化）
    @Bean
    public Queue systemLogQueue() {
        return new Queue(SYSTEM_LOG_QUEUE, true);
    }

    // 绑定任务通知队列到交换机
    @Bean
    public Binding taskNotificationBinding() {
        return BindingBuilder.bind(taskNotificationQueue())
                .to(normalExchange())
                .with(TASK_NOTIFICATION_ROUTING_KEY);
    }

    // 绑定系统日志队列到交换机
    @Bean
    public Binding systemLogBinding() {
        return BindingBuilder.bind(systemLogQueue())
                .to(normalExchange())
                .with(SYSTEM_LOG_ROUTING_KEY);
    }

    // ===================== 公共配置 =====================
    // 配置Jackson消息转换器
    @Bean
    public Jackson2JsonMessageConverter messageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    // 应用转换器到监听器容器
    @Bean
    public SimpleRabbitListenerContainerFactory rabbitListenerContainerFactory() {
        SimpleRabbitListenerContainerFactory factory = new SimpleRabbitListenerContainerFactory();
        factory.setConnectionFactory(connectionFactory);
        factory.setMessageConverter(messageConverter());
        return factory;
    }

    // 应用转换器到RabbitTemplate
    @Bean
    public RabbitTemplate rabbitTemplate() {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setMessageConverter(messageConverter());
        return template;
    }
}