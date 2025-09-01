package com.example.smart_office_software_system.service.impl;

import com.example.smart_office_software_system.configs.RabbitMQConfig;
import com.example.smart_office_software_system.domain.Schedule;
import com.example.smart_office_software_system.mapper.ScheduleMapper;
import com.example.smart_office_software_system.service.ScheduledService;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;

@Service
public class ScheduledServiceImpl implements ScheduledService {
    @Autowired
    private ScheduleMapper scheduleMapper;
    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    // 方法名到方法引用的映射（使用Function避免反射性能开销）
    private final Map<String, Function<Map<String, Object>, Object>> methodMapper = new HashMap<>();

    @Override
    public List<Schedule> findByUserId(Long userId) {
        return scheduleMapper.findByUserId(userId);
    }

    @Override
    public void deleteById(Long id) {
        scheduleMapper.deleteById(id);
    }

    @Override
    public void addSchedule(Schedule schedule) {
        scheduleMapper.addSchedule(schedule);
    }

    @Override
    public Schedule findByTaskId(String taskId) {
        return scheduleMapper.findByTaskId(taskId);
    }

    @Override
    public void deleteByTaskId(String taskId) {
        scheduleMapper.deleteByTaskId(taskId);
    }

    @Override
    public void update(Schedule schedule) {
        scheduleMapper.updateSchedule(schedule);
    }

    @Override
    public List<Schedule> findByUserIdAndDate(Long userId, String dateStr) {
        // 校验参数非空
        if (userId == null || dateStr == null || dateStr.isEmpty()) {
            throw new IllegalArgumentException("用户 ID 和日期均不可为空");
        }

        // 将字符串日期转换为 LocalDate（处理格式异常）
        LocalDate date = LocalDate.parse(dateStr, DATE_FORMATTER);

        // 计算时间范围
        LocalDateTime startTime = date.atStartOfDay();
        LocalDateTime endTime = date.plusDays(1).atStartOfDay();

        // 调用 MyBatis 范围查询
        return scheduleMapper.findByUserIdAndDate(userId, startTime, endTime);
    }

    /**
     * 构造函数中初始化方法映射
     */
    public ScheduledServiceImpl() {
        // 初始化方法映射，使用lambda表达式直接引用方法
        methodMapper.put("findByUserId", data -> {
            Long userId = (Long) data.get("userId");
            return findByUserId(userId);
        });

        methodMapper.put("deleteById", data -> {
            Long id = (Long) data.get("id");
            deleteById(id);
            return null;
        });

        methodMapper.put("addSchedule", data -> {
            HashMap<String, Object> s = (HashMap<String, Object>) data.get("schedule");
            Schedule schedule = new Schedule();
            // 先转成 Number，再转 Long
            Number userIdNum = (Number) s.get("userId");
            schedule.setUserId(userIdNum.longValue());
            schedule.setEventName((String) s.get("eventName"));
            // 处理 LocalDateTime，这里要注意，从 Map 里取出来的是字符串，需要解析成 LocalDateTime
            String startTimeStr = (String) s.get("startTime");
            String endTimeStr = (String) s.get("endTime");
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
            schedule.setStartTime(LocalDateTime.parse(startTimeStr, formatter));
            schedule.setEndTime(LocalDateTime.parse(endTimeStr, formatter));
            schedule.setDescription((String) s.get("description"));
            addSchedule(schedule);
            return null;
        });

        methodMapper.put("findByTaskId", data -> {
            String taskId = (String) data.get("taskId");
            return findByTaskId(taskId);
        });

        methodMapper.put("deleteByTaskId", data -> {
            String taskId = (String) data.get("taskId");
            deleteByTaskId(taskId);
            return null;
        });

        methodMapper.put("update", data -> {
            Schedule schedule = (Schedule) data.get("schedule");
            update(schedule);
            return null;
        });

        methodMapper.put("findByUserIdAndDate", data -> {
            Long userId = (Long) data.get("userId");
            String dateStr = (String) data.get("dateStr");
            return findByUserIdAndDate(userId, dateStr);
        });
    }

    @RabbitListener(queues = RabbitMQConfig.TASK_NOTIFICATION_QUEUE)
    public void listenTask(Map<String, Object> data) {
        try {
            // 从消息中获取方法名
            String funName = (String) data.get("task");
            if (funName == null) {
                throw new IllegalArgumentException("消息中缺少'task'字段，无法确定调用方法");
            }

            // 记录接收到的消息
            System.out.println("接收到任务消息: " + data);

            // 根据方法名查找对应的函数
            Function<Map<String, Object>, Object> method = methodMapper.get(funName);
            if (method == null) {
                throw new IllegalArgumentException("未找到方法: " + funName);
            }

            // 调用方法并处理返回结果
            Object result = method.apply(data);
            System.out.println("方法 " + funName + " 调用成功，返回结果: " + result);

        } catch (Exception e) {
            // 异常处理
            System.err.println("处理任务消息时发生异常: " + e.getMessage());
            e.printStackTrace();

            // 可以在这里添加重试逻辑或错误消息转发
        }
    }
}