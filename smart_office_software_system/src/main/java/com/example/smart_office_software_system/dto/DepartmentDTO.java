package com.example.smart_office_software_system.dto;

import com.example.smart_office_software_system.domain.User;
import lombok.Data;
import lombok.ToString;

import java.util.Date;
import java.util.List;

/**
 * @program: smart_office_software_system
 * @description: 部门实体类
 * @create: 2025-07-07 17:59
 **/


@Data
@ToString
public class DepartmentDTO {

    private Integer id;
    private String deptName;
    private String deptIntro;
    private Integer leaderId;
    private Date createdAt;
    private Date updatedAt;
    private String leader;
    private List<User> userList;
}
