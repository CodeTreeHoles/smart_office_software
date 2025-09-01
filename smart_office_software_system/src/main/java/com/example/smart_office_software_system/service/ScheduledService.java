package com.example.smart_office_software_system.service;

import com.example.smart_office_software_system.domain.Schedule;

import java.time.LocalDate;
import java.util.List;

public interface ScheduledService {
    List<Schedule> findByUserId(Long userId);
    void deleteById(Long id);
    void addSchedule(Schedule schedule);
    Schedule findByTaskId(String taskId);
    void deleteByTaskId(String taskId);
    void update(Schedule schedule);
    List<Schedule> findByUserIdAndDate(Long userId, String date);
}
