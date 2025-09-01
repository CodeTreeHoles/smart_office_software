package com.example.smart_office_software_system.domain;

import lombok.Data;
import lombok.ToString;

import java.util.Date;

@Data
@ToString
public class Department {
    private Integer id;
    private String deptName;
    private String deptIntro;
    private Integer leaderId;
    private Date createdAt;
    private Date updatedAt;
}
