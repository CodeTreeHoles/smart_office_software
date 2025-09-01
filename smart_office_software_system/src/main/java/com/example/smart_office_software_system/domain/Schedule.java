package com.example.smart_office_software_system.domain;

import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Schedule {
    private Long id;
    private String eventName;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private String description;
    private Long userId;
    private LocalDateTime createdTime;
}
