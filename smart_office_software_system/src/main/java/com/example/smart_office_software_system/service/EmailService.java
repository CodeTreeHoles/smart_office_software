package com.example.smart_office_software_system.service;

import java.time.LocalDateTime;

public interface EmailService {

    String sendEmail(String content, String subject, LocalDateTime sendTime, String email);
    void cancelEmail(String taskId);
}
